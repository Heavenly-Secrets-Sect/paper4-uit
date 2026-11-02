"""Shared helpers for the eiv2 report scripts (cluster bootstrap by topology, Holm)."""
from collections import defaultdict

import numpy as np

B = 2000


def ok(rs):
    return [r for r in rs if r["status"] == "ok"]


def cov(rs):
    rs = ok(rs)
    return sum(r["n_covered_nonnull"] for r in rs) / sum(r["n_nonnull"] for r in rs)


def iscore(rs):
    return float(np.mean([r["iscore_nonnull_mean"] for r in ok(rs)]))


def by_topo(rs):
    d = defaultdict(list)
    for r in ok(rs):
        d[r["topology"]].append(r)
    return d


def boot(stat, groups, seed=0):
    rng = np.random.default_rng(seed)
    topos = sorted(set.intersection(*[set(gr) for gr in groups]))
    vals = []
    for _ in range(B):
        pick = [topos[i] for i in rng.choice(len(topos), len(topos))]
        vals.append(stat(*[[r for t in pick for r in gr[t]] for gr in groups]))
    return np.array(vals)


def holm(pvals, alpha=0.05):
    order = np.argsort(pvals)
    rej = np.zeros(len(pvals), dtype=bool)
    for rank, i in enumerate(order):
        if pvals[i] <= alpha / (len(pvals) - rank):
            rej[i] = True
        else:
            break
    return rej


def paired_rows(rows_a, rows_b):
    """Mean paired IS difference a - b, 95% CI clustered by topology, two-sided bootstrap p."""
    idx = {(r["topology"], r["replicate"]): r["iscore_nonnull_mean"] for r in ok(rows_b)}
    d = defaultdict(list)
    for r in ok(rows_a):
        key = (r["topology"], r["replicate"])
        if key in idx:
            d[r["topology"]].append(r["iscore_nonnull_mean"] - idx[key])
    topos = sorted(d)
    est = float(np.mean([v for t in topos for v in d[t]]))
    rng = np.random.default_rng(0)
    bs = np.array([np.mean([v for i in rng.choice(len(topos), len(topos)) for v in d[topos[i]]]) for _ in range(B)])
    lo, hi = np.quantile(bs, (0.025, 0.975))
    return est, lo, hi, min(1.0, 2 * min((bs <= 0).mean(), (bs >= 0).mean()))
