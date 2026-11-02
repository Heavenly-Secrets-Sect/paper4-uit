"""Skeptic known-truth checks of ext_r4lfdropen.lfdr_posterior / select_open_lfdr (synthetic only).

K1  EM with pi0 fixed reaches the MLE of (mu, s) (compare with direct numerical maximisation).
K2  Structural property: with pi0 = 1 - k/m and a floor of k, how many pairs exceed P >= 0.5 when the
    screen has k true signals plus `ind` indirect (moderate) signals? (the claimed mechanism)
K3  Power: true signals of moderate strength (as at T = 40) -> recall of the top-k floor vs v5_1's K rule.
Writes results/ext_verify4_lfdropen/known_truth_skeptic.json
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import optimize
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4 import ext_r4lfdropen as L  # noqa: E402

out = {}

# K1
rng = np.random.default_rng(11)
m, k = 80, 6
z = np.r_[rng.normal(0, 1, m - k), rng.normal(2.5, 1, k)]
p = norm.sf(z)
P, em = L.lfdr_posterior(p, k)
pi0 = 1 - k / m
zc = norm.isf(np.clip(p, 1e-12, 1 - 1e-12))


def nll(th):
    mu, ls = th
    s = max(math.exp(ls), 0.5)
    return -np.sum(np.log(pi0 * norm.pdf(zc) + (1 - pi0) * norm.pdf(zc, mu, s)))


best = min((optimize.minimize(nll, x0, method="Nelder-Mead", options={"xatol": 1e-9, "fatol": 1e-12, "maxiter": 5000})
            for x0 in ([2.5, 0.0], [1.0, 0.5], [3.5, -0.3])), key=lambda r: r.fun)
out["K1_em_vs_mle"] = {"em": [em["mu"], em["s"]], "mle": [best.x[0], max(math.exp(best.x[1]), 0.5)],
                       "nll_em": nll([em["mu"], math.log(em["s"])]), "nll_mle": best.fun}

# K2 / K3: simulate screens
res = {}
for label, k, ind, mu_true, mu_ind in (("k4_ind0_strong", 4, 0, 4.0, 0), ("k4_ind8_strong", 4, 8, 4.0, 2.5),
                                       ("k4_ind8_weak", 4, 8, 2.0, 2.0), ("k11_ind10_weak", 11, 10, 2.0, 2.0),
                                       ("k4_ind0_weak", 4, 0, 2.0, 0)):
    m = 74 if k == 4 else 81
    n_open, rec_floor, rec_v51, n_v51, n_above = [], [], [], [], []
    r = np.random.default_rng(5)
    for rep in range(500):
        zt = r.normal(mu_true, 1, k)
        zi = r.normal(mu_ind, 1, ind)
        zn = r.normal(0, 1, m - k - ind)
        zz = np.r_[zt, zi, zn]
        pp = norm.sf(zz)
        P, em = L.lfdr_posterior(pp, k)
        order = np.argsort(pp, kind="stable")
        floor = set(order[:k].tolist())
        rest = order[k:]
        extra = {int(i) for i in rest if P[i] >= 0.5}
        opened = floor | extra
        K = min(m, max(3 * k, int((pp < 0.10).sum())))
        v51 = set(order[:K].tolist())
        truth = set(range(k))
        n_open.append(len(opened)); n_above.append(len(extra)); n_v51.append(K)
        rec_floor.append(len(truth & opened) / k); rec_v51.append(len(truth & v51) / k)
    res[label] = {"m": m, "k": k, "n_indirect": ind, "mean_open_lfdr": float(np.mean(n_open)),
                  "share_open_eq_floor": float(np.mean(np.array(n_above) == 0)),
                  "recall_lfdr": float(np.mean(rec_floor)), "mean_K_v51": float(np.mean(n_v51)),
                  "recall_v51": float(np.mean(rec_v51))}
out["K2_K3_sim"] = res
(ROOT / "results/ext_verify4_lfdropen").mkdir(exist_ok=True)
(ROOT / "results/ext_verify4_lfdropen/known_truth_skeptic.json").write_text(json.dumps(out, indent=1, default=float))
print(json.dumps(out, indent=1, default=float))
