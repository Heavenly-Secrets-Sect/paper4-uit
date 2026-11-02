"""Shared helpers for the v51 direction: load runs, check pairing, paired CI, one-sided bootstrap p, Holm."""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "results"
TS = [40, 80, 150]
CELLS = [("none", 0.0)] + [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]
DAMAGED = [c for c in CELLS if c[0] != "none"]


def load(name, methods=None):
    rows = []
    for line in open(RES / name / "runs.jsonl"):
        r = json.loads(line)
        if methods is None or r["method"] in methods:
            rows.append(r)
    return rows


def key(r):
    return (r.get("scenario", "clean"), r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])


def index(rows):
    return {(key(r), r["method"]): r for r in rows if r["status"] == "ok" and r.get("iscore_nonnull_mean") is not None}


def check_identical(rows_a, rows_b, method):
    """Rows of ``method`` in two runs: identical status, IS (< 1e-12), covered and non-null counts."""
    a = {key(r): r for r in rows_a if r["method"] == method}
    b = {key(r): r for r in rows_b if r["method"] == method}
    common = set(a) & set(b)
    same = 0
    for k in common:
        x, y = a[k], b[k]
        if x["status"] != y["status"]:
            continue
        if x["status"] != "ok":
            same += 1
            continue
        if (abs(x["iscore_nonnull_mean"] - y["iscore_nonnull_mean"]) < 1e-12 and x["n_covered_nonnull"] == y["n_covered_nonnull"]
                and x["n_nonnull"] == y["n_nonnull"]):
            same += 1
    return {"n_a": len(a), "n_b": len(b), "common": len(common), "identical": same,
            "ok": len(a) == len(b) == len(common) == same and len(a) > 0}


def cell_stats(rows, m, T, kind, rate, scenario="clean"):
    g = [r for r in rows if r["method"] == m and r["T"] == T and r["kind"] == kind and r["rate"] == rate
         and r.get("scenario", "clean") == scenario]
    ok = [r for r in g if r["status"] == "ok"]
    if not ok:
        return None
    w = [r["width_kept"] for r in ok if r.get("width_kept") is not None]
    out = {"n": len(ok), "of": len(g),
           "cov": sum(r["n_covered_nonnull"] for r in ok) / sum(r["n_nonnull"] for r in ok),
           "IS": float(np.mean([r["iscore_nonnull_mean"] for r in ok])),
           "width": float(np.median(w)) if w else float("nan")}
    for k in ("info_n_open", "info_n_open_boot_mean", "info_v51_targeted", "info_v51_ratio", "iscore_null_mean"):
        v = [r[k] for r in ok if r.get(k) is not None]
        out[k] = float(np.mean(v)) if v else None
    return out


def diffs_by_topo(idx, m, ref, T, kind, rate, scenario="clean"):
    d = defaultdict(list)
    for (k, meth), r in idx.items():
        if meth == m and k[0] == scenario and k[3] == T and k[4] == kind and k[5] == rate:
            o = idx.get((k, ref))
            if o:
                d[k[1]].append(r["iscore_nonnull_mean"] - o["iscore_nonnull_mean"])
    return d


def _boot(d, n, seed):
    rng = np.random.default_rng(seed)
    topos = list(d)
    sums = np.array([np.sum(d[t]) for t in topos])
    cnts = np.array([len(d[t]) for t in topos])
    picks = rng.integers(0, len(topos), size=(n, len(topos)))
    return sums[picks].sum(1) / cnts[picks].sum(1)


def paired(idx, m, ref, T, kind, rate, scenario="clean"):
    """Mean paired IS difference, 95% CI (1000 topology resamples, seed 0, as the runner), one-sided p
    for diff < 0 and for diff > 0 (10 000 resamples, seed 1), number of paired runs."""
    d = diffs_by_topo(idx, m, ref, T, kind, rate, scenario)
    if not d:
        return None
    # CI exactly as the runner / narrow paired.py (loop with rng.choice), for comparability
    rng = np.random.default_rng(0)
    topos = list(d)
    est = float(np.mean([v for t in topos for v in d[t]]))
    boots = [np.mean([v for i in rng.choice(len(topos), len(topos)) for v in d[topos[i]]]) for _ in range(1000)]
    lo, hi = np.quantile(boots, (0.025, 0.975))
    b2 = _boot(d, 10_000, 1)
    p_less = (1 + int((b2 >= 0).sum())) / (len(b2) + 1)
    p_greater = (1 + int((b2 <= 0).sum())) / (len(b2) + 1)
    return {"est": est, "lo": float(lo), "hi": float(hi), "p_less": p_less, "p_greater": p_greater,
            "n": sum(len(v) for v in d.values())}


def holm(pvals, alpha=0.025):
    """Holm step-down: list of booleans (rejected) in input order."""
    order = np.argsort(pvals)
    m = len(pvals)
    rej = [False] * m
    for rank, i in enumerate(order):
        if pvals[i] <= alpha / (m - rank):
            rej[i] = True
        else:
            break
    return rej


def fmt_p(p):
    return "–" if p is None else f"{p['est']:+.2f} [{p['lo']:+.2f}, {p['hi']:+.2f}]"
