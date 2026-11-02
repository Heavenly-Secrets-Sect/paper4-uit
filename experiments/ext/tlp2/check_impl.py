"""Implementation checks of src/paper4/ext_tlp2.py on D-07H development (design probe, not the
evaluation bank). Writes results/ext_tlp2_checks/check_impl.json.

1. Batched skeleton-SVAR responses equal ext_tlp.var_responses (B = 1).
2. Horizon-specific LP at h = 0 equals the common-sample LP at h = 0 up to the sample; at large T
   both LP versions and the SVAR are close to the true IRF on the true skeleton.
3. Cache independence: tlp2_db90 called cold (cache cleared) equals tlp2_db90 after tlp2_db;
   tlp2_lp_cal called twice in different orders gives identical intervals.
4. Timing of one msdb call at T = 40 / 80 / 150 (B1 = 200, B2 = 100).
Usage: python experiments/ext/tlp2/check_impl.py
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from paper4 import ext_tlp, ext_tlp2  # noqa: E402
from paper4.estimator import parent_terms  # noqa: E402
from paper4.metrics import truth_effects  # noqa: E402
from paper4.skeleton import true_skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from run_experiment import generator_config  # noqa: E402

cfg = json.loads((ROOT / "experiments/configs/ext_tlp_eval.json").read_text())
gen = generator_config(cfg)
topos = load_bank("D-07H", "development")
out = {}
H, q = 4, gen.lag_max

# 1 + 2
topo = topos[0]
sem = build_dynamic_sem(topo, gen, np.random.default_rng([777, 0]))
skel = true_skeleton(sem)
theta_t, C_t, _, _ = truth_effects(sem, H)
T = 20000
x = sem.simulate(T, np.random.default_rng([777, 2]))
terms = [parent_terms(skel, j, q) for j in range(sem.n)]
parents = [sorted(u for u, v in skel.oriented if v == i) for i in range(sem.n)]
v_ref = ext_tlp.var_responses(x, terms, q, H)
v_bat = ext_tlp2.var_responses_batch(x[None], terms, q, H)[0]
out["var_batch_max_abs_diff"] = float(np.abs(v_ref - v_bat).max())
lp_c = ext_tlp.lp_responses(x, parents, 4, H)
lp_h = ext_tlp2.lp_responses_batch(x[None], parents, 4, H)[0]
out["lp_common_vs_horizon_max_abs_diff_T20000"] = float(np.nanmax(np.abs(lp_c - lp_h)))
out["lp_horizon_vs_truth_max_abs_T20000"] = float(np.nanmax(np.abs(lp_h - theta_t)))
out["var_vs_truth_max_abs_T20000"] = float(np.abs(v_bat - theta_t).max())

# 3 cache independence
sem2 = build_dynamic_sem(topos[1], gen, np.random.default_rng([778, 0]))
sk2 = true_skeleton(sem2)
d2 = sem2.simulate(80, np.random.default_rng([778, 2]))
ext_tlp2._CACHE.clear()
r_db = ext_tlp2._tlp2_db(d2, sk2, q, H, 199, None)
r_90a = ext_tlp2._tlp2_db90(d2, sk2, q, H, 199, None)
ext_tlp2._CACHE.clear()
r_90b = ext_tlp2._tlp2_db90(d2, sk2, q, H, 199, np.random.default_rng(1))
out["db90_cold_equals_warm"] = bool(np.array_equal(r_90a.lo, r_90b.lo) and np.array_equal(r_90a.hi, r_90b.hi))
out["db_and_db90_same_point"] = bool(np.array_equal(r_db.C, r_90a.C))
off = ~np.eye(sem2.n, dtype=bool)
out["db90_over_db95_width_ratio_median"] = float(np.median(((r_90a.hi - r_90a.lo) / (r_db.hi - r_db.lo))[off]))
a = ext_tlp2._tlp2_lp_cal(d2, sk2, q, H, 199, np.random.default_rng(5))
ext_tlp._CACHE.clear()
b = ext_tlp2._tlp2_lp_cal(d2, sk2, q, H, 199, np.random.default_rng(99))
out["lp_cal_order_independent"] = bool(np.array_equal(a.lo, b.lo))
out["db_info_T80"] = r_db.info

# 4 timing
timing = {}
for T in (40, 80, 150):
    d = sem2.simulate(T, np.random.default_rng([779, T]))
    t0 = time.perf_counter()
    r = ext_tlp2.msdb(d, sk2, q, H)
    timing[T] = {"seconds": round(time.perf_counter() - t0, 2), "status": r["status"],
                 "p_lp": r.get("info", {}).get("p_lp")}
out["timing_msdb_one_call"] = timing
print(json.dumps(out, indent=2))
dst = ROOT / "results/ext_tlp2_checks"
dst.mkdir(parents=True, exist_ok=True)
(dst / "check_impl.json").write_text(json.dumps(out, indent=2))
