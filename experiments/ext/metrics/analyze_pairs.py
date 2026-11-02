"""Analysis of results/ext_metrics_pairs/pairs.npz (written by run_pairs.py).

1. Validity check: pooled counts per run must equal the stored a2_baselines / a2b_pselect rows.
2. RQ4.1 pair-level tables: error, lag error, coverage, width and interval score by role of the
   pair (damaged / downstream / untouched) and by the true lag of its direct edge.
3. RQ4.4: AUROC of truth-free signals for misses of the module interval, with bootstrap CIs
   clustered by topology, a grouped-CV logistic combination and the pre-registered rel_width > 2
   flag (rules in docs/ext/metrics.md, written before the run).

Run:  python experiments/ext/metrics/analyze_pairs.py
Writes results/ext_metrics_pairs/{check.txt, rq41_pairs.md, rq41_pairs.json} and
results/ext_metrics_flags/{summary.md, summary.json}.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
PAIRS = ROOT / "results" / "ext_metrics_pairs"
FLAGS = ROOT / "results" / "ext_metrics_flags"
ROLE = {0: "untouched", 1: "downstream", 2: "damaged"}
N_BOOT = 1000
SIGNALS = ("rel_width", "width", "zero_in", "struct_sens", "resid_lb", "rx_pair", "rx_end", "coef_stab", "lag_stab",
           "n_repair", "n_pool", "n_resid_bh")


def load():
    z = np.load(PAIRS / "pairs.npz")
    d = {k: z[k] for k in z.files}
    d["methods"] = [str(m) for m in d["methods"]]
    d["cells"] = [str(c) for c in d["cells"]]
    for k in ("topo", "rep", "T", "cell", "method", "j", "i", "direct_lag", "role", "pk_t", "pk_e"):
        d[k] = d[k].astype(int)
    d["covered"] = (d["lo"] <= d["C_t"]) & (d["C_t"] <= d["hi"])
    d["lost"] = d["C_e"] == 0.0
    w = d["hi"] - d["lo"]
    a = 0.05
    d["IS"] = w + (2 / a) * np.maximum(d["lo"] - d["C_t"], 0) + (2 / a) * np.maximum(d["C_t"] - d["hi"], 0)
    d["width"] = w
    d["abs"] = np.abs(d["C_e"] - d["C_t"])
    d["rel"] = d["abs"] / np.abs(d["C_t"])
    return d


# ----------------------------------------------------------------------------- validity check

def check(d):
    sys.path.insert(0, str(ROOT / "experiments"))
    rows = []
    for name in ("a2_baselines", "a2b_pselect"):
        with open(ROOT / "results" / name / "runs.jsonl", encoding="utf-8") as fh:
            rows += [json.loads(line) for line in fh]
    man = json.loads((ROOT / "results" / "a2_baselines" / "manifest.json").read_text())
    topo_ids = [t["id"] for t in man["topologies"]]
    idx = {(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"], r["method"]): r for r in rows
           if r["status"] == "ok" and r.get("scenario", "clean") == "clean"}
    key = d["topo"] * 10 ** 6 + d["rep"] * 10 ** 5 + d["T"] * 100 + d["cell"] * 10 + d["method"]
    order = np.argsort(key, kind="stable")
    uk, start = np.unique(key[order], return_index=True)
    bounds = list(start) + [len(order)]
    n, bad, missing = 0, 0, 0
    for u, s, e in zip(uk, bounds[:-1], bounds[1:]):
        sel = order[s:e]
        t, rep, T, c, m = d["topo"][sel[0]], d["rep"][sel[0]], d["T"][sel[0]], d["cell"][sel[0]], d["method"][sel[0]]
        kind, rate = d["cells"][c].split("|")
        r = idx.get((topo_ids[t], rep, T, kind, float(rate), d["methods"][m]))
        if r is None:
            missing += 1
            continue
        n += 1
        ok = (r["n_nonnull"] == len(sel) and r["n_lost"] == int(d["lost"][sel].sum())
              and (r.get("n_covered_nonnull") is None or r["n_covered_nonnull"] == int(d["covered"][sel].sum())))
        bad += not ok
    msg = f"runs compared: {n}; mismatches: {bad}; runs without a stored row: {missing}"
    (PAIRS / "check.txt").write_text(msg + "\n", encoding="utf-8")
    return msg


# ----------------------------------------------------------------------------- cluster bootstrap

def boot_weights(n_topo, rng, n_boot=N_BOOT):
    return np.stack([np.bincount(rng.integers(0, n_topo, n_topo), minlength=n_topo) for _ in range(n_boot)])


def cluster_ci_ratio(num, den, topo, W):
    """Ratio of sums (e.g. coverage) with a percentile CI over topology-resampling weights W."""
    nt = W.shape[1]
    sn = np.bincount(topo, weights=num, minlength=nt)
    sd = np.bincount(topo, weights=den, minlength=nt)
    est = sn.sum() / sd.sum() if sd.sum() else np.nan
    with np.errstate(invalid="ignore", divide="ignore"):
        b = (W @ sn) / (W @ sd)
    return est, np.nanquantile(b, 0.025), np.nanquantile(b, 0.975)


# ----------------------------------------------------------------------------- RQ4.1 tables

def pair_stats(d, sel):
    if not sel.any():
        return None
    kept = sel & ~d["lost"]
    lagok = kept & np.isfinite(d["ml_t"]) & np.isfinite(d["ml_e"])
    pk = kept & (d["pk_e"] >= 0)
    has_int = sel & np.isfinite(d["lo"])
    return {
        "n": int(sel.sum()),
        "abs": float(np.median(d["abs"][sel])),
        "rel": float(np.median(d["rel"][sel])),
        "sign": float(np.mean(np.sign(d["C_e"][kept]) != np.sign(d["C_t"][kept]))) if kept.any() else None,
        "lost": float(d["lost"][sel].mean()),
        "mlag": float(np.median(np.abs(d["ml_e"][lagok] - d["ml_t"][lagok]))) if lagok.any() else None,
        "peak": float(np.mean(d["pk_e"][pk] == d["pk_t"][pk])) if pk.any() else None,
        "cov": float(d["covered"][has_int].mean()) if has_int.any() else None,
        "width": float(np.median(d["width"][has_int & ~d["lost"]])) if (has_int & ~d["lost"]).any() else None,
        "IS": float(np.mean(d["IS"][has_int])) if has_int.any() else None,
    }


def f(v, k=3):
    return "–" if v is None or (isinstance(v, float) and not np.isfinite(v)) else f"{v:.{k}f}"


def rq41(d, rng):
    M = {m: i for i, m in enumerate(d["methods"])}
    C = {c: i for i, c in enumerate(d["cells"])}
    show = ["oracle", "plugin", "lp_allpast", "ida_union", "bvar_minnesota", "pselect_union", "tolerant_v4"]
    out_json = {}
    lines = ["# RQ4.1 pair-level error characterisation (ext_metrics_pairs, D-07 development)", "",
             "Pooled over non-null pairs (|C| > 0.1) of 20 topologies x 3 replicates. `abs`, `rel`: median |error|, "
             "median |error|/|C|. `sign`: share of kept pairs (estimate != 0) with the wrong sign. `lost`: share with "
             "estimate exactly 0. `mean-lag`: median |mean-lag error| where both are defined. `peak`: peak-lag hit "
             "rate among kept pairs. `cov`: coverage; `width`: median width (kept pairs); `IS`: mean interval score.",
             ""]
    hdr = "| T | damage | role | method | n | abs | rel | sign | lost | mean-lag | peak | cov | width | IS |"
    sep = "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"

    def row(T, cell, label, m, s):
        return (f"| {T} | {cell} | {label} | {m} | {s['n']} | {f(s['abs'])} | {f(s['rel'])} | {f(s['sign'])} | "
                f"{f(s['lost'])} | {f(s['mlag'])} | {f(s['peak'])} | {f(s['cov'])} | {f(s['width'])} | {f(s['IS'], 2)} |")

    # Table A: by role
    lines += ["## A. By role of the pair relative to the damaged edges", "", hdr, sep]
    for T in (40, 80, 150):
        for cell in d["cells"]:
            for role in (2, 1, 0):
                for m in show:
                    sel = (d["T"] == T) & (d["cell"] == C[cell]) & (d["method"] == M[m]) & (d["role"] == role)
                    s = pair_stats(d, sel)
                    if s is None:
                        continue
                    out_json[f"role|{T}|{cell}|{ROLE[role]}|{m}"] = s
                    lines.append(row(T, cell, ROLE[role], m, s))
    # Table B: by true lag of the direct edge, damaged pairs of missing cells, and all pairs of the undamaged cell
    lines += ["", "## B. By true lag of the pair's direct edge (`none` = no direct edge)", "",
              "Rows `none|0.0 / all`: every non-null pair on the correct skeleton. Rows `missing / damaged`: pairs whose "
              "own edge was deleted.", "",
              "| T | damage | subset | direct lag | method | n | abs | rel | sign | lost | mean-lag | peak | cov | width | IS |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for T in (40, 80, 150):
        for cell, role_sel, label in (("none|0.0", None, "all"), ("missing|0.2", 2, "damaged"),
                                      ("missing|0.5", 2, "damaged"), ("reversed|0.5", 2, "damaged")):
            for lag in (-1, 0, 1, 2):
                for m in show:
                    sel = (d["T"] == T) & (d["cell"] == C[cell]) & (d["method"] == M[m]) & (d["direct_lag"] == lag)
                    if role_sel is not None:
                        sel &= d["role"] == role_sel
                    s = pair_stats(d, sel)
                    if s is None:
                        continue
                    lab = "none" if lag == -1 else str(lag)
                    out_json[f"lag|{T}|{cell}|{label}|{lab}|{m}"] = s
                    lines.append(f"| {T} | {cell} | {label} | {lab} | {m} | {s['n']} | {f(s['abs'])} | {f(s['rel'])} | "
                                 f"{f(s['sign'])} | {f(s['lost'])} | {f(s['mlag'])} | {f(s['peak'])} | {f(s['cov'])} | "
                                 f"{f(s['width'])} | {f(s['IS'], 2)} |")
    # Table C: expectation E2 with a clustered CI: module coverage on damaged pairs, lag 0 vs lag 1-2, missing cells
    W = boot_weights(int(d["topo"].max()) + 1, rng)
    lines += ["", "## C. E2: module coverage on deleted edges, contemporaneous vs lagged (95% CI clustered by topology)",
              "", "| T | damage | method | cov lag 0 (n) | cov lag 1-2 (n) | difference lag0 - lag12 [95% CI] |",
              "|---|---|---|---|---|---|"]
    for T in (40, 80, 150):
        for cell in ("missing|0.2", "missing|0.5"):
            for m in ("tolerant_v4", "pselect_union", "bvar_minnesota", "plugin"):
                base = (d["T"] == T) & (d["cell"] == C[cell]) & (d["method"] == M[m]) & (d["role"] == 2)
                a = base & (d["direct_lag"] == 0)
                b = base & (d["direct_lag"] >= 1)
                nt = W.shape[1]
                ca = np.bincount(d["topo"][a], weights=d["covered"][a], minlength=nt)
                na = np.bincount(d["topo"][a], minlength=nt)
                cb = np.bincount(d["topo"][b], weights=d["covered"][b], minlength=nt)
                nb = np.bincount(d["topo"][b], minlength=nt)
                est = ca.sum() / na.sum() - cb.sum() / nb.sum()
                with np.errstate(invalid="ignore", divide="ignore"):
                    bt = (W @ ca) / (W @ na) - (W @ cb) / (W @ nb)
                lo, hi = np.nanquantile(bt, (0.025, 0.975))
                out_json[f"E2|{T}|{cell}|{m}"] = {"cov_lag0": ca.sum() / na.sum(), "n0": int(na.sum()),
                                                  "cov_lag12": cb.sum() / nb.sum(), "n12": int(nb.sum()),
                                                  "diff": est, "lo": lo, "hi": hi}
                lines.append(f"| {T} | {cell} | {m} | {ca.sum() / na.sum():.3f} ({na.sum()}) | "
                             f"{cb.sum() / nb.sum():.3f} ({nb.sum()}) | {est:+.3f} [{lo:+.3f}, {hi:+.3f}] |")
    # Table D: null pairs: false signals
    nulls = [json.loads(line) for line in open(PAIRS / "nullpairs.jsonl", encoding="utf-8")]
    agg = defaultdict(lambda: [0, 0])
    for r in nulls:
        a = agg[(r["T"], r["cell"], r["method"])]
        a[0] += r["n_null_excl0"]
        a[1] += r["n_null"]
    lines += ["", "## D. Null pairs (|C| <= 0.1): share whose interval excludes 0 (false signals)", "",
              "| T | damage | " + " | ".join(show) + " |", "|---|---|" + "---|" * len(show)]
    for T in (40, 80, 150):
        for c, cell in enumerate(d["cells"]):
            vals = []
            for m in show:
                a = agg.get((T, c, m))
                v = a[0] / a[1] if a and a[1] else None
                out_json[f"null|{T}|{cell}|{m}"] = v
                vals.append(f(v))
            lines.append(f"| {T} | {cell} | " + " | ".join(vals) + " |")
    (PAIRS / "rq41_pairs.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (PAIRS / "rq41_pairs.json").write_text(json.dumps(out_json, indent=1, default=float), encoding="utf-8")


# ----------------------------------------------------------------------------- RQ4.4

class WAuc:
    """AUROC of a fixed (score, label) set under many topology-resampling weight vectors."""

    def __init__(self, score, label, topo):
        self.u, self.inv = np.unique(score, return_inverse=True)
        self.y = label.astype(float)
        self.topo = topo

    def __call__(self, wt):
        w = wt[self.topo]
        P = np.bincount(self.inv, weights=w * self.y, minlength=len(self.u))
        N = np.bincount(self.inv, weights=w * (1 - self.y), minlength=len(self.u))
        tp, tn = P.sum(), N.sum()
        if tp == 0 or tn == 0:
            return np.nan
        below = np.cumsum(N) - N
        return float((P * (below + 0.5 * N)).sum() / (tp * tn))


def auc_with_ci(score, label, topo, W, strata=None):
    ones = np.ones(W.shape[1])
    pooled = WAuc(score, label, topo)
    est = pooled(ones)
    boots = np.array([pooled(w) for w in W])
    res = {"auc": est, "lo": float(np.nanquantile(boots, 0.025)), "hi": float(np.nanquantile(boots, 0.975)),
           "_boots": boots}
    if strata is not None:
        parts = []
        for s in np.unique(strata):
            sel = strata == s
            if len(np.unique(score[sel])) < 2 or label[sel].all() or not label[sel].any():
                continue
            parts.append((WAuc(score[sel], label[sel], topo[sel]), topo[sel]))
        if parts:
            def strat(w):
                vals, wts = [], []
                for a, tp in parts:
                    v = a(w)
                    if np.isfinite(v):
                        vals.append(v)
                        wts.append(w[tp].sum())
                return float(np.average(vals, weights=wts)) if vals else np.nan
            res["strat"] = strat(ones)
            sb = np.array([strat(w) for w in W])
            res["strat_lo"], res["strat_hi"] = float(np.nanquantile(sb, 0.025)), float(np.nanquantile(sb, 0.975))
            res["n_strata"] = len(parts)
    return res


def fit_logistic(X, y, l2=1e-3, iters=60):
    w = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(X @ w, -30, 30)))
        g = X.T @ (p - y) + l2 * w
        Hm = (X * (p * (1 - p))[:, None]).T @ X + l2 * np.eye(len(w))
        w -= np.linalg.solve(Hm, g)
    return w


def design(d, sel, train_median=None):
    cols, names = [], []
    for s in ("rel_width", "width", "struct_sens", "resid_lb", "coef_stab", "lag_stab"):
        cols.append(np.log1p(np.maximum(d[s][sel], 0)))
        names.append(f"log1p_{s}")
    for s in ("rx_pair", "rx_end", "zero_in", "n_repair", "n_pool", "n_resid_bh"):
        cols.append(d[s][sel])
        names.append(s)
    X = np.column_stack(cols)
    miss = ~np.isfinite(X)
    med = np.nanmedian(X, axis=0) if train_median is None else train_median
    X = np.where(miss, med, X)
    ind = miss[:, [names.index("log1p_coef_stab"), names.index("log1p_lag_stab")]].astype(float)
    kind = np.array([c.split("|")[0] for c in d["cells"]])[d["cell"][sel]]
    extra = np.column_stack([ind, np.log(d["T"][sel]), kind == "missing", kind == "reversed", kind == "extra"])
    names += ["na_coef_stab", "na_lag_stab", "logT", "stated_missing", "stated_reversed", "stated_extra"]
    return np.column_stack([X, extra.astype(float)]), names, med


def rq44(d, rng):
    FLAGS.mkdir(parents=True, exist_ok=True)
    mod = d["method"] == d["methods"].index("tolerant_v4")
    miss = ~d["covered"]
    large = d["rel"] > 0.5
    nt = int(d["topo"].max()) + 1
    W = boot_weights(nt, rng)
    strata_all = d["T"] * 10 + d["cell"]
    out = {}
    lines = ["# RQ4.4 for the module (`tolerant_v4`): truth-free flags for interval misses", "",
             "Pre-registered in docs/ext/metrics.md before the run. AUROC: higher signal = higher risk. "
             "95% CIs: bootstrap over the 20 topologies (1000 resamples). Stratified AUROC: pair-weighted mean of "
             "AUROCs within (T, damage cell), over strata where the signal varies.", ""]
    for tset_name, tset in (("T80_150", (80, 150)), ("T40", (40,))):
        base = mod & np.isin(d["T"], tset)
        for oname, outcome in (("miss", miss), ("large_err", large)):
            lines += [f"## {oname}, T in {tset}", "",
                      f"Pairs: {int(base.sum())}; base rate: {outcome[base].mean():.3f}", "",
                      "| signal | defined | AUROC pooled [95% CI] | AUROC stratified [95% CI] | R1 verdict |",
                      "|---|---|---|---|---|"]
            for s in SIGNALS:
                sel = base & np.isfinite(d[s])
                r = auc_with_ci(d[s][sel], outcome[sel], d["topo"][sel], W, strata_all[sel])
                predictive = r["lo"] > 0.5 and r.get("strat_lo", 0) > 0.5
                verdict = ("useful" if predictive and r["auc"] >= 0.65 else "predictive" if predictive
                           else "inverse" if r["hi"] < 0.5 else "no")
                out[f"{tset_name}|{oname}|{s}"] = {k: v for k, v in r.items() if not k.startswith("_")} | {
                    "defined": float(sel.sum() / base.sum()), "verdict": verdict}
                st = (f"{r['strat']:.3f} [{r['strat_lo']:.3f}, {r['strat_hi']:.3f}] ({r['n_strata']} strata)"
                      if "strat" in r else "–")
                lines.append(f"| {s} | {sel.sum() / base.sum():.2f} | {r['auc']:.3f} [{r['lo']:.3f}, {r['hi']:.3f}] | "
                             f"{st} | {verdict} |")
            # combined, grouped 5-fold CV by topology
            idx = np.nonzero(base)[0]
            y = outcome[idx].astype(float)
            fold = d["topo"][idx] % 5
            oof = np.zeros(len(idx))
            for k in range(5):
                tr, te = fold != k, fold == k
                Xtr, names, med = design(d, idx[tr])
                mu, sd = Xtr.mean(axis=0), Xtr.std(axis=0) + 1e-9
                w = fit_logistic(np.column_stack([np.ones(tr.sum()), (Xtr - mu) / sd]), y[tr])
                Xte, _, _ = design(d, idx[te], med)
                oof[te] = np.column_stack([np.ones(te.sum()), (Xte - mu) / sd]) @ w
            topo = d["topo"][idx]
            rc = auc_with_ci(oof, y.astype(bool), topo, W, strata_all[idx])
            rw = auc_with_ci(d["rel_width"][idx], y.astype(bool), topo, W)
            delta = rc["_boots"] - rw["_boots"]
            dlo, dhi = np.nanquantile(delta, (0.025, 0.975))
            Xall, names, _ = design(d, idx)
            mu, sd = Xall.mean(axis=0), Xall.std(axis=0) + 1e-9
            wall = fit_logistic(np.column_stack([np.ones(len(idx)), (Xall - mu) / sd]), y)
            out[f"{tset_name}|{oname}|combined"] = {"auc": rc["auc"], "lo": rc["lo"], "hi": rc["hi"],
                                                    "strat": rc.get("strat"), "delta_vs_rel_width": rc["auc"] - rw["auc"],
                                                    "delta_lo": dlo, "delta_hi": dhi,
                                                    "weights_std": dict(zip(["intercept"] + names, np.round(wall, 3).tolist()))}
            lines += [f"| combined (grouped 5-fold CV, out-of-fold) | 1.00 | {rc['auc']:.3f} [{rc['lo']:.3f}, {rc['hi']:.3f}] | "
                      f"{rc.get('strat', float('nan')):.3f} | R2: ΔAUROC vs rel_width = {rc['auc'] - rw['auc']:+.3f} "
                      f"[{dlo:+.3f}, {dhi:+.3f}] → {'adds information' if dlo > 0 else 'no added information'} |", "",
                      "Standardised logistic weights fitted on all pairs (descriptive): "
                      + ", ".join(f"{k} {v:+.2f}" for k, v in zip(["intercept"] + names, np.round(wall, 2))), ""]
            # R3: rel_width > 2
            flag = d["rel_width"][idx] > 2
            yb = y.astype(bool)
            mf = np.bincount(topo[flag], weights=yb[flag], minlength=nt)
            nf = np.bincount(topo[flag], minlength=nt)
            mu_ = np.bincount(topo[~flag], weights=yb[~flag], minlength=nt)
            nu = np.bincount(topo[~flag], minlength=nt)
            ratio = (mf.sum() / nf.sum()) / (mu_.sum() / nu.sum())
            with np.errstate(invalid="ignore", divide="ignore"):
                rb = ((W @ mf) / (W @ nf)) / ((W @ mu_) / (W @ nu))
            rlo, rhi = np.nanquantile(rb, (0.025, 0.975))
            usable = ratio >= 2 and rlo > 1
            out[f"{tset_name}|{oname}|flag_relw2"] = {"share_flagged": float(flag.mean()),
                                                      "rate_flagged": mf.sum() / nf.sum(),
                                                      "rate_unflagged": mu_.sum() / nu.sum(), "ratio": ratio,
                                                      "ratio_lo": rlo, "ratio_hi": rhi, "usable": bool(usable)}
            lines += [f"R3, flag `rel_width > 2`: flagged {flag.mean():.3f} of pairs; {oname} rate flagged "
                      f"{mf.sum() / nf.sum():.3f} vs unflagged {mu_.sum() / nu.sum():.3f}; ratio {ratio:.2f} "
                      f"[{rlo:.2f}, {rhi:.2f}] → {'usable' if usable else 'not usable'}.", ""]
            if oname == "miss":
                q = np.quantile(d["rel_width"][idx], [0.2, 0.4, 0.6, 0.8])
                b = np.digitize(d["rel_width"][idx], q)
                lines += ["Conditional coverage of the module by quintile of rel_width:", "",
                          "| quintile | rel_width range | pairs | coverage | median width |", "|---|---|---|---|---|"]
                edges = [d["rel_width"][idx].min()] + list(q) + [d["rel_width"][idx].max()]
                cq = []
                for k in range(5):
                    s = b == k
                    cv = 1 - yb[s].mean()
                    cq.append({"lo": edges[k], "hi": edges[k + 1], "n": int(s.sum()), "coverage": cv,
                               "width": float(np.median(d["width"][idx][s]))})
                    lines.append(f"| {k + 1} | {edges[k]:.2f}–{edges[k + 1]:.2f} | {s.sum()} | {cv:.3f} | "
                                 f"{np.median(d['width'][idx][s]):.3f} |")
                out[f"{tset_name}|condcov"] = cq
                lines.append("")
    (FLAGS / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (FLAGS / "summary.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")


def main():
    d = load()
    print(check(d))
    rng = np.random.default_rng(20261102)
    rq41(d, rng)
    rq44(d, rng)
    print("done")


if __name__ == "__main__":
    main()
