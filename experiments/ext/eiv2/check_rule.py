"""Apply the pre-registered rule of docs/ext/eiv2.md to results/ext_eiv2_eval/runs.jsonl, with the
multiplicity report (cluster bootstrap by topology, B = 2000, default_rng(0), Holm at 0.05) and the
extra (non-scoring) tables: noise0.1/noise0.3 paired IS vs v4, null pairs, ablation, r_hat.
Usage: python experiments/ext/eiv2/check_rule.py results/ext_eiv2_eval > results/ext_eiv2_eval/rule_check.txt"""
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
CELLS = [(T, k) for T in (80, 150) for k in ("none", "missing", "reversed")]
SCEN = ("clean", "noise0.1", "noise0.3")
B = 2000
CAND, REF = "tolerant_eiv2", "tolerant_v4"
SHARE = {"clean": 0.0, "noise0.1": 0.1 / 1.1, "noise0.3": 0.3 / 1.3}


def ok(rs):
    return [r for r in rs if r["status"] == "ok"]


def cov(rs):
    rs = ok(rs)
    return sum(r["n_covered_nonnull"] for r in rs) / sum(r["n_nonnull"] for r in rs)


def iscore(rs):
    return float(np.mean([r["iscore_nonnull_mean"] for r in ok(rs)]))


def by_topo(rs):
    d = defaultdict(list)
    for r in ok(rs):
        d[r["topology"]].append(r)
    return d


def boot(stat, groups, seed=0):
    """Cluster bootstrap over topologies; ``groups`` is a list of dicts topo -> rows (same topos)."""
    rng = np.random.default_rng(seed)
    topos = sorted(set.intersection(*[set(gr) for gr in groups]))
    vals = []
    for _ in range(B):
        pick = [topos[i] for i in rng.choice(len(topos), len(topos))]
        vals.append(stat(*[[r for t in pick for r in gr[t]] for gr in groups]))
    return np.array(vals)


def holm(pvals, alpha=0.05):
    order = np.argsort(pvals)
    rej = np.zeros(len(pvals), dtype=bool)
    for rank, i in enumerate(order):
        if pvals[i] <= alpha / (len(pvals) - rank):
            rej[i] = True
        else:
            break
    return rej


def paired(sc, T, k, a, b):
    idx = {(r["topology"], r["replicate"]): r["iscore_nonnull_mean"] for r in ok(g[(sc, T, k, b)])}
    d = defaultdict(list)
    for r in ok(g[(sc, T, k, a)]):
        key = (r["topology"], r["replicate"])
        if key in idx:
            d[r["topology"]].append(r["iscore_nonnull_mean"] - idx[key])
    topos = sorted(d)
    est = float(np.mean([v for t in topos for v in d[t]]))
    rng = np.random.default_rng(0)
    bs = np.array([np.mean([v for i in rng.choice(len(topos), len(topos)) for v in d[topos[i]]]) for _ in range(B)])
    lo, hi = np.quantile(bs, (0.025, 0.975))
    p = min(1.0, 2 * min((bs <= 0).mean(), (bs >= 0).mean()))
    return est, lo, hi, p


methods = ["oracle", "plugin", "tolerant_v4", "tolerant_eiv2", "plugin_eiv2"]
print("# ext_eiv2_eval: rule check (docs/ext/eiv2.md)\n")
print("## Coverage / IS per cell (ok runs)\n")
print("| scenario | T | cell | " + " | ".join(methods) + " |")
print("|---|---|---|" + "---|" * len(methods))
for sc in SCEN:
    for T, k in CELLS:
        print(f"| {sc} | {T} | {k} | " + " | ".join(
            f"{cov(g[(sc, T, k, m)]):.3f} / {iscore(g[(sc, T, k, m)]):.2f}" for m in methods) + " |")
print("\nok runs per method: " + ", ".join(
    f"{m} {sum(r['status'] == 'ok' for r in rows if r['method'] == m)}/{sum(r['method'] == m for r in rows)}" for m in methods))

print("\n## Rule\n")
print("Condition 1 (coverage of tolerant_eiv2 >= 0.90 in every noise cell); cluster-bootstrap one-sided p-values")
c1, p_hi, p_lo = [], [], []
for sc in ("noise0.1", "noise0.3"):
    for T, k in CELLS:
        rs = g[(sc, T, k, CAND)]
        c = cov(rs)
        bs = boot(cov, [by_topo(rs)])
        c1.append((sc, T, k, c, c >= 0.90))
        p_hi.append((bs <= 0.90).mean())   # H0: cov <= 0.90
        p_lo.append((bs >= 0.90).mean())   # H0: cov >= 0.90
rh, rl = holm(np.array(p_hi)), holm(np.array(p_lo))
for i, (sc, T, k, c, passed) in enumerate(c1):
    print(f"  {sc} T={T} {k}: {c:.3f} {'PASS' if passed else 'FAIL'} | p(cov<=0.90) {p_hi[i]:.4f}"
          f"{' *Holm' if rh[i] else ''} | p(cov>=0.90) {p_lo[i]:.4f}{' *Holm' if rl[i] else ''}")
n1 = sum(x[-1] for x in c1)
print(f"  -> {n1}/12 cells pass (point estimate)")
print(f"  -> Holm (12 cells): {rh.sum()}/12 significantly above 0.90; {rl.sum()}/12 significantly below 0.90")
print(f"  -> unadjusted p<0.05: {(np.array(p_hi) < 0.05).sum()}/12 above, {(np.array(p_lo) < 0.05).sum()}/12 below")

print("\nCondition 2 (clean IS of tolerant_eiv2 <= 1.15 x tolerant_v4)")
c2, q_le, q_gt = [], [], []
for T, k in CELLS:
    a, b = g[("clean", T, k, CAND)], g[("clean", T, k, REF)]
    ratio = iscore(a) / iscore(b)
    bs = boot(lambda x, y: np.mean([r["iscore_nonnull_mean"] for r in x]) / np.mean([r["iscore_nonnull_mean"] for r in y]),
              [by_topo(a), by_topo(b)])
    c2.append((T, k, iscore(a), iscore(b), ratio, ratio <= 1.15))
    q_le.append((bs >= 1.15).mean())   # H0: ratio >= 1.15
    q_gt.append((bs <= 1.15).mean())   # H0: ratio <= 1.15
r2l, r2g = holm(np.array(q_le)), holm(np.array(q_gt))
for i, (T, k, a, b, ratio, passed) in enumerate(c2):
    print(f"  T={T} {k}: eiv2 {a:.3f} v4 {b:.3f} ratio {ratio:.3f} {'PASS' if passed else 'FAIL'} | "
          f"p(ratio>=1.15) {q_le[i]:.4f}{' *Holm' if r2l[i] else ''} | p(ratio<=1.15) {q_gt[i]:.4f}{' *Holm' if r2g[i] else ''}")
n2 = sum(x[-1] for x in c2)
print(f"  -> {n2}/6 cells pass (point estimate)")
print(f"  -> Holm (6 cells): {r2l.sum()}/6 significantly below 1.15; {r2g.sum()}/6 significantly above 1.15")
print("\nVERDICT:", "RETAINED" if n1 == 12 and n2 == 6 else "REJECTED", f"(condition 1: {n1}/12, condition 2: {n2}/6)")

print("\n## Paired IS difference tolerant_eiv2 - tolerant_v4 (95% CI clustered by topology; two-sided bootstrap p)\n")
for sc in SCEN:
    res = [paired(sc, T, k, CAND, REF) for T, k in CELLS]
    rej = holm(np.array([x[3] for x in res]))
    for (T, k), (est, lo, hi, p), h in zip(CELLS, res, rej):
        print(f"  {sc} T={T} {k}: {est:+.2f} [{lo:+.2f}, {hi:+.2f}] p={p:.4f}{' *Holm' if h else ''}")
    better = sum(x[2] < 0 for x in res); worse = sum(x[1] > 0 for x in res)
    hb = sum(h and x[0] < 0 for x, h in zip(res, rej)); hw = sum(h and x[0] > 0 for x, h in zip(res, rej))
    print(f"  -> {sc}: CI excludes 0: better {better}/6, worse {worse}/6; Holm (6 cells): better {hb}/6, worse {hw}/6")

print("\n## Ablation: paired IS differences\n")
for a, b in (("plugin_eiv2", "plugin"), ("tolerant_eiv2", "plugin_eiv2")):
    for sc in SCEN:
        res = [paired(sc, T, k, a, b) for T, k in CELLS]
        rej = holm(np.array([x[3] for x in res]))
        cells = "; ".join(f"T{T} {k} {e:+.2f} [{lo:+.2f}, {hi:+.2f}]{'*' if h else ''}"
                          for (T, k), (e, lo, hi, _), h in zip(CELLS, res, rej))
        print(f"  {a} - {b}, {sc}: {cells}")
print("  (* = significant after Holm across the 6 cells of that line)")

print("\n## Null pairs: C_abs_spurious median (mean) and mean iscore_null_mean\n")
NM = ["plugin", "tolerant_v4", "tolerant_eiv2", "plugin_eiv2"]
print("| scenario | T | cell | " + " | ".join(NM) + " |")
print("|---|---|---|" + "---|" * len(NM))
higher = 0
for sc in SCEN:
    for T, k in CELLS:
        cs = []
        meds = {}
        for m in NM:
            rs = ok(g[(sc, T, k, m)])
            v = [r["C_abs_spurious"] for r in rs if r.get("C_abs_spurious") is not None]
            iv = [r["iscore_null_mean"] for r in rs if r.get("iscore_null_mean") is not None]
            meds[m] = np.median(v)
            cs.append(f"{np.median(v):.3f} ({np.mean(v):.3f}) / IS0 {np.mean(iv):.3f}")
        higher += meds["tolerant_eiv2"] > meds["tolerant_v4"]
        print(f"| {sc} | {T} | {k} | " + " | ".join(cs) + " |")
print(f"\ncells where median null |C| of tolerant_eiv2 > tolerant_v4: {higher}/18")

print("\n## r_hat of tolerant_eiv2 (all cells pooled): mean (sd); true share; mean #equations capped at r_hat\n")
for sc in SCEN:
    for T in (80, 150):
        rs = [r for (s, t, k, m), v in g.items() if s == sc and t == T and m == CAND for r in ok(v)]
        rh_ = np.array([r["info_r_hat"] for r in rs]); ru = np.array([r["info_r_used"] for r in rs])
        nc = np.array([r["info_n_eq_capped"] for r in rs])
        print(f"  {sc} T={T}: r_hat {rh_.mean():.3f} ({rh_.std():.3f}), true {SHARE[sc]:.3f}; r_used {ru.mean():.3f}; "
              f"#eq capped {nc.mean():.2f}; PD fixes {sum(r['info_n_pd_fix'] for r in rs)}")
