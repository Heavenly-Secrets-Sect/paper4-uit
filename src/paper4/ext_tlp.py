"""Baseline: Targeted Local Projections (Nemtyrev and Boldea, arXiv 2603.00248, 2026).

The method, as published:
- LP:  beta^LP_h  from regressing y_{j,t+h} on the shock variable y_{i,t} and p lags of every variable.
- VAR: beta^VAR_h, the impulse response of a VAR with q < p lags under the same recursive
       identification (the target).
- TLP: beta^TLP_h = v_h beta^LP_h + (1 - v_h) beta^VAR_h, the ridge estimator that shrinks LP
       toward the target, with the MSE-optimal weight (Theorem 4, eq. 20)

           v_h = max[1 - (Sigma^LP_h - Sigma^COV_h) / (T (beta^LP_h - beta^VAR_h)^2), 0],

       one scalar per horizon (here: per horizon and ordered pair).
- Inference: "mean symmetric double bootstrap" (MSDB). First level: moving-block residual
  bootstrap of the reduced-form VAR (block length T^(1/3)); second level: the same procedure on
  every first-level sample. Variances/covariance are averaged second-level moments (eqs. 23-24);
  the bias part of the weight is re-estimated in every first-level draw; the interval is
  beta^TLP +- q_{1-alpha}(|t_b|) sqrt(Sigma^TLP), t_b studentized by the second-level variance
  and centred at the first-level mean (eqs. 27-28).

Adaptation to Paper 4 (all deviations are listed in docs/ext/tlp.md):
- Target = the plug-in SVAR on the supplied skeleton (estimator.parent_terms, lags 1..lag_max),
  i.e. exactly ``plugin``. Its zero restrictions are the "local misspecification" when the
  skeleton is damaged.
- Shock and identification follow the skeleton as in ``lp_allpast``: the LP for a shock to i
  controls for i's contemporaneous parents in the skeleton, and the target uses B0 from the
  skeleton. Both responses are to a unit structural shock (unit-diagonal Gamma), so they estimate
  the same object when the skeleton is right.
- LP lags p = lag_max + 1 (lag augmentation, as lp_allpast); if the regression leaves fewer than
  MIN_DOF residual degrees of freedom for some shock, p is lowered until it does (at T = 40,
  n = 14 this gives p = 1, fewer lags than the target: deviation from the paper's q <= p).
- Bootstrap DGP: the unrestricted reduced-form VAR(lag_max) (the target without the skeleton's
  zero restrictions), residual rows rescaled by sqrt(rows / dof), moving blocks of length
  round(T^(1/3)). If its companion radius is >= RADIUS_CAP the lag matrices are scaled down to
  RADIUS_CAP so that bootstrap paths stay stationary.
- Estimand: C(H) = sum_h beta^TLP_h (per-horizon weights as in the paper, then summed).
- ``targeted_lp`` uses a single-level bootstrap (B = n_boot): variances and covariance are the
  first-level moments; the weight's bias part is re-estimated in every draw with these fixed
  variances; the interval is C^TLP +- q_{1-alpha}(|C_b - mean C_b|). This is MSDB with the
  second-level variance replaced by a constant, for which the studentization cancels.
- ``targeted_lp_db`` is the double bootstrap (B1 = n_boot, B2 = DB_INNER) and is only used in an
  exploratory probe because of its cost.
- v_h is clipped to [0, 1] (the paper only floors at 0); v_h = 0 when beta^LP = beta^VAR.
"""
from __future__ import annotations

import numpy as np

from .effects import irf
from .estimator import fit_equations, parent_terms
from .methods import ALPHA, MethodResult, _failed
from .skeleton import Skeleton

MIN_DOF = 5
RADIUS_CAP = 0.98
DB_INNER = 49
_TINY = 1e-12


# ----------------------------------------------------------------------------------------------
# estimators on one series

def _lp_lags(T: int, n: int, H: int, lag_max: int, max_parents: int) -> int:
    """The largest p <= lag_max + 1 for which every shock's LP keeps MIN_DOF residual dof (1 if
    none does). At T = 40 with n = 14 this is p = 1 < q = lag_max, a deviation from the paper's
    q <= p: with p = lag_max the LP keeps 1-4 dof and its draws make the interval ~3x wider
    (sanity probe on D-07H, docs/ext/tlp.md)."""
    for p in range(lag_max + 1, 0, -1):
        rows = T - H - p
        cols = 2 + max_parents + n * p              # intercept, shock, parents, lags
        if rows - cols >= MIN_DOF:
            return p
    return 1


def lp_responses(x: np.ndarray, parents: list[list[int]], p: int, H: int) -> np.ndarray:
    """theta_LP[h, j, i]: coefficient of x_{i,t} in the regression of x_{j,t+h} on x_{i,t},
    the skeleton parents of i at t, an intercept and lags 1..p of every node. Common sample
    t = p .. T-H-1 for all horizons (as lp_allpast). Computed by Frisch-Waugh: lags and intercept
    are projected out once, then each shock uses a tiny regression on [x_i, x_pa(i)]."""
    T, n = x.shape
    rows = np.arange(p, T - H)
    W = np.column_stack([np.ones(len(rows))] + [x[rows - lag] for lag in range(1, p + 1)])
    Q, _ = np.linalg.qr(W)
    Y = np.concatenate([x[rows + h] for h in range(H + 1)], axis=1)   # (rows, (H+1) n)
    Z = x[rows]
    Zr = Z - Q @ (Q.T @ Z)
    Yr = Y - Q @ (Q.T @ Y)
    out = np.full((H + 1, n, n), np.nan)
    free = len(rows) - W.shape[1]
    for i in range(n):
        S = [i] + parents[i]
        if free - len(S) < 1:          # infeasible LP for this shock: left NaN, caller uses the target
            continue
        ZS = Zr[:, S]
        beta = np.linalg.lstsq(ZS, Yr, rcond=None)[0][0]               # ((H+1) n,)
        out[:, :, i] = beta.reshape(H + 1, n)
    return out


def _fill(lp: np.ndarray, var: np.ndarray) -> np.ndarray:
    """Shocks whose LP is infeasible take the target's response (weight on LP 0, lambda = inf)."""
    return np.where(np.isnan(lp), var, lp)


def var_responses(x: np.ndarray, terms, lag_max: int, H: int) -> np.ndarray | None:
    fit = fit_equations(x, terms, lag_max)
    if fit.status != "ok":
        return None
    return irf(fit.B, H)


class _VAR:
    """Unrestricted reduced-form VAR(q): the bootstrap DGP."""

    def __init__(self, x: np.ndarray, q: int):
        T, n = x.shape
        rows = np.arange(q, T)
        X = np.column_stack([np.ones(len(rows))] + [x[rows - lag] for lag in range(1, q + 1)])
        beta, *_ = np.linalg.lstsq(X, x[rows], rcond=None)
        resid = x[rows] - X @ beta
        dof = max(len(rows) - X.shape[1], 1)
        self.ok = len(rows) - X.shape[1] >= 1
        self.c = beta[0]
        A = [beta[1 + n * (k - 1): 1 + n * k].T for k in range(1, q + 1)]   # A[k-1][j, i]
        self.radius = _radius(A)
        self.shrunk = 1.0
        if self.radius >= RADIUS_CAP:
            # scale lag k by s^k: the companion eigenvalues scale by s exactly
            s = RADIUS_CAP / self.radius
            A = [a * s ** (k + 1) for k, a in enumerate(A)]
            self.shrunk = s
        self.A = A
        self.q = q
        self.mu = x.mean(axis=0)
        self.resid = (resid - resid.mean(axis=0)) * np.sqrt(len(rows) / dof)
        self.x0 = x[:q]

    def simulate(self, T: int, rng: np.random.Generator) -> np.ndarray:
        """Moving-block residual bootstrap (Bruggemann, Jentsch and Trenkler 2016 style)."""
        m, n = self.resid.shape
        ell = max(1, int(round(T ** (1 / 3))))
        need = T - self.q
        starts = rng.integers(0, m - ell + 1, size=int(np.ceil(need / ell)))
        draws = np.concatenate([self.resid[s: s + ell] for s in starts])[:need]
        x = np.empty((T, n))
        x[: self.q] = self.x0
        # intercept matched to the original mean when the lags were shrunk
        c = self.c if self.shrunk == 1.0 else (np.eye(n) - sum(self.A)) @ self.mu
        for t in range(self.q, T):
            acc = c + draws[t - self.q]
            for k in range(self.q):
                acc = acc + self.A[k] @ x[t - 1 - k]
            x[t] = acc
        return x


def _radius(A: list[np.ndarray]) -> float:
    n, q = A[0].shape[0], len(A)
    comp = np.zeros((n * q, n * q))
    comp[:n] = np.hstack(A)
    if q > 1:
        comp[n:, : n * (q - 1)] = np.eye(n * (q - 1))
    return float(np.max(np.abs(np.linalg.eigvals(comp))))


# ----------------------------------------------------------------------------------------------
# weights

def tlp_weight(lp, var, var_lp, cov):
    """Theorem 4 (eq. 20) with finite-sample variances: T * Var(estimator) = Sigma, so
    v = 1 - (Var_LP - Cov) / (LP - VAR)^2, floored at 0 and (deviation) capped at 1."""
    d2 = (lp - var) ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        v = 1.0 - (var_lp - cov) / d2
    v = np.where(d2 <= _TINY, 0.0, v)
    return np.clip(np.nan_to_num(v, nan=0.0), 0.0, 1.0)


def _moments(lp_draws, var_draws):
    var_lp = lp_draws.var(axis=0, ddof=1)
    cov = ((lp_draws - lp_draws.mean(axis=0)) * (var_draws - var_draws.mean(axis=0))).sum(axis=0) / (len(lp_draws) - 1)
    return var_lp, cov


# ----------------------------------------------------------------------------------------------
# the method

def _setup(data, skel: Skeleton, lag_max: int, H: int):
    T, n = data.shape
    parents = [sorted(u for u, v in skel.oriented if v == i) for i in range(n)]
    p = _lp_lags(T, n, H, lag_max, max(len(pa) for pa in parents))
    terms = [parent_terms(skel, j, lag_max) for j in range(n)]
    return parents, p, terms


def _draws(gen: _VAR, T, parents, p, terms, lag_max, H, B, rng):
    lps, vars_ = [], []
    tries = 0
    while len(lps) < B and tries < 3 * B:
        tries += 1
        xb = gen.simulate(T, rng)
        if not np.all(np.isfinite(xb)):
            continue
        vb = var_responses(xb, terms, lag_max, H)
        if vb is None:
            continue
        lps.append(_fill(lp_responses(xb, parents, p, H), vb))
        vars_.append(vb)
    return np.array(lps), np.array(vars_), xb if lps else None


def targeted_lp(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, double: bool = False,
                inner: int = DB_INNER, name: str = "targeted_lp") -> MethodResult:
    T, n = data.shape
    parents, p, terms = _setup(data, skel, lag_max, H)
    var0 = var_responses(data, terms, lag_max, H)
    if var0 is None:
        return _failed(name, "underdetermined")
    raw0 = lp_responses(data, parents, p, H)
    n_infeasible = int(np.isnan(raw0[0, 0]).sum())
    lp0 = _fill(raw0, var0)
    gen = _VAR(data, lag_max)
    if not gen.ok:
        return _failed(name, "underdetermined")
    info = {"p_lp": p, "n_shock_lp_infeasible": n_infeasible, "var_radius": round(gen.radius, 4), "var_shrunk": gen.shrunk != 1.0}

    if not double:
        lpb, varb, _ = _draws(gen, T, parents, p, terms, lag_max, H, n_boot, rng)
        if len(lpb) < max(10, n_boot // 4):
            return _failed(name, "bootstrap_failed")
        var_lp, cov = _moments(lpb, varb)
        v0 = tlp_weight(lp0, var0, var_lp, cov)
        theta = v0 * lp0 + (1 - v0) * var0
        vb = tlp_weight(lpb, varb, var_lp, cov)                 # bias part re-estimated per draw
        Cb = (vb * lpb + (1 - vb) * varb).sum(axis=1)           # (B, n, n)
        C = theta.sum(axis=0)
        half = np.quantile(np.abs(Cb - Cb.mean(axis=0)), 1 - ALPHA, axis=0)
    else:
        # MSDB: per first-level draw, second-level moments from the VAR re-estimated on that draw
        lp1, var1, mom = [], [], []
        tries = 0
        while len(lp1) < n_boot and tries < 3 * n_boot:
            tries += 1
            xb = gen.simulate(T, rng)
            if not np.all(np.isfinite(xb)):
                continue
            vb1 = var_responses(xb, terms, lag_max, H)
            if vb1 is None:
                continue
            g2 = _VAR(xb, lag_max)
            if not g2.ok:
                continue
            lb1 = _fill(lp_responses(xb, parents, p, H), vb1)
            l2, v2, _ = _draws(g2, T, parents, p, terms, lag_max, H, inner, rng)
            if len(l2) < 5:
                continue
            s_lp, s_cov = _moments(l2, v2)
            w2 = tlp_weight(l2, v2, s_lp, s_cov)                # inner TLP with this draw's own moments
            s_c = (w2 * l2 + (1 - w2) * v2).sum(axis=1).var(axis=0, ddof=1)
            lp1.append(lb1); var1.append(vb1); mom.append((s_lp, s_cov, s_c))
        if len(lp1) < max(10, n_boot // 4):
            return _failed(name, "bootstrap_failed")
        lp1, var1 = np.array(lp1), np.array(var1)
        var_lp = np.mean([m[0] for m in mom], axis=0)          # eq. 24: averaged over b1
        cov = np.mean([m[1] for m in mom], axis=0)
        s_c = np.array([m[2] for m in mom])                     # (B1, n, n)
        v0 = tlp_weight(lp0, var0, var_lp, cov)
        theta = v0 * lp0 + (1 - v0) * var0
        C = theta.sum(axis=0)
        w1 = tlp_weight(lp1, var1, var_lp, cov)
        C1 = (w1 * lp1 + (1 - w1) * var1).sum(axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            t = np.abs(C1 - C1.mean(axis=0)) / np.sqrt(s_c)
        t = np.where(s_c > _TINY, t, 0.0)
        tq = np.quantile(t, 1 - ALPHA, axis=0)
        half = tq * np.sqrt(C1.var(axis=0, ddof=1))             # variance from the original sample's draws
        info["inner"] = inner
    info["v_mean"] = round(float(v0[1:].mean()), 4)             # mean weight on LP, h >= 1
    off = ~np.eye(n, dtype=bool)
    info["v_mean_h0_off"] = round(float(v0[0][off].mean()), 4)
    return MethodResult(name, "ok", C, C - half, C + half, theta, None, info)


# The calibrated variant shares the raw computation with ``targeted_lp`` when both run on the same
# (data, skeleton) in a row, so the evaluation does not pay twice.
_CACHE: dict = {}


def _key(data, skel, lag_max, H, n_boot):
    return (hash(data.tobytes()), data.shape, frozenset(skel.oriented), frozenset(skel.undetermined),
            lag_max, H, n_boot)


def _targeted_lp(data, skel, lag_max, H, n_boot, rng):
    res = targeted_lp(data, skel, lag_max, H, n_boot, rng)
    _CACHE.clear()
    _CACHE[_key(data, skel, lag_max, H, n_boot)] = res
    return res


def _targeted_lp_cal(data, skel, lag_max, H, n_boot, rng):
    """Same estimator; listed in ``calibrate_methods`` so the runner widens it per (T, stated kind)
    on the calibration bank exactly as tolerant_v4. Not part of the published method."""
    hit = _CACHE.get(_key(data, skel, lag_max, H, n_boot))
    res = hit if hit is not None else targeted_lp(data, skel, lag_max, H, n_boot, rng)
    return MethodResult("targeted_lp_cal", res.status, res.C, res.lo, res.hi, res.theta, res.B, dict(res.info))


def _targeted_lp_db(data, skel, lag_max, H, n_boot, rng):
    return targeted_lp(data, skel, lag_max, H, n_boot, rng, double=True, name="targeted_lp_db")


METHODS = {"targeted_lp": _targeted_lp, "targeted_lp_cal": _targeted_lp_cal, "targeted_lp_db": _targeted_lp_db}
