"""Ablation of T and damage level (feedback point 10), exploratory, P4-H7 design split.

Input : results/ext_p4h7_ablation/units_r<rate>.json (p4h7_units.py --split design --rates <rate>)
        results/ext_p4h7_cal/factors.json (marginal beta=0.10 factors from the calibration split)
Note on "success": a unit whose damage draw has k = 0 (reversed flips contemporaneous edges only, so few of them
at a low rate) is filed under the undamaged cell and has no record in the damaged cell. That is not a fit failure and
does not depend on T, so success is reported relative to the best T of the same (kind, rate): success_adj = success / max_T success.
Coverage is conditional on a successful fit.
Rule fixed BEFORE reading the table: a cell (kind, T, rate) is USABLE when the fit succeeds for at least 95% of
the topologies and the pooled coverage of the non-null pairs, at the calibration-split marginal factor of the cell, is at least 0.90.
Output: results/ext_p4h7_ablation/ablation.md and ablation.json
"""
import collections
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "results/ext_p4h7_ablation"
RATES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
factors = json.loads((ROOT / "results/ext_p4h7_cal/factors.json").read_text())
out, lines = [], []
cells = collections.defaultdict(dict)  # (kind, T) -> rate -> dict
raw_success = {}
n_units = None
for r in RATES:
    p = D / f"units_r{r}.json"
    if not p.exists():
        continue
    d = json.loads(p.read_text())
    n_units = d["n_units"]
    by = collections.defaultdict(list)
    for rec in d["records"]:
        by[rec["cell"]].append(rec)
    for cell, recs in by.items():
        _, T, kind = cell.split("|")[0:3]
        T = int(T)
        if kind == "none":
            continue
        fac = factors[f"{cell}|beta0.1"]["marginal"]
        dist = np.concatenate([np.array(x["dist"]) for x in recs])
        half = np.concatenate([np.array(x["half"]) for x in recs])
        succ = len(recs) / n_units
        raw_success[(kind, T, r)] = succ
        cov = float(np.mean(dist <= fac * half))
        isc = float(np.mean(2 * fac * half + 40 * np.maximum(dist - fac * half, 0)))
        cells[(kind, T)][r] = {"success_raw": succ, "coverage": cov, "IS": isc}
for (kind, T), row in cells.items():
    for r, v in row.items():
        best = max(raw_success[(kind, t, r)] for t in (19, 30, 40, 80, 150) if (kind, t, r) in raw_success)
        v["success"] = v["success_raw"] / best if best else 0.0
        v["usable"] = v["success"] >= 0.95 and v["coverage"] >= 0.90
        out.append({"kind": kind, "T": T, "rate": r, **v})
for kind in ("missing", "extra", "reversed"):
    lines += [f"\n### {kind}: success rate / coverage (U = usable)\n", "| T | " + " | ".join(f"{r}" for r in RATES if any(r in v for v in cells.values())) + " |",
              "|---|" + "---|" * len([r for r in RATES if any(r in v for v in cells.values())])]
    for T in (19, 30, 40, 80, 150):
        row = cells.get((kind, T), {})
        lines.append(f"| {T} | " + " | ".join(
            (f"{row[r]['success']:.2f} / {row[r]['coverage']:.2f}{' U' if row[r]['usable'] else ''}" if r in row else "-")
            for r in RATES if any(r in v for v in cells.values())) + " |")
    # smallest T usable at every rate, largest usable rate at each T
    usable_T = [T for T in (19, 30, 40, 80, 150) if cells.get((kind, T)) and all(v["usable"] for v in cells[(kind, T)].values())]
    lines.append(f"\nUsable at every tested rate: T in {usable_T if usable_T else 'none'}.")
(D / "ablation.json").write_text(json.dumps(out, indent=1))
(D / "ablation.md").write_text(f"Design split ({n_units} topologies), exploratory. Cell format: fit success rate / coverage of non-null pairs at the calibration marginal beta=0.10 factor.\n" + "\n".join(lines) + "\n")
print((D / "ablation.md").read_text())
