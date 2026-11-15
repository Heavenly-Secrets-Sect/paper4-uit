"""P4-H8 equal-guarantee comparison dump (feedback point 6): per-pair (dist, half) of several methods on the same units.

Same units, seeds and cells as p4h7_units.py, but the calibrated-method list is a parameter, so every compared method
can be calibrated with the same unit-level order-statistic rule (p4h7_factors.py) on the same calibration topologies
and then evaluated on test topologies. Protocol: docs/ext/p4h8_cmp_spec.md. The test split needs --confirm-frozen and the
frozen factor file.
"""
import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path[:0] = [str(REPO / "src"), str(REPO / "experiments"), str(HERE)]
import run_experiment as R  # noqa: E402
from p4h7_units import build_cfg  # noqa: E402
from paper4.topology import load_bank  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", default="P4-H8")
    ap.add_argument("--split", required=True, choices=["design", "calibration", "test"])
    ap.add_argument("--methods", required=True, help="comma list of registered method names")
    ap.add_argument("--lag", type=int, default=1)
    ap.add_argument("--T", default="40,80,150")
    ap.add_argument("--rates", default="0.2,0.5")
    ap.add_argument("--seed-base", type=int, default=20261116)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--max-topologies", type=int, default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--confirm-frozen", action="store_true")
    ap.add_argument("--frozen", default="experiments/calibration/p4h8_cmp_frozen.json")
    a = ap.parse_args(argv)
    if a.split == "test" and not (a.confirm_frozen and (REPO / a.frozen).exists()):
        raise SystemExit("the test split is run once, after the factors are frozen")
    methods = a.methods.split(",")
    cfg = build_cfg(a.split, a.T, a.seed_base, a.lag, a.rates)
    cfg["methods"] = methods
    cfg["calibrate_methods"] = methods
    topologies = load_bank(a.bank, a.split)[: a.max_topologies]
    ccfg = dict(cfg, replicates=1)
    jobs = [(ccfg, topo, t_idx, 0, None, "calibration") for t_idx, topo in enumerate(topologies)]
    t0, records = time.perf_counter(), []
    prefixes = tuple(m + "|" for m in methods)
    with ProcessPoolExecutor(a.workers) as pool:
        for i, out in enumerate(pool.map(R.run_unit, jobs)):
            for p in out["pairs"]:
                if "counts" in p or not p["cell"].startswith(prefixes):
                    continue
                records.append({"unit": topologies[i].id, "profile": topologies[i].profile, "cell": p["cell"],
                                "dist": p["dist"], "half": p["half"]})
            if i % 25 == 0:
                print(i, round(time.perf_counter() - t0), "s", flush=True)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"bank": a.bank, "split": a.split, "lag": a.lag, "T": cfg["T"], "n_units": len(topologies),
                               "seed_base": a.seed_base, "methods": methods, "records": records}))
    print("done", len(records), "records", round(time.perf_counter() - t0), "s", flush=True)


if __name__ == "__main__":
    main()
