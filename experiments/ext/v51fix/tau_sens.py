"""R3-2 (docs/ext/v51fix.md 1.C): descriptive tau sensitivity of tolerant_v5_1 at T = 150.
tolerant_v5_1_t294 (results/ext_v51fix_t150tau) vs tolerant_v5_1 (results/ext_v51_eval) through identical
tolerant_v4 rows, and vs tolerant_v4 in the same run.

Run: python experiments/ext/v51fix/tau_sens.py -> results/ext_v51fix_t150tau/{sens.md, sens.json}
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "ext" / "v51"))
sys.path.insert(0, str(ROOT / "experiments" / "ext" / "v51fix"))
from common import CELLS, RES, cell_stats, fmt_p, holm, index, load, paired  # noqa: E402
from pair_v4c_bl2 import identity  # noqa: E402

S294, M51, V4 = "tolerant_v5_1_t294", "tolerant_v5_1", "tolerant_v4"
T = 150


def main():
    run = load("ext_v51fix_t150tau")
    ev = [r for r in load("ext_v51_eval") if r["T"] == T]
    idn = identity(ev, run)
    out = ["# v51fix: tau sensitivity at T = 150 (experiments/ext/v51fix/tau_sens.py)", "",
           "D-07 development. tolerant_v5_1_t294 = tolerant_v5_1 with TAU 2.9370 (docs/ext/v51fix.md 1.C). "
           "Paired IS differences, 95% CI clustered by topology (1000, seed 0); one-sided p (10 000, seed 1); Holm 0.025 over 7 cells per direction.", "",
           f"Identity of tolerant_v4 rows (T = 150) with ext_v51_eval: {idn['exact_1e-12']}/{idn['common']} at 1e-12, "
           f"counts identical {idn['counts_identical']}, max |ΔIS| {idn['max_abs_IS_diff']:.2e} -> paired exact **{idn['paired_exact']}**", ""]
    rows = run + ([r for r in ev if r["method"] == M51] if (idn["paired_exact"] or idn["paired_float"]) else [])
    idx = index(rows)
    cal = json.loads((RES / "ext_v51fix_t150tau" / "calibration.json").read_text())
    cal51 = json.loads((RES / "ext_v51_eval" / "calibration.json").read_text())
    out += ["Width factors at T = 150 (runner value; effective = x 0.5): "
            + ", ".join(f"{k} t294 {cal[f'{S294}|150|{k}']} / v5_1 {cal51[f'{M51}|150|{k}']}" for k in ("none", "extra", "missing", "reversed")), ""]
    res = {"identity": idn, "cells": {}}
    S, P1, P2 = {}, {}, {}
    for c in CELLS:
        S[c] = {m: cell_stats(rows, m, T, *c) for m in (V4, M51, S294)}
        P1[c] = paired(idx, S294, M51, T, *c)
        P2[c] = paired(idx, S294, V4, T, *c)
    worse51 = holm([P1[c]["p_greater"] for c in CELLS])
    better51 = holm([P1[c]["p_less"] for c in CELLS])
    worse4 = holm([P2[c]["p_greater"] for c in CELLS])
    better4 = holm([P2[c]["p_less"] for c in CELLS])
    out += ["| cell | v4 cov / IS | v5_1 cov / IS | t294 cov / IS | t294 targeted share, r | t294 − v5_1 [CI] (p worse) | t294 − v4 [CI] (p worse / p better) | Holm: t294 worse than v5_1 / better | Holm: t294 worse than v4 / better |",
            "|---|---|---|---|---|---|---|---|---|"]
    for i, c in enumerate(CELLS):
        s = S[c]
        out.append(f"| {c[0]}-{c[1]} | {s[V4]['cov']:.3f} / {s[V4]['IS']:.3f} | {s[M51]['cov']:.3f} / {s[M51]['IS']:.3f} | "
                   f"{s[S294]['cov']:.3f} / {s[S294]['IS']:.3f} | {s[S294]['info_v51_targeted']:.2f}, {s[S294]['info_v51_ratio']:.2f} | "
                   f"{fmt_p(P1[c])} ({P1[c]['p_greater']:.4f}) | {fmt_p(P2[c])} ({P2[c]['p_greater']:.4f} / {P2[c]['p_less']:.4f}) | "
                   f"{int(worse51[i])} / {int(better51[i])} | {int(worse4[i])} / {int(better4[i])} |")
        res["cells"][f"{c[0]}|{c[1]}"] = {"stats": s, "t294_minus_v51": P1[c], "t294_minus_v4": P2[c],
                                          "holm_worse_than_v51": worse51[i], "holm_better_than_v51": better51[i],
                                          "holm_worse_than_v4": worse4[i], "holm_better_than_v4": better4[i]}
    # descriptive re-application of C2 (T=150 damaged) and C3 (T=150 none)
    c2 = {c: S[c][S294]["cov"] >= 0.90 and S[c][S294]["IS"] <= 1.05 * S[c][V4]["IS"] for c in CELLS if c[0] != "none"}
    c3 = S[("none", 0.0)][S294]["IS"] <= 1.05 * S[("none", 0.0)][V4]["IS"]
    miss = [("missing", 0.2), ("missing", 0.5)]
    sens = all(res["cells"][f"{c[0]}|{c[1]}"]["holm_worse_than_v51"] and P1[c]["lo"] > 0 for c in miss)
    miss_all = [S[c][S294]["info_v51_targeted"] for c in miss]
    out += ["", "## Pre-registered descriptive outputs (1.C)", "",
            f"1. Share of t294 missing runs in the targeted branch at T = 150: {miss_all} (0.00 = 100% all-lag).",
            f"3. C2 re-applied to t294 at T = 150 (6 damaged cells): {sum(c2.values())}/6 "
            f"({', '.join(f'{k[0]}-{k[1]}' for k, v in c2.items() if not v) or 'no failing cell'}); "
            f"C3 at T = 150 none: {'PASS' if c3 else 'FAIL'}.",
            f"   t294 significantly worse than v4 after Holm (7 cells): {sum(worse4)}/7; better: {sum(better4)}/7. "
            f"t294 significantly worse than v5_1 after Holm: {sum(worse51)}/7; better: {sum(better51)}/7.",
            "4. Interpretation rule: " + ("**T = 150 missing advantage depends on TAU > 4.94** (t294 − v5_1 has CI lower bound > 0 "
                                          "and is significant after Holm in both missing cells)." if sens else
                                          "**T = 150 results not sensitive to TAU in this scenario** (criterion of 1.C not met)."),
            "5. Non-missing cells: same code path for t294 and v5_1 (bootstrap stream by name and calibration differ): "
            + ", ".join(f"{c[0]}-{c[1]} {P1[c]['est']:+.3f}" for c in CELLS if c[0] != "missing") + "."]
    res.update({"C2_t294": {f"{k[0]}|{k[1]}": v for k, v in c2.items()}, "C3_t294": c3, "depends_on_tau": sens,
                "worse_than_v4_holm": sum(worse4), "worse_than_v51_holm": sum(worse51)})
    (RES / "ext_v51fix_t150tau" / "sens.md").write_text("\n".join(out) + "\n")
    (RES / "ext_v51fix_t150tau" / "sens.json").write_text(json.dumps(res, indent=1, default=float))
    print("\n".join(out))


if __name__ == "__main__":
    main()
