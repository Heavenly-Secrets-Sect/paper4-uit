"""Frozen analyzer for the P4-H3 sealed confirmatory run of RQ4.3 (see docs/ext/p4h3_rq43.md).

Reads results/ext_p4h3_rq43/pairs.jsonl (P4-H3) and, read-only, results/rq43_edge_cost/pairs.jsonl (D-07).
Writes results/ext_p4h3_rq43/{analysis.json, summary.md}.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr

ROOT = Path(__file__).resolve().parents[4]
NEW = ROOT / "results" / "ext_p4h3_rq43" / "pairs.jsonl"
OLD = ROOT / "results" / "rq43_edge_cost" / "pairs.jsonl"
OUT = ROOT / "results" / "ext_p4h3_rq43"

ROLES = ("on_path", "into_source", "into_target", "other")
ROWS = (("missing", "c"), ("missing", "l"), ("reversed", "c"))
ROW_NAME = {("missing", "c"): "missing contemporaneous", ("missing", "l"): "missing lagged",
            ("reversed", "c"): "reversed contemporaneous"}
REF_ONPATH = {("missing", "c"): 0.93, ("missing", "l"): 0.81, ("reversed", "c"): 0.53}  # docs/ket_qua_rq43.md
RATIO, TOL, RHO_MIN = 3.0, 0.15, 0.9
MIN_CLUSTERS, MIN_N, B, SEED, ALPHA = 8, 20, 2000, 90261103, 0.05
CELLS = [(k, l, r) for (k, l) in ROWS for r in ROLES]


def load(path):
    out = defaultdict(lambda: defaultdict(list))  # topo key -> cell -> [rel_shift]
    meta = {}
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        lc = "c" if r["edge_lag"] == 0 else "l"
        key = (r["split"], r["topology"])
        out[key][(r["kind"], lc, r["role"])].append(r["rel_shift"])
        meta[key] = r["profile"]
    arr = {k: {c: np.array(v) for c, v in d.items()} for k, d in out.items()}
    return arr, meta


def pooled(arr, keys, cell):
    parts = [arr[k][cell] for k in keys if cell in arr[k]]
    return np.concatenate(parts) if parts else np.array([])


def n_clusters(arr, keys, cell):
    return sum(1 for k in keys if cell in arr[k] and len(arr[k][cell]))


def med(v):
    return float(np.median(v)) if len(v) else float("nan")


def evaluable(arr, keys, cell):
    return n_clusters(arr, keys, cell) >= MIN_CLUSTERS and len(pooled(arr, keys, cell)) >= MIN_N


def cell_medians(arr, keys, cells=CELLS):
    return {c: med(pooled(arr, keys, c)) for c in cells if evaluable(arr, keys, c)}


def sp(a, b, minc=10):
    ks = sorted(a.keys() & b.keys())
    if len(ks) < minc:
        return float("nan"), len(ks)
    return float(spearmanr([a[k] for k in ks], [b[k] for k in ks]).statistic), len(ks)


def sp_argsort(a, b):  # the original script's tie handling (descriptive only)
    ks = sorted(a.keys() & b.keys())
    ra = np.argsort(np.argsort([a[k] for k in ks]))
    rb = np.argsort(np.argsort([b[k] for k in ks]))
    return float(np.corrcoef(ra, rb)[0, 1])


def boot_keys(rng, keys):
    return [keys[i] for i in rng.integers(0, len(keys), len(keys))]


def holm(pvals: dict, alpha=ALPHA):
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m, rej, stop = len(items), {}, False
    for i, (k, p) in enumerate(items):
        if stop or p > alpha / (m - i):
            stop = True
            rej[k] = False
        else:
            rej[k] = True
    return rej


def ci(x):
    x = np.array([v for v in x if not np.isnan(v)])
    return (float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))) if len(x) else (float("nan"),) * 2


def main():
    new, meta = load(NEW)
    old, _ = load(OLD)
    kn, ko = sorted(new), sorted(old)
    assert len(kn) == 40 and len({k[1] for k in kn}) == 40, len(kn)
    dev = [k for k in kn if k[0] == "development"]
    con = [k for k in kn if k[0] == "confirmatory"]
    er = [k for k in kn if meta[k] == "erdos_renyi"]
    hub = [k for k in kn if meta[k] == "scale_free_hub"]
    rng = np.random.default_rng(SEED)

    # point estimates
    pt = {c: med(pooled(new, kn, c)) for c in CELLS}
    ev = {c: evaluable(new, kn, c) for c in CELLS}
    pt_old = {c: med(pooled(old, ko, c)) for c in CELLS}

    # bootstrap draws (topology clusters)
    draws = []
    for _ in range(B):
        draws.append({"all": boot_keys(rng, kn), "dev": boot_keys(rng, dev), "con": boot_keys(rng, con),
                      "er": boot_keys(rng, er), "hub": boot_keys(rng, hub), "old": boot_keys(rng, ko)})
    bmed = {c: [] for c in CELLS}
    for d in draws:
        for c in CELLS:
            bmed[c].append(med(pooled(new, d["all"], c)))
    bmed = {c: np.array(v) for c, v in bmed.items()}

    res = {"seed": SEED, "B": B, "rule": {"ratio": RATIO, "tol": TOL, "rho_min": RHO_MIN, "ref_onpath": {f"{k}|{l}": v for (k, l), v in REF_ONPATH.items()}}}

    # cell table
    table = []
    for c in CELLS:
        v = pooled(new, kn, c)
        lo, hi = ci(bmed[c])
        table.append({"damage": c[0], "lag": c[1], "role": c[2], "n": int(len(v)), "clusters": n_clusters(new, kn, c),
                      "evaluable": bool(ev[c]), "median": pt[c], "ci95": [lo, hi], "share_gt_0.2": float(np.mean(v > 0.2)) if len(v) else None,
                      "d07_median": pt_old[c],
                      "dev_median": med(pooled(new, dev, c)), "dev_clusters": n_clusters(new, dev, c),
                      "con_median": med(pooled(new, con, c)), "con_clusters": n_clusters(new, con, c),
                      "er_median": med(pooled(new, er, c)), "er_clusters": n_clusters(new, er, c),
                      "hub_median": med(pooled(new, hub, c)), "hub_clusters": n_clusters(new, hub, c)})
    res["cells"] = table

    # (a)
    pa, a_rows = {}, {}
    for row in ROWS:
        on = (*row, "on_path")
        row_ok = bool(ev[on])
        detail = {}
        for r in ROLES[1:]:
            c = (*row, r)
            if not ev[on]:
                detail[r] = {"evaluable": False, "ok": False}
                continue
            if not ev[c]:
                detail[r] = {"evaluable": False, "ok": None}  # role has < 8 clusters: not a comparison, reported
                continue
            ok = pt[on] >= RATIO * pt[c]
            p = (np.sum(bmed[on] < RATIO * bmed[c]) + 1) / (B + 1)
            pa[f"a|{ROW_NAME[row]}|{r}"] = float(p)
            detail[r] = {"evaluable": True, "ratio": (pt[on] / pt[c]) if pt[c] > 0 else None, "ok": bool(ok), "p": float(p)}
        row_ok = row_ok and all(d["ok"] is not False for d in detail.values())
        a_rows[ROW_NAME[row]] = {"ok": bool(row_ok), "detail": detail}
    res["a"] = {"pass": all(v["ok"] for v in a_rows.values()), "rows": a_rows}

    # (b)
    pb, b_rows = {}, {}
    for row in ROWS:
        on = (*row, "on_path")
        ref = REF_ONPATH[row]
        ok = bool(ev[on] and abs(pt[on] - ref) <= TOL)
        lo_p = (np.sum(bmed[on] <= ref - TOL) + 1) / (B + 1)
        hi_p = (np.sum(bmed[on] >= ref + TOL) + 1) / (B + 1)
        pb[f"b|{ROW_NAME[row]}"] = float(max(lo_p, hi_p))
        b_rows[ROW_NAME[row]] = {"median": pt[on], "ref": ref, "diff": pt[on] - ref, "ok": ok, "ci95": list(ci(bmed[on])), "tost_p": float(max(lo_p, hi_p))}
    res["b"] = {"pass": all(v["ok"] for v in b_rows.values()), "rows": b_rows}

    # Holm over the 12 one-sided bootstrap p-values (a: 9, b: 3)
    allp = {**pa, **pb}
    rej = holm(allp)
    res["holm"] = {"m": len(allp), "rejected": int(sum(rej.values())), "per_test": {k: {"p": allp[k], "rejected": rej[k]} for k in allp},
                   "a_rejected": int(sum(v for k, v in rej.items() if k.startswith("a|"))), "a_m": len(pa),
                   "b_rejected": int(sum(v for k, v in rej.items() if k.startswith("b|"))), "b_m": len(pb)}

    # (c), (d) Spearman with stratified / independent topology-cluster bootstrap
    def spearman_block(name, keysA, keysB, arrA, arrB, bkA, bkB):
        a, b = cell_medians(arrA, keysA), cell_medians(arrB, keysB)
        rho, nc = sp(a, b)
        shared = sorted(a.keys() & b.keys())
        bs = []
        for d in draws:
            ma = {c: med(pooled(arrA, d[bkA], c)) for c in shared}
            mb = {c: med(pooled(arrB, d[bkB], c)) for c in shared}
            r, _ = sp(ma, mb, minc=3)
            bs.append(r)
        lo, hi = ci(bs)
        return {"rho": rho, "cells": nc, "ci95": [lo, hi], "ok": bool(not np.isnan(rho) and rho >= RHO_MIN),
                "rho_original_argsort": sp_argsort(a, b) if nc >= 3 else None,
                "boot_share_ge_0.9": float(np.mean([x >= RHO_MIN for x in bs if not np.isnan(x)])),
                "clusters_A": len(keysA), "clusters_B": len(keysB)}

    c1 = spearman_block("dev_vs_con", dev, con, new, new, "dev", "con")
    c2 = spearman_block("er_vs_hub", er, hub, new, new, "er", "hub")
    d = spearman_block("p4h3_vs_d07", kn, ko, new, old, "all", "old")
    res["c"] = {"pass": c1["ok"] and c2["ok"], "dev_vs_con": c1, "er_vs_hub": c2}
    res["d"] = {"pass": d["ok"], **d}

    # descriptive: on_path median per split
    res["desc_onpath_by_split"] = {ROW_NAME[row]: {"dev": med(pooled(new, dev, (*row, "on_path"))), "con": med(pooled(new, con, (*row, "on_path"))),
                                                   "er": med(pooled(new, er, (*row, "on_path"))), "hub": med(pooled(new, hub, (*row, "on_path")))} for row in ROWS}
    res["verdict"] = "CONFIRMED on the sealed bank P4-H3" if (res["a"]["pass"] and res["b"]["pass"] and res["c"]["pass"] and res["d"]["pass"]) else "NOT CONFIRMED on the sealed bank P4-H3"
    res["criteria"] = {k: res[k]["pass"] for k in "abcd"}
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1), encoding="utf-8")

    L = ["# P4-H3 sealed confirmatory run of RQ4.3: analyzer output", "",
         f"Bank P4-H3 (development + confirmatory, 40 topologies), plugin, T = 2000, seed_base 90261103. Bootstrap: B = {B} topology-cluster resamples, seed {SEED}.", "",
         "## Cell table (all 40 topologies)", "",
         "| damage | lag | role | n pairs | clusters | median [95% CI] | share >0.2 | D-07 median | dev | con | ER | hub |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for t in table:
        L.append(f"| {t['damage']} | {'contemp.' if t['lag']=='c' else 'lagged'} | {t['role']} | {t['n']} | {t['clusters']}{'' if t['evaluable'] else ' (NOT evaluable)'} | "
                 f"{t['median']:.3f} [{t['ci95'][0]:.3f}, {t['ci95'][1]:.3f}] | {t['share_gt_0.2']:.2f} | {t['d07_median']:.3f} | "
                 f"{t['dev_median']:.3f} ({t['dev_clusters']}) | {t['con_median']:.3f} ({t['con_clusters']}) | {t['er_median']:.3f} ({t['er_clusters']}) | {t['hub_median']:.3f} ({t['hub_clusters']}) |")
    L += ["", "## (a) on_path at least 3x every other role", "", "| row | role | ratio on_path / role | ok | one-sided boot p |", "|---|---|---|---|---|"]
    for rn, v in a_rows.items():
        for r, dd in v["detail"].items():
            rt = dd.get("ratio")
            L.append(f"| {rn} | {r} | {'inf' if rt is None else f'{rt:.1f}'} | {dd['ok']} | {dd.get('p', float('nan')):.4f} |")
    L += ["", f"(a) pass = {res['a']['pass']}", "", "## (b) on_path median within +/-0.15 of D-07 (doc values)", "", "| row | median [95% CI] | ref | diff | ok | TOST p |", "|---|---|---|---|---|---|"]
    for rn, v in b_rows.items():
        L.append(f"| {rn} | {v['median']:.3f} [{v['ci95'][0]:.3f}, {v['ci95'][1]:.3f}] | {v['ref']:.2f} | {v['diff']:+.3f} | {v['ok']} | {v['tost_p']:.4f} |")
    L += ["", f"(b) pass = {res['b']['pass']}", "", "## (c) stability and (d) transfer (Spearman over role-by-row median costs)", "",
          "| comparison | rho | cells | 95% CI | share of draws >= 0.9 | ok |", "|---|---|---|---|---|---|"]
    for nm, v in (("dev vs con", c1), ("ER vs hub", c2), ("P4-H3 vs D-07", d)):
        L.append(f"| {nm} | {v['rho']:.3f} | {v['cells']} | [{v['ci95'][0]:.3f}, {v['ci95'][1]:.3f}] | {v['boot_share_ge_0.9']:.2f} | {v['ok']} |")
    L += ["", f"(c) pass = {res['c']['pass']}; (d) pass = {res['d']['pass']}", "",
          f"## Holm (alpha 0.05) over {res['holm']['m']} one-sided bootstrap tests (a: {res['holm']['a_m']}, b: {res['holm']['b_m']})", "",
          f"Rejected: {res['holm']['rejected']}/{res['holm']['m']} (a {res['holm']['a_rejected']}/{res['holm']['a_m']}, b {res['holm']['b_rejected']}/{res['holm']['b_m']}).", "",
          f"## Verdict: {res['verdict']}", "", f"Criteria: {res['criteria']}"]
    (OUT / "summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[-14:]))


if __name__ == "__main__":
    main()
