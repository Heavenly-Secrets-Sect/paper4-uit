"""RQ4.4: can quantities observable without truth predict which reported effects are unreliable?

Per (topology, replicate, T, damage cell) the module (`tolerant_v3_cal`), `plugin` and
`lp_allpast` are fitted on the same data and the stated damage. For every non-null target pair:

signals (no truth needed)
- ``rel_width``     interval width / |C_hat| of the module
- ``struct_sens``   |C_module - C_plugin| / module width (how much the answer moves when the skeleton is relaxed)
- ``method_sens``   |C_plugin - C_lp| / lp width (disagreement between structural and model-free estimates)
- ``zero_in``       1 if the module interval contains 0
outcome
- ``unreliable``    module estimate off by more than 50% of |C_true|, or its interval misses C_true

AUROC of each signal, and of a logistic combination fitted on the development topologies and
evaluated on the confirmatory topologies (topology-level split). The width-only signal is the
trivial benchmark the combination must beat.

Run:  python experiments/run_flags.py [--workers 10]
Writes results/rq44_flags/{pairs.jsonl, summary.md}.
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from paper4 import methods as M  # noqa: E402
from paper4.generator import GeneratorConfig, build_dynamic_sem  # noqa: E402
from paper4.metrics import truth_effects  # noqa: E402
from paper4.skeleton import damage, true_skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

H, LAG_MAX, TAU, N_BOOT = 4, 2, 0.1, 199
C_T = {80: 1.5, 150: 1.3, 300: 1.2}   # tolerant_v3_cal widths, from results/rq42_v3/calibration.json
CELLS = [("none", 0.0), ("missing", 0.2), ("missing", 0.5), ("reversed", 0.2), ("reversed", 0.5)]
SIGNALS = ("rel_width", "struct_sens", "method_sens", "zero_in")


def run_unit(args):
    topo, t_idx, rep, split, seed_base, Ts = args
    unit = seed_base + 1000 * t_idx + rep
    sem = build_dynamic_sem(topo, GeneratorConfig(lag_max=LAG_MAX), np.random.default_rng([unit, 0]))
    truth = true_skeleton(sem)
    _, C_true, _, _ = truth_effects(sem, H)
    off = ~np.eye(sem.n, dtype=bool)
    nonnull = off & (np.abs(C_true) > TAU)
    rows = []
    for c_idx, (kind, rate) in enumerate(CELLS):
        skel = damage(truth, kind, rate, np.random.default_rng([unit, 1, c_idx]), sem.edge_lag)
        for T in Ts:
            data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
            rng = np.random.default_rng([unit, 3, T, c_idx])
            mod = M.calibrate_width(M.tolerant_v3(data, skel, LAG_MAX, H, N_BOOT, rng), C_T[T], "tolerant_v3_cal")
            plug = M.plugin(data, skel, LAG_MAX, H, 0, None)
            lp = M.lp_allpast(data, skel, LAG_MAX, H)
            if mod.status != "ok" or plug.status != "ok" or lp.status != "ok":
                continue
            width = mod.hi - mod.lo
            lp_width = lp.hi - lp.lo
            eps = 1e-9
            for j, i in zip(*np.nonzero(nonnull)):
                err = abs(mod.C[j, i] - C_true[j, i]) / abs(C_true[j, i])
                miss = not (mod.lo[j, i] <= C_true[j, i] <= mod.hi[j, i])
                rows.append({
                    "topology": topo.id, "split": split, "replicate": rep, "T": T, "kind": kind, "rate": rate,
                    "rel_width": float(width[j, i] / (abs(mod.C[j, i]) + eps)),
                    "struct_sens": float(abs(mod.C[j, i] - plug.C[j, i]) / (width[j, i] + eps)),
                    "method_sens": float(abs(plug.C[j, i] - lp.C[j, i]) / (lp_width[j, i] + eps)),
                    "zero_in": float(mod.lo[j, i] <= 0 <= mod.hi[j, i]),
                    "unreliable": int(err > 0.5 or miss),
                })
    return rows


def auroc(score, label) -> float:
    """Mann-Whitney AUROC with average ranks for ties."""
    score, label = np.asarray(score, float), np.asarray(label, int)
    n_pos, n_neg = int(label.sum()), int((1 - label).sum())
    if not n_pos or not n_neg:
        return float("nan")
    order = np.argsort(score, kind="mergesort")
    ranks = np.empty(len(score))
    ranks[order] = np.arange(1, len(score) + 1)
    _, inverse, counts = np.unique(score, return_inverse=True, return_counts=True)
    sums = np.bincount(inverse, weights=ranks)
    ranks = (sums / counts)[inverse]
    return float((ranks[label == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def features(rows):
    X = np.array([[np.log1p(r["rel_width"]), np.log1p(r["struct_sens"]), np.log1p(r["method_sens"]), r["zero_in"]]
                  for r in rows])
    return np.column_stack([np.ones(len(X)), X])


def fit_logistic(X, y, l2=1e-3, iters=50):
    w = np.zeros(X.shape[1])
    for _ in range(iters):                      # Newton-Raphson with a small ridge
        p = 1 / (1 + np.exp(-np.clip(X @ w, -30, 30)))
        g = X.T @ (p - y) + l2 * w
        Hm = (X * (p * (1 - p))[:, None]).T @ X + l2 * np.eye(len(w))
        w -= np.linalg.solve(Hm, g)
    return w


def summarize(rows) -> str:
    train = [r for r in rows if r["split"] == "development"]
    test = [r for r in rows if r["split"] == "confirmatory"]
    w = fit_logistic(features(train), np.array([r["unreliable"] for r in train], float))
    lines = ["# RQ4.4: truth-free reliability flags for the module (`tolerant_v3_cal`)", "",
             "Outcome `unreliable`: estimate off by > 50% of |C_true| or interval misses C_true. "
             "AUROC on confirmatory topologies; the combined flag is a logistic model fitted on development topologies.",
             "", f"Base rate of unreliable pairs (test): {np.mean([r['unreliable'] for r in test]):.3f} "
             f"over {len(test)} pairs.", "",
             "| T | damage | rate | base rate | " + " | ".join(SIGNALS) + " | combined |",
             "|---|---|---|---|" + "---|" * (len(SIGNALS) + 1)]
    groups = [(None, None, None)] + [(T, k, r) for T in sorted({x["T"] for x in test}) for k, r in CELLS]
    for T, k, rr in groups:
        sel = [x for x in test if (T is None or (x["T"] == T and x["kind"] == k and x["rate"] == rr))]
        if not sel:
            continue
        y = [x["unreliable"] for x in sel]
        comb = features(sel) @ w
        cells = [f"{auroc([x[s] for x in sel], y):.3f}" for s in SIGNALS] + [f"{auroc(comb, y):.3f}"]
        label = "all | all | all" if T is None else f"{T} | {k} | {rr:.1f}"
        lines.append(f"| {label} | {np.mean(y):.3f} | " + " | ".join(cells) + " |")
    lines += ["", f"Logistic weights (intercept, log1p rel_width, log1p struct_sens, log1p method_sens, zero_in): "
              f"{np.round(w, 3).tolist()}"]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--replicates", type=int, default=2)
    parser.add_argument("--seed-base", type=int, default=20261301)
    args = parser.parse_args(argv)
    jobs = []
    for split in ("development", "confirmatory"):
        for t_idx, topo in enumerate(load_bank("D-07", split)):
            for rep in range(args.replicates):
                jobs.append((topo, t_idx + (100 if split == "confirmatory" else 0), rep, split, args.seed_base, [80, 150]))
    with ProcessPoolExecutor(args.workers) as pool:
        rows = [r for rs in pool.map(run_unit, jobs) for r in rs]
    out = ROOT / "results" / "rq44_flags"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "pairs.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    (out / "summary.md").write_text(summarize(rows), encoding="utf-8")
    print(f"{len(rows)} pairs -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
