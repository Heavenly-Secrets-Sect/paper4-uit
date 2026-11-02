"""Run a config through the unmodified runner (experiments/run_experiment.py) and also store, in
every run row, pair-level coverage for the pairs that carry a direct true edge.

Only the scoring side is extended: ``evaluate`` is wrapped so each row gets
``pairs = [[j, i, covered, interval_score, direct_lag], ...]`` for non-null ordered pairs i -> j
(|C_true| > tau) whose direct edge i -> j exists in the truth (direct_lag = its lag). Methods are
called exactly as by the runner and still receive ``public(skel)`` only. ``analyze.py`` joins these
rows with the damage log in skeletons.jsonl to label deleted pairs (lag 0 vs lag 1-2).

The pool uses the fork start method so worker processes inherit the wrapped ``evaluate``.

Run:  python experiments/ext/baselines2/run_eval.py --config experiments/configs/ext_baselines2_eval.json --workers 3
"""
import multiprocessing as mp
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

import run_experiment as R  # noqa: E402
from paper4.metrics import interval_score, truth_effects  # noqa: E402

_evaluate = R.evaluate


def evaluate_with_pairs(sem, res, H, *, tau_effect=0.1):
    row = _evaluate(sem, res, H, tau_effect=tau_effect)
    if res.status == "ok" and res.lo is not None:
        n = sem.n
        _, C_t, _, _ = truth_effects(sem, H)
        inside = (res.lo <= C_t) & (C_t <= res.hi)
        score = interval_score(res.lo, res.hi, C_t)
        out = []
        for (u, v), lag in sorted(sem.edge_lag.items()):
            if u < n and v < n and abs(C_t[v, u]) > tau_effect:
                out.append([int(v), int(u), int(inside[v, u]), round(float(score[v, u]), 5), int(lag)])
        row["pairs"] = out
    return row


if __name__ == "__main__":
    mp.set_start_method("fork", force=True)
    R.evaluate = evaluate_with_pairs
    raise SystemExit(R.main(sys.argv[1:]))
