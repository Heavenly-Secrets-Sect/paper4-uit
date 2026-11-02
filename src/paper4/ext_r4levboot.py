"""Round 4, candidate "levboot": leverage-adjusted residuals in the residual bootstrap of tolerant_v5_1.

Only ``estimator.simulate_from_fit`` changes. Everything else (evidence screening, targeted lag
opening, contemporaneous repair, reversal draws, re-selection in every draw, percentile interval,
PRESCALE 0.5 and the runner's per-(T, stated kind) width factor) is ``ext_v51.tolerant_v5_1``
line for line. ``estimator.py`` stays frozen: the method swaps ``estimator.simulate_from_fit``
for the duration of one call (``estimator.bootstrap_C`` looks the name up at call time) and puts
the original back in a ``finally`` block. No other module is touched; no file is modified.

The bootstrap series of v5_1 (``estimator.simulate_from_fit``) resamples whole residual rows of the
data fit, centred, times the uniform factor sqrt(m / dof_j) per equation. The arms replace that pool:

- ``r4levboot_L2`` (HC2-type, Wu 1986; "modified residuals" of the residual bootstrap):
  e_tj = r_tj / sqrt(max(1 - h_tj, FLOOR)), centred per column, no further dof rescale;
- ``r4levboot_L3`` (HC3-type, MacKinnon and White 1985; Davidson and Flachaire 2008 transform):
  e_tj = r_tj / max(1 - h_tj, FLOOR), centred per column, no further dof rescale;
  rows resampled with ``rng.integers(0, m, size=T - p)`` exactly as v5_1 (keeps cross-equation
  dependence and the random-number consumption, see CRN below);
- ``r4levboot_W3`` (the sources' own scheme: recursive-design wild bootstrap, Rademacher weights,
  HC3-type transform, Davidson and Flachaire 2008; Goncalves and Kilian 2004 for the recursive VAR
  design): u*_t = e_t * eta_t with e as in L3 (not centred; eta has mean zero), the row stays at its
  own date t and one eta_t multiplies the whole row (keeps cross-equation dependence);
- ``r4levboot_U`` (identity check only, not a candidate): the uniform pool of v5_1 through this
  module's plumbing; must reproduce ``tolerant_v5_1`` exactly. Mode "ORIG" (used by the driver to
  log the reference's profile and failures) calls the frozen ``estimator.simulate_from_fit`` itself.

h_tj is the leverage of row t in equation j: X_j = [1, data[rows - lag, i] for (i, lag) in
fit.terms[j]] (the design of the fit passed to simulate_from_fit, i.e. the data fit with its selected
opened lag blocks and drawn repaired / reversed contemporaneous terms), h = rowsum(Q^2) from the reduced
QR of X_j (SVD with a rank tolerance if X_j is rank deficient). FLOOR = 0.05.

**Common random numbers (CRN).** When the generator passed in comes from the runner
(``default_rng([unit, 3, T, cell, tag])``), the arm re-seeds it with tolerant_v5_1's tag, so the arm
and the reference v5_1 draw the same rows, the same repair directions and the same reversals; an
arm differs from v5_1 only through its residual pool (L2/L3; W3 draws Rademacher signs instead of
row indices, so its later random numbers differ). This uses no information about the truth; outside
the runner the generator is used as given (info ``crn`` = 0).

Logged per run (info_*): bootstrap tries and successes (failure rate = 1 - successes / tries), and
the leverage profile of the data fit: mean h, max h, share of (row, equation) cells with h > 0.9,
share floored (1 - h < FLOOR), mean over equations of the per-equation mean h, max per-equation mean
h, and the per-equation pool variance relative to RSS/dof averaged over equations (1 for v5_1).

Methods see only the data, the public skeleton and its stated damage.
"""
from __future__ import annotations

import zlib
from contextlib import contextmanager

import numpy as np

from . import estimator as E
from .ext_v51 import tolerant_v5_1

FLOOR = 0.05
REF_NAME = "tolerant_v5_1"
_ORIG_SIM = E.simulate_from_fit   # the frozen function, captured at import


def _ext_seed(name: str) -> int:
    """Same formula as experiments/run_experiment.py ext_seed (stream tag fixed by the name)."""
    return 1000 + zlib.crc32(name.encode()) % 1_000_000


def leverages(fit, data: np.ndarray) -> np.ndarray:
    """(m, n) leverage h_tj of every row in every equation of ``fit`` (module doc)."""
    T, n = data.shape
    p = fit.B.shape[0] - 1
    rows = np.arange(p, T)
    m = len(rows)
    h = np.full((m, n), 1.0 / m)
    for j in range(n):
        tj = fit.terms[j]
        if not tj:
            continue
        X = np.column_stack([np.ones(m)] + [data[rows - lag, i] for i, lag in tj])
        Q, R = np.linalg.qr(X)
        d = np.abs(np.diag(R))
        if d.min() > 1e-10 * max(d.max(), 1e-300):
            h[:, j] = (Q * Q).sum(axis=1)
        else:  # rank deficient: leverage of the column space
            U, s, _ = np.linalg.svd(X, full_matrices=False)
            U = U[:, s > s.max() * max(X.shape) * np.finfo(float).eps]
            h[:, j] = (U * U).sum(axis=1)
    return h


def _profile(fit, data, h, pool) -> dict:
    r = fit.residuals
    s2 = (r ** 2).sum(axis=0) / np.maximum(fit.dof, 1.0)
    pv = pool.var(axis=0)
    eq_mean = h.mean(axis=0)
    return {"lev_mean": float(h.mean()), "lev_max": float(h.max()),
            "lev_share_gt09": float((h > 0.9).mean()), "lev_share_floored": float((1 - h < FLOOR).mean()),
            "lev_eq_mean_max": float(eq_mean.max()),
            "pool_var_ratio": float(np.mean(pv / np.where(s2 > 0, s2, np.nan)))}


def _pool(fit, data, mode: str):
    """Residual pool of one mode, plus its leverage matrix."""
    h = leverages(fit, data)
    r = fit.residuals
    if mode in ("U", "ORIG"):
        m = len(r)
        pool = (r - r.mean(axis=0)) * np.sqrt(m / np.maximum(fit.dof, 1.0))
    elif mode == "L2":
        pool = r / np.sqrt(np.maximum(1 - h, FLOOR))
        pool = pool - pool.mean(axis=0)
    elif mode in ("L3", "W3"):
        pool = r / np.maximum(1 - h, FLOOR)
        if mode == "L3":
            pool = pool - pool.mean(axis=0)
    else:
        raise ValueError(mode)
    return pool, h


def make_simulator(mode: str, stats: dict):
    """A drop-in for ``estimator.simulate_from_fit`` using the pool of ``mode``. The pool of a fit is
    computed once (the bootstrap always passes the same data fit) and its profile kept in ``stats``."""
    cache = {}

    def simulate(fit, data, rng):
        key = id(fit)
        if key not in cache:
            pool, h = _pool(fit, data, mode)
            cache.clear()
            cache[key] = (fit, pool)   # keep fit alive so id() is not reused
            if "lev_mean" not in stats:
                stats.update(_profile(fit, data, h, pool if mode != "W3" else pool - pool.mean(axis=0)))
        if mode == "ORIG":   # profile only; the frozen function draws the series
            return _ORIG_SIM(fit, data, rng)
        pool = cache[key][1]
        T, n = data.shape
        p = fit.B.shape[0] - 1
        A = np.linalg.inv(np.eye(n) - fit.B[0])
        m = len(pool)
        if mode == "W3":
            eta = 2.0 * rng.integers(0, 2, size=T - p) - 1.0
            draws = pool[:T - p] * eta[:, None]
        else:
            draws = pool[rng.integers(0, m, size=T - p)]
        x = np.zeros_like(data)
        x[:p] = data[:p]
        for t in range(p, T):
            acc = fit.intercept + draws[t - p]
            for k in range(1, p + 1):
                acc = acc + fit.B[k] @ x[t - k]
            x[t] = A @ acc
        return x

    return simulate


@contextmanager
def bootstrap_hooks(simulate, stats: dict):
    """Swap ``estimator.simulate_from_fit`` for ``simulate`` and count tries / successes of
    ``estimator.bootstrap_C`` (successes = calls of ``estimator.cumulative``, which bootstrap_C makes
    only for an ok refit). Restores both names afterwards."""
    orig_sim, orig_cum = E.simulate_from_fit, E.cumulative
    stats.setdefault("boot_tries", 0)
    stats.setdefault("boot_succ", 0)

    def sim_c(fit, data, rng):
        stats["boot_tries"] += 1
        return simulate(fit, data, rng)

    def cum_c(*a, **k):
        stats["boot_succ"] += 1
        return orig_cum(*a, **k)

    E.simulate_from_fit, E.cumulative = sim_c, cum_c
    try:
        yield stats
    finally:
        E.simulate_from_fit, E.cumulative = orig_sim, orig_cum


def crn_rng(rng):
    """Re-seed a runner generator with tolerant_v5_1's stream tag (module doc, CRN)."""
    try:
        ent = rng.bit_generator.seed_seq.entropy
    except AttributeError:
        return rng, 0
    if isinstance(ent, (list, tuple)) and len(ent) == 5:
        return np.random.default_rng([*ent[:4], _ext_seed(REF_NAME)]), 1
    return rng, 0


def run_with(mode: str, name: str, data, skel, lag_max, H, n_boot, rng, *, crn: bool = True):
    rng2, used = crn_rng(rng) if crn else (rng, 0)
    stats: dict = {}
    with bootstrap_hooks(make_simulator(mode, stats), stats):
        res = tolerant_v5_1(data, skel, lag_max, H, n_boot, rng2)
    res.name = name
    res.info = {**res.info, **stats, "lev_mode": mode, "lev_floor": FLOOR, "crn": used}
    return res


def _arm(mode: str, name: str):
    def fn(data, skel, lag_max, H, n_boot, rng):
        return run_with(mode, name, data, skel, lag_max, H, n_boot, rng)
    fn.__name__ = name
    return fn


METHODS = {
    "r4levboot_L2": _arm("L2", "r4levboot_L2"),
    "r4levboot_L3": _arm("L3", "r4levboot_L3"),
    "r4levboot_W3": _arm("W3", "r4levboot_W3"),
    "r4levboot_U": _arm("U", "r4levboot_U"),
}
