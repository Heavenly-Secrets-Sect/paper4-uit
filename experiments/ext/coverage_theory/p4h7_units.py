"""P4-H7 unit dump: per-pair (dist, half) of tolerant_v5_1 for every unit, cell and damage rate.

Runs the calibration phase of the runner on one split of a bank and keeps the pairs instead of pooling.
Protocol: docs/ext/p4h7_spec.md. The test split is refused here: it is run once, by the main runner,
with the frozen factors.

    python experiments/ext/coverage_theory/p4h7_units.py --split design --out results/ext_p4h7_design/units.json
"""
import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "experiments"))
import run_experiment as R  # noqa: E402
from paper4.topology import load_bank  # noqa: E402


def build_cfg(split, T, seed_base, lag, rates):
    cfg = json.loads((REPO / "experiments/configs/ext_v51_eval.json").read_text())
    cfg.update({"name": f"p4h7_units_{split}", "T": [int(t) for t in str(T).split(",")], "methods": ["tolerant_v5_1"],
                "paired_references": [], "seed_base": seed_base, "calibrate_methods": ["tolerant_v5_1"]})
    cfg.pop("frozen_calibration", None)
    cfg["generator"] = dict(cfg["generator"], lag_max=lag)
    cfg["damage"] = {"kinds": ["extra", "missing", "reversed"], "rates": [float(r) for r in str(rates).split(",")]}
    return cfg


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", default="P4-H7")
    ap.add_argument("--split", required=True, choices=["design", "calibration", "test"])
    ap.add_argument("--lag", type=int, default=1)
    ap.add_argument("--T", default="19,30,40,80,150")
    ap.add_argument("--rates", default="0.2,0.5")
    ap.add_argument("--seed-base", type=int, default=20261115)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--max-topologies", type=int, default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--confirm-frozen", action="store_true", help="required for the test split")
    ap.add_argument("--frozen", default="experiments/calibration/p4h7_frozen.json", help="frozen factor file that must exist before the test split runs")
    a = ap.parse_args(argv)
    if a.split == "test" and not (a.confirm_frozen and (REPO / a.frozen).exists()):
        raise SystemExit("the test split runs once, after the freeze: the frozen factor file must exist and --confirm-frozen is required")

    cfg = build_cfg(a.split, a.T, a.seed_base, a.lag, a.rates)
    topologies = load_bank(a.bank, a.split)[: a.max_topologies]
    ccfg = dict(cfg, replicates=1)
    jobs = [(ccfg, topo, t_idx, 0, None, "calibration") for t_idx, topo in enumerate(topologies)]
    print(len(jobs), "units", flush=True)
    t0 = time.perf_counter()
    units = []
    with ProcessPoolExecutor(a.workers) as pool:
        for i, out in enumerate(pool.map(R.run_unit, jobs)):
            for p in out["pairs"]:
                if "counts" in p or not p["cell"].startswith("tolerant_v5_1|"):
                    continue
                units.append({"unit": topologies[i].id, "profile": topologies[i].profile, "cell": p["cell"],
                              "dist": p["dist"], "half": p["half"]})
            if i % 20 == 0:
                print(i, round(time.perf_counter() - t0), "s", flush=True)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"bank": a.bank, "split": a.split, "lag": a.lag, "T": cfg["T"], "n_units": len(topologies),
                               "seed_base": a.seed_base, "records": units}))
    print("done", len(units), "records", round(time.perf_counter() - t0), "s", flush=True)


if __name__ == "__main__":
    main()
