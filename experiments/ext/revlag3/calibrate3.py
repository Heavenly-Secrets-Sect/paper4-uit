"""R3-4: tune the width factors of tolerant_v4R / tolerant_v4Rmap on D-07H development with the
main runner's own calibration (experiments/run_experiment.py: calibrate), then write the frozen file
experiments/ext/revlag3/frozen_revlag3.json =
  mod|*            verbatim experiments/calibration/tolerant_v4_frozen.json (tolerant_v4)
  tolerant_v5_1|*  verbatim experiments/ext/v51/frozen_v4_v51.json (for the R3-9 rows)
  tolerant_v4R|T|reversed, tolerant_v4Rmap|T|reversed  (this calibration; also |none as computed)
Run: python experiments/ext/revlag3/calibrate3.py --workers 3
"""
import argparse, hashlib, json, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
from run_experiment import calibrate

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); a = ap.parse_args()
    cfg = json.loads((ROOT / "experiments/configs/ext_revlag3_cal.json").read_text())
    t0 = time.perf_counter()
    c = calibrate(cfg, a.workers)
    sec = round(time.perf_counter() - t0, 1)
    out = ROOT / "results/ext_revlag3_cal"; out.mkdir(parents=True, exist_ok=True)
    (out / "calibration.json").write_text(json.dumps(c, indent=2, sort_keys=True))
    v4 = json.loads((ROOT / "experiments/calibration/tolerant_v4_frozen.json").read_text())
    v51 = json.loads((ROOT / "experiments/ext/v51/frozen_v4_v51.json").read_text())
    fz = {"_note": "Frozen width factors for the revlag3 runs (round 3). mod|* = experiments/calibration/tolerant_v4_frozen.json "
                   "verbatim; tolerant_v5_1|* = experiments/ext/v51/frozen_v4_v51.json verbatim; tolerant_v4R|*, tolerant_v4Rmap|* "
                   "= run_experiment.calibrate on D-07H development (results/ext_revlag3_cal/calibration.json; effective factor = "
                   "value x 0.5 pre-scale)."}
    fz.update({k: v for k, v in v4.items() if k.startswith("mod|")})
    fz.update({k: v for k, v in v51.items() if k.startswith("tolerant_v5_1|")})
    fz.update({k: v for k, v in sorted(c.items()) if k.startswith("tolerant_v4R")})
    p = ROOT / "experiments/ext/revlag3/frozen_revlag3.json"
    p.write_text(json.dumps(fz, indent=2))
    print(json.dumps(c, indent=1, sort_keys=True)); print("seconds", sec, "sha256", hashlib.sha256(p.read_bytes()).hexdigest())
    (out / "timing.txt").write_text(f"calibration seconds {sec} workers {a.workers}\nfrozen sha256 {hashlib.sha256(p.read_bytes()).hexdigest()}\n")


if __name__ == "__main__":
    main()
