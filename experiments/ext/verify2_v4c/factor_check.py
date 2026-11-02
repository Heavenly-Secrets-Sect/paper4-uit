"""Recompute effective factors of ext_v4c_eval/calibration.json and compare with frozen v4 and E3 _cal."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
c = json.loads((ROOT / "results/ext_v4c_eval/calibration.json").read_text())
fr = json.loads((ROOT / "experiments/calibration/tolerant_v4_frozen.json").read_text())
e3 = json.loads((ROOT / "results/ext_redteam_calbase/calibration.json").read_text())
K = ("none", "extra", "missing", "reversed"); TS = (40, 80, 150)
eff = {}
for m in ("tolerant_v4c", "pselect_union_c2", "ida_union_c2", "bvar_minnesota_c2"):
    for T in TS:
        for k in K:
            p = 1.0 if (m == "ida_union_c2" and k == "missing") else 0.5
            eff[f"{m}|{T}|{k}"] = round(c[f"{m}|{T}|{k}"] * p, 4)
out = {"effective": eff,
       "v4c_minus_v4": {f"{T}|{k}": round(eff[f"tolerant_v4c|{T}|{k}"] - fr[f"mod|{T}|{k}"], 4) for T in TS for k in K},
       "below_1_outside_missing": sorted(k for k, v in eff.items() if not k.endswith("missing") and not k.startswith("tolerant") and v < 1 - 1e-9),
       "c2_minus_E3": {}, "at_floor": [k for k, v in eff.items() if abs(v - (1.0 if k.startswith("ida") and k.endswith("missing") else 0.5)) < 1e-9],
       "at_ceiling": [k for k, v in eff.items() if abs(v - (10.0 if k.startswith("ida") and k.endswith("missing") else 5.0)) < 1e-9],
       "mod_keys_equal_frozen": all(c[k] == v for k, v in fr.items() if k.startswith("mod|"))}
for x, xc in (("pselect_union_c2", "pselect_cal"), ("ida_union_c2", "ida_cal"), ("bvar_minnesota_c2", "bvar_cal")):
    for T in TS:
        for k in K:
            if e3[f"{xc}|{T}|{k}"] > 1.0:  # E3 not at floor
                out["c2_minus_E3"][f"{x}|{T}|{k}"] = [eff[f"{x}|{T}|{k}"], e3[f"{xc}|{T}|{k}"], round(eff[f"{x}|{T}|{k}"] - e3[f"{xc}|{T}|{k}"], 4)]
out["c2_vs_E3_abs_diff_ge_0.1"] = {k: v for k, v in out["c2_minus_E3"].items() if abs(v[2]) >= 0.1 - 1e-9}
print(json.dumps(out, indent=1))
(ROOT / "results/ext_verify2_v4c/factor_check.json").write_text(json.dumps(out, indent=1))
