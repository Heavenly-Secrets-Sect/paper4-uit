"""Independent recomputation of baselines3 rule table (verify3_baselines3). Does not import their analyzer."""
import json, sys
from collections import defaultdict
import numpy as np
ROOT = "/Users/kietnt/Desktop/Workspace/Paper4_UIT/"
def load(p): return [json.loads(l) for l in open(ROOT+p)]
rows = load("results/ext_baselines3_eval/runs.jsonl")
tl = load("results/ext_tlp2_t80b/runs.jsonl") + load("results/ext_tlp2_t150c/runs.jsonl")
rows += [r for r in tl if r["method"] == "tlp2_db_p3"]
MODS = ["tolerant_v4", "tolerant_v5_1"]
ENV = ["pselect_union_v3", "pselect_union_v3_cal", "pselect_cal", "fullvar_cal", "targeted_lp_cal", "tlp2_db_p3", "bvar_minnesota_v2_cal"]
CELLS = [(80, 0.2), (80, 0.5), (150, 0.2), (150, 0.5)]
D = {}
cnt = defaultdict(int)
for r in rows:
    if r["kind"] != "missing": continue
    c = (r["T"], round(r["rate"], 3))
    if c not in CELLS: continue
    k = (r["method"], c, r["topology"], r["replicate"])
    if k in D: cnt["dup"] += 1
    D[k] = r
print("dups", cnt["dup"])
topos = sorted({k[2] for k in D}); reps = sorted({k[3] for k in D})
print(len(topos), reps)
B = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
ix = np.random.default_rng(20261102).integers(0, len(topos), size=(B, len(topos)))
out = {}
summ = {}
for m in MODS + ENV:
    for c in CELLS:
        g = [D.get((m, c, t, rp)) for t in topos for rp in reps]
        nn = [D[("tolerant_v4", c, t, rp)]["n_nonnull"] for t in topos for rp in reps]
        ok = [x for x in g if x and x["status"] == "ok"]
        cov = sum(x["n_covered_nonnull"] for x in ok) / sum(nn)
        IS = np.mean([x["iscore_nonnull_mean"] for x in ok])
        summ[(m, c)] = (len(ok), len(g), cov, IS)
P = {}
for m in MODS:
    for X in ENV:
        for c in CELLS:
            s = np.zeros(len(topos)); n = np.zeros(len(topos))
            for i, t in enumerate(topos):
                for rp in reps:
                    a, b = D.get((m, c, t, rp)), D.get((X, c, t, rp))
                    if a and b and a["status"] == "ok" and b["status"] == "ok":
                        s[i] += a["iscore_nonnull_mean"] - b["iscore_nonnull_mean"]; n[i] += 1
            est = s.sum() / n.sum()
            bs = s[ix].sum(1) / n[ix].sum(1)
            lo, hi = np.quantile(bs, [0.025, 0.975])
            pW = (1 + (bs >= 0).sum()) / (B + 1); pL = (1 + (bs <= 0).sum()) / (B + 1)
            P[(m, X, c)] = dict(est=est, lo=lo, hi=hi, p2=min(1, 2 * min(pW, pL)), n=int(n.sum()))
def holm(alpha):
    keys = sorted(P, key=lambda k: P[k]["p2"]); rej = set(); M = len(keys)
    for i, k in enumerate(keys):
        if P[k]["p2"] <= alpha / (M - i): rej.add(k)
        else: break
    return rej
res = {}
for a in (0.05, 0.025):
    rej = holm(a)
    for m in MODS:
        cl = {k: ("W" if P[k]["est"] < 0 else "L") if k in rej else "T" for k in P if k[0] == m}
        W = sorted(k for k, v in cl.items() if v == "W"); L = [k for k, v in cl.items() if v == "L"]
        ecell = {c: all(cl[(m, X, c)] == "W" for X in ENV) and summ[(m, c)][2] >= 0.9 for c in CELLS}
        raw = [k for k in P if k[0] == m and P[k]["hi"] < 0], [k for k in P if k[0] == m and P[k]["lo"] > 0]
        res[f"{m}|{a}"] = dict(W=len(W), T=28 - len(W) - len(L), L=len(L), losses=[f"{k[1]}|{k[2]}" for k in L],
                               ecell={str(c): v for c, v in ecell.items()}, rawW=len(raw[0]), rawL=len(raw[1]),
                               winset=[f"{k[1]}|{k[2][0]}|{k[2][1]}" for k in W])
        print(B, a, m, res[f"{m}|{a}"]["W"], res[f"{m}|{a}"]["T"], res[f"{m}|{a}"]["L"], res[f"{m}|{a}"]["losses"], res[f"{m}|{a}"]["ecell"], "raw", len(raw[0]), len(raw[1]))
# compare with their analysis.json
th = json.load(open(ROOT + "results/ext_baselines3_eval/analysis.json"))
maxd = 0
for k, v in P.items():
    tv = th["result"]["comps"][f"{k[0]}|{k[1]}|{k[2][0]}|{k[2][1]}"]
    maxd = max(maxd, abs(tv["est"] - v["est"]), abs(tv["p2"] - v["p2"]) if B == 4000 else 0)
print("max diff vs their analysis.json (est, p2 if B=4000):", maxd)
ws = json.load(open(ROOT + "experiments/ext/baselines3/p7_win_set.json"))["win_set_D07"]
if B == 4000:
    for m in MODS: print(m, "winset match:", sorted(ws[m]) == sorted(res[f"{m}|0.05"]["winset"]))
for (m, c), v in sorted(summ.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    print(c, m, "ok %d/%d cov %.3f IS %.2f" % v)
json.dump({"B": B, "verdicts": res, "comps": {f"{k[0]}|{k[1]}|{k[2][0]}|{k[2][1]}": v for k, v in P.items()},
           "cells": {f"{k[0]}|{k[1][0]}|{k[1][1]}": v for k, v in summ.items()}},
          open(ROOT + f"results/ext_verify3_baselines3/recompute_B{B}.json", "w"), indent=1, default=float)
