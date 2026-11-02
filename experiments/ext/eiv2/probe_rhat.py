"""Design probe 1 (eiv2; D-07H development only, seed 4242; never D-07):
r_hat of the three admissibility modes of ext_eiv2.estimate_noise_share_v2
("global" = round-1 cap, "pereq" = v2 per-equation cap, "free" = none) on the true skeleton and on
20%-missing / 20%-reversed skeletons, homogeneous (ratio 0 / 0.1 / 0.3) and heterogeneous
(mean ratio 0.1 / 0.3) noise. Usage: probe_rhat.py N_TOPO > results/ext_eiv2_probes/rhat.txt"""
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

n_topo = int(sys.argv[1]) if len(sys.argv) > 1 else 16
gen = GeneratorConfig()
topos = load_bank("D-07H", "development")[:n_topo]
SEED = 4242
res = {}
for t_idx, topo in enumerate(topos):
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([SEED, t_idx]))
    truth = true_skeleton(sem)
    coef = {e: float(sem.B[lag, e[1], e[0]]) for e, lag in sem.edge_lag.items()}
    skels = {"true": truth,
             "missing": damage(truth, "missing", 0.2, np.random.default_rng([SEED, t_idx, 9]), sem.edge_lag, coef),
             "reversed": damage(truth, "reversed", 0.2, np.random.default_rng([SEED, t_idx, 10]), sem.edge_lag, coef)}
    for T in (80, 150):
        x = sem.simulate(T, np.random.default_rng([SEED, t_idx, T, 1]))
        for sc in ("hom0", "hom0.1", "hom0.3", "het0.1", "het0.3"):
            ratio = float(sc[3:])
            rng = np.random.default_rng([SEED, t_idx, T, 2])
            if sc.startswith("hom"):
                y = add_measurement_noise(x, ratio, rng); share = ratio / (1 + ratio)
            else:
                y, rs = add_hetero_noise(x, ratio, rng); share = float(np.mean(rs / (1 + rs)))
            for sk_name, sk in skels.items():
                terms = [parent_terms(sk, j, 2) for j in range(sk.n)]
                for mode in ("global", "pereq", "free"):
                    r, _, d = estimate_noise_share_v2(y, terms, 2, mode=mode)
                    res.setdefault((T, sc, sk_name, mode), []).append((r, share, d["n_eq_capped"], d["n_pd_fix"]))
print(f"# probe_rhat: D-07H development, first {len(topos)} topologies, seed {SEED}; mean (sd) of r_hat, true mean share")
print("| T | scenario | skeleton | true share | global (round 1) | pereq (v2) | free | v2: mean #eq capped at r_hat | v2: PD fixes |")
print("|---|---|---|---|---|---|---|---|---|")
for T in (80, 150):
    for sc in ("hom0", "hom0.1", "hom0.3", "het0.1", "het0.3"):
        for sk_name in ("true", "missing", "reversed"):
            cells = []
            for mode in ("global", "pereq", "free"):
                a = np.array(res[(T, sc, sk_name, mode)])
                cells.append(f"{a[:,0].mean():.3f} ({a[:,0].std():.3f})")
            a = np.array(res[(T, sc, sk_name, "pereq")])
            print(f"| {T} | {sc} | {sk_name} | {a[:,1].mean():.3f} | " + " | ".join(cells) + f" | {a[:,2].mean():.2f} | {a[:,3].sum():.0f} |", flush=True)
