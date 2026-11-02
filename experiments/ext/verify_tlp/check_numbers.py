"""Skeptic re-computation of ext_tlp_eval numbers (independent of experiments/ext/tlp/score.py)."""
import json, sys
from collections import defaultdict, Counter
import numpy as np
R = "/Users/kietnt/Desktop/Workspace/Paper4_UIT/results"
rows = [json.loads(l) for l in open(f"{R}/ext_tlp_eval/runs.jsonl")]
print("rows", len(rows), Counter(r["method"] for r in rows))
print("status", Counter((r["method"], r["status"]) for r in rows if r["status"] != "ok"))
cells = sorted({(r["T"], r["kind"], r["rate"]) for r in rows})
by = defaultdict(dict)
for r in rows:
    by[(r["T"], r["kind"], r["rate"])][(r["topology"], r["replicate"], r["method"])] = r
def cov(c, m):
    g = [r for k, r in by[c].items() if k[2] == m and r["status"] == "ok"]
    return sum(r["n_covered_nonnull"] for r in g) / sum(r["n_nonnull"] for r in g), len(g)
def mean(c, m, key):
    return np.mean([r[key] for k, r in by[c].items() if k[2] == m and r["status"] == "ok" and r.get(key) is not None])
def paired(c, a, b, B=2000, seed=12345):
    d = defaultdict(list)
    for (t, rep, m), r in by[c].items():
        if m == a and (t, rep, b) in by[c] and r["status"] == "ok" and by[c][(t, rep, b)]["status"] == "ok":
            d[t].append(r["iscore_nonnull_mean"] - by[c][(t, rep, b)]["iscore_nonnull_mean"])
    ts = list(d); rng = np.random.default_rng(seed)
    est = np.mean([v for t in ts for v in d[t]])
    bs = [np.mean([v for i in rng.choice(len(ts), len(ts)) for v in d[ts[i]]]) for _ in range(B)]
    return est, *np.quantile(bs, [.025, .975]), sum(map(len, d.values()))
w1 = w2 = 0
for c in cells:
    cv, n = cov(c, "tolerant_v4"); ct, _ = cov(c, "targeted_lp"); cc, _ = cov(c, "targeted_lp_cal")
    p = paired(c, "tolerant_v4", "targeted_lp"); q = paired(c, "tolerant_v4", "targeted_lp_cal")
    v1 = "v4" if cv >= .9 and p[2] < 0 else ("TLP" if ct >= .9 and p[1] > 0 else "tie")
    v2 = "v4" if cv >= .9 and q[2] < 0 else ("CAL" if cc >= .9 and q[1] > 0 else "tie")
    print(c, f"v4 {cv:.3f}/{mean(c,'tolerant_v4','iscore_nonnull_mean'):.2f} w{mean(c,'tolerant_v4','width_kept'):.2f} | "
          f"tlp {ct:.3f}/{mean(c,'targeted_lp','iscore_nonnull_mean'):.2f} w{mean(c,'targeted_lp','width_kept'):.2f} | "
          f"cal {cc:.3f}/{mean(c,'targeted_lp_cal','iscore_nonnull_mean'):.2f} w{mean(c,'targeted_lp_cal','width_kept'):.2f} | "
          f"d1 {p[0]:+.2f}[{p[1]:+.2f},{p[2]:+.2f}] n{p[3]} {v1} | d2 {q[0]:+.2f}[{q[1]:+.2f},{q[2]:+.2f}] {v2} | "
          f"psel {cov(c,'pselect_union')[0]:.3f}/{mean(c,'pselect_union','iscore_nonnull_mean'):.2f} | "
          f"lost tlp {sum(r.get('n_lost',0) for k,r in by[c].items() if k[2]=='targeted_lp')}/{sum(r.get('n_nonnull',0) for k,r in by[c].items() if k[2]=='targeted_lp')} "
          f"v4 {sum(r.get('n_lost',0) for k,r in by[c].items() if k[2]=='tolerant_v4')} | vmean {mean(c,'targeted_lp','info_v_mean'):.3f}")
    if c[1] != "none":
        w1 += v1 == "v4"; w2 += v2 == "v4"
print("v4 wins R1", w1, "R2", w2)
# pairing with a2b_pselect
ref = {}
for l in open(f"{R}/a2b_pselect/runs.jsonl"):
    r = json.loads(l); ref[(r["method"], r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])] = r.get("iscore_nonnull_mean")
match = tot = 0
for r in rows:
    k = (r["method"], r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])
    if k in ref:
        tot += 1; match += (ref[k] == r.get("iscore_nonnull_mean")) or (ref[k] is None and r.get("iscore_nonnull_mean") is None)
print("pairing with a2b_pselect", match, "/", tot, Counter(k[0] for k in ref))
shr = Counter((r["T"], r.get("info_var_shrunk")) for r in rows if r["method"] == "targeted_lp")
print("shrunk", shr)
print("p_lp", Counter((r["T"], r.get("info_p_lp")) for r in rows if r["method"] == "targeted_lp"))
print("infeasible shocks", Counter((r["T"], r.get("info_n_shock_lp_infeasible")) for r in rows if r["method"] == "targeted_lp"))
