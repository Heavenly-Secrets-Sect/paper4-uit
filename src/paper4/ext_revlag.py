"""Round 2, ID "revlag" (synthesis item R2-6b): lag output of the frozen module taken from its
structural draws.

``tolerant_v4L`` is the frozen ``tolerant_v4`` (``tolerant_v3`` machinery widened by the frozen
width factor of experiments/calibration/tolerant_v4_frozen.json, keyed by T and the stated damage
kind) with one change in what it *reports*, not in how it estimates C(H) or its interval:

- ``tolerant_v4`` returns ``theta = irf(fit.B)``, the impulse response of one fit: ``fit0`` (the
  skeleton as received) when no contemporaneous edge is repaired, or one fit with a single random
  orientation of the repaired edges otherwise. Its point estimate of C(H), however, is the mean of
  the structural bootstrap draws whenever structure is drawn (repair or reversal draws). Under a
  stated reversal the draws flip contemporaneous edges, but the lag output stays that of the
  received (reversed) skeleton, i.e. that of ``plugin`` (round-1 finding, bug list B11).
- ``tolerant_v4L`` returns ``theta`` = the mean over the same draws of the impulse responses,
  whenever structure is drawn, so that ``cumulative(theta) == C`` exactly, as for C(H). When no
  structure is drawn the output is identical to ``tolerant_v4`` (``irf(fit0.B)``).

Mean lag and peak lag are computed by metrics.evaluate from ``theta``, as for every method.
C, lo and hi are produced exactly as by ``tolerant_v4``: with the same random stream (the
runner's ``rng(6)``) they are bit-identical (checked in experiments/ext/revlag/check_identity.py).
The runner gives an extension method its own stream (``ext_seed``), so in a run the intervals
of ``tolerant_v4L`` differ from those of ``tolerant_v4`` by bootstrap noise only.

The method reads only the data, the public skeleton and ``skel.damage``. The width factor is read
from the frozen calibration file (tuned on D-07H development); the method must NOT be listed in
``calibrate_methods`` (it would be widened twice).

``tolerant_v4L_draws`` also returns the per-draw impulse responses, used by the pair-level runner
of this direction to report a percentile interval for the mean lag (descriptive only).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from . import methods as M
from .effects import cumulative, irf
from .estimator import fit_equations, parent_terms, percentile_interval, simulate_from_fit, soft_terms
from .skeleton import Skeleton, _creates_cycle

_FROZEN = Path(__file__).resolve().parents[2] / "experiments" / "calibration" / "tolerant_v4_frozen.json"
_FACTORS = None


def frozen_factor(T: int, damage: dict) -> float | None:
    global _FACTORS
    if _FACTORS is None:
        _FACTORS = {k: v for k, v in json.loads(_FROZEN.read_text(encoding="utf-8")).items()
                    if not k.startswith("_")}
    return _FACTORS.get(f"mod|{T}|{M.width_key(damage)}")


def tolerant_v4L_draws(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng,
                       name: str = "tolerant_v4L"):
    """``tolerant_v3`` (methods.tolerant with target_reversal=True), re-implemented so that the
    impulse response of every bootstrap draw is kept. The random stream is consumed in exactly the
    same order as methods.tolerant / estimator.bootstrap_C. Returns (MethodResult, theta_draws or
    None); the MethodResult is already widened by the frozen v4 factor."""
    n = skel.n
    stated = M.stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    full_lags = k_miss > 0
    terms_of = (lambda s: [soft_terms(s, j, lag_max) for j in range(n)]) if full_lags else \
               (lambda s: [parent_terms(s, j, lag_max) for j in range(n)])
    fit0 = fit_equations(data, terms_of(skel), lag_max)
    if fit0.status != "ok":
        return M._failed(name, fit0.status), None
    cands = M.repair_candidates(fit0.residuals, skel, k_miss)
    reversing = k_rev > 0
    draw_structure = bool(cands) or reversing
    pool = M.contemporaneous_pool(data, fit0, k_rev) if reversing else None

    def draw_skel() -> Skeleton:
        s = M._flip_from(skel, pool, k_rev, rng) if reversing else skel.copy()
        for u, v in cands:
            e = (u, v) if rng.random() < 0.5 else (v, u)
            if _creates_cycle(s.oriented | {e}, n):
                e = (v, u) if e == (u, v) else (u, v)
            if not _creates_cycle(s.oriented | {e}, n):
                s.oriented.add(e)
        return s

    fit = fit_equations(data, terms_of(draw_skel()), lag_max) if cands else fit0
    if fit.status != "ok":
        return M._failed(name, fit.status), None
    p = fit.B.shape[0] - 1
    refit = (lambda x: fit_equations(x, terms_of(draw_skel()), lag_max)) if draw_structure else \
            (lambda x: fit_equations(x, fit.terms, p, fit.penalties))
    thetas, tries = [], 0
    while len(thetas) < n_boot and tries < 3 * n_boot:          # = estimator.bootstrap_C
        tries += 1
        fb = refit(simulate_from_fit(fit, data, rng))
        if fb.status == "ok":
            thetas.append(irf(fb.B, H))
    if M._too_few(thetas, n_boot):
        return M._failed(name, "bootstrap_failed"), None
    thetas = np.array(thetas)                                     # (draws, H+1, n, n)
    draws = thetas[:, : H + 1].sum(axis=1)                        # C(H) per draw
    lo, hi = percentile_interval(draws, M.ALPHA)
    theta_fit = irf(fit.B, H)
    if draw_structure:
        C = draws.mean(axis=0)
        theta = thetas.mean(axis=0)                               # cumulative(theta) == C
    else:
        C = cumulative(theta_fit, H)
        theta = theta_fit
    info = {"n_repair": len(cands), "full_lags": full_lags,
            "n_reversal_pool": None if pool is None else len(pool), "lag_from_draws": draw_structure}
    raw = M.MethodResult(name, "ok", C, lo, hi, theta, fit.B, info)
    c = frozen_factor(data.shape[0], skel.damage)
    out = M.calibrate_width(raw, c, name)
    return out, (thetas if out.status == "ok" else None)


def tolerant_v4L(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng) -> M.MethodResult:
    return tolerant_v4L_draws(data, skel, lag_max, H, n_boot, rng)[0]


METHODS = {"tolerant_v4L": tolerant_v4L}
