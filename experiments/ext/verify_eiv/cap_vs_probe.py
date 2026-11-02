"""Skeptic check (exploratory, D-07H development, same seeds as eiv probe 2 = 777):
does the evaluated estimator (ext_eiv.estimate_noise_share, with the admissibility cap
r <= min_j lambda_j) give the same r_hat as the probe-2 estimator (noise_est.gmm_common, no cap)?"""
import sys; sys.path.insert(0, "src"); sys.path.insert(0, "experiments/ext/eiv")
import warnings; warnings.filterwarnings("ignore")
import numpy as np
from paper4.estimator import parent_terms
from paper4.generator import GeneratorConfig, add_measurement_noise, build_dynamic_sem
from paper4.skeleton import true_skeleton
from paper4.topology import load_bank
from paper4.ext_eiv import estimate_noise_share, _lambda_min
from noise_est import gmm_common
gen = GeneratorConfig(); topos = load_bank("D-07H", "development")[:12]
for T in [int(a) for a in sys.argv[1:]] or (80, 150):
    for ratio in (0.1, 0.3):
        a, b, lmin, capped = [], [], [], 0
        for t_idx, topo in enumerate(topos):
            sem = build_dynamic_sem(topo, gen, np.random.default_rng([777, t_idx]))
            sk = true_skeleton(sem)
            x = sem.simulate(T, np.random.default_rng([777, t_idx, T, 1]))
            y = add_measurement_noise(x, ratio, np.random.default_rng([777, t_idx, T, 2]))
            terms = [parent_terms(sk, j, 2) for j in range(sk.n)]
            ra, crit = estimate_noise_share(y, terms, 2)
            rb, _ = gmm_common(y, terms, 2, 2)
            # min lambda over equations, on the same rows as estimate_noise_share
            rows = np.arange(4, T); m = len(rows); var = y.var(0); lams = []
            for j, tj in enumerate(terms):
                X = np.column_stack([y[rows - lag, i] for i, lag in tj]); X = X - X.mean(0)
                lams.append(_lambda_min(X.T @ X, m * np.diag(var[[i for i, _ in tj]])))
            a.append(ra); b.append(rb); lmin.append(min(lams))
            capped += int(np.isfinite(crit).sum() < len(crit) and ra >= min(lams) - 0.0101)
        print(f"T={T} ratio={ratio} share={ratio/(1+ratio):.3f} n={sk.n}: eval estimator {np.mean(a):.3f} | probe2 gmm_common {np.mean(b):.3f} | "
              f"mean min-lambda {np.mean(lmin):.3f} | runs where r_hat sits at the cap {capped}/{len(a)}", flush=True)
