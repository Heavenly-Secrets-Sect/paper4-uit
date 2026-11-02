"""B1: estimate the damage of a supplied skeleton from the data, so the module needs no declaration.

The plan's interface passes a damage estimate with the skeleton (section 7). Module v4 reads it
as declared by the user. Here it is estimated instead, from the same data the module fits.

All tests are made in the **structural** equations of the skeleton's all-lag fit: every node's
lags 1..lag_max plus the skeleton's contemporaneous parents, the fit the module itself uses when
missing edges are suspected. Reduced-form tests are not valid adjacency tests: with u -> w at a
lag and w -> v at lag 0, u "Granger-causes" v in reduced form although the pair is not adjacent,
and the partial correlation of reduced-form residuals is non-zero for the parents of a common
child. Version 1 used both and counted 6-8 missing pairs on correct skeletons.

- **missing**: among the pairs the skeleton leaves out, the number that carry an edge. Each pair
  is tested by the F (Wald) statistic of u's lag block in v's equation, of v's lag block in u's, and
  the correlation of the two structural residuals; the three p-values are combined by Sidak, which
  keeps null p-values uniform as Storey's estimator requires. The number of non-null pairs among
  the m_out left-out pairs is m_out * (1 - pi0_hat) (Storey), which also counts edges too weak
  to reject one by one.
- **extra**: among the pairs the skeleton keeps, the number that carry no edge, m_in * pi0_hat,
  from the joint Wald test of all of u's terms in v's equation and of v's in u's (Sidak over two).
- **reversed**: not identified from data (a contemporaneous direction leaves no trace in Gaussian
  linear data). A fixed allowance is stated instead: 20% of the skeleton's oriented pairs whose
  terms are significant, i.e. the links the data confirm.

Known biases, stated in advance: a hidden common cause correlates structural residuals, so it can
be counted as a missing edge. Storey's estimator under-counts non-nulls when the tests have
little power.
"""
from __future__ import annotations

import math

import numpy as np

from .estimator import soft_terms
from .skeleton import Skeleton


def _norm_sf(z: float) -> float:
    return 0.5 * math.erfc(z / math.sqrt(2))


def _wald_p(beta: np.ndarray, cov: np.ndarray, dof: int) -> float:
    """p-value of the Wald test beta = 0 as an F(k, dof) test (the error variance is estimated),
    F mapped to N(0, 1) by Paulson's approximation. The chi-square version over-rejects at small T."""
    k = len(beta)
    F = float(beta @ np.linalg.solve(cov, beta)) / k
    a, b = 2 / (9 * k), 2 / (9 * max(dof, 1))
    f3 = F ** (1 / 3)
    return _norm_sf(((1 - b) * f3 - (1 - a)) / math.sqrt(a + b * f3 * f3))


def structural_pvalues(data: np.ndarray, skel: Skeleton, lag_max: int) -> dict[frozenset[int], float]:
    """One p-value per unordered pair from the skeleton's structural all-lag fit (see module doc).
    Raises ValueError when an equation has more regressors than rows."""
    T, n = data.shape
    rows = np.arange(lag_max, T)
    m = len(rows)
    fits = []
    for j in range(n):
        terms = soft_terms(skel, j, lag_max)
        if len(terms) + 2 > m:
            raise ValueError("underdetermined")
        X = np.column_stack([np.ones(m)] + [data[rows - lag, i] for i, lag in terms])
        XtX_inv = np.linalg.inv(X.T @ X)
        beta = XtX_inv @ X.T @ data[rows, j]
        resid = data[rows, j] - X @ beta
        dof = m - X.shape[1]
        fits.append((terms, beta, XtX_inv * (resid @ resid / dof), resid, dof))

    def block_p(src, eq, contemporaneous):
        terms, beta, cov, _, dof = fits[eq]
        idx = [1 + t for t, (i, lag) in enumerate(terms) if i == src and (lag > 0 or contemporaneous)]
        return _wald_p(beta[idx], cov[np.ix_(idx, idx)], dof)

    out = {}
    for u in range(n):
        for v in range(u + 1, n):
            if skel.is_adjacent(u, v):
                ps = [block_p(u, v, True), block_p(v, u, True)]
            else:
                ru, rv = fits[u][3], fits[v][3]
                r = float(np.clip(np.corrcoef(ru, rv)[0, 1], -0.999999, 0.999999))
                z = math.atanh(r) * math.sqrt(max(min(fits[u][4], fits[v][4]) - 1, 1))
                ps = [block_p(u, v, False), block_p(v, u, False), 2 * _norm_sf(abs(z))]
            out[frozenset((u, v))] = 1 - (1 - min(ps)) ** len(ps)
    return out


def storey_nonnull(pvalues: list[float], lam: float = 0.5) -> float:
    """Estimated number of non-null hypotheses, m * (1 - pi0_hat), pi0_hat = #{p > lam} / ((1 - lam) m)."""
    m = len(pvalues)
    if m == 0:
        return 0.0
    pi0 = min(1.0, sum(p > lam for p in pvalues) / ((1 - lam) * m))
    return m * (1 - pi0)


def estimate_damage(data: np.ndarray, skel: Skeleton, lag_max: int, *, reversal_share: float = 0.2,
                    alpha: float = 0.05) -> dict | None:
    """Damage record {missing, extra, reversed} estimated from the data, or None when the all-lag
    fit cannot be made (too few observations; the missing-edge branch of the module could not run
    there either)."""
    try:
        pv = structural_pvalues(data, skel, lag_max)
    except ValueError:
        return None
    present = skel.pairs()
    p_out = [p for pair, p in pv.items() if pair not in present]
    p_in = [p for pair, p in pv.items() if pair in present]
    missing = storey_nonnull(p_out)
    extra = len(p_in) - storey_nonnull(p_in)
    confirmed = sum(1 for u, v in skel.oriented if pv[frozenset((u, v))] < alpha)
    return {"missing": int(np.floor(missing + 0.5)), "extra": int(np.floor(extra + 0.5)),
            "reversed": int(np.floor(reversal_share * confirmed + 0.5)), "estimated": True}
