"""Diagnostic (exploratory, D-07H development): why is tolerant_eiv wide in the missing cell?
Forces r to fixed values via monkeypatching estimate_noise_share."""
import sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4 import methods as M, ext_eiv as E  # noqa
from paper4.generator import GeneratorConfig, add_measurement_noise, build_dynamic_sem  # noqa
from paper4.metrics import evaluate  # noqa
from paper4.skeleton import damage, true_skeleton  # noqa
from paper4.topology import load_bank  # noqa
gen = GeneratorConfig(); topos = load_bank("D-07H", "development")[:4]
orig = E.estimate_noise_share
for fixed in (None, 0.0, 0.03):
    if fixed is not None:
        E.estimate_noise_share = lambda d, t, p, grid=E.R_GRID, f=fixed: (f, None)
    else:
        E.estimate_noise_share = orig
    res_all = []
    for t_idx, topo in enumerate(topos):
        sem = build_dynamic_sem(topo, gen, np.random.default_rng([888, t_idx]))
        coef = {e: float(sem.B[lag, e[1], e[0]]) for e, lag in sem.edge_lag.items()}
        sk = damage(true_skeleton(sem), "missing", 0.2, np.random.default_rng([888, t_idx, 9]), sem.edge_lag, coef)
        x = sem.simulate(80, np.random.default_rng([888, t_idx, 80, 1]))
        a = E._eiv(x, sk, 2, 4, 99, np.random.default_rng(4), tolerant=True, name="t", bias_correct=False)
        b = M.tolerant_v3(x, sk, 2, 4, 99, np.random.default_rng(3))
        ra, rb = evaluate(sem, a, 4), evaluate(sem, b, 4)
        res_all.append((ra["width_kept"], rb["width_kept"], a.info["n_repair"], b.info["n_repair"]))
    print(fixed, np.round(res_all, 2).tolist())
