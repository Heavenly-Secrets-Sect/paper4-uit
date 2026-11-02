"""V0 of r5hubscreen2 (docs/ext/r5hubscreen2.md, section 3): unit tests of the v2 reduction and an identity probe
on D-07H development (design-probe units, replicate 7 of seed_base 70261102 + 500 000: outside the calibration
replicates 0..2 and outside every evaluation unit). No D-07 data.

  T1  CSIS branch (|C_j| <= cap - 1) equals round-4 csis_reduce exactly (random cases).
  T2  truncation branch (|C_j| > cap - 1): keeps own lag 1 and EVERY lag-0 term, drops own lags 2..lag_max,
      keeps no pool term at lag_max 2; random stress over lag_max 1..3: no lag-0 term is ever dropped.
  T3  a reduced equation still failing fit_equations' check -> data-level run fails "underdetermined".
  T4  identity probe: on every probe run with hs_reduced = 0, hs2 == tolerant_v5_1 bit for bit (status, C, lo, hi);
      on every probe run with no truncation-branch equation, hs2 == round-4 tolerant_v5_1_hs bit for bit.
      Also: hs_contemp_dropped == 0 on every run.
V0 passes iff T1..T4 all pass. Writes results/ext_r5hubscreen2_tests/{tests.md, tests.json}.

Run: python experiments/ext/r5hubscreen2/tests.py [--units 8 --nboot 99]
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
from paper4.ext_r5hubscreen2 import RedLog2, csis_reduce_v2, fit_reduced2, tolerant_v5_1_hs2  # noqa: E402
from paper4.ext_v51 import tolerant_v5_1  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.skeleton import Skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

OUT = ROOT / "results" / "ext_r5hubscreen2_tests"
SEED_PROBE = 70261102 + 500_000


def random_terms(rng, n, j, lag_max, n_par, n_pool):
    own = [(j, l) for l in range(1, lag_max + 1)]
    others = [i for i in range(n) if i != j]
    pool_nodes = rng.choice(others, size=min(n_pool, len(others)), replace=False)
    pool = [(int(i), l) for i in sorted(pool_nodes) for l in range(1, lag_max + 1)]
    par = sorted((int(i), 0) for i in rng.choice(others, size=min(n_par, len(others)), replace=False))
    return own + pool + par


def t1(rng):
    n_case = n_eq = 0
    bad = []
    for _ in range(3000):
        lag_max = int(rng.integers(1, 4))
        T = int(rng.integers(12, 45))
        m = T - lag_max
        cap = cap_columns(m)
        n = 14
        data = rng.normal(size=(T, n))
        j = int(rng.integers(0, n))
        n_par = int(rng.integers(0, 5))
        tj = random_terms(rng, n, j, lag_max, n_par, int(rng.integers(0, 13)))
        C = [t for t in tj if (t[0] == j and t[1] > 0) or t[1] == 0]
        if len(C) > cap - 1:
            continue
        n_case += 1
        a = csis_reduce(data, tj, j, lag_max)
        b, tr = csis_reduce_v2(data, tj, j, lag_max)
        n_eq += a == b and not tr
        if not (a == b and not tr):
            bad.append({"T": T, "lag": lag_max, "j": j})
    return {"cases": n_case, "equal": n_eq, "pass": n_case > 500 and n_eq == n_case, "bad": bad[:5]}


def t2(rng):
    # deterministic: lag 2, m = 17 (T 19) -> cap 6; 5 parents -> |C| = 7 > 5
    T, lag_max, n, j = 19, 2, 14, 0
    data = rng.normal(size=(T, n))
    tj = [(0, 1), (0, 2)] + [(i, l) for i in (6, 7, 8) for l in (1, 2)] + [(i, 0) for i in (1, 2, 3, 4, 5)]
    r, tr = csis_reduce_v2(data, tj, j, lag_max)
    det = tr and r == [(0, 1)] + [(i, 0) for i in (1, 2, 3, 4, 5)]
    det_r = list(r)
    # stress
    n_trunc = n_all = viol = own2_kept = 0
    for _ in range(4000):
        lag_max = int(rng.integers(1, 4))
        T = int(rng.integers(10, 45))
        data = rng.normal(size=(T, n))
        j = int(rng.integers(0, n))
        tj = random_terms(rng, n, j, lag_max, int(rng.integers(0, 13)), int(rng.integers(0, 13)))
        r, tr = csis_reduce_v2(data, tj, j, lag_max)
        n_all += 1
        n_trunc += tr
        viol += sum(1 for t in tj if t[1] == 0) != sum(1 for t in r if t[1] == 0)
        if tr:
            own2_kept += any(t[0] == j and t[1] >= 2 for t in r)
            viol += (j, 1) not in r
    return {"deterministic_case": det_r, "deterministic_pass": bool(det), "stress_cases": n_all,
            "stress_trunc": n_trunc, "lag0_or_ownlag1_violations": viol, "own_lag_ge2_kept_in_trunc": own2_kept,
            "pass": bool(det) and viol == 0 and own2_kept == 0 and n_trunc > 100}


def t3(rng):
    # node 0 has 6 declared parents; T 8, lag 2 -> m 6: own lag 1 + 6 parents = 7 terms, 7 + 2 > 6 -> fail
    n, T, lag_max = 8, 8, 2
    data = rng.normal(size=(T, n))
    sk = Skeleton(n, {(i, 0) for i in range(1, 7)}, set(), {"kind": "none", "k": 0})
    terms = [[(j, 1), (j, 2)] + ([(i, 0) for i in range(1, 7)] if j == 0 else []) for j in range(n)]
    log = RedLog2()
    f = fit_reduced2(data, terms, lag_max, log)
    res = tolerant_v5_1_hs2(data, sk, lag_max, 4, 19, np.random.default_rng(0))
    ok = f.status == "underdetermined" and log.fit_fail >= 1 and log.contemp_dropped == 0 and res.status == "underdetermined"
    return {"fit_status": f.status, "fit_fail": log.fit_fail, "method_status": res.status,
            "method_info_fit_fail": res.info.get("hs_fit_fail"), "pass": bool(ok)}


def same(a, b):
    return a.status == b.status and (a.status != "ok" or (np.array_equal(a.C, b.C) and np.array_equal(a.lo, b.lo)
                                                          and np.array_equal(a.hi, b.hi)))


def t4(units, nboot):
    topos = load_bank("D-07H", "development")[:units]
    cfg = {"generator": {"lag_max": 2, "q0": 0.3, "cross_coef": [0.3, 0.8], "self_coef": [0.2, 0.6],
                         "noise_var": [0.5, 1.5], "rho_max": 0.9, "burn_in": 200},
           "damage": {"kinds": ["extra", "missing", "reversed"], "rates": [0.2, 0.5]}}
    gen = generator_config(cfg)
    rows = []
    tag = ext_seed("tolerant_v5_1")
    for t_idx, topo in enumerate(topos):
        unit = SEED_PROBE + 1000 * t_idx + 7
        sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
        sks = unit_skeletons(sem, unit, cfg)
        for T in (19, 25, 30, 40):
            data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
            for c_idx, cell in enumerate(sks):
                if cell[1] == 0.5:
                    continue
                skel = public(sks[cell])
                t0 = time.perf_counter()
                a = tolerant_v5_1(data, skel, 2, 4, nboot, np.random.default_rng([unit, 3, T, c_idx, tag]))
                t1_ = time.perf_counter()
                b = tolerant_v5_1_hs2(data, skel, 2, 4, nboot, np.random.default_rng([unit, 3, T, c_idx, tag]))
                t2_ = time.perf_counter()
                c = tolerant_v5_1_hs(data, skel, 2, 4, nboot, np.random.default_rng([unit, 3, T, c_idx, tag]))
                rows.append({"T": T, "cell": f"{cell[0]}-{cell[1]}", "topo": topo.id, "v51": a.status, "hs2": b.status,
                             "hs1": c.status, "reduced": b.info.get("hs_reduced"), "trunc": b.info.get("hs_trunc_eq_total"),
                             "contemp_dropped": b.info.get("hs_contemp_dropped"), "fit_fail": b.info.get("hs_fit_fail"),
                             "screen_fail": b.info.get("hs_screen_fail"),
                             "ident_v51": bool(same(a, b)), "ident_v1": bool(same(b, c)),
                             "sec_v51": round(t1_ - t0, 3), "sec_hs2": round(t2_ - t1_, 3)})
    nonred = [r for r in rows if r["reduced"] == 0]
    notr = [r for r in rows if r["trunc"] == 0]
    ok = (all(r["ident_v51"] for r in nonred) and all(r["ident_v1"] for r in notr)
          and all(r["contemp_dropped"] == 0 for r in rows))
    v51ok_changed = sum(1 for r in rows if r["v51"] == "ok" and not r["ident_v51"])
    return {"runs": len(rows), "nonreduced": len(nonred), "nonreduced_identical_v51": sum(r["ident_v51"] for r in nonred),
            "no_trunc": len(notr), "no_trunc_identical_v1": sum(r["ident_v1"] for r in notr),
            "reduced": len(rows) - len(nonred), "trunc_runs": len(rows) - len(notr),
            "v51_ok": sum(r["v51"] == "ok" for r in rows), "v51_ok_changed": v51ok_changed,
            "hs2_ok": sum(r["hs2"] == "ok" for r in rows), "contemp_dropped_total": sum(r["contemp_dropped"] for r in rows),
            "mean_sec_v51": float(np.mean([r["sec_v51"] for r in rows])),
            "mean_sec_hs2": float(np.mean([r["sec_hs2"] for r in rows])), "pass": bool(ok), "rows": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", type=int, default=8)
    ap.add_argument("--nboot", type=int, default=99)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261105)
    R = {"T1": t1(rng), "T2": t2(rng), "T3": t3(rng), "T4": t4(a.units, a.nboot)}
    R["V0"] = all(R[k]["pass"] for k in ("T1", "T2", "T3", "T4"))
    t4r = R["T4"]
    lines = ["# r5hubscreen2 V0 (generated by experiments/ext/r5hubscreen2/tests.py)", "",
             f"- T1 CSIS branch == round-4 csis_reduce: {R['T1']['equal']}/{R['T1']['cases']} -> {'PASS' if R['T1']['pass'] else 'FAIL'}",
             f"- T2 truncation branch: deterministic case {'PASS' if R['T2']['deterministic_pass'] else 'FAIL'}; stress {R['T2']['stress_cases']} cases "
             f"({R['T2']['stress_trunc']} truncation), lag-0 / own-lag-1 violations {R['T2']['lag0_or_ownlag1_violations']}, "
             f"own lag >= 2 kept in truncation {R['T2']['own_lag_ge2_kept_in_trunc']} -> {'PASS' if R['T2']['pass'] else 'FAIL'}",
             f"- T3 still-underdetermined equation -> fit {R['T3']['fit_status']}, method {R['T3']['method_status']} -> "
             f"{'PASS' if R['T3']['pass'] else 'FAIL'}",
             f"- T4 identity probe (D-07H dev, {a.units} topologies x replicate 7, lag 2, T 19/25/30/40, none + 0.2 cells, n_boot {a.nboot}): "
             f"runs {t4r['runs']}; non-reduced {t4r['nonreduced']}, identical to v5_1 {t4r['nonreduced_identical_v51']}; "
             f"no truncation {t4r['no_trunc']}, identical to round-4 v1 {t4r['no_trunc_identical_v1']}; lag-0 dropped total "
             f"{t4r['contemp_dropped_total']} -> {'PASS' if t4r['pass'] else 'FAIL'}",
             f"- T4 descriptive: reduced runs {t4r['reduced']} (with truncation {t4r['trunc_runs']}); v5_1 ok {t4r['v51_ok']}, "
             f"of which changed by hs2 {t4r['v51_ok_changed']}; hs2 ok {t4r['hs2_ok']}/{t4r['runs']}; "
             f"mean seconds v5_1 {t4r['mean_sec_v51']:.2f}, hs2 {t4r['mean_sec_hs2']:.2f}",
             "", f"**V0: {'PASS' if R['V0'] else 'FAIL'}**"]
    (OUT / "tests.json").write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")
    (OUT / "tests.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
