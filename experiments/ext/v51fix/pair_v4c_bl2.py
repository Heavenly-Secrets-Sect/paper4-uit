"""R3-2 (docs/ext/v51fix.md, 1.A and 1.B): free pairings of tolerant_v5_1 (results/ext_v51_eval) with
tolerant_v4c and the *_c2 baselines (results/ext_v4c_eval) and with pselect_union_v2(_cal) and
bvar_minnesota_v2(_cal) (results/ext_baselines2_eval), through identical tolerant_v4 rows.

Run: python experiments/ext/v51fix/pair_v4c_bl2.py -> results/ext_v51fix_pairs/{pairs.md, pairs.json}
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "ext" / "v51"))
from common import CELLS, RES, TS, cell_stats, fmt_p, holm, index, key, load, paired  # noqa: E402

OUT = RES / "ext_v51fix_pairs"
M = "tolerant_v5_1"
SOURCES = {"ext_v4c_eval": ["tolerant_v4c", "pselect_union_c2", "ida_union_c2", "bvar_minnesota_c2"],
           "ext_baselines2_eval": ["pselect_union_v2", "pselect_union_v2_cal", "bvar_minnesota_v2_cal", "bvar_minnesota_v2"]}
MISS40 = [(40, "missing", 0.2), (40, "missing", 0.5)]
MAIN4 = [(T, "missing", r) for T in (80, 150) for r in (0.2, 0.5)]


def identity(a_rows, b_rows):
    a = {key(r): r for r in a_rows if r["method"] == "tolerant_v4"}
    b = {key(r): r for r in b_rows if r["method"] == "tolerant_v4"}
    common = set(a) & set(b)
    exact = counts_same = 0
    maxdiff = 0.0
    for k in common:
        x, y = a[k], b[k]
        if x["status"] != y["status"]:
            continue
        if x["status"] != "ok":
            exact += 1
            counts_same += 1
            continue
        same_counts = x["n_covered_nonnull"] == y["n_covered_nonnull"] and x["n_nonnull"] == y["n_nonnull"]
        d = abs(x["iscore_nonnull_mean"] - y["iscore_nonnull_mean"])
        maxdiff = max(maxdiff, d)
        if same_counts:
            counts_same += 1
            if d < 1e-12:
                exact += 1
    full = len(a) == len(b) == len(common)
    return {"n_a": len(a), "n_b": len(b), "common": len(common), "exact_1e-12": exact, "counts_identical": counts_same,
            "max_abs_IS_diff": maxdiff, "paired_exact": full and exact == len(a),
            "paired_float": full and counts_same == len(a) and maxdiff < 1e-9}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ev = load("ext_v51_eval")
    rows = [r for r in ev if r["method"] in ("tolerant_v4", M)]
    out = ["# v51fix: free pairings of tolerant_v5_1 (experiments/ext/v51fix/pair_v4c_bl2.py)", "",
           "D-07 development, seed_base 20261102. Rules: docs/ext/v51fix.md 1.A, 1.B. Paired IS difference v5_1 − X, "
           "95% CI clustered by topology (1000, seed 0); one-sided p (10 000, seed 1); Holm 0.025 per direction.", "",
           "## Identity of tolerant_v4 rows with ext_v51_eval", ""]
    res = {"identity": {}, "cells": {}, "counts": {}}
    xs = []
    for run, ms in SOURCES.items():
        other = load(run)
        idn = identity(ev, other)
        res["identity"][run] = idn
        out.append(f"- {run}: {idn['exact_1e-12']}/{idn['common']} identical at 1e-12, counts identical {idn['counts_identical']}, "
                   f"max |ΔIS| {idn['max_abs_IS_diff']:.2e} -> paired exact **{idn['paired_exact']}**, paired (float) {idn['paired_float']}")
        if idn["paired_exact"] or idn["paired_float"]:
            rows += [r for r in other if r["method"] in ms]
            xs += ms
    idx = index(rows)
    cells = [(T, k, r) for T in TS for k, r in CELLS]
    for X in xs:
        S, P = {}, {}
        for c in cells:
            S[c] = (cell_stats(rows, M, *c), cell_stats(rows, X, *c))
            P[c] = paired(idx, M, X, *c)
        win_raw = [S[c][0]["cov"] >= 0.90 and P[c]["hi"] < 0 for c in cells]
        lose_raw = [S[c][1]["cov"] >= 0.90 and P[c]["lo"] > 0 for c in cells]
        p_win = [P[c]["p_less"] if S[c][0]["cov"] >= 0.90 else 1.0 for c in cells]
        p_lose = [P[c]["p_greater"] if S[c][1]["cov"] >= 0.90 else 1.0 for c in cells]
        win_h, lose_h = holm(p_win), holm(p_lose)
        sub = lambda sel, v: sum(v[cells.index(c)] for c in sel)  # noqa: E731
        win_h4 = holm([p_win[cells.index(c)] for c in MAIN4])
        lose_h4 = holm([p_lose[cells.index(c)] for c in MAIN4])
        cnt = {"v51_wins_raw_21": sum(win_raw), "v51_wins_holm_21": sum(win_h), "X_wins_raw_21": sum(lose_raw),
               "X_wins_holm_21": sum(lose_h),
               "T40miss_v51_wins_raw": sub(MISS40, win_raw), "T40miss_v51_wins_holm21": sub(MISS40, win_h),
               "T40miss_X_wins_raw": sub(MISS40, lose_raw), "T40miss_X_wins_holm21": sub(MISS40, lose_h),
               "main4_v51_wins_raw": sub(MAIN4, win_raw), "main4_v51_wins_holm4": sum(win_h4),
               "main4_v51_wins_holm21": sub(MAIN4, win_h),
               "main4_X_wins_raw": sub(MAIN4, lose_raw), "main4_X_wins_holm4": sum(lose_h4),
               "X_wins_cells_holm21": [f"{c[0]} {c[1]}-{c[2]}" for c, h in zip(cells, lose_h) if h],
               "X_wins_cells_raw": [f"{c[0]} {c[1]}-{c[2]}" for c, h in zip(cells, lose_raw) if h],
               "v51_wins_cells_holm21": [f"{c[0]} {c[1]}-{c[2]}" for c, h in zip(cells, win_h) if h]}
        res["counts"][X] = cnt
        out += ["", f"## v5_1 vs {X}", "",
                f"- 21 cells: v5_1 wins {cnt['v51_wins_raw_21']} raw / {cnt['v51_wins_holm_21']} Holm; "
                f"{X} wins {cnt['X_wins_raw_21']} raw / {cnt['X_wins_holm_21']} Holm",
                f"- T40 missing (2): v5_1 wins {cnt['T40miss_v51_wins_raw']} raw / {cnt['T40miss_v51_wins_holm21']} Holm(21); "
                f"{X} wins {cnt['T40miss_X_wins_raw']} raw / {cnt['T40miss_X_wins_holm21']} Holm(21)",
                f"- T80/150 missing (4): v5_1 wins {cnt['main4_v51_wins_raw']} raw / {cnt['main4_v51_wins_holm4']} Holm(4) / "
                f"{cnt['main4_v51_wins_holm21']} Holm(21); {X} wins {cnt['main4_X_wins_raw']} raw / {cnt['main4_X_wins_holm4']} Holm(4)",
                f"- cells where {X} wins: raw {cnt['X_wins_cells_raw']}, Holm(21) {cnt['X_wins_cells_holm21']}", "",
                f"| T | cell | v5_1 cov / IS | {X} cov / IS | v5_1 − X [95% CI] | p less / p greater | win raw/Holm | X wins raw/Holm |",
                "|---|---|---|---|---|---|---|---|"]
        for i, c in enumerate(cells):
            a, b = S[c]
            p = P[c]
            out.append(f"| {c[0]} | {c[1]}-{c[2]} | {a['cov']:.3f} / {a['IS']:.3f} | {b['cov']:.3f} / {b['IS']:.3f} | {fmt_p(p)} | "
                       f"{p['p_less']:.4f} / {p['p_greater']:.4f} | {int(win_raw[i])}/{int(win_h[i])} | {int(lose_raw[i])}/{int(lose_h[i])} |")
            res["cells"][f"{X}|{c[0]}|{c[1]}|{c[2]}"] = {"v51": a, "X": b, "paired": p, "win_raw": win_raw[i], "win_holm21": win_h[i],
                                                       "Xwin_raw": lose_raw[i], "Xwin_holm21": lose_h[i]}
    # pre-registered descriptive criterion 1.A
    if "tolerant_v4c" in res["counts"]:
        c = res["counts"]["tolerant_v4c"]
        crit = c["T40miss_v51_wins_holm21"] == 2 and c["X_wins_holm_21"] == 0
        res["subsumes_v4c"] = crit
        out += ["", "## Pre-registered criterion 1.A ('v5_1 subsumes v4c')", "",
                f"(i) v5_1 beats v4c at both T40 missing cells after Holm(21): {c['T40miss_v51_wins_holm21']}/2; "
                f"(ii) v4c beats v5_1 after Holm(21): {c['X_wins_holm_21']}/21 -> **{'HOLDS' if crit else 'DOES NOT HOLD'}**"]
    (OUT / "pairs.md").write_text("\n".join(out) + "\n")
    (OUT / "pairs.json").write_text(json.dumps(res, indent=1, default=float))
    print("\n".join(l for l in out if not l.startswith("|")))


if __name__ == "__main__":
    main()
