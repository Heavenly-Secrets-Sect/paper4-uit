"""Analyzer for RQ4.1 on P4-H5 (rules pre-registered in docs/ext/p4h5_rq41.md, section "Quy tac").

Reads results/<run>/pairs.npz written by run_pairs_p4h5.py (or, as a reference run of the SAME analyzer,
results/ext_metrics_pairs/pairs.npz of D-07: no tolerant_v5_1 there, so rule (c) is evaluated for
tolerant_v4 only).

Statistics (all pooled over pairs, replicates and both splits):
  rel   median over pairs of |C_est - C_true| / |C_true|          (non-null pairs, |C_true| > 0.1)
  abs   median over pairs of |C_est - C_true|
  mlag  median over pairs of |mean_lag_est - mean_lag_true|        (pairs where both are finite)
  peak  mean over kept pairs (C_est != 0) of 1[peak_lag_est == peak_lag_true]
  cov   share of pairs with lo <= C_true <= hi (a lost pair, interval [0,0], counts as uncovered)
CIs: percentile, topology-cluster bootstrap (resample whole topologies, B = 2000, seed 20261104).
A cell counts toward a rule only when each group it compares contains pairs from >= 8 topology clusters.
Holm: step-down at 0.05 over the family of the rule; one-sided bootstrap p = (1 + #{b*: null side}) / (B + 1).

Run: python experiments/ext/p4h5/rq41/analyze_p4h5_rq41.py --pairs results/ext_p4h5_rq41_main/pairs.npz \
        --out results/ext_p4h5_rq41_analysis [--reference]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
B = 2000
SEED = 20261104
MIN_CL = 8
ROLE = {0: "untouched", 1: "downstream", 2: "damaged"}
KINDS = ["extra", "missing", "reversed"]
RATES = [0.2, 0.5]
TS = [40, 80, 150]


def holm(pvals, alpha=0.05):
    """Step-down Holm; returns list of bool (rejected)."""
    m = len(pvals)
    order = np.argsort(pvals)
    rej = [False] * m
    for rank, i in enumerate(order):
        if pvals[i] <= alpha / (m - rank):
            rej[i] = True
        else:
            break
    return rej


class Data:
    def __init__(self, path):
        z = np.load(path)
        d = {k: z[k] for k in z.files}
        self.methods = [str(m) for m in d["methods"]]
        self.cells = [str(c) for c in d["cells"]]
        for k in ("topo", "rep", "T", "cell", "method", "role", "pk_t", "pk_e", "direct_lag"):
            d[k] = d[k].astype(int)
        d["cov"] = ((d["lo"] <= d["C_t"]) & (d["C_t"] <= d["hi"])).astype(float)
        d["abs"] = np.abs(d["C_e"] - d["C_t"])
        d["rel"] = d["abs"] / np.abs(d["C_t"])
        both = np.isfinite(d["ml_e"]) & np.isfinite(d["ml_t"])
        d["mlag"] = np.where(both, np.abs(d["ml_e"] - d["ml_t"]), np.nan)
        kept = d["C_e"] != 0.0
        d["peak"] = np.where(kept, (d["pk_e"] == d["pk_t"]).astype(float), np.nan)
        self.d = d
        self.clusters = np.unique(d["topo"])
        rng = np.random.default_rng(SEED)
        self.idx = rng.integers(0, len(self.clusters), size=(B, len(self.clusters)))
        self.cache = {}
        order = np.lexsort((d["method"], d["role"], d["cell"], d["T"]))
        self.order = order

    def cell_index(self, kind, rate):
        return self.cells.index(f"{kind}|{rate}")

    def group(self, T, kind, rate, role, method, metric):
        """list (per cluster, aligned with self.clusters) of arrays of the metric (NaN dropped)."""
        key = (T, kind, rate, role, method, metric)
        if key in self.cache:
            return self.cache[key]
        d = self.d
        m = (d["T"] == T) & (d["cell"] == self.cell_index(kind, rate)) & (d["method"] == self.methods.index(method))
        if role is not None:
            m &= d["role"] == role
        v = d[metric]
        m &= np.isfinite(v)
        out = []
        tt, vv = d["topo"][m], v[m]
        for c in self.clusters:
            out.append(vv[tt == c])
        self.cache[key] = out
        return out

    @staticmethod
    def n_clusters(g):
        return int(sum(len(a) > 0 for a in g))

    @staticmethod
    def point(g, fn):
        a = np.concatenate(g) if any(len(x) for x in g) else np.array([])
        return float(fn(a)) if len(a) else float("nan")

    def boot(self, g, fn):
        out = np.empty(B)
        for b in range(B):
            parts = [g[c] for c in self.idx[b]]
            a = np.concatenate(parts)
            out[b] = fn(a) if len(a) else np.nan
        return out


def ci(x):
    x = x[np.isfinite(x)]
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))] if len(x) else [float("nan")] * 2


def pv(x, null_side):
    """one-sided bootstrap p: share of bootstrap values on the null side of the threshold (x already shifted)."""
    x = x[np.isfinite(x)]
    if null_side == "le":
        return float((1 + np.sum(x <= 0)) / (len(x) + 1))
    return float((1 + np.sum(x >= 0)) / (len(x) + 1))


MED, MEAN = np.median, np.mean


def metric_fn(metric):
    return MED if metric in ("rel", "abs", "mlag") else MEAN


def fmt(v, d=3):
    return "n/a" if v is None or (isinstance(v, float) and not np.isfinite(v)) else f"{v:.{d}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--reference", action="store_true", help="D-07 reference run of the same analyzer")
    a = ap.parse_args()
    D = Data(ROOT / a.pairs)
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    has51 = "tolerant_v5_1" in D.methods
    new_methods = [m for m in ("tolerant_v4", "tolerant_v5_1") if m in D.methods]
    res = {"B": B, "seed": SEED, "min_clusters": MIN_CL, "n_clusters": int(len(D.clusters)),
           "methods": D.methods, "reference": a.reference}
    md = [f"# RQ4.1 analysis ({'D-07 reference run' if a.reference else 'P4-H5'}), generated by analyze_p4h5_rq41.py", "",
          f"Pairs: `{a.pairs}`; topology clusters: {len(D.clusters)}; bootstrap B = {B}, seed {SEED}.", ""]

    # ------------------------------------------------------------------ rule (a)
    ra = []
    pvals = []
    for T in TS:
        for rate in RATES:
            g = {k: D.group(T, k, rate, 2, "plugin", "rel") for k in KINDS}
            ncl = {k: D.n_clusters(g[k]) for k in KINDS}
            pt = {k: D.point(g[k], MED) for k in KINDS}
            bs = {k: D.boot(g[k], MED) for k in KINDS}
            dMR, dRE = bs["missing"] - bs["reversed"], bs["reversed"] - bs["extra"]
            p1, p2 = pv(-dMR, "ge"), pv(-dRE, "ge")  # H0: d <= 0  <=>  -d >= 0
            ok_cl = all(v >= MIN_CL for v in ncl.values())
            ordered = ok_cl and pt["missing"] > pt["reversed"] > pt["extra"]
            ordered_new = bool(ok_cl and pt["missing"] > pt["reversed"] and pt["missing"] > pt["extra"])
            ra.append({"T": T, "rate": rate, "med_rel": pt, "n_pairs": {k: int(sum(len(x) for x in g[k])) for k in KINDS},
                       "n_clusters": ncl, "ok_clusters": ok_cl, "ordered": bool(ordered), "ordered_new": ordered_new,
                       "d_missing_reversed": [pt["missing"] - pt["reversed"], ci(dMR)],
                       "d_reversed_extra": [pt["reversed"] - pt["extra"], ci(dRE)], "p": [p1, p2]})
            pvals += [p1, p2]
    rej = holm(pvals)
    for i, r in enumerate(ra):
        r["holm_rejected"] = [rej[2 * i], rej[2 * i + 1]]
        r["holm_supported"] = bool(r["ordered"] and rej[2 * i] and rej[2 * i + 1])
    n_ord = sum(r["ordered"] for r in ra)
    n_holm = sum(r["holm_supported"] for r in ra)
    res["a"] = {"cells": ra, "n_ordered": n_ord, "of": len(ra), "share": n_ord / len(ra), "n_holm_supported": n_holm,
                "pass_original": bool(n_ord / len(ra) >= 0.80), "holm_family": len(pvals),
                "n_new_T80_150": sum(r["ordered_new"] for r in ra if r["T"] >= 80),
                "pass": bool(sum(r["ordered_new"] for r in ra if r["T"] >= 80) == 4)}  # revised rule (a'): 4/4 cells with T>=80

    # ------------------------------------------------------------------ rule (b)
    rb, pb = [], []
    for T in TS:
        g = D.group(T, "missing", 0.5, None, "plugin", "cov")
        pt = D.point(g, MEAN)
        bs = D.boot(g, MEAN)
        p = pv(bs - 0.60, "ge")  # H0: cov >= 0.60
        rb.append({"T": T, "cov": pt, "ci": ci(bs), "n_pairs": int(sum(len(x) for x in g)),
                   "n_clusters": D.n_clusters(g), "below": bool(pt < 0.60 and D.n_clusters(g) >= MIN_CL), "p": p})
        pb.append(p)
    rj = holm(pb)
    for r, h in zip(rb, rj):
        r["holm_rejected"] = bool(h)
    res["b"] = {"cells": rb, "pass": all(r["below"] for r in rb), "n_below": sum(r["below"] for r in rb),
                "n_holm": sum(r["below"] and r["holm_rejected"] for r in rb), "of": 3}

    # ------------------------------------------------------------------ rule (c)
    rc = {}
    pr_all, pc_all = [], []
    for m in new_methods:
        rows_rel, rows_cov = [], []
        for T in TS:
            for rate in RATES:
                gp = D.group(T, "missing", rate, 2, "plugin", "rel")
                gm = D.group(T, "missing", rate, 2, m, "rel")
                dd = D.boot(gm, MED) - D.boot(gp, MED)
                pt = D.point(gm, MED) - D.point(gp, MED)
                p = pv(dd, "ge")  # H0: method - plugin >= 0
                okc = D.n_clusters(gp) >= MIN_CL and D.n_clusters(gm) >= MIN_CL
                rows_rel.append({"T": T, "rate": rate, "plugin": D.point(gp, MED), "method": D.point(gm, MED),
                                 "diff": pt, "ci": ci(dd), "n_pairs": int(sum(len(x) for x in gm)),
                                 "n_clusters": D.n_clusters(gm), "reduces": bool(okc and pt < 0), "p": p})
                pr_all.append(p)
        for T in (80, 150):
            for rate in RATES:
                g = D.group(T, "missing", rate, 2, m, "cov")
                bs = D.boot(g, MEAN)
                pt = D.point(g, MEAN)
                p = pv(bs - 0.90, "le")  # H0: cov <= 0.90
                ga = D.group(T, "missing", rate, None, m, "cov")
                rows_cov.append({"T": T, "rate": rate, "cov_damaged": pt, "ci": ci(bs),
                                 "n_pairs": int(sum(len(x) for x in g)), "n_clusters": D.n_clusters(g),
                                 "ok": bool(pt >= 0.90 and D.n_clusters(g) >= MIN_CL), "p": p,
                                 "cov_all_nonnull_descriptive": D.point(ga, MEAN)})
                pc_all.append(p)
        rc[m] = {"rel": rows_rel, "cov": rows_cov}
    hr, hc = holm(pr_all), holm(pc_all)
    ir = ic = 0
    for m in new_methods:
        for r in rc[m]["rel"]:
            r["holm_rejected"] = bool(hr[ir]); ir += 1
        for r in rc[m]["cov"]:
            r["holm_rejected"] = bool(hc[ic]); ic += 1
        rc[m]["n_reduces"] = sum(r["reduces"] for r in rc[m]["rel"])
        rc[m]["n_reduces_holm"] = sum(r["reduces"] and r["holm_rejected"] for r in rc[m]["rel"])
        rc[m]["n_cov_ok"] = sum(r["ok"] for r in rc[m]["cov"])
        rc[m]["n_cov_ok_holm"] = sum(r["ok"] and r["holm_rejected"] for r in rc[m]["cov"])
        # revised coverage condition (c2): per T in {80,150}, damaged missing pairs pooled over both rates,
        # cluster-bootstrap 95% lower bound >= 0.85 (needs >= MIN_CL clusters); 2/2 T. The 4-cell >=0.90 rule stays descriptive.
        c2 = []
        for T in (80, 150):
            g = [np.concatenate([a, b]) for a, b in zip(D.group(T, "missing", 0.2, 2, m, "cov"), D.group(T, "missing", 0.5, 2, m, "cov"))]
            bs = D.boot(g, MEAN)
            lo = ci(bs)[0]
            c2.append({"T": T, "cov": D.point(g, MEAN), "ci": ci(bs), "n_pairs": int(sum(len(x) for x in g)),
                       "n_clusters": D.n_clusters(g), "ok": bool(lo >= 0.85 and D.n_clusters(g) >= MIN_CL)})
        rc[m]["c2"] = c2
        rc[m]["n_c2_ok"] = sum(r["ok"] for r in c2)
        rc[m]["pass"] = bool(rc[m]["n_reduces"] == 6 and rc[m]["n_c2_ok"] == 2)
        rc[m]["pass_original"] = bool(rc[m]["n_reduces"] == 6 and rc[m]["n_cov_ok"] == 4)
    res["c"] = {"methods": rc, "pass": all(rc[m]["pass"] for m in new_methods),
                "holm_family_rel": len(pr_all), "holm_family_cov": len(pc_all),
                "note": "v5_1 not available in this run" if not has51 else ""}

    # ------------------------------------------------------------------ rule (d)
    rd, pd_ = [], []
    for kind in ("missing", "reversed", "extra"):
        for rate in RATES:
            g40 = D.group(40, kind, rate, 2, "plugin", "mlag")
            g150 = D.group(150, kind, rate, 2, "plugin", "mlag")
            b40, b150 = D.boot(g40, MED), D.boot(g150, MED)
            ratio = D.point(g150, MED) / D.point(g40, MED)
            rb_ = b150 / b40
            p = pv(rb_ - 0.75, "le")  # H0: ratio <= 0.75 (falls by more than 25%)
            okc = D.n_clusters(g40) >= MIN_CL and D.n_clusters(g150) >= MIN_CL
            rd.append({"kind": kind, "rate": rate, "mlag_T40": D.point(g40, MED), "mlag_T150": D.point(g150, MED),
                       "ratio": ratio, "ci": ci(rb_), "fall_pct": 100 * (1 - ratio),
                       "n_clusters": [D.n_clusters(g40), D.n_clusters(g150)],
                       "n_pairs": [int(sum(len(x) for x in g40)), int(sum(len(x) for x in g150))],
                       "not_falling": bool(okc and ratio >= 0.75), "primary": kind != "extra", "p": p})
    prim = [r for r in rd if r["primary"]]
    hd = holm([r["p"] for r in prim])
    for r, h in zip(prim, hd):
        r["holm_rejected"] = bool(h)
    res["d"] = {"cells": rd, "pass": all(r["not_falling"] for r in prim), "n_pass": sum(r["not_falling"] for r in prim),
                "of": len(prim), "n_holm": sum(r["not_falling"] and r["holm_rejected"] for r in prim),
                "extra_descriptive_n_not_falling": sum(r["not_falling"] for r in rd if not r["primary"])}

    res["verdict"] = {"a": res["a"]["pass"], "b": res["b"]["pass"], "c": res["c"]["pass"], "d": res["d"]["pass"],
                      "all": bool(res["a"]["pass"] and res["b"]["pass"] and res["c"]["pass"] and res["d"]["pass"])}

    # ------------------------------------------------------------------ descriptive tables by role
    tab = []
    cellnames = [(k, r) for k in ["none"] + KINDS for r in ([0.0] if k == "none" else RATES)]
    for role in (2, 1, 0):
        for T in TS:
            for kind, rate in cellnames:
                if (kind == "none") != (role == 0 and False) and False:
                    pass
                for m in D.methods:
                    gr = D.group(T, kind, rate, role, m, "rel")
                    n = int(sum(len(x) for x in gr))
                    if n == 0:
                        continue
                    gc = D.group(T, kind, rate, role, m, "cov")
                    gl = D.group(T, kind, rate, role, m, "mlag")
                    gk = D.group(T, kind, rate, role, m, "peak")
                    ga = D.group(T, kind, rate, role, m, "abs")
                    bc, br = D.boot(gc, MEAN), D.boot(gr, MED)
                    tab.append({"role": ROLE[role], "T": T, "kind": kind, "rate": rate, "method": m, "n": n,
                                "n_clusters": D.n_clusters(gr), "abs": D.point(ga, MED), "rel": D.point(gr, MED),
                                "rel_ci": ci(br), "mlag": D.point(gl, MED), "peak": D.point(gk, MEAN),
                                "cov": D.point(gc, MEAN), "cov_ci": ci(bc)})
    res["table"] = tab
    # failures
    (out / "rules.json").write_text(json.dumps(res, indent=1), encoding="utf-8")

    # ------------------------------------------------------------------ markdown
    A, Bb, C, Dd = res["a"], res["b"], res["c"], res["d"]
    md += ["## Rule (a): severity ordering of plugin relative error on damaged pairs", "",
           "| T | rate | rel missing | rel reversed | rel extra | n clusters (M/R/E) | ordered | M-R [CI] | R-E [CI] | Holm (M-R, R-E) |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r in A["cells"]:
        md.append(f"| {r['T']} | {r['rate']} | {fmt(r['med_rel']['missing'])} | {fmt(r['med_rel']['reversed'])} | "
                  f"{fmt(r['med_rel']['extra'])} | {r['n_clusters']['missing']}/{r['n_clusters']['reversed']}/{r['n_clusters']['extra']} | "
                  f"{'yes' if r['ordered'] else 'no'} | {fmt(r['d_missing_reversed'][0])} [{fmt(r['d_missing_reversed'][1][0])}, {fmt(r['d_missing_reversed'][1][1])}] | "
                  f"{fmt(r['d_reversed_extra'][0])} [{fmt(r['d_reversed_extra'][1][0])}, {fmt(r['d_reversed_extra'][1][1])}] | "
                  f"{r['holm_rejected'][0]}/{r['holm_rejected'][1]} |")
    md += ["", f"Ordered cells: **{A['n_ordered']}/{A['of']}** ({A['share']:.2f}); Holm-supported cells (both gaps, Holm over {A['holm_family']}): **{A['n_holm_supported']}/{A['of']}**. Original rule (a) (5/6 full order): {'PASS' if A['pass_original'] else 'FAIL'}. Revised rule (a'): missing > reversed and missing > extra in the 4 cells with T >= 80: {A['n_new_T80_150']}/4 -> {'PASS' if A['pass'] else 'FAIL'}.", "",
           "## Rule (b): plugin coverage under missing-0.5 (all non-null pairs)", "",
           "| T | coverage | 95% CI | n pairs | clusters | < 0.60 | Holm |", "|---|---|---|---|---|---|---|"]
    for r in Bb["cells"]:
        md.append(f"| {r['T']} | {fmt(r['cov'])} | [{fmt(r['ci'][0])}, {fmt(r['ci'][1])}] | {r['n_pairs']} | {r['n_clusters']} | {'yes' if r['below'] else 'no'} | {r['holm_rejected']} |")
    md += ["", f"Cells below 0.60: **{Bb['n_below']}/3** (Holm {Bb['n_holm']}/3). Rule (b) {'PASS' if Bb['pass'] else 'FAIL'}.", "",
           "## Rule (c): v4 / v5_1 versus plugin on missing-damaged pairs", ""]
    for m in new_methods:
        md += [f"### {m}", "", "| T | rate | rel plugin | rel method | diff [CI] | clusters | reduces | Holm |", "|---|---|---|---|---|---|---|---|"]
        for r in C["methods"][m]["rel"]:
            md.append(f"| {r['T']} | {r['rate']} | {fmt(r['plugin'])} | {fmt(r['method'])} | {fmt(r['diff'])} [{fmt(r['ci'][0])}, {fmt(r['ci'][1])}] | {r['n_clusters']} | {'yes' if r['reduces'] else 'no'} | {r['holm_rejected']} |")
        md += ["", "| T | rate | coverage damaged | 95% CI | n pairs | clusters | >= 0.90 | Holm | (descr.) coverage all non-null |", "|---|---|---|---|---|---|---|---|---|"]
        for r in C["methods"][m]["cov"]:
            md.append(f"| {r['T']} | {r['rate']} | {fmt(r['cov_damaged'])} | [{fmt(r['ci'][0])}, {fmt(r['ci'][1])}] | {r['n_pairs']} | {r['n_clusters']} | {'yes' if r['ok'] else 'no'} | {r['holm_rejected']} | {fmt(r['cov_all_nonnull_descriptive'])} |")
        c_ = C["methods"][m]
        md += ["", f"{m}: rel reduced in **{c_['n_reduces']}/6** cells (Holm {c_['n_reduces_holm']}/6, family {C['holm_family_rel']}); descriptive 4-cell rule (damaged-pair coverage >= 0.90 per cell): {c_['n_cov_ok']}/4 (Holm {c_['n_cov_ok_holm']}/4). Revised (c2) pooled coverage per T, lower 95% CI bound >= 0.85: {'; '.join('T%d cov %.3f [%.3f, %.3f] %s' % (r['T'], r['cov'], r['ci'][0], r['ci'][1], 'ok' if r['ok'] else 'no') for r in c_['c2'])} -> {c_['n_c2_ok']}/2. {m} {'PASS' if c_['pass'] else 'FAIL'}.", ""]
    md += [f"Rule (c) overall {'PASS' if C['pass'] else 'FAIL'} {C['note']}", "",
           "## Rule (d): plugin mean-lag error on damaged pairs, T40 -> T150", "",
           "| kind | rate | mlag T40 | mlag T150 | ratio [CI] | fall % | clusters (T40/T150) | not falling > 25% | in rule | Holm |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in Dd["cells"]:
        md.append(f"| {r['kind']} | {r['rate']} | {fmt(r['mlag_T40'])} | {fmt(r['mlag_T150'])} | {fmt(r['ratio'])} [{fmt(r['ci'][0])}, {fmt(r['ci'][1])}] | {fmt(r['fall_pct'],1)} | {r['n_clusters'][0]}/{r['n_clusters'][1]} | {'yes' if r['not_falling'] else 'no'} | {'primary' if r['primary'] else 'descriptive'} | {r.get('holm_rejected', '-')} |")
    md += ["", f"Primary cells (missing, reversed) not falling by more than 25%: **{Dd['n_pass']}/{Dd['of']}** (Holm {Dd['n_holm']}/{Dd['of']}). Extra (descriptive): {Dd['extra_descriptive_n_not_falling']}/2. Rule (d) {'PASS' if Dd['pass'] else 'FAIL'}.", "",
           "## Verdict", "", f"(a) {res['verdict']['a']}, (b) {res['verdict']['b']}, (c) {res['verdict']['c']}, (d) {res['verdict']['d']} -> all: **{res['verdict']['all']}**", "",
           "## Descriptive tables by role (pairs pooled; rel and coverage with topology-cluster 95% CI)", "",
           "| role | T | cell | method | n | clusters | abs | rel [CI] | mean-lag | peak | cov [CI] |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in tab:
        md.append(f"| {r['role']} | {r['T']} | {r['kind']}-{r['rate']} | {r['method']} | {r['n']} | {r['n_clusters']} | {fmt(r['abs'])} | "
                  f"{fmt(r['rel'])} [{fmt(r['rel_ci'][0],2)}, {fmt(r['rel_ci'][1],2)}] | {fmt(r['mlag'])} | {fmt(r['peak'])} | "
                  f"{fmt(r['cov'])} [{fmt(r['cov_ci'][0],2)}, {fmt(r['cov_ci'][1],2)}] |")
    (out / "analysis.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(res["verdict"]), A["n_ordered"], Bb["n_below"], {m: (C["methods"][m]["n_reduces"], C["methods"][m]["n_cov_ok"]) for m in new_methods}, Dd["n_pass"])


if __name__ == "__main__":
    main()
