"""Numbers for the R2-10 corrections appended to docs/ext/eiv.md (round-1 results, no new runs):
coverage of tolerant_eiv / tolerant_v4 at noise0.1, paired IS differences eiv - v4 (95% CI
clustered by topology, B = 2000, seed 0), and null-pair |C| (C_abs_spurious, median and mean over
runs) for v4 and eiv in every cell of results/ext_eiv_a1noise/runs.jsonl.
Usage: python experiments/ext/eiv2/r1_corrections.py > results/ext_eiv2_r1fix/corrections.txt"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
rows = [json.loads(line) for line in open(ROOT / "results/ext_eiv_a1noise/runs.jsonl")]
g = defaultdict(list)
for r in rows:
    if r["status"] == "ok":
        g[(r["scenario"], r["T"], r["kind"], r["method"])].append(r)
cells = [(T, k) for T in (80, 150) for k in ("none", "missing", "reversed")]


def cov(rs):
    return sum(r["n_covered_nonnull"] for r in rs) / sum(r["n_nonnull"] for r in rs)


def paired(sc, T, k, a, b, B=2000):
    idx = {(r["topology"], r["replicate"]): r["iscore_nonnull_mean"] for r in g[(sc, T, k, b)]}
    d = defaultdict(list)
    for r in g[(sc, T, k, a)]:
        key = (r["topology"], r["replicate"])
        if key in idx:
            d[r["topology"]].append(r["iscore_nonnull_mean"] - idx[key])
    topos = list(d)
    est = np.mean([v for t in topos for v in d[t]])
    rng = np.random.default_rng(0)
    bs = [np.mean([v for i in rng.choice(len(topos), len(topos)) for v in d[topos[i]]]) for _ in range(B)]
    lo, hi = np.quantile(bs, (0.025, 0.975))
    return est, lo, hi


print("# Round-1 numbers recomputed from results/ext_eiv_a1noise/runs.jsonl (eiv2 agent, round 2)\n")
print("## noise0.1: coverage (eiv / v4) and paired IS eiv - v4 [95% CI clustered by topology]\n")
for T, k in cells:
    e, v = cov(g[("noise0.1", T, k, "tolerant_eiv")]), cov(g[("noise0.1", T, k, "tolerant_v4")])
    est, lo, hi = paired("noise0.1", T, k, "tolerant_eiv", "tolerant_v4")
    print(f"T={T} {k}: cov eiv {e:.3f} v4 {v:.3f} | dIS {est:+.2f} [{lo:+.2f}, {hi:+.2f}]")
c = [cov(g[("noise0.1", T, k, "tolerant_eiv")]) for T, k in cells]
cv = [cov(g[("noise0.1", T, k, "tolerant_v4")]) for T, k in cells]
print(f"min coverage eiv at noise0.1: {min(c):.4f}; v4 cells >= 0.90 at noise0.1: {sum(x >= 0.90 for x in cv)}/6\n")
print("## Null pairs: C_abs_spurious median over runs (mean in brackets), v4 -> eiv\n")
for sc in ("clean", "noise0.1", "noise0.3"):
    for T, k in cells:
        s = []
        for m in ("tolerant_v4", "tolerant_eiv"):
            v = [r["C_abs_spurious"] for r in g[(sc, T, k, m)] if r.get("C_abs_spurious") is not None]
            s.append(f"{np.median(v):.3f} ({np.mean(v):.3f})")
        print(f"{sc} T={T} {k}: v4 {s[0]} -> eiv {s[1]}")
