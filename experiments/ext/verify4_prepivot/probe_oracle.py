"""Skeptic probe (D-07H development only, seed_base 7_760_000): in the bootstrap world vs the real world.
For each dataset: prepivot_core -> f_d; unscaled outer interval; the oracle factor f* needed for 0.95 pooled
non-null coverage (grid over f, using the TRUE C via metrics.evaluate -- evaluation only); the ratio
percentile half-width / (z * sd of outer draws) on non-null pairs. Writes results/ext_verify4_prepivot/probe_oracle.json."""
import json, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
sys.path.insert(0, "/Users/kietnt/Desktop/Workspace/Paper4_UIT/experiments/ext/r4prepivot")
from common import R, ROOT, evaluate, build_dynamic_sem, M  # noqa
from paper4 import ext_r4prepivot as P
from paper4.methods import MethodResult
from paper4.topology import load_bank
GRID = np.round(np.arange(0.6, 2.01, 0.05), 2)

def job(a):
    kind, rate, T, t_idx = a
    cfg = json.loads((ROOT / "experiments/configs/ext_v51_eval.json").read_text())
    cfg["seed_base"] = 7_760_000
    topo = load_bank("D-07H", "development")[t_idx]
    unit = cfg["seed_base"] + 1000 * t_idx
    gen = R.generator_config(cfg)
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skel = R.public(R.unit_skeletons(sem, unit, cfg)[(kind, rate)])
    data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
    rng = np.random.default_rng([unit, 3, T, 99])
    # outer draws (recorded) for sd ratio
    res, call = P.v51_recorded(data, skel, gen.lag_max, cfg["H"], cfg["n_boot"], np.random.default_rng([unit, 3, T, 99]), keep=0)
    core = P.prepivot_core(data, skel, gen.lag_max, cfg["H"], cfg["n_boot"], rng)
    if core["status"] != "ok":
        return {"kind": kind, "T": T, "t_idx": t_idx, "status": core["status"]}
    f = P.factors(core)
    v = core["v51"]
    lo0, hi0 = core["lo0"], core["hi0"]
    cov = {}
    for g in GRID:
        lo, hi = P.widen(lo0, hi0, g)
        row = evaluate(sem, MethodResult("x", "ok", v.C, lo, hi, v.theta, v.B, {}), cfg["H"], tau_effect=cfg["tau_effect"])
        cov[str(g)] = [row["n_covered_nonnull"], row["n_nonnull"]]
    d = call["draws"]
    C0 = P.cumulative(P.irf(call["fit"].B, cfg["H"]), cfg["H"]) if hasattr(P, "cumulative") else None
    sd = d.std(axis=0, ddof=1); half = (hi0 - lo0) / 2
    off = ~np.eye(d.shape[1], dtype=bool)
    m = off & (np.abs(C0) > 0.1) & (sd > 1e-9)
    ratio = float(np.median(half[m] / (P.Z * sd[m])))
    return {"kind": kind, "rate": rate, "T": T, "t_idx": t_idx, "status": "ok", "f_pp": f["pp"], "f_orig": f["orig"],
            "cov": cov, "pct_half_over_1.96sd_median": ratio}

if __name__ == "__main__":
    cells = [("none", 0.0, 80), ("missing", 0.5, 80), ("none", 0.0, 40)]
    jobs = [(k, r, T, i) for (k, r, T) in cells for i in range(20)]
    with ProcessPoolExecutor(2) as ex:
        out = list(ex.map(job, jobs, chunksize=1))
    summ = {}
    for (k, r, T) in cells:
        rs = [o for o in out if o["kind"] == k and o["T"] == T and o["status"] == "ok"]
        pooled = {g: sum(o["cov"][str(g)][0] for o in rs) / max(1, sum(o["cov"][str(g)][1] for o in rs)) for g in GRID}
        fstar = next((float(g) for g in GRID if pooled[g] >= 0.95), None)
        fpp = float(np.median([o["f_pp"] for o in rs]))
        # coverage at the per-dataset f_pp (nearest grid point) -- pooled
        def cov_at(o, fv):
            g = GRID[np.argmin(np.abs(GRID - fv))]; return o["cov"][str(g)]
        c_pp = sum(cov_at(o, o["f_pp"])[0] for o in rs) / sum(cov_at(o, o["f_pp"])[1] for o in rs)
        summ[f"{k}|{r}|T{T}"] = {"n": len(rs), "f_star_pooled_0.95": fstar, "f_pp_median": fpp,
                                 "cov_at_f_pp_nearest_grid": c_pp, "pooled_cov_curve": {str(g): round(pooled[g], 4) for g in GRID},
                                 "pct_half_over_1.96sd_median": float(np.median([o["pct_half_over_1.96sd_median"] for o in rs]))}
    dst = Path("/Users/kietnt/Desktop/Workspace/Paper4_UIT/results/ext_verify4_prepivot"); dst.mkdir(parents=True, exist_ok=True)
    (dst / "probe_oracle.json").write_text(json.dumps({"summary": summ, "runs": out}, indent=1))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "pooled_cov_curve"} for k, v in summ.items()}, indent=1))
