"""Skeptic checks on the f_d vs damage claim (r4prepivot)."""
import json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
R = Path("/Users/kietnt/Desktop/Workspace/Paper4_UIT/results")
out = {}
rows = [json.loads(l) for l in open(R/"ext_r4prepivot_primary/rows.jsonl")]
rows += [json.loads(l) for l in open(R/"ext_r4prepivot_secondary/rows.jsonl")]
pp = [r for r in rows if r["method"]=="tolerant_v5_1_pp" and r["status"]=="ok"]
def sp(sub):
    x=[r["k"] for r in sub]; y=[r["info_f_pp"] for r in sub]
    rho,p = spearmanr(x,y); return {"rho": float(rho), "p": float(p), "n": len(sub)}
for T in (40,80,150):
    out[f"missing_only_T{T}"] = sp([r for r in pp if r["kind"]=="missing" and r["T"]==T])
    out[f"reversed_only_T{T}"] = sp([r for r in pp if r["kind"]=="reversed" and r["T"]==T])
    out[f"none_vs_missing_T{T}"] = sp([r for r in pp if r["kind"] in("missing","none") and r["T"]==T])
    out[f"targeted_flag_missing_T{T}"] = float(np.mean([r.get("info_v51_targeted",-1) for r in pp if r["kind"]=="missing" and r["T"]==T]))
# primary pooled as the report computed: missing+none (primary only has none at T80)
prim = [r for r in pp if r in pp]
P = [json.loads(l) for l in open(R/"ext_r4prepivot_primary/rows.jsonl")]
P = [r for r in P if r["method"]=="tolerant_v5_1_pp" and r["status"]=="ok"]
out["report_pooled_missing+none_primary"] = sp([r for r in P if r["kind"] in ("missing","none")])
out["primary_missing_only_pooledT"] = sp([r for r in P if r["kind"]=="missing"])
# median f per cell, primary+secondary, plus bank eff
cells = {}
for r in pp:
    cells.setdefault((r["T"], r["kind"], r["rate"]), []).append(r["info_f_pp"])
bank = {}
for r in rows:
    if r["method"]=="tolerant_v5_1": bank[(r["T"], r["kind"], r["rate"])] = r["f_v51_eff"]
out["cells"] = {f"T{k[0]}|{k[1]}|{k[2]}": {"f_med": float(np.median(v)), "bank_eff": bank[k], "gap": bank[k]-float(np.median(v))} for k, v in sorted(cells.items())}
json.dump(out, open(R/"ext_verify4_prepivot/fcheck.json","w"), indent=1)
print(json.dumps(out, indent=1))
