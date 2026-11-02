"""Descriptive report of results/ext_eiv2_hetero (pre-registered in docs/ext/eiv2.md, no verdict):
coverage / IS of tolerant_eiv2, tolerant_eiv, tolerant_v4, plugin under noise0.3, het0.1, het0.3;
cap-fix effect tolerant_eiv2 - tolerant_eiv at noise0.3 (paired IS and coverage difference, cluster
bootstrap by topology, B = 2000, default_rng(0), Holm across 6 cells); r_hat vs true mean share;
bit-for-bit check of the noise0.3 rows shared with results/ext_eiv2_eval.
Usage: python experiments/ext/eiv2/describe_hetero.py > results/ext_eiv2_hetero/describe.txt"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from check_rule_lib import B, boot, by_topo, cov, holm, iscore, ok, paired_rows  # noqa: E402

rows = [json.loads(line) for line in open(ROOT / "results/ext_eiv2_hetero/runs.jsonl")]
g = defaultdict(list)
for r in rows:
    g[(r["scenario"], r["T"], r["kind"], r["method"])].append(r)
CELLS = [(T, k) for T in (80, 150) for k in ("none", "missing", "reversed")]
SCEN = ("noise0.3", "het0.3")
M = ["plugin", "tolerant_v4", "tolerant_eiv", "tolerant_eiv2"]
# mean true share of the heterogeneous scenarios: ratios evenly spaced on [0, 2r] over n = 14 series
SHARE = {"noise0.3": 0.3 / 1.3}
for sc, r in (("het0.1", 0.1), ("het0.3", 0.3)):
    rs = np.linspace(0, 2 * r, 14)
    SHARE[sc] = float(np.mean(rs / (1 + rs)))

print("# ext_eiv2_hetero: descriptive report (docs/ext/eiv2.md)\n")
print("## Coverage / IS per cell\n")
print("| scenario | T | cell | " + " | ".join(M) + " |")
print("|---|---|---|" + "---|" * len(M))
for sc in SCEN:
    for T, k in CELLS:
        print(f"| {sc} | {T} | {k} | " + " | ".join(f"{cov(g[(sc, T, k, m)]):.3f} / {iscore(g[(sc, T, k, m)]):.2f}" for m in M) + " |")
print("\nok runs per method: " + ", ".join(
    f"{m} {sum(r['status'] == 'ok' for r in rows if r['method'] == m)}/{sum(r['method'] == m for r in rows)}" for m in M))
for m in M[1:]:
    n = sum(cov(g[(sc, T, k, m)]) >= 0.90 for sc in ("het0.3",) for T, k in CELLS)
    print(f"{m}: cells with coverage >= 0.90 in het0.3: {n}/6")

for a, b in (("tolerant_eiv2", "tolerant_eiv"), ("tolerant_eiv2", "tolerant_v4")):
    print(f"\n## Paired IS {a} - {b} (95% CI clustered by topology; * = Holm across the 6 cells of the scenario)\n")
    for sc in SCEN:
        res = [paired_rows(g[(sc, T, k, a)], g[(sc, T, k, b)]) for T, k in CELLS]
        rej = holm(np.array([x[3] for x in res]))
        print(f"  {sc}: " + "; ".join(f"T{T} {k} {e:+.2f} [{lo:+.2f}, {hi:+.2f}]{'*' if h else ''}"
                                      for (T, k), (e, lo, hi, _), h in zip(CELLS, res, rej)))

print("\n## Coverage difference tolerant_eiv2 - tolerant_eiv at noise0.3 (95% CI clustered by topology)\n")
pv = []
out = []
for T, k in CELLS:
    a, b = by_topo(g[("noise0.3", T, k, "tolerant_eiv2")]), by_topo(g[("noise0.3", T, k, "tolerant_eiv")])
    d = cov(g[("noise0.3", T, k, "tolerant_eiv2")]) - cov(g[("noise0.3", T, k, "tolerant_eiv")])
    bs = boot(lambda x, y: cov(x) - cov(y), [a, b])
    lo, hi = np.quantile(bs, (0.025, 0.975))
    pv.append(min(1.0, 2 * min((bs <= 0).mean(), (bs >= 0).mean())))
    out.append((T, k, d, lo, hi))
rej = holm(np.array(pv))
for (T, k, d, lo, hi), p, h in zip(out, pv, rej):
    print(f"  T={T} {k}: {d:+.3f} [{lo:+.3f}, {hi:+.3f}] p={p:.4f}{' *Holm' if h else ''}")

print("\n## r_hat (all cells pooled): mean (sd) vs true mean share\n")
for m in ("tolerant_eiv", "tolerant_eiv2"):
    for sc in SCEN:
        for T in (80, 150):
            v = np.array([r["info_r_hat"] for (s, t, k, mm), rs in g.items() if s == sc and t == T and mm == m for r in ok(rs)])
            print(f"  {m} {sc} T={T}: {v.mean():.3f} ({v.std():.3f}); true mean share {SHARE[sc]:.3f}")

print("\n## Null pairs: median C_abs_spurious, tolerant_v4 / tolerant_eiv / tolerant_eiv2\n")
for sc in SCEN:
    for T, k in CELLS:
        s = [f"{np.median([r['C_abs_spurious'] for r in ok(g[(sc, T, k, m)]) if r.get('C_abs_spurious') is not None]):.3f}"
             for m in ("tolerant_v4", "tolerant_eiv", "tolerant_eiv2")]
        print(f"  {sc} T={T} {k}: " + " / ".join(s))

print("\n## Reproducibility: noise0.3 rows shared with results/ext_eiv2_eval\n")
ev = ROOT / "results/ext_eiv2_eval/runs.jsonl"
if ev.exists():
    key = lambda r: (r["topology"], r["replicate"], r["T"], r["kind"], r["method"])  # noqa: E731
    e = {key(r): r for r in map(json.loads, open(ev)) if r["scenario"] == "noise0.3"}
    same = diff = 0
    for r in rows:
        if r["scenario"] == "noise0.3" and key(r) in e:
            a, b = e[key(r)], r
            fields = ("status", "n_covered_nonnull", "iscore_nonnull_mean", "C_abs_err_nonnull")
            if all(a.get(f) == b.get(f) for f in fields):
                same += 1
            else:
                diff += 1
    print(f"  rows identical: {same}, rows different: {diff}")
else:
    print("  results/ext_eiv2_eval/runs.jsonl not found")
print(f"\n(B = {B})")
