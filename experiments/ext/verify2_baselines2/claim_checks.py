"""Skeptic claim checks (verify2_baselines2) on stored files only. Writes results/ext_verify2_baselines2/claim_checks.json."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
R = ROOT / "results/ext_baselines2_eval"
e = json.load(open(R / "envelope.json")); n = json.load(open(R / "numbers.json"))
h = set(e["holm_rejected"])
out = {}
for rate in (0.2, 0.5):
    cell = e["cells"][f"80|missing|{rate}"]
    out[f"T80_m{rate}_baselines_not_holm"] = sorted(m for m in cell if m not in ("strongest", "strongest_cov90", "tolerant_v5")
                                                    and isinstance(cell[m], dict) and f"80|{rate}|{m}" not in h)
lag = n["deleted_pairs_by_lag"]
out["v4_lag0_minus_lag12_T>=80"] = {k: [round(v["diff"], 3), round(v["lo"], 3), round(v["hi"], 3)] for k, v in lag.items()
                                    if k.endswith("tolerant_v4") and not k.startswith("40")}
out["bvar_v2_cal_lag0_cov_all_T"] = {k: round(v["cov0"], 3) for k, v in lag.items() if k.endswith("bvar_minnesota_v2_cal")}
v = n["v2_vs_v1"]
out["pselect_v1_minus_v2_T80_missing"] = {k: v[k]["v1_minus_v2"] for k in ("80|missing|0.2|pselect_union_v2", "80|missing|0.5|pselect_union_v2")}
out["tally"] = n["tally_all_cells"]
(ROOT / "results/ext_verify2_baselines2/claim_checks.json").write_text(json.dumps(out, indent=1, default=float))
print(json.dumps(out, indent=1, default=float))
