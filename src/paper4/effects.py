"""Impulse responses and the effect summaries reported by Paper 4.

Coefficient arrays have shape (lag_max + 1, n, n): ``B[k, j, i]`` is the effect of x_i at t-k
on x_j at t, so ``B[0]`` holds the contemporaneous edges. The model is

    x_t = B[0] x_t + sum_{k>=1} B[k] x_{t-k} + e_t.
"""
from __future__ import annotations

import numpy as np


def irf(B: np.ndarray, H: int) -> np.ndarray:
    """Responses to a unit structural shock: ``theta[h, j, i]`` is the change in x_j at t+h
    after e_i rises by one at t, relative to no shock."""
    p = B.shape[0] - 1
    n = B.shape[1]
    A = np.linalg.inv(np.eye(n) - B[0])
    theta = np.zeros((H + 1, n, n))
    theta[0] = A
    for h in range(1, H + 1):
        acc = np.zeros((n, n))
        for k in range(1, min(h, p) + 1):
            acc += B[k] @ theta[h - k]
        theta[h] = A @ acc
    return theta


def cumulative(theta: np.ndarray, H: int) -> np.ndarray:
    """C(H) = sum_{h=0..H} theta(h), for every (j, i) pair."""
    return theta[: H + 1].sum(axis=0)


def mean_lag(theta: np.ndarray, H: int, tau: float = 1e-3, max_opposite: float = 0.1) -> np.ndarray:
    """sum h|theta| / sum |theta| over h = 0..H.

    Undefined (NaN) when |C(H)| <= tau, or when the mass of the response with the sign opposite
    to C(H) exceeds ``max_opposite`` of the total: a response that largely cancels itself out has
    no meaningful delay. A small opposite mass is tolerated because estimation noise fills the
    exact zeros of the true response with values of either sign.
    """
    th = theta[: H + 1]
    absth = np.abs(th)
    total = absth.sum(axis=0)
    h = np.arange(H + 1)[:, None, None]
    C = th.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        lag = (h * absth).sum(axis=0) / total
        opposite = np.where(np.sign(th) == -np.sign(C), absth, 0.0).sum(axis=0) / total
    undefined = (np.abs(C) <= tau) | ~(opposite <= max_opposite)
    return np.where(undefined, np.nan, lag)


def peak_lag(theta: np.ndarray, H: int) -> np.ndarray:
    return np.argmax(np.abs(theta[: H + 1]), axis=0)


def companion_radius(B: np.ndarray) -> float:
    """Spectral radius of the reduced-form companion matrix; < 1 means stationary."""
    p = B.shape[0] - 1
    n = B.shape[1]
    A = np.linalg.inv(np.eye(n) - B[0])
    if p == 0:
        return 0.0
    top = np.hstack([A @ B[k] for k in range(1, p + 1)])
    comp = np.zeros((n * p, n * p))
    comp[:n] = top
    if p > 1:
        comp[n:, : n * (p - 1)] = np.eye(n * (p - 1))
    return float(np.max(np.abs(np.linalg.eigvals(comp))))
