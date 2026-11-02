"""Skeptic probe (verify5_hubscreen2): is the T19-missing IS tail of hs2 really from 'near-explosive fits'?
Re-runs hs2 on the top-IS runs and on median runs (same seeds as run_r5.run_unit) and reports the spectral radius of
the data-level reduced-form companion matrix, and the minimum equation dof of the data-level fit.
Writes results/ext_verify5_hubscreen2/tail_probe.json."""
import json
import sys
import warnings
from pathlib import Path

import numpy as np

ROOT = Path("/Users/kietnt/Desktop/Workspace/Paper4_UIT")
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
warnings.filterwarnings("ignore")
from run_experiment import ext_seed, generator_config, public, unit_skeletons  # noqa
from paper4 import ext_r5hubscreen2 as H  # noqa
from paper4.generator import build_dynamic_sem  # noqa
from paper4.topology import load_bank  # noqa

LAYOUT = {"kinds": ["extra", "missing", "reversed"], "rates": [0.2, 0.5]}
cfg = json.loads((ROOT / "experiments/configs/ext_r5hubscreen2_p2.json").read_text())
gen = generator_config(cfg)
topos = load_bank("D-07", "development")
idx = {t.id: i for i, t in enumerate(topos)}
cases = [("syn_dag_13", 2), ("syn_dag_13", 1), ("syn_dag_02", 0), ("syn_dag_00", 0), ("syn_dag_06", 0),
         ("syn_dag_05", 0), ("syn_dag_00", 1), ("syn_dag_03", 1)]
fits = []
orig = H.fit_equations


def wrap(data, terms, lag_max, *a, **k):
    f = orig(data, terms, lag_max, *a, **k)
    fits.append(f)
    return f


H.fit_equations = wrap
out = []
for tid, rep in cases:
    t_idx = idx[tid]
    unit = cfg["seed_base"] + 1000 * t_idx + rep
    sem = build_dynamic_sem(topos[t_idx], gen, np.random.default_rng([unit, 0]))
    skels = unit_skeletons(sem, unit, dict(cfg, damage=LAYOUT))
    T = 19
    data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
    for c_idx, ((kind, rate), full) in enumerate(skels.items()):
        if (kind, float(rate)) != ("missing", 0.2):
            continue
        fits.clear()
        res = H.tolerant_v5_1_hs2(data, public(full), 2, 4, 199, np.random.default_rng([unit, 3, T, c_idx, ext_seed("tolerant_v5_1")]))
        n = sem.n
        # data-level fit = first fit after screening (fit0), and the final data fit is res.B
        B = res.B
        A0inv = np.linalg.inv(np.eye(n) - B[0])
        comp = np.zeros((2 * n, 2 * n))
        comp[:n, :n] = A0inv @ B[1]; comp[:n, n:] = A0inv @ B[2]; comp[n:, :n] = np.eye(n)
        rho = float(max(abs(np.linalg.eigvals(comp))))
        # bootstrap draws: spectral radius of each draw-level fit (fits after the first two data-level ones)
        rhos = []
        for f in fits[2:]:
            if f.status != "ok":
                continue
            try:
                Ai = np.linalg.inv(np.eye(n) - f.B[0])
            except np.linalg.LinAlgError:
                continue
            c = np.zeros((2 * n, 2 * n)); c[:n, :n] = Ai @ f.B[1]; c[:n, n:] = Ai @ f.B[2]; c[n:, :n] = np.eye(n)
            rhos.append(float(max(abs(np.linalg.eigvals(c)))))
        min_dof = float(min(fits[0].dof)) if fits else None
        out.append({"topology": tid, "replicate": rep, "status": res.status, "rho_data": round(rho, 3),
                    "min_dof_fit0": min_dof, "draw_rho_median": round(float(np.median(rhos)), 3) if rhos else None,
                    "draw_rho_p95": round(float(np.quantile(rhos, 0.95)), 3) if rhos else None,
                    "share_draws_rho_ge_1": round(float(np.mean(np.array(rhos) >= 1)), 3) if rhos else None,
                    "n_draw_fits": len(rhos)})
        print(out[-1], flush=True)
(ROOT / "results/ext_verify5_hubscreen2/tail_probe.json").write_text(json.dumps(out, indent=1))
