"""Pre-screen (code path, exactness, timing). D-07H development ONLY, probe seed 7_740_000.
Not used for any decision.

1. Exactness: the recorder reproduces ext_v51.tolerant_v5_1 bit for bit (same rng seed, with and
   without the recorder) on 5 D-07H topologies x {missing-0.5, reversed-0.5} at T = 40.
2. Timing and code path: prepivot_core with reduced B_O = 5, B_I = 19 on the same 5 topologies,
   T in {40, 80}, cells none / missing-0.5 / reversed-0.5, and one full-size (39 x 19) dataset per T.
   (The proposed B_I = 1 fast double bootstrap cannot form the sd root, which needs >= 2 inner draws.)
Writes results/ext_r4prepivot_prescreen/prescreen.json.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import R, ROOT, run_dataset  # noqa: E402
from paper4 import ext_v51  # noqa: E402
from paper4.ext_r4prepivot import v51_recorded  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

CFG = json.loads((ROOT / "experiments/configs/ext_v51_eval.json").read_text(encoding="utf-8"))
CFG = dict(CFG, seed_base=7_740_000, name="ext_r4prepivot_prescreen")


def exactness(args):
    topo, t_idx, kind, rate = args
    gen = R.generator_config(CFG)
    unit = CFG["seed_base"] + 1000 * t_idx
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skel = R.public(R.unit_skeletons(sem, unit, CFG)[(kind, rate)])
    data = sem.simulate(40, np.random.default_rng([unit, 2, 40]))
    a = ext_v51.tolerant_v5_1(data, skel, 2, 4, 199, np.random.default_rng([unit, 9]))
    b, call = v51_recorded(data, skel, 2, 4, 199, np.random.default_rng([unit, 9]), keep=39)
    same = a.status == b.status and (a.status != "ok" or (np.array_equal(a.lo, b.lo) and np.array_equal(a.hi, b.hi)
                                                          and np.array_equal(a.C, b.C)))
    from paper4.estimator import percentile_interval
    lo0, hi0 = percentile_interval(call["draws"])
    mid, half = (lo0 + hi0) / 2, (hi0 - lo0) / 2
    unscaled_ok = bool(np.allclose(b.lo, mid - 0.5 * half) and np.allclose(b.hi, mid + 0.5 * half))
    return {"topology": topo.id, "kind": kind, "rate": rate, "identical": bool(same), "prescale_identity": unscaled_ok,
            "n_xs": len(call["xs"])}


def main():
    topos = load_bank("D-07H", "development")[:5]
    out = {"bank": "D-07H", "split": "development", "seed_base": CFG["seed_base"]}
    t0 = time.perf_counter()
    with ProcessPoolExecutor(3) as pool:
        out["exactness"] = list(pool.map(exactness, [(t, i, k, r) for i, t in enumerate(topos)
                                                     for k, r in (("missing", 0.5), ("reversed", 0.5))]))
        jobs = [(CFG, t, i, 0, T, k, r, "main", 5, 19) for i, t in enumerate(topos) for T in (40, 80)
                for k, r in (("none", 0.0), ("missing", 0.5), ("reversed", 0.5))]
        rows = [r for rs in pool.map(run_dataset, jobs) for r in rs]
        full = [(CFG, topos[0], 0, 0, T, "missing", 0.5, "main", 39, 19) for T in (40, 80)]
        full_rows = [r for rs in pool.map(run_dataset, full) for r in rs]
    out["reduced"] = [{k: r.get(k) for k in ("topology", "T", "kind", "rate", "method", "status", "info_f_d",
                                             "info_f_all", "info_n_inner_ok", "f_v51_eff", "coverage_nonnull",
                                             "iscore_nonnull_mean", "seconds_total", "seconds_outer", "seconds_inner")}
                      for r in rows]
    out["full_size"] = [{k: r.get(k) for k in ("topology", "T", "kind", "rate", "method", "status", "info_f_d",
                                               "info_f_all", "info_n_inner_ok", "info_n_roots", "f_v51_eff",
                                               "seconds_total", "seconds_outer", "seconds_inner")} for r in full_rows]
    out["seconds"] = round(time.perf_counter() - t0, 1)
    dst = ROOT / "results" / "ext_r4prepivot_prescreen"
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "prescreen.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({"exact": [e["identical"] for e in out["exactness"]],
                      "prescale": [e["prescale_identity"] for e in out["exactness"]],
                      "full": out["full_size"], "seconds": out["seconds"]}, indent=1))


if __name__ == "__main__":
    main()
