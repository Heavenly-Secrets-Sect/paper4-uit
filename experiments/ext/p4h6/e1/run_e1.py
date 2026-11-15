"""E1 stage C on P4-H6 development (frozen spec docs/ext/p4h6_e1.md): tolerant_v5_1 with width-factor rule R0, R1, R2 or R3.

Thin driver around experiments/ext/r4ngorient/run_ng.py (not modified), same as run_e2.py but for the P4-H6 `development` split.
Guards: bank must be P4-H6, split development, phase main, methods oracle and tolerant_v5_1, shock gauss, the output directory must not
exist (no reruns), the frozen factor file must match its sha256. `--smoke` swaps the bank to D-07 development and writes to <name>_smoke.

Run: python experiments/ext/p4h6/e1/run_e1.py --config experiments/configs/ext_p4h6_e1_<r0|r1|r2|r3>.json --workers 4
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "experiments" / "ext" / "r4ngorient"))
import run_ng as R  # noqa: E402

ALLOWED_METHODS = ("oracle", "tolerant_v5_1")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--max-units", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    if cfg.get("phase", "main") != "main" or cfg.get("shock") != "gauss":
        raise SystemExit("only phase main and shock gauss are allowed")
    if sorted(cfg["methods"]) != sorted(ALLOWED_METHODS):
        raise SystemExit(f"methods must be {ALLOWED_METHODS}")
    if a.smoke:
        cfg = {**cfg, "bank": "D-07", "split": "development", "name": cfg["name"] + "_smoke"}
    else:
        if cfg["bank"] != "P4-H6" or cfg["split"] != "development":
            raise SystemExit("this driver runs only P4-H6 development (use --smoke for a dry run)")
        if a.max_units:
            raise SystemExit("--max-units is only for --smoke")
    out = R.ROOT / "results" / cfg["name"]
    if out.exists():
        raise SystemExit(f"{out} exists: no reruns")
    fac = R.load_frozen(cfg)
    ext = R.ext_methods()
    for name in cfg["methods"]:
        if name != "oracle" and name not in ext:
            raise SystemExit(f"unknown method {name}")
    for name in cfg.get("calibrate_methods", []):
        for T in cfg["T"]:
            for wk in ("none", "extra", "missing", "reversed"):
                if f"{name}|{T}|{wk}" not in fac:
                    raise SystemExit(f"missing width factor {name}|{T}|{wk}")
    topologies = R.load_bank(cfg["bank"], cfg["split"])
    jobs = [(cfg, topo, t_idx, rep, fac, "main") for t_idx, topo in enumerate(topologies) for rep in range(cfg["replicates"])]
    if a.max_units:
        jobs = jobs[: a.max_units]
    start = time.perf_counter()
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(a.workers) as pool:
        for res in pool.map(R.run_unit, jobs):
            rows.extend(res["rows"])
    secs = round(time.perf_counter() - start, 1)
    with open(out / "runs.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    manifest = {"config": cfg, "phase": "main", "seconds": secs, "n_units": len(jobs), "n_rows": len(rows), "workers": a.workers,
                "python": sys.executable, "numpy": np.__version__, "platform": platform.platform(),
                "frozen_calibration_sha256": cfg.get("frozen_calibration_sha256"),
                "topologies": [{"id": t.id, "profile": t.profile, "sha256": t.sha256} for t in topologies]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"{len(rows)} rows, {len(jobs)} units in {secs} s -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
