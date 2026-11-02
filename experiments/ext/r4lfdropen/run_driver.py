"""Driver for the r4lfdropen runs: the unmodified runner (experiments/run_experiment.py), with two hooks.

- Without --frozen-from: the runner's own calibration runs; its raw output (before the runner overlays
  ``frozen_calibration``) is also written to results/<name>/calibration_raw.json, so the factors the
  candidate's calibration would give tolerant_v5_1 can be compared with the frozen ones.
- With --frozen-from <json>: calibration is not re-run; the width factors are read from that file
  (keys starting with "_" dropped). Used for the scenario runs, whose calibration block is the eval run's.

Run: /Users/kietnt/miniconda3/bin/python experiments/ext/r4lfdropen/run_driver.py --config <cfg> --workers 3 [--frozen-from <json>]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

import run_experiment as RE  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--frozen-from", default=None)
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    out = ROOT / "results" / cfg["name"]
    out.mkdir(parents=True, exist_ok=True)
    orig = RE.calibrate
    if a.frozen_from:
        frozen = json.loads((ROOT / a.frozen_from).read_text(encoding="utf-8"))

        def calibrate(cfg_, workers):
            (out / "calibration_source.txt").write_text(a.frozen_from + "\n", encoding="utf-8")
            return {k: v for k, v in frozen.items() if not k.startswith("_")}
    else:
        def calibrate(cfg_, workers):
            res = orig(cfg_, workers)
            (out / "calibration_raw.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
            return res
    RE.calibrate = calibrate
    return RE.main(["--config", a.config, "--workers", str(a.workers)])


if __name__ == "__main__":
    raise SystemExit(main())
