"""B1: dynamic SEM generator with known truth.

With a single observed unit (N = 1) the Dynamic SEM reduces to a recursive structural VAR:

    x_t = B0 x_t + sum_{k=1..lag_max} B_k x_{t-k} + e_t,   e_t ~ N(0, diag(noise_var)).

Each edge u -> v of the static topology becomes one edge at one lag. The plan does not fix how
lags and coefficients are drawn; the defaults below are proposals awaiting a supervisor decision
and are recorded with every run.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

import numpy as np

from .effects import companion_radius
from .topology import Topology


@dataclass(frozen=True)
class GeneratorConfig:
    lag_max: int = 2
    q0: float = 0.3                       # probability that an edge is contemporaneous
    cross_coef: tuple[float, float] = (0.3, 0.8)   # |b| of a cross edge, random sign
    self_coef: tuple[float, float] = (0.2, 0.6)    # own lag-1 coefficient of every node
    noise_var: tuple[float, float] = (0.5, 1.5)
    rho_max: float = 0.9                  # lagged part is shrunk until the companion radius is below this
    burn_in: int = 200

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DynamicSEM:
    topology_id: str
    nodes: tuple[str, ...]
    B: np.ndarray                         # (lag_max + 1, n, n)
    noise_var: np.ndarray                 # (n,)
    edge_lag: dict[tuple[int, int], int]  # (source, target) -> lag of the cross edge
    config: GeneratorConfig
    shrink: float = 1.0
    meta: dict = field(default_factory=dict)

    @property
    def n(self) -> int:
        return len(self.nodes)

    @property
    def lag_max(self) -> int:
        return self.B.shape[0] - 1

    def simulate(self, T: int, rng: np.random.Generator) -> np.ndarray:
        """T consecutive observations from the stationary regime."""
        n, p = self.n, self.lag_max
        A = np.linalg.inv(np.eye(n) - self.B[0])
        sd = np.sqrt(self.noise_var)
        total = T + self.config.burn_in
        x = np.zeros((total + p, n))
        for t in range(p, total + p):
            acc = rng.normal(size=n) * sd
            for k in range(1, p + 1):
                acc += self.B[k] @ x[t - k]
            x[t] = A @ acc
        return x[p + self.config.burn_in:]


def build_dynamic_sem(topology: Topology, config: GeneratorConfig, rng: np.random.Generator) -> DynamicSEM:
    n, p = topology.n_nodes, config.lag_max
    B = np.zeros((p + 1, n, n))
    edge_lag: dict[tuple[int, int], int] = {}
    for u, v in topology.edges:
        i, j = topology.index(u), topology.index(v)
        lag = 0 if rng.random() < config.q0 else int(rng.integers(1, p + 1))
        B[lag, j, i] = rng.uniform(*config.cross_coef) * rng.choice((-1.0, 1.0))
        edge_lag[(i, j)] = lag
    for j in range(n):
        B[1, j, j] = rng.uniform(*config.self_coef)
    noise_var = rng.uniform(*config.noise_var, size=n)

    # Contemporaneous edges follow the acyclic topology, so B0 is acyclic by construction.
    shrink = 1.0
    while companion_radius(B) >= config.rho_max:
        B[1:] *= 0.95
        shrink *= 0.95
    return DynamicSEM(
        topology_id=topology.id,
        nodes=topology.nodes,
        B=B,
        noise_var=noise_var,
        edge_lag=edge_lag,
        config=config,
        shrink=shrink,
        meta={"companion_radius": companion_radius(B), "bank": topology.bank, "profile": topology.profile},
    )
