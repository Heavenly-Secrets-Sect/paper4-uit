"""Width table of tolerant_auto3 (and its no-gate ablation) on the calibration bank.

Uses exactly the calibration units of the runner (D-07H development, seed_base + 500000 + 1000 *
topology + replicate, the config's calibration kinds and rates, same data streams). For every run
it fits the raw (unwidened) module in both gate states and records which state the gate chose.
The factor per key is chosen as in run_experiment.calibrate: the smallest c on the grid 1.0..10.0
whose pooled coverage of non-null pairs reaches min(0.95, max coverage - 0.005).

- closed|T : runs where the gate stayed closed (or the gate could not be computed), closed fit
- open|T   : runs where the gate fired, open fit
- nogate|T : all runs, open fit (ablation without the gate)

The keys are the module's own diagnosis; the stated damage is never read.

Run: python experiments/ext/gate/calibrate_gate.py --config experiments/configs/ext_gate_auto3.json --workers 3
Writes experiments/ext/gate/width_table.json and width_table_detail.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from run_experiment import C_GRID, generator_config, unit_skeletons  # noqa: E402
from paper4 import ext_gate as G  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.metrics import truth_effects  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

OUT = Path(__file__).resolve().parent


def unit_job(args):
    cfg, t_idx, rep = args
    cal = cfg["calibration"]
    topo = load_bank(cal["bank"], cal["split"])[t_idx]
    ccfg = dict(cfg, damage={"kinds": cal["kinds"], "rates": cal.get("rates", cfg["damage"]["rates"])})
    gen = generator_config(cfg)
    lag_max, H, n_boot = gen.lag_max, cfg["H"], cfg["n_boot"]
    unit = cfg["seed_base"] + 500_000 + 1000 * t_idx + rep
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skels = unit_skeletons(sem, unit, ccfg)
    _, C_true, _, _ = truth_effects(sem, H)
    nonnull = ~np.eye(sem.n, dtype=bool) & (np.abs(C_true) > cfg["tau_effect"])
    out = []
    for T in cfg["T"]:
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        for c_idx, ((kind, rate), skel) in enumerate(skels.items()):
            rec = {"T": T, "kind": kind, "rate": rate, "topology": topo.id}
            for s_idx, state in enumerate(("closed", "open")):
                res = G.auto3_raw(data, skel, lag_max, H, n_boot, np.random.default_rng([unit, 31, T, c_idx, s_idx]),
                                  force_state=state)
                if s_idx == 0:
                    gate = G.diagnose_gate(data, skel, lag_max)["p_gate"]
                    rec["state"] = "open" if (gate is not None and gate <= G.ALPHA_GATE) else "closed"
                    rec["p_gate"] = gate
                if res.status == "ok":
                    mid, half = (res.lo + res.hi) / 2, (res.hi - res.lo) / 2
                    rec[state] = {"dist": np.abs(C_true - mid)[nonnull].tolist(), "half": half[nonnull].tolist()}
            out.append(rec)
    return out


def factor(dist, half) -> float:
    dist, half = np.array(dist), np.array(half)
    cov = np.array([(dist <= c * half).mean() for c in C_GRID])
    target = min(0.95, cov.max() - 0.005)
    return float(C_GRID[np.argmax(cov >= target)])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args(argv)
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    cal = cfg["calibration"]
    n_topo = len(load_bank(cal["bank"], cal["split"])[: cal.get("max_topologies") or None])
    jobs = [(cfg, t, rep) for t in range(n_topo) for rep in range(cal["replicates"])]
    with ProcessPoolExecutor(args.workers) as pool:
        recs = [r for out in pool.map(unit_job, jobs) for r in out]
    pooled = defaultdict(lambda: ([], []))
    detail = defaultdict(lambda: {"closed": 0, "open": 0})
    for r in recs:
        detail[f"{r['T']}|{r['kind']}|{r['rate']}"][r["state"]] += 1
        if r["state"] in r and r.get(r["state"]):
            key = f"{r['state']}|{r['T']}"
            pooled[key][0].extend(r[r["state"]]["dist"])
            pooled[key][1].extend(r[r["state"]]["half"])
        if r.get("open"):
            pooled[f"nogate|{r['T']}"][0].extend(r["open"]["dist"])
            pooled[f"nogate|{r['T']}"][1].extend(r["open"]["half"])
    table = {k: factor(*v) for k, v in sorted(pooled.items())}
    (OUT / "width_table.json").write_text(json.dumps(table, indent=2), encoding="utf-8")
    (OUT / "width_table_detail.json").write_text(json.dumps(
        {"n_runs": len(recs), "n_boot": cfg["n_boot"], "alpha_gate": G.ALPHA_GATE, "flip_prob": G.FLIP_PROB,
         "gate_state_counts": detail, "n_pairs": {k: len(v[0]) for k, v in pooled.items()}}, indent=2),
        encoding="utf-8")
    print(json.dumps(table, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
