"""Module version 5.1 (direction "v51", round 2): switch between v5's targeted opening and v3's
all-lag opening by the rows-to-regressors ratio of the all-lag fit.

Round 1 (docs/ext/narrow.md) found that targeted opening of off-skeleton lag blocks, re-selected in
every bootstrap draw (``ext_narrow.tolerant_v5``), cuts the interval score at T = 40 by a third,
but costs at T = 150 when many edges are missing, where opening every lag is already cheap
(``tolerant_v5_cal2``, all lags with two-sided calibration, is as good as v4 there). v5.1 uses each
where it is better:

- stated missing edges and r < TAU  -> targeted opening, re-selected per draw (v5, de-duplicated);
- otherwise                         -> v3 (all lags when missing edges are stated; the skeleton's
                                       own terms otherwise), i.e. v5_cal2.

r = (T - lag_max) / (1 + n * lag_max + |oriented pairs| / n) is the number of rows per regressor
of the all-lag fit, averaged over equations (intercept, every node's lags 1..lag_max, the stated
skeleton's contemporaneous parents). It uses only T, lag_max and the stated skeleton.

**De-duplication (bug of ext_narrow, docs/decision_rules.md, last section).** ``ext_narrow.opened_terms``
lists a lag block twice when a repaired contemporaneous edge falls on an opened pair; OLS then splits
the coefficient between the copies and ``fit_equations`` keeps one copy (about half the coefficient).
``tolerant_sel_dd`` below is ``ext_narrow.tolerant_sel`` with the terms de-duplicated
(``list(dict.fromkeys(...))``) and nothing else changed: same screening, same random-number calls,
so it reproduces ``tolerant_sel`` exactly whenever no duplicate occurs. ``ext_narrow.py`` (evaluated
in round 1) is imported, never modified.

TAU was fixed from a design probe on D-07H development only (experiments/ext/v51/probe_tau2.py,
procedure and result in docs/ext/v51.md), before any D-07 run of this module. The D-07 data of
round 1 had already hinted that the switch lies between T = 40 and T = 150.

Both branches return the interval pre-scaled by ext_narrow.PRESCALE = 0.5, so the runner's width
calibration (grid 1.0..10) acts as a two-sided factor 0.5..5 per (T, stated kind). With no stated
missing edge v5.1 is v3 pre-scaled, as v5 and v5_cal2.

Methods see only the data, the skeleton and its stated damage.
"""
from __future__ import annotations

import numpy as np

from .effects import irf
from .estimator import bootstrap_C, fit_equations, percentile_interval
from .ext_narrow import _prescale, opened_terms, select_open
from .methods import (ALPHA, MethodResult, _failed, _flip_from, _too_few, contemporaneous_pool,
                      repair_candidates, stated_counts, tolerant)
from .skeleton import Skeleton, _creates_cycle

TAU = 6.6083  # probe_tau2 on D-07H development (T* = 200, mean r at T = 200); see docs/ext/v51.md


def allag_ratio(skel: Skeleton, T: int, lag_max: int) -> float:
    """Rows per regressor of the all-lag fit, averaged over equations (module doc)."""
    n = skel.n
    return (T - lag_max) / (1 + n * lag_max + len(skel.oriented) / n)


def dedup_terms(skel: Skeleton, opened, j: int, lag_max: int):
    """``ext_narrow.opened_terms`` without duplicate terms (module doc)."""
    return list(dict.fromkeys(opened_terms(skel, opened, j, lag_max)))


def tolerant_sel_dd(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, reselect: bool = True,
                    mult: float = 3.0, alpha_open: float = 0.10, name: str = "tolerant_v5_1") -> MethodResult:
    """``ext_narrow.tolerant_sel`` with de-duplicated terms; otherwise line for line the same."""
    n = skel.n
    stated = stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    if k_miss == 0:
        return tolerant(data, skel, lag_max, H, n_boot, rng, target_reversal=True, name=name)
    try:
        opened = select_open(data, skel, lag_max, k_miss, mult, alpha_open)
    except ValueError:
        return _failed(name, "underdetermined")
    n_dup = [0]

    def terms_for(s: Skeleton, op):
        out = []
        for j in range(n):
            raw = opened_terms(s, op, j, lag_max)
            dd = list(dict.fromkeys(raw))
            n_dup[0] += len(raw) - len(dd)
            out.append(dd)
        return out

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
    n_dup_data = n_dup[0]
    n_open = []

    def refit(x):
        if reselect:
            try:
                op = select_open(x, skel, lag_max, k_miss, mult, alpha_open)
            except ValueError:
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
                         "n_reversal_pool": None if pool is None else len(pool),
                         "n_dup_terms_data": n_dup_data, "n_dup_terms_total": n_dup[0]})


def tolerant_v5_1(data, skel, lag_max, H, n_boot, rng):
    T = data.shape[0]
    k_miss = stated_counts(skel.damage)["missing"]
    r = allag_ratio(skel, T, lag_max)
    targeted = k_miss > 0 and TAU is not None and r < TAU
    if targeted:
        res = tolerant_sel_dd(data, skel, lag_max, H, n_boot, rng, reselect=True, name="tolerant_v5_1")
    else:
        res = tolerant(data, skel, lag_max, H, n_boot, rng, target_reversal=True, name="tolerant_v5_1")
    out = _prescale(res, "tolerant_v5_1")
    out.info.update({"v51_targeted": int(targeted), "v51_ratio": float(r)})
    return out


METHODS = {"tolerant_v5_1": tolerant_v5_1} if TAU is not None else {}
