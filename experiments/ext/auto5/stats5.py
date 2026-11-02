"""Shared statistics for the auto5 analyses: pooled coverage, paired IS differences with a 95%
bootstrap CI clustered by topology, one-sided coverage tests, and Holm's step-down procedure."""
from __future__ import annotations

import json
from collections import defaultdict

import numpy as np

N_BOOT = 2000


def load(path):
    return [json.loads(line) for line in open(path, encoding="utf-8")]


def key(r):
    return (r.get("scenario", "clean"), r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])


def index(rows):
    idx = defaultdict(dict)
    for r in rows:
        if r.get("status") == "ok" and r.get("iscore_nonnull_mean") is not None:
            idx[key(r)].setdefault(r["method"], r)
    return idx


def coverage(rows):
    den = sum(r["n_nonnull"] for r in rows)
    return sum(r["n_covered_nonnull"] for r in rows) / den if den else float("nan")


def coverage_test(rows, thr=0.90, seed=0):
    """Pooled coverage and one-sided bootstrap p-value for H0: coverage <= thr (clustered by topology)."""
    by = defaultdict(lambda: [0, 0])
    for r in rows:
        by[r["topology"]][0] += r["n_covered_nonnull"]
        by[r["topology"]][1] += r["n_nonnull"]
    topos = list(by)
    a = np.array([by[t][0] for t in topos], float)
    b = np.array([by[t][1] for t in topos], float)
    rng = np.random.default_rng(seed)
    pick = rng.integers(0, len(topos), size=(N_BOOT, len(topos)))
    boots = a[pick].sum(1) / b[pick].sum(1)
    return float(a.sum() / b.sum()), float(np.mean(boots <= thr))


def paired(idx, sel, m, ref, seed=0):
    """Mean paired IS difference m - ref over the keys passing ``sel``; CI and two-sided p from a
    bootstrap over topologies."""
    d = defaultdict(list)
    for k, ms in idx.items():
        if sel(k) and m in ms and ref in ms:
            d[k[1]].append(ms[m]["iscore_nonnull_mean"] - ms[ref]["iscore_nonnull_mean"])
    if not d:
        return None
    topos = list(d)
    sums = np.array([sum(d[t]) for t in topos])
    cnts = np.array([len(d[t]) for t in topos])
    rng = np.random.default_rng(seed)
    pick = rng.integers(0, len(topos), size=(N_BOOT, len(topos)))
    boots = sums[pick].sum(1) / cnts[pick].sum(1)
    est = float(sums.sum() / cnts.sum())
    lo, hi = np.quantile(boots, (0.025, 0.975))
    p = float(min(1.0, 2 * min(np.mean(boots <= 0), np.mean(boots >= 0))))
    return {"est": est, "lo": float(lo), "hi": float(hi), "p": p, "n": int(cnts.sum())}


def holm(pvals, alpha=0.05):
    """Boolean rejections of Holm's step-down procedure, in the input order."""
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    rej = np.zeros(len(p), bool)
    for rank, i in enumerate(order):
        if p[i] <= alpha / (len(p) - rank):
            rej[i] = True
        else:
            break
    return rej.tolist()


def fmt(d):
    return "–" if d is None else f"{d['est']:+.2f} [{d['lo']:+.2f}, {d['hi']:+.2f}]"
