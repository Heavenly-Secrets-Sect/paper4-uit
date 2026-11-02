"""Frozen width factors of r4ngorient (docs/ext/r4ngorient.md, section 5.2).

tolerant_v5_1|* and mod|* = experiments/ext/v51/frozen_v4_v51.json verbatim; tolerant_ngA|* and
tolerant_ngB|* = results/ext_r4ngorient_cal_gauss/calibration.json (Gaussian D-07H development).
Driver check: NG-A's none/extra factors must equal v5_1's (same method bit for bit, same stream).
Writes experiments/ext/r4ngorient/frozen_ngorient.json and prints its sha256.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
src = json.loads((ROOT / "experiments/ext/v51/frozen_v4_v51.json").read_text(encoding="utf-8"))
cal = json.loads((ROOT / "results/ext_r4ngorient_cal_gauss/calibration.json").read_text(encoding="utf-8"))
out = {"_note": "r4ngorient frozen width factors. tolerant_v5_1|* and mod|* = experiments/ext/v51/frozen_v4_v51.json "
                "verbatim; tolerant_ngA|* / tolerant_ngB|* tuned on Gaussian D-07H development by run_ng.py "
                "(phase calibration, results/ext_r4ngorient_cal_gauss/calibration.json)."}
out.update({k: v for k, v in src.items() if not k.startswith("_")})
need = [f"{m}|{T}|{wk}" for m in ("tolerant_ngA", "tolerant_ngB") for T in (40, 80, 150)
        for wk in ("none", "extra", "missing", "reversed")]
for k in need:
    if k not in cal:
        raise SystemExit(f"calibration lacks {k}")
    out[k] = cal[k]
checks = []
for T in (40, 80, 150):
    for wk in ("none", "extra"):
        a, b = out[f"tolerant_ngA|{T}|{wk}"], out[f"tolerant_v5_1|{T}|{wk}"]
        checks.append((T, wk, a, b, a == b))
path = ROOT / "experiments/ext/r4ngorient/frozen_ngorient.json"
path.write_text(json.dumps(out, indent=2), encoding="utf-8")
print("driver check NG-A none/extra == v5_1 frozen:", all(c[-1] for c in checks))
for c in checks:
    print("  ", c)
for m in ("tolerant_v5_1", "tolerant_ngA", "tolerant_ngB"):
    print(m, {f"{T}|{wk}": out[f"{m}|{T}|{wk}"] for T in (40, 80, 150) for wk in ("none", "extra", "missing", "reversed")})
print("sha256", hashlib.sha256(path.read_bytes()).hexdigest())
