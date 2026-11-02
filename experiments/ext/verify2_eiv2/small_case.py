"""Skeptic check (round 2) of ext_eiv2 on constructed known-truth systems only (no bank data)."""
import sys; sys.path.insert(0, "src")
import warnings; warnings.filterwarnings("ignore")
import numpy as np
from paper4.ext_eiv2 import estimate_noise_share_v2, tolerant_eiv2, plugin_eiv2
from paper4.ext_eiv import estimate_noise_share
from paper4.estimator import parent_terms
from paper4.skeleton import Skeleton
from paper4.generator import add_measurement_noise
from paper4.effects import irf, cumulative

n, p, H = 3, 2, 4
B = np.zeros((p + 1, n, n))
B[1, 0, 0] = 0.5; B[0, 1, 0] = 0.7; B[1, 1, 1] = 0.4; B[2, 2, 1] = 0.6; B[1, 2, 2] = 0.3
skel = Skeleton(n, oriented={(0, 1), (1, 2)}, damage={"kind": "none", "rate": 0.0, "k": 0})
Ctrue = cumulative(irf(B, H), H)
pairs = [(1, 0), (2, 1), (2, 0)]          # (j, i): non-null effects
def sim(T, rng, Bm=B):
    x = np.zeros((T + 300, n)); A = np.linalg.inv(np.eye(n) - Bm[0])
    for t in range(2, T + 300):
        x[t] = A @ (Bm[1] @ x[t-1] + Bm[2] @ x[t-2] + rng.normal(size=n))
    return x[300:]
terms = [parent_terms(skel, j, p) for j in range(n)]
share = 0.3 / 1.3
print("# A. constructed 3-node system, noise ratio 0.3 (true share %.3f)" % share)
rng = np.random.default_rng(0); y = add_measurement_noise(sim(40000, rng), 0.3, rng)
for mode in ("pereq", "global", "free"):
    print(f"  T=40000 mode={mode}: r_hat {estimate_noise_share_v2(y, terms, p, mode=mode)[0]:.3f}")
print(f"  T=40000 round-1 estimate_noise_share: {estimate_noise_share(y, terms, p)[0]:.3f}")
x0 = sim(40000, np.random.default_rng(1))
print(f"  T=40000 CLEAN pereq: r_hat {estimate_noise_share_v2(x0, terms, p)[0]:.3f} (truth 0)")
res = tolerant_eiv2(y[:5000], skel, p, H, 99, np.random.default_rng(3))
print("  tolerant_eiv2 T=5000: C_hat vs C_true on non-null pairs:",
      [(f"{res.C[j,i]:+.3f}", f"{Ctrue[j,i]:+.3f}") for j, i in pairs], "r_hat", round(res.info["r_hat"], 3))

print("\n# B. coverage on the constructed system, T=150, noise 0.3, 40 reps, n_boot 99 (UNCALIBRATED widths)")
for name, f in (("tolerant_eiv2", tolerant_eiv2), ("plugin_eiv2", plugin_eiv2)):
    cov = []; rh = []
    for s in range(40):
        rr = np.random.default_rng([7, s]); yy = add_measurement_noise(sim(150, rr), 0.3, rr)
        r = f(yy, skel, p, H, 99, np.random.default_rng([8, s]))
        if r.status != "ok": continue
        cov += [r.lo[j, i] <= Ctrue[j, i] <= r.hi[j, i] for j, i in pairs]; rh.append(r.info["r_hat"])
    print(f"  {name}: coverage {np.mean(cov):.3f} over {len(cov)} pair-runs; r_hat mean {np.mean(rh):.3f} sd {np.std(rh):.3f}")

print("\n# C. global vs per-equation cap with one near-collinear equation (x3 ~ x0 + small noise feeding x4)")
n2 = 5
B2 = np.zeros((p + 1, n2, n2))
B2[1, 0, 0] = 0.5; B2[0, 1, 0] = 0.7; B2[1, 1, 1] = 0.4; B2[2, 2, 1] = 0.6; B2[1, 2, 2] = 0.3
B2[0, 3, 0] = 1.0; B2[0, 4, 0] = 0.4; B2[0, 4, 3] = 0.4
sk2 = Skeleton(n2, oriented={(0, 1), (1, 2), (0, 3), (0, 4), (3, 4)}, damage={"kind": "none", "rate": 0.0, "k": 0})
t2 = [parent_terms(sk2, j, p) for j in range(n2)]
def sim2(T, rng):
    x = np.zeros((T + 300, n2)); A = np.linalg.inv(np.eye(n2) - B2[0])
    sd = np.array([1, 1, 1, 0.15, 1.0])
    for t in range(2, T + 300):
        x[t] = A @ (B2[1] @ x[t-1] + B2[2] @ x[t-2] + sd * rng.normal(size=n2))
    return x[300:]
for T in (80, 150, 2000):
    out = {m: [] for m in ("pereq", "global")}
    for s in range(30):
        rr = np.random.default_rng([11, T, s]); yy = add_measurement_noise(sim2(T, rr), 0.3, rr)
        for m in out: out[m].append(estimate_noise_share_v2(yy, t2, p, mode=m)[0])
    print(f"  T={T}: pereq {np.mean(out['pereq']):.3f} ({np.std(out['pereq']):.3f})  global {np.mean(out['global']):.3f} ({np.std(out['global']):.3f})  truth {share:.3f}")

print("\n# D. true mean share under het r=0.3 (ratios linspace(0, 0.6, n)), share_i = r_i/(1+r_i)")
for nn in (7, 10, 14, 20):
    rr = np.linspace(0, 0.6, nn); print(f"  n={nn}: mean share {np.mean(rr/(1+rr)):.4f}")
