"""Skeptic check of ext_eiv (exploratory; constructed systems + D-07H development only)."""
import sys; sys.path.insert(0, "src")
import numpy as np
from paper4.ext_eiv import fit_corrected, estimate_noise_share, fit_stationary
from paper4.estimator import parent_terms
from paper4.skeleton import Skeleton
from paper4.generator import add_measurement_noise

# --- A: constructed 3-node recursive SVAR, lag_max 2 -----------------------------------
n, p = 3, 2
B = np.zeros((p + 1, n, n))
B[1, 0, 0] = 0.5                      # x0 own lag
B[0, 1, 0] = 0.7                      # x0 -> x1 contemporaneous
B[1, 1, 1] = 0.4
B[2, 2, 1] = 0.6                      # x1 -> x2 at lag 2
B[1, 2, 2] = 0.3
skel = Skeleton(n, oriented={(0, 1), (1, 2)}, damage={"kind": "none", "rate": 0.0, "k": 0})
def sim(T, rng):
    x = np.zeros((T + 300, n)); A = np.linalg.inv(np.eye(n) - B[0])
    for t in range(2, T + 300):
        x[t] = A @ (B[1] @ x[t-1] + B[2] @ x[t-2] + rng.normal(size=n))
    return x[300:]
terms = [parent_terms(skel, j, p) for j in range(n)]
print("terms", terms)
rng = np.random.default_rng(0)
x = sim(40000, rng); y = add_measurement_noise(x, 0.3, rng)
share = 0.3 / 1.3
truth = {(j, t): B[t[1], j, t[0]] for j in range(n) for t in terms[j]}
f_ols, _ = fit_corrected(y, terms, p, np.zeros(n))
f_cor, ap = fit_corrected(y, terms, p, share * y.var(0))
print("A. T=40000 noise 0.3; coef: truth / OLS / corrected(true D)  guard applied", np.round(ap, 3))
for (j, (i, lag)), v in truth.items():
    print(f"   x{i} lag{lag} -> x{j}: {v:+.3f} / {f_ols.B[lag, j, i]:+.3f} / {f_cor.B[lag, j, i]:+.3f}")
r, _ = estimate_noise_share(y, terms, p)
print("   r_hat at T=40000:", r, "true share", round(share, 3))
for T in (150, 1000, 5000):
    rs = []
    for s in range(30):
        rr = np.random.default_rng([1, T, s]); xx = sim(T, rr); yy = add_measurement_noise(xx, 0.3, rr)
        rs.append(estimate_noise_share(yy, terms, p)[0])
    print(f"   constructed T={T}: r_hat mean {np.mean(rs):.3f} sd {np.std(rs):.3f} (30 reps)")
