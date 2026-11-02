"""Skeptic recomputation of r4hubscreen numbers from runs.jsonl (independent code)."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path("/Users/kietnt/Desktop/Workspace/Paper4_UIT")
rows = []
for n in ("ext_r4hubscreen_lag2", "ext_r4hubscreen_lag1"):
    rows += [json.loads(l) for l in open(ROOT / "results" / n / "runs.jsonl")]
key = lambda r: (r["lag_max"], r["T"], r["kind"], r["topology"], r["replicate"])
by = defaultdict(dict)
for r in rows:
    by[key(r)][r["method"]] = r
out = {}
# 1) "identical wherever v5_1 runs": count v5_1-ok runs where candidate differs
tot = same = 0; diff_cells = defaultdict(lambda: [0, 0, 0])
for k, d in by.items():
    v, c = d["tolerant_v5_1"], d["tolerant_v5_1_hs"]
    if v["status"] != "ok":
        continue
    tot += 1
    ident = c["status"] == "ok" and abs(c["iscore_nonnull_mean"] - v["iscore_nonnull_mean"]) < 1e-12 and c["n_covered_nonnull"] == v["n_covered_nonnull"]
    same += ident
    cell = f"{k[0]}|{k[1]}|{k[2]}"
    diff_cells[cell][0] += 1; diff_cells[cell][1] += (not ident); diff_cells[cell][2] += c["hs_reduced"]
out["v51_ok_runs_total"] = tot; out["v51_ok_runs_identical"] = same
out["v51_ok_runs_nonidentical_by_cell"] = {c: {"v51_ok": a, "cand_differs": b, "cand_reduced": e} for c, (a, b, e) in sorted(diff_cells.items()) if b}
# 2) mean/median IS per primary cell; candidate vs plugin_hs_cal
P = [(2, T, k) for T in (19, 25, 30, 35) for k in ("missing", "reversed", "extra")]
cells = {}
for lag, T, kind in P:
    ks = [k for k in by if k[:3] == (lag, T, kind)]
    def col(m, f="iscore_nonnull_mean"):
        return np.array([by[k][m][f] for k in ks if by[k][m]["status"] == "ok"])
    c = col("tolerant_v5_1_hs"); h = col("plugin_hs_cal")
    # rescued only: v5_1 failed
    resc = [k for k in ks if by[k]["tolerant_v5_1"]["status"] != "ok"]
    rc = np.array([by[k]["tolerant_v5_1_hs"]["iscore_nonnull_mean"] for k in resc if by[k]["tolerant_v5_1_hs"]["status"] == "ok" and by[k]["plugin_hs_cal"]["status"] == "ok"])
    rh = np.array([by[k]["plugin_hs_cal"]["iscore_nonnull_mean"] for k in resc if by[k]["tolerant_v5_1_hs"]["status"] == "ok" and by[k]["plugin_hs_cal"]["status"] == "ok"])
    rcov_c = sum(by[k]["tolerant_v5_1_hs"]["n_covered_nonnull"] for k in resc) / max(1, sum(by[k]["tolerant_v5_1_hs"]["n_nonnull"] for k in resc))
    rcov_h = sum(by[k]["plugin_hs_cal"]["n_covered_nonnull"] for k in resc) / max(1, sum(by[k]["plugin_hs_cal"]["n_nonnull"] for k in resc))
    nred = sum(by[k]["tolerant_v5_1_hs"]["hs_reduced"] for k in ks)
    cells[f"{lag}|{T}|{kind}"] = {"n": len(ks), "cand_ok": len(c), "cand_IS_mean": float(c.mean()), "cand_IS_median": float(np.median(c)),
        "cand_IS_max": float(c.max()), "n_cand_IS_gt50": int((c > 50).sum()), "hs_cal_IS_mean": float(h.mean()), "hs_cal_IS_median": float(np.median(h)),
        "cand_le_hscal_mean": bool(c.mean() <= h.mean()), "n_reduced": int(nred),
        "rescued_n": len(resc), "rescued_cand_IS_mean": float(rc.mean()) if len(rc) else None, "rescued_hscal_IS_mean": float(rh.mean()) if len(rh) else None,
        "rescued_cand_IS_median": float(np.median(rc)) if len(rc) else None, "rescued_hscal_IS_median": float(np.median(rh)) if len(rh) else None,
        "rescued_cov_cand": rcov_c, "rescued_cov_hscal": rcov_h,
        "cand_width_median": float(np.median(col("tolerant_v5_1_hs", "width_kept"))), "hscal_width_median": float(np.median(col("plugin_hs_cal", "width_kept")))}
out["primary"] = cells
out["cells_cand_le_hscal_mean"] = sum(v["cand_le_hscal_mean"] for v in cells.values())
out["cells_T_le_25_cand_le_hscal_mean"] = sum(v["cand_le_hscal_mean"] for k, v in cells.items() if int(k.split("|")[1]) <= 25)
json.dump(out, open(ROOT / "results/ext_verify4_hubscreen/recheck.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "primary"}, indent=1))
for k, v in cells.items():
    print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items()})
