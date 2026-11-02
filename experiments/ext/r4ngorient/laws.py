"""Unit-variance shock laws of the r4ngorient scenarios (docs/ext/r4ngorient.md).

ng_mix: each observed node gets one law, drawn with equal probability from
  laplace   Laplace(0, 1/sqrt 2)                      skew 0, exkurt 3
  t5        Student-t5 * sqrt(3/5)                    skew 0, exkurt 6
  skewexp   (Exp(1) - 1) * random sign               skew +/-2, exkurt 6
  uniform   U(-sqrt 3, sqrt 3)                        skew 0, exkurt -1.2
seeded per (topology, replicate) by rng([unit, 8]) (the sign of skewexp is drawn there too).
ng_t10: every observed node Student-t10 * sqrt(8/10) (exkurt 1). Latent nodes stay Gaussian.
gauss: N(0, 1).
"""
from __future__ import annotations

import numpy as np

MIX_LAWS = ("laplace", "t5", "skewexp", "uniform")


def sample(rng: np.random.Generator, law: str, size, sign: float = 1.0) -> np.ndarray:
    if law == "gauss":
        return rng.normal(size=size)
    if law == "laplace":
        return rng.laplace(0.0, 1 / np.sqrt(2), size=size)
    if law == "t5":
        return rng.standard_t(5, size=size) * np.sqrt(3 / 5)
    if law == "t10":
        return rng.standard_t(10, size=size) * np.sqrt(8 / 10)
    if law == "skewexp":
        return (rng.exponential(1.0, size=size) - 1.0) * sign
    if law == "uniform":
        return rng.uniform(-np.sqrt(3), np.sqrt(3), size=size)
    raise ValueError(law)


def node_laws(shock: str, unit: int, n_obs: int) -> list[tuple[str, float]]:
    """(law, sign) per observed node, fixed per (topology, replicate) = unit."""
    if shock == "gauss":
        return [("gauss", 1.0)] * n_obs
    if shock == "ng_t10":
        return [("t10", 1.0)] * n_obs
    if shock == "ng_mix":
        r = np.random.default_rng([unit, 8])
        idx = r.integers(0, len(MIX_LAWS), size=n_obs)
        sg = np.where(r.random(n_obs) < 0.5, -1.0, 1.0)
        return [(MIX_LAWS[i], float(s)) for i, s in zip(idx, sg)]
    raise ValueError(shock)


def simulate(sem, T: int, rng: np.random.Generator, laws: list[tuple[str, float]]) -> np.ndarray:
    """``DynamicSEM.simulate`` with the given per-node unit-variance laws for the observed nodes
    (latent nodes Gaussian). Same recursion, burn-in and scaling by sqrt(noise_var)."""
    n, p = sem.n_all, sem.lag_max
    A = np.linalg.inv(np.eye(n) - sem.B[0])
    sd = np.sqrt(sem.noise_var)
    total = T + sem.config.burn_in
    E = np.empty((total, n))
    for j in range(n):
        law, sign = laws[j] if j < len(laws) else ("gauss", 1.0)
        E[:, j] = sample(rng, law, total, sign)
    x = np.zeros((total + p, n))
    for t in range(p, total + p):
        acc = E[t - p] * sd
        for k in range(1, p + 1):
            acc = acc + sem.B[k] @ x[t - k]
        x[t] = A @ acc
    return x[p + sem.config.burn_in:, : sem.n]
