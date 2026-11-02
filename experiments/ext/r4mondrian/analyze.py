"""Pre-registered analysis of r4mondrian (docs/ext/r4mondrian.md, section 3). Mechanical.

Inputs: results/<run>/pairs.npz and runs.jsonl from run_pairs.py; q tables from calibrate.py;
stored v5_1 rows (results/ext_v51_eval/runs.jsonl, or ext_v51_a1 for the scenario run) for V1.

Per run (topology, replicate, scenario, T, cell): IS = mean interval score over non-null pairs,
coverage pooled over pairs; cell IS = mean over runs (as the runner). Paired differences: cluster
bootstrap by topology (ratio of sums over resampled topologies), B = 20000, seed 20261104,
percentile 95% CI; one-sided p_less = (1 + #{b >= 0}) / (B + 1), p_greater = (1 + #{b <= 0}) / (B + 1);
two-sided p = min(1, 2 min(p_less, p_greater)). Holm step-down at 0.05.

Run:  python experiments/ext/r4mondrian/analyze.py --run ext_r4mondrian_eval --stored ext_v51_eval [--table q_table.json]
Writes results/<run>/<tag>.{md,json}.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from paper4 import ext_r4mondrian as X  # noqa: E402

KINDS = ["none", "extra", "missing", "reversed"]
CELLS = [("none", 0.0)] + [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]
OCAL = {40: 1.4, 80: 1.3, 150: 1.2}
B, SEED = 20000, 20261104


def holm(p, alpha=0.05):
    p = np.asarray(p, float)
    order = np.argsort(p)
    rej = np.zeros(len(p), bool)
    for rank, i in enumerate(order):
        if p[i] <= alpha / (len(p) - rank):
            rej[i] = True
        else:
            break
    return rej


def cluster_boot(topo, x, w=None):
    """Mean of x (weighted by w, default 1) with topology clusters: estimate, CI, p_less, p_greater, p2."""
    w = np.ones_like(x, dtype=float) if w is None else np.asarray(w, float)
    ids = np.unique(topo)
    sx = np.array([np.sum(x[topo == t] * w[topo == t]) for t in ids])
    sw = np.array([np.sum(w[topo == t]) for t in ids])
    est = float(sx.sum() / sw.sum())
    rng = np.random.default_rng(SEED)
    pick = rng.integers(0, len(ids), size=(B, len(ids)))
    b = sx[pick].sum(1) / sw[pick].sum(1)
    lo, hi = np.quantile(b, (0.025, 0.975))
    pl = (1 + int((b >= 0).sum())) / (B + 1)
    pg = (1 + int((b <= 0).sum())) / (B + 1)
    return {"est": est, "lo": float(lo), "hi": float(hi), "p_less": pl, "p_greater": pg, "p2": min(1.0, 2 * min(pl, pg))}


def iscore(lo, hi, x):
    return (hi - lo) + 40 * np.maximum(lo - x, 0) + 40 * np.maximum(x - hi, 0)


def check_v1(run, stored, scen_names):
    """V1: v5_1 rows of the driver vs stored runner rows (status, IS < 1e-12, covered, non-null)."""
    def key(r):
        return (r.get("scenario", "clean"), r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])
    a = {key(r): r for r in map(json.loads, open(ROOT / "results" / run / "runs.jsonl"))}
    b = {key(r): r for r in map(json.loads, open(ROOT / "results" / stored / "runs.jsonl"))
         if r["method"] == "tolerant_v5_1" and r.get("scenario", "clean") in scen_names}
    common = set(a) & set(b)
    same = 0
    for k in common:
        x, y = a[k], b[k]
        if x["status"] != y["status"]:
            continue
        if x["status"] != "ok" or (abs(x["iscore_nonnull_mean"] - y["iscore_nonnull_mean"]) < 1e-12
                                   and x["n_covered_nonnull"] == y["n_covered_nonnull"] and x["n_nonnull"] == y["n_nonnull"]):
            same += 1
    fails = sum(1 for r in a.values() if r["status"] != "ok")
    return {"n_driver": len(a), "n_stored": len(b), "common": len(common), "identical": same, "failed_runs": fails,
            "ok": len(a) == len(b) == len(common) == same and len(a) > 0}


def arms(P, table):
    """Half-widths of M0 and M2 for every pair from the q table."""
    T, st, R, h = P["T"], P["stated"], P["R"].astype(bool), P["h"]
    q0 = np.empty(len(T)); qR = np.empty(len(T)); qS = np.empty(len(T))
    for t in np.unique(T):
        for kc, kind in enumerate(KINDS):
            m = (T == t) & (st == kc)
            if m.any():
                q0[m] = table[f"{t}|{kind}|all"]["q"]
                qR[m] = table[f"{t}|{kind}|R"]["q"]
                qS[m] = table[f"{t}|{kind}|S"]["q"]
    return q0 * h, np.where(R, qR, qS) * h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--stored", default="ext_v51_eval")
    ap.add_argument("--table", default="q_table.json")
    ap.add_argument("--tag", default="ruling")
    ap.add_argument("--descriptive", action="store_true", help="no verdict (sensitivity / scenario runs)")
    a = ap.parse_args()
    P = dict(np.load(ROOT / "results" / a.run / "pairs.npz"))
    cfg = json.loads((ROOT / "results" / a.run / "manifest.json").read_text())["config"]
    scen_names = [s["name"] for s in (cfg.get("scenarios") or [{"name": "clean"}])]
    table = {k: v for k, v in json.loads((HERE / a.table).read_text()).items() if not k.startswith("_")}
    frozen = json.loads((ROOT / "experiments/ext/v51/frozen_v4_v51.json").read_text())
    cells = [("none", 0.0)] + [(k, r) for k in cfg["damage"]["kinds"] for r in cfg["damage"]["rates"]]
    Ts = cfg["T"]
    C, mid = P["C_t"], P["mid"]
    hM0, hM2 = arms(P, table)
    L = {"v51": (P["lo51"], P["hi51"]), "M0": (mid - hM0, mid + hM0), "M2": (mid - hM2, mid + hM2)}
    cov = {m: (lo <= C) & (C <= hi) for m, (lo, hi) in L.items()}
    isc = {m: iscore(lo, hi, C) for m, (lo, hi) in L.items()}
    runs = {s: [json.loads(x) for x in open(ROOT / "results" / a.run / "runs.jsonl")] for s in [0]}[0]
    res = {"run": a.run, "table": a.table, "cells": [], "V": {}}
    out = [f"# r4mondrian analysis `{a.tag}` of {a.run} (q table {a.table}; generated by experiments/ext/r4mondrian/analyze.py)", ""]

    # ---- validity
    v1 = check_v1(a.run, a.stored, scen_names)
    q_dev = max(abs(table[f"{T}|{k}|all"]["q"] - 0.5 * frozen[f"tolerant_v5_1|{T}|{k}"]) for T in (40, 80, 150) for k in KINDS)
    res["V"]["V1"] = v1
    res["V"]["V3_max_abs_q_minus_frozen"] = q_dev
    out += ["## Validity", "", f"- V1 (driver v5_1 rows = stored `{a.stored}` rows): {v1['identical']}/{v1['common']} identical "
            f"({v1['n_driver']} vs {v1['n_stored']} rows, failed runs {v1['failed_runs']}) -> **{'PASS' if v1['ok'] else 'FAIL'}**",
            f"- V3 (max |q_M0 − 0.5 × frozen factor| over 12 keys ≤ 0.05): {q_dev:.4f} -> **{'PASS' if q_dev <= 0.05 + 1e-12 else 'FAIL'}**"]

    # ---- per-cell statistics and paired differences
    rows_tab = []
    for sc_i, sc in enumerate(scen_names):
        for T in Ts:
            for c_idx, (kind, rate) in enumerate(cells):
                m = (P["scen"] == sc_i) & (P["T"] == T) & (P["cell"] == c_idx)
                if not m.any():
                    continue
                rid = P["topo"][m] * 10 + P["rep"][m]
                topo = P["topo"][m]
                ur, inv = np.unique(rid, return_inverse=True)
                rtopo = np.array([topo[inv == k][0] for k in range(len(ur))])
                per = {mm: np.bincount(inv, weights=isc[mm][m]) / np.bincount(inv) for mm in L}
                nrun_all = sum(1 for r in runs if r.get("scenario", "clean") == sc and r["T"] == T and r["kind"] == kind
                               and r["rate"] == rate)
                nfail = sum(1 for r in runs if r.get("scenario", "clean") == sc and r["T"] == T and r["kind"] == kind
                            and r["rate"] == rate and r["status"] != "ok")
                row = {"scen": sc, "T": T, "kind": kind, "rate": rate, "n_runs": int(len(ur)), "n_fail": nfail,
                       "of": nrun_all, "n_pairs": int(m.sum()), "share_R": float(P["R"][m].mean())}
                for mm in L:
                    row[f"cov_{mm}"] = float(cov[mm][m].mean())
                    row[f"IS_{mm}"] = float(per[mm].mean())
                    row[f"w_{mm}"] = float(np.median(L[mm][1][m] - L[mm][0][m]))
                for cls, cm in (("R", P["R"][m].astype(bool)), ("S", ~P["R"][m].astype(bool))):
                    for mm in L:
                        row[f"cov_{mm}_{cls}"] = float(cov[mm][m][cm].mean()) if cm.any() else None
                    row[f"n_{cls}"] = int(cm.sum())
                row["d_M2_v51"] = cluster_boot(rtopo, per["M2"] - per["v51"])
                row["d_M2_M0"] = cluster_boot(rtopo, per["M2"] - per["M0"])
                row["d_M0_v51"] = cluster_boot(rtopo, per["M0"] - per["v51"])
                # affected pairs (reversed cells; dC >= 0.05) vs oracle_cal
                if kind == "reversed" and np.isfinite(P["olo"][m]).all():
                    aff = P["dC"][m] >= 0.05
                    omid, ohalf = (P["olo"][m] + P["ohi"][m]) / 2, (P["ohi"][m] - P["olo"][m]) / 2
                    cov_ocal = (omid - OCAL[T] * ohalf <= C[m]) & (C[m] <= omid + OCAL[T] * ohalf)
                    if aff.any():
                        row["aff"] = {"n": int(aff.sum()), "cov_v51": float(cov["v51"][m][aff].mean()),
                                      "cov_M0": float(cov["M0"][m][aff].mean()), "cov_M2": float(cov["M2"][m][aff].mean()),
                                      "cov_ocal": float(cov_ocal[aff].mean()), "share_R": float(P["R"][m][aff].mean()),
                                      "d": cluster_boot(topo[aff], (cov["M2"][m][aff].astype(float) - cov["v51"][m][aff])),
                                      "gap_M2_ocal": cluster_boot(topo[aff], cov["M2"][m][aff].astype(float) - cov_ocal[aff]),
                                      "gap_v51_ocal": cluster_boot(topo[aff], cov["v51"][m][aff].astype(float) - cov_ocal[aff])}
                rows_tab.append(row)
    res["cells"] = rows_tab

    # ---- V4 and the rule (clean scenario only)
    clean = [r for r in rows_tab if r["scen"] == scen_names[0]]
    v4 = [(abs(r["IS_M0"] / r["IS_v51"] - 1) <= 0.02 and abs(r["cov_M0"] - r["cov_v51"]) <= 0.02) for r in clean]
    res["V"]["V4"] = {"pass": int(sum(v4)), "of": len(v4)}
    out.append(f"- V4 (M0 vs v5_1: |IS ratio − 1| ≤ 0.02 and |Δcov| ≤ 0.02, every cell): {sum(v4)}/{len(v4)} -> "
               f"**{'PASS' if all(v4) else 'FAIL'}**")
    valid = v1["ok"] and q_dev <= 0.05 + 1e-12 and all(v4)
    res["V"]["valid"] = valid
    out += [f"- Validity overall: **{'PASS' if valid else 'FAIL'}**", ""]

    out += ["## Cells (coverage pooled over non-null pairs; IS mean over runs)", "",
            "| scen | T | cell | runs ok | share R | cov v5_1 | cov M0 | cov M2 | IS v5_1 | IS M0 | IS M2 | M0 − v5_1 [CI] p2 | M2 − v5_1 [CI] p2 | M2 − M0 [CI] p2 |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    f = lambda d: f"{d['est']:+.3f} [{d['lo']:+.3f}, {d['hi']:+.3f}] {d['p2']:.4f}"  # noqa: E731
    for r in rows_tab:
        out.append(f"| {r['scen']} | {r['T']} | {r['kind']}-{r['rate']} | {r['n_runs']}/{r['of']} | {r['share_R']:.2f} | {r['cov_v51']:.3f} | "
                   f"{r['cov_M0']:.3f} | {r['cov_M2']:.3f} | {r['IS_v51']:.3f} | {r['IS_M0']:.3f} | {r['IS_M2']:.3f} | "
                   f"{f(r['d_M0_v51'])} | {f(r['d_M2_v51'])} | {f(r['d_M2_M0'])} |")
    out += ["", "## Coverage by class (R = structure-sensitive, S = rest)", "",
            "| scen | T | cell | n R | cov v5_1 R | cov M0 R | cov M2 R | n S | cov v5_1 S | cov M0 S | cov M2 S |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    g = lambda x: "–" if x is None else f"{x:.3f}"  # noqa: E731
    for r in rows_tab:
        out.append(f"| {r['scen']} | {r['T']} | {r['kind']}-{r['rate']} | {r['n_R']} | {g(r['cov_v51_R'])} | {g(r['cov_M0_R'])} | "
                   f"{g(r['cov_M2_R'])} | {r['n_S']} | {g(r['cov_v51_S'])} | {g(r['cov_M0_S'])} | {g(r['cov_M2_S'])} |")

    if not a.descriptive:
        dam = [r for r in clean if r["kind"] != "none"]
        h_v = holm([r["d_M2_v51"]["p2"] for r in dam])
        h_m = holm([r["d_M2_M0"]["p2"] for r in dam])
        for r, x, y in zip(dam, h_v, h_m):
            r["holm_v51"], r["holm_M0"] = bool(x), bool(y)
            r["win"] = bool(x and y and r["d_M2_v51"]["est"] < 0 and r["d_M2_M0"]["est"] < 0 and r["cov_M2"] >= 0.90)
        h_all = holm([r["d_M2_v51"]["p2"] for r in clean])
        worse = [bool(x and r["d_M2_v51"]["est"] > 0) for r, x in zip(clean, h_all)]
        n_win = sum(r["win"] for r in dam)
        cov_dam = all(r["cov_M2"] >= 0.90 and (r["n_fail"] <= 3) for r in dam)
        cov_none = all(r["cov_M2"] >= 0.90 and (r["n_fail"] <= 3) for r in clean if r["kind"] == "none")
        ratio_ok = all(r["IS_M2"] <= 1.05 * r["IS_v51"] for r in clean)
        no_worse = not any(worse)
        retained = valid and n_win >= 4 and cov_dam and cov_none and ratio_ok and no_worse
        res["rule"] = {"wins": n_win, "holm_v51_rejections_better": int(sum(1 for r in dam if r["holm_v51"] and r["d_M2_v51"]["est"] < 0)),
                       "holm_M0_rejections_better": int(sum(1 for r in dam if r["holm_M0"] and r["d_M2_M0"]["est"] < 0)),
                       "cov_damaged_all_ge_090": cov_dam, "cov_none_all_ge_090": cov_none, "ratio_le_105_all": ratio_ok,
                       "holm21_worse": int(sum(worse)), "valid": valid, "retained": retained}
        out += ["", "## Rule (section 3 of docs/ext/r4mondrian.md)", "",
                "| T | cell | cov M2 | M2 − v5_1 p2 | Holm 18 (v5_1) | M2 − M0 p2 | Holm 18 (M0) | WIN |", "|---|---|---|---|---|---|---|---|"]
        for r in dam:
            out.append(f"| {r['T']} | {r['kind']}-{r['rate']} | {r['cov_M2']:.3f} | {r['d_M2_v51']['p2']:.4f} | {'rej' if r['holm_v51'] else '-'} | "
                       f"{r['d_M2_M0']['p2']:.4f} | {'rej' if r['holm_M0'] else '-'} | {'WIN' if r['win'] else '-'} |")
        rr = res["rule"]
        out += ["", f"WIN {rr['wins']}/18 (Holm 18 vs v5_1, better: {rr['holm_v51_rejections_better']}/18; Holm 18 vs M0, better: "
                    f"{rr['holm_M0_rejections_better']}/18); coverage ≥ 0.90 in all 18 damaged cells: {cov_dam}; in the 3 none cells: {cov_none}; "
                    f"IS ratio M2/v5_1 ≤ 1.05 in all 21 cells: {ratio_ok}; Holm-21 significant worsening vs v5_1: {rr['holm21_worse']}/21; "
                    f"validity: {valid}.", "",
                f"**Verdict: {'RETAINED (exploratory)' if retained else 'NOT RETAINED'}**"]

        # secondary: affected pairs
        aff = [r for r in clean if "aff" in r]
        if aff:
            p1 = [r["aff"]["d"]["p_greater"] for r in aff]
            hh = holm(p1)
            out += ["", "## Secondary: reversal-affected pairs (dC ≥ 0.05), coverage; one-sided p (M2 > v5_1), Holm over 6", "",
                    "| T | cell | n aff | share R | cov v5_1 | cov M0 | cov M2 | cov oracle_cal | M2 − v5_1 [CI] | p | Holm 6 | v5_1 − oracle_cal [CI] | M2 − oracle_cal [CI] |",
                    "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
            for r, x in zip(aff, hh):
                d = r["aff"]
                d["holm6"] = bool(x and d["d"]["est"] > 0)
                out.append(f"| {r['T']} | {r['kind']}-{r['rate']} | {d['n']} | {d['share_R']:.2f} | {d['cov_v51']:.3f} | {d['cov_M0']:.3f} | "
                           f"{d['cov_M2']:.3f} | {d['cov_ocal']:.3f} | {d['d']['est']:+.3f} [{d['d']['lo']:+.3f}, {d['d']['hi']:+.3f}] | "
                           f"{d['d']['p_greater']:.4f} | {'rej' if d['holm6'] else '-'} | "
                           f"{d['gap_v51_ocal']['est']:+.3f} [{d['gap_v51_ocal']['lo']:+.3f}, {d['gap_v51_ocal']['hi']:+.3f}] | "
                           f"{d['gap_M2_ocal']['est']:+.3f} [{d['gap_M2_ocal']['lo']:+.3f}, {d['gap_M2_ocal']['hi']:+.3f}] |")
            out.append(f"\nSecondary count: M2 raises affected-pair coverage after Holm(6) in {sum(r['aff']['holm6'] for r in aff)}/6 cells.")

    (ROOT / "results" / a.run / f"{a.tag}.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (ROOT / "results" / a.run / f"{a.tag}.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
