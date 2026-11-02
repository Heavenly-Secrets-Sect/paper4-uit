"""Draft estimators of the white measurement-noise share per series (exploratory probe only).

y_t = x_t + v_t, x a VAR(p), v white with diagonal covariance D. In standardised units
d_i = D_ii / var(y_i). White noise inflates only the lag-0 autocovariance, so for the right d
the Yule-Walker coefficients solved from lags 1..p also fit the deeper autocovariances
p+1..p+m (extended Yule-Walker). The criterion is the misfit at the deeper lags.
"""
from __future__ import annotations

import numpy as np


def autocov(z: np.ndarray, K: int) -> list[np.ndarray]:
    T = len(z)
    zc = z - z.mean(axis=0)
    return [zc[k:].T @ zc[: T - k] / T for k in range(K + 1)]   # G[k] = E[z_t z_{t-k}']


def yw_misfit(G: list[np.ndarray], d: np.ndarray, p: int, m: int) -> float:
    n = G[0].shape[0]
    G0 = G[0] - np.diag(d)
    def g(k):
        if k == 0:
            return G0
        return G[k] if k > 0 else G[-k].T
    R = np.block([[g(b - a) for b in range(p)] for a in range(p)])
    r = np.hstack([g(1 + a) for a in range(p)])
    try:
        A = np.linalg.solve(R.T, r.T).T
    except np.linalg.LinAlgError:
        return np.inf
    tot = 0.0
    for k in range(p + 1, p + m + 1):
        pred = sum(A[:, l * n:(l + 1) * n] @ g(k - 1 - l) for l in range(p))
        tot += float(((G[k] - pred) ** 2).sum())
    return tot


def common_ratio(data: np.ndarray, p: int, m: int = 2, grid=None) -> float:
    z = (data - data.mean(0)) / data.std(0)
    G = autocov(z, p + m)
    grid = np.arange(0.0, 0.61, 0.01) if grid is None else grid
    vals = [yw_misfit(G, np.full(z.shape[1], r), p, m) for r in grid]
    return float(grid[int(np.argmin(vals))])


def per_series(data: np.ndarray, p: int, m: int = 2, iters: int = 30, hi: float = 0.7) -> np.ndarray:
    """Coordinate descent on a grid, started at the common ratio."""
    z = (data - data.mean(0)) / data.std(0)
    n = z.shape[1]
    G = autocov(z, p + m)
    r0 = common_ratio(data, p, m)
    d = np.full(n, r0)
    grid = np.arange(0.0, hi + 1e-9, 0.02)
    for _ in range(3):
        for i in range(n):
            best = (np.inf, d[i])
            for v in grid:
                dd = d.copy(); dd[i] = v
                f = yw_misfit(G, dd, p, m)
                if f < best[0]:
                    best = (f, v)
            d[i] = best[1]
    return d


# ----------------------------------------------------------------------------- GMM on skeleton equations

def design(data, terms, p, extra_lags):
    """Per equation: regressors X (centred), target y (centred), instruments Z (deeper lags of the
    nodes in the equation, centred) on common rows."""
    T, n = data.shape
    q = p + extra_lags
    rows = np.arange(q, T)
    out = []
    for j, tj in enumerate(terms):
        X = np.column_stack([data[rows - lag, i] for i, lag in tj])
        y = data[rows, j]
        nodes = sorted({j} | {i for i, _ in tj})
        Z = np.column_stack([data[rows - lag, i] for i in nodes for lag in range(p + 1, q + 1)])
        out.append((X - X.mean(0), y - y.mean(), Z - Z.mean(0), [i for i, _ in tj]))
    return out


def corrected_beta(X, y, idx, dvar, m):
    """(X'X - m D_X)^{-1} X'y; dvar is the noise variance per node (data units)."""
    G = X.T @ X - m * np.diag(dvar[idx])
    return np.linalg.solve(G, X.T @ y)


def gmm_common(data, terms, p, extra_lags=2, grid=None):
    var = data.var(0)
    eqs = design(data, terms, p, extra_lags)
    m = len(eqs[0][1])
    grid = np.arange(0.0, 0.61, 0.01) if grid is None else grid
    vals = []
    for r in grid:
        dvar = r * var
        tot = 0.0
        for X, y, Z, idx in eqs:
            try:
                b = corrected_beta(X, y, idx, dvar, m)
            except np.linalg.LinAlgError:
                tot = np.inf; break
            u = y - X @ b
            g = Z.T @ u / m
            # standardise by sd of u and Z columns -> correlations
            g = g / (u.std() * Z.std(0))
            tot += float((g ** 2).sum())
        vals.append(tot)
    vals = np.array(vals)
    return float(grid[int(np.argmin(vals))]), vals
