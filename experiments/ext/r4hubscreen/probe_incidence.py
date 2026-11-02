"""Design probe (D-07H development only): how often the skeleton's own equations fail the
underdetermination checks of tolerant_v5_1 (screen_pairs: |X| + lag_max + 2 > m with intercept;
fit_equations: |terms| + 2 > m), per (lag_max, T, cell). Uses only skeletons (no data).

Run: python experiments/ext/r4hubscreen/probe_incidence.py -> results/ext_r4hubscreen_probe/incidence.{md,json}
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
from run_experiment import generator_config, unit_skeletons  # noqa: E402
from paper4.estimator import parent_terms  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

SEED = 20261102
OUT = ROOT / "results" / "ext_r4hubscreen_probe"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    topos = load_bank("D-07H", "development")
    res = {}
    lines = ["# Incidence of underdetermined base equations, D-07H development (probe)", "",
             "Per cell: share of units with >= 1 failing equation in screen_pairs / in fit_equations (base terms), "
             "and max |base terms| over equations (mean over units).", "",
             "| lag_max | T | m | cell | screen fail | fit fail | mean max |terms| | mean #fail eq (screen) |", "|---|---|---|---|---|---|---|---|"]
    for lag in (1, 2):
        cfg = {"generator": {"lag_max": lag, "q0": 0.3, "cross_coef": [0.3, 0.8], "self_coef": [0.2, 0.6],
                             "noise_var": [0.5, 1.5], "rho_max": 0.9, "burn_in": 200},
               "damage": {"kinds": ["extra", "missing", "reversed"], "rates": [0.2, 0.5]}}
        gen = generator_config(cfg)
        sk_units = []
        for t_idx, topo in enumerate(topos):
            for rep in range(3):
                unit = SEED + 500_000 + 1000 * t_idx + rep
                sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
                sk_units.append(unit_skeletons(sem, unit, cfg))
        for T in (19, 25, 30, 35, 40):
            m = T - lag
            for cell in [("none", 0.0), ("missing", 0.2), ("reversed", 0.2), ("extra", 0.2), ("missing", 0.5)]:
                sf = ff = 0
                mx, nfe = [], []
                for sk in sk_units:
                    s = sk[cell]
                    lens = [len(parent_terms(s, j, lag)) for j in range(s.n)]
                    scr = [L + 1 + lag + 2 > m for L in lens]
                    fit = [L + 2 > m for L in lens]
                    sf += any(scr); ff += any(fit); mx.append(max(lens)); nfe.append(sum(scr))
                N = len(sk_units)
                res[f"{lag}|{T}|{cell[0]}-{cell[1]}"] = {"screen_fail": sf / N, "fit_fail": ff / N,
                                                         "mean_max_terms": float(np.mean(mx)), "n_units": N}
                lines.append(f"| {lag} | {T} | {m} | {cell[0]}-{cell[1]} | {sf/N:.2f} | {ff/N:.2f} | {np.mean(mx):.1f} | {np.mean(nfe):.2f} |")
    (OUT / "incidence.json").write_text(json.dumps(res, indent=1))
    (OUT / "incidence.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
