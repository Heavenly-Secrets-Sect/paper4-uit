"""Skeptic check of ext_gate (verify_gate): (a) F-test of restricted_tests vs exact OLS + scipy F,
(b) gate false-alarm rate on true skeletons and power on missing-0.2, on D-07H development
topologies with fresh seeds (seed_base + 900000, not used by calibration), (c) undiagnosable rate.
Exploratory, D-07H development only."""
import json, sys, math
from pathlib import Path
import numpy as np
from scipy import stats
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
from run_experiment import generator_config
from paper4 import ext_gate as G
from paper4.estimator import parent_terms
from paper4.generator import build_dynamic_sem
from paper4.skeleton import true_skeleton, damage
from paper4.topology import load_bank
from concurrent.futures import ProcessPoolExecutor

cfg = json.load(open(ROOT / "experiments/configs/ext_gate_auto3.json"))
gen = generator_config(cfg)
topos = load_bank("D-07H", "development")

def exact_pair(data, skel, lag_max, u, v):
    T, n = data.shape; rows = np.arange(lag_max, T); m = len(rows)
    out = []
    for src, eq in ((u, v), (v, u)):
        tj = parent_terms(skel, eq, lag_max)
        X0 = np.column_stack([np.ones(m)] + [data[rows - l, i] for i, l in tj])
        X1 = np.column_stack([X0] + [data[rows - l, src] for l in range(1, lag_max + 1)])
        y = data[rows, eq]
        r0 = y - X0 @ np.linalg.lstsq(X0, y, rcond=None)[0]; r1 = y - X1 @ np.linalg.lstsq(X1, y, rcond=None)[0]
        d2 = m - X1.shape[1]
        F = ((r0 @ r0 - r1 @ r1) / lag_max) / (r1 @ r1 / d2)
        out.append(stats.f.sf(F, lag_max, d2))
    return out

def job(args):
    t_idx, rep = args
    unit = cfg["seed_base"] + 900000 + 1000 * t_idx + rep
    sem = build_dynamic_sem(topos[t_idx], gen, np.random.default_rng([unit, 0]))
    truth = true_skeleton(sem)
    miss = damage(truth, "missing", 0.2, np.random.default_rng([unit, 1]))
    res = []
    for T in (40, 80, 150):
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        d0 = G.diagnose_gate(data, truth, gen.lag_max); d1 = G.diagnose_gate(data, miss, gen.lag_max)
        rec = {"T": T, "p_none": d0["p_gate"], "p_miss": d1["p_gate"], "nbh0": d0["n_bh"], "ks0": d0["k_storey"]}
        if t_idx == 0 and rep == 0:
            pairs = G.left_out_pairs(truth)
            # compare the per-test F p-values (recompute inside, replicating restricted_tests internals)
            p_pair, p_corr = G.restricted_tests(data, truth, gen.lag_max, pairs)
            ex = [exact_pair(data, truth, gen.lag_max, u, v) for u, v in pairs[:5]]
            rec["exact_first5"] = ex; rec["p_pair_first5"] = p_pair[:5].tolist(); rec["p_corr_first5"] = p_corr[:5].tolist()
        res.append(rec)
    return res

if __name__ == "__main__":
    jobs = [(t, r) for t in range(len(topos)) for r in range(5)]
    with ProcessPoolExecutor(2) as ex:
        recs = [x for out in ex.map(job, jobs) for x in out]
    for r in recs:
        if "exact_first5" in r:
            print("T", r["T"], "exact F p (u->v, v->u):", np.round(r["exact_first5"], 4).tolist())
            print("   p_corr:", np.round(r["p_corr_first5"], 4).tolist(), " sidak pair:", np.round(r["p_pair_first5"], 4).tolist())
    for T in (40, 80, 150):
        rs = [r for r in recs if r["T"] == T]
        p0 = [r["p_none"] for r in rs if r["p_none"] is not None]; p1 = [r["p_miss"] for r in rs if r["p_miss"] is not None]
        print(f"T={T}: n={len(rs)} undiag none={sum(r['p_none'] is None for r in rs)} | false alarm @0.10: {np.mean(np.array(p0) <= 0.10):.3f} @0.05: {np.mean(np.array(p0)<=0.05):.3f} "
              f"| power missing0.2 @0.10: {np.mean(np.array(p1) <= 0.10):.3f} | mean n_bh/k_storey on true skel: {np.mean([r['nbh0'] for r in rs]):.2f}/{np.mean([r['ks0'] for r in rs]):.2f}")
