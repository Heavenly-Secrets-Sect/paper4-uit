"""Sanity checks of ext_baselines2 on small known-truth examples (no bank data):
1. the closed-form NIG marginal likelihood equals scipy's multivariate-t density;
2. NIG posterior draws of sigma^2 centre on the true error variance at large T;
3. pselect_union_v2 on a 4-node SVAR with a deleted contemporaneous edge re-selects it and
   fits it in both orientations; coverage of the deleted pair's C(H) over a few seeds.
4. uncalibrated / calibrated variants return identical raw intervals (shared stream + cache).
Writes results/ext_baselines2_sanity/sanity.txt."""
import math, sys
from pathlib import Path
import numpy as np
from scipy.stats import multivariate_t

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4 import ext_baselines2 as E  # noqa
from paper4.effects import cumulative, irf  # noqa
from paper4.skeleton import Skeleton  # noqa

out = []
rng = np.random.default_rng(1)
# 1. marginal likelihood
m, k = 30, 4
X = rng.normal(size=(m, k)); X -= X.mean(0)
y = X @ rng.normal(size=k) + rng.normal(size=m); y -= y.mean()
v0 = rng.uniform(0.1, 2, size=k); a0, b0 = 1.5, 0.7
prec = X.T @ X + np.diag(1 / v0); L = np.linalg.cholesky(prec)
bn = np.linalg.solve(prec, X.T @ y); an = a0 + m / 2; bsc = b0 + 0.5 * (y @ y - (X.T @ y) @ bn)
ld = -2 * np.log(np.diag(L)).sum() - np.log(v0).sum()
lml = math.lgamma(an) - math.lgamma(a0) + a0 * math.log(b0) - an * math.log(bsc) + 0.5 * ld - 0.5 * m * math.log(2 * math.pi)
ref = multivariate_t(loc=np.zeros(m), shape=(b0 / a0) * (np.eye(m) + X @ np.diag(v0) @ X.T), df=2 * a0).logpdf(y)
out.append(f"1. NIG log ML closed form {lml:.6f} vs scipy multivariate_t {ref:.6f}")

# a 4-node SVAR: 0 -> 1 (lag 0, 0.6), 1 -> 2 (lag 1, 0.5), 2 -> 3 (lag 0, 0.5), own lags 0.4
def sim(T, seed, sig=(1.0, 0.8, 1.2, 0.6)):
    r = np.random.default_rng(seed)
    B = np.zeros((3, 4, 4)); B[0, 1, 0] = 0.6; B[1, 2, 1] = 0.5; B[0, 3, 2] = 0.5
    for j in range(4): B[1, j, j] = 0.4
    A = np.linalg.inv(np.eye(4) - B[0]); x = np.zeros((T + 200, 4))
    e = r.normal(size=(T + 200, 4)) * np.sqrt(sig)
    for t in range(2, T + 200):
        x[t] = A @ (B[1] @ x[t - 1] + B[2] @ x[t - 2] + e[t])
    return x[200:], B
C_true = cumulative(irf(sim(10, 0)[1], 4), 4)

# 2. sigma^2 posterior
data, _ = sim(3000, 2)
skel = Skeleton(4, oriented={(0, 1), (1, 2), (2, 3)}, damage={"kind": "none", "rate": 0.0, "k": 0})
res = E._bvar_core(data, skel, 2, 4, 199, np.random.default_rng(3))
out.append(f"2. bvar_v2 T=3000: lambda={res.info['lambda']}, theta={res.info['theta']}, "
           f"C(0->3) est {res.C[3,0]:.3f} [{res.lo[3,0]:.3f}, {res.hi[3,0]:.3f}] true {C_true[3,0]:.3f}")

# 3. pselect_v2 with the contemporaneous edge 0 -> 1 deleted
cov, sel, unor = [], [], []
for seed in range(20):
    data, _ = sim(150, 100 + seed)
    sk = Skeleton(4, oriented={(1, 2), (2, 3)}, damage={"kind": "missing", "rate": 0.3, "k": 1})
    r = E._pselect_core(data, sk, 2, 4, 199, np.random.default_rng(seed))
    cov.append(r.lo[1, 0] <= C_true[1, 0] <= r.hi[1, 0])
    sel.append(r.info["n_selected"]); unor.append(r.info["n_unoriented"])
out.append(f"3. pselect_v2 T=150, deleted 0->1 (true C {C_true[1,0]:.3f}): coverage {np.mean(cov):.2f} over 20 seeds; "
           f"mean selected pairs {np.mean(sel):.2f} (truth 3); mean unoriented {np.mean(unor):.2f}; last info {r.info}")

# 4. shared stream
sk = Skeleton(4, oriented={(1, 2), (2, 3)}, damage={"kind": "missing", "rate": 0.3, "k": 1})
a = E.pselect_union_v2(data, sk, 2, 4, 199, None); E._CACHE.clear(); b = E.pselect_union_v2_cal(data, sk, 2, 4, 199, None)
c = E.bvar_minnesota_v2(data, sk, 2, 4, 199, None); d = E.bvar_minnesota_v2_cal(data, sk, 2, 4, 199, None)
out.append(f"4. identical raw intervals: pselect {np.array_equal(a.lo, b.lo) and np.array_equal(a.hi, b.hi)} "
           f"(cache cleared between calls), bvar {np.array_equal(c.lo, d.lo)}; names {a.name}, {b.name}")
d = ROOT / "results" / "ext_baselines2_sanity"; d.mkdir(parents=True, exist_ok=True)
(d / "sanity.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
