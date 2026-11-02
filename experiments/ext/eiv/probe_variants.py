"""Probe 4/5 (exploratory, D-07H development, uncalibrated): variants of the eiv module.
Usage: probe_variants.py N_TOPO N_BOOT KIND"""
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
V = {"v3": lambda y, sk: M.tolerant_v3(y, sk, 2, 4, n_boot, np.random.default_rng(3)),
     "eiv_nobc": lambda y, sk: E._eiv(y, sk, 2, 4, n_boot, np.random.default_rng(4), tolerant=True, name="a", bias_correct=False),
     "eiv_bc": lambda y, sk: E._eiv(y, sk, 2, 4, n_boot, np.random.default_rng(4), tolerant=True, name="b", bias_correct=True)}
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
                    agg[(T, ratio, name)].append((row["n_covered_nonnull"], row["n_nonnull"], row["iscore_nonnull_mean"], row["width_kept"], res.info.get("r_used", np.nan)))
for key in sorted(agg):
    a = np.array(agg[key])
    print(f"{kind} T={key[0]} ratio={key[1]} {key[2]:9s} n={len(a)} cov={a[:,0].sum()/a[:,1].sum():.3f} IS={a[:,2].mean():.2f} width={np.median(a[:,3]):.2f} r_used={np.nanmean(a[:,4]):.3f}")
