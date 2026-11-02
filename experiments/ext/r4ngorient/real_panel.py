"""Descriptive non-Gaussianity check of the real 14 x 19 panel (docs/ext/r4ngorient.md, section 5.4).
No rule, no decision. Reads ACIIDS files read-only.

Data: ACIIDS/02_observational_data/processed/core14_provenance.csv (long format), window "defensible"
of core14_provenance.json (2020Q2..2024Q4). Transform of experiments/ext/llm/signal_quality.py
(first differences for the 8 DIFF columns, levels otherwise, 18 rows). Values are cross-checked
against candidate_quarterly_matrix_raw.csv. Stated skeleton: the 21 prior edges of Paper 1 among the
14 nodes (prior_graph_final_278.json). lag_max 1 -> 17 usable rows. Equation j: estimator.parent_terms
(own lag, lags of adjacent nodes, contemporaneous parents); if underdetermined (terms + 2 > m) the
fallback is own lag + contemporaneous parents. Residuals by OLS with intercept.

Per node: skewness, excess kurtosis, JB, asymptotic chi2(2) p, exact Monte Carlo p (10^4 Gaussian
draws through the same design: residual = M e), Shapiro-Wilk p; Holm over 14 for each p.
Also: Monte Carlo power of JB (MC critical value at 0.05, 10^4 reps, iid samples centred) at m = 17
and 18 for each ng_mix law and t10, and (extra, descriptive) how many of the 21 stated edges would
open the module's gate (ng_evidence) on these residuals.

Writes results/ext_r4ngorient_realpanel/{real_panel.md, real_panel.json}.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import laws  # noqa: E402
from paper4.estimator import parent_terms  # noqa: E402
from paper4.ext_r4ngorient import _ols_resid, ng_evidence  # noqa: E402
from paper4.skeleton import Skeleton, _creates_cycle  # noqa: E402

ACI = Path("/Users/kietnt/Desktop/Workspace/ACIIDS")
PROV_CSV = ACI / "02_observational_data/processed/core14_provenance.csv"
PROV_JSON = ACI / "02_observational_data/processed/core14_provenance.json"
MATRIX = ACI / "02_observational_data/processed/candidate_quarterly_matrix_raw.csv"
PRIOR = ACI / "01_paper1_foundation/prior_graph/prior_graph_final_278.json"
DIFF = {"bank_npl_ratio", "bank_ldr_ratio", "bank_provision_coverage_proxy_pct", "stock_adj_close_last_vnd",
        "stock_avg_daily_volume_cp", "stock_avg_daily_trade_value_vnd", "macro_cpi_avg_pct", "macro_policy_rate_pct"}
N_MC = 10_000
SEED = 20261104


def holm(p):
    p = np.asarray(p, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    run = 0.0
    for r, idx in enumerate(order):
        run = max(run, (len(p) - r) * p[idx])
        adj[idx] = min(1.0, run)
    return adj


def moments(r):
    z = (r - r.mean()) / r.std()
    sk, ek = float(np.mean(z ** 3)), float(np.mean(z ** 4) - 3)
    m = len(r)
    return sk, ek, m * (sk ** 2 / 6 + ek ** 2 / 24)


def jb_batch(R):
    """JB of each row of R (rows = samples)."""
    Z = R - R.mean(axis=1, keepdims=True)
    s = Z.std(axis=1, keepdims=True)
    Z = Z / s
    sk = (Z ** 3).mean(axis=1)
    ek = (Z ** 4).mean(axis=1) - 3
    return R.shape[1] * (sk ** 2 / 6 + ek ** 2 / 24)


def main():
    prov = json.loads(PROV_JSON.read_text(encoding="utf-8"))
    nodes = prov["nodes"]
    quarters = prov["windows"]["defensible"]["quarters"]
    rows = list(csv.DictReader(PROV_CSV.open(encoding="utf-8")))
    val = {(r["quarter"], r["node_id"]): r for r in rows}
    X = np.array([[float(val[(q, n)]["value"]) for n in nodes] for q in quarters])
    nature = {n: sorted({val[(q, n)]["nature"] for q in quarters}) for n in nodes}
    mat = {r["quarter"]: r for r in csv.DictReader(MATRIX.open(encoding="utf-8"))}
    xcheck = max(abs(float(mat[q][n]) - X[i, k]) for i, q in enumerate(quarters) for k, n in enumerate(nodes))
    Y = np.column_stack([np.diff(X[:, k]) if n in DIFF else X[1:, k] for k, n in enumerate(nodes)])
    idx = {n: i for i, n in enumerate(nodes)}
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    edges = [(idx[a], idx[b]) for k in prior for a, b in [k.split("|")] if a in idx and b in idx]
    assert len(edges) == 21 and not _creates_cycle(set(edges), 14)
    skel = Skeleton(14, oriented=set(edges), damage={"kind": "none", "rate": 0.0, "k": 0})
    lag = 1
    T = Y.shape[0]
    m = T - lag
    rows_ = np.arange(lag, T)
    rng = np.random.default_rng(SEED)
    out = {"quarters": quarters, "m": m, "xcheck_max_abs_diff": xcheck, "nodes": []}
    resid = {}
    for j, n in enumerate(nodes):
        tj = parent_terms(skel, j, lag)
        fallback = False
        if len(tj) + 2 > m:
            tj = [(j, 1)] + sorted((u, 0) for u, v in skel.oriented if v == j)
            fallback = True
        r = _ols_resid(Y, tj, j, lag)
        resid[j] = r
        sk, ek, jb = moments(r)
        D = np.column_stack([np.ones(m)] + [Y[rows_ - l_, i] for i, l_ in tj])
        Q, _ = np.linalg.qr(D)
        E = rng.normal(size=(N_MC, m))
        Rm = E - (E @ Q) @ Q.T
        jbs = jb_batch(Rm)
        p_mc = (1 + np.sum(jbs >= jb)) / (1 + N_MC)
        out["nodes"].append({"node": n, "nature": nature[n], "n_terms": len(tj), "fallback": fallback,
                             "skew": sk, "exkurt": ek, "JB": jb, "p_asym": math.exp(-jb / 2), "p_mc": float(p_mc),
                             "p_sw": float(stats.shapiro(r).pvalue),
                             "group": "simulated" if n.startswith("bank_") else "real"})
    for key in ("p_mc", "p_sw"):
        for rec, ph in zip(out["nodes"], holm([r[key] for r in out["nodes"]])):
            rec[key + "_holm14"] = float(ph)
    # power of JB at m = 17, 18
    power = {}
    for mm in (17, 18):
        g = rng.normal(size=(N_MC, mm))
        crit = float(np.quantile(jb_batch(g), 0.95))
        power[mm] = {"crit_0.05": crit}
        for law in ("laplace", "t5", "skewexp", "uniform", "t10"):
            S = laws.sample(rng, law, (N_MC, mm), 1.0)
            power[mm][law] = float(np.mean(jb_batch(S) > crit))
    out["power"] = power
    # extra: module gate on the 21 stated edges
    gates = []
    for u, v in sorted(edges):
        tv = [t for t in (parent_terms(skel, v, lag) if len(parent_terms(skel, v, lag)) + 2 <= m else
                          [(v, 1)] + sorted((a, 0) for a, b in skel.oriented if b == v)) if t != (u, 0)]
        ev = ng_evidence(resid[u], _ols_resid(Y, tv, v, lag))
        gates.append({"u": nodes[u], "v": nodes[v], "gate": ev["gate"], "gate_p": ev["gate_p"]})
    out["gate_21_edges"] = {"n_open": sum(g["gate"] for g in gates), "edges": gates}
    res = ROOT / "results" / "ext_r4ngorient_realpanel"
    res.mkdir(parents=True, exist_ok=True)
    (res / "real_panel.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = ["# Panel thật 14 × 19: non-Gaussianity của phần dư cấu trúc (mô tả, không rule)", "",
         f"Sinh bởi experiments/ext/r4ngorient/real_panel.py. Cửa sổ {quarters[0]}..{quarters[-1]}, transform của "
         f"signal_quality.py (18 dòng), lag_max 1, m = {m} dòng phần dư. Skeleton: 21 cạnh prior Paper 1. "
         f"Kiểm tra chéo với candidate_quarterly_matrix_raw.csv: max |Δ| = {xcheck:.2e}. MC: {N_MC} lần, seed {SEED}.", ""]
    for grp, title in (("real", "Nút real / derived_from_real (macro, stock)"),
                       ("simulated", "Nút banking simulated_calibrated / derived_from_simulated (phản ánh simulator, không phải thực tế)")):
        L += [f"## {title}", "", "| node | nature | số term | fallback | skew | exkurt | JB | p tiệm cận | p MC | p MC Holm (14) | p SW | p SW Holm (14) |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in out["nodes"]:
            if r["group"] != grp:
                continue
            L.append(f"| {r['node']} | {'/'.join(r['nature'])} | {r['n_terms']} | {'có' if r['fallback'] else '-'} | {r['skew']:+.2f} | "
                     f"{r['exkurt']:+.2f} | {r['JB']:.2f} | {r['p_asym']:.3f} | {r['p_mc']:.3f} | {r['p_mc_holm14']:.3f} | "
                     f"{r['p_sw']:.3f} | {r['p_sw_holm14']:.3f} |")
        L.append("")
    L += ["## Power Monte Carlo của JB (mức 0.05, critical value MC), mẫu iid", "",
          "| m | crit | laplace | t5 | skewexp | uniform | t10 |", "|---|---|---|---|---|---|---|"]
    for mm, pw in power.items():
        L.append(f"| {mm} | {pw['crit_0.05']:.2f} | {pw['laplace']:.3f} | {pw['t5']:.3f} | {pw['skewexp']:.3f} | "
                 f"{pw['uniform']:.3f} | {pw['t10']:.3f} |")
    L += ["", f"Thêm (mô tả): gate của module mở ở {out['gate_21_edges']['n_open']}/21 cạnh khai báo trên các phần dư này. "
          "Không đọc chiều từ panel thật: m = 17 quá nhỏ, và 7 nút banking là dữ liệu mô phỏng."]
    (res / "real_panel.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
