"""E1 stage B: build the width-factor tables R1 (one number), R2 (per T), R3 (per kind) from the calibration pairs
(frozen spec docs/ext/p4h6_e1.md), and the four evaluation configs (R0 to R3) on P4-H6 development.

R0 is experiments/ext/v51/frozen_v4_v51.json verbatim. R1 to R3 use the runner's choice rule (smallest c in C_GRID whose coverage reaches
min(0.95, max coverage - 0.005)) on the pooled pairs. Writes experiments/ext/p4h6/e1/factors_{r1,r2,r3}.json and
experiments/configs/ext_p4h6_e1_{r0,r1,r2,r3}.json, each config carrying its factor file's sha256.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "experiments" / "ext" / "r4ngorient"))
import run_ng as R  # noqa: E402

NAME = "tolerant_v5_1"
TS = (40, 80, 150)
KINDS = ("none", "extra", "missing", "reversed")


def pick(dist, half):
    dist, half = np.asarray(dist), np.asarray(half)
    cov = np.array([(dist <= c * half).mean() for c in R.C_GRID])
    target = min(1 - R.M.ALPHA, cov.max() - 0.005)
    return float(R.C_GRID[np.argmax(cov >= target)])


def pooled(cells, keys):
    d, h = [], []
    for k in keys:
        d += cells[k]["dist"]
        h += cells[k]["half"]
    return pick(d, h)


SMOKE = "--smoke" in sys.argv  # dry run on the smoke calibration; writes under experiments/ext/p4h6/e1/smoke/ only


def main() -> int:
    cells = json.loads((ROOT / ("results/ext_p4h6_e1_cal_smoke" if SMOKE else "results/ext_p4h6_e1_cal") / "calpairs.json").read_text(encoding="utf-8"))
    key = lambda T, k: f"{NAME}|{T}|{k}"  # noqa: E731
    allk = [key(T, k) for T in TS for k in KINDS]
    miss = [k for k in allk if k not in cells]
    if miss:
        raise SystemExit(f"missing calibration cells: {miss}")
    r1 = pooled(cells, allk)
    r2 = {T: pooled(cells, [key(T, k) for k in KINDS]) for T in TS}
    r3 = {k: pooled(cells, [key(T, k) for T in TS]) for k in KINDS}
    tables = {
        "r1": {key(T, k): r1 for T in TS for k in KINDS},
        "r2": {key(T, k): r2[T] for T in TS for k in KINDS},
        "r3": {key(T, k): r3[k] for T in TS for k in KINDS},
    }
    base = json.loads((ROOT / "experiments/configs/ext_p4h6_e2_gauss.json").read_text(encoding="utf-8"))
    cfgs = {}
    for tag in ("r0", "r1", "r2", "r3"):
        if tag == "r0":
            path = "experiments/ext/v51/frozen_v4_v51.json"
        else:
            path = f"experiments/ext/p4h6/e1/{'smoke/' if SMOKE else ''}factors_{tag}.json"
            note = {"_note": f"E1 rule {tag.upper()}: factors from the calibration pairs of D-07H development (docs/ext/p4h6_e1.md)."}
            (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
            (ROOT / path).write_text(json.dumps({**note, **tables[tag]}, indent=1) + "\n", encoding="utf-8")
        sha = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        cfg = {**base, "name": f"ext_p4h6_e1_{tag}", "split": "development", "shock": "gauss", "seed_base": 90261114,
               "frozen_calibration": path, "frozen_calibration_sha256": sha,
               "purpose": f"E1 evaluation on P4-H6 development, rule {tag.upper()}. Spec: docs/ext/p4h6_e1.md."}
        cfg_path = ROOT / (f"experiments/ext/p4h6/e1/smoke/ext_p4h6_e1_{tag}.json" if SMOKE else f"experiments/configs/ext_p4h6_e1_{tag}.json")
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
        cfgs[tag] = sha
    print("R1 =", r1, "| R2 =", r2, "| R3 =", r3)
    print("config sha256:", cfgs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
