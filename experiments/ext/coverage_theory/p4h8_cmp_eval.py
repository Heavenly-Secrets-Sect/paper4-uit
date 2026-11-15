"""P4-H8 comparison at the same guarantee level: evaluate the frozen factors on the test dump (docs/ext/p4h8_cmp_spec.md).

    python p4h8_cmp_eval.py --test results/ext_p4h8_cmp/test.json --frozen experiments/calibration/p4h8_cmp_frozen.json
Per (method, T, stated kind) cell: topology hit rate (at most 10% of non-null pairs missed, failed fits count as misses) with the
exact binomial interval, pooled pair coverage, mean width and mean interval score; per (T, kind) the winner among the methods
whose hit-rate interval reaches 0.90 (lowest mean IS) and the paired IS difference to SRCI with a topology cluster bootstrap.
"""
import argparse
import collections
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.stats import beta as beta_dist

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path[:0] = [str(HERE)]
from p4h7_factors import expected_runs, run_score  # noqa: E402

SRCI = "tolerant_v5_1"
LABEL = {"tolerant_v5_1": "SRCI", "pselect_union_v3": "PSel-Union (32x)", "pselect_cal": "PSel", "fullvar_cal": "Full VAR",
         "targeted_lp_cal": "TLP", "bvar_minnesota_v2_cal": "BVAR-Minnesota"}


def cp(k, n):
    lo = 0.0 if k == 0 else beta_dist.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else beta_dist.ppf(0.975, k + 1, n - k)
    return float(lo), float(hi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", default=str(REPO / "results/ext_p4h8_cmp/test.json"))
    ap.add_argument("--frozen", default="experiments/calibration/p4h8_cmp_frozen.json")
    a = ap.parse_args()
    fac = json.loads((REPO / a.frozen).read_text())["factors"]
    d = json.loads(Path(a.test).read_text())
    exp = expected_runs(d)
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in d["records"]:
        by[r["cell"]][r["unit"]].append(r)
    # unit ids in the order of the topology list, for the expected-runs map
    res = {}
    for cell, units in by.items():
        method, T, kind = cell.split("|")[0], cell.split("|")[1], cell.split("|")[2]
        f = fac[f"{cell}|beta0.1"]["marginal"]
        if f is None or math.isinf(f) or f > 10:
            res[(method, T, kind)] = {"abstain": True}
            continue
        hit, IS, W, cov_num, cov_den, unit_is = 0, [], [], 0, 0, {}
        n_exp = 0
        for u, c in exp[kind].items():
            if c <= 0:
                continue
            n_exp += 1
            rs = units.get(u, [])
            ok = len(rs) >= c and max([run_score(r["dist"], r["half"], 0.10) for r in rs] or [0.0]) <= f
            hit += bool(ok)
            if rs:
                dist = np.concatenate([np.array(r["dist"]) for r in rs]); half = np.concatenate([np.array(r["half"]) for r in rs])
                unit_is[u] = float(np.mean(2 * f * half + 40 * np.maximum(dist - f * half, 0)))
                W.append(float(np.mean(2 * f * half)))
                cov_num += int((dist <= f * half).sum()); cov_den += len(dist)
        lo, hi = cp(hit, n_exp)
        res[(method, T, kind)] = {"abstain": False, "factor": f, "hit": hit / n_exp, "ci": [lo, hi], "cov": cov_num / max(cov_den, 1),
                                  "IS": float(np.mean(list(unit_is.values()))), "width": float(np.mean(W)), "unit_is": unit_is}
    lines = ["| T | kind | method | factor | hit rate [95% CI] | pair cov | mean width | mean IS | at guarantee level |",
             "|---|---|---|---|---|---|---|---|---|"]
    wins = collections.Counter()
    diffs = collections.defaultdict(list)
    rng = np.random.default_rng(0)
    for T in ("40", "150"):
        for kind in ("none", "extra", "missing", "reversed"):
            cands = []
            for m in LABEL:
                r = res.get((m, T, kind))
                if r is None:
                    continue
                if r["abstain"]:
                    lines.append(f"| {T} | {kind} | {LABEL[m]} | abstain | - | - | - | - | no |")
                    continue
                ok = r["ci"][1] >= 0.90
                lines.append(f"| {T} | {kind} | {LABEL[m]} | {r['factor']} | {r['hit']:.3f} [{r['ci'][0]:.3f}, {r['ci'][1]:.3f}] | {r['cov']:.3f} | "
                             f"{r['width']:.2f} | {r['IS']:.2f} | {'yes' if ok else 'no'} |")
                if ok:
                    cands.append((r["IS"], m))
            if cands:
                wins[min(cands)[1]] += 1
            s = res.get((SRCI, T, kind))
            if s and not s["abstain"]:
                for m in LABEL:
                    r = res.get((m, T, kind))
                    if m == SRCI or r is None or r["abstain"]:
                        continue
                    us = sorted(set(s["unit_is"]) & set(r["unit_is"]))
                    dd = np.array([r["unit_is"][u] - s["unit_is"][u] for u in us])
                    bs = [rng.choice(dd, len(dd)).mean() for _ in range(1000)]
                    diffs[m].append((T, kind, float(dd.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))))
    lines.append("\nCells won (lowest mean IS among methods at the guarantee level): " + ", ".join(f"{LABEL[m]} {n}" for m, n in wins.most_common()))
    lines.append("\nPaired IS difference to SRCI (method minus SRCI; positive = SRCI better), 95% topology cluster bootstrap:\n")
    lines.append("| method | cells SRCI better (CI above 0) | cells method better (CI below 0) | cells inconclusive | total |")
    lines.append("|---|---|---|---|---|")
    for m, v in diffs.items():
        lines.append(f"| {LABEL[m]} | {sum(x[3] > 0 for x in v)} | {sum(x[4] < 0 for x in v)} | {sum(x[3] <= 0 <= x[4] for x in v)} | {len(v)} |")
    out = REPO / "results/ext_p4h8_cmp"
    (out / "test_eval.md").write_text("\n".join(lines) + "\n")
    (out / "test_eval.json").write_text(json.dumps({"diffs": diffs, "wins": wins, "cells": {"|".join(k): {x: y for x, y in v.items() if x != "unit_is"} for k, v in res.items()}}, indent=1, default=float))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
