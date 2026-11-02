"""Extension "eiv": the tolerant module made robust to measurement error (errors-in-variables).

Model. The observed series is y_t = x_t + v_t, where x_t follows the recursive SVAR of the
module and v_t is white measurement error, independent across series and time, with diagonal
covariance D. Least squares on y attenuates every coefficient (regression dilution), so C(H) is
pulled towards 0 and the bootstrap, which resamples the same attenuated fit, does not see it.

Correction (Fuller 1987, "corrected least squares", method-of-moments errors-in-variables):

    beta_j = (X_j' X_j - m D_{X_j})^{-1} X_j' y_j

where D_{X_j} holds the noise variance of each regressor. Lagged regressors carry noise from
another time point than the target, so no covariance term between target and regressors needs
correcting. A Fuller-type guard keeps the corrected Gram matrix well conditioned: with lambda the
smallest generalised root of det(X'X - lambda m D_X) = 0, the correction is scaled to
min(1, 0.7 lambda), so no direction of the regressor space has its signal amplified by more
than 1 / (1 - 0.7) (GUARD; 0.9 and 0.5 were also probed, docs/ext/eiv.md). A corrected fit that
is not stationary has its correction scaled back by 0.8 until it is.

Noise variance (never read from the generator). D = r * diag(var(y)) with one reliability
parameter r, the share of each observed variance that is white noise (homogeneous reliability).
r is estimated by GMM on the equations of the given skeleton (``parent_terms``): measurement
error is serially uncorrelated, so with the right D the corrected residual of every equation is
orthogonal to the deeper lags p+1, p+2 of the nodes in that equation (instruments of
Hansen-Sargent / Durbin type). The criterion is the sum of squared instrument-residual
correlations over all equations; r is the minimiser on a grid over [0, 0.6]. A probe on the
calibration bank (docs/ext/eiv.md) showed this to be close to unbiased at noise ratios 0, 0.1,
0.3 for the true skeleton and for 20% missing, extra or reversed damage; the unrestricted
extended Yule-Walker version was not (it returned r near 0 at T = 80-150).

Uncertainty. Bootstrap of the whole procedure: structural shocks are the corrected residuals
transformed to the corrected shock covariance Sigma_e = Cov(resid) - N(D) with
N = (I - B0) D (I - B0)' + sum_k B_k D B_k' (the noise part of the residual), whole rows
resampled; x* is simulated from the corrected fit; white noise N(0, D) is added to get y*; r is
re-estimated on y* and the corrected fit redone.

Tolerance. The machinery of ``tolerant_v3`` is kept: all lags when missing edges are stated (only
the skeleton's own terms, incl. repaired contemporaneous edges, are corrected; the added lag block
enters uncorrected, as controls, because correcting it was unstable), contemporaneous repair from
the raw structural residual correlation exactly as v3 (the noise-corrected correlation inflated
false repairs), targeted reversal draws. ``tolerant_eiv`` is listed in ``calibrate_methods``, so
its width is tuned per (T, stated kind) on clean data of the calibration bank, as for tolerant_v4.
A bootstrap bias correction of r is implemented (``bias_correct``) but off: it raised the
interval score in the probes.

Methods:
- ``tolerant_eiv``   the module with the correction (the candidate; width-calibrated by the runner)
- ``plugin_eiv``     ablation: corrected least squares on the skeleton as given, same bootstrap,
                     no tolerance machinery, no width calibration
"""
from __future__ import annotations

import numpy as np

from .effects import companion_radius, cumulative, irf
from .estimator import Fit, parent_terms, percentile_interval, soft_terms
from .methods import (ALPHA, MethodResult, _failed, _fisher_p, _flip_from, _too_few,
                      contemporaneous_pool, repair_candidates, stated_counts)
from .skeleton import Skeleton, _creates_cycle

R_GRID = np.round(np.arange(0.0, 0.6001, 0.01), 3)
EXTRA_LAGS = 2          # instruments: lags p+1 .. p+EXTRA_LAGS
GUARD = 0.7             # Fuller-type guard: correction scaled to at most GUARD * lambda_min
RHO_MAX = 0.99          # corrected fits must stay stationary
N_PILOT = 49            # pilot bootstrap draws for the bias correction of r
BOOT_REESTIMATE = True  # re-estimate r in every bootstrap draw
GUARD_MODE = "ratio"    # "ratio": s = min(1, GUARD*lambda); "minus1": s = min(1, lambda - 1)
REPAIR_CORRECTED = False  # repair test on the noise-corrected shock covariance (inflates correlations)


# --------------------------------------------------------------------------- noise share by GMM

def estimate_noise_share(data: np.ndarray, terms: list, p: int, grid: np.ndarray = R_GRID) -> tuple[float, np.ndarray]:
    """GMM estimate of r (D = r * diag(var(y))) on the given equations, vectorised over the grid."""
    T, n = data.shape
    q = p + EXTRA_LAGS
    rows = np.arange(q, T)
    m = len(rows)
    var = data.var(axis=0)
    crit = np.zeros(len(grid))
    for j, tj in enumerate(terms):
        X = np.column_stack([data[rows - lag, i] for i, lag in tj])
        y = data[rows, j]
        nodes = sorted({j} | {i for i, _ in tj})
        Z = np.column_stack([data[rows - lag, i] for i in nodes for lag in range(p + 1, q + 1)])
        X = X - X.mean(0); y = y - y.mean(); Z = Z - Z.mean(0)
        XX, Xy, ZX, Zy, yy = X.T @ X, X.T @ y, Z.T @ X, Z.T @ y, y @ y
        sdZ = np.sqrt((Z ** 2).mean(0))
        dv = var[[i for i, _ in tj]]
        G = XX[None] - m * grid[:, None, None] * np.diag(dv)[None]          # (R, k, k)
        try:
            b = np.linalg.solve(G, np.broadcast_to(Xy, (len(grid), len(Xy)))[..., None])[..., 0]
        except np.linalg.LinAlgError:
            b = np.stack([np.linalg.lstsq(g, Xy, rcond=None)[0] for g in G])
        Zu = Zy[None] - b @ ZX.T                                            # (R, l)
        uu = yy - 2 * b @ Xy + np.einsum("ri,ij,rj->r", b, XX, b)
        sdu = np.sqrt(np.maximum(uu / m, 1e-12))
        g = Zu / m / (sdu[:, None] * sdZ[None])
        crit += (g ** 2).sum(axis=1)
        # an indefinite corrected Gram matrix is not admissible
        lam = _lambda_min(XX, m * np.diag(dv))
        crit[grid > lam] = np.inf
    best = int(np.argmin(crit)) if np.isfinite(crit).any() else 0
    return float(grid[best]), crit


def _lambda_min(XX: np.ndarray, M: np.ndarray) -> float:
    """Smallest lambda with det(XX - lambda M) = 0 for diagonal M >= 0 (inf if M = 0)."""
    d = np.diag(M)
    if not np.any(d > 0):
        return np.inf
    try:
        A = np.linalg.inv(XX)
    except np.linalg.LinAlgError:
        return 0.0
    r = np.sqrt(d)
    K = A * r[:, None] * r[None, :]
    top = float(np.linalg.eigvalsh((K + K.T) / 2)[-1])
    return 1.0 / top if top > 0 else np.inf


# --------------------------------------------------------------------------- corrected fit

def fit_corrected(data: np.ndarray, terms: list, p: int, dvar: np.ndarray,
                  masks: list | None = None) -> tuple[Fit, np.ndarray]:
    """Corrected least squares per equation (see module docstring); returns the Fit and the
    correction factor actually applied per equation (1 = full correction). ``masks[j]`` (bool per
    term) restricts the correction to some regressors; the others enter uncorrected, as controls."""
    T, n = data.shape
    rows = np.arange(p, T)
    m = len(rows)
    B = np.zeros((p + 1, n, n))
    intercept = np.zeros(n)
    resid = np.zeros((m, n))
    dof = np.zeros(n)
    applied = np.ones(n)
    if not np.all(np.isfinite(data)):
        return Fit("nonfinite", B, intercept, resid, dof, terms), applied
    for j in range(n):
        tj = terms[j]
        y = data[rows, j]
        if len(tj) + 2 > m:
            return Fit("underdetermined", B, intercept, resid, dof, terms), applied
        X = np.column_stack([data[rows - lag, i] for i, lag in tj])
        xm, ym = X.mean(axis=0), y.mean()
        Xc, yc = X - xm, y - ym
        XX = Xc.T @ Xc
        dx = dvar[[i for i, _ in tj]]
        if masks is not None:
            dx = dx * masks[j]
        M = m * np.diag(dx)
        s = 1.0
        if np.any(dvar > 0):
            lam = _lambda_min(XX, M)
            s = min(1.0, GUARD * lam) if GUARD_MODE == "ratio" else min(1.0, max(0.0, lam - 1.0))
        applied[j] = s
        if not np.all(np.isfinite(XX)):
            return Fit("nonfinite", B, intercept, resid, dof, terms), applied
        try:
            beta = np.linalg.solve(XX - s * M, Xc.T @ yc)
        except np.linalg.LinAlgError:
            return Fit("singular", B, intercept, resid, dof, terms), applied
        intercept[j] = ym - xm @ beta
        for (i, lag), b in zip(tj, beta):
            B[lag, j, i] = b
        resid[:, j] = yc - Xc @ beta
        dof[j] = m - 1 - len(tj)
    return Fit("ok", B, intercept, resid, dof, terms), applied


def fit_stationary(data, terms, p, dvar, masks=None, rho_max: float = RHO_MAX):
    """fit_corrected, with the correction scaled back (factor 0.8 at a time, at most 10 times,
    then none) while the corrected fit is not stationary (companion radius >= rho_max).
    Returns (fit, applied correction per equation, scale of D used)."""
    scale = 1.0
    for _ in range(11):
        fit, applied = fit_corrected(data, terms, p, scale * dvar, masks)
        if fit.status != "ok" or companion_radius(fit.B) < rho_max:
            return fit, applied, scale
        scale *= 0.8
    fit, applied = fit_corrected(data, terms, p, 0 * dvar)
    return fit, applied, 0.0


def noise_part(B: np.ndarray, dvar: np.ndarray) -> np.ndarray:
    """Covariance of the measurement-noise part of the structural residual."""
    n = B.shape[1]
    D = np.diag(dvar)
    M0 = np.eye(n) - B[0]
    N = M0 @ D @ M0.T
    for k in range(1, B.shape[0]):
        N += B[k] @ D @ B[k].T
    return N


def shock_transform(fit: Fit, dvar: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Rescaled residual rows R (centred, dof-corrected) and the matrix W such that R @ W has
    covariance Sigma_e = Cov(R) - N(D), eigenvalues floored at 5% of the mean residual variance.
    Returns (shocks R @ W, Sigma_e)."""
    m = len(fit.residuals)
    R = (fit.residuals - fit.residuals.mean(axis=0)) * np.sqrt(m / np.maximum(fit.dof, 1.0))
    S = R.T @ R / m
    Se = S - noise_part(fit.B, dvar)
    floor = 0.05 * float(np.mean(np.diag(S)))
    ev, V = np.linalg.eigh((Se + Se.T) / 2)
    Se = (V * np.maximum(ev, floor)) @ V.T
    es, Vs = np.linalg.eigh((S + S.T) / 2)
    S_inv_half = (Vs / np.sqrt(np.maximum(es, 1e-12))) @ Vs.T
    ev2, V2 = np.linalg.eigh(Se)
    Se_half = (V2 * np.sqrt(np.maximum(ev2, 0))) @ V2.T
    return R @ (S_inv_half @ Se_half), Se


def simulate_noisy(fit: Fit, shocks: np.ndarray, dvar: np.ndarray, data: np.ndarray,
                   rng: np.random.Generator) -> np.ndarray:
    T, n = data.shape
    p = fit.B.shape[0] - 1
    A = np.linalg.inv(np.eye(n) - fit.B[0])
    m = len(shocks)
    draws = shocks[rng.integers(0, m, size=T - p)]
    x = np.zeros_like(data)
    x[:p] = data[:p]
    for t in range(p, T):
        acc = fit.intercept + draws[t - p]
        for k in range(1, p + 1):
            acc = acc + fit.B[k] @ x[t - k]
        x[t] = A @ acc
    return x + rng.normal(size=x.shape) * np.sqrt(dvar)


def repair_from_cov(Se: np.ndarray, m: int, skel: Skeleton, cap: int, q: float = 0.1) -> list[tuple[int, int]]:
    """As methods.repair_candidates, but on the noise-corrected structural shock covariance."""
    if cap <= 0:
        return []
    n = Se.shape[0]
    sd = np.sqrt(np.diag(Se))
    corr = Se / np.outer(sd, sd)
    tests = sorted((_fisher_p(corr[u, v], m), u, v)
                   for u in range(n) for v in range(u + 1, n) if not skel.is_adjacent(u, v))
    keep = 0
    for rank, (pv, _, _) in enumerate(tests, start=1):
        if pv <= q * rank / len(tests):
            keep = rank
    return [(u, v) for _, u, v in tests[:keep]][:cap]


# --------------------------------------------------------------------------- methods

def _eiv(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, tolerant: bool, name: str,
         bias_correct: bool = False) -> MethodResult:
    n = skel.n
    est_terms = [parent_terms(skel, j, lag_max) for j in range(n)]   # equations used to estimate r
    var = data.var(axis=0)
    r_hat, _ = estimate_noise_share(data, est_terms, lag_max)

    stated = stated_counts(skel.damage) if tolerant else {"missing": 0, "reversed": 0}
    k_miss, k_rev = stated["missing"], stated["reversed"]
    full_lags = k_miss > 0

    def terms_masks(s: Skeleton):
        """Regressors of the module and which of them are corrected: with full lags, only the
        skeleton's own terms (incl. repaired contemporaneous edges) are corrected; the added lag
        block is a safety net entered as uncorrected controls."""
        if not full_lags:
            t = [parent_terms(s, j, lag_max) for j in range(n)]
            return t, None
        t = [soft_terms(s, j, lag_max) for j in range(n)]
        own = [set(parent_terms(s, j, lag_max)) for j in range(n)]
        return t, [np.array([term in own[j] for term in t[j]], dtype=float) for j in range(n)]

    t0, k0 = terms_masks(skel)
    fit0, _, sc0 = fit_stationary(data, t0, lag_max, r_hat * var, k0)
    if fit0.status != "ok":
        return _failed(name, fit0.status)

    # bootstrap bias correction of r (the GMM estimate is pulled towards 0 by weak instruments)
    bias = 0.0
    if bias_correct and r_hat > 0:
        shocks0, _ = shock_transform(fit0, sc0 * r_hat * var)
        pilot = []
        for _ in range(N_PILOT):
            yb = simulate_noisy(fit0, shocks0, sc0 * r_hat * var, data, rng)
            if np.all(np.isfinite(yb)):
                pilot.append(estimate_noise_share(yb, est_terms, lag_max)[0])
        if pilot:
            bias = float(np.mean(pilot)) - r_hat
    r_use = float(np.clip(r_hat - bias, 0.0, R_GRID[-1]))
    dvar = r_use * var

    fit0, applied0, sc0 = fit_stationary(data, t0, lag_max, dvar, k0)
    if fit0.status != "ok":
        return _failed(name, fit0.status)
    dvar = sc0 * dvar          # the noise level actually used (backed off if the fit was explosive)
    if REPAIR_CORRECTED:
        _, Se0 = shock_transform(fit0, dvar)
        cands = repair_from_cov(Se0, len(fit0.residuals), skel, k_miss)
    else:   # raw structural residual correlation, as tolerant_v3 (see docs/ext/eiv.md, probe 4)
        cands = repair_candidates(fit0.residuals, skel, k_miss)
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
        if BOOT_REESTIMATE:
            rb, _ = estimate_noise_share(yb, est_terms, lag_max)
            rb = float(np.clip(rb - bias, 0.0, R_GRID[-1]))
        else:
            rb = float(np.mean(dvar / var))
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
    info = {"r_hat": r_hat, "r_bias": bias, "r_used": float(np.mean(dvar / var)),
            "r_boot_mean": float(np.mean(r_boot)), "guard_min": float(np.min(applied0)),
            "n_repair": len(cands), "full_lags": full_lags}
    return MethodResult(name, "ok", C, lo, hi, theta, fit.B, info)


def tolerant_eiv(data, skel, lag_max, H, n_boot, rng) -> MethodResult:
    return _eiv(data, skel, lag_max, H, n_boot, rng, tolerant=True, name="tolerant_eiv")


def plugin_eiv(data, skel, lag_max, H, n_boot, rng) -> MethodResult:
    return _eiv(data, skel, lag_max, H, n_boot, rng, tolerant=False, name="plugin_eiv")


METHODS = {"tolerant_eiv": tolerant_eiv, "plugin_eiv": plugin_eiv}
