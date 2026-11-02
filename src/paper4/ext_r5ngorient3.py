"""Round 5, ID "ngorient3": NG-A v3, component (A) of the proposed ``tolerant_v5_2``.

Background: docs/ext/synthesis_round4.md sections 2.2 and 4.1 (A); design and rule: docs/ext/r5ngorient3.md.

NG-A v2 (``ext_r4ngorient.tolerant_ngA``) replaces the two fair coins of ``tolerant_v5_1`` (direction of a
repaired contemporaneous edge, step 3; which pool edges are reversed, step 4) by gated non-Gaussian
pairwise evidence of Hyvarinen and Smith (2013, JMLR 14:111-152). The round-4 verifier found a
construction error in v2's evidence: in the tanh form the sign of the super-/sub-Gaussian correction is
taken from the MEAN excess kurtosis of the pair, which is inconsistent for pairs of different laws
(e.g. t5 -> uniform was wrong 52% of the time at m = 400). v3 changes only the evidence function:

``ng_evidence3(x, y)`` (R > 0 means x -> y):
- standardise x, y over m rows; JB gate exactly as v2 (Sidak over the two series, alpha 0.10);
- form selector exactly as v2: S = m (skew_x^2 + skew_y^2) / 6, K = m (exkurt_x^2 + exkurt_y^2) / 24;
  S >= K: v2's skew form (H-S 2013 eq. 13: each series sign-flipped to positive skewness,
  R = rho mean(x^2 y - x y^2));
- S < K: "lik" form, the approximate log-likelihood ratio of the two directions (H-S 2013 section 2),
      R = mean[ G_x(x) - G_x(r_xy) + G_y(r_yx) - G_y(y) ],
      rho = mean(x y), r_yx = (y - rho x) / sqrt(1 - rho^2), r_xy = (x - rho y) / sqrt(1 - rho^2),
  where G_x is a unit-variance log-density chosen from the sign of x's OWN excess kurtosis and G_y
  from y's own: exkurt >= 0 -> hyperbolic secant, G(u) = -log cosh(pi u / 2) (the log cosh family);
  exkurt < 0 -> generalised Gaussian with shape 4, G(u) = -(u / a)^4, a^2 = Gamma(1/4) / Gamma(3/4).
  Each residual takes the family of the variable it stands in for in its direction (r_yx replaces y in
  x -> y, r_xy replaces x in y -> x), so the normalising constants cancel inside each difference and,
  when both families agree, R is exactly H-S's likelihood ratio with one G;
- forms and families fixed from the full sample; se by v2's delete-one-block jackknife (10 contiguous
  blocks, standardisation and rho redone in each subsample); p = Phi(R / se) clipped to [0.05, 0.95];
  p = 0.5 exactly when the gate is closed.

Everything else is ``ext_r4ngorient``'s NG-A line for line (branches copied below with the evidence
function as a parameter; with ``evidence=ext_r4ngorient.ng_evidence`` they reproduce ``tolerant_ngA``
bit for bit, checked by experiments/ext/r5ngorient3/check_copy.py): per-draw recomputation, step 3
``rng.random() < p_uv``, step 4 Plackett-Luce through Efraimidis-Spirakis keys with w_e = 1 - p(stated
direction), ``methods._flip_from`` when every weight is 0.5, common random numbers with v5_1 (same
number of random-number calls; identical to v5_1 when every gate is closed), v5_1's switch, targeted
opening, BH repair, pool, 199 draws, percentile interval, PRESCALE 0.5. The width factor is
tolerant_v5_1's frozen factor (no re-tune).

Methods read only the data, the public skeleton and ``skel.damage``. Evidence diagnostics are returned in
``info["ng_diag"]`` for the evaluation, which labels them with the truth outside the method.
"""
from __future__ import annotations

import math

import numpy as np

from . import methods as M
from .effects import cumulative, irf
from .estimator import bootstrap_C, fit_equations, parent_terms, percentile_interval, soft_terms
from .ext_narrow import _prescale, opened_terms, select_open
from .ext_r4ngorient import (GATE_ALPHA, N_BLOCKS, P_CLIP, _add_repairs, _Diag, _flip_weighted, _ols_resid,
                             _phi, _std)
from .ext_r4ngorient import ng_evidence as ng_evidence_v2
from .ext_v51 import TAU, allag_ratio
from .skeleton import Skeleton

_HALF_PI = math.pi / 2
_GG4_A4 = (math.gamma(0.25) / math.gamma(0.75)) ** 2       # a^4 with a^2 = Gamma(1/4) / Gamma(3/4)


def g_super(u: np.ndarray) -> np.ndarray:
    """Log-density (without its constant) of the unit-variance hyperbolic secant law: -log cosh(pi u / 2)."""
    z = np.abs(_HALF_PI * u)
    return -(z + np.log1p(np.exp(-2.0 * z)))


def g_sub(u: np.ndarray) -> np.ndarray:
    """Log-density (without its constant) of the unit-variance generalised Gaussian of shape 4."""
    u2 = u * u
    return -(u2 * u2) / _GG4_A4


def _fam(exkurt: float):
    return (g_super, "super") if exkurt >= 0 else (g_sub, "sub")


def ng_evidence3(xr, yr, *, n_blocks: int = N_BLOCKS, gate_alpha: float = GATE_ALPHA) -> dict:
    """Gated per-variable likelihood-ratio evidence that x -> y (module doc). Returns
    {"p", "gate", "gate_p", "R", "se", "form", "fam"}."""
    out = {"p": 0.5, "gate": False, "gate_p": 1.0, "R": 0.0, "se": float("nan"), "form": "none", "fam": ""}
    if xr is None or yr is None:
        return out
    x, y = _std(xr), _std(yr)
    if x is None or y is None:
        return out
    m = len(x)
    skx, sky = float(np.mean(x ** 3)), float(np.mean(y ** 3))
    ekx, eky = float(np.mean(x ** 4)) - 3.0, float(np.mean(y ** 4)) - 3.0
    jbx, jby = m * (skx ** 2 / 6 + ekx ** 2 / 24), m * (sky ** 2 / 6 + eky ** 2 / 24)
    px, py = math.exp(-jbx / 2), math.exp(-jby / 2)   # chi2(2) upper tail
    gate_p = 1 - (1 - min(px, py)) ** 2
    out["gate_p"] = gate_p
    if not gate_p < gate_alpha:
        return out
    out["gate"] = True
    S = m * (skx ** 2 + sky ** 2) / 6
    K = m * (ekx ** 2 + eky ** 2) / 24
    if S >= K:
        form = "skew"
        sx = -1.0 if skx < 0 else 1.0
        sy = -1.0 if sky < 0 else 1.0
        gx = gy = None
        fam = ""
    else:
        form = "lik"
        sx = sy = 1.0
        (gx, fx), (gy, fy) = _fam(ekx), _fam(eky)
        fam = f"{fx}/{fy}"
    xr, yr = np.asarray(xr, float), np.asarray(yr, float)

    def stat(idx) -> float | None:
        a, b = _std(xr[idx]), _std(yr[idx])
        if a is None or b is None:
            return None
        a, b = sx * a, sy * b
        rho = float(np.mean(a * b))
        if form == "skew":
            return rho * float(np.mean(a * a * b - a * b * b))
        if not abs(rho) < 1.0 - 1e-12:
            return None
        s = math.sqrt(1.0 - rho * rho)
        r_yx, r_xy = (b - rho * a) / s, (a - rho * b) / s
        return float(np.mean(gx(a) - gx(r_xy) + gy(r_yx) - gy(b)))

    R = stat(np.arange(m))
    reps = []
    for blk in np.array_split(np.arange(m), n_blocks):
        keep = np.setdiff1d(np.arange(m), blk)
        r = stat(keep)
        if r is not None and math.isfinite(r):
            reps.append(r)
    out["form"], out["fam"] = form, fam
    if R is None or not math.isfinite(R) or len(reps) < 2:
        return out
    reps = np.array(reps)
    B = len(reps)
    se = math.sqrt((B - 1) / B * float(((reps - reps.mean()) ** 2).sum()))
    out["R"], out["se"] = float(R), se
    if not (se > 0 and math.isfinite(se)):
        return out
    out["p"] = min(max(_phi(R / se), P_CLIP[0]), P_CLIP[1])
    return out


# ----------------------------------------------------------------------------- evidence for the draws (arm A)

def pool_probs(x, fitb, pool, lag_max: int, evidence):
    """Probability that each pool edge (stated u -> v) is reversed (``ext_r4ngorient.pool_probs``, arm A)."""
    w, rec = [], []
    for u, v in pool:
        xr = fitb.residuals[:, u]
        tv = [t for t in fitb.terms[v] if t != (u, 0)]
        yr = _ols_resid(x, tv, v, lag_max)
        ev = evidence(xr, yr)
        w.append(1 - ev["p"])
        rec.append((u, v, ev["gate"], ev["p"]))
    return w, rec


def cand_probs(f0, cs, evidence):
    """P(u -> v) for each repair candidate (``ext_r4ngorient.cand_probs``, arm A)."""
    p, rec = [], []
    for u, v in cs:
        ev = evidence(f0.residuals[:, u], f0.residuals[:, v])
        p.append(ev["p"])
        rec.append((u, v, ev["gate"], ev["p"]))
    return p, rec


# ----------------------------------------------------------------------------- branches (copied, arm A only)

def _tolerant_ng(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, evidence,
                 name: str) -> M.MethodResult:
    """``ext_r4ngorient._tolerant_ng`` (arm A) with the evidence function as a parameter."""
    n = skel.n
    stated = M.stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    full_lags = k_miss > 0
    term_j = (lambda s, j: soft_terms(s, j, lag_max)) if full_lags else (lambda s, j: parent_terms(s, j, lag_max))
    terms_of = lambda s: [term_j(s, j) for j in range(n)]  # noqa: E731
    fit0 = fit_equations(data, terms_of(skel), lag_max)
    if fit0.status != "ok":
        return M._failed(name, fit0.status)
    cands = M.repair_candidates(fit0.residuals, skel, k_miss)
    reversing = k_rev > 0
    draw_structure = bool(cands) or reversing
    pool = M.contemporaneous_pool(data, fit0, k_rev) if reversing else None
    diag = _Diag()

    def ev_all(x, fb, record=False):
        pc, rc = cand_probs(fb, cands, evidence) if cands else ([], [])
        w, rp = pool_probs(x, fb, pool, lag_max, evidence) if reversing else ([], [])
        if record:
            diag.data_cands, diag.data_pool = rc, rp
        else:
            diag.gates(rc)
            diag.gates(rp)
        return pc, w

    def draw_skel(pc, w, tally=None) -> Skeleton:
        s = _flip_weighted(skel, pool, w, k_rev, rng) if reversing else skel.copy()
        if tally is not None and reversing:
            diag.flips(pool, s)
        return _add_repairs(s, cands, pc, rng, n, tally)

    pc0, w0 = ev_all(data, fit0, record=True)
    fit = fit_equations(data, terms_of(draw_skel(pc0, w0)), lag_max) if cands else fit0
    if fit.status != "ok":
        return M._failed(name, fit.status)

    def refit(x):
        fb = fit_equations(x, terms_of(skel), lag_max)
        if fb.status != "ok":
            return fb
        pc, w = ev_all(x, fb)
        return fit_equations(x, terms_of(draw_skel(pc, w, diag.cand_tally)), lag_max)

    draws = bootstrap_C(data, fit, H, n_boot, rng, refit=refit if draw_structure else None)
    if M._too_few(draws, n_boot):
        return M._failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, M.ALPHA)
    theta = irf(fit.B, H)
    C = draws.mean(axis=0) if draw_structure else cumulative(theta, H)
    return M.MethodResult(name, "ok", C, lo, hi, theta, fit.B,
                          {"n_repair": len(cands), "full_lags": full_lags,
                           "n_reversal_pool": None if pool is None else len(pool), "ng_diag": diag.as_dict()})


def _sel_dd_ng(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, evidence, name: str,
               mult: float = 3.0, alpha_open: float = 0.10) -> M.MethodResult:
    """``ext_r4ngorient._sel_dd_ng`` (arm A) with the evidence function as a parameter."""
    n = skel.n
    stated = M.stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    try:
        opened = select_open(data, skel, lag_max, k_miss, mult, alpha_open)
    except ValueError:
        return M._failed(name, "underdetermined")

    def terms_for(s: Skeleton, op):
        return [list(dict.fromkeys(opened_terms(s, op, j, lag_max))) for j in range(n)]

    fit0 = fit_equations(data, terms_for(skel, opened), lag_max)
    if fit0.status != "ok":
        return M._failed(name, fit0.status)
    cands = M.repair_candidates(fit0.residuals, skel, k_miss)
    reversing = k_rev > 0
    pool = M.contemporaneous_pool(data, fit0, k_rev) if reversing else None
    diag = _Diag()

    def ev_all(x, fb, cs, record=False):
        pc, rc = cand_probs(fb, cs, evidence) if cs else ([], [])
        w, rp = pool_probs(x, fb, pool, lag_max, evidence) if reversing else ([], [])
        if record:
            diag.data_cands, diag.data_pool = rc, rp
        else:
            diag.gates(rc)
            diag.gates(rp)
        return pc, w

    def draw_skel(cs, pc, w, tally=None) -> Skeleton:
        s = _flip_weighted(skel, pool, w, k_rev, rng) if reversing else skel.copy()
        if tally is not None and reversing:
            diag.flips(pool, s)
        return _add_repairs(s, cs, pc, rng, n, tally)

    pc0, w0 = ev_all(data, fit0, cands, record=True)
    fit = fit_equations(data, terms_for(draw_skel(cands, pc0, w0), opened), lag_max) if cands else fit0
    if fit.status != "ok":
        return M._failed(name, fit.status)
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
        cs = M.repair_candidates(f0.residuals, skel, k_miss)
        if not cs and not reversing:
            return f0
        pc, w = ev_all(x, f0, cs)
        return fit_equations(x, terms_for(draw_skel(cs, pc, w, diag.cand_tally), op), lag_max)

    draws = bootstrap_C(data, fit, H, n_boot, rng, refit=refit)
    if M._too_few(draws, n_boot):
        return M._failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, M.ALPHA)
    theta = irf(fit.B, H)
    return M.MethodResult(name, "ok", draws.mean(axis=0), lo, hi, theta, fit.B,
                          {"n_repair": len(cands), "n_open": len(opened),
                           "n_open_boot_mean": float(np.mean(n_open)) if n_open else None,
                           "n_reversal_pool": None if pool is None else len(pool), "ng_diag": diag.as_dict()})


def v51_ng(data, skel, lag_max, H, n_boot, rng, *, evidence, name: str) -> M.MethodResult:
    """``ext_v51.tolerant_v5_1`` with NG orientation of steps 3 and 4 using ``evidence``."""
    T = data.shape[0]
    k_miss = M.stated_counts(skel.damage)["missing"]
    r = allag_ratio(skel, T, lag_max)
    targeted = k_miss > 0 and TAU is not None and r < TAU
    if targeted:
        res = _sel_dd_ng(data, skel, lag_max, H, n_boot, rng, evidence=evidence, name=name)
    else:
        res = _tolerant_ng(data, skel, lag_max, H, n_boot, rng, evidence=evidence, name=name)
    out = _prescale(res, name)
    out.info.update({"v51_targeted": int(targeted), "v51_ratio": float(r)})
    return out


def tolerant_ngA3(data, skel, lag_max, H, n_boot, rng):
    return v51_ng(data, skel, lag_max, H, n_boot, rng, evidence=ng_evidence3, name="tolerant_ngA3")


def copy_with_v2_evidence(data, skel, lag_max, H, n_boot, rng):
    """Not registered: the copied branches with v2's evidence (must equal ``tolerant_ngA`` bit for bit)."""
    return v51_ng(data, skel, lag_max, H, n_boot, rng, evidence=ng_evidence_v2, name="tolerant_ngA")


METHODS = {"tolerant_ngA3": tolerant_ngA3}
