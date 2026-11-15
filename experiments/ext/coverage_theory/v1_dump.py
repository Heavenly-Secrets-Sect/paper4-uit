"""V1 dump: rerun the v5.1 calibration phase of ext_v51_eval on D-07H development and keep the per-pair
(dist, half) per unit instead of pooling them. Output: results/ext_coverage_v1/v1_pairs.json (about 0.5 MB,
regenerate in about a minute with 10 workers). Read-only with respect to everything else in the repo.
"""
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

OUT = REPO / "results/ext_coverage_v1/v1_pairs.json"


def main():
    cfg = json.loads((REPO / "experiments/configs/ext_v51_eval.json").read_text())
    cal = cfg["calibration"]
    topologies = load_bank(cal["bank"], cal["split"])
    ccfg = dict(cfg, replicates=cal["replicates"])
    ccfg["damage"] = {"kinds": cal["kinds"], "rates": cal.get("rates", cfg["damage"]["rates"])}
    jobs = [(ccfg, topo, t_idx, rep, None, "calibration")
            for t_idx, topo in enumerate(topologies) for rep in range(cal["replicates"])]
    print(len(jobs), "calibration jobs", flush=True)
    t0 = time.perf_counter()
    units = []
    with ProcessPoolExecutor(10) as pool:
        for i, out in enumerate(pool.map(R.run_unit, jobs)):
            for p in out["pairs"]:
                if "counts" in p or not p["cell"].startswith("tolerant_v5_1|"):
                    continue
                units.append({"job": i, "cell": p["cell"], "dist": p["dist"], "half": p["half"]})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(units))
    print("done", len(units), "unit-cells", round(time.perf_counter() - t0), "s", flush=True)


if __name__ == "__main__":
    main()
