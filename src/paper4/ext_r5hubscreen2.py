"""Round 5, component B of ``tolerant_v5_2``: ``hubscreen`` v2 (docs/ext/r5hubscreen2.md).

Round 4 (``ext_r4hubscreen.tolerant_v5_1_hs``, docs/ext/r4hubscreen.md) replaced v5_1's
``_failed('underdetermined')`` by a conditional-SIS reduction of the failing equation. Its verifier found
that, when the conditioning set C_j (own lags + contemporaneous parents) alone exceeded the column cap,
v1 kept own lag 1 and only the top-|t| contemporaneous parents, so it **dropped declared contemporaneous
parents** in 55% (T19 reversed) and 38% (T19 extra) of those reductions: a truncation that deletes
skeleton edges, not screening (docs/ext/synthesis_round4.md, section 2.8).

v2 (synthesis_round4.md, section 4.1 (B)) changes only that branch. For an equation j whose term list
fails the check that applies (``fit_equations``: len(terms) + 2 > m; ``ext_narrow.screen_pairs``:
1 + len(terms) + lag_max + 2 > m):

- C_j = own lags 1..lag_max and every lag-0 term the list carries; pool = the other (lagged) terms;
  cap = floor(m / 2.5) columns including the intercept (as v1);
- if |C_j| <= cap - 1: exactly v1 (keep C_j and the top d = cap - 1 - |C_j| pool terms by conditional |t|);
- if |C_j| >  cap - 1: drop own lags 2..lag_max; C'_j = own lag 1 + every lag-0 term. Then keep C'_j and
  the top d' = cap - 1 - |C'_j| pool terms if d' > 0 (never the case at lag_max 2). **No lag-0 term is
  ever dropped** (declared parents, and in bootstrap draws also the parents the drawn skeleton carries
  after repair / reversal). If C'_j is still over the cap it is kept whole: the cap is the screening
  budget, not the feasibility check;
- if the reduced list still fails ``fit_equations``' check, the fit is "underdetermined": at the data level
  the run fails (counted in ITT); in a bootstrap draw the draw fails and ``bootstrap_C`` handles it as for
  v5_1 (the run fails only through ``_too_few``). If the reduced base equation of the screening step still
  fails the screening check, ``ValueError`` is raised as in ``ext_narrow.screen_pairs`` (data level: run
  fails "underdetermined"; draw level: the data selection is kept, as v5_1).

Everything else is ``ext_r4hubscreen`` (and therefore ``tolerant_v5_1``) line for line: same switch, same
screening, same repair/reversal draws, same random-number calls, same bootstrap stream (the driver uses
``ext_seed("tolerant_v5_1")``). The check depends on the term count only, so on a run where no data-level
or draw-level term list fails, the output is bit-identical to ``tolerant_v5_1``.

Output info: ``hs_reduced`` (any reduction in data or draws), ``hs_eq_data`` / ``hs_eq_total`` (number of
reduced equations), ``hs_trunc_eq_data`` / ``hs_trunc_eq_total`` (equations in the |C_j| > cap - 1 branch),
``hs_contemp_dropped`` (lag-0 terms dropped; 0 by construction, counted as a check), ``hs_fit_fail`` /
``hs_screen_fail`` (reduced equations still failing a check). Methods see only the data, the public
skeleton and its stated damage. The interval is pre-scaled by ``ext_narrow.PRESCALE``; the width factor
is applied by experiments/ext/r5hubscreen2/run_r5.py (v5_1's frozen factor on runs without reduction,
f_red otherwise).

Existing modules are imported, never modified.
"""
from __future__ import annotations

import math

import numpy as np

from .effects import cumulative, irf
from .estimator import bootstrap_C, fit_equations, parent_terms, percentile_interval, soft_terms
from .ext_narrow import _f_p, _norm_sf, _prescale, opened_terms
from .ext_r4hubscreen import _cond_t, cap_columns
from .ext_v51 import TAU, allag_ratio
from .methods import (ALPHA, MethodResult, _failed, _flip_from, _too_few, contemporaneous_pool,
                      repair_candidates, stated_counts)
from .skeleton import Skeleton, _creates_cycle


class RedLog2:
    """Reduction counters (data level and per bootstrap draw)."""

    def __init__(self):
        self.eq = 0
        self.dropped = 0
        self.data_eq = 0
        self.trunc = 0
        self.trunc_data = 0
        self.contemp_dropped = 0
        self.fit_fail = 0
        self.screen_fail = 0
        self.draw_flags = []
        self._cur = 0
        self.nodes = set()

    def note(self, j: int, before: list, after: list, trunc: bool, phase: str):
        self.eq += 1
        self.dropped += len(before) - len(after)
        self.contemp_dropped += sum(1 for t in before if t[1] == 0) - sum(1 for t in after if t[1] == 0)
        if trunc:
            self.trunc += 1
        if phase == "data":
            self.data_eq += 1
            self.nodes.add(j)
            if trunc:
                self.trunc_data += 1
        else:
            self._cur += 1

    def end_draw(self):
        self.draw_flags.append(self._cur > 0)
        self._cur = 0


def csis_reduce_v2(data: np.ndarray, tj: list, j: int, lag_max: int) -> tuple[list, bool]:
    """Reduced term list of equation j (module doc) and whether the truncation branch was taken.
    Keeps the original order of the kept terms."""
    T = data.shape[0]
    rows = np.arange(lag_max, T)
    m = len(rows)
    cap = cap_columns(m)
    col = lambda t: data[rows - t[1], t[0]]  # noqa: E731
    y = data[rows, j]
    C = [t for t in tj if (t[0] == j and t[1] > 0) or t[1] == 0]
    pool = [t for t in tj if t not in C]
    trunc = len(C) > cap - 1
    if trunc:
        C = [t for t in C if not (t[0] == j and t[1] >= 2)]
    d = cap - 1 - len(C)
    keep = set(C)
    if pool and d > 0:
        Xc = np.column_stack([np.ones(m)] + [col(t) for t in C])
        tt = _cond_t(y, Xc, np.column_stack([col(t) for t in pool]))
        order = sorted(range(len(pool)), key=lambda i: (-tt[i], i))
        keep |= {pool[i] for i in order[:d]}
    return [t for t in tj if t in keep], trunc


def fit_reduced2(data: np.ndarray, terms: list, lag_max: int, log: RedLog2 | None = None, phase: str = "data"):
    """``fit_equations`` after the v2 reduction of every term list that fails its check (len + 2 > m)."""
    m = data.shape[0] - lag_max
    new = []
    for j, tj in enumerate(terms):
        if tj and len(tj) + 2 > m:
            r, trunc = csis_reduce_v2(data, tj, j, lag_max)
            if log is not None:
                log.note(j, tj, r, trunc, phase)
                if len(r) + 2 > m:
                    log.fit_fail += 1
            new.append(r)
        else:
            new.append(tj)
    return fit_equations(data, new, lag_max)


def screen_pairs_hs2(data: np.ndarray, skel: Skeleton, lag_max: int, log: RedLog2 | None = None,
                     phase: str = "data") -> list[tuple[float, int, int]]:
    """``ext_narrow.screen_pairs`` with the v2 reduction of base equations that fail its check."""
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
            r_, trunc = csis_reduce_v2(data, tj, j, lag_max)
            if log is not None:
                log.note(j, tj, r_, trunc, phase)
            tj = r_
        X = np.column_stack([np.ones(m)] + [data[rows - lag, i] for i, lag in tj])
        if X.shape[1] + lag_max + 2 > m:  # still over after v2: behave as screen_pairs
            if log is not None:
                log.screen_fail += 1
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


def select_open_hs2(data, skel, lag_max, k_miss, mult, alpha_open, log=None, phase="data"):
    tests = screen_pairs_hs2(data, skel, lag_max, log, phase)
    n_sig = sum(1 for p, _, _ in tests if p < alpha_open)
    K = min(len(tests), max(int(math.ceil(mult * k_miss)), n_sig))
    return [(u, v) for _, u, v in tests[:K]]


def tolerant_hs2(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, log: RedLog2, *,
                 name: str) -> MethodResult:
    """``ext_r4hubscreen.tolerant_hs`` with the v2 reduction."""
    n = skel.n
    stated = stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    full_lags = k_miss > 0
    terms_of = (lambda s: [soft_terms(s, j, lag_max) for j in range(n)]) if full_lags else \
               (lambda s: [parent_terms(s, j, lag_max) for j in range(n)])
    base_terms = terms_of(skel)
    fit0 = fit_reduced2(data, base_terms, lag_max, log)
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

    fit = fit_reduced2(data, terms_of(draw_skel()), lag_max, log) if cands else fit0
    if fit.status != "ok":
        return _failed(name, fit.status)

    def refit(x):
        f = fit_reduced2(x, terms_of(draw_skel()) if draw_structure else base_terms, lag_max, log, "draw")
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


def tolerant_sel_hs2(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, log: RedLog2, *,
                     mult: float = 3.0, alpha_open: float = 0.10, name: str) -> MethodResult:
    """``ext_r4hubscreen.tolerant_sel_hs`` (= ``ext_v51.tolerant_sel_dd(reselect=True)``) with the v2 reduction."""
    n = skel.n
    stated = stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    if k_miss == 0:
        return tolerant_hs2(data, skel, lag_max, H, n_boot, rng, log, name=name)
    try:
        opened = select_open_hs2(data, skel, lag_max, k_miss, mult, alpha_open, log)
    except ValueError:
        return _failed(name, "underdetermined")

    def terms_for(s: Skeleton, op):
        return [list(dict.fromkeys(opened_terms(s, op, j, lag_max))) for j in range(n)]

    fit0 = fit_reduced2(data, terms_for(skel, opened), lag_max, log)
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

    fit = fit_reduced2(data, terms_for(draw_skel(cands), opened), lag_max, log) if cands else fit0
    if fit.status != "ok":
        return _failed(name, fit.status)
    n_open = []

    def refit(x):
        try:
            op = select_open_hs2(x, skel, lag_max, k_miss, mult, alpha_open, log, "draw")
        except ValueError:
            op = opened
        n_open.append(len(op))
        f0 = fit_reduced2(x, terms_for(skel, op), lag_max, log, "draw")
        if f0.status != "ok":
            log.end_draw()
            return f0
        cs = repair_candidates(f0.residuals, skel, k_miss)
        if not cs and not reversing:
            log.end_draw()
            return f0
        f = fit_reduced2(x, terms_for(draw_skel(cs), op), lag_max, log, "draw")
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


def tolerant_v5_1_hs2(data, skel, lag_max, H, n_boot, rng):
    """Component B of tolerant_v5_2: ``tolerant_v5_1`` with the v2 reduction of failing equations."""
    name = "tolerant_v5_1_hs2"
    T = data.shape[0]
    k_miss = stated_counts(skel.damage)["missing"]
    r = allag_ratio(skel, T, lag_max)
    targeted = k_miss > 0 and TAU is not None and r < TAU
    log = RedLog2()
    if targeted:
        res = tolerant_sel_hs2(data, skel, lag_max, H, n_boot, rng, log, name=name)
    else:
        res = tolerant_hs2(data, skel, lag_max, H, n_boot, rng, log, name=name)
    out = _prescale(res, name)
    info = {"v51_targeted": int(targeted), "v51_ratio": float(r),
            "hs_reduced": int(log.eq > 0), "hs_eq_data": log.data_eq, "hs_eq_total": log.eq,
            "hs_trunc_eq_data": log.trunc_data, "hs_trunc_eq_total": log.trunc,
            "hs_terms_dropped": log.dropped, "hs_contemp_dropped": log.contemp_dropped,
            "hs_fit_fail": log.fit_fail, "hs_screen_fail": log.screen_fail,
            "hs_draws_reduced": int(sum(log.draw_flags)), "hs_draws_total": len(log.draw_flags),
            "hs_nodes_data": sorted(log.nodes)}
    if out.status == "ok":
        out.info.update(info)
    else:
        out.info = info
    return out


METHODS = {"tolerant_v5_1_hs2": tolerant_v5_1_hs2}
