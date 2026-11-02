"""Skeptic known-truth check of tolerant_v4L (synthetic hand-built SEM, no bank data).
Chain 0 -> 1 (lag 0, 0.8), 1 -> 2 (lag 0, 0.6), 2 -> 3 (lag 1, 0.5), self-lags 0.3.
Skeleton: true, then edge (0,1) reversed to (1,0), stated damage {kind reversed, k 1}.
Checks: (1) same rng -> v4L C/lo/hi == v4 C/lo/hi; (2) cumulative(theta_v4L) == C when structure drawn;
(3) none-cell theta identical; (4) peak lag for pair 0->1 (truth peak 0) under v4 vs v4L, over seeds.
Writes results/ext_verify2_revlag/known_truth.md"""
import sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
from paper4 import methods as M
from paper4.effects import cumulative, irf, mean_lag, peak_lag
from paper4.ext_revlag import tolerant_v4L_draws, frozen_factor
from paper4.generator import DynamicSEM, GeneratorConfig
from paper4.skeleton import Skeleton
import warnings; warnings.filterwarnings("ignore")
cfg = GeneratorConfig(lag_max=2, q0=0.3, cross_coef=(0.3, 0.8), self_coef=(0.2, 0.6), noise_var=(0.5, 1.5), rho_max=0.9, burn_in=200)
n, H, p = 4, 4, 2
B = np.zeros((p + 1, n, n))
for i in range(n): B[1, i, i] = 0.3
B[0, 1, 0] = 0.8; B[0, 2, 1] = 0.6; B[1, 3, 2] = 0.5
edge_lag = {(0, 1): 0, (1, 2): 0, (2, 3): 1}
sem = DynamicSEM("toy", tuple("abcd"), B, np.ones(n), edge_lag, cfg)
th_t = irf(B, H); C_t = cumulative(th_t, H); pk_t = peak_lag(th_t, H)
L = ["# Known-truth check of tolerant_v4L (hand-built 4-node SEM)", "",
     f"truth: C[1,0]={C_t[1,0]:.3f}, peak lag 0->1 = {pk_t[1,0]}, C[2,0]={C_t[2,0]:.3f} peak {pk_t[2,0]}", ""]
good = Skeleton(n, oriented={(0, 1), (1, 2), (2, 3)}, damage={"kind": "none", "rate": 0.0, "k": 0})
rev = Skeleton(n, oriented={(1, 0), (1, 2), (2, 3)}, damage={"kind": "reversed", "rate": 0.5, "k": 1})
ident, cumok, none_same = [], [], []
hits = {"v4": [], "v4L": []}; hits02 = {"v4": [], "v4L": []}; covs = {"v4": [], "v4L": []}
for s in range(12):
    for T in (80, 150):
        data = sem.simulate(T, np.random.default_rng([s, T]))
        for nm, sk in (("none", good), ("rev", rev)):
            v3 = M.tolerant_v3(data, sk, p, H, 99, np.random.default_rng([s, T, 6]))
            v4 = M.calibrate_width(v3, frozen_factor(T, sk.damage), "tolerant_v4")
            v4L, thetas = tolerant_v4L_draws(data, sk, p, H, 99, np.random.default_rng([s, T, 6]))
            ident.append(np.array_equal(v4.C, v4L.C) and np.array_equal(v4.lo, v4L.lo) and np.array_equal(v4.hi, v4L.hi))
            if nm == "none":
                none_same.append(np.array_equal(v4.theta, v4L.theta))
            else:
                cumok.append(np.allclose(cumulative(v4L.theta, H), v4L.C))
                for k, r in (("v4", v4), ("v4L", v4L)):
                    pe = peak_lag(r.theta, H)
                    hits[k].append(pe[1, 0] == pk_t[1, 0]); hits02[k].append(pe[2, 0] == pk_t[2, 0])
                    covs[k].append(r.lo[1, 0] <= C_t[1, 0] <= r.hi[1, 0])
L += [f"- (1) v4L C/lo/hi bit-identical to v4 under same rng: {sum(ident)}/{len(ident)}",
      f"- (2) cumulative(theta_v4L) == C in reversed cell: {sum(cumok)}/{len(cumok)}",
      f"- (3) none cell theta identical: {sum(none_same)}/{len(none_same)}",
      f"- (4) peak-lag hit on reversed pair 0->1 (truth peak {pk_t[1,0]}): v4 {np.mean(hits['v4']):.3f}, v4L {np.mean(hits['v4L']):.3f} (n={len(hits['v4'])})",
      f"- (4b) peak-lag hit on downstream pair 0->2: v4 {np.mean(hits02['v4']):.3f}, v4L {np.mean(hits02['v4L']):.3f}",
      f"- (5) coverage of C[1,0] by v4 interval in reversed cell: {np.mean(covs['v4']):.3f} (v4L identical: {np.mean(covs['v4L']):.3f})"]
(ROOT / "results/ext_verify2_revlag/known_truth.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
