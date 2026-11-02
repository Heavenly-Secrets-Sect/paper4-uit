import math, numpy as np
from paper4.diagnose import _norm_sf
from paper4.estimator import parent_terms, fit_equations

def f_pvalue(F, k, dof):
    a, b = 2 / (9 * k), 2 / (9 * max(dof, 1))
    f3 = max(F, 0.0) ** (1 / 3)
    return _norm_sf(((1 - b) * f3 - (1 - a)) / math.sqrt(a + b * f3 * f3))

def restricted_tests(data, skel, lag_max, pairs_out):
    """Tests of each left-out pair in the skeleton's own structural fit: F test of adding u's lags
    to v's equation and v's lags to u's, and Fisher z of the correlation of the two residuals."""
    T, n = data.shape
    rows = np.arange(lag_max, T); m = len(rows)
    Q, R, dof = [], [], []
    for j in range(n):
        tj = parent_terms(skel, j, lag_max)
        X = np.column_stack([np.ones(m)] + [data[rows - lag, i] for i, lag in tj])
        if X.shape[1] + lag_max + 2 > m:
            raise ValueError('underdetermined')
        q, _ = np.linalg.qr(X)
        y = data[rows, j]
        r = y - q @ (q.T @ y)
        Q.append(q); R.append(r); dof.append(m - X.shape[1])
    Lags = {i: np.column_stack([data[rows - lag, i] for lag in range(1, lag_max + 1)]) for i in range(n)}
    Rm = np.column_stack(R)
    corr = np.corrcoef(Rm.T)
    pl, pc = [], []
    for u, v in pairs_out:
        ps = []
        for src, eq in ((u, v), (v, u)):
            Z = Lags[src]; Zr = Z - Q[eq] @ (Q[eq].T @ Z)
            g = Zr.T @ R[eq]
            ssr_drop = float(g @ np.linalg.solve(Zr.T @ Zr, g))
            rss = float(R[eq] @ R[eq])
            d2 = dof[eq] - lag_max
            F = (ssr_drop / lag_max) / ((rss - ssr_drop) / d2)
            ps.append(f_pvalue(F, lag_max, d2))
        r = float(np.clip(corr[u, v], -0.999999, 0.999999))
        z = math.atanh(r) * math.sqrt(max(min(dof[u], dof[v]) - 1, 1))
        c = 2 * _norm_sf(abs(z))
        ps.append(c)
        pl.append(1 - (1 - min(ps)) ** 3); pc.append(c)
    return np.array(pl), np.array(pc)

def sim_indep(fit, data, rng):
    """Residual bootstrap under independent structural shocks: each equation's residuals are
    resampled on their own, which is the null of a correct skeleton."""
    T, n = data.shape
    p = fit.B.shape[0] - 1
    A = np.linalg.inv(np.eye(n) - fit.B[0])
    m = len(fit.residuals)
    scale = np.sqrt(m / np.maximum(fit.dof, 1.0))
    resid = (fit.residuals - fit.residuals.mean(axis=0)) * scale
    idx = rng.integers(0, m, size=(T - p, n))
    draws = resid[idx, np.arange(n)]
    x = np.zeros_like(data); x[:p] = data[:p]
    for t in range(p, T):
        acc = fit.intercept + draws[t - p]
        for k in range(1, p + 1):
            acc = acc + fit.B[k] @ x[t - k]
        x[t] = A @ acc
    return x

def gate_p(data, skel, lag_max, rng, tests='restricted', n_gate=0):
    n = skel.n
    present = skel.pairs()
    pairs_out = [(u, v) for u in range(n) for v in range(u + 1, n) if frozenset((u, v)) not in present]
    fn = restricted_tests
    if tests == 'alllag':
        import gate_core
        fn = gate_core.leftout_tests
    p, pc = fn(data, skel, lag_max, pairs_out)
    s0 = float(p.min())
    if n_gate == 0:
        return 1 - (1 - s0) ** len(p), p, pc, pairs_out
    null = fit_equations(data, [parent_terms(skel, j, lag_max) for j in range(n)], lag_max)
    hits = done = 0
    for _ in range(n_gate):
        try:
            pb, _ = fn(sim_indep(null, data, rng), skel, lag_max, pairs_out)
        except (ValueError, np.linalg.LinAlgError):
            continue
        hits += pb.min() <= s0; done += 1
    return (1 + hits) / (1 + done), p, pc, pairs_out
