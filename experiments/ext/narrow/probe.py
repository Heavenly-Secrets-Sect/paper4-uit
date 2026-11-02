"""Exploratory probe for the "narrow" direction, on the CALIBRATION bank (D-07H development) only.

For each variant, the interval is rescaled by the factor c* that brings pooled coverage of the
missing cells (rates 0.2 and 0.5 pooled, as the runner calibrates per stated kind) to 0.95 on this
same probe sample, grid 0.5..5 step 0.05. Reported: raw coverage (c = 1), c*, and per cell the
coverage and mean interval score at c*. This mimics what the width calibration will do; it is
optimistic for every variant equally. D-07 is never touched.

Run: python experiments/ext/narrow/probe.py --topos 10 --nboot 99 --workers 3 --out <json>
"""
import argparse, json, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4 import methods as M
from paper4.ext_narrow import tolerant_sel
from paper4.generator import GeneratorConfig, build_dynamic_sem
from paper4.metrics import truth_effects
from paper4.skeleton import damage, true_skeleton
from paper4.topology import load_bank

GEN = GeneratorConfig(lag_max=2, q0=0.3, cross_coef=(0.3, 0.8), self_coef=(0.2, 0.6), noise_var=(0.5, 1.5),
                      rho_max=0.9, burn_in=200)
VARIANTS = {
    "v3_all": None,
    "m2_a05_fixed": dict(mult=2.0, alpha_open=0.05, reselect=False),
    "m2_a05_resel": dict(mult=2.0, alpha_open=0.05, reselect=True),
    "m3_a10_resel": dict(mult=3.0, alpha_open=0.10, reselect=True),
    "m1_a01_resel": dict(mult=1.0, alpha_open=0.01, reselect=True),
    "m2_a20_resel": dict(mult=2.0, alpha_open=0.20, reselect=True),
    "m4_a05_resel": dict(mult=4.0, alpha_open=0.05, reselect=True),
}


def unit(args):
    t_idx, topo, Ts, nboot, kinds, variants = args
    seed = 7_700_000 + t_idx
    sem = build_dynamic_sem(topo, GEN, np.random.default_rng([seed, 0]))
    truth = true_skeleton(sem)
    _, C_true, _, _ = truth_effects(sem, 4)
    nonnull = ~np.eye(sem.n, dtype=bool) & (np.abs(C_true) > 0.1)
    out = []
    for T in Ts:
        data = sem.simulate(T, np.random.default_rng([seed, 2, T]))
        for kind, rate in kinds:
            skel = damage(truth, kind, rate, np.random.default_rng([seed, 1, kind == "missing"]), sem.edge_lag)
            for v_idx, name in enumerate(variants):
                kw = VARIANTS[name]
                rng = np.random.default_rng([seed, 3, T, v_idx, int(rate * 10)])
                t0 = time.perf_counter()
                if kw is None:
                    r = M.tolerant_v3(data, skel, 2, 4, nboot, rng)
                else:
                    r = tolerant_sel(data, skel, 2, 4, nboot, rng, name=name, **kw)
                sec = time.perf_counter() - t0
                if r.status != "ok":
                    out.append({"T": T, "kind": kind, "rate": rate, "v": name, "status": r.status})
                    continue
                mid, half = (r.lo + r.hi) / 2, (r.hi - r.lo) / 2
                out.append({"T": T, "kind": kind, "rate": rate, "v": name, "status": "ok", "sec": sec,
                            "dist": np.abs(C_true - mid)[nonnull].tolist(), "half": half[nonnull].tolist(),
                            "n_nan": int(np.isnan(half).sum()), "n_open": r.info.get("n_open"), "n_open_boot": r.info.get("n_open_boot_mean")})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topos", type=int, default=10)
    ap.add_argument("--nboot", type=int, default=99)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--T", type=int, nargs="+", default=[40, 80, 150])
    ap.add_argument("--variants", nargs="+", default=list(VARIANTS))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    topos = load_bank("D-07H", "development")[: a.topos]
    kinds = [("missing", 0.2), ("missing", 0.5)]
    jobs = [(i, t, a.T, a.nboot, kinds, a.variants) for i, t in enumerate(topos)]
    rows = []
    t0 = time.perf_counter()
    with ProcessPoolExecutor(a.workers) as pool:
        for o in pool.map(unit, jobs):
            rows.extend(o)
    grid = np.round(np.arange(0.5, 5.001, 0.05), 3)
    report = []
    for T in a.T:
        for v in a.variants:
            rs = [r for r in rows if r["T"] == T and r["v"] == v and r["status"] == "ok"]
            nfail = sum(1 for r in rows if r["T"] == T and r["v"] == v and r["status"] != "ok")
            if not rs:
                report.append({"T": T, "v": v, "fail": nfail}); continue
            d = np.concatenate([r["dist"] for r in rs]); h = np.concatenate([r["half"] for r in rs])
            cov = np.array([(d <= c * h).mean() for c in grid])
            c = float(grid[np.argmax(cov >= min(0.95, cov.max() - 0.005))])
            entry = {"T": T, "v": v, "fail": nfail, "raw_cov": float((d <= h).mean()), "c_star": c,
                     "sec": float(np.mean([r["sec"] for r in rs])), "n_nan": int(sum(r["n_nan"] for r in rs))}
            for rate in (0.2, 0.5):
                rr = [r for r in rs if r["rate"] == rate]
                ds = [np.array(r["dist"]) for r in rr]; hs = [np.array(r["half"]) for r in rr]
                IS = np.mean([np.mean(2 * c * hh + 40 * np.maximum(dd - c * hh, 0)) for dd, hh in zip(ds, hs)])
                cv = np.concatenate(ds) <= c * np.concatenate(hs)
                entry[f"cov{rate}"] = float(cv.mean()); entry[f"IS{rate}"] = float(IS)
                entry[f"width{rate}"] = float(np.median(2 * c * np.concatenate(hs)))
                entry[f"n_open{rate}"] = float(np.mean([r["n_open"] for r in rr])) if rr and rr[0]["n_open"] is not None else None
            report.append(entry)
            print(json.dumps(entry))
    Path(a.out).write_text(json.dumps({"args": vars(a), "seconds": time.perf_counter() - t0, "report": report}, indent=1))


if __name__ == "__main__":
    main()
