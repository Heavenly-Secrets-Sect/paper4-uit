"""Apply the pre-registered rule of docs/ext/eiv.md to results/<name>/runs.jsonl.
Usage: python experiments/ext/eiv/check_rule.py results/ext_eiv_a1noise"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

out = Path(sys.argv[1])
rows = [json.loads(line) for line in open(out / "runs.jsonl")]
g = defaultdict(list)
for r in rows:
    g[(r["scenario"], r["T"], r["kind"], r["method"])].append(r)


def cov(rs):
    ok = [r for r in rs if r["status"] == "ok"]
    return sum(r["n_covered_nonnull"] for r in ok) / sum(r["n_nonnull"] for r in ok)


def iscore(rs):
    return float(np.mean([r["iscore_nonnull_mean"] for r in rs if r["status"] == "ok"]))


def nok(rs):
    return f"{sum(r['status'] == 'ok' for r in rs)}/{len(rs)}"


cells = [(T, k) for T in (80, 150) for k in ("none", "missing", "reversed")]
methods = ["oracle", "plugin", "inflate", "lp_allpast", "tolerant_v4", "tolerant_eiv"]
print("## Coverage / IS per cell\n")
print("| scenario | T | cell | " + " | ".join(methods) + " |")
print("|---|---|---|" + "---|" * len(methods))
for sc in ("clean", "noise0.1", "noise0.3"):
    for T, k in cells:
        print(f"| {sc} | {T} | {k} | " + " | ".join(f"{cov(g[(sc, T, k, m)]):.3f} / {iscore(g[(sc, T, k, m)]):.2f}" for m in methods) + " |")

print("\n## Rule\n")
c1 = []
for sc in ("noise0.1", "noise0.3"):
    for T, k in cells:
        c = cov(g[(sc, T, k, "tolerant_eiv")])
        c1.append((sc, T, k, c, c >= 0.90))
c2 = []
for T, k in cells:
    a, b = iscore(g[("clean", T, k, "tolerant_eiv")]), iscore(g[("clean", T, k, "tolerant_v4")])
    c2.append((T, k, a, b, a / b, a / b <= 1.15))
print("Condition 1 (coverage >= 0.90 in every noise cell):")
for sc, T, k, c, ok in c1:
    print(f"  {sc} T={T} {k}: {c:.3f} {'PASS' if ok else 'FAIL'}")
print(f"  -> {sum(x[-1] for x in c1)}/12 cells")
print("Condition 2 (clean IS <= 1.15 x tolerant_v4):")
for T, k, a, b, ratio, ok in c2:
    print(f"  T={T} {k}: eiv {a:.3f} v4 {b:.3f} ratio {ratio:.3f} {'PASS' if ok else 'FAIL'}")
print(f"  -> {sum(x[-1] for x in c2)}/6 cells")
print("VERDICT:", "RETAINED" if all(x[-1] for x in c1) and all(x[-1] for x in c2) else "REJECTED")

print("\n## r_hat of tolerant_eiv (mean) by scenario and T; true share 0 / 0.091 / 0.231\n")
for sc in ("clean", "noise0.1", "noise0.3"):
    for T in (80, 150):
        v = [r["info_r_hat"] for (s, t, k, m), rs in g.items() if s == sc and t == T and m == "tolerant_eiv"
             for r in rs if r.get("info_r_hat") is not None]
        u = [r["info_r_used"] for (s, t, k, m), rs in g.items() if s == sc and t == T and m == "tolerant_eiv"
             for r in rs if r.get("info_r_used") is not None]
        print(f"  {sc} T={T}: r_hat mean {np.mean(v):.3f} sd {np.std(v):.3f}; r_used mean {np.mean(u):.3f}")

print("\n## Width (median kept) and median abs err of C(H), tolerant_v4 vs tolerant_eiv\n")
for sc in ("clean", "noise0.1", "noise0.3"):
    for T, k in cells:
        s = []
        for m in ("tolerant_v4", "tolerant_eiv"):
            rs = [r for r in g[(sc, T, k, m)] if r["status"] == "ok"]
            s.append(f"{m}: width {np.median([r['width_kept'] for r in rs]):.3f} abserr {np.median([r['C_abs_err_nonnull'] for r in rs]):.3f} ok {nok(g[(sc, T, k, m)])}")
        print(f"  {sc} T={T} {k}: " + "; ".join(s))
