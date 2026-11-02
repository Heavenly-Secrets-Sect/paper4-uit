"""Red team P1/P2: pair-level records for frozen methods, with the runner's exact seeds.

P1 (bank D-07 development, eval seeds): plugin, tolerant_v4, bvar_minnesota, pselect_union.
P2 (bank D-07H development, calibration seeds): tolerant_v3, pselect_union, for coverage-vs-c curves.

Run: python experiments/ext/redteam/pair_probe.py p1|p2 [workers] [max_topologies]
Writes experiments/ext/redteam/out/<mode>.npz
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4 import methods as M  # noqa: E402
from paper4.generator import GeneratorConfig, build_dynamic_sem  # noqa: E402
from paper4.metrics import interval_score, truth_effects  # noqa: E402
from paper4.skeleton import damage, true_skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

SEED, H, LAG, NB, TAU = 20261102, 4, 2, 199, 0.1
KINDS, RATES = ["extra", "missing", "reversed"], [0.2, 0.5]
ALLCELLS = [("none", 0.0)] + [(k, r) for k in KINDS for r in RATES]
CALIB = json.loads((ROOT / "results/a2b_pselect/calibration.json").read_text())
GEN = GeneratorConfig(lag_max=2, q0=0.3, cross_coef=(0.3, 0.8), self_coef=(0.2, 0.6), noise_var=(0.5, 1.5),
                      rho_max=0.9, burn_in=200)


def job(args):
    mode, topo, t_idx, rep = args
    unit = SEED + (500_000 if mode == "p2" else 0) + 1000 * t_idx + rep
    sem = build_dynamic_sem(topo, GEN, np.random.default_rng([unit, 0]))
    truth = true_skeleton(sem)
    coef = {e: float(sem.B[lag, e[1], e[0]]) for e, lag in sem.edge_lag.items()}
    _, C_true, _, _ = truth_effects(sem, H)
    off = ~np.eye(sem.n, dtype=bool)
    nonnull = off & (np.abs(C_true) > TAU)
    null = off & ~nonnull
    if mode == "p1":
        want = [("missing", 0.2), ("missing", 0.5), ("reversed", 0.2), ("reversed", 0.5)]
        meths = ["plugin", "tolerant_v4", "bvar_minnesota", "pselect_union"]
    else:
        want = [("none", 0.0), ("missing", 0.2), ("missing", 0.5), ("reversed", 0.2), ("reversed", 0.5)]
        meths = ["tolerant_v3", "pselect_union"]
    recs = []
    for T in (40, 80, 150):
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        for c_idx, (kind, rate) in enumerate(ALLCELLS):
            if (kind, rate) not in want:
                continue
            k_idx = (["none"] + KINDS).index(kind)
            skel = damage(truth, kind, rate, np.random.default_rng([unit, 1, k_idx]), sem.edge_lag, coef)
            # affected pairs: C_true moves by >= 0.05 when the damaged true edges are zeroed
            B0 = sem.B.copy()
            for entry in skel.log:
                u, v = entry["pair"]
                for e in ((u, v), (v, u)):
                    if e in sem.edge_lag:
                        B0[sem.edge_lag[e], e[1], e[0]] = 0.0
            sem0 = build_like(sem, B0)
            _, C0, _, _ = truth_effects(sem0, H)
            affected = nonnull & (np.abs(C_true - C0) >= 0.05)
            rng = lambda tag: np.random.default_rng([unit, 3, T, c_idx, tag])  # noqa: E731
            res = {}
            for m in meths:
                if m == "plugin":
                    res[m] = M.plugin(data, skel, LAG, H, NB, rng(1))
                elif m == "tolerant_v3":
                    res[m] = M.tolerant_v3(data, skel, LAG, H, NB, rng(6))
                elif m == "tolerant_v4":
                    v3 = M.tolerant_v3(data, skel, LAG, H, NB, rng(6))
                    res[m] = M.calibrate_width(v3, CALIB.get(f"mod|{T}|{M.width_key(skel.damage)}"), m)
                elif m == "bvar_minnesota":
                    res[m] = M.bvar_minnesota(data, skel, LAG, H, NB, rng(8))
                elif m == "pselect_union":
                    res[m] = M.pselect_union(data, skel, LAG, H, NB, rng(9))
            for m, r in res.items():
                if r.status != "ok":
                    continue
                for j in range(sem.n):
                    for i in range(sem.n):
                        if i == j:
                            continue
                        cat = 2 if affected[j, i] else (1 if nonnull[j, i] else 0)   # 0 null, 1 unaffected, 2 affected
                        recs.append((t_idx, rep, T, c_idx, meths.index(m), cat, C_true[j, i], r.lo[j, i], r.hi[j, i],
                                     r.C[j, i]))
    return recs


def build_like(sem, B):
    from paper4.generator import DynamicSEM
    return DynamicSEM(sem.topology_id, sem.nodes, B, sem.noise_var, dict(sem.edge_lag), sem.config)


if __name__ == "__main__":
    mode = sys.argv[1]
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    maxt = int(sys.argv[3]) if len(sys.argv) > 3 else None
    bank = ("D-07", "development") if mode == "p1" else ("D-07H", "development")
    reps = 3 if mode == "p1" else 1
    topos = load_bank(*bank)[:maxt]
    jobs = [(mode, t, i, r) for i, t in enumerate(topos) for r in range(reps)]
    recs = []
    with ProcessPoolExecutor(workers) as pool:
        for out in pool.map(job, jobs):
            recs.extend(out)
    arr = np.array(recs, dtype=float)
    outdir = Path(__file__).parent / "out"
    outdir.mkdir(exist_ok=True)
    np.savez_compressed(outdir / f"{mode}.npz", recs=arr)
    print(mode, arr.shape)
