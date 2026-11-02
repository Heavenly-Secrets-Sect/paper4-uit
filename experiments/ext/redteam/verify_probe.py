"""Check that pair-level records of pair_probe.py reproduce the stored rows of a2_baselines / a2b_pselect."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4.topology import load_bank
from paper4.metrics import interval_score
recs = np.load(Path(__file__).parent / "out/p1.npz")["recs"]
M = ["plugin", "tolerant_v4", "bvar_minnesota", "pselect_union"]
CELLS = [("none", 0.0), ("extra", 0.2), ("extra", 0.5), ("missing", 0.2), ("missing", 0.5), ("reversed", 0.2), ("reversed", 0.5)]
ids = [t.id for t in load_bank("D-07", "development")]
stored = {}
for run in ("a2_baselines", "a2b_pselect"):
    for line in open(ROOT / "results" / run / "runs.jsonl"):
        r = json.loads(line)
        stored[(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"], r["method"])] = r
g = defaultdict(list)
for row in recs:
    g[tuple(int(x) for x in row[:5])].append(row)
same = diff = 0
for (t, rep, T, c, m), rows in g.items():
    rows = np.array(rows)
    nn = rows[:, 5] > 0
    ct, lo, hi = rows[:, 6], rows[:, 7], rows[:, 8]
    cov = int(((lo <= ct) & (ct <= hi))[nn].sum())
    isc = float(interval_score(lo, hi, ct)[nn].mean())
    s = stored[(ids[t], rep, T, CELLS[c][0], CELLS[c][1], M[m])]
    if s["n_covered_nonnull"] == cov and abs(s["iscore_nonnull_mean"] - isc) < 1e-9:
        same += 1
    else:
        diff += 1
        print("DIFF", ids[t], rep, T, CELLS[c], M[m], s["n_covered_nonnull"], cov, s["iscore_nonnull_mean"], isc)
print("probe groups identical to stored rows:", same, "differing:", diff)
