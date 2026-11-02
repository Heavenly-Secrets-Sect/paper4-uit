"""Probe 6 (exploratory, D-07H development, uncalibrated): guard and bootstrap variants.
Usage: probe_guard.py N_TOPO N_BOOT KIND"""
import sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4 import methods as M, ext_eiv as E  # noqa
from paper4.generator import GeneratorConfig, add_measurement_noise, build_dynamic_sem  # noqa
from paper4.metrics import evaluate  # noqa
from paper4.skeleton import damage, true_skeleton  # noqa
from paper4.topology import load_bank  # noqa
n_topo, n_boot, kind = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 888
gen = GeneratorConfig(); topos = load_bank("D-07H", "development")[:n_topo]
def run(y, sk, guard, reest, g=0.9):
    E.GUARD_MODE, E.BOOT_REESTIMATE, E.GUARD = guard, reest, g
    return E._eiv(y, sk, 2, 4, n_boot, np.random.default_rng(4), tolerant=True, name="x")
V0 = {"v3": lambda y, sk: M.tolerant_v3(y, sk, 2, 4, n_boot, np.random.default_rng(3)),
     "A_ratio_re": lambda y, sk: run(y, sk, "ratio", True),
     "B_ratio_fix": lambda y, sk: run(y, sk, "ratio", False),
     "C_minus1_re": lambda y, sk: run(y, sk, "minus1", True)}
V = V0 if (len(sys.argv) <= 5 or sys.argv[5] != "g") else {
     "v3": V0["v3"],
     "G0.5": lambda y, sk: run(y, sk, "ratio", True, 0.5),
     "G0.7": lambda y, sk: run(y, sk, "ratio", True, 0.7)}
agg = defaultdict(list)
for t_idx, topo in enumerate(topos):
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([seed, t_idx]))
    sk = true_skeleton(sem)
    if kind != "none":
        coef = {e: float(sem.B[lag, e[1], e[0]]) for e, lag in sem.edge_lag.items()}
        sk = damage(sk, kind, 0.2, np.random.default_rng([seed, t_idx, 9]), sem.edge_lag, coef)
    for T in (80, 150):
        x = sem.simulate(T, np.random.default_rng([seed, t_idx, T, 1]))
        for ratio in (0.0, 0.3):
            y = add_measurement_noise(x, ratio, np.random.default_rng([seed, t_idx, T, 2]))
            for name, f in V.items():
                res = f(y, sk); row = evaluate(sem, res, 4)
                if res.status == "ok":
                    agg[(T, ratio, name)].append((row["n_covered_nonnull"], row["n_nonnull"], row["iscore_nonnull_mean"], row["width_kept"], row["C_abs_err_nonnull"]))
for key in sorted(agg):
    a = np.array(agg[key])
    print(f"{kind} T={key[0]} ratio={key[1]} {key[2]:12s} n={len(a)} cov={a[:,0].sum()/a[:,1].sum():.3f} IS={a[:,2].mean():.2f} width={np.median(a[:,3]):.2f} abserr={np.median(a[:,4]):.3f}")
