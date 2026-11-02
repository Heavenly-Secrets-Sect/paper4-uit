"""Verifier: independent recomputation of the registered v2 (and v1) rule from runs.jsonl, own code.
Topology-cluster bootstrap (own implementation), several seeds, plus a topology-level t test for robustness."""
import sys, json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats
ROOT = Path(__file__).resolve().parents[3]

def load(name):
    d = {}
    for l in open(ROOT / f"results/{name}/runs.jsonl"):
        r = json.loads(l); d[(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"], r["method"])] = r
    return d

def holm(p):
    p = np.asarray(p); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for i, k in enumerate(o):
        run = max(run, (m - i) * p[k]); adj[k] = min(1, run)
    return adj

def comp(d, arm, ref, T, kind, rate, seed, B=20000):
    per = defaultdict(list); cov = {arm: [0, 0], ref: [0, 0]}; ia = []; ir = []; fail = {arm: 0, ref: 0}
    for k, r in d.items():
        if k[2] == T and k[3] == kind and k[4] == rate and k[5] == ref:
            a = d.get(k[:5] + (arm,))
            for m_, x in ((arm, a), (ref, r)):
                if x is None or x["status"] != "ok": fail[m_] += 1
                else: cov[m_][0] += x["n_covered_nonnull"]; cov[m_][1] += x["n_nonnull"]
            if a and a["status"] == "ok" and r["status"] == "ok":
                per[k[0]].append(a["iscore_nonnull_mean"] - r["iscore_nonnull_mean"])
                ia.append(a["iscore_nonnull_mean"]); ir.append(r["iscore_nonnull_mean"])
    tops = sorted(per); s = np.array([sum(per[t]) for t in tops]); n = np.array([len(per[t]) for t in tops])
    rng = np.random.default_rng(seed)
    W = np.stack([np.bincount(rng.integers(0, len(tops), len(tops)), minlength=len(tops)) for _ in range(B)])
    reps = (W @ s) / (W @ n); est = s.sum() / n.sum()
    tm = s / n
    t_p_better = stats.ttest_1samp(tm, 0, alternative="less").pvalue
    t_p_worse = stats.ttest_1samp(tm, 0, alternative="greater").pvalue
    return {"T": T, "cell": f"{kind}-{rate}", "d": est, "ci": [np.quantile(reps, .025), np.quantile(reps, .975)],
            "p_better": max(np.mean(reps >= 0), 1 / B), "p_worse": max(np.mean(reps <= 0), 1 / B),
            "t_better": t_p_better, "t_worse": t_p_worse, "ratio": np.mean(ia) / np.mean(ir),
            "cov_arm": cov[arm][0] / cov[arm][1], "cov_ref": cov[ref][0] / cov[ref][1], "fail": (fail[arm], fail[ref])}

CELLS = [("none", 0.0), ("extra", 0.2), ("extra", 0.5), ("missing", 0.2), ("missing", 0.5), ("reversed", 0.2), ("reversed", 0.5)]
PRIM = [(T, k, r) for T in (80, 150) for k in ("missing", "reversed") for r in (0.2, 0.5)]
out = {}
for ver, pfx in (("v1", "ext_r4ngorient_"), ("v2", "ext_r4ngorient_v2_")):
    ng, ga = load(pfx + "ngmix"), load(pfx + "gauss")
    for arm in ("tolerant_ngA", "tolerant_ngB"):
        for seed in (20261104, 1, 2):
            prim = [comp(ng, arm, "tolerant_v5_1", *c, seed) for c in PRIM]
            hb = holm([c["p_better"] for c in prim]); ht = holm([c["t_better"] for c in prim])
            wins = [c["T"] and c["cell"] for c, p in zip(prim, hb) if p < .05 and c["cov_arm"] >= .9 and c["fail"][0] <= c["fail"][1] + 1]
            twins = [c["cell"] + f"@{c['T']}" for c, p in zip(prim, ht) if p < .05]
            gauss = [comp(ga, arm, "tolerant_v5_1", T, k, r, seed) for T in (40, 80, 150) for k, r in CELLS]
            hw = holm([c["p_worse"] for c in gauss])
            nha = all(c["ratio"] <= 1.03 for c in gauss) and all(p >= .05 for p in hw)
            nha_bad = [(c["T"], c["cell"], round(c["ratio"], 4)) for c, p in zip(gauss, hw) if c["ratio"] > 1.03 or p < .05]
            nonprim = [(40, k, r) for k, r in CELLS] + [(T, k, r) for T in (80, 150) for k, r in CELLS[:3]]
            nb = [comp(ng, arm, "tolerant_v5_1", *c, seed) for c in nonprim]
            nhb_bad = [(c["T"], c["cell"]) for c in nb if c["ratio"] > 1.05 or (c["cov_ref"] >= .9 and c["cov_arm"] < .9)]
            key = f"{ver}|{arm}|seed{seed}"
            out[key] = {"WIN": len(wins), "wins": wins, "holm_p": [round(float(p), 4) for p in hb],
                        "d": [round(c["d"], 4) for c in prim], "t_test_holm_wins": twins,
                        "cov_min_primary": round(min(c["cov_arm"] for c in prim), 4),
                        "noharm_a": nha, "noharm_a_bad": nha_bad, "n_gauss_cells": len(gauss),
                        "noharm_b_bad": nhb_bad, "n_nonprim_cells": len(nb),
                        "v5_1_cov_range_ngmix": [round(min(c["cov_ref"] for c in prim + nb), 3), round(max(c["cov_ref"] for c in prim + nb), 3)]}
            print(key, json.dumps(out[key]))
(ROOT / "results/ext_verify4_ngorient/t4_recompute.json").write_text(json.dumps(out, indent=1, default=float))
