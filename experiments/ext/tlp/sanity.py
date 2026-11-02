"""Sanity and timing checks for ext_tlp on the CALIBRATION bank (D-07H development) only.

1. With the true skeleton and large T, LP, the skeleton SVAR and TLP all recover the true IRF.
2. With a missing-0.5 skeleton, the target is biased and the weight on LP should rise with T.
3. Seconds per call at T = 40/80/150 (n_boot = 199).
"""
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4 import ext_tlp as X  # noqa: E402
from paper4.generator import GeneratorConfig, build_dynamic_sem  # noqa: E402
from paper4.metrics import truth_effects  # noqa: E402
from paper4.skeleton import damage, true_skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

gen = GeneratorConfig()
topos = load_bank("D-07H", "development")
H = 4
for t_idx in range(2):
    sem = build_dynamic_sem(topos[t_idx], gen, np.random.default_rng([99, t_idx]))
    theta_t, C_t, _, _ = truth_effects(sem, H)
    off = ~np.eye(sem.n, dtype=bool)
    sk = true_skeleton(sem)
    miss = damage(sk, "missing", 0.5, np.random.default_rng([99, t_idx, 1]), sem.edge_lag)
    for T in (2000,):
        x = sem.simulate(T, np.random.default_rng([99, t_idx, T]))
        for lab, s in (("true", sk), ("miss0.5", miss)):
            parents, p, terms = X._setup(x, s, 2, H)
            lp = X.lp_responses(x, parents, p, H)
            va = X.var_responses(x, terms, 2, H)
            print(f"topo{t_idx} T={T} {lab}: max|LP-truth|={np.abs(lp - theta_t).max():.3f} "
                  f"max|VAR-truth|={np.abs(va - theta_t).max():.3f} p={p}")
    for T in (40, 80, 150):
        x = sem.simulate(T, np.random.default_rng([7, t_idx, T]))
        for lab, s in (("true", sk), ("miss0.5", miss)):
            t0 = time.perf_counter()
            r = X.targeted_lp(x, s, 2, H, 199, np.random.default_rng(1))
            dt = time.perf_counter() - t0
            if r.status != "ok":
                print(T, lab, r.status); continue
            nn = off & (np.abs(C_t) > 0.1)
            cov = np.mean((r.lo <= C_t) & (C_t <= r.hi), where=nn)
            print(f"topo{t_idx} T={T} {lab}: {dt:.2f}s cov={cov:.2f} width={np.median((r.hi-r.lo)[nn]):.2f} "
                  f"abs_err={np.median(np.abs(r.C-C_t)[nn]):.3f} info={r.info}")
