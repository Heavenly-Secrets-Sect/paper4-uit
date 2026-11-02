"""Skeptic check (verify5_hubscreen2): independently confirm that tolerant_v5_1_hs2 never drops a declared
contemporaneous parent, using instrumentation that does NOT rely on the module's own RedLog2 counter.

For a slice of the P2 grid (D-07 dev, seed_base 70261102, same units/seeds as run_r5.run_unit), it:
  - wraps ext_r5hubscreen2.csis_reduce_v2: for EVERY reduction call (data, screening, draws) checks that the set of
    lag-0 terms in the output equals the set in the input, and that own lag 1 is kept when present;
  - wraps ext_r5hubscreen2.fit_equations: records the first data-level fit's term lists and checks that every
    declared parent (u, 0) for (u, j) in the PUBLIC skeleton's oriented set is present in equation j;
  - re-runs the driver's run_unit for hs2 only (with the factors_used.json of the P2 run) and compares
    iscore_nonnull_mean / status with the logged rows (reproduction check).
Writes results/ext_verify5_hubscreen2/check_lag0.json. Never modifies existing files.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path("/Users/kietnt/Desktop/Workspace/Paper4_UIT")
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "experiments" / "ext" / "r5hubscreen2"))


def work(args):
    topo_idx, rep, Ts = args
    import warnings
    warnings.filterwarnings("ignore")
    import run_r5  # driver (imports the module)
    from paper4 import ext_r5hubscreen2 as H
    from paper4.topology import load_bank
    from run_experiment import public, unit_skeletons, generator_config
    from paper4.generator import build_dynamic_sem

    stats = {"reduce_calls": 0, "trunc_calls": 0, "lag0_in": 0, "lag0_violations": 0, "ownlag1_violations": 0,
             "data_fits_checked": 0, "declared_parent_missing": 0, "declared_parents_total": 0}
    orig_reduce = H.csis_reduce_v2
    orig_fit = H.fit_equations
    state = {"first_fit_done": False, "skel": None}

    def reduce_wrap(data, tj, j, lag_max):
        r, tr = orig_reduce(data, tj, j, lag_max)
        stats["reduce_calls"] += 1
        stats["trunc_calls"] += int(tr)
        lin = {t for t in tj if t[1] == 0}
        lout = {t for t in r if t[1] == 0}
        stats["lag0_in"] += len(lin)
        if lin != lout:
            stats["lag0_violations"] += 1
        if (j, 1) in tj and (j, 1) not in r:
            stats["ownlag1_violations"] += 1
        return r, tr

    def fit_wrap(data, terms, lag_max, *a, **k):
        if not state["first_fit_done"] and state["skel"] is not None:
            state["first_fit_done"] = True
            sk = state["skel"]
            stats["data_fits_checked"] += 1
            for (u, v) in sk.oriented:
                stats["declared_parents_total"] += 1
                if (u, 0) not in terms[v]:
                    stats["declared_parent_missing"] += 1
        return orig_fit(data, terms, lag_max, *a, **k)

    H.csis_reduce_v2 = reduce_wrap
    H.fit_equations = fit_wrap
    orig_method = H.tolerant_v5_1_hs2

    def method_wrap(data, skel, lag_max, Hh, n_boot, rng):
        state["first_fit_done"] = False
        state["skel"] = skel
        return orig_method(data, skel, lag_max, Hh, n_boot, rng)

    run_r5.tolerant_v5_1_hs2 = method_wrap
    cfg = json.loads((ROOT / "experiments/configs/ext_r5hubscreen2_p2.json").read_text())
    cfg = dict(cfg, T=Ts, methods=[])
    fac = json.loads((ROOT / "results/ext_r5hubscreen2_p2/factors_used.json").read_text())
    topo = load_bank(cfg["bank"], cfg["split"])[topo_idx]
    rows = run_r5.run_unit((cfg, topo, topo_idx, rep, "main", fac))
    return stats, [{k: r.get(k) for k in ("method", "status", "iscore_nonnull_mean", "topology", "replicate", "T",
                                         "kind", "hs_reduced", "hs_trunc_eq_total", "hs_contemp_dropped")} for r in rows]


def main():
    jobs = [(t, rep, [19, 25]) for t in range(20) for rep in (0, 1)]
    agg, rows = {}, []
    with ProcessPoolExecutor(2) as pool:
        for st, rr in pool.map(work, jobs):
            for k, v in st.items():
                agg[k] = agg.get(k, 0) + v
            rows += rr
    logged = {}
    for l in open(ROOT / "results/ext_r5hubscreen2_p2/runs.jsonl"):
        r = json.loads(l)
        if r["method"] == "tolerant_v5_1_hs2":
            logged[(r["topology"], r["replicate"], r["T"], r["kind"])] = r
    match = mism = 0
    bad = []
    for r in rows:
        L = logged[(r["topology"], r["replicate"], r["T"], r["kind"])]
        same = L["status"] == r["status"] and (r["status"] != "ok" or L["iscore_nonnull_mean"] == r["iscore_nonnull_mean"])
        match += same
        if not same:
            mism += 1
            bad.append([r, {k: L[k] for k in ("status", "iscore_nonnull_mean")}])
    out = {"jobs": len(jobs), "hs2_runs": len(rows), "trunc_runs": sum(1 for r in rows if (r["hs_trunc_eq_total"] or 0) > 0),
           "instrumentation": agg, "reproduced_vs_logged": {"match": match, "mismatch": mism, "examples": bad[:5]}}
    (ROOT / "results/ext_verify5_hubscreen2/check_lag0.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
