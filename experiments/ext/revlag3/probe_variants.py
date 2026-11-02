"""R3-4 design probe 2, D-07H development ONLY: three variants of tolerant_v4R suggested by probe 1
(tempered evidence, defensive mixture with uniform draws, parametric bootstrap of the orientation
decision). Calibrates them with run_experiment.calibrate on D-07H development (calibration units),
writes experiments/ext/revlag3/probe_frozen_variants.json (mod|* of v4 + v4R/v4Rmap + variants),
and the probe config experiments/configs/ext_revlag3_probe2.json (D-07H development main units).
Run: python experiments/ext/revlag3/probe_variants.py --workers 3, then run_pairs3.py on the config.
"""
import argparse, hashlib, json, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
from run_experiment import calibrate


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); a = ap.parse_args()
    from paper4.ext_revlag3 import PROBE_VARIANTS
    var = list(PROBE_VARIANTS)
    cfg = json.loads((ROOT / "experiments/configs/ext_revlag3_cal.json").read_text())
    cfg.update(name="ext_revlag3_cal_variants", methods=var, calibrate_methods=var)
    t0 = time.perf_counter(); c = calibrate(cfg, a.workers); sec = round(time.perf_counter() - t0, 1)
    out = ROOT / "results/ext_revlag3_probe2"; out.mkdir(parents=True, exist_ok=True)
    (out / "calibration_variants.json").write_text(json.dumps(c, indent=2, sort_keys=True))
    fz = json.loads((ROOT / "experiments/ext/revlag3/frozen_revlag3.json").read_text())
    fz["_note"] = "PROBE ONLY (D-07H). " + fz["_note"]
    fz.update({k: v for k, v in c.items() if k.split("|")[0] in var})
    p = ROOT / "experiments/ext/revlag3/probe_frozen_variants.json"; p.write_text(json.dumps(fz, indent=2))
    pc = json.loads((ROOT / "experiments/configs/ext_revlag3_probe.json").read_text())
    pc.update(name="ext_revlag3_probe2", methods=["oracle", "tolerant_v4", "tolerant_v4R"] + var,
              calibrate_methods=["tolerant_v4R"] + var, frozen_calibration="experiments/ext/revlag3/probe_frozen_variants.json",
              frozen_calibration_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
              purpose="R3-4 design probe 2, D-07H development ONLY (20 topologies x 1 replicate, reversed cells): variants of tolerant_v4R. Not used for any claim.")
    (ROOT / "experiments/configs/ext_revlag3_probe2.json").write_text(json.dumps(pc, indent=2))
    print(json.dumps({k: v for k, v in c.items() if k.split("|")[0] in var}, indent=1, sort_keys=True), "seconds", sec)
    (out / "timing.txt").write_text(f"variant calibration seconds {sec}\n")


if __name__ == "__main__":
    main()
