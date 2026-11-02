"""Validity check on D-07H development (design probe, no evaluation data): tolerant_v5_1_hs must equal
tolerant_v5_1 exactly (C, lo, hi, status) on every run where it reports no reduction, with the same
random-number stream. Also unit tests of csis_reduce on a known case, and timing.

Run: python experiments/ext/r4hubscreen/check_identity.py [--units 8] -> results/ext_r4hubscreen_identity/identity.{md,json}
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
from run_experiment import ext_seed, generator_config, public, unit_skeletons  # noqa: E402
from paper4.ext_r4hubscreen import cap_columns, csis_reduce, tolerant_v5_1_hs  # noqa: E402
from paper4.ext_v51 import tolerant_v5_1  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

OUT = ROOT / "results" / "ext_r4hubscreen_identity"


def unit_test():
    """y depends on own lag 1 and x3 lag 1 strongly; x1, x2 lags are noise. With a cap that leaves one
    pool slot, CSIS must keep (3, 1)."""
    rng = np.random.default_rng(0)
    T = 40
    X = rng.normal(size=(T, 4))
    for t in range(1, T):
        X[t, 0] = 0.5 * X[t - 1, 0] + 1.5 * X[t - 1, 3] + 0.3 * rng.normal()
    m = T - 1
    cap = cap_columns(m)  # 15
    tj = [(0, 1)] + [(i, 1) for i in (1, 2, 3)] + [(0, 0)] * 0
    # force a tiny cap by passing a shorter series slice: m=7 -> cap=2 -> d = 2-1-1 = 0; use m=9 -> cap 3 -> d=1
    short = X[:10]
    kept = csis_reduce(short, tj, 0, 1)
    return {"cap_full": cap, "kept_short": kept, "pass": kept == [(0, 1), (3, 1)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", type=int, default=8)
    ap.add_argument("--nboot", type=int, default=99)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    topos = load_bank("D-07H", "development")[: a.units]
    rows = []
    for lag, Ts in ((2, (25, 30, 40)), (1, (19,))):
        cfg = {"generator": {"lag_max": lag, "q0": 0.3, "cross_coef": [0.3, 0.8], "self_coef": [0.2, 0.6],
                             "noise_var": [0.5, 1.5], "rho_max": 0.9, "burn_in": 200},
               "damage": {"kinds": ["extra", "missing", "reversed"], "rates": [0.2, 0.5]}}
        gen = generator_config(cfg)
        for t_idx, topo in enumerate(topos):
            unit = 20261102 + 500_000 + 1000 * t_idx + 7  # replicate 7: outside the calibration units
            sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
            sks = unit_skeletons(sem, unit, cfg)
            for T in Ts:
                data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
                for c_idx, cell in enumerate(sks):
                    if cell[1] == 0.5:
                        continue
                    skel = public(sks[cell])
                    t0 = time.perf_counter()
                    a1 = tolerant_v5_1(data, skel, lag, 4, a.nboot, np.random.default_rng([unit, 3, T, c_idx, 9]))
                    t1 = time.perf_counter()
                    b1 = tolerant_v5_1_hs(data, skel, lag, 4, a.nboot, np.random.default_rng([unit, 3, T, c_idx, 9]))
                    t2 = time.perf_counter()
                    same = (a1.status == b1.status and (a1.status != "ok" or (
                        np.array_equal(a1.C, b1.C) and np.array_equal(a1.lo, b1.lo) and np.array_equal(a1.hi, b1.hi))))
                    rows.append({"lag": lag, "T": T, "cell": f"{cell[0]}-{cell[1]}", "topo": topo.id,
                                 "v51": a1.status, "hs": b1.status, "reduced": b1.info.get("hs_reduced"),
                                 "eq_data": b1.info.get("hs_eq_data"), "draws_red": b1.info.get("hs_draws_reduced"),
                                 "dropped": b1.info.get("hs_terms_dropped"), "identical": bool(same),
                                 "sec_v51": round(t1 - t0, 2), "sec_hs": round(t2 - t1, 2)})
    nonred = [r for r in rows if r["reduced"] == 0]
    viol = [r for r in nonred if not r["identical"]]
    ut = unit_test()
    lines = ["# Identity check tolerant_v5_1_hs vs tolerant_v5_1 (D-07H development, replicate 7, n_boot %d)" % a.nboot, "",
             f"- unit test csis_reduce: {ut}",
             f"- runs: {len(rows)}; without reduction: {len(nonred)}; identical among them: {len(nonred) - len(viol)} -> "
             f"**{'PASS' if not viol and ut['pass'] else 'FAIL'}**",
             f"- runs with reduction: {len(rows) - len(nonred)}; v5_1 failed among them: "
             f"{sum(r['v51'] != 'ok' for r in rows if r['reduced'])}; hs failed overall: {sum(r['hs'] != 'ok' for r in rows)}",
             f"- mean seconds per run: v5_1 {np.mean([r['sec_v51'] for r in rows]):.2f}, hs {np.mean([r['sec_hs'] for r in rows]):.2f}",
             "", "| lag | T | cell | runs | reduced | v5_1 ok | hs ok | identical (non-reduced) |", "|---|---|---|---|---|---|---|---|"]
    keys = sorted({(r["lag"], r["T"], r["cell"]) for r in rows})
    for k in keys:
        g = [r for r in rows if (r["lag"], r["T"], r["cell"]) == k]
        nr = [r for r in g if r["reduced"] == 0]
        lines.append(f"| {k[0]} | {k[1]} | {k[2]} | {len(g)} | {sum(r['reduced'] for r in g)} | {sum(r['v51']=='ok' for r in g)} | "
                     f"{sum(r['hs']=='ok' for r in g)} | {sum(r['identical'] for r in nr)}/{len(nr)} |")
    (OUT / "identity.json").write_text(json.dumps({"rows": rows, "unit_test": str(ut)}, indent=1))
    (OUT / "identity.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
