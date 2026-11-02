"""B1 version 5 (ID "auto5", round 2): ``tolerant_auto3`` with targeted opening (with re-selection)
when the gate is open, and a two-sided width calibration. No stated damage is read.

What is kept from ``tolerant_auto3`` (src/paper4/ext_gate.py, docs/ext/gate.md), unchanged and
imported: the restricted structural pair tests, the global Sidak gate at alpha 0.10, the closed
branch (the skeleton's own terms), the BH contemporaneous repair under the evidence budget
K = max(#BH, Storey count, 1), and the reversal allowance (flip each |t| > 1.645 contemporaneous
edge with probability 0.2 per draw).

Changes (docs/ext/auto5.md section 3; every choice was fixed on two probes of D-07H development,
results/ext_auto5_probe/, before the evaluation rule was written):

1. **Targeted opening with re-selection when the gate is open** (src/paper4/ext_narrow.py,
   ``select_open`` imported unchanged; ``opened_terms`` imported and de-duplicated, see
   ``targeted_terms``). When rows / (1 + n * lag_max) < ``tau_rows`` the open branch opens the lag
   blocks of the K pairs with the smallest screening p-value, K = max(ceil(3 * k_open), #{p < 0.10})
   (v5's constants), with k_open = max(#BH discoveries of the gate, 1) (``OPEN_BUDGET = "bh"``; it
   plays the role of v5's stated missing count; the Storey count over-counts, probe budget.md).
   Selection and contemporaneous repair are re-run inside every bootstrap draw (as in
   ``tolerant_v5``). Otherwise the open branch is auto3's all-lag branch.
   - ``tolerant_auto5``: ``tau_rows = inf``, i.e. targeted whenever the gate is open (the probe
     preferred it at every T).
   - ``tolerant_auto5_small`` (ablation, reported, not ruled): ``tau_rows = 2.0``, targeted only at
     T = 40 here (n = 14, lag_max = 2), the literal "targeted at small T" design of R2-3c.
2. **Two-sided width calibration**: the factor per (T, branch) is chosen on a grid 0.5..5.0
   (step 0.05) instead of 1.0..10, so it can narrow an over-covering interval. Target as
   everywhere: min(0.95, max coverage - 0.005). Factors are tuned in-sample on the D-07H development
   probe (experiments/ext/auto5/analyse_probe2.py, make_width_table.py) and keyed by the module's
   own diagnosis (closed / open_all / open_tgt), never by the stated damage, so the method is not in
   the runner's ``calibrate_methods`` (as for auto3).

``FLIP_MODE = "mec"`` (flip only CPDAG-reversible significant edges) was probed and not kept.
Methods see only the data, the skeleton (pairs and orientation); ``skel.damage`` is dropped first.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from .effects import cumulative, irf
from .estimator import bootstrap_C, fit_equations, parent_terms, percentile_interval, soft_terms
from .ext_gate import ALPHA_GATE, FLIP_PROB, diagnose_gate
from .ext_narrow import opened_terms, select_open
from .methods import (ALPHA, MethodResult, _cpdag, _failed, _too_few, calibrate_width, contemporaneous_pool,
                      repair_candidates)
from .skeleton import Skeleton, _creates_cycle

TAU_ROWS = math.inf     # targeted opening when (T - lag_max) / (1 + n * lag_max) < TAU_ROWS (fixed on the probe)
TAU_ROWS_SMALL = 2.0    # ablation tolerant_auto5_small
FLIP_MODE = "sig"       # "sig" (auto3) or "mec" (fixed on the probe)
OPEN_BUDGET = "bh"      # k for the targeted opening: "max" = max(#BH, Storey, 1) (the repair budget) or "bh" = max(#BH, 1)
MULT, ALPHA_OPEN = 3.0, 0.10   # v5's selection constants, unchanged
C_GRID2 = np.round(np.arange(0.5, 5.0001, 0.05), 2)
WIDTH_TABLE = Path(__file__).resolve().parents[2] / "experiments" / "ext" / "auto5" / "width_table.json"


def targeted_terms(skel: Skeleton, opened, j: int, lag_max: int):
    """``ext_narrow.opened_terms`` without duplicates. When a repaired contemporaneous edge falls on
    an opened pair, ``opened_terms`` lists that pair's lag block twice (once as an adjacent pair, once
    as opened); OLS then splits the coefficient between the two copies and ``fit_equations`` keeps one
    copy, i.e. half the lag coefficient, and at T = 40 the duplicates can make an equation
    underdetermined. Reported as a bug of ext_narrow in docs/ext/auto5.md; fixed here only."""
    return list(dict.fromkeys(opened_terms(skel, opened, j, lag_max)))


def rows_ratio(T: int, n: int, lag_max: int) -> float:
    return (T - lag_max) / (1 + n * lag_max)


def flip_pool(data, fit, mode: str) -> list[tuple[int, int]]:
    pool = contemporaneous_pool(data, fit, 0)   # exactly the edges with |t| > 1.645
    if mode == "sig" or not pool:
        return pool
    _, lines = _cpdag(set(pool), fit.B.shape[1])
    return [e for e in pool if frozenset(e) in lines]


def auto5_raw(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, alpha_gate: float = ALPHA_GATE,
              flip_prob: float = FLIP_PROB, flip_mode: str | None = None, tau_rows: float | None = None,
              open_mode: str | None = None, open_budget: str | None = None,
              name: str = "tolerant_auto5") -> MethodResult:
    """Uncalibrated interval. ``info['branch']`` is 'closed', 'open_all' or 'open_tgt'.
    ``open_mode`` ('all' / 'targeted') overrides the T rule; it is for the probe only."""
    n = skel.n
    T = data.shape[0]
    flip_mode = flip_mode or FLIP_MODE
    tau_rows = TAU_ROWS if tau_rows is None else tau_rows
    base = Skeleton(n, set(skel.oriented), set(skel.undetermined))   # stated damage dropped here
    diag = diagnose_gate(data, base, lag_max)
    if diag["p_gate"] is None:
        state = "undiagnosable"
    else:
        state = "open" if diag["p_gate"] <= alpha_gate else "closed"
    if state != "open":
        branch = "closed"
    elif open_mode is not None:
        branch = "open_tgt" if open_mode == "targeted" else "open_all"
    else:
        branch = "open_tgt" if rows_ratio(T, n, lag_max) < tau_rows else "open_all"
    budget = max(diag["n_bh"], diag["k_storey"], 1) if state == "open" else 0
    open_budget = open_budget or OPEN_BUDGET
    k_open = max(diag["n_bh"], 1) if open_budget == "bh" else budget   # plays v5's stated missing count

    opened = None
    if branch == "open_tgt":
        try:
            opened = select_open(data, base, lag_max, k_open, MULT, ALPHA_OPEN)
        except ValueError:
            branch = "open_all"   # selection impossible: fall back to all lags

    def terms_of(s: Skeleton, op=None):
        if branch == "closed":
            return [parent_terms(s, j, lag_max) for j in range(n)]
        if branch == "open_all":
            return [soft_terms(s, j, lag_max) for j in range(n)]
        return [targeted_terms(s, op, j, lag_max) for j in range(n)]

    fit0 = fit_equations(data, terms_of(base, opened), lag_max)
    if fit0.status != "ok":
        return _failed(name, fit0.status)
    cands = repair_candidates(fit0.residuals, base, budget) if branch != "closed" else []
    pool = flip_pool(data, fit0, flip_mode) if flip_prob > 0 else []

    def draw_skel(cs) -> Skeleton:
        s = base.copy()
        for idx in rng.permutation(len(pool)):
            if rng.random() < flip_prob:
                u, v = pool[idx]
                trial = (s.oriented - {(u, v)}) | {(v, u)}
                if not _creates_cycle(trial, n):
                    s.oriented = trial
        for u, v in cs:
            e = (u, v) if rng.random() < 0.5 else (v, u)
            if _creates_cycle(s.oriented | {e}, n):
                e = (e[1], e[0])
            if not _creates_cycle(s.oriented | {e}, n):
                s.oriented.add(e)
        return s

    fit = fit_equations(data, terms_of(draw_skel(cands), opened), lag_max) if cands else fit0
    if fit.status != "ok":
        return _failed(name, fit.status)
    n_open_boot = []
    if branch == "open_tgt":
        def refit(x):
            try:
                op = select_open(x, base, lag_max, k_open, MULT, ALPHA_OPEN)
            except ValueError:
                op = opened
            n_open_boot.append(len(op))
            f0 = fit_equations(x, terms_of(base, op), lag_max)
            if f0.status != "ok":
                return f0
            cs = repair_candidates(f0.residuals, base, budget)
            if not cs and not pool:
                return f0
            return fit_equations(x, terms_of(draw_skel(cs), op), lag_max)
    elif cands or pool:
        def refit(x):
            return fit_equations(x, terms_of(draw_skel(cands), opened), lag_max)
    else:
        refit = None
    draws = bootstrap_C(data, fit, H, n_boot, rng, refit=refit)
    if _too_few(draws, n_boot):
        return _failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, ALPHA)
    theta = irf(fit.B, H)
    C = draws.mean(axis=0) if (cands or branch == "open_tgt") else cumulative(theta, H)
    info = {"state": state, "branch": branch, "p_gate": diag["p_gate"], "n_bh": diag["n_bh"],
            "k_storey": diag["k_storey"], "n_repair": len(cands), "n_flip_pool": len(pool),
            "n_open": None if opened is None else len(opened),
            "n_open_boot_mean": float(np.mean(n_open_boot)) if n_open_boot else None}
    return MethodResult(name, "ok", C, lo, hi, theta, fit.B, info)


_TABLE = None


def _width(T: int, key: str) -> float | None:
    """Factor of the calibration table for ``key`` at the nearest calibrated T (None if absent)."""
    global _TABLE
    if _TABLE is None:
        _TABLE = json.loads(WIDTH_TABLE.read_text(encoding="utf-8")) if WIDTH_TABLE.exists() else {}
    Ts = sorted(int(k.split("|")[1]) for k in _TABLE if k.split("|")[0] == key)
    if not Ts:
        return None
    return _TABLE[f"{key}|{min(Ts, key=lambda t: abs(t - T))}"]


def tolerant_auto5(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng) -> MethodResult:
    """B1 v5: gate; closed or targeted (re-selected) open branch; two-sided width by (T, branch)."""
    raw = auto5_raw(data, skel, lag_max, H, n_boot, rng)
    if raw.status != "ok":
        return raw
    return calibrate_width(raw, _width(data.shape[0], raw.info["branch"]), "tolerant_auto5")


def tolerant_auto5_small(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng) -> MethodResult:
    """Ablation: targeted opening only when rows / regressors < 2 (T = 40 here), all lags otherwise."""
    raw = auto5_raw(data, skel, lag_max, H, n_boot, rng, tau_rows=TAU_ROWS_SMALL, name="tolerant_auto5_small")
    if raw.status != "ok":
        return raw
    return calibrate_width(raw, _width(data.shape[0], raw.info["branch"]), "tolerant_auto5_small")


METHODS = {"tolerant_auto5": tolerant_auto5, "tolerant_auto5_small": tolerant_auto5_small}
