"""Extension "eiv2" (round 2, synthesis item R2-5): errors-in-variables module, version 2.

Same model, correction, bootstrap and tolerance machinery as ``ext_eiv`` (round 1, evaluated and
left unchanged; see its docstring and docs/ext/eiv.md). The ONE change is in the GMM estimate of
the noise share r (D = r * diag(var(y))):

Round 1 (``ext_eiv.estimate_noise_share``) set the criterion to +inf for every grid value r above
lambda_j of ANY equation j, inside the loop over equations. lambda_j is the smallest generalised
root of det(X_j'X_j - lambda m D_j) = 0 (the largest r for which the corrected Gram matrix of
equation j is still positive definite). So r_hat was capped at min_j lambda_j over all 14
equations, and in finite samples one near-collinear equation was enough to pull r_hat far below
the true share (docs/ext/synthesis_round1.md, 1.2 and X8: 0.193 -> 0.121 at T = 80).

Version 2 (``estimate_noise_share_v2``, mode "pereq"): a per-equation cap. In the criterion,
equation j is corrected with r_j = min(r, GUARD * lambda_j), the same Fuller-type guard that the
fit itself applies (``ext_eiv.fit_corrected``), so an ill-conditioned equation contributes a
partially corrected moment instead of vetoing the whole grid. Every corrected Gram matrix used in
the criterion is checked to be positive definite (Cholesky); a grid point where the check fails
in some equation has that equation's r_j halved until it passes (counted in the diagnostics).
The modes "global" (round-1 behaviour) and "free" (no admissibility handling, like the probe-2
estimator ``experiments/ext/eiv/noise_est.gmm_common``) are kept for the probes only.

The heterogeneous variant ``tolerant_eiv2h`` (probe only unless stated otherwise in
docs/ext/eiv2.md) is not implemented here; heterogeneous noise is tested against the homogeneous
model, see experiments/ext/eiv2/.

Methods:
- ``tolerant_eiv2``  the candidate: tolerant machinery + corrected LS with per-equation capped GMM
                     estimate of r (width-calibrated by the runner via ``calibrate_methods``)
- ``plugin_eiv2``    ablation: corrected LS (per-equation capped r) on the skeleton as given, same
                     bootstrap, no tolerance machinery, no width calibration
"""
from __future__ import annotations

import numpy as np

from .effects import cumulative, irf
from .estimator import parent_terms, percentile_interval, soft_terms
from .ext_eiv import (EXTRA_LAGS, GUARD, R_GRID, _lambda_min, fit_stationary, shock_transform,
                      simulate_noisy)
from .methods import (ALPHA, MethodResult, _failed, _flip_from, _too_few, contemporaneous_pool,
                      repair_candidates, stated_counts)
from .skeleton import Skeleton, _creates_cycle

EST_MODE = "pereq"      # "pereq" (v2), "global" (round-1 cap), "free" (no admissibility handling)
CAP_GUARD = GUARD       # per-equation cap: r_j = min(r, CAP_GUARD * lambda_j)
CRIT = "corr"           # "corr": sum of squared instrument-residual correlations (round 1);
                        # "liml": sum over equations of u'P_Z u / u'u (LIML / Anderson-Rubin-type ratio)


def _is_pd(G: np.ndarray) -> np.ndarray:
    """Positive definiteness of a stack of symmetric matrices (R, k, k), via Cholesky per slice."""
    ok = np.ones(len(G), dtype=bool)
    try:
        np.linalg.cholesky(G)
        return ok
    except np.linalg.LinAlgError:
        pass
    for i, g in enumerate(G):
        try:
            np.linalg.cholesky(g)
        except np.linalg.LinAlgError:
            ok[i] = False
    return ok


def estimate_noise_share_v2(data: np.ndarray, terms: list, p: int, grid: np.ndarray = R_GRID,
                            mode: str = EST_MODE, crit_kind: str | None = None) -> tuple[float, np.ndarray, dict]:
    """GMM estimate of r on the given equations (see module docstring). Returns
    (r_hat, criterion over the grid, diagnostics)."""
    crit_kind = crit_kind or CRIT
    T, n = data.shape
    q = p + EXTRA_LAGS
    rows = np.arange(q, T)
    m = len(rows)
    var = data.var(axis=0)
    crit = np.zeros(len(grid))
    lams = []
    n_fix = 0
    for j, tj in enumerate(terms):
        X = np.column_stack([data[rows - lag, i] for i, lag in tj])
        y = data[rows, j]
        nodes = sorted({j} | {i for i, _ in tj})
        Z = np.column_stack([data[rows - lag, i] for i in nodes for lag in range(p + 1, q + 1)])
        X = X - X.mean(0); y = y - y.mean(); Z = Z - Z.mean(0)
        XX, Xy, ZX, Zy, yy = X.T @ X, X.T @ y, Z.T @ X, Z.T @ y, y @ y
        sdZ = np.sqrt((Z ** 2).mean(0))
        dv = var[[i for i, _ in tj]]
        lam = _lambda_min(XX, m * np.diag(dv))
        lams.append(lam)
        r_eq = np.minimum(grid, CAP_GUARD * lam) if mode == "pereq" else grid.astype(float)
        G = XX[None] - m * r_eq[:, None, None] * np.diag(dv)[None]          # (R, k, k)
        if mode == "pereq":
            ok = _is_pd(G)
            tries = 0
            while not ok.all() and tries < 20:
                n_fix += int((~ok).sum())
                r_eq = np.where(ok, r_eq, r_eq / 2)
                G = XX[None] - m * r_eq[:, None, None] * np.diag(dv)[None]
                ok = _is_pd(G)
                tries += 1
        try:
            b = np.linalg.solve(G, np.broadcast_to(Xy, (len(grid), len(Xy)))[..., None])[..., 0]
        except np.linalg.LinAlgError:
            b = np.stack([np.linalg.lstsq(g, Xy, rcond=None)[0] for g in G])
        Zu = Zy[None] - b @ ZX.T                                            # (R, l)
        uu = yy - 2 * b @ Xy + np.einsum("ri,ij,rj->r", b, XX, b)
        if crit_kind == "liml":
            ZZ = Z.T @ Z
            W = np.linalg.solve(ZZ + 1e-10 * np.trace(ZZ) * np.eye(len(ZZ)), Zu.T)       # (l, R)
            crit += np.einsum("ri,ir->r", Zu, W) / np.maximum(uu, 1e-12)
        else:
            sdu = np.sqrt(np.maximum(uu / m, 1e-12))
            g = Zu / m / (sdu[:, None] * sdZ[None])
            crit += (g ** 2).sum(axis=1)
        if mode == "global":   # round-1 behaviour, kept for the probes
            crit[grid > lam] = np.inf
    best = int(np.argmin(crit)) if np.isfinite(crit).any() else 0
    r_hat = float(grid[best])
    lams = np.array(lams)
    diag = {"lam_min": float(lams.min()), "n_eq_capped": int((CAP_GUARD * lams < r_hat).sum()),
            "n_pd_fix": n_fix}
    return r_hat, crit, diag


# --------------------------------------------------------------------------- methods

def _eiv2(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, tolerant: bool,
          name: str, mode: str = EST_MODE, _r_probe: float | None = None) -> MethodResult:
    """As ``ext_eiv._eiv`` (bias correction off, r re-estimated in every bootstrap draw), with
    the per-equation capped estimator of r. ``_r_probe`` (design probes on the calibration bank
    only, never used by the registered methods) fixes r instead of estimating it, to separate the
    error of r_hat from the rest of the procedure."""
    n = skel.n
    est_terms = [parent_terms(skel, j, lag_max) for j in range(n)]   # equations used to estimate r
    var = data.var(axis=0)
    if _r_probe is None:
        r_hat, _, d0 = estimate_noise_share_v2(data, est_terms, lag_max, mode=mode)
    else:
        r_hat, d0 = float(_r_probe), {"lam_min": float("nan"), "n_eq_capped": -1, "n_pd_fix": 0}

    stated = stated_counts(skel.damage) if tolerant else {"missing": 0, "reversed": 0}
    k_miss, k_rev = stated["missing"], stated["reversed"]
    full_lags = k_miss > 0

    def terms_masks(s: Skeleton):
        if not full_lags:
            return [parent_terms(s, j, lag_max) for j in range(n)], None
        t = [soft_terms(s, j, lag_max) for j in range(n)]
        own = [set(parent_terms(s, j, lag_max)) for j in range(n)]
        return t, [np.array([term in own[j] for term in t[j]], dtype=float) for j in range(n)]

    t0, k0 = terms_masks(skel)
    dvar = r_hat * var
    fit0, applied0, sc0 = fit_stationary(data, t0, lag_max, dvar, k0)
    if fit0.status != "ok":
        return _failed(name, fit0.status)
    dvar = sc0 * dvar
    cands = repair_candidates(fit0.residuals, skel, k_miss)    # raw residual correlation, as v3
    reversing = k_rev > 0
    pool = contemporaneous_pool(data, fit0, k_rev) if reversing else None
    draw_structure = bool(cands) or reversing

    def draw_skel() -> Skeleton:
        s = _flip_from(skel, pool, k_rev, rng) if reversing else skel.copy()
        for u, v in cands:
            e = (u, v) if rng.random() < 0.5 else (v, u)
            if _creates_cycle(s.oriented | {e}, n):
                e = (v, u) if e == (u, v) else (u, v)
            if not _creates_cycle(s.oriented | {e}, n):
                s.oriented.add(e)
        return s

    fit, km = fit0, k0
    if cands:
        t1, km = terms_masks(draw_skel())
        fit, applied0, sc1 = fit_stationary(data, t1, lag_max, dvar, km)
        dvar = sc1 * dvar
        if fit.status != "ok":
            return _failed(name, fit.status)
    shocks, _ = shock_transform(fit, dvar)

    draws, r_boot = [], []
    tries = 0
    while len(draws) < n_boot and tries < 3 * n_boot:
        tries += 1
        yb = simulate_noisy(fit, shocks, dvar, data, rng)
        if not np.all(np.isfinite(yb)):
            continue
        rb = estimate_noise_share_v2(yb, est_terms, lag_max, mode=mode)[0] if _r_probe is None else r_hat
        tb, kb = terms_masks(draw_skel()) if draw_structure else (fit.terms, km)
        fb, _, _ = fit_stationary(yb, tb, lag_max, rb * yb.var(axis=0), kb)
        if fb.status == "ok":
            draws.append(cumulative(irf(fb.B, H), H))
            r_boot.append(rb)
    draws = np.array(draws)
    if _too_few(draws, n_boot):
        return _failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, ALPHA)
    theta = irf(fit.B, H)
    C = draws.mean(axis=0) if draw_structure else cumulative(theta, H)
    info = {"r_hat": r_hat, "r_used": float(np.mean(dvar / var)), "r_boot_mean": float(np.mean(r_boot)),
            "guard_min": float(np.min(applied0)), "lam_min": d0["lam_min"],
            "n_eq_capped": d0["n_eq_capped"], "n_pd_fix": d0["n_pd_fix"],
            "n_repair": len(cands), "full_lags": full_lags}
    return MethodResult(name, "ok", C, lo, hi, theta, fit.B, info)


def tolerant_eiv2(data, skel, lag_max, H, n_boot, rng) -> MethodResult:
    return _eiv2(data, skel, lag_max, H, n_boot, rng, tolerant=True, name="tolerant_eiv2")


def plugin_eiv2(data, skel, lag_max, H, n_boot, rng) -> MethodResult:
    return _eiv2(data, skel, lag_max, H, n_boot, rng, tolerant=False, name="plugin_eiv2")


METHODS = {"tolerant_eiv2": tolerant_eiv2, "plugin_eiv2": plugin_eiv2}
