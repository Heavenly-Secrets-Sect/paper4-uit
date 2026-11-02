"""Skeptic checks of the redteam report (read-only on results)."""
import json, sys
from collections import defaultdict
from math import sqrt
from pathlib import Path
import numpy as np
from scipy import stats
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments")); sys.path.insert(0, str(ROOT / "src"))

def load(run): return [json.loads(l) for l in open(ROOT / "results" / run / "runs.jsonl")]

# (a) F7: v4 - pselect_union paired diffs in a2b_pselect, missing-0.2, t-based cluster CI
a2b = load("a2b_pselect")
print("a2b methods", sorted({r["method"] for r in a2b}))
idx = {(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"], r["method"]): r for r in a2b if r["status"] == "ok"}
for T in (40, 80, 150):
    for rate in (0.2, 0.5):
        by = defaultdict(list)
        for (t, rep, TT, k, ra, m), r in idx.items():
            if m == "tolerant_v4" and TT == T and k == "missing" and ra == rate:
                p = idx.get((t, rep, TT, k, ra, "pselect_union"))
                if p: by[t].append(r["iscore_nonnull_mean"] - p["iscore_nonnull_mean"])
        x = np.array([np.mean(v) for v in by.values()]); se = x.std(ddof=1) / sqrt(len(x))
        up95 = x.mean() + stats.t.ppf(0.975, len(x) - 1) * se
        upB = x.mean() + stats.t.ppf(1 - 0.025 / 54, len(x) - 1) * se
        print(f"v4-pselect T={T} missing-{rate}: {x.mean():+.3f} up95 {up95:+.3f} upBonf54 {upB:+.3f} n_topo {len(x)}")
# (b) F5: pselect n_graphs and n_selected
for T in (40, 80, 150):
    rs = [r for r in a2b if r["method"] == "pselect_union" and r["T"] == T and r["status"] == "ok"]
    keys = [k for k in rs[0] if "graph" in k or "select" in k]
    print(T, "pselect info keys", keys, {k: round(float(np.mean([r[k] for r in rs])), 2) for k in keys})
