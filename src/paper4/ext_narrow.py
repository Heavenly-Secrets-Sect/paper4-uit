"""Module version 5 candidates (direction "narrow"): narrower intervals on stated missing edges at small T.

Why v4 is over-wide at T = 40. When missing edges are stated, v3/v4 put every node's lags 1..lag_max
into every equation (14 x 2 = 28 lagged regressors from 38 rows at T = 40). Nothing can be lost,
but the variance of every coefficient explodes. v4's width factor cannot correct the resulting
over-coverage either: the calibration grid starts at 1.0, and at T = 40 the tuned factor sits at
that floor (coverage 0.98, width about twice that of ``pselect_union``).

Two changes, tested separately (see docs/ext/narrow.md):

1. **Targeted opening** (``tolerant_v5_sel``, ``tolerant_v5``). Instead of all lags of all nodes,
   only the lag blocks of off-skeleton pairs with data evidence are opened. Evidence for a
   non-adjacent pair (u, v) is measured in the **structural** equations of the skeleton's own fit
   (own lags, the lags of adjacent pairs, the skeleton's contemporaneous parents), never in the
   reduced form (B1 showed the reduced-form Granger test is not an adjacency test):
     - F test of u's lag block added to v's equation, and of v's lag block added to u's equation
       (Frisch-Waugh, exact F reference via Paulson's normal approximation);
     - Fisher z of the correlation of the two structural residuals (a missing contemporaneous edge);
     - the three p-values are combined by Sidak.
   Opened set = the K pairs with the smallest combined p-value, K = max(ceil(mult * k_stated),
   #{p < alpha_open}), capped at the number of off-skeleton pairs. The stated missing count thus
   sets a floor on how much is opened; strong evidence can open more. Contemporaneous repair is
   v3's (BH on the residuals of this fit, at most k_stated edges, random direction per draw).
   ``tolerant_v5`` re-runs the selection inside every bootstrap draw, so the interval aggregates over
   the evidence-selected skeletons around the stated one (plan RQ4.2: effect interval over the
   plausible skeletons around the chosen skeleton); ``tolerant_v5_sel`` selects once on the data.
2. **Two-sided width calibration** (every v5 method). The interval is returned pre-scaled by
   ``PRESCALE`` = 0.5 about its midpoint, so the runner's calibration grid 1.0..10 (step 0.1) maps to
   effective factors 0.5..5 (step 0.05): the per-(T, stated kind) factor can now also narrow an
   over-covering interval. ``tolerant_v5_cal2`` is v3 itself with only this change (ablation).

With no stated missing edge every v5 method is v3 (pre-scaled), so on undamaged, extra and reversed
cells it differs from v4 only through the finer calibration grid.

Methods see only the data, the skeleton and its stated damage.
"""
from __future__ import annotations

import math

import numpy as np

from .effects import cumulative, irf
from .estimator import bootstrap_C, fit_equations, parent_terms, percentile_interval
from .methods import (ALPHA, MethodResult, _failed, _too_few, contemporaneous_pool, _flip_from,
                      repair_candidates, stated_counts, tolerant)
from .skeleton import Skeleton, _creates_cycle

PRESCALE = 0.5


def _norm_sf(z: float) -> float:
    return 0.5 * math.erfc(z / math.sqrt(2))


def _f_p(F: float, k: int, dof: int) -> float:
    """Upper tail of F(k, dof) by Paulson's normal approximation (as in diagnose.py)."""
    if not np.isfinite(F) or F <= 0:
        return 1.0
    a, b = 2 / (9 * k), 2 / (9 * max(dof, 1))
    f3 = F ** (1 / 3)
    return _norm_sf(((1 - b) * f3 - (1 - a)) / math.sqrt(a + b * f3 * f3))


def screen_pairs(data: np.ndarray, skel: Skeleton, lag_max: int) -> list[tuple[float, int, int]]:
    """(combined p, u, v) for every non-adjacent pair u < v, smallest p first, from the skeleton's
    structural fit (see module doc). Raises ValueError when a base equation is underdetermined."""
    T, n = data.shape
    rows = np.arange(lag_max, T)
    m = len(rows)
    adj = skel.adjacency().astype(bool)
    lagmat = np.stack([data[rows - lag] for lag in range(1, lag_max + 1)], axis=2)  # (m, n, lag)
    resid = np.zeros((m, n))
    dof = np.zeros(n, dtype=int)
    block_p = {}  # (src, eq) -> p of src's lag block in eq's equation
    for j in range(n):
        tj = parent_terms(skel, j, lag_max)
        X = np.column_stack([np.ones(m)] + [data[rows - lag, i] for i, lag in tj])
        if X.shape[1] + lag_max + 2 > m:
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
        L = lagmat[:, cand, :].reshape(m, -1)                 # (m, c * lag)
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


def select_open(data, skel: Skeleton, lag_max: int, k_miss: int, mult: float, alpha_open: float):
    """Off-skeleton pairs whose lag blocks are opened (see module doc)."""
    tests = screen_pairs(data, skel, lag_max)
    n_sig = sum(1 for p, _, _ in tests if p < alpha_open)
    K = min(len(tests), max(int(math.ceil(mult * k_miss)), n_sig))
    return [(u, v) for _, u, v in tests[:K]]


def opened_terms(skel: Skeleton, opened, j: int, lag_max: int):
    """The skeleton's terms of equation j plus the lag blocks of the opened pairs touching j."""
    terms = parent_terms(skel, j, lag_max)
    extra = sorted({i for u, v in opened for i, w in ((u, v), (v, u)) if w == j})
    lagged = [t for t in terms if t[1] > 0] + [(i, lag) for i in extra for lag in range(1, lag_max + 1)]
    return lagged + [t for t in terms if t[1] == 0]


def _prescale(res: MethodResult, name: str) -> MethodResult:
    if res.status != "ok":
        return _failed(name, res.status)
    mid, half = (res.lo + res.hi) / 2, (res.hi - res.lo) / 2
    return MethodResult(name, "ok", res.C, mid - PRESCALE * half, mid + PRESCALE * half, res.theta, res.B,
                        {**res.info, "prescale": PRESCALE})


def tolerant_sel(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, reselect: bool,
                 mult: float = 3.0, alpha_open: float = 0.10, name: str = "tolerant_v5") -> MethodResult:
    """v3 with targeted instead of full opening when missing edges are stated (module doc).
    Without stated missing edges it is exactly ``tolerant_v3``."""
    n = skel.n
    stated = stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    if k_miss == 0:
        res = tolerant(data, skel, lag_max, H, n_boot, rng, target_reversal=True, name=name)
        return res
    try:
        opened = select_open(data, skel, lag_max, k_miss, mult, alpha_open)
    except ValueError:
        return _failed(name, "underdetermined")

    def terms_for(s: Skeleton, op):
        return [opened_terms(s, op, j, lag_max) for j in range(n)]

    fit0 = fit_equations(data, terms_for(skel, opened), lag_max)
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

    fit = fit_equations(data, terms_for(draw_skel(cands), opened), lag_max) if cands else fit0
    if fit.status != "ok":
        return _failed(name, fit.status)
    n_open = []

    def refit(x):
        if reselect:
            try:
                op = select_open(x, skel, lag_max, k_miss, mult, alpha_open)
            except ValueError:  # selection impossible on this draw: keep the data's selection
                op = opened
            n_open.append(len(op))
            f0 = fit_equations(x, terms_for(skel, op), lag_max)
            if f0.status != "ok":
                return f0
            cs = repair_candidates(f0.residuals, skel, k_miss)
            if not cs and not reversing:
                return f0
            return fit_equations(x, terms_for(draw_skel(cs), op), lag_max)
        return fit_equations(x, terms_for(draw_skel(cands), opened), lag_max)

    draws = bootstrap_C(data, fit, H, n_boot, rng, refit=refit)
    if _too_few(draws, n_boot):
        return _failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, ALPHA)
    theta = irf(fit.B, H)
    return MethodResult(name, "ok", draws.mean(axis=0), lo, hi, theta, fit.B,
                        {"n_repair": len(cands), "n_open": len(opened),
                         "n_open_boot_mean": float(np.mean(n_open)) if n_open else None,
                         "n_reversal_pool": None if pool is None else len(pool)})


def tolerant_v5(data, skel, lag_max, H, n_boot, rng):
    """Targeted opening, re-selected in every bootstrap draw, two-sided calibration."""
    return _prescale(tolerant_sel(data, skel, lag_max, H, n_boot, rng, reselect=True, name="tolerant_v5"),
                     "tolerant_v5")


def tolerant_v5_sel(data, skel, lag_max, H, n_boot, rng):
    """Ablation: targeted opening selected once on the data, two-sided calibration."""
    return _prescale(tolerant_sel(data, skel, lag_max, H, n_boot, rng, reselect=False, name="tolerant_v5_sel"),
                     "tolerant_v5_sel")


def tolerant_v5_cal2(data, skel, lag_max, H, n_boot, rng):
    """Ablation: v3 (all lags) with only the two-sided calibration."""
    return _prescale(tolerant(data, skel, lag_max, H, n_boot, rng, target_reversal=True, name="tolerant_v5_cal2"),
                     "tolerant_v5_cal2")


METHODS = {
    "tolerant_v5": tolerant_v5,
    "tolerant_v5_sel": tolerant_v5_sel,
    "tolerant_v5_cal2": tolerant_v5_cal2,
}
