"""Signal-quality proxies for the LLM outputs (direction "llm"); makes NO LLM call.

There is no ground truth on the real panel. Proxies:
1. Self-consistency across prompt variants (L1 Kendall tau, L4 agreement, L3 Jaccard).
2. Agreement with Paper 1: (a) the pipeline-accepted relations among the 14 core nodes;
   (b) the human gold labels (evaluation_benchmark/ground_truth_v1.2_draft.jsonl, 16 relations among the
   core nodes, 11 distinct pairs). L4 retrieval includes Paper 1's evidence chunks, so (a) and (b) are
   NOT independent of the text the LLM read; they measure faithfulness more than truth.
3. Agreement with the data where the data speak: bivariate Granger tests (lag 1) on the 14 x 19 panel
   (first differences for the 8 columns that fail a unit-root test in levels, per ACIIDS
   node_set_selection.md), and a pairwise LiNGAM direction measure on AR(1) residuals. With T = 19 (17
   usable residuals) both are very weak; 7 banking columns are simulated_calibrated or derived, so the
   "data direction" for banking pairs is a property of the simulator, not of Vietnam.
4. L3 against the observed policy-rate changes (macro_policy_rate_pct is real SBV data).
5. Translation to the binormal AUROC scale used by textinfo (AUROC = Phi(d / sqrt 2)).

Output: results/ext_llm_quality/quality.json
"""
from __future__ import annotations

import collections
import itertools
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (MATRIX_PATH, NODES, QUARTERS, ROOT, SHORT, FROM_SHORT, load_gold, load_panel,  # noqa: E402
                    load_relations)

OUT = ROOT / "results" / "ext_llm_quality"
DIFF = {"bank_npl_ratio", "bank_ldr_ratio", "bank_provision_coverage_proxy_pct", "stock_adj_close_last_vnd",
        "stock_avg_daily_volume_cp", "stock_avg_daily_trade_value_vnd", "macro_cpi_avg_pct", "macro_policy_rate_pct"}
SIMULATED = {"bank_npl_ratio", "bank_car_ratio", "bank_nim_ratio", "bank_roe_ratio", "bank_ldr_ratio",
             "bank_provision_coverage_proxy_pct", "bank_z_score"}


def auroc(pos, neg):
    if not pos or not neg:
        return None
    s = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return s / (len(pos) * len(neg))


def auroc_ci(pos, neg, B=4000, seed=1):
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(B):
        p = list(rng.choice(pos, len(pos)))
        n = list(rng.choice(neg, len(neg)))
        vals.append(auroc(p, n))
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def transformed_panel():
    X = load_panel()
    cols = []
    for k, n in enumerate(NODES):
        x = X[:, k]
        cols.append(np.diff(x) if n in DIFF else x[1:])
    return np.column_stack(cols)  # 18 x 14, aligned 2020Q3..2024Q4


def granger_p(Y, i, j):
    """p-value of 'x_i Granger-causes x_j' (lag 1, bivariate)."""
    y, x = Y[1:, j], Y[:-1, i]
    ylag = Y[:-1, j]
    n = len(y)
    Xr = np.column_stack([np.ones(n), ylag])
    Xu = np.column_stack([np.ones(n), ylag, x])
    rss = lambda A: float(np.sum((y - A @ np.linalg.lstsq(A, y, rcond=None)[0]) ** 2))  # noqa: E731
    rr, ru = rss(Xr), rss(Xu)
    F = (rr - ru) / (ru / (n - 3))
    return float(1 - stats.f.cdf(F, 1, n - 3))


def ar1_resid(Y):
    R = []
    for k in range(Y.shape[1]):
        y, yl = Y[1:, k], Y[:-1, k]
        A = np.column_stack([np.ones(len(y)), yl])
        e = y - A @ np.linalg.lstsq(A, y, rcond=None)[0]
        R.append((e - e.mean()) / (e.std() + 1e-12))
    return np.column_stack(R)


def lingam_measure(ex, ey):
    """Hyvarinen & Smith (2013) tanh likelihood-ratio approximation; > 0 suggests x -> y."""
    rho = float(np.mean(ex * ey))
    return rho * float(np.mean(ex * np.tanh(ey) - np.tanh(ex) * ey))


def lingam_boot(R, i, j, B=500, seed=3):
    rng = np.random.default_rng(seed)
    n = R.shape[0]
    v = [lingam_measure(R[idx, i], R[idx, j]) for idx in (rng.integers(0, n, n) for _ in range(B))]
    return float(np.mean(np.array(v) > 0))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    order = json.loads((ROOT / "results/ext_llm_order/order.json").read_text(encoding="utf-8"))
    edges = json.loads((ROOT / "results/ext_llm_edges/edges.json").read_text(encoding="utf-8"))
    shocks = json.loads((ROOT / "results/ext_llm_shocks/events.json").read_text(encoding="utf-8"))
    q = {"notes": "Proxies only; no ground truth on real data. See docs/ext/llm.md."}

    # 1. self-consistency
    q["self_consistency"] = {
        "L1_kendall_tau": order["kendall_tau"],
        "L1_prior_edges_reversed_per_order": {v: o["n_prior_edges_reversed"] for v, o in order["orders"].items()},
        "L4": edges["summary"],
        "L3": {k: shocks["summary"][k] for k in ("usable_keys_A", "usable_keys_B", "keys_both", "jaccard_A_B")},
    }
    # L1 stability restricted to pairs where an order is meaningful: within a domain block, and the 21 prior pairs
    def pos_of(v):
        return {n: k for k, n in enumerate(order["orders"][v]["order"])}
    P_ = {v: pos_of(v) for v in ("T1", "T2", "P", "pooled")}
    blocks = collections.defaultdict(list)
    for n in NODES:
        blocks[n.split("_")[0]].append(SHORT[n])
    within = {}
    for v1, v2 in (("T1", "T2"), ("T1", "P"), ("T2", "P")):
        conc = disc = 0
        for blk in blocks.values():
            for x_, y_ in itertools.combinations(blk, 2):
                s1 = np.sign(P_[v1][x_] - P_[v1][y_])
                s2 = np.sign(P_[v2][x_] - P_[v2][y_])
                conc += s1 == s2
                disc += s1 != s2
        within[f"{v1}~{v2}"] = (conc - disc) / (conc + disc)
    q["self_consistency"]["L1_kendall_tau_within_domain_blocks"] = within
    prior_or = {}
    for v1, v2 in (("T1", "T2"), ("T1", "P"), ("T2", "P")):
        same = sum((P_[v1][e["source"]] < P_[v1][e["target"]]) == (P_[v2][e["source"]] < P_[v2][e["target"]])
                   for e in order["prior_edges"])
        prior_or[f"{v1}~{v2}"] = same / len(order["prior_edges"])
    q["self_consistency"]["L1_orientation_agreement_on_21_prior_pairs"] = prior_or
    pv = [r for r in edges["pairs"] if set(r["per_variant"]) == {"A", "B"}]
    a = [r["per_variant"]["A"]["p_edge"] for r in pv]
    b = [r["per_variant"]["B"]["p_edge"] for r in pv]
    r_ab = float(np.corrcoef(a, b)[0, 1])
    q["self_consistency"]["L4_support_pearson_A_B"] = r_ab
    q["self_consistency"]["L4_mean_p_edge"] = {"A": float(np.mean(a)), "B": float(np.mean(b))}

    # cross-method: L1 (no text) vs L4 (text) on reversal of prior edges
    l1 = {(e["source_id"], e["target_id"]): e for e in order["prior_edges"]}
    l4 = {(r["prior_source"], r["prior_target"]): r for r in edges["pairs"] if r["kind"] == "prior"}
    ks = sorted(set(l1) & set(l4))
    x1 = [l1[k]["reversal_suspicion"] for k in ks]
    x4 = [l4[k]["reversal_score"] for k in ks]
    q["cross_method_L1_vs_L4_reversal_spearman"] = float(stats.spearmanr(x1, x4).statistic)
    q["cross_method_flagged_by_both"] = [f"{SHORT[s]}->{SHORT[t]}" for (s, t) in ks
                                         if l1[(s, t)]["reversal_suspicion"] > 0.5 and l4[(s, t)]["reversal_score"] > 0.5]

    # 2a. Paper 1 pipeline-accepted relations among core nodes (direction per pair)
    rels = [r for r in load_relations() if r["final_status"] == "accepted"]
    acc = collections.Counter()
    for r in rels:
        s, t = r["relation"]["source_node"], r["relation"]["target_node"]
        if s in NODES and t in NODES and s != t:
            acc[(s, t)] += 1
    l4pair = {tuple(r["pair"]): r for r in edges["pairs"]}
    pos_order = {FROM_SHORT[n]: k for k, n in enumerate(order["orders"]["pooled"]["order"])}
    rows = []
    for (s, t), n in acc.items():
        r = l4pair.get(tuple(sorted((s, t))))
        l4dir = None
        if r and r["direction_majority"] not in ("unclear", "disagree", "both"):
            l4dir = r["direction_majority"] == f"{SHORT[s]}->{SHORT[t]}"
        rows.append({"relation": f"{SHORT[s]}->{SHORT[t]}", "n_accepted": n,
                     "L4_support": r["support_mean"] if r else None, "L4_direction_agrees": l4dir,
                     "L1_order_agrees": pos_order[s] < pos_order[t]})
    q["paper1_accepted"] = {
        "n_directed_relations": len(rows),
        "L4_support_ge_0.5": sum(1 for x in rows if x["L4_support"] is not None and x["L4_support"] >= 0.5),
        "L4_direction_agree": sum(1 for x in rows if x["L4_direction_agrees"] is True),
        "L4_direction_disagree": sum(1 for x in rows if x["L4_direction_agrees"] is False),
        "L1_order_agree": sum(1 for x in rows if x["L1_order_agrees"]),
        "rows": rows}

    # 2b. human gold labels (pair level: valid if any valid_causal instance)
    gold = [g for g in load_gold() if g["source_node"] in NODES and g["target_node"] in NODES]
    gp = collections.defaultdict(list)
    for g in gold:
        gp[tuple(sorted((g["source_node"], g["target_node"])))].append(g)
    pos, neg, grow = [], [], []
    dir_ok = dir_bad = l1_ok = l1_bad = 0
    for k, gs in gp.items():
        valid = any(g["gold_label"] == "valid_causal" for g in gs)
        r = l4pair.get(k)
        s_ = r["support_mean"] if r else None
        if s_ is not None:
            (pos if valid else neg).append(s_)
        if valid:
            g0 = next(g for g in gs if g["gold_label"] == "valid_causal")
            want = f"{SHORT[g0['source_node']]}->{SHORT[g0['target_node']]}"
            if r and r["direction_majority"] not in ("unclear", "disagree", "both"):
                dir_ok += r["direction_majority"] == want
                dir_bad += r["direction_majority"] != want
            if pos_order[g0["source_node"]] < pos_order[g0["target_node"]]:
                l1_ok += 1
            else:
                l1_bad += 1
        grow.append({"pair": [SHORT[x] for x in k], "gold_valid": valid, "labels": [g["gold_label"] for g in gs],
                     "assertion_types": [g["assertion_type"] for g in gs], "L4_support": s_,
                     "L4_direction": r["direction_majority"] if r else None})
    au = auroc(pos, neg)
    q["paper1_human_gold"] = {"n_pairs": len(gp), "n_valid": len(pos), "n_invalid": len(neg),
                              "L4_support_auroc_valid_vs_invalid": au,
                              "L4_support_auroc_ci95_bootstrap": auroc_ci(pos, neg) if pos and neg else None,
                              "L4_direction_on_valid": {"agree": dir_ok, "disagree": dir_bad},
                              "L1_order_on_valid": {"agree": l1_ok, "disagree": l1_bad}, "rows": grow}

    # 3. data: Granger + pairwise LiNGAM on the panel
    Y = transformed_panel()
    R = ar1_resid(Y)
    drows = []
    for r in edges["pairs"]:
        a_, b_ = r["pair"]
        i, j = NODES.index(a_), NODES.index(b_)
        pab, pba = granger_p(Y, i, j), granger_p(Y, j, i)
        lg = lingam_measure(R[:, i], R[:, j])
        ddir = None
        if pab < 0.10 <= pba:
            ddir = f"{SHORT[a_]}->{SHORT[b_]}"
        elif pba < 0.10 <= pab:
            ddir = f"{SHORT[b_]}->{SHORT[a_]}"
        cdir = f"{SHORT[a_]}->{SHORT[b_]}" if lg > 0 else f"{SHORT[b_]}->{SHORT[a_]}"
        rec = {"pair": [SHORT[a_], SHORT[b_]], "kind": r["kind"], "granger_p_ab": pab, "granger_p_ba": pba,
               "granger_direction_p10": ddir, "lingam_measure_ab": lg, "lingam_direction": cdir,
               "lingam_boot_share_ab": lingam_boot(R, i, j), "involves_simulated": bool({a_, b_} & SIMULATED),
               "L4_direction": r["direction_majority"], "L4_lag": r["lag_majority"]}
        if r["kind"] == "prior":
            rec["prior_direction"] = f"{SHORT[r['prior_source']]}->{SHORT[r['prior_target']]}"
        drows.append(rec)
    def agree_count(key, ref):
        ok = bad = 0
        for d in drows:
            dd, rr = d[key], d.get(ref)
            if dd and rr and rr not in ("unclear", "disagree", "both"):
                ok += dd == rr
                bad += dd != rr
        return {"agree": ok, "disagree": bad}
    all_p = [d["granger_p_ab"] for d in drows] + [d["granger_p_ba"] for d in drows]
    q["data"] = {
        "panel": "14 x 19 (2020Q2..2024Q4); 8 columns first-differenced -> 18 rows; 17 usable for lag-1 tests",
        "n_granger_tests": len(all_p), "share_p_below_0.10": float(np.mean(np.array(all_p) < 0.10)),
        "expected_share_under_null": 0.10,
        "granger_vs_L4_direction": agree_count("granger_direction_p10", "L4_direction"),
        "granger_vs_prior_direction": agree_count("granger_direction_p10", "prior_direction"),
        "lingam_vs_L4_direction": agree_count("lingam_direction", "L4_direction"),
        "lingam_vs_prior_direction": agree_count("lingam_direction", "prior_direction"),
        "lingam_vs_L4_direction_real_only": None,
        "rows": drows}
    real = [d for d in drows if not d["involves_simulated"]]
    ok = sum(1 for d in real if d["L4_direction"] not in ("unclear", "disagree", "both") and d["lingam_direction"] == d["L4_direction"])
    bad = sum(1 for d in real if d["L4_direction"] not in ("unclear", "disagree", "both") and d["lingam_direction"] != d["L4_direction"])
    q["data"]["lingam_vs_L4_direction_real_only"] = {"agree": ok, "disagree": bad}

    # 4. L3 vs observed policy-rate changes
    X = load_panel()
    pr = X[:, NODES.index("macro_policy_rate_pct")]
    rows_c = list(csv.DictReader((ROOT / "results/ext_llm_shocks/shocks.csv").open(encoding="utf-8")))
    rows_u = list(csv.DictReader((ROOT / "results/ext_llm_shocks/shocks_union.csv").open(encoding="utf-8")))
    # policy-rate level is end-of-quarter or average; change in q vs q-1 (q = 2020Q2 uses the 2020Q1 row)
    raw = {r["quarter"]: r for r in csv.DictReader(MATRIX_PATH.open(encoding="utf-8"))}
    prev = [float(raw["2020Q1"]["macro_policy_rate_pct"])] + list(pr[:-1])
    dpr = pr - np.array(prev)
    res = {}
    for name, rows in (("consensus", rows_c), ("union", rows_u)):
        s_rate = np.array([float(r["shock_POLICY_RATE"]) for r in rows])
        s_mon = np.array([float(r["monetary_stance"]) for r in rows])
        nz = dpr != 0
        def hit(s):
            m = nz & (s != 0)
            return {"quarters_rate_changed": int(nz.sum()), "quarters_text_nonzero": int((s != 0).sum()),
                    "both_nonzero": int(m.sum()), "sign_match_when_both": int((np.sign(s[m]) == np.sign(dpr[m])).sum()),
                    "text_nonzero_rate_unchanged": int(((s != 0) & ~nz).sum()),
                    "rate_changed_text_silent": int((nz & (s == 0)).sum()),
                    "pearson": float(np.corrcoef(s, dpr)[0, 1]) if s.std() > 0 else None}
        res[name] = {"shock_POLICY_RATE": hit(s_rate), "monetary_stance": hit(s_mon)}
    res["observed_policy_rate_change_by_quarter"] = {qq: float(d) for qq, d in zip(QUARTERS, dpr) if d != 0}
    q["L3_vs_observed_policy_rate"] = res

    # 5. AUROC translation (binormal, equal variance): AUROC = Phi(d / sqrt(2))
    def auc_from_d(d):
        return float(stats.norm.cdf(d / math.sqrt(2)))
    # Reliability of the 2-variant mean (Spearman-Brown) bounds its validity: corr(score, latent) <= sqrt(rel).
    rel2 = 2 * r_ab / (1 + r_ab) if r_ab > 0 else 0.0
    q["auroc_translation"] = {
        "L4_support_reliability_single": r_ab, "L4_support_reliability_mean_of_2": rel2,
        "upper_bound_corr_with_latent": math.sqrt(rel2),
        "gold_based_auroc_point": au, "gold_based_auroc_ci95": q["paper1_human_gold"]["L4_support_auroc_ci95_bootstrap"],
        "note": "AUROC = Phi(d/sqrt2) (textinfo's binormal model). See docs/ext/llm.md section 6 for the reasoning.",
        "example_d_for_auroc": {a_: float(math.sqrt(2) * stats.norm.ppf(a_)) for a_ in (0.6, 0.7, 0.8, 0.9)},
        "auc_from_d_check": {d: auc_from_d(d) for d in (0.36, 0.74, 1.19, 1.81)}}
    (OUT / "quality.json").write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding="utf-8")
    brief = {k: v for k, v in q.items() if k not in ("paper1_accepted", "paper1_human_gold", "data")}
    brief["paper1_accepted"] = {k: v for k, v in q["paper1_accepted"].items() if k != "rows"}
    brief["paper1_human_gold"] = {k: v for k, v in q["paper1_human_gold"].items() if k != "rows"}
    brief["data"] = {k: v for k, v in q["data"].items() if k != "rows"}
    print(json.dumps(brief, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
