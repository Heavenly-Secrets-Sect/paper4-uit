"""Round 4, direction "hubscreen": conditional sure-independence screening (CSIS) of an
underdetermined equation's own terms, instead of failing.

Problem. ``tolerant_v5_1`` returns ``_failed('underdetermined')`` when one structural equation of
the skeleton has too many regressors for the rows: in ``ext_narrow.screen_pairs`` when
``|X| + lag_max + 2 > m`` (X with intercept), in ``estimator.fit_equations`` when
``|terms| + 2 > m``. Every adjacent pair puts lags 1..lag_max of both nodes into each other's
equation (``estimator.parent_terms``), so hub nodes break first: at lag_max 2 and T <= 30 a large
share of D-07 topologies cannot be fitted at all, by any skeleton-based method
(docs/ext/region51.md; docs/ext/r4hubscreen.md, probe).

Change (only for equations that would fail; everything else is ``tolerant_v5_1`` line for line).
For an equation j whose term list fails the check that applies (screening or fitting):

- conditioning set C_j = own lags 1..lag_max and the contemporaneous parents (lag 0 terms) that
  the term list carries; the remaining terms (lagged terms of other nodes: the skeleton's adjacent
  pairs and, inside fits, the lag blocks opened in step (2)) form the screening pool;
- every pool term is ranked by |t| of its coefficient when it is added alone to the OLS of y_j on
  [1, C_j] (conditional SIS, Barut, Fan and Verhasselt 2016, with the conditioning set chosen from
  prior knowledge as in their section 2; Fan and Lv 2008 for SIS);
- the equation keeps C_j and the top d pool terms, d = max(0, cap - 1 - |C_j|), cap = floor(m / 2.5)
  columns including the intercept;
- if |C_j| alone exceeds cap - 1, it keeps own lag 1 and the contemporaneous parents ranked by the
  same conditional |t| (given [1, own lag 1]) up to the cap, and no pool term.

Refinement of the proposed design, fixed before any evaluation (docs/ext/r4hubscreen.md, section 2):
skeleton lag terms and opened lag terms are ranked JOINTLY in one pool. The proposal reduced the
skeleton terms first and then limited the opened blocks to the remaining room; since the skeleton
terms alone fill the cap, that order would close every opened block of a failing equation, which
is exactly what step (2) is for.

The check is a function of the term count only, never of the data, so on a run where no term list
of any data-level or bootstrap-level fit fails, every call below performs the same arithmetic and
the same random-number calls as ``tolerant_v5_1`` and the output is identical (tested in
experiments/ext/r4hubscreen/check_identity.py). Bootstrap draws re-run the screening and the
reduction on each simulated series (step (5) unchanged).

Methods see only the data, the public skeleton and its stated damage. The interval is pre-scaled by
``ext_narrow.PRESCALE``; the width factor is applied by the driver experiments/ext/r4hubscreen/run_r4.py
(two factors per (T, stated kind): v5_1's factor on runs without reduction, a factor tuned on reduced
calibration runs otherwise).
"""
from __future__ import annotations

import math

import numpy as np

from .effects import cumulative, irf
from .estimator import bootstrap_C, fit_equations, parent_terms, percentile_interval, soft_terms
from .ext_narrow import _f_p, _norm_sf, _prescale, opened_terms
from .ext_v51 import TAU, allag_ratio
from .methods import (ALPHA, MethodResult, _failed, _flip_from, _too_few, contemporaneous_pool,
                      repair_candidates, stated_counts)
from .skeleton import Skeleton, _creates_cycle

CAP_DIV = 2.5


class RedLog:
    """Counts reductions: equations reduced, terms dropped, and whether any happened in the data-level
    fits (``data``) or in bootstrap draws (``draws``)."""

    def __init__(self):
        self.eq = 0
        self.dropped = 0
        self.data_eq = 0
        self.draw_flags = []
        self._cur = 0
        self.nodes = set()

    def note(self, j: int, n_drop: int, phase: str):
        self.eq += 1
        self.dropped += n_drop
        if phase == "data":
            self.data_eq += 1
            self.nodes.add(j)
        else:
            self._cur += 1

    def end_draw(self):
        self.draw_flags.append(self._cur > 0)
        self._cur = 0


def cap_columns(m: int) -> int:
    return int(math.floor(m / CAP_DIV))


def _cond_t(y: np.ndarray, Xc: np.ndarray, cands: np.ndarray) -> np.ndarray:
    """|t| of each candidate column added alone to the OLS of y on Xc (Xc includes the intercept)."""
    m = len(y)
    Q, _ = np.linalg.qr(Xc)
    ry = y - Q @ (Q.T @ y)
    R = cands - Q @ (Q.T @ cands)
    sxx = np.einsum("mk,mk->k", R, R)
    sxy = R.T @ ry
    syy = float(ry @ ry)
    df = m - Xc.shape[1] - 1
    out = np.zeros(cands.shape[1])
    good = sxx > 1e-12 * max(1.0, float(np.max(sxx)) if sxx.size else 1.0)
    if df <= 0:
        return out
    b = np.where(good, sxy / np.where(good, sxx, 1.0), 0.0)
    rss = np.maximum(syy - b * sxy, 1e-300)
    se = np.sqrt(rss / df / np.where(good, sxx, 1.0))
    out[good] = np.abs(b[good] / se[good])
    return out


def csis_reduce(data: np.ndarray, tj: list, j: int, lag_max: int) -> list:
    """Reduced term list of equation j (module doc). Keeps the original order of the kept terms."""
    T = data.shape[0]
    rows = np.arange(lag_max, T)
    m = len(rows)
    cap = cap_columns(m)
    col = lambda t: data[rows - t[1], t[0]]  # noqa: E731
    y = data[rows, j]
    C = [t for t in tj if (t[0] == j and t[1] > 0) or t[1] == 0]
    pool = [t for t in tj if t not in C]
    if len(C) > cap - 1:
        base = [t for t in C if t == (j, 1)]
        cand = [t for t in C if t[1] == 0]
        Xc = np.column_stack([np.ones(m)] + [col(t) for t in base])
        room = max(0, cap - 1 - len(base))
        if cand and room:
            tt = _cond_t(y, Xc, np.column_stack([col(t) for t in cand]))
            order = sorted(range(len(cand)), key=lambda i: (-tt[i], i))
            keep = set(base) | {cand[i] for i in order[:room]}
        else:
            keep = set(base)
    else:
        d = cap - 1 - len(C)
        keep = set(C)
        if pool and d > 0:
            Xc = np.column_stack([np.ones(m)] + [col(t) for t in C])
            tt = _cond_t(y, Xc, np.column_stack([col(t) for t in pool]))
            order = sorted(range(len(pool)), key=lambda i: (-tt[i], i))
            keep |= {pool[i] for i in order[:d]}
    return [t for t in tj if t in keep]


def fit_reduced(data: np.ndarray, terms: list, lag_max: int, log: RedLog | None = None, phase: str = "data"):
    """``fit_equations`` after reducing every term list that would fail its check (len + 2 > m)."""
    m = data.shape[0] - lag_max
    new = []
    for j, tj in enumerate(terms):
        if tj and len(tj) + 2 > m:
            r = csis_reduce(data, tj, j, lag_max)
            if log is not None:
                log.note(j, len(tj) - len(r), phase)
            new.append(r)
        else:
            new.append(tj)
    return fit_equations(data, new, lag_max)


def screen_pairs_hs(data: np.ndarray, skel: Skeleton, lag_max: int, log: RedLog | None = None,
                    phase: str = "data") -> list[tuple[float, int, int]]:
    """``ext_narrow.screen_pairs`` with CSIS reduction of base equations that fail its check."""
    T, n = data.shape
    rows = np.arange(lag_max, T)
    m = len(rows)
    adj = skel.adjacency().astype(bool)
    lagmat = np.stack([data[rows - lag] for lag in range(1, lag_max + 1)], axis=2)  # (m, n, lag)
    resid = np.zeros((m, n))
    dof = np.zeros(n, dtype=int)
    block_p = {}
    for j in range(n):
        tj = parent_terms(skel, j, lag_max)
        if 1 + len(tj) + lag_max + 2 > m:
            r_ = csis_reduce(data, tj, j, lag_max)
            if log is not None:
                log.note(j, len(tj) - len(r_), phase)
            tj = r_
        X = np.column_stack([np.ones(m)] + [data[rows - lag, i] for i, lag in tj])
        if X.shape[1] + lag_max + 2 > m:  # cannot happen after reduction; kept as in screen_pairs
            raise ValueError("underdetermined")
        Q, _ = np.linalg.qr(X)
        y = data[rows, j]
        r = y - Q @ (Q.T @ y)
        rss0 = float(r @ r)
        resid[:, j] = r
        dof[j] = m - X.shape[1]
        d1 = dof[j] - lag_max
        cand = [u for u in range(n) if u != j and not adj[u, j]]
        if not cand:
            continue
        L = lagmat[:, cand, :].reshape(m, -1)
        Z = (L - Q @ (Q.T @ L)).reshape(m, len(cand), lag_max)
        ZtZ = np.einsum("mcp,mcq->cpq", Z, Z)
        Ztr = np.einsum("mcp,m->cp", Z, r)
        for c_idx, u in enumerate(cand):
            try:
                b = np.linalg.solve(ZtZ[c_idx], Ztr[c_idx])
            except np.linalg.LinAlgError:
                block_p[(u, j)] = 1.0
                continue
            ss = float(Ztr[c_idx] @ b)
            rss1 = max(rss0 - ss, 1e-12)
            F = (ss / lag_max) / (rss1 / max(d1, 1))
            block_p[(u, j)] = _f_p(F, lag_max, d1)
    out = []
    for u in range(n):
        for v in range(u + 1, n):
            if adj[u, v]:
                continue
            ru, rv = resid[:, u], resid[:, v]
            den = math.sqrt(float(ru @ ru) * float(rv @ rv))
            rr = float(ru @ rv) / den if den > 0 else 0.0
            rr = max(min(rr, 0.999999), -0.999999)
            z = math.atanh(rr) * math.sqrt(max(min(dof[u], dof[v]) - 1, 1))
            ps = [block_p[(u, v)], block_p[(v, u)], 2 * _norm_sf(abs(z))]
            out.append((1 - (1 - min(ps)) ** 3, u, v))
    out.sort()
    return out


def select_open_hs(data, skel, lag_max, k_miss, mult, alpha_open, log=None, phase="data"):
    tests = screen_pairs_hs(data, skel, lag_max, log, phase)
    n_sig = sum(1 for p, _, _ in tests if p < alpha_open)
    K = min(len(tests), max(int(math.ceil(mult * k_miss)), n_sig))
    return [(u, v) for _, u, v in tests[:K]]


def tolerant_hs(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, log: RedLog, *,
                name: str) -> MethodResult:
    """``methods.tolerant(..., target_reversal=True)`` with ``fit_reduced`` (v5_1's branch without
    stated missing edges, and its all-lag branch)."""
    n = skel.n
    stated = stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    full_lags = k_miss > 0
    terms_of = (lambda s: [soft_terms(s, j, lag_max) for j in range(n)]) if full_lags else \
               (lambda s: [parent_terms(s, j, lag_max) for j in range(n)])
    base_terms = terms_of(skel)
    fit0 = fit_reduced(data, base_terms, lag_max, log)
    if fit0.status != "ok":
        return _failed(name, fit0.status)
    cands = repair_candidates(fit0.residuals, skel, k_miss)
    reversing = k_rev > 0
    draw_structure = bool(cands) or reversing
    pool = contemporaneous_pool(data, fit0, k_rev) if reversing else None

    def draw_skel() -> Skeleton:
        s = _flip_from(skel, pool, k_rev, rng) if reversing else skel.copy()
        for u, v in cands:
            e = (u, v) if rng.random() < 0.5 else (v, u)
            if _creates_cycle(s.oriented | {e}, n):
                e = (v, u) if e == (u, v) else (u, v)
            if not _creates_cycle(s.oriented | {e}, n):
                s.oriented.add(e)
        return s

    fit = fit_reduced(data, terms_of(draw_skel()), lag_max, log) if cands else fit0
    if fit.status != "ok":
        return _failed(name, fit.status)

    def refit(x):
        f = fit_reduced(x, terms_of(draw_skel()) if draw_structure else base_terms, lag_max, log, "draw")
        log.end_draw()
        return f

    draws = bootstrap_C(data, fit, H, n_boot, rng, refit=refit)
    if _too_few(draws, n_boot):
        return _failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, ALPHA)
    theta = irf(fit.B, H)
    C = draws.mean(axis=0) if draw_structure else cumulative(theta, H)
    return MethodResult(name, "ok", C, lo, hi, theta, fit.B,
                        {"n_repair": len(cands), "full_lags": full_lags,
                         "n_reversal_pool": None if pool is None else len(pool)})


def tolerant_sel_hs(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, log: RedLog, *,
                    mult: float = 3.0, alpha_open: float = 0.10, name: str) -> MethodResult:
    """``ext_v51.tolerant_sel_dd(reselect=True)`` with ``select_open_hs`` and ``fit_reduced``."""
    n = skel.n
    stated = stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    if k_miss == 0:
        return tolerant_hs(data, skel, lag_max, H, n_boot, rng, log, name=name)
    try:
        opened = select_open_hs(data, skel, lag_max, k_miss, mult, alpha_open, log)
    except ValueError:
        return _failed(name, "underdetermined")

    def terms_for(s: Skeleton, op):
        return [list(dict.fromkeys(opened_terms(s, op, j, lag_max))) for j in range(n)]

    fit0 = fit_reduced(data, terms_for(skel, opened), lag_max, log)
    if fit0.status != "ok":
        return _failed(name, fit0.status)
    cands = repair_candidates(fit0.residuals, skel, k_miss)
    reversing = k_rev > 0
    pool = contemporaneous_pool(data, fit0, k_rev) if reversing else None

    def draw_skel(cs) -> Skeleton:
        s = _flip_from(skel, pool, k_rev, rng) if reversing else skel.copy()
        for u, v in cs:
            e = (u, v) if rng.random() < 0.5 else (v, u)
            if _creates_cycle(s.oriented | {e}, n):
                e = (v, u) if e == (u, v) else (u, v)
            if not _creates_cycle(s.oriented | {e}, n):
                s.oriented.add(e)
        return s

    fit = fit_reduced(data, terms_for(draw_skel(cands), opened), lag_max, log) if cands else fit0
    if fit.status != "ok":
        return _failed(name, fit.status)
    n_open = []

    def refit(x):
        try:
            op = select_open_hs(x, skel, lag_max, k_miss, mult, alpha_open, log, "draw")
        except ValueError:
            op = opened
        n_open.append(len(op))
        f0 = fit_reduced(x, terms_for(skel, op), lag_max, log, "draw")
        if f0.status != "ok":
            log.end_draw()
            return f0
        cs = repair_candidates(f0.residuals, skel, k_miss)
        if not cs and not reversing:
            log.end_draw()
            return f0
        f = fit_reduced(x, terms_for(draw_skel(cs), op), lag_max, log, "draw")
        log.end_draw()
        return f

    draws = bootstrap_C(data, fit, H, n_boot, rng, refit=refit)
    if _too_few(draws, n_boot):
        return _failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, ALPHA)
    theta = irf(fit.B, H)
    return MethodResult(name, "ok", draws.mean(axis=0), lo, hi, theta, fit.B,
                        {"n_repair": len(cands), "n_open": len(opened),
                         "n_open_boot_mean": float(np.mean(n_open)) if n_open else None,
                         "n_reversal_pool": None if pool is None else len(pool)})


def tolerant_v5_1_hs(data, skel, lag_max, H, n_boot, rng):
    """The candidate: ``tolerant_v5_1`` with CSIS reduction of failing equations (module doc)."""
    name = "tolerant_v5_1_hs"
    T = data.shape[0]
    k_miss = stated_counts(skel.damage)["missing"]
    r = allag_ratio(skel, T, lag_max)
    targeted = k_miss > 0 and TAU is not None and r < TAU
    log = RedLog()
    if targeted:
        res = tolerant_sel_hs(data, skel, lag_max, H, n_boot, rng, log, name=name)
    else:
        res = tolerant_hs(data, skel, lag_max, H, n_boot, rng, log, name=name)
    out = _prescale(res, name)
    n_draw_red = int(sum(log.draw_flags))
    info = {"v51_targeted": int(targeted), "v51_ratio": float(r),
            "hs_reduced": int(log.eq > 0), "hs_eq_data": log.data_eq, "hs_eq_total": log.eq,
            "hs_terms_dropped": log.dropped, "hs_draws_reduced": n_draw_red,
            "hs_draws_total": len(log.draw_flags), "hs_nodes_data": sorted(log.nodes)}
    if out.status == "ok":
        out.info.update(info)
    else:
        out.info = info
    return out


def plugin_hs(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng):
    """Secondary reference: ``methods.plugin`` with the same CSIS reduction (always runnable).
    Bootstrap refits re-run the reduction on each simulated series."""
    name = "plugin_hs"
    n = skel.n
    terms = [parent_terms(skel, j, lag_max) for j in range(n)]
    log = RedLog()
    fit = fit_reduced(data, terms, lag_max, log)
    if fit.status != "ok":
        return _failed(name, fit.status)
    theta = irf(fit.B, H)
    draws = bootstrap_C(data, fit, H, n_boot, rng, refit=lambda x: fit_reduced(x, terms, lag_max, log, "draw"))
    if _too_few(draws, n_boot):
        return _failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, ALPHA)
    return MethodResult(name, "ok", cumulative(theta, H), lo, hi, theta, fit.B,
                        {"hs_reduced": int(log.eq > 0), "hs_eq_data": log.data_eq})


METHODS = {"tolerant_v5_1_hs": tolerant_v5_1_hs, "plugin_hs": plugin_hs}
