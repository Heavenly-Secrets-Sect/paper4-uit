"""Verifier known-truth check of the BaB core (bab_draws with fixed structure) in the canonical Kilian
setting: bivariate VAR(1), persistent, T = 40, fixed true structure. Compare plain percentile
(bootstrap_C) vs BaB percentile coverage of C(H) and the bias of the point estimate.
Also: Kilian (1998) recursive shrink vs the linear shrink used by the candidate."""
import json, sys
import numpy as np
ROOT = "/Users/kietnt/Desktop/Workspace/Paper4_UIT"
sys.path.insert(0, ROOT + "/src")
from paper4 import ext_r4kilianbab as K
from paper4.estimator import fit_equations, bootstrap_C, percentile_interval
from paper4.effects import irf, cumulative, companion_radius

H, T, REPS, NB = 4, 40, int(sys.argv[1]) if len(sys.argv) > 1 else 150, 199
B = np.zeros((2, 2, 2)); B[1] = [[0.9, 0.1], [0.0, 0.85]]
terms = [[(0, 1), (1, 1)], [(0, 1), (1, 1)]]
Ct = cumulative(irf(B, H), H)
def sim(rng):
    x = np.zeros((T + 200, 2)); e = rng.standard_normal((T + 200, 2))
    for t in range(1, T + 200): x[t] = B[1] @ x[t - 1] + e[t]
    return x[200:]
cov_p, cov_b, w_p, w_b, est_ls, est_bab, is_p, is_b = [], [], [], [], [], [], [], []
def iscore(lo, hi, y, a=0.05):
    return (hi - lo) + 2 / a * (lo - y) * (y < lo) + 2 / a * (y - hi) * (y > hi)
for r in range(REPS):
    rng = np.random.default_rng([4242, r])
    data = sim(rng)
    fit = fit_equations(data, terms, 1)
    dp = bootstrap_C(data, fit, H, NB, np.random.default_rng([1, r]))
    db, fit_c, info = K.bab_draws(data, fit, H, NB, np.random.default_rng([2, r]))
    lp, hp = percentile_interval(dp); lb, hb = percentile_interval(db)
    cov_p.append(((lp <= Ct) & (Ct <= hp)).mean()); cov_b.append(((lb <= Ct) & (Ct <= hb)).mean())
    w_p.append((hp - lp).mean()); w_b.append((hb - lb).mean())
    is_p.append(iscore(lp, hp, Ct).mean()); is_b.append(iscore(lb, hb, Ct).mean())
    est_ls.append(cumulative(irf(fit.B, H), H) - Ct); est_bab.append(cumulative(irf(fit_c.B, H), H) - Ct)
res = {"setting": "VAR(1) A=[[.9,.1],[0,.85]], T=40, H=4, reps=%d, n_boot=199" % REPS,
       "coverage_percentile": float(np.mean(cov_p)), "coverage_bab": float(np.mean(cov_b)),
       "width_percentile": float(np.mean(w_p)), "width_bab": float(np.mean(w_b)),
       "IS_percentile": float(np.mean(is_p)), "IS_bab": float(np.mean(is_b)),
       "mean_bias_C_LS": np.mean(est_ls, axis=0).round(3).tolist(), "mean_bias_C_BaB": np.mean(est_bab, axis=0).round(3).tolist(),
       "C_true": Ct.round(3).tolist()}
# shrink forms
def kilian_recursive(Bm, bias):
    if companion_radius(Bm) >= 1: return Bm, 0.0
    Bc = Bm.copy(); Bc[1:] -= bias[1:]
    if companion_radius(Bc) < 1: return Bc, 1.0
    psi, delta = 1.0, 1.0
    while True:
        psi = delta * psi; delta = round(delta - 0.01, 2)
        Bc = Bm.copy(); Bc[1:] -= psi * bias[1:]
        if companion_radius(Bc) < 1 or psi <= 0: return Bc, psi
cmp = []
for target in (0.98, 0.95, 0.9, 0.8, 0.6, 0.4):
    Bm = np.zeros((2, 1, 1)); Bm[1, 0, 0] = target
    bias = np.zeros_like(Bm); bias[1, 0, 0] = -(1.0 - target) * 1.5  # full correction overshoots unit root
    _, d_lin, _ = K.kilian_correct(Bm, bias); _, d_rec = kilian_recursive(Bm, bias)
    cmp.append({"B": target, "d_linear": d_lin, "d_recursive_kilian1998": round(d_rec, 4)})
res["shrink_linear_vs_recursive"] = cmp
json.dump(res, open(ROOT + "/results/ext_verify4_kilianbab/known_truth.json", "w"), indent=1)
print(json.dumps(res, indent=1))
