"""Error, coverage and width against the generator truth (plan section 5.4).

Strength is scored at two levels, pending open question 2: the cumulative effect C(H) of every
ordered pair i -> j (i != j), and, for structural methods, each true cross coefficient. Lag is the
mean lag of the impulse response, with the peak lag as a secondary measure.

Pairs are split by the truth: non-null when |C_true| > tau_effect. A non-null pair whose estimate
is exactly 0 (no path left in the fitted model) is "lost": it counts as uncovered and as a lag
failure, never silently dropped.
"""
from __future__ import annotations

import numpy as np

from .effects import cumulative, irf, mean_lag, peak_lag
from .generator import DynamicSEM
from .methods import ALPHA, MethodResult


def _median(values) -> float | None:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    return float(np.median(values)) if values.size else None


def _mean(values) -> float | None:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    return float(np.mean(values)) if values.size else None


def truth_effects(sem: DynamicSEM, H: int):
    theta = irf(sem.B, H)
    return theta, cumulative(theta, H), mean_lag(theta, H), peak_lag(theta, H)


def interval_score(lo, hi, x, alpha: float = ALPHA):
    """Gneiting and Raftery (2007): width plus 2/alpha times the distance by which x misses."""
    return (hi - lo) + (2 / alpha) * np.maximum(lo - x, 0) + (2 / alpha) * np.maximum(x - hi, 0)


def evaluate(sem: DynamicSEM, res: MethodResult, H: int, *, tau_effect: float = 0.1) -> dict:
    """One summary row for one (truth, skeleton, data, method) run. Pair-level sums are stored
    alongside medians so that pooled rates can be formed across runs."""
    row = {"method": res.name, "status": res.status, **{f"info_{k}": v for k, v in res.info.items()}}
    if res.status != "ok":
        return row
    n = sem.n
    theta_t, C_t, ml_t, pk_t = truth_effects(sem, H)
    off = ~np.eye(n, dtype=bool)
    nonnull = off & (np.abs(C_t) > tau_effect)
    null = off & ~nonnull
    est_zero = res.C == 0.0
    lost = nonnull & est_zero
    kept = nonnull & ~est_zero
    err = res.C - C_t

    row.update({
        "n_nonnull": int(nonnull.sum()),
        "n_lost": int(lost.sum()),
        "C_abs_err_nonnull": _median(np.abs(err[nonnull])),
        "C_rel_err_nonnull": _median(np.abs(err[nonnull]) / np.abs(C_t[nonnull])),
        "C_sign_err_kept": float(np.mean(np.sign(res.C[kept]) != np.sign(C_t[kept]))) if kept.any() else None,
        # Null pairs the fitted model can still reach: how large are the spurious effects?
        "C_abs_spurious": _median(np.abs(res.C[null & ~est_zero])),
    })

    if res.lo is not None:
        inside = (res.lo <= C_t) & (C_t <= res.hi)
        score = interval_score(res.lo, res.hi, C_t)
        width = res.hi - res.lo
        row.update({
            "n_covered_nonnull": int(inside[nonnull].sum()),
            "n_covered_kept": int(inside[kept].sum()),
            "n_kept": int(kept.sum()),
            "coverage_nonnull": float(inside[nonnull].mean()) if nonnull.any() else None,
            "width_kept": _median(width[kept]),
            "iscore_nonnull_mean": _mean(score[nonnull]),
            "iscore_nonnull_median": _median(score[nonnull]),
            "n_null_reach": int((null & ~est_zero).sum()),
            "n_covered_null_reach": int(inside[null & ~est_zero].sum()),
        })

    if res.theta is not None:
        ml_e = mean_lag(res.theta, H)
        pk_e = peak_lag(res.theta, H)
        lag_true = nonnull & np.isfinite(ml_t)
        both = lag_true & np.isfinite(ml_e)
        row.update({
            "lag_defined_rate": float(both.sum() / lag_true.sum()) if lag_true.any() else None,
            "mean_lag_abs_err": _median(np.abs(ml_e[both] - ml_t[both])),
            "peak_lag_hit_kept": float(np.mean(pk_e[kept] == pk_t[kept])) if kept.any() else None,
        })

    if res.B is not None:
        cross = np.ones_like(sem.B, dtype=bool)
        cross[:, np.arange(n), np.arange(n)] = False
        true_terms = (sem.B != 0) & cross
        fitted = (res.B != 0) & cross
        row.update({
            "edge_abs_err_fitted": _median(np.abs(res.B - sem.B)[true_terms & fitted]),
            "edge_share_unfitted": float((true_terms & ~fitted).sum() / true_terms.sum()),
            "edge_abs_spurious": _median(np.abs(res.B)[~true_terms & fitted]),
        })
    return row
