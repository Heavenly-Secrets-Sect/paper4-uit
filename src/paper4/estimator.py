"""Fitting the dynamic SEM on a skeleton, and the residual bootstrap shared by all methods.

How a skeleton maps onto regressors (open question 1; provisional default):

- every node depends on its own lags 1..lag_max;
- every adjacent pair, oriented or not, admits lags 1..lag_max in both directions: time order
  already fixes the direction of a lagged edge, so orientation says nothing about lagged terms;
- an oriented pair u -> v adds the contemporaneous term u_t to the equation of v; an undetermined
  pair adds no contemporaneous term.

A skeleton with ``lag_hint`` (oracle reference only) admits exactly its true terms instead.
The oriented part of a skeleton is acyclic, hence so is B0 and each equation is fitted alone.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .effects import cumulative, irf
from .skeleton import Skeleton

Term = tuple[int, int]  # (source node, lag)


def parent_terms(skel: Skeleton, j: int, lag_max: int) -> list[Term]:
    own = [(j, lag) for lag in range(1, lag_max + 1)]
    if skel.lag_hint is not None:
        return own + sorted((u, skel.lag_hint[(u, v)]) for u, v in skel.oriented if v == j)
    terms = list(own)
    for pair in sorted(skel.pairs(), key=sorted):
        if j in pair:
            (i,) = pair - {j}
            terms += [(i, lag) for lag in range(1, lag_max + 1)]
    terms += sorted((u, 0) for u, v in skel.oriented if v == j)
    return terms


def soft_terms(skel: Skeleton, j: int, lag_max: int) -> list[Term]:
    """Own lags, every other node's lags 1..lag_max, and the skeleton's contemporaneous parents."""
    terms = [(i, lag) for lag in range(1, lag_max + 1) for i in range(skel.n)]
    return terms + sorted((u, 0) for u, v in skel.oriented if v == j)


@dataclass
class Fit:
    status: str                  # "ok" or "underdetermined"
    B: np.ndarray                # (lag_max + 1, n, n)
    intercept: np.ndarray        # (n,)
    residuals: np.ndarray        # (rows, n) structural residuals
    dof: np.ndarray              # residual degrees of freedom per equation
    terms: list[list[Term]]
    penalties: list[np.ndarray] | None = None


def fit_equations(data: np.ndarray, terms: list[list[Term]], lag_max: int,
                  penalties: list[np.ndarray] | None = None) -> Fit:
    """OLS per equation, or ridge with one penalty per regressor when ``penalties`` is given
    (intercept never penalised). Ridge degrees of freedom are the trace of the hat matrix."""
    T, n = data.shape
    rows = np.arange(lag_max, T)
    m = len(rows)
    B = np.zeros((lag_max + 1, n, n))
    intercept = np.zeros(n)
    resid = np.zeros((m, n))
    dof = np.zeros(n)
    status = "ok"
    for j in range(n):
        tj = terms[j]
        y = data[rows, j]
        if not tj:
            intercept[j] = y.mean()
            resid[:, j] = y - y.mean()
            dof[j] = m - 1
            continue
        X = np.column_stack([data[rows - lag, i] for i, lag in tj])
        if penalties is None and len(tj) + 2 > m:
            status = "underdetermined"
            continue
        xm, ym = X.mean(axis=0), y.mean()
        Xc, yc = X - xm, y - ym
        G = Xc.T @ Xc
        if penalties is None:
            beta = np.linalg.lstsq(Xc, yc, rcond=None)[0]
            df = len(tj)
        else:
            A = G + np.diag(penalties[j])
            beta = np.linalg.solve(A, Xc.T @ yc)
            df = float(np.trace(np.linalg.solve(A, G)))
        intercept[j] = ym - xm @ beta
        for (i, lag), b in zip(tj, beta):
            B[lag, j, i] = b
        resid[:, j] = yc - Xc @ beta
        dof[j] = m - 1 - df
    return Fit(status, B, intercept, resid, dof, terms, penalties)


def simulate_from_fit(fit: Fit, data: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """One residual-bootstrap series: whole residual rows resampled (keeps cross-equation
    dependence), centred and rescaled by sqrt(rows / dof) so their variance is not understated."""
    T, n = data.shape
    p = fit.B.shape[0] - 1
    A = np.linalg.inv(np.eye(n) - fit.B[0])
    m = len(fit.residuals)
    scale = np.sqrt(m / np.maximum(fit.dof, 1.0))
    resid = (fit.residuals - fit.residuals.mean(axis=0)) * scale
    draws = resid[rng.integers(0, m, size=T - p)]
    x = np.zeros_like(data)
    x[:p] = data[:p]
    for t in range(p, T):
        acc = fit.intercept + draws[t - p]
        for k in range(1, p + 1):
            acc = acc + fit.B[k] @ x[t - k]
        x[t] = A @ acc
    return x


def bootstrap_C(data: np.ndarray, fit: Fit, H: int, n_boot: int, rng: np.random.Generator,
                refit=None) -> np.ndarray:
    """C(H) from ``n_boot`` bootstrap refits. ``refit(series) -> Fit`` defaults to refitting the
    same terms and penalties."""
    p = fit.B.shape[0] - 1
    refit = refit or (lambda x: fit_equations(x, fit.terms, p, fit.penalties))
    out = []
    tries = 0
    while len(out) < n_boot and tries < 3 * n_boot:
        tries += 1
        fb = refit(simulate_from_fit(fit, data, rng))
        if fb.status == "ok":
            out.append(cumulative(irf(fb.B, H), H))
    return np.array(out)


def percentile_interval(draws: np.ndarray, alpha: float = 0.05) -> tuple[np.ndarray, np.ndarray]:
    lo, hi = np.quantile(draws, (alpha / 2, 1 - alpha / 2), axis=0)
    return lo, hi
