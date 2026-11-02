"""Design probe for the switching threshold tau of tolerant_v5_1, on the CALIBRATION bank only
(D-07H development). D-07 is never touched. Procedure fixed in docs/ext/v51.md before running.

For every topology x replicate x T x missing rate (0.2, 0.5; nested damage), fit
  - "targeted": v5's targeted opening re-selected per draw (ext_narrow.tolerant_sel, reselect=True,
    mult 3, alpha_open 0.10), and
  - "all": v3 with all lags (methods.tolerant, target_reversal=True), i.e. v5_cal2 before scaling.
Per (T, variant), c* is the factor (grid 0.5..5 step 0.05, as the runner's two-sided grid for v5)
that brings coverage pooled over both rates to min(0.95, max - 0.005), as the runner calibrates.
Per run: IS at c*. d(T) = mean over runs of IS_targeted - IS_all, CI clustered by topology.
Also records r = (T - lag_max) / (1 + n lag_max + |oriented| / n) of each stated skeleton.

Run: python experiments/ext/v51/probe_tau2.py --topos 20 --reps 3 --nboot 199 --workers 3 --out experiments/ext/v51/probe_tau2.json

probe_tau2 = probe_tau with the targeted variant de-duplicated (ext_v51.tolerant_sel_dd instead of
ext_narrow.tolerant_sel, see docs/decision_rules.md, last section). Same seeds, grid and analysis; the
"all" variant is therefore identical to probe_tau.
"""
import argparse
import json
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4 import methods as M  # noqa: E402
from paper4.ext_v51 import tolerant_sel_dd as tolerant_sel  # noqa: E402  (de-duplicated terms)
from paper4.ext_v51 import allag_ratio  # noqa: E402
from paper4.generator import GeneratorConfig, build_dynamic_sem  # noqa: E402
from paper4.metrics import truth_effects  # noqa: E402
from paper4.skeleton import damage, true_skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

GEN = GeneratorConfig(lag_max=2, q0=0.3, cross_coef=(0.3, 0.8), self_coef=(0.2, 0.6), noise_var=(0.5, 1.5),
                      rho_max=0.9, burn_in=200)
GRID = np.round(np.arange(0.5, 5.001, 0.05), 3)


def unit(args):
    t_idx, rep, topo, Ts, nboot = args
    seed = 7_710_000 + 100 * t_idx + rep
    sem = build_dynamic_sem(topo, GEN, np.random.default_rng([seed, 0]))
    truth = true_skeleton(sem)
    coef = {e: float(sem.B[lag, e[1], e[0]]) for e, lag in sem.edge_lag.items()}
    _, C_true, _, _ = truth_effects(sem, 4)
    nonnull = ~np.eye(sem.n, dtype=bool) & (np.abs(C_true) > 0.1)
    out = []
    for T in Ts:
        data = sem.simulate(T, np.random.default_rng([seed, 2, T]))
        for rate in (0.2, 0.5):
            skel = damage(truth, "missing", rate, np.random.default_rng([seed, 1, 2]), sem.edge_lag, coef)
            skel.log, skel.lag_hint = [], None   # public skeleton only
            for v_idx, v in enumerate(("targeted", "all")):
                rng = np.random.default_rng([seed, 3, T, v_idx, int(rate * 10)])
                t0 = time.perf_counter()
                if v == "targeted":
                    r = tolerant_sel(data, skel, 2, 4, nboot, rng, reselect=True, name=v)
                else:
                    r = M.tolerant(data, skel, 2, 4, nboot, rng, target_reversal=True, name=v)
                rec = {"topo": topo.id, "rep": rep, "T": T, "rate": rate, "v": v, "status": r.status,
                       "sec": time.perf_counter() - t0, "ratio": allag_ratio(skel, T, 2), "k": skel.damage.get("k")}
                if r.status == "ok":
                    mid, half = (r.lo + r.hi) / 2, (r.hi - r.lo) / 2
                    rec.update({"dist": np.abs(C_true - mid)[nonnull].tolist(), "half": half[nonnull].tolist(),
                                "n_open": r.info.get("n_open"), "n_open_boot": r.info.get("n_open_boot_mean")})
                out.append(rec)
    return out


def analyse(rows, Ts):
    rep = {}
    for T in Ts:
        cstar, IS = {}, {}
        for v in ("targeted", "all"):
            rs = [r for r in rows if r["T"] == T and r["v"] == v and r["status"] == "ok"]
            d = np.concatenate([r["dist"] for r in rs]); h = np.concatenate([r["half"] for r in rs])
            cov = np.array([(d <= c * h).mean() for c in GRID])
            c = float(GRID[np.argmax(cov >= min(0.95, cov.max() - 0.005))])
            cstar[v] = c
            for r in rs:
                dd, hh = np.array(r["dist"]), np.array(r["half"])
                IS[(r["topo"], r["rep"], r["rate"], v)] = (float(np.mean(2 * c * hh + 40 * np.maximum(dd - c * hh, 0))),
                                                           float(np.mean(dd <= c * hh)))
        diffs = defaultdict(list)
        per_rate = {0.2: [], 0.5: []}
        for (topo, rp, rate, v), (s, _) in IS.items():
            if v == "targeted" and (topo, rp, rate, "all") in IS:
                dlt = s - IS[(topo, rp, rate, "all")][0]
                diffs[topo].append(dlt)
                per_rate[rate].append(dlt)
        topos = list(diffs)
        est = float(np.mean([x for t in topos for x in diffs[t]]))
        rng = np.random.default_rng(0)
        boots = [np.mean([x for i in rng.choice(len(topos), len(topos)) for x in diffs[topos[i]]]) for _ in range(2000)]
        lo, hi = np.quantile(boots, (0.025, 0.975))
        entry = {"T": T, "c_star": cstar, "d": est, "lo": float(lo), "hi": float(hi), "n_pairs": sum(map(len, diffs.values())),
                 "d_rate0.2": float(np.mean(per_rate[0.2])), "d_rate0.5": float(np.mean(per_rate[0.5])),
                 "ratio_mean": float(np.mean([r["ratio"] for r in rows if r["T"] == T])),
                 "ratio_min": float(np.min([r["ratio"] for r in rows if r["T"] == T])),
                 "ratio_max": float(np.max([r["ratio"] for r in rows if r["T"] == T])),
                 "fail": {v: sum(1 for r in rows if r["T"] == T and r["v"] == v and r["status"] != "ok") for v in ("targeted", "all")},
                 "sec": {v: float(np.mean([r["sec"] for r in rows if r["T"] == T and r["v"] == v])) for v in ("targeted", "all")}}
        for v in ("targeted", "all"):
            for rate in (0.2, 0.5):
                vals = [IS[k] for k in IS if k[2] == rate and k[3] == v]
                entry[f"IS_{v}_{rate}"] = float(np.mean([x[0] for x in vals]))
                entry[f"cov_{v}_{rate}"] = float(np.mean([x[1] for x in vals]))
            no = [r["n_open"] for r in rows if r["T"] == T and r["v"] == v and r.get("n_open") is not None]
            entry[f"n_open_{v}"] = float(np.mean(no)) if no else None
        entry["targeted_clearly_better"] = bool(hi < 0)
        rep[T] = entry
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topos", type=int, default=20)
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--nboot", type=int, default=99)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--T", type=int, nargs="+", default=[40, 60, 80, 100, 120, 150, 200])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    topos = load_bank("D-07H", "development")[: a.topos]
    jobs = [(i, rp, t, a.T, a.nboot) for i, t in enumerate(topos) for rp in range(a.reps)]
    t0 = time.perf_counter()
    rows = []
    with ProcessPoolExecutor(a.workers) as pool:
        for o in pool.map(unit, jobs):
            rows.extend(o)
    report = analyse(rows, a.T)
    # threshold rule (docs/ext/v51.md): T* = largest probed T with targeted clearly better at every probed T <= T*
    Tstar = None
    for T in a.T:
        if report[T]["targeted_clearly_better"]:
            Tstar = T
        else:
            break
    if Tstar is None:
        tau, note = 0.0, "targeted not clearly better at the smallest T: tau = 0 (v5_1 = v5_cal2)"
    elif Tstar == a.T[-1]:
        tau, note = report[Tstar]["ratio_mean"], "targeted clearly better at every probed T: tau = mean ratio at the largest T"
    else:
        nxt = a.T[a.T.index(Tstar) + 1]
        tau = (report[Tstar]["ratio_mean"] + report[nxt]["ratio_mean"]) / 2
        note = f"T* = {Tstar}, next probed T = {nxt}: tau = midpoint of their mean ratios"
    res = {"args": vars(a), "seconds": time.perf_counter() - t0, "report": report, "T_star": Tstar, "tau": tau, "note": note}
    Path(a.out).write_text(json.dumps(res, indent=1))
    for T in a.T:
        e = report[T]
        print(f"T={T} ratio {e['ratio_mean']:.2f} [{e['ratio_min']:.2f},{e['ratio_max']:.2f}] c* {e['c_star']} "
              f"d {e['d']:+.3f} [{e['lo']:+.3f},{e['hi']:+.3f}] (0.2: {e['d_rate0.2']:+.3f}, 0.5: {e['d_rate0.5']:+.3f}) "
              f"fail {e['fail']} sec {e['sec']}")
    print(f"T* = {Tstar}; tau = {tau:.4f}; {note}; {res['seconds']:.0f} s")


if __name__ == "__main__":
    main()
