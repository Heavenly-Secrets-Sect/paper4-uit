"""Analysis of ext_baselines2_eval (rule pre-registered in docs/ext/baselines2.md, written before the run).

Reads results/ext_baselines2_eval/{runs.jsonl, skeletons.jsonl}; also results/a2b_pselect/runs.jsonl
and results/a2_baselines/runs.jsonl for the round-1 baselines (same data seeds) and the v4 regression check.
Writes results/ext_baselines2_eval/{analysis.md, rule_check.txt, numbers.json}.

Statistics (fixed before the run):
- coverage: pooled over non-null pairs of ok runs (runner convention), with a 95% CI clustered by topology;
- paired IS difference v4 - X per (topology, replicate) run; estimate = mean over runs; 95% percentile CI
  from B = 4000 cluster-bootstrap resamples of the 20 topologies (rng seed 20261102);
- one-sided p for "v4 better" = (1 + #{bootstrap mean >= 0}) / (B + 1); Holm step-down at family level
  0.025 one-sided (= two-sided 0.05, the level of the CI) across the comparisons of one rule.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "ext_baselines2_eval"
B = 4000
SEED = 20261102
V4 = "tolerant_v4"
PSEL = ["pselect_union_v2", "pselect_union_v2_cal"]
BVAR = ["bvar_minnesota_v2", "bvar_minnesota_v2_cal"]
CELLS = [("none", 0.0), ("extra", 0.2), ("extra", 0.5), ("missing", 0.2), ("missing", 0.5),
         ("reversed", 0.2), ("reversed", 0.5)]
TS = [40, 80, 150]


def load(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


def holm(pvals: dict, level: float) -> dict:
    """Holm step-down: returns {key: rejected}."""
    order = sorted(pvals, key=lambda k: pvals[k])
    m = len(order)
    rej = {k: False for k in pvals}
    for r, k in enumerate(order):
        if pvals[k] <= level / (m - r):
            rej[k] = True
        else:
            break
    return rej


def cluster_boot(per_topo: dict, rng) -> tuple[float, float, float, np.ndarray]:
    topos = sorted(per_topo)
    vals = [np.asarray(per_topo[t], float) for t in topos]
    est = float(np.mean(np.concatenate(vals)))
    sums = np.array([v.sum() for v in vals])
    cnts = np.array([len(v) for v in vals])
    idx = rng.integers(0, len(topos), size=(B, len(topos)))
    boots = sums[idx].sum(axis=1) / cnts[idx].sum(axis=1)
    lo, hi = np.quantile(boots, (0.025, 0.975))
    return est, float(lo), float(hi), boots


def main() -> int:
    rows = load(OUT / "runs.jsonl")
    skels = load(OUT / "skeletons.jsonl")
    rng = np.random.default_rng(SEED)
    methods = [V4] + PSEL + BVAR
    num = {}
    lines = ["# ext_baselines2_eval: analysis (D-07 development, exploratory)", "",
             "Rule pre-registered in docs/ext/baselines2.md. Coverage pooled over non-null pairs of ok runs; "
             "CI 95% clustered by topology (B = 4000).", ""]

    # ---------------------------------------------------------------- run-level summary
    groups = defaultdict(list)
    for r in rows:
        groups[(r["T"], r["kind"], r["rate"], r["method"])].append(r)

    def cov_ci(g):
        ok = [r for r in g if r["status"] == "ok"]
        per = defaultdict(lambda: [0, 0])
        for r in ok:
            per[r["topology"]][0] += r["n_covered_nonnull"]
            per[r["topology"]][1] += r["n_nonnull"]
        topos = sorted(per)
        c = np.array([per[t][0] for t in topos], float)
        n = np.array([per[t][1] for t in topos], float)
        est = c.sum() / n.sum()
        idx = rng.integers(0, len(topos), size=(B, len(topos)))
        bs = c[idx].sum(1) / n[idx].sum(1)
        return float(est), float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975)), len(ok), len(g)

    lines += ["## 1. Summary per cell", "",
              "| T | cell | method | ok | cov [95% CI] | IS | width (median) | IS null pairs | lag err (median) |",
              "|---|---|---|---|---|---|---|---|---|"]
    summ = {}
    for T in TS:
        for kind, rate in CELLS:
            for m in methods:
                g = groups.get((T, kind, rate, m), [])
                if not g:
                    continue
                ok = [r for r in g if r["status"] == "ok"]
                c, clo, chi, n_ok, n_all = cov_ci(g)
                IS = float(np.mean([r["iscore_nonnull_mean"] for r in ok]))
                w = float(np.median([r["width_kept"] for r in ok if r.get("width_kept") is not None]))
                isn = float(np.mean([r["iscore_null_mean"] for r in ok if r.get("iscore_null_mean") is not None]))
                le = [r["mean_lag_abs_err"] for r in ok if r.get("mean_lag_abs_err") is not None]
                le = float(np.median(le)) if le else float("nan")
                key = f"{T}|{kind}|{rate}|{m}"
                summ[key] = {"ok": n_ok, "n": n_all, "cov": c, "cov_lo": clo, "cov_hi": chi, "IS": IS, "width": w,
                             "IS_null": isn, "lag_err": le}
                lines.append(f"| {T} | {kind}-{rate} | {m} | {n_ok}/{n_all} | {c:.3f} [{clo:.3f}, {chi:.3f}] | {IS:.2f} | "
                             f"{w:.3f} | {isn:.2f} | {le:.3f} |")
    num["summary"] = summ

    # ---------------------------------------------------------------- paired differences
    idx = {(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"], r["method"]): r
           for r in rows if r["status"] == "ok" and r.get("iscore_nonnull_mean") is not None}

    def paired(T, kind, rate, m, ref=V4, index=idx, index_m=None):
        index_m = index_m or index
        per = defaultdict(list)
        for (tp, rep, t, k, rt, meth), r in index_m.items():
            if meth == m and t == T and k == kind and rt == rate:
                b = index.get((tp, rep, t, k, rt, ref))
                if b is not None:
                    per[tp].append(b["iscore_nonnull_mean"] - r["iscore_nonnull_mean"])   # ref - m
        if not per:
            return None
        est, lo, hi, boots = cluster_boot(per, rng)
        p_better = (1 + int((boots >= 0).sum())) / (B + 1)    # ref better (diff < 0)
        p_worse = (1 + int((boots <= 0).sum())) / (B + 1)     # ref worse (diff > 0)
        return {"est": est, "lo": lo, "hi": hi, "p_v4_better": p_better, "p_v4_worse": p_worse,
                "n_pairs": int(sum(len(v) for v in per.values()))}

    pair = {}
    for T in TS:
        for kind, rate in CELLS:
            for m in PSEL + BVAR:
                d = paired(T, kind, rate, m)
                if d:
                    pair[f"{T}|{kind}|{rate}|{m}"] = d
    num["paired_v4_minus_X"] = pair

    # ---------------------------------------------------------------- rules
    def rule(Xs, label):
        out, pv = [], {}
        cells = [(T, "missing", r) for T in (80, 150) for r in (0.2, 0.5)]
        for X in Xs:
            for T, kind, rate in cells:
                pv[(X, T, rate)] = pair[f"{T}|{kind}|{rate}|{X}"]["p_v4_better"]
        rej = holm(pv, 0.025)
        res = {}
        out += [f"### {label}", "",
                "| X | T | cell | v4 cov | IS v4 | IS X | cov X | v4 - X [95% CI] | p (one-sided) | CI rule | Holm |",
                "|---|---|---|---|---|---|---|---|---|---|---|"]
        n_ci, n_holm = defaultdict(int), defaultdict(int)
        for X in Xs:
            for T, kind, rate in cells:
                d = pair[f"{T}|{kind}|{rate}|{X}"]
                s4, sx = summ[f"{T}|{kind}|{rate}|{V4}"], summ[f"{T}|{kind}|{rate}|{X}"]
                ok_ci = s4["cov"] >= 0.90 and d["hi"] < 0
                ok_holm = s4["cov"] >= 0.90 and rej[(X, T, rate)]
                n_ci[X] += ok_ci
                n_holm[X] += ok_holm
                res[f"{X}|{T}|{rate}"] = {"ci_pass": bool(ok_ci), "holm_pass": bool(ok_holm), **d}
                out.append(f"| {X} | {T} | missing-{rate} | {s4['cov']:.3f} | {s4['IS']:.2f} | {sx['IS']:.2f} | {sx['cov']:.3f} | "
                           f"{d['est']:+.2f} [{d['lo']:+.2f}, {d['hi']:+.2f}] | {d['p_v4_better']:.4f} | "
                           f"{'pass' if ok_ci else 'FAIL'} | {'pass' if ok_holm else 'FAIL'} |")
        verdict = all(n_ci[X] == 4 for X in Xs)
        verdict_holm = all(n_holm[X] == 4 for X in Xs)
        out += ["", "Counts (cells out of 4): " + "; ".join(f"{X}: {n_ci[X]}/4 (Holm over {len(pv)}: {n_holm[X]}/4)" for X in Xs),
                "", f"**Verdict {label}: {'HOLDS' if verdict else 'FAILS'}** (CI rule); under Holm: "
                f"{'HOLDS' if verdict_holm else 'FAILS'}.", ""]
        return out, {"verdict": "HOLDS" if verdict else "FAILS", "verdict_holm": "HOLDS" if verdict_holm else "FAILS",
                     "counts": dict(n_ci), "counts_holm": dict(n_holm), "cells": res}

    lines += ["## 2. Pre-registered rules", ""]
    o1, r1 = rule(PSEL, "R-B2 (primary, X in pselect_union_v2 / _cal)")
    o2, r2 = rule(BVAR, "R-B2s (secondary, X in bvar_minnesota_v2 / _cal)")
    lines += o1 + o2
    num["rule_primary"], num["rule_secondary"] = r1, r2

    # ---------------------------------------------------------------- descriptive: all cells
    pv_all = {k: min(1.0, 2 * min(d["p_v4_better"], d["p_v4_worse"])) for k, d in pair.items()}
    rej_all = holm(pv_all, 0.05)
    lines += ["## 3. Descriptive: every cell (v4 - X, 95% CI). W = v4 better (upper < 0) and v4 cov >= 0.90; "
              "L = v4 worse (lower > 0); T = tie. Holm (two-sided 0.05) over all "
              f"{len(pv_all)} comparisons in brackets.", "",
              "| T | cell | " + " | ".join(PSEL + BVAR) + " |", "|---|---|" + "---|" * len(PSEL + BVAR)]
    tally = defaultdict(lambda: defaultdict(int))
    for T in TS:
        for kind, rate in CELLS:
            cells_out = []
            for m in PSEL + BVAR:
                k = f"{T}|{kind}|{rate}|{m}"
                d = pair[k]
                v4c = summ[f"{T}|{kind}|{rate}|{V4}"]["cov"]
                lab = "W" if (d["hi"] < 0 and v4c >= 0.90) else ("L" if d["lo"] > 0 else "T")
                labh = "W" if (rej_all[k] and d["est"] < 0 and v4c >= 0.90) else ("L" if rej_all[k] and d["est"] > 0 else "T")
                tally[m][lab] += 1
                tally[m]["holm_" + labh] += 1
                cells_out.append(f"{d['est']:+.2f} [{d['lo']:+.2f}, {d['hi']:+.2f}] {lab} ({labh})")
            lines.append(f"| {T} | {kind}-{rate} | " + " | ".join(cells_out) + " |")
    lines += ["", "Tally over 21 cells: " + "; ".join(
        f"{m}: W {tally[m]['W']} / T {tally[m]['T']} / L {tally[m]['L']} (Holm: W {tally[m]['holm_W']} / T {tally[m]['holm_T']} / L {tally[m]['holm_L']})"
        for m in PSEL + BVAR), ""]
    num["tally_all_cells"] = {m: dict(v) for m, v in tally.items()}

    # ---------------------------------------------------------------- v2 vs round-1 baselines (same data seeds)
    old = []
    for name, path, meth in (("pselect_union", "a2b_pselect", "pselect_union"), ("bvar_minnesota", "a2_baselines", "bvar_minnesota")):
        p = ROOT / "results" / path / "runs.jsonl"
        if p.exists():
            old += [r for r in load(p) if r["method"] == meth]
    oidx = {(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"], r["method"]): r
            for r in old if r["status"] == "ok" and r.get("iscore_nonnull_mean") is not None}
    comb = dict(idx)
    comb.update(oidx)
    lines += ["## 4. Descriptive: v2 against the round-1 version on the same data (IS(v1) - IS(v2); positive = v2 better), "
              "and v4 against round-1 pselect_union", "",
              "| T | cell | pselect v1 cov / IS | pselect v2 cov / IS | v1 - v2 | bvar v1 cov / IS | bvar v2 cov / IS | v1 - v2 | v4 - pselect v1 |",
              "|---|---|---|---|---|---|---|---|---|"]
    v1v2 = {}

    def cov_is(index, T, kind, rate, m):
        g = [r for (tp, rep, t, k, rt, meth), r in index.items() if (t, k, rt, meth) == (T, kind, rate, m)]
        if not g:
            return None
        return (sum(r["n_covered_nonnull"] for r in g) / sum(r["n_nonnull"] for r in g),
                float(np.mean([r["iscore_nonnull_mean"] for r in g])))

    for T in TS:
        for kind, rate in CELLS:
            cellv = []
            for m1, m2 in (("pselect_union", "pselect_union_v2"), ("bvar_minnesota", "bvar_minnesota_v2")):
                a, b = cov_is(oidx, T, kind, rate, m1), cov_is(idx, T, kind, rate, m2)
                d = paired(T, kind, rate, m2, ref=m1, index=comb, index_m=comb)
                v1v2[f"{T}|{kind}|{rate}|{m2}"] = {"v1": a, "v2": b, "v1_minus_v2": d}
                cellv += [f"{a[0]:.3f} / {a[1]:.2f}" if a else "–", f"{b[0]:.3f} / {b[1]:.2f}" if b else "–",
                          f"{d['est']:+.2f} [{d['lo']:+.2f}, {d['hi']:+.2f}]" if d else "–"]
            d4 = paired(T, kind, rate, "pselect_union", ref=V4, index=comb, index_m=comb)
            v1v2[f"{T}|{kind}|{rate}|v4_minus_pselect_v1"] = d4
            lines.append(f"| {T} | {kind}-{rate} | " + " | ".join(cellv) + " | "
                         + (f"{d4['est']:+.2f} [{d4['lo']:+.2f}, {d4['hi']:+.2f}]" if d4 else "–") + " |")
    num["v2_vs_v1"] = v1v2

    # ---------------------------------------------------------------- regression check of v4 against a2b_pselect
    ref = ROOT / "results" / "a2b_pselect" / "runs.jsonl"
    if ref.exists():
        a2b = {(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"]): r for r in load(ref) if r["method"] == V4}
        mine = [r for r in rows if r["method"] == V4]
        mism = sum(1 for r in mine if (a := a2b.get((r["topology"], r["replicate"], r["T"], r["kind"], r["rate"]))) is None
                   or a["status"] != r["status"] or (r["status"] == "ok" and (a["iscore_nonnull_mean"] != r["iscore_nonnull_mean"]
                                                                              or a["n_covered_nonnull"] != r["n_covered_nonnull"])))
        lines += ["", f"## 5. Regression check: {len(mine)} tolerant_v4 rows compared with results/a2b_pselect; mismatches: {mism}", ""]
        num["v4_regression"] = {"n": len(mine), "mismatches": mism}

    # ---------------------------------------------------------------- deleted pairs: lag 0 vs lag 1-2
    dlog = {}
    for s in skels:
        if "kind" in s and s.get("kind") == "missing" and "log" in s:
            dlog[(s["topology"], s["replicate"], s["rate"])] = {frozenset(e["pair"]) for e in s["log"] if "pair" in e}
    lines += ["## 6. Deleted edges (missing cells): coverage of the deleted pair's C(H), true direct lag 0 vs 1-2 "
              "(difference CI clustered by topology); untouched direct-edge pairs for reference", "",
              "| T | cell | method | cov lag 0 (n) | cov lag 1-2 (n) | lag0 - lag12 [95% CI] | IS lag 0 | IS lag 1-2 | cov untouched direct (n) |",
              "|---|---|---|---|---|---|---|---|---|"]
    lagtab = {}
    for T in (40, 80, 150):
        for rate in (0.2, 0.5):
            for m in methods:
                per0, per12, isl = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0]), {0: [], 12: []}
                unt = [0, 0]
                for r in rows:
                    if (r["T"], r["kind"], r["rate"], r["method"]) != (T, "missing", rate, m) or r["status"] != "ok":
                        continue
                    dam = dlog.get((r["topology"], r["replicate"], rate), set())
                    for j, i, cov, sc, lag in r.get("pairs", []):
                        if frozenset((i, j)) in dam:
                            tgt = per0 if lag == 0 else per12
                            tgt[r["topology"]][0] += cov
                            tgt[r["topology"]][1] += 1
                            isl[0 if lag == 0 else 12].append(sc)
                        else:
                            unt[0] += cov
                            unt[1] += 1
                topos = sorted(set(per0) | set(per12))
                if not topos:
                    continue
                c0 = sum(v[0] for v in per0.values()); n0 = sum(v[1] for v in per0.values())
                c1 = sum(v[0] for v in per12.values()); n1 = sum(v[1] for v in per12.values())
                a = np.array([[per0[t][0], per0[t][1], per12[t][0], per12[t][1]] for t in topos], float)
                ix = rng.integers(0, len(topos), size=(B, len(topos)))
                s = a[ix].sum(axis=1)
                with np.errstate(invalid="ignore", divide="ignore"):
                    diff = s[:, 0] / s[:, 1] - s[:, 2] / s[:, 3]
                diff = diff[np.isfinite(diff)]
                est = c0 / n0 - c1 / n1
                lo, hi = np.quantile(diff, (0.025, 0.975))
                lagtab[f"{T}|{rate}|{m}"] = {"cov0": c0 / n0, "n0": n0, "cov12": c1 / n1, "n12": n1, "diff": est,
                                             "lo": float(lo), "hi": float(hi), "IS0": float(np.mean(isl[0])),
                                             "IS12": float(np.mean(isl[12])), "cov_untouched": unt[0] / max(unt[1], 1),
                                             "n_untouched": unt[1]}
                lines.append(f"| {T} | missing-{rate} | {m} | {c0 / n0:.3f} ({n0}) | {c1 / n1:.3f} ({n1}) | {est:+.3f} "
                             f"[{lo:+.3f}, {hi:+.3f}] | {np.mean(isl[0]):.2f} | {np.mean(isl[12]):.2f} | "
                             f"{unt[0] / max(unt[1], 1):.3f} ({unt[1]}) |")
    num["deleted_pairs_by_lag"] = lagtab

    # ---------------------------------------------------------------- info of the baselines
    lines += ["", "## 7. Baseline internals (mean over ok runs)", "",
              "| T | cell | pselect_v2 n_selected | n_unoriented | n_graphs | n_members_ok | n_draws | bvar_v2 lambda | theta |",
              "|---|---|---|---|---|---|---|---|---|"]
    info = {}
    for T in TS:
        for kind, rate in CELLS:
            gp = [r for r in groups.get((T, kind, rate, "pselect_union_v2"), []) if r["status"] == "ok"]
            gb = [r for r in groups.get((T, kind, rate, "bvar_minnesota_v2"), []) if r["status"] == "ok"]
            f = lambda g, k: float(np.mean([r.get(f"info_{k}", np.nan) for r in g])) if g else float("nan")  # noqa: E731
            vals = [f(gp, "n_selected"), f(gp, "n_unoriented"), f(gp, "n_graphs"), f(gp, "n_members_ok"), f(gp, "n_draws"),
                    f(gb, "lambda"), f(gb, "theta")]
            info[f"{T}|{kind}|{rate}"] = vals
            lines.append(f"| {T} | {kind}-{rate} | " + " | ".join(f"{v:.2f}" for v in vals) + " |")
    num["internals"] = info
    cal = json.loads((OUT / "calibration.json").read_text())
    num["calibration"] = {k: v for k, v in cal.items() if "_v2_cal" in k or k.startswith("mod|")}
    lines += ["", "## 8. Width factors used (calibration.json)", "", "| T | kind | v4 (frozen) | pselect_v2_cal | bvar_v2_cal |",
              "|---|---|---|---|---|"]
    for T in TS:
        for kind in ("none", "extra", "missing", "reversed"):
            lines.append(f"| {T} | {kind} | {cal.get(f'mod|{T}|{kind}')} | {cal.get(f'pselect_union_v2_cal|{T}|{kind}')} | "
                         f"{cal.get(f'bvar_minnesota_v2_cal|{T}|{kind}')} |")

    (OUT / "analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "rule_check.txt").write_text("\n".join(o1 + o2) + "\n", encoding="utf-8")
    (OUT / "numbers.json").write_text(json.dumps(num, indent=1, default=float), encoding="utf-8")
    print("\n".join(o1 + o2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
