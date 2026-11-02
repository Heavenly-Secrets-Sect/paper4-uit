"""R2-3b: apply the pre-registered rule of docs/ext/auto5.md section 2.

tolerant_auto3 (results/ext_gate_auto3, round-1 rows) against the baselines width-calibrated per T
only (results/ext_auto5_fair, produced by fair_baselines.py). Paired by (topology, replicate, T,
kind, rate); differences IS(auto3) - IS(X) with a 95% CI and a two-sided p-value from a bootstrap
over topologies (2000 resamples, stats5.paired).

Win: auto3 coverage >= 0.90 and CI upper bound < 0. Loss: CI lower bound > 0. Else tie.
Holm (alpha 0.05) over the 21 cells of each baseline and over the 8 claim cells (missing/reversed x
0.2/0.5 at T = 80, 150): a Holm win is a Holm-rejected cell with negative estimate and auto3
coverage >= 0.90; a Holm loss is a Holm-rejected cell with positive estimate.

Run: python experiments/ext/auto5/compare_fair.py
Writes results/ext_auto5_fair/rule_check.md and rule_check.json.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stats5 as S  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "ext_auto5_fair"
BASE = ["plugin", "ida_union", "bvar_minnesota", "pselect_union"]
CELLS = [("none", 0.0), ("extra", 0.2), ("extra", 0.5), ("missing", 0.2), ("missing", 0.5),
         ("reversed", 0.2), ("reversed", 0.5)]
TS = (40, 80, 150)
A = "tolerant_auto3"


def main():
    fair = S.load(OUT / "runs.jsonl")
    gate = [r for r in S.load(ROOT / "results" / "ext_gate_auto3" / "runs.jsonl") if r["method"] in (A, "tolerant_v4")]
    rows = fair + gate
    idx = S.index(rows)
    grp = defaultdict(list)
    for r in rows:
        if r.get("status") == "ok" and r.get("iscore_nonnull_mean") is not None:
            grp[(r["T"], r["kind"], r["rate"], r["method"])].append(r)

    def cs(T, kind, rate, m):
        g = grp[(T, kind, rate, m)]
        return {"cov": S.coverage(g), "IS": float(np.mean([r["iscore_nonnull_mean"] for r in g])) if g else None,
                "n": len(g)}

    cal = json.loads((OUT / "calibration.json").read_text(encoding="utf-8"))
    J = {"factors": cal, "cells": {}, "rule": {}}
    L = ["# R2-3b: tolerant_auto3 vs baselines width-calibrated per T only (D-07 development)", "",
         "Baselines: factor per (baseline, T) tuned on D-07H development, pooled over all calibration cells "
         "including none; the stated kind is never read. `_calT` two-sided grid 0.5..5.0 (primary), `_calT1` "
         "one-sided grid 1.0..10.0, `_raw` uncalibrated. auto3 rows: results/ext_gate_auto3 (round 1).", "",
         "## Width factors", ""]
    for m in BASE:
        L.append(f"- {m}: calT " + ", ".join(f"T{T} {cal[f'{m}_calT|{T}']}" for T in TS)
                 + "; calT1 " + ", ".join(f"T{T} {cal[f'{m}_calT1|{T}']}" for T in TS)
                 + "; calibration-bank coverage at c = 1: " + ", ".join(f"T{T} {cal[f'_coverage_at_1|{m}|{T}']:.3f}" for T in TS))
    for T in TS:
        for kind, rate in CELLS:
            key = f"{T}|{kind}|{rate}"
            c = {"auto3": cs(T, kind, rate, A), "tolerant_v4": cs(T, kind, rate, "tolerant_v4")}
            sel = lambda k, T=T, kind=kind, rate=rate: k[3] == T and k[4] == kind and k[5] == rate  # noqa: E731
            for m in BASE:
                for suf in ("_calT", "_calT1", "_raw"):
                    c[m + suf] = cs(T, kind, rate, m + suf)
                    c[m + suf]["diff"] = S.paired(idx, sel, A, m + suf)
            J["cells"][key] = c

    # rule, primary version _calT
    claim_cells = [f"{T}|{k}|{r}" for T in (80, 150) for k in ("missing", "reversed") for r in (0.2, 0.5)]
    for suf in ("_calT", "_calT1", "_raw"):
        L += ["", f"## auto3 vs `X{suf}`: IS(auto3) - IS(X) [95% CI]; W/L/T = win/loss/tie by the rule", "",
              "| T | cell | auto3 cov / IS | " + " | ".join(f"{m}{suf} cov / IS | diff" for m in BASE) + " |",
              "|---|---|---|" + "---|---|" * len(BASE)]
        res = {}
        for m in BASE:
            res[m] = {}
            for key, c in J["cells"].items():
                d = c[m + suf]["diff"]
                if d is None:
                    res[m][key] = ("–", None, None)
                    continue
                if c["auto3"]["cov"] >= 0.90 and d["hi"] < 0:
                    out = "W"
                elif d["lo"] > 0:
                    out = "L"
                else:
                    out = "T"
                res[m][key] = (out, d["p"], d["est"])
        for key, c in J["cells"].items():
            T, kind, rate = key.split("|")
            L.append(f"| {T} | {kind} {rate} | {c['auto3']['cov']:.3f} / {c['auto3']['IS']:.2f} | " + " | ".join(
                f"{c[m + suf]['cov']:.3f} / {c[m + suf]['IS']:.2f} | {S.fmt(c[m + suf]['diff'])} {res[m][key][0]}" for m in BASE) + " |")
        L += ["", f"### Counts (`{suf}`)", "",
              "| baseline | wins / ties / losses (21 cells) | Holm wins / losses (21) | claim cells won (8) | Holm wins in claim cells (8) |",
              "|---|---|---|---|---|"]
        summ = {}
        for m in BASE:
            keys = list(J["cells"])
            outs = [res[m][k][0] for k in keys]
            ps = [res[m][k][1] for k in keys]
            rej = S.holm(ps)
            hw = sum(1 for k, h in zip(keys, rej) if h and res[m][k][2] < 0 and J["cells"][k]["auto3"]["cov"] >= 0.90)
            hl = sum(1 for k, h in zip(keys, rej) if h and res[m][k][2] > 0)
            cw = sum(res[m][k][0] == "W" for k in claim_cells)
            rej8 = S.holm([res[m][k][1] for k in claim_cells])
            hw8 = sum(1 for k, h in zip(claim_cells, rej8) if h and res[m][k][2] < 0 and J["cells"][k]["auto3"]["cov"] >= 0.90)
            summ[m] = {"wins": outs.count("W"), "ties": outs.count("T"), "losses": outs.count("L"), "holm_wins21": hw,
                       "holm_losses21": hl, "claim_wins8": cw, "holm_wins8": hw8,
                       "claim_cells_not_won": [k for k in claim_cells if res[m][k][0] != "W"],
                       "per_cell": {k: res[m][k][0] for k in keys}}
            L.append(f"| {m}{suf} | {outs.count('W')} / {outs.count('T')} / {outs.count('L')} | {hw} / {hl} | {cw}/8 | {hw8}/8 |")
        J["rule"][suf] = summ
        if suf == "_calT":
            ok = all(summ[m]["claim_wins8"] == 8 for m in BASE)
            J["rule"]["claim_allowed"] = ok
            L += ["", f"**Pre-registered claim (auto3 wins every X_calT in all 8 missing/reversed cells at T = 80, 150): "
                  f"{'ALLOWED' if ok else 'NOT ALLOWED'}.**"]
            if not ok:
                L.append("Claim cells not won: " + "; ".join(f"{m}: {', '.join(summ[m]['claim_cells_not_won']) or 'none'}" for m in BASE))
    # correct skeleton (none cell) report
    L += ["", "## Correct skeleton (none cell): auto3 - X", "", "| T | X | X cov / IS | auto3 - X |", "|---|---|---|---|"]
    for T in TS:
        c = J["cells"][f"{T}|none|0.0"]
        for m in ("ida_union_calT", "plugin_calT", "ida_union_calT1", "plugin_calT1", "ida_union_raw", "plugin_raw"):
            L.append(f"| {T} | {m} | {c[m]['cov']:.3f} / {c[m]['IS']:.2f} | {S.fmt(c[m]['diff'])} |")
    (OUT / "rule_check.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (OUT / "rule_check.json").write_text(json.dumps(J, indent=1), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
