"""Red team: statistics on finished results (no new runs)."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from math import erf, sqrt
ROOT = Path(__file__).resolve().parents[3]

def load(run):
    return [json.loads(l) for l in open(ROOT / "results" / run / "runs.jsonl")]

def clustered_cov(rows, nres=4000, seed=0):
    by = defaultdict(lambda: [0, 0])
    for r in rows:
        by[r["topology"]][0] += r["n_covered_nonnull"]; by[r["topology"]][1] += r["n_nonnull"]
    a = np.array(list(by.values()), float)
    est = a[:, 0].sum() / a[:, 1].sum()
    rng = np.random.default_rng(seed)
    b = [a[i, 0].sum() / a[i, 1].sum() for i in (rng.integers(0, len(a), len(a)) for _ in range(nres))]
    per = a[:, 0] / a[:, 1]
    return est, np.quantile(b, [0.025, 0.975]), per.min(), per.max()

def diffs(rows, m, ref):
    idx = {(r["topology"], r["replicate"], r["method"]): r["iscore_nonnull_mean"] for r in rows if r["status"] == "ok"}
    by = defaultdict(list)
    for (t, rep, mm), v in idx.items():
        if mm == m and (t, rep, ref) in idx:
            by[t].append(v - idx[(t, rep, ref)])
    return by

def tci(by, alpha):
    from scipy import stats
    x = np.array([np.mean(v) for v in by.values()])
    se = x.std(ddof=1) / sqrt(len(x))
    return x.mean(), x.mean() + stats.t.ppf(1 - alpha / 2, len(x) - 1) * se

def cells(rows):
    g = defaultdict(list)
    for r in rows:
        if r["status"] == "ok" and r.get("n_nonnull") is not None:
            g[(r.get("scenario", "clean"), r["T"], r["kind"], r["rate"])].append(r)
    return g

print("== 1. Clustered (topology) 95% CI of pooled coverage, tolerant_v4 and key baselines")
for run, meths in [("a2_baselines", ["tolerant_v4", "ida_union", "bvar_minnesota"]), ("a2b_pselect", ["pselect_union"]),
                   ("a1_latent_noise", ["tolerant_v4"]), ("a3_ges", ["tolerant_v4"])]:
    rows = load(run)
    for key, g in sorted(cells(rows).items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2], kv[0][3])):
        for m in meths:
            gm = [r for r in g if r["method"] == m]
            if not gm: continue
            est, (lo, hi), pmin, pmax = clustered_cov(gm)
            if run.startswith("a2") and key[2] not in ("missing", "reversed"): continue
            flag = " <-- CI crosses 0.90" if lo < 0.90 <= est else (" <-- est<0.90 but CI reaches 0.90" if est < 0.90 <= hi else "")
            print(f"{run} {key} {m}: cov {est:.3f} [{lo:.3f},{hi:.3f}] per-topology range {pmin:.2f}-{pmax:.2f}{flag}")

print("\n== 2. Multiplicity: A2 / A2b cell wins under per-test 95% vs Bonferroni (t-based cluster CI, 20 topologies)")
try:
    import scipy  # noqa
    have = True
except ImportError:
    have = False
if have:
    a2 = load("a2_baselines"); a2b = load("a2b_pselect")
    # pair a2b rows into a2 (same seeds): use a2b tolerant_v4 and pselect
    tests = []
    for run, refs in ((a2, ["ida_union", "bvar_minnesota"]), (a2b, ["pselect_union"])):
        for key, g in cells(run).items():
            if key[2] == "none": continue
            for ref in refs:
                by = diffs(g, "tolerant_v4", ref)
                tests.append((key, ref, by))
    n = len(tests)
    for alpha, lab in ((0.05, "per-test"), (0.05 / n, f"Bonferroni over {n} tests")):
        win = defaultdict(lambda: True)
        for key, ref, by in tests:
            est, up = tci(by, alpha)
            win[key] &= up < 0
        cnt = defaultdict(int)
        for key, w in win.items(): cnt[key[2]] += w
        print(lab, dict(cnt), "missing cells lost:", sorted(k[1:] for k, w in win.items() if not w and k[2] == "missing"))
else:
    print("scipy missing")

print("\n== 3. Seed pairing a2_baselines vs a2b_pselect (plugin and tolerant_v4 rows must be identical)")
A = {(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"], r["method"]): r for r in load("a2_baselines")}
same = diff = 0
for r in load("a2b_pselect"):
    k = (r["topology"], r["replicate"], r["T"], r["kind"], r["rate"], r["method"])
    if k in A:
        if A[k].get("iscore_nonnull_mean") == r.get("iscore_nonnull_mean") and A[k].get("n_covered_nonnull") == r.get("n_covered_nonnull"): same += 1
        else: diff += 1
print("identical", same, "differing", diff)

print("\n== 4. Module width factors across configs (should be identical: 'frozen v4')")
keys = None
for run in ["rq42_v4", "a2_baselines", "a2b_pselect", "a3_ges", "a1_latent_noise", "a2_heldout", "b1v2_auto"]:
    c = json.loads((ROOT / "results" / run / "calibration.json").read_text())
    mod = {k: v for k, v in c.items() if k.startswith("mod|")}
    print(run, mod)

print("\n== 5. Lost-pair share and width (T=40/80/150, missing cells), a2_baselines + a2b")
for run in ("a2_baselines", "a2b_pselect"):
    for key, g in sorted(cells(load(run)).items()):
        if key[2] != "missing": continue
        for m in sorted({r["method"] for r in g}):
            gm = [r for r in g if r["method"] == m]
            lost = sum(r["n_lost"] for r in gm) / sum(r["n_nonnull"] for r in gm)
            ck = sum(r["n_covered_kept"] for r in gm) / max(1, sum(r["n_kept"] for r in gm))
            if m in ("tolerant_v4", "pselect_union", "bvar_minnesota", "ida_union", "plugin"):
                print(run, key[1:], m, f"lost {lost:.3f} cov_kept {ck:.3f} width_med {np.median([r['width_kept'] for r in gm if r.get('width_kept') is not None]):.2f}")

print("\n== 6. Null-pair coverage among reachable null pairs (n_covered_null_reach / n_null_reach), a2 + a2b, T=80")
for run in ("a2_baselines", "a2b_pselect"):
    for key, g in sorted(cells(load(run)).items()):
        if key[1] != 80: continue
        out = []
        for m in ("plugin", "tolerant_v4", "ida_union", "bvar_minnesota", "pselect_union"):
            gm = [r for r in g if r["method"] == m]
            if gm:
                out.append(f"{m} {sum(r['n_covered_null_reach'] for r in gm)/max(1,sum(r['n_null_reach'] for r in gm)):.3f} (n_reach/run {np.mean([r['n_null_reach'] for r in gm]):.0f})")
        print(run, key[2:], "; ".join(out))
