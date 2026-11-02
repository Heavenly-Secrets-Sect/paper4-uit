"""Round 3, ID "revlag3" (synthesis_round2.md, item R3-4): a feasible comparator for the reversal
branch of the frozen module.

Round 2 found that under stated reversals ``tolerant_v4`` under-covers the pairs affected by the
reversed edges (0.86 at T = 80, 0.91 at T = 150) while an oracle widened to the same width covers
0.94-0.98, and that the gap comes from centring, not width. The oracle knows the true direction;
the module only knows how many contemporaneous edges are reversed. This module asks whether a
method that uses the data's own evidence on orientation closes part of that gap.

Why there is evidence at all. In the skeleton-to-regressor map of estimator.py, an oriented pair
u -> v puts u_t in v's equation, while lags enter both equations of every adjacent pair. The lag
sets of u's and v's equations differ (they have different neighbours), and flipping u -> v changes
which contemporaneous parents each equation has (and possibly v-structures). Flipping an edge
therefore changes the Gaussian likelihood of the structural system in general; it is only unchanged
when the two orientations are equivalent (same neighbours, no v-structure change). ``tolerant_v3``
(the frozen module's machinery) ignores this: each bootstrap draw flips k_rev pairs chosen uniformly
from the pool of significant contemporaneous pairs.

Methods (reversal handling only; with no stated reversal both return ``tolerant_v3`` pre-scaled):

- ``tolerant_v4R``  evidence-weighted orientation draws. For every pair e = (u, v) of the v3 pool
  (``contemporaneous_pool``), dl_e = change in the Gaussian log-likelihood of the structural system
  (equations u and v only change) when e alone is flipped, computed once on the data with the
  skeleton's own terms. Prior probability that e is one of the reversed pairs pi = k_rev / |pool|;
  log posterior odds a_e = logit(pi) + dl_e. Every bootstrap draw orders the pool by a_e + Gumbel
  noise (Plackett-Luce sampling without replacement, i.e. weighted sampling with weights exp(a_e))
  and flips the first k_rev pairs whose flip keeps the oriented part acyclic, exactly as v3 flips
  the first k_rev of a uniform permutation. Everything else is v3: same fit0 as bootstrap DGP, same
  repair branch, same refit per draw, point estimate = mean of the draws. Single change vs v3:
  the flip order is evidence-weighted instead of uniform.
- ``tolerant_v4Rmap`` hard orientation (ablation): flip the k_rev pairs with the largest a_e (same
  acyclicity rule, deterministic), fit that skeleton, residual bootstrap with fixed terms
  (point estimate = fit of the MAP skeleton). No orientation uncertainty in the interval.

Width. Both return the percentile interval pre-scaled by 0.5 about its midpoint (as ext_v51 /
ext_narrow), so the runner's calibration grid 1.0..10 acts as a two-sided factor 0.5..5. The
factor per (T, stated kind) is tuned on D-07H development by the runner's own calibration
(``calibrate_methods``), frozen in experiments/ext/revlag3/frozen_revlag3.json.

Methods read only the data, the public skeleton and its stated damage. No truth.
"""
from __future__ import annotations

import math

import numpy as np

from . import methods as M
from .effects import cumulative, irf
from .estimator import bootstrap_C, fit_equations, parent_terms, percentile_interval, soft_terms
from .skeleton import Skeleton, _creates_cycle

PRESCALE = 0.5


def _prescale(res: M.MethodResult, name: str) -> M.MethodResult:
    if res.status != "ok":
        return M._failed(name, res.status)
    mid, half = (res.lo + res.hi) / 2, (res.hi - res.lo) / 2
    return M.MethodResult(name, "ok", res.C, mid - PRESCALE * half, mid + PRESCALE * half, res.theta, res.B,
                          {**res.info, "prescale": PRESCALE})


def _rss(data: np.ndarray, terms_j, j: int, lag_max: int) -> float | None:
    """Residual sum of squares of one structural equation (OLS with intercept), as fit_equations."""
    T = data.shape[0]
    rows = np.arange(lag_max, T)
    y = data[rows, j]
    if not terms_j:
        return float(((y - y.mean()) ** 2).sum())
    if len(terms_j) + 2 > len(rows):
        return None
    X = np.column_stack([data[rows - lag, i] for i, lag in terms_j])
    Xc, yc = X - X.mean(axis=0), y - y.mean()
    beta = np.linalg.lstsq(Xc, yc, rcond=None)[0]
    r = yc - Xc @ beta
    return float(r @ r)


def orientation_evidence(data: np.ndarray, skel: Skeleton, pool, lag_max: int, full_lags: bool) -> np.ndarray:
    """dl_e for every pair of ``pool``: Gaussian log-likelihood of the structural system with e
    flipped minus that of the skeleton as given (only the equations of u and v change). 0 for a
    flip that would create a directed cycle on its own (it is skipped by every draw anyway)."""
    term = soft_terms if full_lags else parent_terms
    m = data.shape[0] - lag_max
    base_rss = {}
    out = np.zeros(len(pool))
    for idx, (u, v) in enumerate(pool):
        trial = (skel.oriented - {(u, v)}) | {(v, u)}
        if _creates_cycle(trial, skel.n):
            continue
        flipped = skel.copy()
        flipped.oriented = trial
        dl = 0.0
        ok = True
        for j in (u, v):
            if j not in base_rss:
                base_rss[j] = _rss(data, term(skel, j, lag_max), j, lag_max)
            r1 = _rss(data, term(flipped, j, lag_max), j, lag_max)
            r0 = base_rss[j]
            if r0 is None or r1 is None or r0 <= 0 or r1 <= 0:
                ok = False
                break
            dl += -0.5 * m * (math.log(r1) - math.log(r0))
        out[idx] = dl if ok and math.isfinite(dl) else 0.0
    return out


def log_odds(dl: np.ndarray, k: int, n_pool: int) -> np.ndarray:
    pi = min(max(k / max(n_pool, 1), 1e-6), 1 - 1e-6)
    return math.log(pi / (1 - pi)) + dl


def _flip_ordered(skel: Skeleton, pool, order, k: int) -> Skeleton:
    """``methods._flip_from`` with a given order instead of a uniform permutation."""
    out = skel.copy()
    flipped = 0
    for idx in order:
        if flipped == k:
            break
        u, v = pool[idx]
        trial = (out.oriented - {(u, v)}) | {(v, u)}
        if not _creates_cycle(trial, skel.n):
            out.oriented = trial
            flipped += 1
    return out


def _tolerant_ew(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, hard: bool,
                 name: str, temper: float = 1.0, mix: float = 0.0, bag: bool = False) -> M.MethodResult:
    n = skel.n
    stated = M.stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    if k_rev == 0:
        res = M.tolerant(data, skel, lag_max, H, n_boot, rng, target_reversal=True, name=name)
        return res
    full_lags = k_miss > 0
    terms_of = (lambda s: [soft_terms(s, j, lag_max) for j in range(n)]) if full_lags else \
               (lambda s: [parent_terms(s, j, lag_max) for j in range(n)])
    fit0 = fit_equations(data, terms_of(skel), lag_max)
    if fit0.status != "ok":
        return M._failed(name, fit0.status)
    cands = M.repair_candidates(fit0.residuals, skel, k_miss)
    pool = M.contemporaneous_pool(data, fit0, k_rev)
    dl = orientation_evidence(data, skel, pool, lag_max, full_lags)
    a = log_odds(temper * dl, k_rev, len(pool))
    info = {"n_repair": len(cands), "full_lags": full_lags, "n_reversal_pool": len(pool),
            "dl_max": float(dl.max()) if len(dl) else None, "n_dl_pos": int((dl > 0).sum())}

    def add_repairs(s: Skeleton) -> Skeleton:
        for u, v in cands:
            e = (u, v) if rng.random() < 0.5 else (v, u)
            if _creates_cycle(s.oriented | {e}, n):
                e = (v, u) if e == (u, v) else (u, v)
            if not _creates_cycle(s.oriented | {e}, n):
                s.oriented.add(e)
        return s

    if hard:
        order = list(np.argsort(-a, kind="stable"))
        s_map = _flip_ordered(skel, pool, order, k_rev)
        if not cands:
            fit = fit_equations(data, terms_of(s_map), lag_max)
            if fit.status != "ok":
                return M._failed(name, fit.status)
            draws = bootstrap_C(data, fit, H, n_boot, rng)
            if M._too_few(draws, n_boot):
                return M._failed(name, "bootstrap_failed")
            lo, hi = percentile_interval(draws, M.ALPHA)
            theta = irf(fit.B, H)
            return M.MethodResult(name, "ok", cumulative(theta, H), lo, hi, theta, fit.B, info)
        draw_skel = lambda: add_repairs(s_map.copy())  # noqa: E731
    elif bag:
        # parametric bootstrap of the orientation decision: DGP = MAP orientation; in every bootstrap
        # series the evidence is recomputed and the draw's orientation sampled from it
        s_map = _flip_ordered(skel, pool, list(np.argsort(-a, kind="stable")), k_rev)
        fit = fit_equations(data, terms_of(add_repairs(s_map.copy())), lag_max)
        if fit.status != "ok":
            return M._failed(name, fit.status)

        def refit_bag(x):
            ab = log_odds(temper * orientation_evidence(x, skel, pool, lag_max, full_lags), k_rev, len(pool))
            keys = ab + rng.gumbel(size=len(pool))
            sb = add_repairs(_flip_ordered(skel, pool, list(np.argsort(-keys, kind="stable")), k_rev))
            return fit_equations(x, terms_of(sb), lag_max)
        draws = bootstrap_C(data, fit, H, n_boot, rng, refit=refit_bag)
        if M._too_few(draws, n_boot):
            return M._failed(name, "bootstrap_failed")
        lo, hi = percentile_interval(draws, M.ALPHA)
        theta = irf(fit.B, H)
        return M.MethodResult(name, "ok", draws.mean(axis=0), lo, hi, theta, fit.B, info)
    else:
        def draw_skel() -> Skeleton:
            if mix > 0 and rng.random() < mix:
                keys = rng.gumbel(size=len(pool))            # uniform order, as v3
            else:
                keys = a + rng.gumbel(size=len(pool))
            return add_repairs(_flip_ordered(skel, pool, list(np.argsort(-keys, kind="stable")), k_rev))

    fit = fit_equations(data, terms_of(draw_skel()), lag_max) if (cands or hard) else fit0
    if fit.status != "ok":
        return M._failed(name, fit.status)
    refit = lambda x: fit_equations(x, terms_of(draw_skel()), lag_max)  # noqa: E731
    draws = bootstrap_C(data, fit, H, n_boot, rng, refit=refit)
    if M._too_few(draws, n_boot):
        return M._failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, M.ALPHA)
    theta = irf(fit.B, H)
    return M.MethodResult(name, "ok", draws.mean(axis=0), lo, hi, theta, fit.B, info)


def tolerant_v4R(data, skel, lag_max, H, n_boot, rng):
    return _prescale(_tolerant_ew(data, skel, lag_max, H, n_boot, rng, hard=False, name="tolerant_v4R"),
                     "tolerant_v4R")


def tolerant_v4Rmap(data, skel, lag_max, H, n_boot, rng):
    return _prescale(_tolerant_ew(data, skel, lag_max, H, n_boot, rng, hard=True, name="tolerant_v4Rmap"),
                     "tolerant_v4Rmap")


def _variant(name, **kw):
    def fn(data, skel, lag_max, H, n_boot, rng):
        return _prescale(_tolerant_ew(data, skel, lag_max, H, n_boot, rng, hard=False, name=name, **kw), name)
    fn.__name__ = name
    return fn


# Design-probe variants (D-07H development only; docs/ext/revlag3.md, "Probe thiết kế")
PROBE_VARIANTS = {"tolerant_v4R_t05": dict(temper=0.5), "tolerant_v4R_mix": dict(mix=0.5),
                  "tolerant_v4R_bag": dict(bag=True)}

METHODS = {"tolerant_v4R": tolerant_v4R, "tolerant_v4Rmap": tolerant_v4Rmap,
           **{k: _variant(k, **v) for k, v in PROBE_VARIANTS.items()}}
