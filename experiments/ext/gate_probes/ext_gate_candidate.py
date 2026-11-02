"""B1 version 3 (ID "gate"): a self-diagnosing tolerant module with a decision gate.

``tolerant_auto3`` needs no stated damage. It reads only the data and the skeleton; ``skel.damage``
is never read (the skeleton is copied with an empty damage record before anything else).

Lessons of B1 versions 1 and 2 (docs/decision_rules.md): a count estimate of missing edges is
biased up on correct skeletons, every false alarm opened all lags and cost 1.3-1.6x interval
score, and reduced-form tests are not adjacency tests. Version 3 therefore decides before it
repairs:

1. **Pair tests in the skeleton's own structural fit.** Each equation is fitted on the skeleton's
   terms (``parent_terms``: own lags, lags of adjacent nodes, contemporaneous parents). For every
   pair (u, v) the skeleton leaves out: the F test of adding u's lags 1..lag_max to v's equation,
   the same for v's lags in u's equation, and the Fisher z of the correlation of the two structural
   residuals. Under a correct skeleton (and lag_max), each equation is correctly specified and the
   structural shocks are independent, so the three tests are valid; they are Sidak-combined into
   one p-value per pair. Unlike the all-lag fit of diagnose.py, the restricted fit keeps its
   degrees of freedom, so the tests keep power at small T. (A missing lagged edge u -> v shows up
   as u's lag block in v's equation; a missing contemporaneous edge as residual correlation.)
2. **Global gate** (spirit of Eulig et al., AAAI 2025: test the graph's implications before using
   it). H0: "the skeleton has no missing edge". Statistic: the smallest pair p-value; global
   p-value: Sidak over the m left-out pairs, 1 - (1 - p_min)^m. An exploratory probe on D-07H
   development (docs/ext/gate.md) found this analytic version as accurate as a parametric
   bootstrap under independent shocks and kept it (cheaper, deterministic).
3. **Gate closed** (p_gate > alpha_gate): the skeleton is fitted as given (``plugin``'s terms).
4. **Gate open**: the missing-edge branch of module v4: every node's lags enter every equation, and
   contemporaneous edges are restored where the all-lag structural residuals are correlated
   (Benjamini-Hochberg q = 0.1, ``repair_candidates``), random direction per bootstrap draw. The
   repair budget is tied to the evidence: at most K = max(#BH discoveries among left-out pairs,
   Storey count) pairs, both from step 1. (A probe showed that opening lags only for flagged pairs
   loses coverage to edges too weak to flag; once the gate has fired, opening all lags is cheap.)
5. **Reversal allowance**: contemporaneous reversals inside the Markov equivalence class leave no
   trace in Gaussian data, so they cannot be diagnosed. In both states, each bootstrap draw flips
   each significant contemporaneous edge (|t| > 1.645) independently with probability
   ``flip_prob`` (cycles skipped). A percentile interval then spans both orientations of a
   confirmed contemporaneous link.
6. **Width**: the interval is widened about its midpoint by a factor tuned per (T, gate state) on
   the calibration bank (D-07H development, the calibration cells of v4), by
   experiments/ext/gate/calibrate_gate.py, stored in experiments/ext/gate/width_table.json. The
   factor is keyed by the module's own diagnosis, never by the stated damage, which is why the
   method is not listed in the runner's ``calibrate_methods`` (that key is the stated kind).

Point estimate: the fit of the gated skeleton when no structure is drawn; otherwise the mean of
the draws, as in module v4.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from .diagnose import _norm_sf, storey_nonnull
from .effects import cumulative, irf
from .estimator import bootstrap_C, fit_equations, parent_terms, percentile_interval, soft_terms
from .methods import (ALPHA, MethodResult, _failed, _too_few, calibrate_width, contemporaneous_pool,
                      repair_candidates)
from .skeleton import Skeleton, _creates_cycle

ALPHA_GATE = 0.10
Q_BH = 0.10
FLIP_PROB = 0.2
WIDTH_TABLE = Path(__file__).resolve().parents[2] / "experiments" / "ext" / "gate" / "width_table.json"


def _f_pvalue(F: float, k: int, dof: int) -> float:
    """Upper tail of F(k, dof) by Paulson's normal approximation (as diagnose._wald_p)."""
    a, b = 2 / (9 * k), 2 / (9 * max(dof, 1))
    f3 = max(F, 0.0) ** (1 / 3)
    return _norm_sf(((1 - b) * f3 - (1 - a)) / math.sqrt(a + b * f3 * f3))


def _bh(p: np.ndarray, q: float) -> np.ndarray:
    order = np.argsort(p)
    k = len(p)
    ok = p[order] <= q * np.arange(1, k + 1) / k
    keep = np.zeros(k, dtype=bool)
    if ok.any():
        keep[order[: int(np.max(np.nonzero(ok)[0])) + 1]] = True
    return keep


def left_out_pairs(skel: Skeleton) -> list[tuple[int, int]]:
    present = skel.pairs()
    return [(u, v) for u in range(skel.n) for v in range(u + 1, skel.n) if frozenset((u, v)) not in present]


def restricted_tests(data: np.ndarray, skel: Skeleton, lag_max: int,
                     pairs_out: list[tuple[int, int]]) -> tuple[np.ndarray, np.ndarray]:
    """Per left-out pair: (Sidak-combined p-value of the three tests, p-value of the residual
    correlation alone), in the skeleton's own structural fit. Raises ValueError when an equation
    plus one lag block has too few rows."""
    T, n = data.shape
    rows = np.arange(lag_max, T)
    m = len(rows)
    Q, R, dof = [], [], []
    for j in range(n):
        tj = parent_terms(skel, j, lag_max)
        X = np.column_stack([np.ones(m)] + [data[rows - lag, i] for i, lag in tj])
        if X.shape[1] + lag_max + 2 > m:
            raise ValueError("underdetermined")
        q, _ = np.linalg.qr(X)
        y = data[rows, j]
        Q.append(q)
        R.append(y - q @ (q.T @ y))
        dof.append(m - X.shape[1])
    lags = {i: np.column_stack([data[rows - lag, i] for lag in range(1, lag_max + 1)]) for i in range(n)}
    corr = np.corrcoef(np.column_stack(R).T)
    p_pair, p_corr = [], []
    for u, v in pairs_out:
        ps = []
        for src, eq in ((u, v), (v, u)):
            Zr = lags[src] - Q[eq] @ (Q[eq].T @ lags[src])
            g = Zr.T @ R[eq]
            drop = float(g @ np.linalg.solve(Zr.T @ Zr, g))
            d2 = dof[eq] - lag_max
            F = (drop / lag_max) / (max(float(R[eq] @ R[eq]) - drop, 1e-12) / d2)
            ps.append(_f_pvalue(F, lag_max, d2))
        r = float(np.clip(corr[u, v], -0.999999, 0.999999))
        pc = 2 * _norm_sf(abs(math.atanh(r)) * math.sqrt(max(min(dof[u], dof[v]) - 1, 1)))
        ps.append(pc)
        p_pair.append(1 - (1 - min(ps)) ** len(ps))
        p_corr.append(pc)
    return np.array(p_pair), np.array(p_corr)


def diagnose_gate(data: np.ndarray, skel: Skeleton, lag_max: int, q: float = Q_BH) -> dict:
    """Gate p-value and evidence counts; {'p_gate': None} when the restricted fit cannot be made."""
    pairs_out = left_out_pairs(skel)
    if not pairs_out:
        return {"p_gate": 1.0, "n_bh": 0, "k_storey": 0, "m_out": 0}
    try:
        p, _ = restricted_tests(data, skel, lag_max, pairs_out)
    except (ValueError, np.linalg.LinAlgError):
        return {"p_gate": None, "n_bh": 0, "k_storey": 0, "m_out": len(pairs_out)}
    return {"p_gate": float(1 - (1 - p.min()) ** len(p)), "n_bh": int(_bh(p, q).sum()),
            "k_storey": int(np.floor(storey_nonnull(list(p)) + 0.5)), "m_out": len(pairs_out)}


def _significant_contemporaneous(data, fit) -> list[tuple[int, int]]:
    return contemporaneous_pool(data, fit, 0)  # k = 0: exactly the pairs with |t| > 1.645


def auto3_raw(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, alpha_gate: float = ALPHA_GATE,
              flip_prob: float = FLIP_PROB, force_state: str | None = None,
              name: str = "tolerant_auto3") -> MethodResult:
    """Uncalibrated interval; ``info['state']`` is the gate decision ('closed', 'open', or
    'undiagnosable', which is fitted as closed). ``force_state`` is for the calibration probe only."""
    n = skel.n
    base = Skeleton(n, set(skel.oriented), set(skel.undetermined))  # stated damage dropped here
    diag = diagnose_gate(data, base, lag_max)
    if force_state is not None:
        state = force_state
    elif diag["p_gate"] is None:
        state = "undiagnosable"
    else:
        state = "open" if diag["p_gate"] <= alpha_gate else "closed"
    opened = state == "open"
    terms_of = (lambda s: [soft_terms(s, j, lag_max) for j in range(n)]) if opened else \
               (lambda s: [parent_terms(s, j, lag_max) for j in range(n)])
    fit0 = fit_equations(data, terms_of(base), lag_max)
    if fit0.status != "ok":
        return _failed(name, fit0.status)
    budget = max(diag["n_bh"], diag["k_storey"], 1) if opened else 0
    cands = repair_candidates(fit0.residuals, base, budget) if opened else []
    pool = _significant_contemporaneous(data, fit0) if flip_prob > 0 else []
    draw_structure = bool(cands) or bool(pool)

    def draw_skel() -> Skeleton:
        s = base.copy()
        for idx in rng.permutation(len(pool)):
            if rng.random() < flip_prob:
                u, v = pool[idx]
                trial = (s.oriented - {(u, v)}) | {(v, u)}
                if not _creates_cycle(trial, n):
                    s.oriented = trial
        for u, v in cands:
            e = (u, v) if rng.random() < 0.5 else (v, u)
            if _creates_cycle(s.oriented | {e}, n):
                e = (e[1], e[0])
            if not _creates_cycle(s.oriented | {e}, n):
                s.oriented.add(e)
        return s

    fit = fit_equations(data, terms_of(draw_skel()), lag_max) if cands else fit0
    if fit.status != "ok":
        return _failed(name, fit.status)
    refit = (lambda x: fit_equations(x, terms_of(draw_skel()), lag_max)) if draw_structure else None
    draws = bootstrap_C(data, fit, H, n_boot, rng, refit=refit)
    if _too_few(draws, n_boot):
        return _failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, ALPHA)
    theta = irf(fit.B, H)
    C = draws.mean(axis=0) if cands else cumulative(theta, H)
    info = {"state": state, "p_gate": diag["p_gate"], "n_bh": diag["n_bh"], "k_storey": diag["k_storey"],
            "n_repair": len(cands), "n_flip_pool": len(pool)}
    return MethodResult(name, "ok", C, lo, hi, theta, fit.B, info)


_TABLE = None


def _width(T: int, state: str) -> float | None:
    global _TABLE
    if _TABLE is None:
        _TABLE = json.loads(WIDTH_TABLE.read_text(encoding="utf-8")) if WIDTH_TABLE.exists() else {}
    key = "closed" if state == "undiagnosable" else state
    Ts = sorted({int(k.split("|")[0]) for k in _TABLE if k.endswith("|" + key)})
    if not Ts:
        return None
    t_near = min(Ts, key=lambda t: abs(t - T))
    return _TABLE.get(f"{t_near}|{key}")


def tolerant_auto3(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng) -> MethodResult:
    raw = auto3_raw(data, skel, lag_max, H, n_boot, rng)
    if raw.status != "ok":
        return raw
    return calibrate_width(raw, _width(data.shape[0] - 0, raw.info["state"]), "tolerant_auto3")


METHODS = {"tolerant_auto3": tolerant_auto3}
