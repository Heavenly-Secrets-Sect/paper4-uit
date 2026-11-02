"""Confirmatory analysis of spec P7 (docs/ext/baselines3.md, "Frozen spec P7 for P4-H2"). Self-contained apart from
analyze.py (same directory, pinned in the spec manifest) and numpy.

P7 CONFIRMED for m in {tolerant_v4, tolerant_v5_1} iff
  (i)   pooled coverage(m) >= 0.90 in 4/4 cells (T 80/150 x missing 0.2/0.5; a failed run of m counts all its
        non-null pairs as uncovered);
  (ii)  failure rate of m <= 2% in every cell, and every validity check passes;
  (iii) every comparison in W_D07(m) (experiments/ext/baselines3/p7_win_set.json, the comparisons that were W under
        Holm on D-07 development) is W under Holm (two-sided 0.05) over the 56-comparison family on P4-H2;
  (iv)  0/28 comparisons of m are L under the same Holm.
Bonferroni overlay (lead, synthesis_round2 3.3): the same with Holm at 0.025, reported next to it.
Bootstrap: B = 20000 (not analyze.py's 4000). Reason, found on D-07 after the rule check: with B = 4000 the smallest
two-sided p is 2/4001 = 5.0e-4 > 0.025/56, so the Bonferroni overlay could reject nothing. Fixed here before any P4-H2
use; W_D07 itself comes from the pre-registered B = 4000 analysis.

Validity checks (any failure -> NOT CONFIRMED for both m, with the reason printed):
  - the run is the P4-H2 confirmatory run of experiments/configs/ext_baselines3_p4h2.json (manifest config equal
    to the config file, bank P4-H2, split confirmatory), baselines3_manifest.json present;
  - every (method, cell) has exactly 20 x 3 = 60 rows; only missing-0.2/0.5 at T 80/150;
  - every ok row of a calibrated method carries info_c_T equal to the frozen factor of its (T, stated kind);
  - method_modules in baselines3_manifest.json equal expected_modules of the config.

Usage:
  python experiments/ext/baselines3/analyze_p4h2.py                -> results/ext_baselines3_p4h2/ruling.{md,json}
  python experiments/ext/baselines3/analyze_p4h2.py --dev-dryrun   -> D-07 development rows (ext_baselines3_eval +
        stored tlp2_db_p3), output to results/ext_baselines3_dryrun_p4h2/ (pipeline test only, not a result)
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze as A  # noqa: E402

ROOT = HERE.parents[2]
CFG_PATH = ROOT / "experiments/configs/ext_baselines3_p4h2.json"
WIN = HERE / "p7_win_set.json"
B_P4H2 = 20000
P1_RUN = ROOT / "results/ext_v51fix_p4h2/runs.jsonl"     # consistency check only (same kinds list / seed_base)


def validity(rows, cfg, man, frozen, expect_bank):
    probs = []
    if man is None:
        probs.append("baselines3_manifest.json missing")
    elif man.get("method_modules") != {m: mod for m, mod in cfg["expected_modules"].items() if m in cfg["methods"]}:
        probs.append(f"method_modules {man.get('method_modules')} != expected_modules")
    cnt = Counter((r["method"], r["T"], r["kind"], round(float(r["rate"]), 6)) for r in rows)
    for m in cfg["methods"]:
        for T, rate in A.CELLS:
            if cnt.get((m, T, "missing", rate), 0) != 60:
                probs.append(f"{m} T{T} missing-{rate}: {cnt.get((m, T, 'missing', rate), 0)} rows, expected 60")
    extra = [k for k in cnt if (k[1], k[3]) not in A.CELLS or k[2] != "missing"]
    if extra:
        probs.append(f"unexpected cells {sorted(set(extra))[:5]}")
    for r in rows:
        m = r["method"]
        if r["status"] != "ok":
            continue
        key = None
        if m == "tolerant_v4":
            key = f"mod|{r['T']}|missing"
        elif m in cfg.get("calibrate_methods", []):
            key = f"{m}|{r['T']}|missing"
        if key is not None and r.get("info_c_T") != frozen.get(key):
            probs.append(f"{m} row c_T {r.get('info_c_T')} != frozen {key} = {frozen.get(key)}")
            break
    if expect_bank and (cfg["bank"] != "P4-H2" or cfg["split"] != "confirmatory"):
        probs.append("config is not the P4-H2 confirmatory config")
    return probs


def p7(res, win, col):
    out = {}
    for m in A.MODS:
        cov_ok = all(res["cells"][(m, T, r)]["cov"] >= A.COV_MIN for T, r in A.CELLS)
        fail_ok = all(res["cells"][(m, T, r)]["fail_rate"] <= A.FAIL_MAX for T, r in A.CELLS)
        ws = []
        for k in win[m]:
            X, T, r = k.split("|")
            ws.append((k, res["comps"][(m, X, int(T), float(r))][col]))
        win_ok = all(v == "W" for _, v in ws)
        L = [f"{X}|{T}|{r}" for X in A.ENVELOPE for T, r in A.CELLS if res["comps"][(m, X, T, r)][col] == "L"]
        out[m] = {"i_cov": cov_ok, "ii_fail": fail_ok, "iii_win_set": win_ok, "iii_detail": ws, "iv_noloss": not L,
                  "losses": L, "confirmed": bool(cov_ok and fail_ok and win_ok and not L),
                  "win_set_size": len(win[m]), "win_set_confirmed": sum(v == "W" for _, v in ws)}
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    dry = "--dev-dryrun" in argv
    cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))
    frozen = json.loads((ROOT / cfg["frozen_calibration"]).read_text(encoding="utf-8"))
    win = json.loads(WIN.read_text(encoding="utf-8"))["win_set_D07"]
    if dry:
        src = ROOT / "results/ext_baselines3_eval"
        out = ROOT / "results/ext_baselines3_dryrun_p4h2"
        rows = A.load(src / "runs.jsonl")
        tl = A.load(ROOT / "results/ext_tlp2_t80b/runs.jsonl") + A.load(ROOT / "results/ext_tlp2_t150c/runs.jsonl")
        rows += [r for r in tl if r["method"] == "tlp2_db_p3"]
        man = json.loads((src / "baselines3_manifest.json").read_text())
        man = dict(man, method_modules={**man["method_modules"], "tlp2_db_p3": "paper4.ext_tlp2"})
        probs = validity(rows, cfg, man, frozen, expect_bank=False)
    else:
        src = ROOT / "results" / cfg["name"]
        out = src
        rows = A.load(src / "runs.jsonl")
        mpath = src / "baselines3_manifest.json"
        man = json.loads(mpath.read_text()) if mpath.exists() else None
        runman = json.loads((src / "manifest.json").read_text())
        probs = validity(rows, cfg, man, frozen, expect_bank=True)
        if runman["config"] != cfg:
            probs.append("results manifest config differs from experiments/configs/ext_baselines3_p4h2.json")
    out.mkdir(parents=True, exist_ok=True)
    idx = A.index(rows, set(A.MODS + A.ENVELOPE))
    topologies = sorted({k[0] for k in idx})
    if len(topologies) != 20:
        probs.append(f"{len(topologies)} topologies, expected 20")
    A.B = B_P4H2
    res = A.score(idx, topologies)
    v05, v025 = p7(res, win, "holm0.05"), p7(res, win, "holm0.025")
    if probs:
        for m in A.MODS:
            v05[m]["confirmed"] = v025[m]["confirmed"] = False
    stmt = A.verdicts(res)
    consist = None
    if not dry and P1_RUN.exists():
        p1 = A.index(A.load(P1_RUN), {"tolerant_v4", "tolerant_v5_1"})
        mism = n = 0
        for k, r in idx.items():
            if k[5] in ("tolerant_v4", "tolerant_v5_1") and k in p1:
                n += 1
                a, b = r, p1[k]
                if a["status"] != b["status"] or (a["status"] == "ok" and (
                        abs(a["iscore_nonnull_mean"] - b["iscore_nonnull_mean"]) > 1e-8
                        or a["n_covered_nonnull"] != b["n_covered_nonnull"])):
                    mism += 1
        consist = {"n_compared": n, "mismatches": mism}
    lines = ["# Spec P7 ruling" + (" (DEV DRY RUN on D-07 development: pipeline test, NOT a result)" if dry else
                                   " (P4-H2 confirmatory)"), "",
             "Validity: " + ("PASS" if not probs else "FAIL: " + "; ".join(probs)), "",
             A.fmt_table(res), ""]
    for m in A.MODS:
        v, w = v05[m], v025[m]
        lines += [f"## {m}: **{'CONFIRMED' if v['confirmed'] else 'NOT CONFIRMED'}** (Holm 0.05); "
                  f"Bonferroni overlay (Holm 0.025): {'CONFIRMED' if w['confirmed'] else 'NOT CONFIRMED'}", "",
                  f"- (i) coverage >= 0.90 in 4/4 cells: {v['i_cov']} (" + ", ".join(
                      f"T{T} m{r} {res['cells'][(m, T, r)]['cov']:.3f}" for T, r in A.CELLS) + ")",
                  f"- (ii) failure <= 2%: {v['ii_fail']} (" + ", ".join(
                      f"{res['cells'][(m, T, r)]['n_fail']}/{res['cells'][(m, T, r)]['n_runs']}" for T, r in A.CELLS) + ")",
                  f"- (iii) W_D07 set confirmed: {v['win_set_confirmed']}/{v['win_set_size']} -> {v['iii_win_set']}",
                  f"- (iv) no L: {v['iv_noloss']} {v['losses'] or ''}",
                  f"- descriptive statement on these rows: {A.STMT[stmt[m]['statement']]}; W {stmt[m]['W']} / T {stmt[m]['T']} / L {stmt[m]['L']}; "
                  f"E-cell {stmt[m]['E_cell']}", ""]
    if consist is not None:
        lines.append(f"Consistency with results/ext_v51fix_p4h2 (v4/v5_1 rows at the same cells; informational): "
                     f"{consist['mismatches']} mismatches of {consist['n_compared']}")
    (out / ("ruling_dryrun.md" if dry else "ruling.md")).write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / ("ruling_dryrun.json" if dry else "ruling.json")).write_text(json.dumps(
        {"validity_problems": probs, "p7_holm0.05": v05, "p7_holm0.025": v025, "statements": stmt,
         "consistency_p1": consist, "result": A.jsonable(res)}, indent=1, default=str), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
