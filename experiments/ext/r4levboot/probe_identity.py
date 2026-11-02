"""Checks and design probe on D-07H development ONLY (calibration bank; D-07 is never touched here).

For the first --topos topologies of D-07H development, 1 replicate, lag_max in --lags, T in --Ts,
cells none / missing-0.2 / reversed-0.2 / missing-0.5 (runner seeding with seed_base 77_000_000,
not used anywhere else):
  I1  r4levboot_U (uniform pool through the module's plumbing, CRN) == tolerant_v5_1 exactly
      (lo, hi, C max abs diff 0);
  I2  the reference wrapper of the driver (profile-only simulator) leaves tolerant_v5_1 unchanged;
  I3  estimator.simulate_from_fit / estimator.cumulative are restored after every call, also after
      an exception inside the method;
  I4  leverage: sum_t h_tj = number of columns of X_j (incl. intercept) for every equation of the fit;
  P   leverage profile, pool-variance ratio, raw width ratio arm / v5_1 and seconds per call.
Writes results/ext_r4levboot_probe/probe.json.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

import run_experiment as R  # noqa: E402
from paper4 import estimator as E  # noqa: E402
from paper4 import ext_r4levboot as L  # noqa: E402
from paper4.ext_v51 import tolerant_v5_1  # noqa: E402
from paper4.generator import GeneratorConfig, build_dynamic_sem  # noqa: E402
from paper4.skeleton import damage, true_skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

GEN = dict(q0=0.3, cross_coef=(0.3, 0.8), self_coef=(0.2, 0.6), noise_var=(0.5, 1.5), rho_max=0.9, burn_in=200)
SEED = 77_000_000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topos", type=int, default=4)
    ap.add_argument("--Ts", type=int, nargs="+", default=[40, 150])
    ap.add_argument("--lags", type=int, nargs="+", default=[2])
    ap.add_argument("--nboot", type=int, default=199)
    args = ap.parse_args()
    topos = load_bank("D-07H", "development")[: args.topos]
    out = {"checks": {"I1_maxdiff": 0.0, "I1_n": 0, "I2_maxdiff": 0.0, "I3_restored": True, "I4_maxdev": 0.0},
           "profile": []}
    orig_sim, orig_cum = E.simulate_from_fit, E.cumulative
    for lag in args.lags:
        gen = GeneratorConfig(lag_max=lag, **GEN)
        for t_idx, topo in enumerate(topos):
            unit = SEED + 1000 * t_idx + lag
            sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
            truth = true_skeleton(sem)
            coef = {e: float(sem.B[lg, e[1], e[0]]) for e, lg in sem.edge_lag.items()}
            cells = [("none", 0.0), ("missing", 0.2), ("missing", 0.5), ("reversed", 0.2)]
            for T in args.Ts:
                data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
                for c_idx, (kind, rate) in enumerate(cells):
                    k_idx = {"none": 0, "missing": 1, "reversed": 2}[kind]
                    skel = R.public(damage(truth, kind, rate, np.random.default_rng([unit, 1, k_idx]),
                                           sem.edge_lag, coef))
                    rng = lambda tag: np.random.default_rng([unit, 3, T, c_idx, tag])  # noqa: E731
                    t0 = time.perf_counter()
                    ref = tolerant_v5_1(data, skel, lag, 4, args.nboot, rng(R.ext_seed("tolerant_v5_1")))
                    t_ref = time.perf_counter() - t0
                    rec = {"lag_max": lag, "T": T, "topo": topo.id, "kind": kind, "rate": rate,
                           "ref_status": ref.status, "sec": {"ref": t_ref}}
                    # I2: driver's profile-only wrapper
                    st = {}
                    with L.bootstrap_hooks(L.make_simulator("ORIG", st), st):
                        ref2 = tolerant_v5_1(data, skel, lag, 4, args.nboot, rng(R.ext_seed("tolerant_v5_1")))
                    rec["ref_profile"] = st
                    if ref.status == "ok" and ref2.status == "ok":
                        out["checks"]["I2_maxdiff"] = max(out["checks"]["I2_maxdiff"],
                                                          float(np.max(np.abs(ref.lo - ref2.lo))),
                                                          float(np.max(np.abs(ref.hi - ref2.hi))))
                    for mode in ("U", "L2", "L3", "W3"):
                        name = f"r4levboot_{mode}"
                        t0 = time.perf_counter()
                        res = L.METHODS[name](data, skel, lag, 4, args.nboot, rng(R.ext_seed(name)))
                        rec["sec"][mode] = time.perf_counter() - t0
                        if E.simulate_from_fit is not orig_sim or E.cumulative is not orig_cum:
                            out["checks"]["I3_restored"] = False
                        rec[mode] = {"status": res.status,
                                     **{k: res.info.get(k) for k in ("lev_mean", "lev_max", "lev_share_gt09",
                                                                      "lev_share_floored", "lev_eq_mean_max",
                                                                      "pool_var_ratio", "boot_tries", "boot_succ", "crn")}}
                        if res.status == "ok" and ref.status == "ok":
                            w = np.median((res.hi - res.lo)[~np.eye(sem.n, dtype=bool)])
                            w0 = np.median((ref.hi - ref.lo)[~np.eye(sem.n, dtype=bool)])
                            rec[mode]["width_ratio_median"] = float(w / w0)
                            if mode == "U":
                                d = max(float(np.max(np.abs(res.lo - ref.lo))), float(np.max(np.abs(res.hi - ref.hi))),
                                        float(np.max(np.abs(res.C - ref.C))))
                                out["checks"]["I1_maxdiff"] = max(out["checks"]["I1_maxdiff"], d)
                                out["checks"]["I1_n"] += 1
                    out["profile"].append(rec)
                    print(json.dumps({k: rec[k] for k in ("lag_max", "T", "topo", "kind", "rate")}),
                          {m: (rec[m].get("lev_mean"), rec[m].get("lev_share_gt09"), rec[m].get("pool_var_ratio"),
                               rec[m].get("width_ratio_median")) for m in ("L2", "L3", "W3")},
                          {k: round(v, 2) for k, v in rec["sec"].items()}, flush=True)
            # I4 on one fit: leverage sums
            from paper4.estimator import fit_equations, parent_terms
            terms = [parent_terms(truth, j, lag) for j in range(sem.n)]
            data = sem.simulate(80, np.random.default_rng([unit, 2, 80]))
            fit = fit_equations(data, terms, lag)
            h = L.leverages(fit, data)
            dev = max(abs(h[:, j].sum() - (1 + len(terms[j]))) for j in range(sem.n))
            out["checks"]["I4_maxdev"] = max(out["checks"]["I4_maxdev"], float(dev))
    # I3 after an exception
    def boom(fit, data, rng):
        raise RuntimeError("x")
    try:
        with L.bootstrap_hooks(boom, {}):
            E.simulate_from_fit(None, None, None)
    except RuntimeError:
        pass
    out["checks"]["I3_restored"] &= (E.simulate_from_fit is orig_sim and E.cumulative is orig_cum)
    d = ROOT / "results" / "ext_r4levboot_probe"
    d.mkdir(parents=True, exist_ok=True)
    (d / "probe.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out["checks"]))


if __name__ == "__main__":
    main()
