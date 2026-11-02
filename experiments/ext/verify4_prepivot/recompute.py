"""Independent recomputation of r4prepivot primary numbers (skeptic verification)."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path("/Users/kietnt/Desktop/Workspace/Paper4_UIT"); RES = ROOT/"results"
part = sys.argv[1]; stored = sys.argv[2]
rows = [json.loads(l) for l in open(RES/f"ext_r4prepivot_{part}/rows.jsonl")]
st = {}
for l in open(RES/stored/"runs.jsonl"):
    r = json.loads(l)
    if r["method"] == "tolerant_v5_1":
        st[(r.get("scenario","clean"), r["topology"], r["replicate"], r["T"], r["kind"], float(r["rate"]))] = r
# pairing: compare every float field shared
same = diff = miss = 0; maxd = 0
for r in rows:
    if r["method"] != "tolerant_v5_1": continue
    k = (r.get("scenario","clean"), r["topology"], r["replicate"], r["T"], r["kind"], float(r["rate"]))
    s = st.get(k)
    if s is None: miss += 1; continue
    if r["status"] != s["status"]: diff += 1; continue
    if r["status"] != "ok": same += 1; continue
    d = max(abs(r[f]-s[f]) for f in ("iscore_nonnull_mean","coverage_nonnull","width_kept","iscore_null_mean") if r.get(f) is not None and s.get(f) is not None)
    maxd = max(maxd, d)
    if d < 1e-9 and r["n_covered_nonnull"] == s["n_covered_nonnull"]: same += 1
    else: diff += 1
out = {"pairing": {"same": same, "diff": diff, "missing": miss, "max_abs_diff": maxd}}
by = defaultdict(dict)
for r in rows: by[(r.get("scenario","clean"), r["T"], r["kind"], float(r["rate"]))].setdefault((r["topology"], r["replicate"]), {})[r["method"]] = r
B = 20000
cells = []
for c, runs in by.items():
    rec = {"cell": list(c), "n": len(runs)}
    for m in ("tolerant_v5_1","tolerant_v5_1_pp","tolerant_v5_1_pp_orig"):
        cov = sum(d[m]["n_covered_nonnull"] for d in runs.values() if d[m]["status"]=="ok")
        tot = sum(d["tolerant_v5_1"]["n_nonnull"] or 0 for d in runs.values())
        ok = [d[m] for d in runs.values() if d[m]["status"]=="ok"]
        rec[m] = {"cov": cov/tot, "IS": float(np.mean([r["iscore_nonnull_mean"] for r in ok])), "ok": len(ok),
                  "cov_runmean": float(np.mean([r["coverage_nonnull"] for r in ok]))}
    # ratio, own bootstrap with different seed
    for m in ("tolerant_v5_1_pp","tolerant_v5_1_pp_orig"):
        prs = [(t, d[m]["iscore_nonnull_mean"], d["tolerant_v5_1"]["iscore_nonnull_mean"]) for (t,_), d in runs.items()
               if d[m]["status"]=="ok" and d["tolerant_v5_1"]["status"]=="ok"]
        tp = sorted({p[0] for p in prs})
        num = np.array([sum(p[1] for p in prs if p[0]==t) for t in tp]); den = np.array([sum(p[2] for p in prs if p[0]==t) for t in tp])
        rng = np.random.default_rng(777)
        idx = rng.integers(0, len(tp), (B, len(tp)))
        bt = num[idx].sum(1)/den[idx].sum(1)
        rec[m]["R"] = float(num.sum()/den.sum()); rec[m]["ci"] = [float(np.quantile(bt,.025)), float(np.quantile(bt,.975))]
        rec[m]["p_ni"] = float((1+(bt>=1.10).sum())/(B+1)); rec[m]["p_worse"] = float((1+(bt<=1.0).sum())/(B+1))
        # per-run paired sign: fraction of runs where pp IS > v51 IS
        rec[m]["frac_runs_worse"] = float(np.mean([p[1]>p[2] for p in prs]))
    pp = [d["tolerant_v5_1_pp"] for d in runs.values() if d["tolerant_v5_1_pp"]["status"]=="ok"]
    f = np.array([r["info_f_pp"] for r in pp]); fo = np.array([r["info_f_orig"] for r in pp])
    rec["f_pp_med"] = float(np.median(f)); rec["f_orig_med"] = float(np.median(fo))
    rec["f_v51_eff"] = next(iter(runs.values()))["tolerant_v5_1"]["f_v51_eff"]
    rec["f_ratio"] = rec["f_pp_med"]/rec["f_v51_eff"]
    # what factor would v51-scale need: fraction of pp runs with f >= bank
    rec["frac_f_ge_bank"] = float(np.mean(f >= rec["f_v51_eff"]))
    cells.append(rec)
def holm(ps, a=0.05):
    o = np.argsort(ps); rej=[False]*len(ps)
    for i, j in enumerate(o):
        if ps[j] <= a/(len(ps)-i): rej[j]=True
        else: break
    return rej
for m in ("tolerant_v5_1_pp","tolerant_v5_1_pp_orig"):
    for key in ("p_ni","p_worse"):
        rj = holm([c[m][key] for c in cells])
        for c, r in zip(cells, rj): c[m][key+"_holm"] = r
    out[m+"_counts"] = {"ni_holm": sum(c[m]["p_ni_holm"] for c in cells), "worse_holm": sum(c[m]["p_worse_holm"] for c in cells),
                        "worse_raw": sum(c[m]["p_worse"] < 0.05 for c in cells), "cov_ge_090": sum(c[m]["cov"]>=0.90 for c in cells), "n_cells": len(cells)}
out["cells"] = cells
json.dump(out, open(RES/f"ext_verify4_prepivot/recompute_{part}.json","w"), indent=1)
print(json.dumps(out["pairing"]), json.dumps(out["tolerant_v5_1_pp_counts"]), json.dumps(out["tolerant_v5_1_pp_orig_counts"]))
for c in cells:
    v,p,o = c["tolerant_v5_1"], c["tolerant_v5_1_pp"], c["tolerant_v5_1_pp_orig"]
    print(c["cell"], c["n"], f"cov {v['cov']:.3f}->{p['cov']:.3f} (orig {o['cov']:.3f}) IS {v['IS']:.2f}->{p['IS']:.2f} R {p['R']:.3f} [{p['ci'][0]:.3f},{p['ci'][1]:.3f}] pni {p['p_ni']:.3f} pw {p['p_worse']:.4f} worseH {p['p_worse_holm']} f {c['f_pp_med']:.3f}/{c['f_v51_eff']:.2f}={c['f_ratio']:.2f} fge {c['frac_f_ge_bank']:.2f} runsworse {p['frac_runs_worse']:.2f} ok {p['ok']}")
