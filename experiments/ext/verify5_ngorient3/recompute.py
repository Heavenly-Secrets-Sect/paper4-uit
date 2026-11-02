"""Skeptic: independent recomputation of P1 endpoint, per-cell dIS, Holm, factor equality, v3-v2 from runs.jsonl."""
import json, collections
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
def load(n):
    return [json.loads(l) for l in open(ROOT/f"results/ext_r5ngorient3_{n}/runs.jsonl")]
out = {}
rng = np.random.default_rng(424242); B = 20000
def holm(ps):
    o = np.argsort(ps); k = len(ps); adj = np.empty(k); run = 0
    for i, j in enumerate(o):
        run = max(run, min(1, (k-i)*ps[j])); adj[j] = run
    return adj.tolist()
for shock in ("ngmix", "gauss"):
    R = load(shock)
    idx = collections.defaultdict(dict)
    for r in R:
        idx[(r["T"], r["kind"], r["rate"], r["topology"], r["replicate"])][r["method"]] = r
    # factor equality
    neq = tot = 0
    for k, d in idx.items():
        if "tolerant_v5_1" in d and "tolerant_ngA3" in d and d["tolerant_v5_1"]["status"] == "ok":
            tot += 1; neq += d["tolerant_v5_1"].get("info_c_T") != d["tolerant_ngA3"].get("info_c_T")
    out[f"{shock}_factor_neq"] = [neq, tot]
    cells = sorted({(k[0], k[1], k[2]) for k in idx})
    topos = sorted({k[3] for k in idx})
    ti = {t: i for i, t in enumerate(topos)}
    res = {}
    for c in cells:
        rows = [(k[3], d) for k, d in idx.items() if k[:3] == c]
        def arr(m):
            S = np.zeros(len(topos)); N = np.zeros(len(topos))
            for t, d in rows:
                if d["tolerant_v5_1"]["status"] == "ok" and d[m]["status"] == "ok" and d["tolerant_ngA"]["status"] == "ok":
                    S[ti[t]] += d[m]["iscore_nonnull_mean"]; N[ti[t]] += 1
            return S, N
        sref, n = arr("tolerant_v5_1"); s3, _ = arr("tolerant_ngA3"); s2, _ = arr("tolerant_ngA")
        cov = sum(d["tolerant_ngA3"]["n_covered_nonnull"] for t, d in rows) / sum(d["tolerant_ngA3"]["n_nonnull"] for t, d in rows)
        res[c] = dict(sref=sref, s3=s3, s2=s2, n=n, cov3=cov, ncl=int((n > 0).sum()))
    W = rng.multinomial(len(topos), np.ones(len(topos))/len(topos), size=B)  # cluster counts
    def stats(c, arm):
        d = res[c]; num = (d[arm] - d["sref"]); 
        rat = (W @ num) / (W @ d["sref"])
        dis = (W @ num) / (W @ d["n"])
        return num.sum()/d["sref"].sum(), rat, num.sum()/d["n"].sum(), dis
    if shock == "ngmix":
        prim = [c for c in cells if c[0] in (80, 150) and c[1] in ("missing", "reversed")]
        E3 = np.mean([stats(c, "s3")[0] for c in prim]); E3b = np.mean([stats(c, "s3")[1] for c in prim], axis=0)
        E2 = np.mean([stats(c, "s2")[0] for c in prim]); E2b = np.mean([stats(c, "s2")[1] for c in prim], axis=0)
        # v3 - v2 relative to v5_1
        out["E3"] = [E3, *np.percentile(E3b, [2.5, 97.5]), float(np.quantile(E3b, .95)), float((E3b >= 0).mean())]
        out["E2"] = [E2, *np.percentile(E2b, [2.5, 97.5]), float(np.quantile(E2b, .95))]
        D = E3b - E2b
        out["E3_minus_E2"] = [E3 - E2, *np.percentile(D, [2.5, 97.5])]
        ps = []; tab = []
        for c in prim:
            _, _, dis, disb = stats(c, "s3"); p = max(float((disb >= 0).mean()), 1/B); ps.append(p)
            tab.append([c, round(dis, 4), np.round(np.percentile(disb, [2.5, 97.5]), 4).tolist(), p, round(res[c]["cov3"], 3), res[c]["ncl"]])
        for row, h in zip(tab, holm(ps)): row.append(h)
        out["P1_cells"] = [[str(x) for x in r] for r in tab]
        nonprim = [c for c in cells if c not in prim]
        out["nh_b_max_ratio"] = max(1 + stats(c, "s3")[0] for c in nonprim)
        c = (40, "reversed", 0.5); _, _, dis, disb = stats(c, "s3")
        out["T40rev05"] = [dis, *np.percentile(disb, [2.5, 97.5])]
    else:
        rat = [1 + stats(c, "s3")[0] for c in cells]
        ps = [max(float((stats(c, "s3")[3] <= 0).mean()), 1/B) for c in cells]
        out["gauss_ratio_range"] = [min(rat), max(rat)]; out["gauss_holm_min"] = min(holm(ps))
        out["gauss_cov3_min"] = min(res[c]["cov3"] for c in cells)
Path(ROOT/"results/ext_verify5_ngorient3/recompute.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps(out, indent=1, default=str))
