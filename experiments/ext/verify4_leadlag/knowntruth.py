"""Skeptic known-truth checks of the leadlag gate (uses the candidate's haugh_q / chi2_sf_even unchanged)."""
import sys, json
sys.path.insert(0, "/Users/kietnt/Desktop/Workspace/Paper4_UIT/src")
import numpy as np
from scipy import stats
from paper4.ext_r4leadlag import haugh_q, chi2_sf_even, cross_corr
out = {}
# 1. chi2 tail exactness
err = max(abs(chi2_sf_even(x, d) - stats.chi2.sf(x, d)) for x in np.linspace(0.1, 60, 300) for d in (2, 4, 8, 12))
print("chi2_sf_even max abs err vs scipy:", err); out["chi2_err"] = err
# 2. Q under independence of two white series (Haugh's own setting)
rng = np.random.default_rng(1)
for m in (78, 148):
    M = 4 if m < 100 else 6
    ps = [haugh_q(rng.normal(size=m), rng.normal(size=m), M)[1] for _ in range(4000)]
    print(f"white independent m={m}: size at 0.05 = {np.mean(np.array(ps)<.05):.3f}")
    out[f"size_white_m{m}"] = float(np.mean(np.array(ps) < .05))

def ols_resid(y, X):
    X = np.column_stack([np.ones(len(y)), X]); b = np.linalg.lstsq(X, y, rcond=None)[0]; return y - X @ b

def sim(T, phi, lag_u, lag_v, conf, edge, rng, p=2):
    """2 observed nodes u, v with own AR(1) 0.4; optional latent L (AR(1) phi) driving u at lag_u, v at lag_v
    with coefficient 0.6; optional true contemporaneous edge u->v (0.5). Returns residuals:
    A-like (each eq: own lags 1..p + other's lags 1..p [opened block]; v eq without u_t),
    D-like (each eq: own lags 1..p only)."""
    burn = 200; N = T + burn
    L = np.zeros(N); u = np.zeros(N); v = np.zeros(N)
    eL, eu, ev = rng.normal(size=N), rng.normal(size=N), rng.normal(size=N)
    for t in range(3, N):
        L[t] = phi * L[t-1] + eL[t]
        u[t] = 0.4 * u[t-1] + eu[t] + (0.6 * L[t-lag_u] if conf else 0)
        v[t] = 0.4 * v[t-1] + ev[t] + (0.6 * L[t-lag_v] if conf else 0) + (0.5 * u[t] if edge else 0)
    u, v = u[burn:], v[burn:]
    rows = np.arange(p, T)
    lag = lambda x, l: x[rows - l]
    own_u = np.column_stack([lag(u, l) for l in range(1, p+1)]); own_v = np.column_stack([lag(v, l) for l in range(1, p+1)])
    A = (ols_resid(u[rows], np.column_stack([own_u, own_v])), ols_resid(v[rows], np.column_stack([own_v, own_u])))
    Dd = (ols_resid(u[rows], own_u), ols_resid(v[rows], own_v))
    return A, Dd

def rate(T, n, **kw):
    M = 4 if T <= 80 else 6
    rng = np.random.default_rng(hash(str(kw)) % 2**32 + T)
    fa = fd = 0
    for _ in range(n):
        A, Dd = sim(T, rng=rng, **kw)
        fa += haugh_q(*A, M)[1] < .05; fd += haugh_q(*Dd, M)[1] < .05
    return fa / n, fd / n

cases = {
    "E0 edge, no confounder (gate null)": dict(phi=0.0, lag_u=0, lag_v=0, conf=False, edge=True),
    "no edge, no confounder": dict(phi=0.0, lag_u=0, lag_v=0, conf=False, edge=False),
    "confounder phi0.8 lag0/lag0": dict(phi=0.8, lag_u=0, lag_v=0, conf=True, edge=False),
    "confounder phi0.5 lag0/lag0": dict(phi=0.5, lag_u=0, lag_v=0, conf=True, edge=False),
    "confounder phi0.8 lag0/lag2": dict(phi=0.8, lag_u=0, lag_v=2, conf=True, edge=False),
    "white confounder lag0/lag0": dict(phi=0.0, lag_u=0, lag_v=0, conf=True, edge=False),
}
for name, kw in cases.items():
    for T in (80, 150, 1000):
        n = 1000 if T < 1000 else 300
        a, d = rate(T, n, **kw)
        print(f"{name:38s} T={T:5d}: flag rate A-like {a:.3f}  D-like {d:.3f}")
        out[f"{name}|T{T}"] = {"A": a, "D": d}
json.dump(out, open("/Users/kietnt/Desktop/Workspace/Paper4_UIT/results/ext_verify4_leadlag/knowntruth.json", "w"), indent=1)
