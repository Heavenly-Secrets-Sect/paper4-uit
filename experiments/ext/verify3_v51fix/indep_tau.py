import json
from collections import defaultdict
from pathlib import Path
import numpy as np
R = Path(__file__).resolve().parents[3] / "results"
def load(run): return [json.loads(l) for l in open(R / run / "runs.jsonl")]
def key(r): return (r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])
ev = load("ext_v51_eval"); ta = load("ext_v51fix_t150tau")
I = defaultdict(dict)
for r in ev:
    if r["T"] == 150: I[r["method"]][key(r)] = r
J = defaultdict(dict)
for r in ta: J[r["method"]][key(r)] = r
print({m: len(v) for m, v in J.items()}, "status", {s for r in ta for s in [r["status"]]})
same = sum(1 for k, r in J["tolerant_v4"].items() if abs(r["iscore_nonnull_mean"] - I["tolerant_v4"][k]["iscore_nonnull_mean"]) < 1e-12 and r["n_covered_nonnull"] == I["tolerant_v4"][k]["n_covered_nonnull"])
print("v4 identical", same, len(J["tolerant_v4"]))
t = J["tolerant_v5_1_t294"]
miss = [r for r in t.values() if r["kind"] == "missing"]
print("allag share missing", sum(r["info_v51_targeted"] == 0 for r in miss), len(miss), "targeted nonmissing", sum(r["info_v51_targeted"] for r in t.values() if r["kind"] != "missing"))
res = {}
def holm(p, a=0.025):
    o = np.argsort(p); m = len(p); rej = [False]*m
    for i, j in enumerate(o):
        if p[j] <= a/(m-i): rej[j] = True
        else: break
    return rej
CELLS = [("none", 0.0)] + [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]
for ref, refidx in (("v5_1", I["tolerant_v5_1"]), ("v4", J["tolerant_v4"])):
    pg, pl, rows = [], [], []
    for kd, rt in CELLS:
        d = defaultdict(list)
        for k, r in t.items():
            if k[3] == kd and k[4] == rt: d[k[0]].append(r["iscore_nonnull_mean"] - refidx[k]["iscore_nonnull_mean"])
        tp = sorted(d); s = np.array([sum(d[x]) for x in tp]); n = np.array([len(d[x]) for x in tp])
        pk = np.random.default_rng(7).integers(0, len(tp), (20000, len(tp))); b = s[pk].sum(1)/n[pk].sum(1)
        g = [r for r in t.values() if r["kind"] == kd and r["rate"] == rt]
        cov = sum(r["n_covered_nonnull"] for r in g)/sum(r["n_nonnull"] for r in g)
        ist = np.mean([r["iscore_nonnull_mean"] for r in g]); isv4 = np.mean([J["tolerant_v4"][key(r)]["iscore_nonnull_mean"] for r in g])
        lo, hi = np.quantile(b, (.025, .975))
        pg.append((1+(b <= 0).sum())/20001); pl.append((1+(b >= 0).sum())/20001)
        rows.append([kd, rt, round(s.sum()/n.sum(), 4), round(lo, 4), round(hi, 4), round(cov, 3), round(ist/isv4, 3)])
    hg, hl = holm(pg), holm(pl)
    for row, a, b2 in zip(rows, hg, hl): row += [a, b2]
    res[ref] = rows
    print("t294 -", ref); [print("  ", r) for r in rows]
(R / "ext_verify3_v51fix" / "indep_tau.json").write_text(json.dumps(res, indent=1, default=str))
