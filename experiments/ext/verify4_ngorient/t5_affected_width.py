"""Verifier: interval width of NG-A vs v5_1 on affected pairs (dC >= 0.05) and on all non-null pairs, v2 ng_mix
reversed cells; checks the claim 'narrows the affected coverage gap without widening intervals'."""
import sys, json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
z = np.load(ROOT / "results/ext_r4ngorient_v2_ngmix/pairs.npz")
meth = [str(m) for m in z["methods"]]; cells = [str(c) for c in z["cells"]]
A, V = meth.index("tolerant_ngA"), meth.index("tolerant_v5_1")
out = {}
for T in (80, 150):
    for cn in ("reversed|0.2", "reversed|0.5"):
        c = cells.index(cn)
        res = {}
        for lab, mk in (("A", A), ("V", V)):
            s = (z["T"] == T) & (z["cell"] == c) & (z["method"] == mk)
            key = np.stack([z["topo"][s], z["rep"][s], z["j"][s], z["i"][s]], 1)
            o = np.lexsort(key.T[::-1]); res[lab] = {k: z[k][s][o] for k in ("lo", "hi", "C_t", "dC", "topo")}
        aff = res["V"]["dC"] >= 0.05
        wA = res["A"]["hi"] - res["A"]["lo"]; wV = res["V"]["hi"] - res["V"]["lo"]
        covA = (res["A"]["lo"] <= res["A"]["C_t"]) & (res["A"]["C_t"] <= res["A"]["hi"])
        covV = (res["V"]["lo"] <= res["V"]["C_t"]) & (res["V"]["C_t"] <= res["V"]["hi"])
        tops = np.unique(res["V"]["topo"][aff]); rng = np.random.default_rng(5)
        tw = np.array([[wA[aff & (res["V"]["topo"] == t)].sum(), wV[aff & (res["V"]["topo"] == t)].sum()] for t in tops])
        reps = []
        for _ in range(5000):
            b = rng.integers(0, len(tops), len(tops)); reps.append(tw[b, 0].sum() / tw[b, 1].sum())
        out[f"T{T}|{cn}"] = {"n_aff": int(aff.sum()), "cov_aff_V": float(covV[aff].mean()), "cov_aff_A": float(covA[aff].mean()),
                            "mean_width_aff_ratio_A_over_V": float(wA[aff].mean() / wV[aff].mean()),
                            "ratio_CI": [float(np.quantile(reps, .025)), float(np.quantile(reps, .975))],
                            "median_width_aff_V_A": [float(np.median(wV[aff])), float(np.median(wA[aff]))],
                            "share_aff_pairs_wider_A": float(np.mean(wA[aff] > wV[aff] + 1e-12)),
                            "mean_width_all_ratio": float(wA.mean() / wV.mean())}
        print(f"T{T}|{cn}", out[f"T{T}|{cn}"])
(ROOT / "results/ext_verify4_ngorient/t5_affected_width.json").write_text(json.dumps(out, indent=1))
