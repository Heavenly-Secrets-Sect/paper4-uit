"""SRCI without the stated damage vs SRCI and BVAR-Minnesota at the same guarantee level (docs/ext/p4h8_auto_spec.md).
Reads results/ext_p4h8_auto/test.json (new) and results/ext_p4h8_cmp/test.json (SRCI and BVAR-Minnesota on the same topologies)
with their frozen factors. Writes results/ext_p4h8_auto/test_eval.md and test_eval.json.
"""
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


def cp(k, n):
    lo = 0.0 if k == 0 else beta_dist.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else beta_dist.ppf(0.975, k + 1, n - k)
    return float(lo), float(hi)


def cells(path, frozen_path, methods):
    d = json.loads(Path(path).read_text())
    fac = json.loads((REPO / frozen_path).read_text())["factors"]
    exp = expected_runs(d)
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in d["records"]:
        by[r["cell"]][r["unit"]].append(r)
    out = {}
    for cell, units in by.items():
        m, T, kind = cell.split("|")[:3]
        if m not in methods:
            continue
        f = fac[f"{cell}|beta0.1"]["marginal"]
        if f is None or math.isinf(f) or f > 10:
            out[cell] = {"abstain": True}
            continue
        hit, n, uis, W, cn, cd = 0, 0, {}, [], 0, 0
        for u, c in exp[kind].items():
            if c <= 0:
                continue
            n += 1
            rs = units.get(u, [])
            hit += bool(len(rs) >= c and max([run_score(r["dist"], r["half"], 0.10) for r in rs] or [0.0]) <= f)
            if rs:
                dist = np.concatenate([np.array(r["dist"]) for r in rs]); half = np.concatenate([np.array(r["half"]) for r in rs])
                uis[u] = float(np.mean(2 * f * half + 40 * np.maximum(dist - f * half, 0)))
                W.append(float(np.mean(2 * f * half))); cn += int((dist <= f * half).sum()); cd += len(dist)
        lo, hi = cp(hit, n)
        out[cell] = {"abstain": False, "factor": f, "hit": hit / n, "ci": [lo, hi], "cov": cn / max(cd, 1), "IS": float(np.mean(list(uis.values()))),
                     "width": float(np.mean(W)), "uis": uis}
    return out


def main():
    a = cells(REPO / "results/ext_p4h8_auto/test.json", "experiments/calibration/p4h8_auto_frozen.json", {"srci_auto"})
    b = cells(REPO / "results/ext_p4h8_cmp/test.json", "experiments/calibration/p4h8_cmp_frozen.json", {"tolerant_v5_1", "bvar_minnesota_v2_cal"})
    rng = np.random.default_rng(0)
    lines = ["| T | kind | hit rate [95% CI] | pair cov | width | IS (auto) | IS (SRCI) | IS (BVAR) | auto - SRCI [95% CI] | auto - BVAR [95% CI] |", "|---|---|---|---|---|---|---|---|---|---|"]
    rec = {}
    for T in ("40", "150"):
        for k in ("none", "extra", "missing", "reversed"):
            x, s, v = a.get(f"srci_auto|{T}|{k}"), b.get(f"tolerant_v5_1|{T}|{k}"), b.get(f"bvar_minnesota_v2_cal|{T}|{k}")
            if not x or x["abstain"]:
                lines.append(f"| {T} | {k} | abstain | | | | | | | |")
                continue
            def diff(o):
                if not o or o["abstain"]:
                    return None
                us = sorted(set(x["uis"]) & set(o["uis"]))
                dd = np.array([x["uis"][u] - o["uis"][u] for u in us])
                bs = [rng.choice(dd, len(dd)).mean() for _ in range(1000)]
                return float(dd.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
            ds, dv = diff(s), diff(v)
            rec[f"{T}|{k}"] = {"hit": x["hit"], "ci": x["ci"], "cov": x["cov"], "width": x["width"], "IS": x["IS"], "IS_srci": s["IS"], "IS_bvar": v["IS"], "d_srci": ds, "d_bvar": dv}
            f = lambda d: "" if d is None else f"{d[0]:+.2f} [{d[1]:+.2f}, {d[2]:+.2f}]"
            lines.append(f"| {T} | {k} | {x['hit']:.3f} [{x['ci'][0]:.3f}, {x['ci'][1]:.3f}] | {x['cov']:.3f} | {x['width']:.2f} | {x['IS']:.2f} | {s['IS']:.2f} | {v['IS']:.2f} | {f(ds)} | {f(dv)} |")
    out = REPO / "results/ext_p4h8_auto"
    (out / "test_eval.md").write_text("\n".join(lines) + "\n")
    (out / "test_eval.json").write_text(json.dumps(rec, indent=1))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
