"""Pre-registered analysis of R3-1 (docs/ext/baselines3.md section 3). Written before ext_baselines3_eval ran.

Family: m in {tolerant_v4, tolerant_v5_1} x X in ENVELOPE (7) x cell in {80, 150} x {missing 0.2, 0.5} = 56.
Per comparison: d = IS(m) - IS(X) per run (topology, replicate) where both are ok; estimate = mean; cluster
bootstrap over topologies with ONE shared index matrix (B = 4000, rng default_rng(20261102)); 95% percentile CI;
p_W = (1 + #{boot >= 0}) / (B + 1), p_L = (1 + #{boot <= 0}) / (B + 1), p2 = min(1, 2 min(p_W, p_L)).
Holm step-down over the 56 two-sided p at ALPHA (0.05; Bonferroni overlay 0.025): W / L / T. Raw CI counts too.
Coverage of m: pooled over non-null pairs of all runs; a failed run of m counts all its non-null pairs uncovered.

Rule (each m): E-cell(m, c) = cov >= 0.90, failure rate <= 2%, 7/7 W in c; E-full = 4/4 E-cell;
E-noloss = 0/28 L; E-major = W >= 15/28. Statement (a)-(d), first that holds.

Usage (D-07):  python experiments/ext/baselines3/analyze.py
  reads results/ext_baselines3_eval/runs.jsonl, tlp2_db_p3 rows from results/ext_tlp2_t80b and ext_tlp2_t150c,
  writes results/ext_baselines3_eval/{rule_check.md, analysis.json, describe.md}.
The functions load_rows / score / verdicts are reused by analyze_p4h2.py.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
MODS = ["tolerant_v4", "tolerant_v5_1"]
ENVELOPE = ["pselect_union_v3", "pselect_union_v3_cal", "pselect_cal", "fullvar_cal", "targeted_lp_cal",
            "tlp2_db_p3", "bvar_minnesota_v2_cal"]
CELLS = [(80, 0.2), (80, 0.5), (150, 0.2), (150, 0.5)]
B = 4000
SEED = 20261102
COV_MIN = 0.90
FAIL_MAX = 0.02


def load(p):
    with open(p, encoding="utf-8") as fh:
        return [json.loads(x) for x in fh]


def rkey(r):
    return (r["topology"], r["replicate"], r["T"], r["kind"], round(float(r["rate"]), 6))


def index(rows, methods):
    out = {}
    for r in rows:
        if r["method"] in methods and r["kind"] == "missing" and (r["T"], round(float(r["rate"]), 6)) in CELLS:
            out[rkey(r) + (r["method"],)] = r
    return out


def holm(pvals: dict, alpha: float) -> set:
    order = sorted(pvals, key=lambda k: (pvals[k], str(k)))
    rej, m = set(), len(order)
    for i, k in enumerate(order):
        if pvals[k] <= alpha / (m - i):
            rej.add(k)
        else:
            break
    return rej


def score(idx: dict, topologies: list[str], alpha: float = 0.05, mods=MODS, envelope=ENVELOPE) -> dict:
    """idx: (topology, replicate, T, kind, rate, method) -> row. Returns per-comparison stats and cell stats."""
    topologies = sorted(topologies)
    tpos = {t: i for i, t in enumerate(topologies)}
    ix = np.random.default_rng(SEED).integers(0, len(topologies), size=(B, len(topologies)))
    reps = sorted({k[1] for k in idx})
    nonnull = {}
    for k, r in idx.items():
        if r["status"] == "ok" and r.get("n_nonnull") is not None:
            nonnull[k[:5]] = r["n_nonnull"]
    cells, comps = {}, {}
    for m in mods + envelope:
        for T, rate in CELLS:
            runs = [(t, rp, T, "missing", rate) for t in topologies for rp in reps if (t, rp, T, "missing", rate) in nonnull]
            got = [idx.get(u + (m,)) for u in runs]
            n_fail = sum(1 for g in got if g is None or g["status"] != "ok")
            cov_num = sum(g["n_covered_nonnull"] for g in got if g is not None and g["status"] == "ok")
            cov_den = sum(nonnull[u] for u in runs)
            ok_is = [g["iscore_nonnull_mean"] for g in got if g is not None and g["status"] == "ok"
                     and g.get("iscore_nonnull_mean") is not None]
            cells[(m, T, rate)] = {"n_runs": len(runs), "n_fail": n_fail, "fail_rate": n_fail / len(runs) if runs else None,
                                   "cov": cov_num / cov_den if cov_den else float("nan"),
                                   "IS": float(np.mean(ok_is)) if ok_is else float("nan"),
                                   "n_ok": len(ok_is)}
    for m in mods:
        for X in envelope:
            for T, rate in CELLS:
                sums, cnts = np.zeros(len(topologies)), np.zeros(len(topologies))
                for t in topologies:
                    for rp in reps:
                        a = idx.get((t, rp, T, "missing", rate, m))
                        b = idx.get((t, rp, T, "missing", rate, X))
                        if a and b and a["status"] == "ok" and b["status"] == "ok" \
                                and a.get("iscore_nonnull_mean") is not None and b.get("iscore_nonnull_mean") is not None:
                            sums[tpos[t]] += a["iscore_nonnull_mean"] - b["iscore_nonnull_mean"]
                            cnts[tpos[t]] += 1
                if cnts.sum() == 0:
                    comps[(m, X, T, rate)] = {"n": 0, "est": float("nan"), "lo": float("nan"), "hi": float("nan"),
                                              "pW": 1.0, "pL": 1.0, "p2": 1.0}
                    continue
                est = float(sums.sum() / cnts.sum())
                with np.errstate(invalid="ignore", divide="ignore"):
                    boots = sums[ix].sum(1) / cnts[ix].sum(1)
                boots = boots[np.isfinite(boots)]
                lo, hi = np.quantile(boots, (0.025, 0.975))
                pW = (1 + int((boots >= 0).sum())) / (len(boots) + 1)
                pL = (1 + int((boots <= 0).sum())) / (len(boots) + 1)
                comps[(m, X, T, rate)] = {"n": int(cnts.sum()), "est": est, "lo": float(lo), "hi": float(hi),
                                          "pW": pW, "pL": pL, "p2": min(1.0, 2 * min(pW, pL))}
    for a_ in sorted({alpha, 0.025}):
        rej = holm({k: v["p2"] for k, v in comps.items()}, a_)
        for k, v in comps.items():
            v[f"holm{a_}"] = ("W" if v["est"] < 0 else "L") if k in rej else "T"
    for v in comps.values():
        v["raw"] = "W" if v["hi"] < 0 else ("L" if v["lo"] > 0 else "T")
    return {"cells": cells, "comps": comps}


def verdicts(res: dict, mods=MODS, envelope=ENVELOPE, col: str = "holm0.05") -> dict:
    out = {}
    for m in mods:
        ecell = {}
        for T, rate in CELLS:
            c = res["cells"][(m, T, rate)]
            ws = [res["comps"][(m, X, T, rate)][col] == "W" for X in envelope]
            ecell[f"{T}|{rate}"] = bool(c["cov"] >= COV_MIN and c["fail_rate"] <= FAIL_MAX and all(ws))
        cl = [res["comps"][(m, X, T, r)][col] for X in envelope for T, r in CELLS]
        W, L = cl.count("W"), cl.count("L")
        full = all(ecell.values())
        noloss = L == 0
        major = W >= 15
        if full:
            stmt = "a"
        elif noloss and any(ecell.values()):
            stmt = "b"
        elif noloss:
            stmt = "c"
        else:
            stmt = "d"
        losses = [f"{X} @ T{T} missing-{r}" for X in envelope for T, r in CELLS if res["comps"][(m, X, T, r)][col] == "L"]
        out[m] = {"E_cell": ecell, "E_full": full, "E_noloss": noloss, "E_major": major, "W": W, "T": cl.count("T"),
                  "L": L, "statement": stmt, "losses": losses,
                  "cov_ok_cells": sum(res["cells"][(m, T, r)]["cov"] >= COV_MIN for T, r in CELLS)}
    return out


def fmt_table(res, mods=MODS, envelope=ENVELOPE):
    lines = ["| m | X | T | cell | cov m | IS m | IS X | cov X | m - X [95% CI] | p2 | raw | Holm 0.05 | Holm 0.025 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in mods:
        for T, rate in CELLS:
            for X in envelope:
                c = res["comps"][(m, X, T, rate)]
                cm, cx = res["cells"][(m, T, rate)], res["cells"][(X, T, rate)]
                lines.append(f"| {m} | {X} | {T} | missing-{rate} | {cm['cov']:.3f} | {cm['IS']:.2f} | {cx['IS']:.2f} | "
                             f"{cx['cov']:.3f} | {c['est']:+.2f} [{c['lo']:+.2f}, {c['hi']:+.2f}] | {c['p2']:.4f} | "
                             f"{c['raw']} | {c['holm0.05']} | {c['holm0.025']} |")
    return "\n".join(lines)


def jsonable(res):
    return {"cells": {"|".join(map(str, k)): v for k, v in res["cells"].items()},
            "comps": {"|".join(map(str, k)): v for k, v in res["comps"].items()}}


STMT = {"a": "(a) thắng mọi baseline ở 4/4 cell", "b": "(b) không thua; thắng envelope ở một số cell",
        "c": "(c) không thua; không thắng trọn cell nào", "d": "(d) có so sánh thua"}


def regression(new_rows):
    """Fresh rows vs stored rows of the same (data, skeleton, cell position)."""
    checks = {"tolerant_v4": "ext_baselines2_eval", "bvar_minnesota_v2_cal": "ext_baselines2_eval",
              "tolerant_v5_1": "ext_v51_eval", "pselect_cal": "ext_redteam_calbase", "fullvar_cal": "ext_redteam_calbase",
              "targeted_lp": "ext_tlp_eval", "targeted_lp_cal": "ext_tlp_eval"}
    new = index(new_rows, set(checks))
    out = {}
    cache = {}
    for m, src in checks.items():
        if src not in cache:
            cache[src] = index(load(ROOT / "results" / src / "runs.jsonl"), set(checks))
        old = cache[src]
        keys = [k for k in new if k[5] == m]
        mism = 0
        for k in keys:
            a, b = new[k], old.get(k)
            if b is None or a["status"] != b["status"] or (a["status"] == "ok" and (
                    a["iscore_nonnull_mean"] != b["iscore_nonnull_mean"] or a["n_covered_nonnull"] != b["n_covered_nonnull"])):
                mism += 1
        out[m] = {"source": src, "n_rows": len(keys), "mismatches": mism}
    return out


def main() -> int:
    out = ROOT / "results" / "ext_baselines3_eval"
    rows = load(out / "runs.jsonl")
    tl = load(ROOT / "results/ext_tlp2_t80b/runs.jsonl") + load(ROOT / "results/ext_tlp2_t150c/runs.jsonl")
    rows_all = rows + [r for r in tl if r["method"] == "tlp2_db_p3"]
    idx = index(rows_all, set(MODS + ENVELOPE))
    topologies = sorted({k[0] for k in idx})
    res = score(idx, topologies)
    ver = verdicts(res)
    ver025 = verdicts(res, col="holm0.025")
    reg = regression(rows)
    lines = ["# R3-1 rule check (D-07 development, exploratory)", "",
             f"Runs: results/ext_baselines3_eval (all methods except tlp2_db_p3), tlp2_db_p3 from results/ext_tlp2_t80b + "
             f"ext_tlp2_t150c (content seeded). {len(topologies)} topologies.", "",
             "Regression (fresh vs stored rows; expected 0): " + ", ".join(
                 f"{m} vs {v['source']}: {v['mismatches']}/{v['n_rows']}" for m, v in reg.items()), "",
             fmt_table(res), ""]
    for m in MODS:
        v, v2 = ver[m], ver025[m]
        lines += [f"## {m}", "",
                  f"- coverage >= 0.90 in {v['cov_ok_cells']}/4 cells; failure rates: " + ", ".join(
                      f"T{T} m{r}: {res['cells'][(m, T, r)]['n_fail']}/{res['cells'][(m, T, r)]['n_runs']}" for T, r in CELLS),
                  f"- Holm 0.05 over 56: W {v['W']} / T {v['T']} / L {v['L']} (of 28); E-cell: {v['E_cell']}",
                  f"- E-full {v['E_full']}, E-noloss {v['E_noloss']}, E-major {v['E_major']} -> statement **{STMT[v['statement']]}**",
                  f"- losses: {v['losses'] or 'none'}",
                  f"- raw CI counts: W {sum(res['comps'][(m, X, T, r)]['raw'] == 'W' for X in ENVELOPE for T, r in CELLS)} / "
                  f"L {sum(res['comps'][(m, X, T, r)]['raw'] == 'L' for X in ENVELOPE for T, r in CELLS)} (of 28)",
                  f"- Bonferroni overlay (Holm 0.025): W {v2['W']} / T {v2['T']} / L {v2['L']}; E-cell {v2['E_cell']}; statement {v2['statement']}",
                  ""]
    win_set = {m: [f"{X}|{T}|{r}" for X in ENVELOPE for T, r in CELLS if res["comps"][(m, X, T, r)]["holm0.05"] == "W"]
               for m in MODS}
    (out / "rule_check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "analysis.json").write_text(json.dumps({"result": jsonable(res), "verdicts": ver, "verdicts_holm0.025": ver025,
                                                   "regression": reg, "win_set_D07": win_set}, indent=1), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
