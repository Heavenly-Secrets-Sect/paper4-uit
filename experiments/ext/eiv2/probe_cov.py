"""Design probe 2 (eiv2; D-07H development only, seed 5151; never D-07; widths NOT calibrated):
coverage / IS / median |C| on null pairs of tolerant_v3, tolerant_eiv (round 1) and variants of
tolerant_eiv2, under clean, homogeneous (0.1, 0.3) and heterogeneous (mean 0.3) noise.
Usage: probe_cov.py N_TOPO N_BOOT VARIANTS(comma list) > results/ext_eiv2_probes/cov_<tag>.txt
Variants: v3, eiv1, eiv2 (pereq, cap 0.7), eiv2c99 (pereq, cap 0.99), eiv2free, plugin, plugin_eiv2,
eiv2liml (pereq, LIML-type criterion), eiv2g9 (fit guard 0.9 instead of 0.7);
DIAGNOSTICS ONLY (read the true mean noise share, never candidates): eiv2trueD, eiv2trueDg9."""
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(Path(__file__).parent))
import warnings; warnings.filterwarnings("ignore")
from paper4 import ext_eiv as E1  # noqa
from paper4 import ext_eiv2 as E2  # noqa
from paper4 import methods as M  # noqa
from paper4.ext_eiv import tolerant_eiv  # noqa
from paper4.generator import GeneratorConfig, add_measurement_noise, build_dynamic_sem  # noqa
from paper4.metrics import evaluate  # noqa
from paper4.skeleton import damage, true_skeleton  # noqa
from paper4.topology import load_bank  # noqa
from hetero import add_hetero_noise  # noqa

SEED = 5151
SCEN = ("hom0", "hom0.1", "hom0.3", "het0.3")


def run_variant(v, y, sk, n_boot, rng, share=None):
    E1.GUARD = 0.9 if v.endswith("g9") else 0.7
    E2.CRIT = "liml" if v == "eiv2liml" else "corr"
    if v.startswith("eiv2trueD"):
        E2.CAP_GUARD = 0.7
        return E2._eiv2(y, sk, 2, 4, n_boot, rng, tolerant=True, name=v, _r_probe=share)
    if v == "v3":
        return M.tolerant_v3(y, sk, 2, 4, n_boot, rng)
    if v == "plugin":
        return M.plugin(y, sk, 2, 4, n_boot, rng)
    if v == "eiv1":
        return tolerant_eiv(y, sk, 2, 4, n_boot, rng)
    if v == "plugin_eiv2":
        E2.CAP_GUARD = 0.7
        return E2.plugin_eiv2(y, sk, 2, 4, n_boot, rng)
    E2.CAP_GUARD = 0.99 if v == "eiv2c99" else 0.7
    mode = "free" if v == "eiv2free" else "pereq"
    return E2._eiv2(y, sk, 2, 4, n_boot, rng, tolerant=True, name=v, mode=mode)


def job(args):
    t_idx, n_boot, variants = args
    topo = load_bank("D-07H", "development")[t_idx]
    gen = GeneratorConfig()
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([SEED, t_idx]))
    truth = true_skeleton(sem)
    coef = {e: float(sem.B[lag, e[1], e[0]]) for e, lag in sem.edge_lag.items()}
    skels = {"none": truth,
             "missing": damage(truth, "missing", 0.2, np.random.default_rng([SEED, t_idx, 9]), sem.edge_lag, coef),
             "reversed": damage(truth, "reversed", 0.2, np.random.default_rng([SEED, t_idx, 10]), sem.edge_lag, coef)}
    out = []
    for T in (80, 150):
        x = sem.simulate(T, np.random.default_rng([SEED, t_idx, T, 1]))
        for sc in SCEN:
            ratio = float(sc[3:])
            rng = np.random.default_rng([SEED, t_idx, T, 2])
            if sc.startswith("hom"):
                y = add_measurement_noise(x, ratio, rng); share = ratio / (1 + ratio)
            else:
                y, rs = add_hetero_noise(x, ratio, rng); share = float(np.mean(rs / (1 + rs)))
            for kind, sk in skels.items():
                for v_idx, v in enumerate(variants):
                    res = run_variant(v, y, sk, n_boot, np.random.default_rng([SEED, t_idx, T, 3, v_idx]), share)
                    row = evaluate(sem, res, 4)
                    out.append((T, sc, kind, v, row, res.info.get("r_hat")))
    return out


if __name__ == "__main__":
    n_topo, n_boot, variants = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3].split(",")
    agg = defaultdict(list)
    with ProcessPoolExecutor(3) as pool:
        for out in pool.map(job, [(t, n_boot, variants) for t in range(n_topo)]):
            for T, sc, kind, v, row, r in out:
                agg[(T, sc, kind, v)].append((row, r))
    print(f"# probe_cov: D-07H development, {n_topo} topologies, seed {SEED}, n_boot {n_boot}, UNCALIBRATED widths")
    print("# cell: coverage / IS / median C_abs_spurious (null pairs) / mean r_hat")
    print("| T | scenario | damage | " + " | ".join(variants) + " |")
    print("|---|---|---|" + "---|" * len(variants))
    for T in (80, 150):
        for sc in SCEN:
            for kind in ("none", "missing", "reversed"):
                cells = []
                for v in variants:
                    rs = [(row, r) for row, r in agg[(T, sc, kind, v)] if row["status"] == "ok"]
                    cov = sum(row["n_covered_nonnull"] for row, _ in rs) / max(1, sum(row["n_nonnull"] for row, _ in rs))
                    IS = np.mean([row["iscore_nonnull_mean"] for row, _ in rs])
                    sp = np.median([row["C_abs_spurious"] for row, _ in rs if row["C_abs_spurious"] is not None])
                    rh = np.mean([r for _, r in rs if r is not None]) if any(r is not None for _, r in rs) else float("nan")
                    cells.append(f"{cov:.3f} / {IS:.2f} / {sp:.3f} / {rh:.3f}")
                print(f"| {T} | {sc} | {kind} | " + " | ".join(cells) + " |", flush=True)
