"""Probe 1 (exploratory, D-07H development): can the noise share be estimated from the data?"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from paper4.generator import GeneratorConfig, add_measurement_noise, build_dynamic_sem  # noqa
from paper4.topology import load_bank  # noqa
from noise_est import common_ratio, per_series  # noqa

gen = GeneratorConfig()
topos = load_bank("D-07H", "development")[:10]
mode = sys.argv[1] if len(sys.argv) > 1 else "common"
for m in (2, 4):
    for T in (80, 150):
        for ratio in (0.0, 0.1, 0.3):
            est = []
            for t_idx, topo in enumerate(topos):
                sem = build_dynamic_sem(topo, gen, np.random.default_rng([777, t_idx]))
                x = sem.simulate(T, np.random.default_rng([777, t_idx, T, 1]))
                y = add_measurement_noise(x, ratio, np.random.default_rng([777, t_idx, T, 2]))
                if mode == "common":
                    est.append(common_ratio(y, 2, m))
                else:
                    est.append(per_series(y, 2, m).mean())
            true_share = ratio / (1 + ratio)
            print(f"m={m} T={T} ratio={ratio} true share={true_share:.3f} est mean={np.mean(est):.3f} sd={np.std(est):.3f}")
