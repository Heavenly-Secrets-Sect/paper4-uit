"""V1 analysis: unit-level scores of the v5.1 width calibration on D-07H development.

Reads results/ext_coverage_v1/v1_pairs.json (made by v1_dump.py) and, per (T, stated kind), reports:
the pooled pair-level factor as the code computes it (reproduced), the frozen factor, the maximum pooled
coverage on the grid, and the distribution of the unit score S = smallest grid factor at which at most beta of
a run's non-null pairs are missed (max over the two damage rates), plus the max-rule factor (max over units).
Writes results/ext_coverage_v1/v1_summary.md.
"""
import collections
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import run_experiment as R  # noqa: E402

G = np.array(R.C_GRID)
units = json.loads((ROOT / "results/ext_coverage_v1/v1_pairs.json").read_text())
frozen = json.loads((ROOT / "results/ext_v51_eval/calibration.json").read_text())
cells = collections.defaultdict(lambda: collections.defaultdict(list))
for e in units:
    cells[e["cell"]][e["job"]].append(e)


def score(dist, half, beta):
    d, h = np.array(dist), np.array(half)
    rho = np.where(h > 0, d / np.where(h > 0, h, 1), np.where(d > 0, np.inf, 0.0))
    for c in G:
        if (rho > c).mean() <= beta + 1e-12:
            return float(c)
    return np.inf


lines = ["| cell | units | pairs/run | pooled c* (reproduced) | frozen | max pooled coverage | S(0.05) median / q90 / max | S(0.10) median / q90 / max | S=inf |",
         "|---|---|---|---|---|---|---|---|---|"]
for cell in sorted(cells, key=lambda c: (int(c.split("|")[1]), c)):
    dist = [x for es in cells[cell].values() for e in es for x in e["dist"]]
    half = [x for es in cells[cell].values() for e in es for x in e["half"]]
    dist, half = np.array(dist), np.array(half)
    cov = np.array([(dist <= c * half).mean() for c in G])
    cstar = G[np.argmax(cov >= min(0.95, cov.max() - 0.005))]
    s = {b: np.array([max(score(e["dist"], e["half"], b) for e in es) for es in cells[cell].values()]) for b in (0.05, 0.10)}
    ppr = np.mean([len(e["dist"]) for es in cells[cell].values() for e in es])
    inf = max((~np.isfinite(v)).mean() for v in s.values())
    f = lambda v: f"{np.median(v):.1f} / {np.quantile(v, 0.9):.1f} / {v.max():.1f}"
    lines.append(f"| {cell} | {len(cells[cell])} | {ppr:.1f} | {cstar:.1f} | {frozen.get(cell, '-')} | {cov.max():.3f} | {f(s[0.05])} | {f(s[0.10])} | {100 * inf:.0f}% |")
out = ROOT / "results/ext_coverage_v1/v1_summary.md"
out.write_text("\n".join(lines) + "\n")
print("\n".join(lines))
