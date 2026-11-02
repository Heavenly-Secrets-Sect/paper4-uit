"""Round-4 candidate "leadlag": a lead-lag residual cross-correlation gate before contemporaneous repair.

Change to ``tolerant_v5_1`` (src/paper4/ext_v51.py), step (3) only. Everything else (targeted lag
opening re-selected per draw, reversal draws, prescale 0.5, two-sided width calibration) is the
module of record, imported and never modified.

Step (3) of v5_1 restores contemporaneous edges between non-adjacent pairs whose structural residuals
(of the fit ``f0`` = skeleton terms + opened lag blocks) are correlated at lag 0: Benjamini-Hochberg at
q = 0.1, the strongest ``k_miss`` pairs. A hidden common cause of two observed nodes leaves the same
lag-0 footprint, so v5_1 adds a spurious contemporaneous edge between co-children.

Gate (sources: Haugh 1976, JASA 71:378-385; Hong 1996, Biometrika 83:615-625; negative-control logic
of Lipsitch, Tchetgen Tchetgen and Cohen 2010, Epidemiology 21:383-388). In the model the structural
shocks are white and mutually independent. If (u, v) carries a missing contemporaneous edge u -> v,
r_v,t = b r_u,t + e_v,t (plus terms absorbed by the opened lags), so the residual cross-correlation
lives at lag 0 only: a *lead* r_u,t+l (l > 0) cannot be caused by r_v,t, and a lag r_u,t-l is
orthogonal to r_v,t once u's lags are in v's equation. A persistent hidden common cause L (AR(1)) of u
and v leaves cross-correlation at non-zero lags too (corr(L_t, L_t+l) = phi^|l|). The gate is Haugh's
portmanteau over l in {-M..M} \\ {0} with his small-sample weight,

    Q = m * sum_{0 < |l| <= M} (m / (m - |l|)) * rho_uv(l)^2  ~  chi2(2M) under no lead-lag dependence,

rho_uv(l) = sum_t r_u,t r_v,t+l / sqrt(sum r_u^2 * sum r_v^2) on the m rows of the fit. The chi2 tail
with even degrees of freedom is computed exactly (Poisson sum). M = 4 when T <= 80 and M = 6 otherwise
(fixed before any run). A BH-significant pair with p_Q < ALPHA_GATE = 0.05 is labelled
"confounded" and not repaired; the next BH-significant pair takes its slot, until ``k_miss`` pairs are
repaired or the BH list ends. This happens on the data and again inside every bootstrap draw (as v5_1
re-runs step (3) in every draw).

With no label the repaired set is exactly ``repair_candidates``' (same BH list, same order, same cap),
so the method reproduces v5_1 draw for draw when the gate never fires, and is v5_1 itself whenever no
missing edge is stated (k_miss = 0: no repair at all).

Variant D (``tolerant_v5_1_leadlag_skel``, added after the D-07H design probe of docs/ext/r4leadlag.md,
before any D-07 run): the BH list and the repair are those of f0 as above, but the gate statistic is
computed on the residuals of the skeleton-only structural fit (the skeleton's own terms, no opened lag
blocks; as in ``ext_narrow.screen_pairs``), on the data and in every draw. The probe showed that the
opened lag blocks of f0 absorb most of the lead-lag footprint of a persistent confounder (variant A
labels 0-4% of co-child pairs), while the skeleton-only residuals keep part of it, at the price of more
false labels on true missing edges.

Known blind spot (stated in the paper): a white-noise (non-persistent) confounder that drives both
children at the same lag is indistinguishable from a contemporaneous edge under Gaussianity.

Methods see only the data, the public skeleton and its stated damage. The per-pair scores in ``info``
are data quantities; any truth-based classification is done by the evaluation driver, not here.
"""
from __future__ import annotations

import math

import numpy as np

from .effects import cumulative, irf
from .estimator import bootstrap_C, fit_equations, parent_terms, percentile_interval, soft_terms
from .ext_narrow import _prescale, opened_terms, select_open
from .ext_v51 import TAU, allag_ratio
from .methods import (ALPHA, MethodResult, _failed, _fisher_p, _flip_from, _too_few, contemporaneous_pool,
                      stated_counts, tolerant)
from .skeleton import Skeleton, _creates_cycle

NAME = "tolerant_v5_1_leadlag"          # variant A: gate on the f0 residuals (the candidate as assigned)
NAME_SKEL = "tolerant_v5_1_leadlag_skel"  # variant D: gate on the skeleton-only structural residuals
ALPHA_GATE = 0.05
BH_Q = 0.1


def gate_M(T: int) -> int:
    """Number of non-zero lags on each side (fixed: 4 at T <= 80, 6 above)."""
    return 4 if T <= 80 else 6


def chi2_sf_even(x: float, df: int) -> float:
    """Upper tail of chi2 with even df = 2M: exp(-x/2) * sum_{k<M} (x/2)^k / k! (exact)."""
    if x <= 0:
        return 1.0
    h = x / 2.0
    term, total = 1.0, 1.0
    for k in range(1, df // 2):
        term *= h / k
        total += term
    return float(min(1.0, math.exp(-h) * total))


def cross_corr(ru: np.ndarray, rv: np.ndarray, M: int) -> dict[int, float]:
    """rho_uv(l) = sum_t ru_t rv_{t+l} / sqrt(sum ru^2 sum rv^2), l in {-M..M} (Haugh 1976, eq. 2.2)."""
    ru = ru - ru.mean()
    rv = rv - rv.mean()
    den = math.sqrt(float(ru @ ru) * float(rv @ rv))
    m = len(ru)
    out = {}
    for l in range(-M, M + 1):
        if den <= 0 or abs(l) >= m:
            out[l] = 0.0
        elif l >= 0:
            out[l] = float(ru[: m - l] @ rv[l:]) / den
        else:
            out[l] = float(ru[-l:] @ rv[: m + l]) / den
    return out


def haugh_q(ru: np.ndarray, rv: np.ndarray, M: int) -> tuple[float, float]:
    """(Q, p) of the lead-lag portmanteau, lag 0 excluded, with the small-sample weight m / (m - |l|)."""
    m = len(ru)
    rho = cross_corr(ru, rv, M)
    q = m * sum((m / (m - abs(l))) * rho[l] ** 2 for l in rho if l != 0)
    return float(q), chi2_sf_even(q, 2 * M)


def bh_ranked(residuals: np.ndarray, skel: Skeleton, q: float = BH_Q) -> list[tuple[float, int, int]]:
    """``methods.repair_candidates`` without the cap: the BH-significant non-adjacent pairs, strongest
    first, as (p, u, v). Same tests, same sort, same step-up rule."""
    m, n = residuals.shape
    corr = np.corrcoef(residuals.T)
    tests = sorted((_fisher_p(corr[u, v], m), u, v)
                   for u in range(n) for v in range(u + 1, n) if not skel.is_adjacent(u, v))
    keep = 0
    for rank, (p, _, _) in enumerate(tests, start=1):
        if p <= q * rank / len(tests):
            keep = rank
    return tests[:keep]


def gated_candidates(residuals: np.ndarray, skel: Skeleton, cap: int, T: int, log: dict | None = None,
                     gate_res: np.ndarray | None = None):
    """Repair set of step (3) with the lead-lag gate (module doc). Returns the list of (u, v) to repair.
    BH runs on ``residuals`` (f0, as v5_1); the gate statistic on ``gate_res`` (default: the same residuals).
    When ``log`` is given, records the BH list, the gate p-values and the labelled pairs."""
    if cap <= 0:
        return []
    G = residuals if gate_res is None else gate_res
    M = gate_M(T)
    ranked = bh_ranked(residuals, skel)
    out, labelled, gate_p = [], [], []
    for p0, u, v in ranked:
        if len(out) == cap:
            break
        _, pq = haugh_q(G[:, u], G[:, v], M)
        gate_p.append([u, v, float(p0), pq])
        if pq < ALPHA_GATE:
            labelled.append([u, v])
            continue
        out.append((u, v))
    if log is not None:
        log.update({"n_bh": len(ranked), "labelled": labelled, "repaired": [list(e) for e in out],
                    "gate_p": gate_p,
                    "ungated": [[u, v] for _, u, v in ranked[:cap]]})
    return out


def pair_scores(residuals: np.ndarray, skel: Skeleton, T: int) -> list[list]:
    """For every non-adjacent pair: [u, v, Fisher p at lag 0, Haugh Q, p_Q] on the given residuals.
    Data quantities only (used for the AUROC diagnostic by the driver)."""
    m, n = residuals.shape
    M = gate_M(T)
    corr = np.corrcoef(residuals.T)
    out = []
    for u in range(n):
        for v in range(u + 1, n):
            if skel.is_adjacent(u, v):
                continue
            qs, pq = haugh_q(residuals[:, u], residuals[:, v], M)
            out.append([u, v, float(_fisher_p(corr[u, v], m)), round(qs, 4), pq])
    return out


def skeleton_residuals(x: np.ndarray, skel: Skeleton, lag_max: int) -> np.ndarray:
    """Structural residuals of the skeleton's own terms (no opened blocks), as in ext_narrow.screen_pairs."""
    return fit_equations(x, [parent_terms(skel, j, lag_max) for j in range(skel.n)], lag_max).residuals


def tolerant_sel_dd_ll(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, mult: float = 3.0,
                       alpha_open: float = 0.10, name: str = NAME, gate_on: str = "f0") -> MethodResult:
    """``ext_v51.tolerant_sel_dd`` (reselect=True) with ``repair_candidates`` replaced by
    ``gated_candidates`` on the data and in every draw; otherwise line for line the same.
    ``gate_on``: "f0" (variant A) or "skel" (variant D, gate statistic on the skeleton-only residuals)."""
    n = skel.n
    T = data.shape[0]
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
    glog: dict = {}
    g0 = skeleton_residuals(data, skel, lag_max) if gate_on == "skel" else None
    cands = gated_candidates(fit0.residuals, skel, k_miss, T, glog, g0)
    scores = pair_scores(fit0.residuals if g0 is None else g0, skel, T)
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
    n_open, d_lab, d_rep, d_bh = [], [], [], []

    def refit(x):
        try:
            op = select_open(x, skel, lag_max, k_miss, mult, alpha_open)
        except ValueError:
            op = opened
        n_open.append(len(op))
        f0 = fit_equations(x, terms_for(skel, op), lag_max)
        if f0.status != "ok":
            return f0
        dl: dict = {}
        gx = skeleton_residuals(x, skel, lag_max) if gate_on == "skel" else None
        cs = gated_candidates(f0.residuals, skel, k_miss, T, dl, gx)
        d_lab.append(len(dl.get("labelled", [])))
        d_rep.append(len(cs))
        d_bh.append(dl.get("n_bh", 0))
        if not cs and not reversing:
            return f0
        return fit_equations(x, terms_for(draw_skel(cs), op), lag_max)

    draws = bootstrap_C(data, fit, H, n_boot, rng, refit=refit)
    if _too_few(draws, n_boot):
        return _failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, ALPHA)
    theta = irf(fit.B, H)
    return MethodResult(name, "ok", draws.mean(axis=0), lo, hi, theta, fit.B,
                        {"n_repair": len(cands), "n_open": len(opened),
                         "n_open_boot_mean": float(np.mean(n_open)) if n_open else None,
                         "n_reversal_pool": None if pool is None else len(pool),
                         "n_dup_terms_data": n_dup_data, "n_dup_terms_total": n_dup[0],
                         "gate_M": gate_M(T), "gate_n_bh": glog.get("n_bh", 0),
                         "gate_n_labelled": len(glog.get("labelled", [])),
                         "gate_labelled": glog.get("labelled", []), "gate_repaired": glog.get("repaired", []),
                         "gate_ungated": glog.get("ungated", []), "gate_p": glog.get("gate_p", []),
                         "gate_scores": scores,
                         "gate_draw_labelled_mean": float(np.mean(d_lab)) if d_lab else None,
                         "gate_draw_repaired_mean": float(np.mean(d_rep)) if d_rep else None,
                         "gate_draw_bh_mean": float(np.mean(d_bh)) if d_bh else None,
                         "gate_draw_any_label_share": float(np.mean(np.array(d_lab) > 0)) if d_lab else None})


def tolerant_ll(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, name: str = NAME,
                gate_on: str = "f0") -> MethodResult:
    """All-lag branch: ``methods.tolerant(target_reversal=True)`` with the gated repair set. Only reached
    when missing edges are stated and r >= TAU (T >= about 194 with 14 nodes; never on the paper's grid)."""
    n = skel.n
    T = data.shape[0]
    stated = stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    if k_miss == 0:
        return tolerant(data, skel, lag_max, H, n_boot, rng, target_reversal=True, name=name)
    terms_of = lambda s: [soft_terms(s, j, lag_max) for j in range(n)]  # noqa: E731
    fit0 = fit_equations(data, terms_of(skel), lag_max)
    if fit0.status != "ok":
        return _failed(name, fit0.status)
    glog: dict = {}
    g0 = skeleton_residuals(data, skel, lag_max) if gate_on == "skel" else None
    cands = gated_candidates(fit0.residuals, skel, k_miss, T, glog, g0)
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
        return _failed(name, fit.status)
    refit = (lambda x: fit_equations(x, terms_of(draw_skel()), lag_max)) if draw_structure else None
    draws = bootstrap_C(data, fit, H, n_boot, rng, refit=refit)
    if _too_few(draws, n_boot):
        return _failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, ALPHA)
    theta = irf(fit.B, H)
    C = draws.mean(axis=0) if draw_structure else cumulative(theta, H)
    return MethodResult(name, "ok", C, lo, hi, theta, fit.B,
                        {"n_repair": len(cands), "full_lags": True,
                         "n_reversal_pool": None if pool is None else len(pool),
                         "gate_M": gate_M(T), "gate_n_bh": glog.get("n_bh", 0),
                         "gate_n_labelled": len(glog.get("labelled", [])),
                         "gate_labelled": glog.get("labelled", []), "gate_repaired": glog.get("repaired", [])})


def _v51_gated(data, skel, lag_max, H, n_boot, rng, name: str, gate_on: str):
    T = data.shape[0]
    k_miss = stated_counts(skel.damage)["missing"]
    r = allag_ratio(skel, T, lag_max)
    targeted = k_miss > 0 and TAU is not None and r < TAU
    if targeted:
        res = tolerant_sel_dd_ll(data, skel, lag_max, H, n_boot, rng, name=name, gate_on=gate_on)
    else:
        res = tolerant_ll(data, skel, lag_max, H, n_boot, rng, name=name, gate_on=gate_on)
    out = _prescale(res, name)
    out.info.update({"v51_targeted": int(targeted), "v51_ratio": float(r)})
    return out


def tolerant_v5_1_leadlag(data, skel, lag_max, H, n_boot, rng):
    """Variant A: ``ext_v51.tolerant_v5_1`` with the lead-lag gate (on the f0 residuals) in step (3)."""
    return _v51_gated(data, skel, lag_max, H, n_boot, rng, NAME, "f0")


def tolerant_v5_1_leadlag_skel(data, skel, lag_max, H, n_boot, rng):
    """Variant D: as A, with the gate statistic on the skeleton-only structural residuals."""
    return _v51_gated(data, skel, lag_max, H, n_boot, rng, NAME_SKEL, "skel")


METHODS = {NAME: tolerant_v5_1_leadlag, NAME_SKEL: tolerant_v5_1_leadlag_skel}
