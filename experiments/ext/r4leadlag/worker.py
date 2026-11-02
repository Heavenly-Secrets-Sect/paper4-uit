"""Worker-side patches of the runner for the r4leadlag runs (the runner itself is not modified).

1. Bootstrap stream tag: ``tolerant_v5_1_leadlag`` and ``tolerant_v5_1_leadlag_skel`` get the stream tag of ``tolerant_v5_1``
   (``ext_seed('tolerant_v5_1')``), so both methods use the same random numbers in every cell. Where the
   gate does not act (no stated missing edge, or no pair labelled in any draw) the two rows are then
   identical, and elsewhere the comparison is paired at the level of random numbers too. Other methods'
   tags are unchanged, so tolerant_v5_1 / oracle rows reproduce stored runs.
2. Evaluation extras (truth used only here, after the method has returned):
   - co-child pairs (ordered pairs of observed nodes sharing a hidden parent): coverage and interval
     score over all of them and over the non-null ones;
   - the class of every pair in the candidate's gate logs: E0 = true contemporaneous edge missing from the
     skeleton, EL = true lagged edge missing from the skeleton, C = co-child pair that is not a true edge,
     CE = co-child pair that is also a true edge, N = neither.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
for p in (str(ROOT / "src"), str(ROOT / "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import run_experiment as RE  # noqa: E402
from paper4 import metrics as MT  # noqa: E402
from paper4.ext_r4leadlag import NAME, NAME_SKEL  # noqa: E402

NAMES = (NAME, NAME_SKEL)

_ORIG_RUN_UNIT = RE.run_unit
_ORIG_EXT_SEED = RE.ext_seed
_ORIG_EVALUATE = MT.evaluate
REF = "tolerant_v5_1"


def ext_seed_ll(name: str) -> int:
    return _ORIG_EXT_SEED(REF if name in NAMES else name)


def _cochild(sem):
    kids = {}
    for a, child, _lag in sem.meta.get("latent_edges", []):
        kids.setdefault(a, set()).add(int(child))
    pairs = set()
    for ch in kids.values():
        for u in ch:
            for v in ch:
                if u != v:
                    pairs.add((u, v))
    return pairs


def classify(sem, u: int, v: int, cochild=None) -> str:
    cochild = _cochild(sem) if cochild is None else cochild
    lag = sem.edge_lag.get((u, v), sem.edge_lag.get((v, u)))
    cc = (u, v) in cochild
    if lag is None:
        return "C" if cc else "N"
    if cc:
        return "CE"
    return "E0" if lag == 0 else "EL"


def evaluate_ll(sem, res, H, *, tau_effect=0.1):
    row = _ORIG_EVALUATE(sem, res, H, tau_effect=tau_effect)
    if res.status != "ok" or res.lo is None:
        return row
    cc = _cochild(sem)
    if cc:
        _, C_t, _, _ = MT.truth_effects(sem, H)
        idx = tuple(np.array(sorted(cc)).T)
        inside = (res.lo <= C_t) & (C_t <= res.hi)
        score = MT.interval_score(res.lo, res.hi, C_t)
        nn = np.abs(C_t[idx]) > tau_effect
        row.update({"cc_n": int(len(cc)), "cc_n_cov": int(inside[idx].sum()), "cc_is_sum": float(score[idx].sum()),
                    "cc_n_nonnull": int(nn.sum()), "cc_n_cov_nonnull": int(inside[idx][nn].sum()),
                    "cc_is_sum_nonnull": float(score[idx][nn].sum())})
    if res.name in NAMES:
        info = res.info
        for key in ("gate_labelled", "gate_repaired", "gate_ungated"):
            if key in info:
                row[f"cls_{key}"] = [classify(sem, u, v, cc) for u, v in info[key]]
        if "gate_p" in info:
            row["cls_gate_p"] = [classify(sem, int(u), int(v), cc) for u, v, _, _ in info["gate_p"]]
        if "gate_scores" in info:
            row["cls_gate_scores"] = [classify(sem, int(s[0]), int(s[1]), cc) for s in info["gate_scores"]]
    return row


def patch():
    RE.ext_seed = ext_seed_ll
    RE.evaluate = evaluate_ll


def run_unit_ll(args):
    patch()
    return _ORIG_RUN_UNIT(args)
