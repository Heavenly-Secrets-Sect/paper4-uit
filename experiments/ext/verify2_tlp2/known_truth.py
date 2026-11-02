"""Verifier (tlp2, round 2): known-truth check of ext_tlp2 on D-07H development (true skeleton,
public view). Coverage / abs error of tlp2_db, tlp2_db90, tlp2_db_p3 vs truth, plus determinism
(content seed) and the cache-free property of tlp2_lp_cal. Writes results/ext_verify2_tlp2/known_truth.json."""
import json, sys, time, warnings
from pathlib import Path
import numpy as np
warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
import run_experiment as R
from paper4 import ext_tlp2
from paper4.ext_tlp import targeted_lp
from paper4.generator import build_dynamic_sem
from paper4.metrics import truth_effects
from paper4.skeleton import true_skeleton
from paper4.topology import load_bank

cfg = json.loads((ROOT / "experiments/configs/ext_tlp2_t80a.json").read_text())
gen = R.generator_config(cfg)
topos = load_bank("D-07H", "development")
H, lag_max = 4, 2
out = {"bank": "D-07H development", "cells": {}}
for T, units in ((150, [(i, r) for i in range(4) for r in range(2)]), (400, [(i, 0) for i in range(3)])):
    acc = {m: {"cov": [], "abserr": [], "half": []} for m in ("tlp2_db", "tlp2_db90", "tlp2_db_p3", "targeted_lp")}
    for i, r in units:
        sem = build_dynamic_sem(topos[i], gen, np.random.default_rng([987654, i, r]))
        _, C_t, _, _ = truth_effects(sem, H)
        nn = ~np.eye(sem.n, dtype=bool) & (np.abs(C_t) > 0.1)
        sk = R.public(true_skeleton(sem))
        d = sem.simulate(T, np.random.default_rng([987655, i, r, T]))
        res = {"tlp2_db": ext_tlp2.METHODS["tlp2_db"](d, sk, lag_max, H, 199, None),
               "tlp2_db90": ext_tlp2.METHODS["tlp2_db90"](d, sk, lag_max, H, 199, None),
               "tlp2_db_p3": ext_tlp2.METHODS["tlp2_db_p3"](d, sk, lag_max, H, 199, None),
               "targeted_lp": targeted_lp(d, sk, lag_max, H, 199, np.random.default_rng(1))}
        for m, x in res.items():
            if x.status != "ok":
                continue
            acc[m]["cov"].append(float(((x.lo <= C_t) & (C_t <= x.hi))[nn].mean()))
            acc[m]["abserr"].append(float(np.abs(x.C - C_t)[nn].mean()))
            acc[m]["half"].append(float(((x.hi - x.lo) / 2)[nn].mean()))
    out["cells"][f"T{T}"] = {m: {k: float(np.mean(v)) for k, v in a.items()} | {"n_units": len(a["cov"])} for m, a in acc.items()}
# determinism / cache
sem = build_dynamic_sem(topos[0], gen, np.random.default_rng([987654, 0, 0]))
sk = R.public(true_skeleton(sem)); d = sem.simulate(80, np.random.default_rng([1, 2]))
ext_tlp2._CACHE.clear()
a = ext_tlp2.METHODS["tlp2_db90"](d, sk, lag_max, H, 199, None)
ext_tlp2._CACHE.clear()
b = ext_tlp2.METHODS["tlp2_db"](d, sk, lag_max, H, 199, None)
c = ext_tlp2.METHODS["tlp2_db90"](d, sk, lag_max, H, 199, None)
l1 = ext_tlp2.METHODS["tlp2_lp_cal"](d, sk, lag_max, H, 199, np.random.default_rng(5))
l2 = ext_tlp2.METHODS["tlp2_lp_cal"](d, sk, lag_max, H, 199, np.random.default_rng(77))
out["determinism"] = {"db90_cold_eq_warm": bool(np.array_equal(a.lo, c.lo) and np.array_equal(a.hi, c.hi)),
                      "db_C_eq_db90_C": bool(np.array_equal(b.C, a.C)),
                      "db90_narrower": float(np.median(((a.hi - a.lo) / (b.hi - b.lo))[~np.eye(sem.n, dtype=bool)])),
                      "lp_cal_rng_independent": bool(np.array_equal(l1.lo, l2.lo) and np.array_equal(l1.hi, l2.hi))}
# does any tlp2 method read stated damage? flip damage and compare
sk2 = sk.copy(); sk2.damage = {"kind": "missing", "rate": 0.5, "k": 9}
ext_tlp2._CACHE.clear()
b2 = ext_tlp2.METHODS["tlp2_db"](d, sk2, lag_max, H, 199, None)
out["determinism"]["db_ignores_stated_damage"] = bool(np.array_equal(b.lo, b2.lo))
p = ROOT / "results/ext_verify2_tlp2"; p.mkdir(parents=True, exist_ok=True)
(p / "known_truth.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=1))
