"""Probe 2 (exploratory, D-07H development): GMM noise share on skeleton-restricted equations."""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from paper4.estimator import parent_terms, soft_terms  # noqa
from paper4.generator import GeneratorConfig, add_measurement_noise, build_dynamic_sem  # noqa
from paper4.skeleton import damage, true_skeleton  # noqa
from paper4.topology import load_bank  # noqa
from noise_est import gmm_common  # noqa

gen = GeneratorConfig()
topos = load_bank("D-07H", "development")[:12]
kind = sys.argv[1] if len(sys.argv) > 1 else "none"
mode = sys.argv[2] if len(sys.argv) > 2 else "plugin"
L = int(sys.argv[3]) if len(sys.argv) > 3 else 2
for T in (80, 150):
    for ratio in (0.0, 0.1, 0.3):
        est = []
        for t_idx, topo in enumerate(topos):
            sem = build_dynamic_sem(topo, gen, np.random.default_rng([777, t_idx]))
            sk = true_skeleton(sem)
            if kind != "none":
                coef = {e: float(sem.B[lag, e[1], e[0]]) for e, lag in sem.edge_lag.items()}
                sk = damage(sk, kind, 0.2, np.random.default_rng([777, t_idx, 9]), sem.edge_lag, coef)
            x = sem.simulate(T, np.random.default_rng([777, t_idx, T, 1]))
            y = add_measurement_noise(x, ratio, np.random.default_rng([777, t_idx, T, 2]))
            tf = soft_terms if mode == "full" else parent_terms
            terms = [tf(sk, j, 2) for j in range(sk.n)]
            r, _ = gmm_common(y, terms, 2, L)
            est.append(r)
        print(f"{kind} {mode} L={L} T={T} ratio={ratio} true share={ratio/(1+ratio):.3f} est mean={np.mean(est):.3f} sd={np.std(est):.3f} med={np.median(est):.3f}")
