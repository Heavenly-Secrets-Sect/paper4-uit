"""Compute budget per method (D-07H development ONLY; no D-07 data). For a few calibration-bank units, built
exactly as the runner's calibration phase builds them (unit = seed_base + 500000 + 1000 * t_idx + rep, a2 kinds
list), fit every envelope method once per (T, missing rate) in ONE process and record wall seconds and
bootstrap draws per call. Also checks that pselect_union_v3 and _v3_cal share draws and that the method output
does not change when the stated damage is removed (it must not read it).

Usage: python experiments/ext/baselines3/timing.py [n_topologies]  -> results/ext_baselines3_budget/timing.json
"""
import json, os, sys, time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
import run_experiment as R
from paper4 import methods as M
from paper4.generator import build_dynamic_sem
from paper4.topology import load_bank

CFG = json.loads((ROOT / "experiments/configs/ext_baselines2_eval.json").read_text())
NAMES = ["tolerant_v4", "tolerant_v5_1", "pselect_union_v3", "pselect_cal", "fullvar_cal", "targeted_lp",
         "tlp2_db_p3", "bvar_minnesota_v2"]
DRAWS = {"tolerant_v4": "199 bootstrap refits (repair/orientation redrawn per draw)",
         "tolerant_v5_1": "199 bootstrap refits with lag re-selection per draw",
         "pselect_union_v3": "199 per orientation member; see info n_draws",
         "pselect_cal": "<=16 graphs x max(10, 199 // n_graphs) draws (round-1 pselect_union)",
         "fullvar_cal": "199 bootstrap refits",
         "targeted_lp": "199 single-level VAR-sieve draws (cal shares them)",
         "tlp2_db_p3": "MSDB B1 = 200 first-level x B2 = 100 second-level draws",
         "bvar_minnesota_v2": "199 posterior draws (cal shares them)"}


def main():
    n_topo = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    out = ROOT / "results/ext_baselines3_budget"; out.mkdir(parents=True, exist_ok=True)
    gen = R.generator_config(CFG); ext = R.ext_methods()
    topos = load_bank("D-07H", "development")[:n_topo]
    frozen = json.loads((ROOT / "experiments/calibration/tolerant_v4_frozen.json").read_text())
    rec, checks = [], []
    load0 = os.getloadavg()
    for t_idx, topo in enumerate(topos):
        unit = CFG["seed_base"] + 500_000 + 1000 * t_idx
        sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
        skels = R.unit_skeletons(sem, unit, CFG)
        for T in (80, 150):
            data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
            for rate in (0.2, 0.5):
                skel = R.public(skels[("missing", rate)])
                for name in NAMES:
                    rng = np.random.default_rng([unit, 3, T, 9, 1])
                    t0 = time.perf_counter()
                    if name == "tolerant_v4":
                        res = M.calibrate_width(M.tolerant_v3(data, skel, gen.lag_max, CFG["H"], 199, rng),
                                                frozen[f"mod|{T}|missing"], "tolerant_v4")
                    else:
                        res = ext[name](data, skel, gen.lag_max, CFG["H"], 199, rng)
                    sec = time.perf_counter() - t0
                    rec.append({"topology": topo.id, "T": T, "rate": rate, "method": name, "status": res.status,
                                "seconds": round(sec, 3), **{f"info_{k}": v for k, v in res.info.items()
                                                             if k in ("n_draws", "n_graphs", "n_members", "n_members_ok")}})
                    print(rec[-1], flush=True)
                # v3 / v3_cal share draws; v3 ignores stated damage
                a = ext["pselect_union_v3"](data, skel, gen.lag_max, CFG["H"], 199, None)
                b = ext["pselect_union_v3_cal"](data, skel, gen.lag_max, CFG["H"], 199, None)
                s2 = skel.copy(); s2.damage = {}
                from paper4 import ext_baselines3 as E3
                E3._CACHE.clear()
                c = ext["pselect_union_v3"](data, s2, gen.lag_max, CFG["H"], 199, None)
                mid_a, mid_b = (a.lo + a.hi) / 2, (b.lo + b.hi) / 2
                checks.append({"topology": topo.id, "T": T, "rate": rate,
                               "cal_same_mid": bool(np.allclose(mid_a, mid_b)),
                               "cal_half_ratio": float(np.nanmedian(((b.hi - b.lo) / np.where(a.hi > a.lo, a.hi - a.lo, np.nan)))),
                               "blind_to_stated_damage": bool(np.array_equal(a.lo, c.lo) and np.array_equal(a.hi, c.hi))})
    summ = {}
    for name in NAMES:
        for T in (80, 150):
            g = [r for r in rec if r["method"] == name and r["T"] == T]
            summ[f"{name}|{T}"] = {"median_seconds": float(np.median([r["seconds"] for r in g])),
                                   "mean_seconds": float(np.mean([r["seconds"] for r in g])),
                                   "draws": DRAWS[name],
                                   "mean_info_n_draws": (float(np.mean([r["info_n_draws"] for r in g if "info_n_draws" in r]))
                                                         if any("info_n_draws" in r for r in g) else None),
                                   "n_calls": len(g)}
    res = {"bank": "D-07H development (calibration-phase units)", "n_topologies": n_topo,
           "loadavg_start": load0, "loadavg_end": os.getloadavg(), "single_process": True,
           "summary": summ, "checks": checks, "calls": rec}
    (out / "timing.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(summ, indent=1)); print(json.dumps(checks, indent=1))


if __name__ == "__main__":
    main()
