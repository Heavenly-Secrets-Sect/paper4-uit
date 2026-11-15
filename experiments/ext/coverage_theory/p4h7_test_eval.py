"""P4-H7 test evaluation (protocol: docs/ext/p4h7_spec.md). Run ONCE, after the freeze.

Input : results/ext_p4h7_test/units.json (made by p4h7_units.py --split test, allowed only after the freeze)
        experiments/calibration/p4h7_frozen.json
Output: results/ext_p4h7_test/test_eval.md and test_eval.json

Per (T, stated kind) cell and per factor variant {pooled (shipped rule), marginal beta .05/.10, PAC beta .05/.10}:
  hit rate  = fraction of test topologies whose unit score S_test(beta) <= factor (failed fits count as misses),
              with the exact Clopper-Pearson 95% interval;
  pair miss = mean over test runs of the fraction of non-null pairs outside the interval;
  pooled coverage of non-null pairs;
  mean interval score and mean width of the non-null pairs (IS = width + 40 * distance outside, alpha = 0.05).
Success criteria are those of the spec: the marginal beta=0.10 hit rate's interval contains or exceeds 0.90 in
at least 80% of cells and no cell's upper limit is below 0.85.
"""
import argparse
import collections
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import beta as beta_dist

from p4h7_factors import expected_runs, run_score

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results/ext_p4h7_test"


def cp_interval(k, n, alpha=0.05):
    lo = 0.0 if k == 0 else beta_dist.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta_dist.ppf(1 - alpha / 2, k + 1, n - k)
    return float(lo), float(hi)


def main():
    global OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(OUT), help="folder with units.json; outputs go there (use results/ext_p4h7_design for a dry run)")
    ap.add_argument("--frozen", default="experiments/calibration/p4h7_frozen.json")
    ap.add_argument("--expected-runs", action="store_true", help="P4-H8 rule: a missing record is a failure only where a run was expected; a factor above 10 or infinite is an abstention")
    a = ap.parse_args()
    OUT = Path(a.dir)
    frozen = json.loads((ROOT / a.frozen).read_text())["factors"]
    d = json.loads((OUT / "units.json").read_text())
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in d["records"]:
        by[r["cell"]][r["unit"]].append(r)
    n_units = d["n_units"]
    exp = expected_runs(d) if a.expected_runs else None
    rows, lines, crit = [], ["| cell | variant | factor | hit rate | 95% CI | pair miss | pooled cov | IS | width |",
                             "|---|---|---|---|---|---|---|---|---|"], []
    for cell in sorted(by, key=lambda c: (int(c.split("|")[1]), c)):
        need = 1 if cell.split("|")[2] == "none" else 2
        variants = [("pooled", None, frozen[f"{cell}|pooled"])]
        for b in (0.05, 0.10):
            f = frozen[f"{cell}|beta{b}"]
            variants += [(f"marginal b{b}", b, f["marginal"]), (f"PAC b{b}", b, f["pac"])]
        for name, b, fac in variants:
            if fac is None or (isinstance(fac, float) and math.isinf(fac)) or (exp is not None and fac > 10):
                lines.append(f"| {cell} | {name} | abstain | - | - | - | - | - | - |")
                continue
            beta_eval = b if b is not None else 0.10
            hits = 0
            if exp is None:
                for u, rs in by[cell].items():
                    ok = len(rs) >= need and max(run_score(r["dist"], r["half"], beta_eval) for r in rs) <= fac
                    hits += bool(ok)
                n_cell = n_units
            else:
                kind = cell.split("|")[2]
                for u, c in exp[kind].items():
                    if c <= 0:
                        continue
                    rs = by[cell].get(u, [])
                    hits += bool(len(rs) >= c and max([run_score(r["dist"], r["half"], beta_eval) for r in rs] or [0.0]) <= fac)
                n_cell = sum(1 for c in exp[kind].values() if c > 0)
            hits_total = hits  # units absent from the dump (failed in every run) count as misses
            lo, hi = cp_interval(hits_total, n_cell)
            dist = np.concatenate([np.array(r["dist"]) for rs in by[cell].values() for r in rs])
            half = np.concatenate([np.array(r["half"]) for rs in by[cell].values() for r in rs])
            miss_run = [np.mean(np.array(r["dist"]) > fac * np.array(r["half"])) for rs in by[cell].values() for r in rs]
            cov = float(np.mean(dist <= fac * half))
            width = 2 * fac * half
            isc = width + 40 * np.maximum(dist - fac * half, 0)
            row = {"cell": cell, "variant": name, "factor": fac, "hit": hits_total / n_cell, "ci": [lo, hi],
                   "pair_miss": float(np.mean(miss_run)), "pooled_cov": cov, "IS": float(isc.mean()), "width": float(width.mean())}
            rows.append(row)
            lines.append(f"| {cell} | {name} | {fac} | {row['hit']:.3f} | [{lo:.3f}, {hi:.3f}] | {row['pair_miss']:.3f} | "
                         f"{cov:.3f} | {row['IS']:.2f} | {row['width']:.2f} |")
            if name == "marginal b0.1":
                crit.append((cell, lo, hi))
    ok_cells = sum(hi >= 0.90 for _, lo, hi in crit)
    worst_hi = min(hi for _, lo, hi in crit)
    n_abstain = sum(1 for l in lines if "| marginal b0.1 | abstain" in l)
    verdict = (f"Criterion (i): marginal beta=0.10 hit rate interval reaches 0.90 in {ok_cells}/{len(crit)} non-abstaining cells "
               f"(need >= 80%); smallest upper limit {worst_hi:.3f} (need >= 0.85). Abstaining cells (no finite factor): {n_abstain}.")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "test_eval.json").write_text(json.dumps({"rows": rows, "verdict": verdict}, indent=2))
    (OUT / "test_eval.md").write_text("\n".join(lines) + "\n\n" + verdict + "\n")
    print(verdict)


if __name__ == "__main__":
    main()
