"""Skeptic probe (D-07H development only): how often does csis_reduce actually use the CSIS ranking,
and how often does it drop contemporaneous parents / own lag 2? Plus unit tests of _cond_t and a
known-truth selection test of CSIS vs random choice."""
import json, sys
from collections import Counter
from pathlib import Path
import numpy as np
ROOT = Path("/Users/kietnt/Desktop/Workspace/Paper4_UIT")
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
from run_experiment import ext_seed, generator_config, public, unit_skeletons
import paper4.ext_r4hubscreen as HS
from paper4.generator import build_dynamic_sem
from paper4.topology import load_bank

out = {}
# ---- unit test 1: _cond_t equals direct OLS |t|
rng = np.random.default_rng(1)
m = 20; Xc = np.column_stack([np.ones(m), rng.normal(size=(m, 3))]); cands = rng.normal(size=(m, 5)); y = rng.normal(size=m)
mine = HS._cond_t(y, Xc, cands)
ref = []
for k in range(5):
    X = np.column_stack([Xc, cands[:, k]]); b, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ b; s2 = r @ r / (m - X.shape[1]); cov = s2 * np.linalg.inv(X.T @ X); ref.append(abs(b[-1]) / np.sqrt(cov[-1, -1]))
out["unit_cond_t_maxabsdiff"] = float(np.max(np.abs(mine - np.array(ref))))

# ---- known-truth selection test: hub eq at lag 2, T19 (m=17, cap 6): own lags (2) as C, 6 neighbours x 2 lags = 12 pool terms,
# truth: 2 neighbours with lag-1 coef 0.5; d = 6-1-2 = 3. Recall of the 2 true terms vs random (expected 3/12 per term).
def sim(T, beta, rs):
    n = 7; X = np.zeros((T + 50, n)); e = rs.normal(size=(T + 50, n))
    for t in range(2, T + 50):
        X[t, 1:] = 0.4 * X[t - 1, 1:] + e[t, 1:]
        X[t, 0] = 0.3 * X[t - 1, 0] + 0.1 * X[t - 2, 0] + beta * (X[t - 1, 1] + X[t - 1, 2]) + e[t, 0]
    return X[50:]
tj = [(0, 1), (0, 2)] + [(i, l) for i in range(1, 7) for l in (1, 2)]
for beta in (0.3, 0.5, 0.8):
    rs = np.random.default_rng(7); hits = []
    for rep in range(500):
        kept = HS.csis_reduce(sim(19, beta, rs), tj, 0, 2)
        hits.append(sum(t in kept for t in [(1, 1), (2, 1)]) / 2)
    out[f"known_truth_recall_beta{beta}_T19"] = float(np.mean(hits))
out["known_truth_recall_random_baseline"] = 3 / 12

# ---- branch incidence on D-07H development, lag 2, T19/T25/T30, the candidate's own runs
log = []
orig = HS.csis_reduce
def wrapped(data, tj, j, lag_max):
    T = data.shape[0]; mm = T - lag_max; cap = HS.cap_columns(mm)
    C = [t for t in tj if (t[0] == j and t[1] > 0) or t[1] == 0]
    pool = [t for t in tj if t not in C]
    r = orig(data, tj, j, lag_max)
    n_c0 = sum(1 for t in tj if t[1] == 0); n_c0_kept = sum(1 for t in r if t[1] == 0)
    log.append({"T": T, "n_terms": len(tj), "cap": cap, "C": len(C), "pool": len(pool),
                "branch": "C>cap-1" if len(C) > cap - 1 else ("d<=0" if cap - 1 - len(C) <= 0 else "csis"),
                "contemp_dropped": n_c0 - n_c0_kept, "own_lag_dropped": sum(1 for t in C if t[0] == j and t[1] > 0 and t not in r),
                "pool_kept": sum(1 for t in r if t in pool), "kept": len(r)})
    return r
HS.csis_reduce = wrapped
topos = load_bank("D-07H", "development")[:10]
cfg = {"generator": {"lag_max": 2, "q0": 0.3, "cross_coef": [0.3, 0.8], "self_coef": [0.2, 0.6], "noise_var": [0.5, 1.5],
                     "rho_max": 0.9, "burn_in": 200}, "damage": {"kinds": ["extra", "missing", "reversed"], "rates": [0.2, 0.5]}}
gen = generator_config(cfg)
stats = {}
for T in (19, 25, 30):
    for kind in ("missing", "reversed", "extra"):
        log.clear(); nrun = 0
        for t_idx, topo in enumerate(topos):
            unit = 20261102 + 500_000 + 1000 * t_idx + 8   # replicate 8: outside calibration (0..2) and identity (7) units
            sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
            sks = unit_skeletons(sem, unit, cfg)
            data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
            for c_idx, cell in enumerate(sks):
                if cell != (kind, 0.2):
                    continue
                HS.tolerant_v5_1_hs(data, public(sks[cell]), 2, 4, 29, np.random.default_rng([unit, 3, T, c_idx, 5]))
                nrun += 1
        b = Counter(r["branch"] for r in log); n = len(log) or 1
        stats[f"2|{T}|{kind}"] = {"runs": nrun, "reductions": len(log), "branch_share": {k: v / n for k, v in b.items()},
            "share_contemp_parent_dropped": sum(r["contemp_dropped"] > 0 for r in log) / n,
            "share_own_lag_dropped": sum(r["own_lag_dropped"] > 0 for r in log) / n,
            "mean_terms_before": float(np.mean([r["n_terms"] for r in log])) if log else None,
            "mean_kept": float(np.mean([r["kept"] for r in log])) if log else None,
            "mean_pool_kept": float(np.mean([r["pool_kept"] for r in log])) if log else None}
        print(T, kind, stats[f"2|{T}|{kind}"], flush=True)
out["branch_incidence_D07H"] = stats
json.dump(out, open(ROOT / "results/ext_verify4_hubscreen/probe_branches.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "branch_incidence_D07H"}, indent=1))
