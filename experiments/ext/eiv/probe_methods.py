"""Probe 3 (exploratory, D-07H development, uncalibrated): coverage / IS / abs err of the corrected
methods against their uncorrected counterparts. Usage: probe_methods.py N_TOPO N_BOOT KIND"""
import sys, time
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from paper4 import methods as M  # noqa
from paper4.ext_eiv import plugin_eiv, tolerant_eiv  # noqa
from paper4.generator import GeneratorConfig, add_measurement_noise, build_dynamic_sem  # noqa
from paper4.metrics import evaluate  # noqa
from paper4.skeleton import damage, true_skeleton  # noqa
from paper4.topology import load_bank  # noqa

n_topo, n_boot, kind = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
gen = GeneratorConfig()
topos = load_bank("D-07H", "development")[:n_topo]
agg = defaultdict(list)
tm = defaultdict(float)
for t_idx, topo in enumerate(topos):
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([888, t_idx]))
    sk = true_skeleton(sem)
    if kind != "none":
        coef = {e: float(sem.B[lag, e[1], e[0]]) for e, lag in sem.edge_lag.items()}
        sk = damage(sk, kind, 0.2, np.random.default_rng([888, t_idx, 9]), sem.edge_lag, coef)
    for T in (80, 150):
        x = sem.simulate(T, np.random.default_rng([888, t_idx, T, 1]))
        for ratio in (0.0, 0.1, 0.3):
            y = add_measurement_noise(x, ratio, np.random.default_rng([888, t_idx, T, 2]))
            fns = {"plugin": lambda: M.plugin(y, sk, 2, 4, n_boot, np.random.default_rng(1)),
                   "plugin_eiv": lambda: plugin_eiv(y, sk, 2, 4, n_boot, np.random.default_rng(2)),
                   "tolerant_v3": lambda: M.tolerant_v3(y, sk, 2, 4, n_boot, np.random.default_rng(3)),
                   "tolerant_eiv": lambda: tolerant_eiv(y, sk, 2, 4, n_boot, np.random.default_rng(4))}
            for name, f in fns.items():
                t0 = time.perf_counter(); res = f(); tm[name] += time.perf_counter() - t0
                row = evaluate(sem, res, 4)
                if res.status != "ok":
                    agg[(T, ratio, name)].append(None); continue
                agg[(T, ratio, name)].append((row["n_covered_nonnull"], row["n_nonnull"], row["iscore_nonnull_mean"],
                                              row["width_kept"], row["C_abs_err_nonnull"], res.info.get("r_used", np.nan), res.info.get("r_boot_mean", np.nan)))
for key in sorted(agg):
    v = [r for r in agg[key] if r is not None]
    a = np.array(v)
    print(f"T={key[0]} ratio={key[1]} {key[2]:13s} ok={len(v)}/{len(agg[key])} cov={a[:,0].sum()/a[:,1].sum():.3f} "
          f"IS={a[:,2].mean():.2f} width={np.median(a[:,3]):.2f} abserr={np.median(a[:,4]):.3f} r_used={np.nanmean(a[:,5]):.3f} r_boot={np.nanmean(a[:,6]):.3f}")
print({k: round(v, 1) for k, v in tm.items()})
