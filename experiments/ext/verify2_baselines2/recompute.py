"""Skeptic re-computation (verify2_baselines2) of results/ext_baselines2_eval numbers, independent code.
Bootstrap: own rng (seed 7), B=4000, cluster by topology; also t-based CI as robustness."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy import stats
ROOT = Path(__file__).resolve().parents[3]
R = ROOT / "results/ext_baselines2_eval"
OUT = ROOT / "results/ext_verify2_baselines2"
rows = [json.loads(l) for l in open(R / "runs.jsonl")]
from collections import Counter
out = {"n_rows": len(rows), "status": dict(Counter(r["status"] for r in rows)),
       "methods": dict(Counter(r["method"] for r in rows))}
ok = [r for r in rows if r["status"] == "ok"]
key = lambda r: (r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])
by = defaultdict(dict)
for r in ok: by[r["method"]][key(r)] = r
rng = np.random.default_rng(7)
B = 4000
def boot(per):
    tp = sorted(per); s = np.array([sum(per[t]) for t in tp]); n = np.array([len(per[t]) for t in tp])
    ix = rng.integers(0, len(tp), (B, len(tp)))
    bs = s[ix].sum(1) / n[ix].sum(1)
    tm = np.array([np.mean(per[t]) for t in tp])
    se = tm.std(ddof=1) / np.sqrt(len(tp))
    return float(s.sum() / n.sum()), *map(float, np.quantile(bs, [.025, .975])), (1 + int((bs >= 0).sum())) / (B + 1), \
        float(tm.mean() - stats.t.ppf(.975, len(tp) - 1) * se), float(tm.mean() + stats.t.ppf(.975, len(tp) - 1) * se), len(tp)
res = {}
for X in ["pselect_union_v2", "pselect_union_v2_cal", "bvar_minnesota_v2", "bvar_minnesota_v2_cal"]:
    for T in (80, 150):
        for rate in (0.2, 0.5):
            k4 = [k for k in by["tolerant_v4"] if k[2:] == (T, "missing", rate)]
            cov4 = sum(by["tolerant_v4"][k]["n_covered_nonnull"] for k in k4) / sum(by["tolerant_v4"][k]["n_nonnull"] for k in k4)
            kx = [k for k in by[X] if k[2:] == (T, "missing", rate)]
            covx = sum(by[X][k]["n_covered_nonnull"] for k in kx) / sum(by[X][k]["n_nonnull"] for k in kx)
            per = defaultdict(list)
            for k in k4:
                if k in by[X]:
                    per[k[0]].append(by["tolerant_v4"][k]["iscore_nonnull_mean"] - by[X][k]["iscore_nonnull_mean"])
            est, lo, hi, p, tlo, thi, nt = boot(per)
            res[f"{X}|{T}|{rate}"] = dict(cov_v4=cov4, cov_X=covx, IS_v4=float(np.mean([by['tolerant_v4'][k]['iscore_nonnull_mean'] for k in k4])),
                                          IS_X=float(np.mean([by[X][k]['iscore_nonnull_mean'] for k in kx])), est=est, lo=lo, hi=hi, p=p,
                                          t_lo=tlo, t_hi=thi, n_pairs=sum(len(v) for v in per.values()), n_topo=nt)
out["rule_cells"] = res
def holm(p, a):
    o = sorted(p, key=p.get); rej = {k: False for k in p}
    for i, k in enumerate(o):
        if p[k] <= a / (len(o) - i): rej[k] = True
        else: break
    return rej
for fam, Xs in (("primary", ["pselect_union_v2", "pselect_union_v2_cal"]), ("secondary", ["bvar_minnesota_v2", "bvar_minnesota_v2_cal"])):
    p = {k: v["p"] for k, v in res.items() if k.split("|")[0] in Xs}
    h = holm(p, .025)
    out[fam] = {"ci_pass": {k: res[k]["hi"] < 0 and res[k]["cov_v4"] >= .9 for k in p}, "holm_pass": h,
                "t_ci_pass": {k: res[k]["t_hi"] < 0 for k in p}}
# v4 regression vs a2b_pselect
a2b = {key(r): r for r in map(json.loads, open(ROOT / "results/a2b_pselect/runs.jsonl")) if r["method"] == "tolerant_v4"}
mm = 0; fields = ["iscore_nonnull_mean", "n_covered_nonnull", "iscore_null_mean", "width_kept", "C_abs_err_nonnull"]
for r in rows:
    if r["method"] != "tolerant_v4": continue
    a = a2b.get(key(r))
    if a is None or a["status"] != r["status"] or any(a.get(f) != r.get(f) for f in fields if f in a): mm += 1
out["v4_regression"] = {"n": sum(r["method"] == "tolerant_v4" for r in rows), "mismatch": mm}
# null IS
nul = {}
for m in ["tolerant_v4", "pselect_union_v2"]:
    for T in (80, 150):
        for rate in (0.2, 0.5):
            nul[f"{m}|{T}|{rate}"] = float(np.mean([r["iscore_null_mean"] for k, r in by[m].items() if k[2:] == (T, "missing", rate)]))
out["null_IS"] = nul
json.dump(out, open(OUT / "recompute.json", "w"), indent=1, default=str)
for k, v in res.items():
    print(k, f"cov4 {v['cov_v4']:.3f} covX {v['cov_X']:.3f} IS {v['IS_v4']:.2f}/{v['IS_X']:.2f} d {v['est']:+.2f} [{v['lo']:+.2f},{v['hi']:+.2f}] p {v['p']:.4f} t[{v['t_lo']:+.2f},{v['t_hi']:+.2f}] n {v['n_pairs']}")
print(out["status"], out["methods"], out["v4_regression"], nul)
print({f: sum(out[f]["holm_pass"].values()) for f in ("primary", "secondary")}, {f: sum(out[f]["ci_pass"].values()) for f in ("primary", "secondary")})
