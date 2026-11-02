"""POST HOC, descriptive (written after the pre-registered analysis of ext_baselines2_eval; not part of any rule).

Question: in the missing cells, which baseline is the strongest on the same data (lowest mean interval score),
counting every baseline version stored for D-07 development seed_base 20261102, and does tolerant_v4 beat it?
Also tolerant_v5 (results/ext_narrow_eval) against pselect_union_v2(_cal), as R2-1 suggests "v4 (and v5 if
available)".

Pairing check: every source file also holds tolerant_v4 rows; a source is used only if its v4 rows equal the v4 rows
of ext_baselines2_eval (iscore_nonnull_mean and n_covered_nonnull, per (topology, replicate, T, kind, rate)).

Statistics as in analyze.py: paired v4 - X per run, mean, 95% percentile CI from 4000 cluster-bootstrap resamples of
the 20 topologies (rng seed 20261103, a separate stream). Holm (two-sided 0.05) over all comparisons of the table.
Writes results/ext_baselines2_eval/{envelope.md, envelope.json}.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "ext_baselines2_eval"
B = 4000
SOURCES = {
    "ext_baselines2_eval": ["pselect_union_v2", "pselect_union_v2_cal", "bvar_minnesota_v2", "bvar_minnesota_v2_cal"],
    "a2b_pselect": ["pselect_union"],
    "a2_baselines": ["ida_union", "bvar_minnesota", "lp_allpast", "plugin"],
    "ext_redteam_calbase": ["pselect_cal", "bvar_cal", "ida_cal", "fullvar_cal"],
    "ext_tlp_eval": ["targeted_lp", "targeted_lp_cal"],
    "ext_narrow_eval": ["tolerant_v5"],
}


def load(p):
    with open(p, encoding="utf-8") as fh:
        return [json.loads(x) for x in fh]


def key(r):
    return (r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])


def main() -> int:
    rng = np.random.default_rng(20261103)
    ref_v4 = {key(r): r for r in load(OUT / "runs.jsonl") if r["method"] == "tolerant_v4"}
    idx, pairing = {}, {}
    for src, meths in SOURCES.items():
        rows = load(ROOT / "results" / src / "runs.jsonl")
        v4 = {key(r): r for r in rows if r["method"] == "tolerant_v4"}
        mism = sum(1 for k, r in ref_v4.items() if k not in v4 or v4[k]["status"] != r["status"] or
                   (r["status"] == "ok" and (v4[k]["iscore_nonnull_mean"] != r["iscore_nonnull_mean"]
                                             or v4[k]["n_covered_nonnull"] != r["n_covered_nonnull"])))
        pairing[src] = mism
        if mism:
            continue
        for r in rows:
            if r["method"] in meths and r["status"] == "ok" and r.get("iscore_nonnull_mean") is not None:
                idx[key(r) + (r["method"],)] = r
    meths = [m for src, ms in SOURCES.items() if pairing[src] == 0 for m in ms]

    def stats(T, kind, rate, m, ref="tolerant_v4", refidx=None):
        refidx = refidx or {k: r for k, r in ref_v4.items() if r["status"] == "ok"}
        g = [r for k, r in idx.items() if k[2:] == (T, kind, rate, m)]
        if not g:   # e.g. lp_allpast is underdetermined at T = 40: no ok run, left out of that cell
            return None
        cov = sum(r["n_covered_nonnull"] for r in g) / sum(r["n_nonnull"] for r in g)
        IS = float(np.mean([r["iscore_nonnull_mean"] for r in g]))
        per = defaultdict(list)
        for k, r in idx.items():
            if k[2:] == (T, kind, rate, m):
                b = refidx.get(k[:5]) if ref == "tolerant_v4" else idx.get(k[:5] + (ref,))
                if b is not None:
                    per[k[0]].append(b["iscore_nonnull_mean"] - r["iscore_nonnull_mean"])
        topos = sorted(per)
        sums = np.array([sum(per[t]) for t in topos]); cnts = np.array([len(per[t]) for t in topos])
        est = float(sums.sum() / cnts.sum())
        ix = rng.integers(0, len(topos), size=(B, len(topos)))
        boots = sums[ix].sum(1) / cnts[ix].sum(1)
        lo, hi = np.quantile(boots, (0.025, 0.975))
        p2 = min(1.0, 2 * min((1 + (boots >= 0).sum()) / (B + 1), (1 + (boots <= 0).sum()) / (B + 1)))
        return {"cov": cov, "IS": IS, "est": est, "lo": float(lo), "hi": float(hi), "p2": float(p2), "n": int(cnts.sum())}

    out = {"pairing_mismatches": pairing, "cells": {}}
    lines = ["# POST HOC (descriptive, not a rule): strongest baseline per missing cell, all stored versions",
             "", "Pairing check (tolerant_v4 rows equal to ext_baselines2_eval; sources with mismatches are dropped): "
             + ", ".join(f"{s}: {m} mismatches" for s, m in pairing.items()), ""]
    allp = {}
    for T in (40, 80, 150):
        for rate in (0.2, 0.5):
            v4 = [r for k, r in ref_v4.items() if k[2:] == (T, "missing", rate) and r["status"] == "ok"]
            v4cov = sum(r["n_covered_nonnull"] for r in v4) / sum(r["n_nonnull"] for r in v4)
            v4IS = float(np.mean([r["iscore_nonnull_mean"] for r in v4]))
            cell = {m: d for m in meths if (d := stats(T, "missing", rate, m)) is not None}
            out["cells"][f"{T}|missing|{rate}"] = {"tolerant_v4": {"cov": v4cov, "IS": v4IS}, **cell}
            for m, d in cell.items():
                allp[(T, rate, m)] = d["p2"]
            lines += [f"## T = {T}, missing-{rate}: tolerant_v4 cov {v4cov:.3f}, IS {v4IS:.2f}", "",
                      "| method | cov | IS | v4 - X [95% CI] | p two-sided |", "|---|---|---|---|---|"]
            for m in sorted(cell, key=lambda m: cell[m]["IS"]):
                d = cell[m]
                lines.append(f"| {m} | {d['cov']:.3f} | {d['IS']:.2f} | {d['est']:+.2f} [{d['lo']:+.2f}, {d['hi']:+.2f}] | {d['p2']:.4f} |")
            base = [m for m in cell if m != "tolerant_v5"]
            best = min(base, key=lambda m: cell[m]["IS"])
            best90 = min([m for m in base if cell[m]["cov"] >= 0.90] or base, key=lambda m: cell[m]["IS"])
            out["cells"][f"{T}|missing|{rate}"]["strongest"] = best
            out["cells"][f"{T}|missing|{rate}"]["strongest_cov90"] = best90
            lines += ["", f"Strongest baseline by IS: **{best}**; strongest with coverage >= 0.90: **{best90}**.", ""]
    # Holm over all comparisons in the table
    order = sorted(allp, key=allp.get)
    rej = {}
    for r_, k in enumerate(order):
        if allp[k] <= 0.05 / (len(order) - r_):
            rej[k] = True
        else:
            break
    out["holm_rejected"] = [f"{T}|{rate}|{m}" for (T, rate, m) in rej]
    lines += [f"Holm (two-sided 0.05) over all {len(allp)} comparisons above: rejected = "
              + ", ".join(f"T{T} m{rate} {m}" for (T, rate, m) in order if rej.get((T, rate, m))), ""]
    # v5 against pselect_v2 / _cal
    if pairing.get("ext_narrow_eval") == 0:
        lines += ["## tolerant_v5 - pselect_union_v2(_cal), missing cells (IS difference, 95% CI)", "",
                  "| T | cell | v5 cov | v5 IS | v5 - pselect_v2 | v5 - pselect_v2_cal |", "|---|---|---|---|---|---|"]
        out["v5"] = {}
        for T in (40, 80, 150):
            for rate in (0.2, 0.5):
                c5 = out["cells"][f"{T}|missing|{rate}"]["tolerant_v5"]
                ds = [stats(T, "missing", rate, x, ref="tolerant_v5") for x in ("pselect_union_v2", "pselect_union_v2_cal")]
                out["v5"][f"{T}|{rate}"] = ds
                lines.append(f"| {T} | missing-{rate} | {c5['cov']:.3f} | {c5['IS']:.2f} | "
                             + " | ".join(f"{d['est']:+.2f} [{d['lo']:+.2f}, {d['hi']:+.2f}]" for d in ds) + " |")
    (OUT / "envelope.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "envelope.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
