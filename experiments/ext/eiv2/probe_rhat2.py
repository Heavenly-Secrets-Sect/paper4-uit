"""Design probe 1b (eiv2; D-07H development only, seed 4242 as probe 1; never D-07): r_hat of
admissibility mode x criterion: global/corr (round 1), pereq/corr (v2 default), pereq/liml,
free/liml. Same data as probe_rhat.py. Usage: probe_rhat2.py > results/ext_eiv2_probes/rhat2.txt"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(Path(__file__).parent))
import warnings; warnings.filterwarnings("ignore")
from paper4.estimator import parent_terms  # noqa
from paper4.ext_eiv2 import estimate_noise_share_v2  # noqa
from paper4.generator import GeneratorConfig, add_measurement_noise, build_dynamic_sem  # noqa
from paper4.skeleton import damage, true_skeleton  # noqa
from paper4.topology import load_bank  # noqa
from hetero import add_hetero_noise  # noqa

gen = GeneratorConfig()
topos = load_bank("D-07H", "development")
SEED = 4242
V = [("global", "corr"), ("pereq", "corr"), ("pereq", "liml"), ("free", "liml")]
res = {}
for t_idx, topo in enumerate(topos):
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([SEED, t_idx]))
    truth = true_skeleton(sem)
    coef = {e: float(sem.B[lag, e[1], e[0]]) for e, lag in sem.edge_lag.items()}
    skels = {"true": truth,
             "missing": damage(truth, "missing", 0.2, np.random.default_rng([SEED, t_idx, 9]), sem.edge_lag, coef)}
    for T in (80, 150):
        x = sem.simulate(T, np.random.default_rng([SEED, t_idx, T, 1]))
        for sc in ("hom0", "hom0.1", "hom0.3", "het0.3"):
            ratio = float(sc[3:])
            rng = np.random.default_rng([SEED, t_idx, T, 2])
            if sc.startswith("hom"):
                y = add_measurement_noise(x, ratio, rng); share = ratio / (1 + ratio)
            else:
                y, rs = add_hetero_noise(x, ratio, rng); share = float(np.mean(rs / (1 + rs)))
            for sk_name, sk in skels.items():
                terms = [parent_terms(sk, j, 2) for j in range(sk.n)]
                for mode, ck in V:
                    r, _, d = estimate_noise_share_v2(y, terms, 2, mode=mode, crit_kind=ck)
                    res.setdefault((T, sc, sk_name, mode, ck), []).append((r, share))
print(f"# probe_rhat2: D-07H development, {len(topos)} topologies, seed {SEED}; mean (sd) [RMSE vs true share] of r_hat")
print("| T | scenario | skeleton | true share | " + " | ".join(f"{m}/{c}" for m, c in V) + " |")
print("|---|---|---|---|" + "---|" * len(V))
for T in (80, 150):
    for sc in ("hom0", "hom0.1", "hom0.3", "het0.3"):
        for sk_name in ("true", "missing"):
            cells = []
            for mode, ck in V:
                a = np.array(res[(T, sc, sk_name, mode, ck)])
                cells.append(f"{a[:,0].mean():.3f} ({a[:,0].std():.3f}) [{np.sqrt(np.mean((a[:,0]-a[:,1])**2)):.3f}]")
            print(f"| {T} | {sc} | {sk_name} | {a[:,1].mean():.3f} | " + " | ".join(cells) + " |", flush=True)
