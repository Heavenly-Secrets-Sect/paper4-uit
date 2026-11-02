"""Round-1 redteam numbers that existed only in shell output (synthesis 1.6 / R2-9), recomputed from
stored results and written to results/ext_baselines2_r1fix/numbers.md:
- pselect_union internals (a2b_pselect): mean info_n_graphs and info_n_selected per T (all cells, and none cell);
- F7: v4 - pselect_union IS margin at missing-0.2, t-based CI clustered by topology (20), per-test 95% and
  Bonferroni over 54 tests (as in stats_existing.py);
- F6 reframed (verifier): share of v4's margin over pselect_cal obtained by fullvar_cal,
  (IS(pselect_cal) - IS(fullvar_cal)) / (IS(pselect_cal) - IS(v4)), from ext_redteam_calbase.
"""
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
load = lambda p: [json.loads(l) for l in open(ROOT / p)]  # noqa: E731
out = ["# Round-1 redteam numbers written to file (recomputed from stored results)", ""]
a2b = load("results/a2b_pselect/runs.jsonl")
ps = [r for r in a2b if r["method"] == "pselect_union" and r["status"] == "ok"]
out += ["## pselect_union internals (results/a2b_pselect)", "", "| T | mean n_graphs (all cells) | mean n_selected (all cells) | mean n_selected (none cell) |", "|---|---|---|---|"]
for T in (40, 80, 150):
    g = [r for r in ps if r["T"] == T]
    gn = [r for r in g if r["kind"] == "none"]
    out.append(f"| {T} | {np.mean([r['info_n_graphs'] for r in g]):.2f} | {np.mean([r['info_n_selected'] for r in g]):.2f} | "
               f"{np.mean([r['info_n_selected'] for r in gn]):.2f} |")
out += ["", "Draws per graph in round 1: per = max(10, 199 // n_graphs) = max(10, 199 // 16) = 12.", ""]

idx = {(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"], r["method"]): r for r in a2b if r["status"] == "ok"}
out += ["## F7: v4 - pselect_union at missing-0.2 (t-based CI clustered by topology, df 19)", "",
        "| T | estimate | per-test 95% CI | Bonferroni (54 tests) CI |", "|---|---|---|---|"]
for T in (40, 80, 150):
    per = defaultdict(list)
    for (tp, rep, t, k, rt, m), r in idx.items():
        if m == "tolerant_v4" and t == T and k == "missing" and rt == 0.2:
            o = idx.get((tp, rep, t, k, rt, "pselect_union"))
            if o:
                per[tp].append(r["iscore_nonnull_mean"] - o["iscore_nonnull_mean"])
    tm = np.array([np.mean(v) for v in per.values()])
    est, se = tm.mean(), tm.std(ddof=1) / np.sqrt(len(tm))
    q1, qb = stats.t.ppf(0.975, len(tm) - 1), stats.t.ppf(1 - 0.05 / (2 * 54), len(tm) - 1)
    out.append(f"| {T} | {est:+.3f} | [{est - q1 * se:+.3f}, {est + q1 * se:+.3f}] | [{est - qb * se:+.3f}, {est + qb * se:+.3f}] |")

cb = load("results/ext_redteam_calbase/runs.jsonl")
def mis(T, rate, m):
    g = [r for r in cb if r["T"] == T and r["kind"] == "missing" and r["rate"] == rate and r["method"] == m and r["status"] == "ok"]
    return float(np.mean([r["iscore_nonnull_mean"] for r in g]))
out += ["", "## F6 reframed: share of v4's margin over pselect_cal reached by fullvar_cal (results/ext_redteam_calbase)", "",
        "| T | cell | IS v4 | IS pselect_cal | IS fullvar_cal | share |", "|---|---|---|---|---|---|"]
for T in (80, 150):
    for rate in (0.2, 0.5):
        a, b, c = mis(T, rate, "tolerant_v4"), mis(T, rate, "pselect_cal"), mis(T, rate, "fullvar_cal")
        out.append(f"| {T} | missing-{rate} | {a:.3f} | {b:.3f} | {c:.3f} | {(b - c) / (b - a):+.2f} |")
d = ROOT / "results" / "ext_baselines2_r1fix"; d.mkdir(parents=True, exist_ok=True)
(d / "numbers.md").write_text("\n".join(out) + "\n")
print("\n".join(out))
