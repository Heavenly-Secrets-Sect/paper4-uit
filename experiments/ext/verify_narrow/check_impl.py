"""Skeptic checks of ext_narrow: (a) post-probe vectorised screen_pairs == probe-time version;
(b) F statistic equals a direct nested-OLS F; (c) on a small constructed SVAR the removed edge is ranked top."""
import sys, math
import numpy as np
sys.path.insert(0, '/Users/kietnt/Desktop/Workspace/Paper4_UIT/src')
sys.path.insert(0, '/Users/kietnt/Desktop/Workspace/Paper4_UIT/experiments/ext/verify_narrow')
from paper4 import ext_narrow as N
import narrow_orig_snapshot as O
from paper4.generator import GeneratorConfig, build_dynamic_sem
from paper4.skeleton import damage, true_skeleton, Skeleton
from paper4.topology import load_bank
from paper4.estimator import parent_terms

# (a) equivalence on D-07H development (calibration bank) topologies
topos = load_bank('D-07H', 'development')
maxd = 0; nsame = 0; ntot = 0
for ti in range(6):
    sem = build_dynamic_sem(topos[ti], GeneratorConfig(), np.random.default_rng(10 + ti)); tr = true_skeleton(sem)
    for T in (40, 80, 150):
        d = sem.simulate(T, np.random.default_rng(20 + ti))
        for kind, rate in [('missing', .2), ('missing', .5), ('none', 0)]:
            s = damage(tr, kind, rate, np.random.default_rng(3), sem.edge_lag)
            try:
                a = N.screen_pairs(d, s, 2); b = O.screen_pairs(d, s, 2)
            except ValueError as e:
                print('underdetermined', ti, T, kind, rate); continue
            ntot += 1
            nsame += [x[1:] for x in a] == [x[1:] for x in b]
            maxd = max(maxd, max(abs(x[0] - y[0]) for x, y in zip(sorted(a, key=lambda t: t[1:]), sorted(b, key=lambda t: t[1:]))))
print(f'(a) order identical {nsame}/{ntot}, max |p diff| {maxd:.2e}')

# (b) direct F for one pair
sem = build_dynamic_sem(topos[0], GeneratorConfig(), np.random.default_rng(1)); tr = true_skeleton(sem)
d = sem.simulate(80, np.random.default_rng(2)); s = damage(tr, 'missing', .5, np.random.default_rng(3), sem.edge_lag)
lag = 2; rows = np.arange(lag, 80); m = len(rows); adj = s.adjacency()
j = 0; u = next(x for x in range(1, s.n) if not adj[x, j])
X0 = np.column_stack([np.ones(m)] + [d[rows - l, i] for i, l in parent_terms(s, j, lag)])
X1 = np.column_stack([X0] + [d[rows - l, u] for l in (1, 2)])
y = d[rows, j]
rss = lambda X: float(np.sum((y - X @ np.linalg.lstsq(X, y, rcond=None)[0]) ** 2))
F = ((rss(X0) - rss(X1)) / 2) / (rss(X1) / (m - X1.shape[1]))
from scipy import stats
p_exact = stats.f.sf(F, 2, m - X1.shape[1]); p_paulson = N._f_p(F, 2, m - X1.shape[1])
print(f'(b) direct F={F:.4f}, exact p={p_exact:.4g}, Paulson p={p_paulson:.4g}')

# (c) small constructed SVAR: 4 nodes, edges 0->1 lag1 (0.7), 1->2 lag0 (0.6), 2->3 lag1 (0.6); no other.
rng = np.random.default_rng(5); T = 300
x = np.zeros((T + 100, 4)); e = rng.normal(size=(T + 100, 4))
for t in range(2, T + 100):
    x[t, 0] = 0.4 * x[t - 1, 0] + e[t, 0]
    x[t, 1] = 0.3 * x[t - 1, 1] + 0.7 * x[t - 1, 0] + e[t, 1]
    x[t, 2] = 0.3 * x[t - 1, 2] + 0.6 * x[t, 1] + e[t, 2]
    x[t, 3] = 0.3 * x[t - 1, 3] + 0.6 * x[t - 1, 2] + e[t, 3]
x = x[100:]
# stated skeleton missing 0->1 (lagged) ; and a second case missing 1->2 (contemporaneous)
for drop, oriented in [('0-1 lagged', {(1, 2), (2, 3)}), ('1-2 contemp', {(0, 1), (2, 3)})]:
    sk = Skeleton(4, oriented=set(oriented), damage={'kind': 'missing', 'rate': 0.33, 'k': 1})
    res = N.screen_pairs(x, sk, 2)
    print('(c) drop', drop, '->', [(round(p, 4), u, v) for p, u, v in res])
    print('    select_open(k=1):', N.select_open(x, sk, 2, 1, 3.0, 0.10))

# (b') F computed inside screen_pairs for (u -> j) vs direct
calls = []
orig = N._f_p
N._f_p = lambda F_, k, dof: (calls.append((F_, k, dof)), orig(F_, k, dof))[1]
N.screen_pairs(d, s, 2)
N._f_p = orig
# first equation j=0 candidates are in order of u ascending: the first call is for the smallest non-adjacent u
print(f"(b') screen_pairs first F={calls[0][0]:.4f} dof={calls[0][2]} vs direct F={F:.4f} dof={m - X1.shape[1]} (u={u})")
