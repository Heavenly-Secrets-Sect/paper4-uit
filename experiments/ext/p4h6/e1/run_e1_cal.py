"""E1 stage A: collect the calibration pairs of tolerant_v5_1 on D-07H development (frozen spec docs/ext/p4h6_e1.md).

Thin wrapper around experiments/ext/r4ngorient/run_ng.py (not modified): it runs run_ng.run_unit in phase "calibration" with the
same unit seeds as the runner's calibration (seed_base + 500000 + 1000*topology + replicate) and stores, per cell
"tolerant_v5_1|T|kind", the non-null distances |C_true - mid| and half-widths. Nothing here touches any P4-H6 split.
Writes results/ext_p4h6_e1_cal/{calpairs.json, replication.json, manifest.json}.

Run: python experiments/ext/p4h6/e1/run_e1_cal.py --config experiments/configs/ext_p4h6_e1_cal.json --workers 4
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "experiments" / "ext" / "r4ngorient"))
import run_ng as R  # noqa: E402


def pick(dist, half):
    dist, half = np.asarray(dist), np.asarray(half)
    cov = np.array([(dist <= c * half).mean() for c in R.C_GRID])
    target = min(1 - R.M.ALPHA, cov.max() - 0.005)
    return float(R.C_GRID[np.argmax(cov >= target)])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    if cfg["bank"] != "D-07H" or cfg["split"] != "development" or cfg.get("phase") != "calibration":
        raise SystemExit("E1 stage A runs only D-07H development, phase calibration")
    out = ROOT / "results" / cfg["name"]
    if out.exists():
        raise SystemExit(f"{out} exists: no reruns")
    topologies = R.load_bank(cfg["bank"], cfg["split"])[: cfg.get("max_topologies") or None]
    jobs = [(cfg, topo, t_idx, rep, {}, "calibration") for t_idx, topo in enumerate(topologies) for rep in range(cfg["replicates"])]
    start = time.perf_counter()
    cells = {}
    with ProcessPoolExecutor(a.workers) as pool:
        for res in pool.map(R.run_unit, jobs):
            for p in res["calpairs"]:
                d = cells.setdefault(p["cell"], {"dist": [], "half": []})
                d["dist"].extend(p["dist"])
                d["half"].extend(p["half"])
    secs = round(time.perf_counter() - start, 1)
    out.mkdir(parents=True, exist_ok=True)
    (out / "calpairs.json").write_text(json.dumps(cells), encoding="utf-8")
    frozen = json.loads((ROOT / "experiments/ext/v51/frozen_v4_v51.json").read_text(encoding="utf-8"))
    rep = {c: {"n_pairs": len(v["dist"]), "recomputed": pick(v["dist"], v["half"]), "frozen_R0": frozen.get(c)} for c, v in sorted(cells.items())}
    (out / "replication.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    (out / "manifest.json").write_text(json.dumps({"config": cfg, "seconds": secs, "n_units": len(jobs), "python": sys.executable}, indent=1), encoding="utf-8")
    same = sum(1 for v in rep.values() if v["frozen_R0"] is not None and abs(v["recomputed"] - v["frozen_R0"]) < 1e-9)
    print(f"{len(cells)} cells, {len(jobs)} units in {secs} s; recomputed equals frozen R0 in {same}/{len(rep)} cells -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
