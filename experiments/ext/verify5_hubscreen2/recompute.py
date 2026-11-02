"""Skeptic recomputation (verify5_hubscreen2) of the r5hubscreen2 ruling numbers from runs.jsonl, written
independently of experiments/ext/r5hubscreen2/analyze.py. Also: P2c with different bootstrap seeds, a
percentile-free check, and the v2-vs-v1 range. Writes results/ext_verify5_hubscreen2/recompute.json."""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path("/Users/kietnt/Desktop/Workspace/Paper4_UIT")
R = ROOT / "results"


def load(n):
    return [json.loads(l) for l in open(R / n / "runs.jsonl")]


p2, g = load("ext_r5hubscreen2_p2"), load("ext_r5hubscreen2_g")
HS2, V51, V1, PH = "tolerant_v5_1_hs2", "tolerant_v5_1", "tolerant_v5_1_hs", "plugin_hs_cal"


def index(rows):
    d = defaultdict(dict)
    for r in rows:
        d[(r["topology"], r["replicate"], r["T"], r["kind"], float(r["rate"]))][r["method"]] = r
    return d


I2, IG = index(p2), index(g)
out = {}

# V1
hs = [r for r in p2 + g if r["method"] == HS2]
nonred = [r for r in hs if r["hs_reduced"] == 0]
out["V1"] = {"nonreduced": len(nonred),
             "identical": sum(1 for r in nonred if r["hs_status"] == r["v51_status"] and (r["hs_status"] != "ok" or r["raw_ident_v51"])),
             "lag0_dropped": sum(int(r.get("hs_contemp_dropped") or 0) for r in hs),
             "fit_fail": sum(int(r.get("hs_fit_fail") or 0) for r in hs),
             "screen_fail": sum(int(r.get("hs_screen_fail") or 0) for r in hs),
             "v51_ok": sum(1 for r in hs if r["v51_status"] == "ok"),
             "v51_ok_changed": sum(1 for r in hs if r["v51_status"] == "ok" and not r["raw_ident_v51"]),
             "g_reduced": sum(r["hs_reduced"] for r in hs if r["T"] >= 40)}

# P2a/b
cells = {}
for T in (19, 25, 30, 35):
    for k in ("missing", "reversed", "extra"):
        rows = [d[HS2] for key, d in I2.items() if key[2] == T and key[3] == k]
        ok = [r for r in rows if r["status"] == "ok"]
        itt = sum(r["n_covered_nonnull"] for r in ok) / sum(r["n_nonnull_truth"] for r in rows)
        cells[f"{T}|{k}"] = {"n": len(rows), "ok": len(ok), "itt": round(itt, 4)}
out["P2ab"] = cells


def holm(ps, a=0.05):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); rej = [False] * len(ps)
    for r, i in enumerate(o):
        if ps[i] <= a / (len(ps) - r):
            rej[i] = True
        else:
            break
    return rej


# P2c, several seeds
pc = {}
for seedoff in (0, 1, 2):
    ps, info = [], []
    for i, (T, k) in enumerate([(T, k) for T in (19, 25) for k in ("missing", "reversed", "extra")]):
        da, db = defaultdict(list), defaultdict(list)
        for key, d in I2.items():
            if key[2] != T or key[3] != k:
                continue
            h, p = d[HS2], d[PH]
            if h["v51_status"] != "ok" and h["status"] == "ok" and p["status"] == "ok":
                da[key[0]].append(h["iscore_nonnull_mean"]); db[key[0]].append(p["iscore_nonnull_mean"])
        tops = sorted(da)
        sa = np.array([sum(da[t]) for t in tops]); sb = np.array([sum(db[t]) for t in tops])
        rng = np.random.default_rng(987654 + 100 * seedoff + i)
        pk = rng.integers(0, len(tops), size=(20000, len(tops)))
        rat = sa[pk].sum(1) / sb[pk].sum(1)
        p = (1 + int((rat >= 1.10).sum())) / 20001
        ps.append(p)
        n = sum(len(v) for v in da.values())
        info.append({"cell": f"{T}|{k}", "n": n, "clusters": len(tops), "mean_hs2": round(sa.sum() / n, 3),
                     "mean_phs": round(sb.sum() / n, 3), "ratio": round(sa.sum() / sb.sum(), 4),
                     "upper95": round(float(np.quantile(rat, 0.95)), 3), "p": round(p, 5),
                     "median_hs2": round(float(np.median([v for l in da.values() for v in l])), 3),
                     "median_phs": round(float(np.median([v for l in db.values() for v in l])), 3)})
    rej = holm(ps)
    for j, x in enumerate(info):
        x["holm"] = rej[j]; x["pass"] = rej[j] and x["clusters"] >= 8
    pc[f"seedset{seedoff}"] = {"cells": info, "n_pass": sum(x["pass"] for x in info)}
out["P2c"] = pc

# G no-harm
gres = []
for T in (40, 80, 150):
    for k, r in [("none", 0.0)] + [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]:
        a, b, nrow = [], [], 0
        for key, d in IG.items():
            if key[2] != T or key[3] != k or key[4] != r:
                continue
            nrow += HS2 in d
            if d[HS2]["status"] == "ok" and d[V51]["status"] == "ok":
                a.append(d[HS2]["iscore_nonnull_mean"]); b.append(d[V51]["iscore_nonnull_mean"])
        gres.append({"cell": f"{T}|{k}|{r}", "rows": nrow, "paired": len(a), "ratio": float(np.mean(a) / np.mean(b)),
                     "identical_IS": all(x == y for x, y in zip(a, b))})
out["G"] = {"cells": len(gres), "all_rows_60": all(x["rows"] == 60 for x in gres),
            "all_ratio_1": all(x["ratio"] == 1.0 for x in gres), "all_IS_identical": all(x["identical_IS"] for x in gres)}

# v2 vs v1 and hs2 vs v5_1 (T25 missing), T19 missing v2 vs v1
vv = {}
for T in (19, 25, 30, 35):
    for k in ("missing", "reversed", "extra"):
        a, b = [], []
        for key, d in I2.items():
            if key[2] == T and key[3] == k and d[HS2]["status"] == "ok" and d[V1]["status"] == "ok":
                a.append(d[HS2]["iscore_nonnull_mean"]); b.append(d[V1]["iscore_nonnull_mean"])
        vv[f"{T}|{k}"] = {"n": len(a), "ratio": round(float(np.mean(a) / np.mean(b)), 4),
                          "max_hs2": round(max(a), 1), "max_v1": round(max(b), 1)}
out["v2_vs_v1"] = vv
a, b, tp = [], [], set()
for key, d in I2.items():
    if key[2] == 25 and key[3] == "missing" and d[HS2]["status"] == "ok" and d[V51]["status"] == "ok":
        a.append(d[HS2]["iscore_nonnull_mean"]); b.append(d[V51]["iscore_nonnull_mean"]); tp.add(key[0])
out["T25_missing_hs2_vs_v51"] = {"n": len(a), "clusters": len(tp), "ratio": round(float(np.mean(a) / np.mean(b)), 4),
                                 "diff": round(float(np.mean(a) - np.mean(b)), 3),
                                 "coverage_note": "see below"}
# coverage on T25 missing for both (does wider IS buy coverage?)
for m in (HS2, V51):
    rows = [d[m] for key, d in I2.items() if key[2] == 25 and key[3] == "missing" and d[HS2]["status"] == "ok" and d[V51]["status"] == "ok"]
    out["T25_missing_hs2_vs_v51"][f"cov_{m}"] = round(sum(r["n_covered_nonnull"] for r in rows) / sum(r["n_nonnull"] for r in rows), 4)
    out["T25_missing_hs2_vs_v51"][f"width_{m}"] = round(float(np.mean([r["width_kept"] for r in rows])), 3)
(R / "ext_verify5_hubscreen2" / "recompute.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
