"""Round 4, candidate "kilianbab": Kilian (1998) bootstrap-after-bootstrap (BaB) bias correction of
the lag coefficients inside ``tolerant_v5_1``, plus a bias-corrected percentile (BC, z0 only) arm.

Sources: Kilian L. (1998) "Small-sample confidence intervals for impulse response functions",
REStat 80(2):218-230; Pope A.L. (1990) JTSA 11(3):249-258 (the small-sample bias of LS in a VAR is
O(1/T) and pulls persistence toward zero); Engsted T., Pedersen T.Q. (2014) Econometrics 2(1):45-71
(bootstrap vs analytic bias correction in VARs, stationarity adjustment); Efron B. (1987) JASA
82(397):171-185 (BC percentile, here with acceleration a = 0); Kilian L. (1999) REStat 81(4):652-660
(percentile-t is unreliable at small T, so it is not used).

What is the same as ``tolerant_v5_1`` (ext_v51.py): steps (1)-(4) - evidence screening, targeted
lag opening re-selected per draw, contemporaneous repair with a random direction per draw, targeted
reversal draws - and the branch switch (``tolerant_sel_dd`` when missing edges are stated and
r < TAU, ``methods.tolerant(target_reversal=True)`` otherwise). The two branch functions are copied
below line for line up to the point where they call ``bootstrap_C``; only the bootstrap differs.

What is new (Kilian 1998, adapted):

Stage 1 (bias estimate, FIXED structure). From the data fit ``fit`` (the fit v5_1 passes to
``simulate_from_fit``), draw B1 = 99 residual-bootstrap series and refit each with ``fit.terms``
fixed: no re-selection, no BH repair, no reversal flip. bias = mean_b(B*_b[1:]) - fit.B[1:], kept
only at lag >= 1 positions present in ``fit.terms``. B0 is never corrected; zeros set by selection
are never touched. (A round-v3 probe read the bias off draws that also re-drew structure, so
orientation variability was counted as bias; that probe made reversed-0.5 worse and was dropped,
docs/decision_rules.md, v3 section.)

Correction with Kilian's stationarity adjustment. If companion_radius(B) >= 1 no correction is
applied. Otherwise B_c[1:] = B[1:] - d * bias with d = 1, lowered in steps of 0.01 until
companion_radius(B_c) < 1.

Stage 2. ``fit_c`` = ``fit`` with B replaced by B_c (same intercept, same original residuals and
degrees of freedom). Every draw simulates from ``fit_c``, re-runs (1)-(4) exactly as v5_1, and then
subtracts d_b * bias at the positions that are both in that draw's lag terms and in the bias
support, with the same per-draw stationarity adjustment, before C(H) = cumulative(irf). Point
estimate = mean of the corrected draws.

Arms (one set of draws; the BC and raw arms are deterministic transforms of the BaB draws, read from
a per-process cache, so differences between arms carry no Monte Carlo noise):
- ``r4kilianbab_bab``    (K1): percentile interval of the corrected draws, pre-scaled 0.5 as v5_1;
                               the runner's two-sided width factor is re-tuned for it (calibrate_methods).
- ``r4kilianbab_babbc``  (KBC): BC endpoints Phi(2 z0 + z_a), z0 = Phi^-1(share of draws < C_hat) per
                               pair, C_hat = C(H) of fit_c (the centre of the bootstrap world),
                               |z0| capped at 0.5, plain percentile for a pair when more than 20% of its
                               draws are tied at one value; pre-scaled 0.5; own re-tuned factor.
- ``r4kilianbab_babraw`` (K0): percentile interval of the corrected draws, no pre-scale, no factor.

Cache ownership: the runner calls extension methods in sorted name order, so ``r4kilianbab_bab``
(a prefix of the other two names) computes the draws with its own random stream whenever it is
listed; the other two arms then reuse them. Called alone, each arm computes the draws with its own
stream (same algorithm, different Monte Carlo draws).

Methods see only the data, the skeleton and its stated damage.
"""
from __future__ import annotations

import hashlib
from statistics import NormalDist

import numpy as np

from .effects import companion_radius, cumulative, irf
from .estimator import Fit, fit_equations, parent_terms, percentile_interval, simulate_from_fit, soft_terms
from .ext_narrow import PRESCALE, _prescale, opened_terms, select_open
from .ext_v51 import TAU, allag_ratio
from .methods import (ALPHA, MethodResult, _failed, _flip_from, _too_few, contemporaneous_pool,
                      repair_candidates, stated_counts)
from .skeleton import Skeleton, _creates_cycle

B1 = 99            # stage-1 bootstrap size (bias estimate)
D_STEP = 0.01      # Kilian's stationarity shrink step
Z0_CAP = 0.5       # BC: cap on |z0|
TIE_SHARE = 0.20   # BC: plain percentile when more than this share of a pair's draws share one value
_ND = NormalDist()


# --------------------------------------------------------------------------- Kilian correction

def lag_mask(terms, lag_max: int, n: int) -> np.ndarray:
    """Boolean (lag_max + 1, n, n) mask of the lag >= 1 coefficients a fit with ``terms`` estimates."""
    m = np.zeros((lag_max + 1, n, n), dtype=bool)
    for j, tj in enumerate(terms):
        for i, lag in tj:
            if lag >= 1:
                m[lag, j, i] = True
    return m


def kilian_correct(B: np.ndarray, bias: np.ndarray) -> tuple[np.ndarray, float, int]:
    """B with B[1:] -= d * bias, d = 1 lowered by 0.01 until the companion radius is < 1
    (Kilian 1998). No correction when B itself is not stationary. Returns (B_c, d, flag) with
    flag 0 = full correction, 1 = shrunk, 2 = not corrected (B non-stationary)."""
    if companion_radius(B) >= 1:
        return B, 0.0, 2
    d = 1.0
    while True:
        Bc = B.copy()
        Bc[1:] -= d * bias[1:]
        if companion_radius(Bc) < 1:
            return Bc, d, int(d < 1.0)
        d = round(d - D_STEP, 2)
        if d <= 0:
            return B, 0.0, 1


def stage1_bias(data: np.ndarray, fit: Fit, lag_max: int, rng, b1: int = B1) -> tuple[np.ndarray, int]:
    """Kilian stage 1 with the structure of ``fit`` held fixed (module doc). Returns the bias array
    (zero outside the lag >= 1 support of fit.terms) and the number of successful refits."""
    acc = np.zeros_like(fit.B)
    ok, tries = 0, 0
    while ok < b1 and tries < 3 * b1:
        tries += 1
        fb = fit_equations(simulate_from_fit(fit, data, rng), fit.terms, lag_max, fit.penalties)
        if fb.status == "ok":
            acc += fb.B
            ok += 1
    if ok == 0:
        return np.zeros_like(fit.B), 0
    bias = acc / ok - fit.B
    bias[0] = 0.0
    bias *= lag_mask(fit.terms, lag_max, data.shape[1])
    return bias, ok


def bab_draws(data, fit: Fit, H: int, n_boot: int, rng, refit=None):
    """Stage 1 + correction of the data fit + stage 2 (module doc). ``refit`` is v5_1's per-draw
    refit (steps 1-4); None means the fixed terms of ``fit``."""
    lag_max = fit.B.shape[0] - 1
    n = data.shape[1]
    bias, n1 = stage1_bias(data, fit, lag_max, rng)
    support = lag_mask(fit.terms, lag_max, n)  # lag >= 1 positions of the data fit (bias is zero elsewhere)
    B_c, d, flag = kilian_correct(fit.B, bias)
    fit_c = Fit(fit.status, B_c, fit.intercept, fit.residuals, fit.dof, fit.terms, fit.penalties)
    refit = refit or (lambda x: fit_equations(x, fit.terms, lag_max, fit.penalties))
    out, flags, ds = [], [], []
    tries = 0
    while len(out) < n_boot and tries < 3 * n_boot:
        tries += 1
        fb = refit(simulate_from_fit(fit_c, data, rng))
        if fb.status != "ok":
            continue
        mask = support & lag_mask(fb.terms, lag_max, n)
        Bb, db, fl = kilian_correct(fb.B, bias * mask)
        out.append(cumulative(irf(Bb, H), H))
        flags.append(fl)
        ds.append(db)
    flags = np.array(flags)
    sup = support[1:]
    info = {
        "bab_n_stage1": n1,
        "bab_d": d,
        "bab_data_flag": flag,
        "bab_radius_raw": companion_radius(fit.B),
        "bab_radius_c": companion_radius(B_c),
        "bab_share_draws_shrunk": float(np.mean(flags == 1)) if len(flags) else None,
        "bab_share_draws_uncorrected": float(np.mean(flags == 2)) if len(flags) else None,
        "bab_mean_d_draws": float(np.mean(ds)) if ds else None,
        "bab_absbias_mean": float(np.abs(bias[1:][sup]).mean()) if sup.any() else 0.0,
    }
    for lag in range(1, lag_max + 1):
        s = support[lag]
        diag = np.zeros((n, n), dtype=bool)
        diag[np.arange(n), np.arange(n)] = True
        info[f"bab_absbias_lag{lag}"] = float(np.abs(bias[lag][s]).mean()) if s.any() else 0.0
        info[f"bab_bias_own_lag{lag}"] = float(bias[lag][s & diag].mean()) if (s & diag).any() else 0.0
        info[f"bab_absbias_cross_lag{lag}"] = float(np.abs(bias[lag][s & ~diag]).mean()) if (s & ~diag).any() else 0.0
    return np.array(out), fit_c, info


# --------------------------------------------------------------------------- v5_1 branches (copied up to the bootstrap)

def _branch_targeted(data, skel: Skeleton, lag_max: int, rng, mult: float = 3.0, alpha_open: float = 0.10):
    """``ext_v51.tolerant_sel_dd`` with reselect=True, k_miss > 0, up to its ``bootstrap_C`` call.
    Returns (fit, refit, draw_structure, info) or a failure status string."""
    n = skel.n
    stated = stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    try:
        opened = select_open(data, skel, lag_max, k_miss, mult, alpha_open)
    except ValueError:
        return "underdetermined"
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
        return fit0.status
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
        return fit.status
    n_open = []

    def refit(x):
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

    info = {"n_repair": len(cands), "n_open": len(opened),
            "n_reversal_pool": None if pool is None else len(pool), "_n_open": n_open}
    return fit, refit, True, info


def _branch_tolerant(data, skel: Skeleton, lag_max: int, rng):
    """``methods.tolerant(target_reversal=True)`` up to its ``bootstrap_C`` call."""
    n = skel.n
    stated = stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    full_lags = k_miss > 0
    terms_of = (lambda s: [soft_terms(s, j, lag_max) for j in range(n)]) if full_lags else \
               (lambda s: [parent_terms(s, j, lag_max) for j in range(n)])
    fit0 = fit_equations(data, terms_of(skel), lag_max)
    if fit0.status != "ok":
        return fit0.status
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

    fit = fit_equations(data, terms_of(draw_skel()), lag_max) if cands else fit0
    if fit.status != "ok":
        return fit.status
    refit = (lambda x: fit_equations(x, terms_of(draw_skel()), lag_max)) if draw_structure else None
    info = {"n_repair": len(cands), "full_lags": full_lags,
            "n_reversal_pool": None if pool is None else len(pool)}
    return fit, refit, draw_structure, info


# --------------------------------------------------------------------------- BC endpoints

def bc_interval(draws: np.ndarray, C_hat: np.ndarray, alpha: float = ALPHA):
    """Efron (1987) BC endpoints per pair with a = 0, |z0| capped, ties -> plain percentile."""
    lo, hi = percentile_interval(draws, alpha)
    nb = draws.shape[0]
    n1, n2 = C_hat.shape
    z_lo, z_hi = _ND.inv_cdf(alpha / 2), _ND.inv_cdf(1 - alpha / 2)
    skipped, capped, z0s = 0, 0, []
    for j in range(n1):
        for i in range(n2):
            d = draws[:, j, i]
            _, counts = np.unique(d, return_counts=True)
            if counts.max() > TIE_SHARE * nb:
                skipped += 1
                continue
            share = float(np.mean(d < C_hat[j, i]))
            if share <= 0.0 or share >= 1.0:
                z0 = Z0_CAP if share >= 1.0 else -Z0_CAP
                capped += 1
            else:
                z0 = _ND.inv_cdf(share)
                if abs(z0) > Z0_CAP:
                    z0 = float(np.sign(z0)) * Z0_CAP
                    capped += 1
            z0s.append(z0)
            a1, a2 = _ND.cdf(2 * z0 + z_lo), _ND.cdf(2 * z0 + z_hi)
            lo[j, i], hi[j, i] = np.quantile(d, (a1, a2))
    tot = n1 * n2
    return lo, hi, {"bc_share_skipped": skipped / tot, "bc_share_capped": capped / tot,
                    "bc_mean_abs_z0": float(np.mean(np.abs(z0s))) if z0s else None,
                    "bc_mean_z0": float(np.mean(z0s)) if z0s else None}


# --------------------------------------------------------------------------- core + cache

_CACHE: dict = {}


def _key(data, skel: Skeleton, lag_max, H, n_boot):
    h = hashlib.sha256(np.ascontiguousarray(data).tobytes()).hexdigest()
    return (h, data.shape, tuple(sorted(skel.oriented)), tuple(sorted(tuple(sorted(p)) for p in skel.undetermined)),
            tuple(sorted(skel.damage.items(), key=lambda kv: kv[0])), lag_max, H, n_boot)


def _core(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng):
    key = _key(data, skel, lag_max, H, n_boot)
    if key in _CACHE:
        return _CACHE[key]
    T = data.shape[0]
    k_miss = stated_counts(skel.damage)["missing"]
    r = allag_ratio(skel, T, lag_max)
    targeted = k_miss > 0 and TAU is not None and r < TAU
    parts = _branch_targeted(data, skel, lag_max, rng) if targeted else _branch_tolerant(data, skel, lag_max, rng)
    if isinstance(parts, str):
        out = {"status": parts}
    else:
        fit, refit, draw_structure, info = parts
        draws, fit_c, binfo = bab_draws(data, fit, H, n_boot, rng, refit=refit)
        n_open = info.pop("_n_open", None)
        if n_open is not None:
            info["n_open_boot_mean"] = float(np.mean(n_open)) if n_open else None
        if _too_few(draws, n_boot):
            out = {"status": "bootstrap_failed"}
        else:
            C_hat = cumulative(irf(fit_c.B, H), H)
            out = {"status": "ok", "draws": draws, "fit_c": fit_c, "C_hat": C_hat,
                   "info": {**info, **binfo, "v51_targeted": int(targeted), "v51_ratio": float(r),
                            "n_draws": int(len(draws))}}
    _CACHE.clear()  # the runner fits all methods of one cell in a row: keep only the latest key
    _CACHE[key] = out
    return out


def _result(name, core, H, lo, hi, extra=None):
    fit_c = core["fit_c"]
    return MethodResult(name, "ok", core["draws"].mean(axis=0), lo, hi, irf(fit_c.B, H), fit_c.B,
                        {**core["info"], **(extra or {})})


def r4kilianbab_bab(data, skel, lag_max, H, n_boot, rng):
    """K1: BaB percentile interval, pre-scaled 0.5 (runner factor re-tuned)."""
    name = "r4kilianbab_bab"
    core = _core(data, skel, lag_max, H, n_boot, rng)
    if core["status"] != "ok":
        return _failed(name, core["status"])
    lo, hi = percentile_interval(core["draws"], ALPHA)
    return _prescale(_result(name, core, H, lo, hi), name)


def r4kilianbab_babbc(data, skel, lag_max, H, n_boot, rng):
    """KBC: BaB draws with BC endpoints, pre-scaled 0.5 (own runner factor)."""
    name = "r4kilianbab_babbc"
    core = _core(data, skel, lag_max, H, n_boot, rng)
    if core["status"] != "ok":
        return _failed(name, core["status"])
    lo, hi, binfo = bc_interval(core["draws"], core["C_hat"], ALPHA)
    return _prescale(_result(name, core, H, lo, hi, binfo), name)


def r4kilianbab_babraw(data, skel, lag_max, H, n_boot, rng):
    """K0: BaB percentile interval, no pre-scale and no factor."""
    name = "r4kilianbab_babraw"
    core = _core(data, skel, lag_max, H, n_boot, rng)
    if core["status"] != "ok":
        return _failed(name, core["status"])
    lo, hi = percentile_interval(core["draws"], ALPHA)
    return _result(name, core, H, lo, hi)


assert PRESCALE == 0.5
METHODS = {
    "r4kilianbab_bab": r4kilianbab_bab,
    "r4kilianbab_babbc": r4kilianbab_babbc,
    "r4kilianbab_babraw": r4kilianbab_babraw,
}
