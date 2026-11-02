"""Analyzer for r4prepivot (rule in docs/ext/r4prepivot.md, written before any D-07 run).

Usage: /Users/kietnt/miniconda3/bin/python experiments/ext/r4prepivot/analyze.py <part> [<part> ...]
  part in {primary, secondary, scen, lag1}. Writes results/ext_r4prepivot_<part>/analysis.{md,json};
  for "primary" also ruling.md / ruling.json.

Per cell: pooled coverage over non-null pairs (ITT: a failed run counts its non-null pairs, taken from
the paired tolerant_v5_1 row, as uncovered), mean IS, median width, ratio of means
IS_pp / IS_v51 over runs where both are ok, cluster bootstrap by topology (B = 20000, seed 20261104),
one-sided 95% upper bound (95th percentile of the bootstrap ratio), one-sided p for H0: ratio >= 1.10,
p = (1 + #{ratio* >= 1.10}) / (B + 1); Holm at 0.05 over the cells of the family.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "results"
B = 20000
SEED = 20261104
MARGIN = 1.10
ALPHA = 0.05
METHODS = ("tolerant_v5_1", "tolerant_v5_1_pp", "tolerant_v5_1_pp_orig")


def load_rows(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def ckey(r):
    return (r.get("scenario", "clean"), r["T"], r["kind"], float(r["rate"]))


def rkey(r):
    return (r.get("scenario", "clean"), r["topology"], r["replicate"], r["T"], r["kind"], float(r["rate"]))


def pairing(rows, stored_name, reps):
    """Our tolerant_v5_1 rows vs the stored run's: same status, |dIS| < 1e-12, same covered / non-null counts."""
    stored = {rkey(r): r for r in load_rows(RES / stored_name / "runs.jsonl") if r["method"] == "tolerant_v5_1"}
    ours = [r for r in rows if r["method"] == "tolerant_v5_1"]
    same, missing, diff = 0, 0, []
    for r in ours:
        s = stored.get(rkey(r))
        if s is None:
            missing += 1
            continue
        if r["status"] != s["status"]:
            diff.append(rkey(r))
            continue
        if r["status"] != "ok" or (abs(r["iscore_nonnull_mean"] - s["iscore_nonnull_mean"]) < 1e-12
                                   and r["n_covered_nonnull"] == s["n_covered_nonnull"] and r["n_nonnull"] == s["n_nonnull"]):
            same += 1
        else:
            diff.append(rkey(r))
    return {"stored_run": stored_name, "ours": len(ours), "identical": same, "not_in_stored": missing,
            "different": len(diff), "first_diffs": [list(d) for d in diff[:5]], "ok": same == len(ours) and len(ours) > 0}


def cell_table(rows):
    by = defaultdict(lambda: defaultdict(dict))
    for r in rows:
        by[ckey(r)][(r["topology"], r["replicate"])][r["method"]] = r
    return by


def cov_itt(runs, m):
    cov = tot = 0
    for d in runs.values():
        ref = d["tolerant_v5_1"]
        r = d.get(m)
        nn = (r or ref).get("n_nonnull") or ref.get("n_nonnull") or 0
        tot += nn
        if r and r["status"] == "ok":
            cov += r["n_covered_nonnull"]
    return cov / tot if tot else float("nan")


def ratio_test(runs, m, ref="tolerant_v5_1", seed=SEED):
    pairs = [(t, d[m]["iscore_nonnull_mean"], d[ref]["iscore_nonnull_mean"]) for (t, _), d in runs.items()
             if d.get(m, {}).get("status") == "ok" and d.get(ref, {}).get("status") == "ok"]
    topo = sorted({p[0] for p in pairs})
    num = np.array([sum(p[1] for p in pairs if p[0] == t) for t in topo])
    den = np.array([sum(p[2] for p in pairs if p[0] == t) for t in topo])
    est = num.sum() / den.sum()
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(topo), size=(B, len(topo)))
    boot = num[idx].sum(axis=1) / den[idx].sum(axis=1)
    return {"ratio": float(est), "upper95_1s": float(np.quantile(boot, 0.95)),
            "ci95_2s": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
            "p_H0_ge_margin": float((1 + (boot >= MARGIN).sum()) / (B + 1)),
            "p_worse_than_1": float((1 + (boot <= 1.0).sum()) / (B + 1)),
            "n_pairs": len(pairs), "n_clusters": len(topo)}


def holm(ps, alpha=ALPHA):
    order = np.argsort(ps)
    rej = [False] * len(ps)
    for rank, i in enumerate(order):
        if ps[i] <= alpha / (len(ps) - rank):
            rej[i] = True
        else:
            break
    return rej


def describe(vals):
    v = np.array([x for x in vals if x is not None and np.isfinite(x)])
    if not v.size:
        return None
    return {"n": int(v.size), "median": float(np.median(v)), "q25": float(np.quantile(v, 0.25)),
            "q75": float(np.quantile(v, 0.75)), "min": float(v.min()), "max": float(v.max()), "mean": float(v.mean())}


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    # average ranks for ties
    def avg_rank(a):
        order = np.argsort(a, kind="mergesort")
        ranks = np.empty(len(a))
        sa = a[order]
        i = 0
        while i < len(a):
            j = i
            while j + 1 < len(a) and sa[j + 1] == sa[i]:
                j += 1
            ranks[order[i:j + 1]] = (i + j) / 2
            i = j + 1
        return ranks
    rx, ry = avg_rank(x), avg_rank(y)
    return float(np.corrcoef(rx, ry)[0, 1]) if np.std(rx) > 0 and np.std(ry) > 0 else float("nan")


def analyze(part):
    name = f"ext_r4prepivot_{part}"
    spec = json.loads((ROOT / "experiments/configs" / f"{name}.json").read_text(encoding="utf-8"))
    rows = load_rows(RES / name / "rows.jsonl")
    man = json.loads((RES / name / "manifest.json").read_text(encoding="utf-8"))
    pair = pairing(rows, spec["pair_with"], spec["replicates"])
    by = cell_table(rows)
    cells = [(sc["name"], T, k, float(r)) for sc in spec["scenarios"] for T, k, r in spec["cells"]]
    out = {"part": part, "pairing": pair, "seconds": man["seconds"], "n_datasets": man["n_datasets"],
           "start_utc": man["start_utc"], "end_utc": man["end_utc"], "cells": []}
    for c in cells:
        runs = by[c]
        rec = {"cell": list(c), "n_runs": len(runs)}
        for m in METHODS:
            ok = [d[m] for d in runs.values() if d.get(m, {}).get("status") == "ok"]
            rec[m] = {"ok": len(ok), "cov_itt": cov_itt(runs, m),
                      "IS": float(np.mean([r["iscore_nonnull_mean"] for r in ok])) if ok else None,
                      "width_median": float(np.median([r["width_kept"] for r in ok if r.get("width_kept") is not None]))
                      if ok else None,
                      "IS_null": float(np.mean([r["iscore_null_mean"] for r in ok if r.get("iscore_null_mean") is not None]))
                      if ok else None}
        for m in METHODS[1:]:
            rec[m]["ratio_test"] = ratio_test(runs, m)
        pp = [d["tolerant_v5_1_pp"] for d in runs.values() if d.get("tolerant_v5_1_pp", {}).get("status") == "ok"]
        rec["f_pp"] = describe([r.get("info_f_pp") for r in pp])
        rec["f_orig"] = describe([r.get("info_f_orig") for r in pp])
        rec["f_v51_eff"] = next((d["tolerant_v5_1"].get("f_v51_eff") for d in runs.values()), None)
        rec["n_inner_ok"] = describe([r.get("info_n_inner_ok") for r in pp])
        rec["n_roots_nn"] = describe([r.get("info_n_roots_nn") for r in pp])
        allr = [d["tolerant_v5_1"] for d in runs.values()]
        rec["sec_total"] = describe([r.get("seconds_total") for r in allr])
        rec["sec_outer"] = describe([r.get("seconds_outer") for r in allr])
        rec["status_pp"] = dict(sorted({s: sum(1 for d in runs.values() if d.get("tolerant_v5_1_pp", {}).get("status") == s)
                                        for s in {d.get("tolerant_v5_1_pp", {}).get("status") for d in runs.values()}}.items()))
        out["cells"].append(rec)
    for m in METHODS[1:]:
        ps = [c[m]["ratio_test"]["p_H0_ge_margin"] for c in out["cells"]]
        for c, rej in zip(out["cells"], holm(ps)):
            c[m]["noninf_holm"] = bool(rej)
            c[m]["noninf_raw"] = c[m]["ratio_test"]["upper95_1s"] < MARGIN
        ps_w = [c[m]["ratio_test"]["p_worse_than_1"] for c in out["cells"]]
    # correlations of f with damage size (k) and with T, run level
    pp_rows = [r for r in rows if r["method"] == "tolerant_v5_1_pp" and r["status"] == "ok"]
    corr = {}
    for kind in sorted({r["kind"] for r in pp_rows}):
        sub = [r for r in pp_rows if r["kind"] in (kind, "none")]
        if len({r["k"] for r in sub}) > 1:
            corr[f"spearman_f_vs_k|{kind}+none"] = {"rho": spearman([r["k"] for r in sub], [r["info_f_pp"] for r in sub]),
                                                     "n": len(sub)}
            for T in sorted({r["T"] for r in sub}):
                s2 = [r for r in sub if r["T"] == T]
                if len({r["k"] for r in s2}) > 1:
                    corr[f"spearman_f_vs_k|{kind}+none|T{T}"] = {
                        "rho": spearman([r["k"] for r in s2], [r["info_f_pp"] for r in s2]), "n": len(s2)}
    if len({r["T"] for r in pp_rows}) > 1:
        corr["spearman_f_vs_T"] = {"rho": spearman([r["T"] for r in pp_rows], [r["info_f_pp"] for r in pp_rows]),
                                   "n": len(pp_rows)}
    # per-run association between f_pp / f_v51_eff and the IS ratio
    out["correlations"] = corr
    return out


def fmt(x, d=3):
    return "–" if x is None else f"{x:.{d}f}"


def write_md(o):
    L = [f"# r4prepivot, part `{o['part']}`", "",
         f"Run {o['start_utc']} – {o['end_utc']}, {o['seconds']} s, {o['n_datasets']} datasets.",
         f"Pairing of tolerant_v5_1 rows with `{o['pairing']['stored_run']}`: {o['pairing']['identical']}/{o['pairing']['ours']} identical "
         f"(different {o['pairing']['different']}, not in stored {o['pairing']['not_in_stored']}) -> {'PASS' if o['pairing']['ok'] else 'FAIL'}.", "",
         "| scenario | T | kind | rate | runs | cov v51 | cov pp | cov orig | IS v51 | IS pp | IS orig | ratio pp [2s 95% CI] | upper 1s | p(H0 >= 1.10) | NI raw / Holm | ratio orig | NI orig Holm | f_pp median [IQR] | f_orig median | f_v51 eff | width v51 / pp | pp ok |",
         "|" + "---|" * 22]
    for c in o["cells"]:
        sc, T, k, r = c["cell"]
        v, p, q = c["tolerant_v5_1"], c["tolerant_v5_1_pp"], c["tolerant_v5_1_pp_orig"]
        rt, rq = p["ratio_test"], q["ratio_test"]
        f = c["f_pp"] or {}
        L.append(f"| {sc} | {T} | {k} | {r:.1f} | {c['n_runs']} | {fmt(v['cov_itt'])} | {fmt(p['cov_itt'])} | {fmt(q['cov_itt'])} | "
                 f"{fmt(v['IS'], 2)} | {fmt(p['IS'], 2)} | {fmt(q['IS'], 2)} | {rt['ratio']:.3f} [{rt['ci95_2s'][0]:.3f}, {rt['ci95_2s'][1]:.3f}] | "
                 f"{rt['upper95_1s']:.3f} | {rt['p_H0_ge_margin']:.4g} | {'Y' if p['noninf_raw'] else 'N'} / {'Y' if p['noninf_holm'] else 'N'} | "
                 f"{rq['ratio']:.3f} | {'Y' if q['noninf_holm'] else 'N'} | {fmt(f.get('median'))} [{fmt(f.get('q25'))}, {fmt(f.get('q75'))}] | "
                 f"{fmt((c['f_orig'] or {}).get('median'))} | {fmt(c['f_v51_eff'])} | {fmt(v['width_median'], 2)} / {fmt(p['width_median'], 2)} | {p['ok']}/{c['n_runs']} |")
    L += ["", "Runtime per dataset (seconds, median [min, max]) and outer share:", ""]
    for c in o["cells"]:
        s, so = c["sec_total"] or {}, c["sec_outer"] or {}
        L.append(f"- {c['cell']}: total {fmt(s.get('median'), 2)} [{fmt(s.get('min'), 2)}, {fmt(s.get('max'), 2)}], "
                 f"v5.1 alone {fmt(so.get('median'), 2)}, ratio {fmt((s.get('median') or 0) / (so.get('median') or 1), 1)}x; "
                 f"inner worlds ok median {fmt((c['n_inner_ok'] or {}).get('median'), 0)}; pp status {c['status_pp']}")
    L += ["", "Spearman correlations (run level):", ""]
    for k, v in o["correlations"].items():
        L.append(f"- {k}: rho {v['rho']:.3f} (n {v['n']})")
    return "\n".join(L) + "\n"


def ruling(o):
    cells = o["cells"]
    ni = sum(c["tolerant_v5_1_pp"]["noninf_holm"] for c in cells)
    ni_raw = sum(c["tolerant_v5_1_pp"]["noninf_raw"] for c in cells)
    cov_ok = sum(c["tolerant_v5_1_pp"]["cov_itt"] >= 0.90 for c in cells)
    fail_ok = all(c["n_runs"] - c["tolerant_v5_1_pp"]["ok"] <= 3 for c in cells)
    retained = o["pairing"]["ok"] and ni >= 7 and cov_ok == len(cells) and fail_ok
    ni_o = sum(c["tolerant_v5_1_pp_orig"]["noninf_holm"] for c in cells)
    cov_o = sum(c["tolerant_v5_1_pp_orig"]["cov_itt"] >= 0.90 for c in cells)
    line = (f"pairing {'PASS' if o['pairing']['ok'] else 'FAIL'}; non-inferior (Holm 0.05 over {len(cells)}) "
            f"{ni}/{len(cells)} (raw one-sided 95% bound < 1.10: {ni_raw}/{len(cells)}); coverage >= 0.90 in "
            f"{cov_ok}/{len(cells)}; failure cap (<= 3 failed of {cells[0]['n_runs']}) {'PASS' if fail_ok else 'FAIL'} -> "
            f"tolerant_v5_1_pp {'RETAINED as a bank-free alternative (exploratory)' if retained else 'NOT RETAINED (sensitivity analysis only)'}. "
            f"Secondary (design as proposed, descriptive): non-inferior Holm {ni_o}/{len(cells)}, coverage >= 0.90 in {cov_o}/{len(cells)}.")
    return {"retained": retained, "noninf_holm": ni, "noninf_raw": ni_raw, "cov_ok": cov_ok, "fail_cap_ok": fail_ok,
            "orig_noninf_holm": ni_o, "orig_cov_ok": cov_o, "verdict": line}


def main(parts):
    for part in parts:
        o = analyze(part)
        d = RES / f"ext_r4prepivot_{part}"
        md = write_md(o)
        if part == "primary":
            rl = ruling(o)
            o["ruling"] = rl
            (d / "ruling.json").write_text(json.dumps(rl, indent=1), encoding="utf-8")
            (d / "ruling.md").write_text(f"# Ruling, r4prepivot primary\n\n{rl['verdict']}\n", encoding="utf-8")
            md += f"\n## Ruling\n\n{rl['verdict']}\n"
        (d / "analysis.json").write_text(json.dumps(o, indent=1), encoding="utf-8")
        (d / "analysis.md").write_text(md, encoding="utf-8")
        print(md)


if __name__ == "__main__":
    main(sys.argv[1:] or ["primary"])
