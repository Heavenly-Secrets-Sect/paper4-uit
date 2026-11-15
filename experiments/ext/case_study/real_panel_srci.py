"""Case study: the method on the real 14-variable quarterly panel (feedback point 1). Illustration only.

Data (read-only from ACIIDS): candidate_quarterly_matrix_raw.csv, nodes and the 'defensible' window (2020Q2..2024Q4,
19 quarters) from core14_provenance.json, columns z-scored. Skeleton: the 21-edge prior (induced subgraph of
prior_graph_final_278.json on the 14 nodes), all edges oriented. lag_max = 1, H = 4, n_boot = 199.

DISCLOSURE (must appear in the paper): the macro and stock variables are observed; the seven bank variables are
simulated-calibrated (core14_provenance.json: nature = simulated_calibrated). Pairs between observed variables are
marked REAL; every pair that involves a bank variable is ILLUSTRATIVE. There is no causal ground truth, so no
coverage or accuracy is reported here, only the interval, its width and its stability.

Pairs of interest are fixed here, before running, from paths of the prior skeleton and economic relevance:
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4 import methods as M  # noqa: E402
from paper4.ext_v51 import tolerant_v5_1  # noqa: E402
from paper4.skeleton import Skeleton, _creates_cycle  # noqa: E402

ACIIDS = Path("/Users/kietnt/Desktop/Workspace/ACIIDS")
PROV = ACIIDS / "02_observational_data/processed/core14_provenance.json"
MATRIX = ACIIDS / "02_observational_data/processed/candidate_quarterly_matrix_raw.csv"
PRIOR = ACIIDS / "01_paper1_foundation/prior_graph/prior_graph_final_278.json"

PAIRS = [  # (cause, effect, label)
    ("macro_policy_rate_pct", "stock_return_qoq_pct"),
    ("macro_policy_rate_pct", "stock_avg_daily_trade_value_vnd"),
    ("macro_policy_rate_pct", "macro_gdp_yoy_pct"),
    ("macro_policy_rate_pct", "macro_cpi_avg_pct"),
    ("macro_cpi_avg_pct", "stock_avg_daily_volume_cp"),
    ("macro_policy_rate_pct", "bank_npl_ratio"),
    ("macro_policy_rate_pct", "bank_roe_ratio"),
    ("macro_cpi_avg_pct", "bank_roe_ratio"),
    ("macro_gdp_yoy_pct", "bank_car_ratio"),
    ("bank_ldr_ratio", "bank_npl_ratio"),
]
__doc__ += "\n".join(f"  {a} -> {b}" for a, b in PAIRS)


def load_panel():
    prov = json.loads(PROV.read_text(encoding="utf-8"))
    nodes, quarters = prov["nodes"], prov["windows"]["defensible"]["quarters"]
    rows = {r["quarter"]: r for r in csv.DictReader(MATRIX.open(encoding="utf-8"))}
    X = np.array([[float(rows[q][n]) for n in nodes] for q in quarters])
    X = (X - X.mean(axis=0)) / X.std(axis=0, ddof=1)
    g = json.loads(PRIOR.read_text(encoding="utf-8"))
    edges = [(nodes.index(k.split("|")[0]), nodes.index(k.split("|")[1])) for k in g
             if k.split("|")[0] in nodes and k.split("|")[1] in nodes]
    assert X.shape == (19, 14) and len(edges) == 21 and not _creates_cycle(set(edges), 14)
    nature = {n: prov["by_node"][n]["nature"] for n in nodes}
    return nodes, quarters, X, edges, nature


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--factors", default=None, help="JSON with 'factors' from p4h*_frozen (cell|beta0.1 -> marginal) or the shipped calibration file")
    ap.add_argument("--variant", default="marginal", choices=["marginal", "pac", "shipped"])
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--out", default=str(ROOT / "results/ext_case_study"))
    a = ap.parse_args(argv)
    nodes, quarters, X, edges, nature = load_panel()
    idx = {n: i for i, n in enumerate(nodes)}
    shipped = json.loads((ROOT / "results/ext_region51_lag1/calibration.json").read_text())
    frozen = json.loads(Path(a.factors).read_text())["factors"] if a.factors else None

    def factor(kind):
        if a.variant == "shipped" or frozen is None:
            return shipped[f"tolerant_v5_1|19|{kind}"]
        return frozen[f"tolerant_v5_1|19|{kind}|beta0.1"][a.variant]

    cases = [("none", 0.0, 0), ("missing", 0.2, 4), ("missing", 0.5, 11)]
    res = []
    for kind, rate, k in cases:
        skel = Skeleton(14, oriented=set(edges), damage={"kind": kind, "rate": rate, "k": k})
        fac = factor(M.width_key(skel.damage))
        for s in range(a.seeds):
            r = tolerant_v5_1(X, skel, 1, 4, 199, np.random.default_rng([20261115, s]))
            if r.status != "ok":
                res.append({"stated": f"{kind}-{rate}", "seed": s, "status": r.status})
                continue
            c = M.calibrate_width(r, fac, "tolerant_v5_1")
            for cause, effect in PAIRS:
                i, j = idx[cause], idx[effect]
                res.append({"stated": f"{kind}-{rate}", "seed": s, "status": "ok", "cause": cause, "effect": effect,
                            "real": nature[cause] != "simulated_calibrated" and nature[effect] != "simulated_calibrated",
                            "C": float(c.C[i, j]), "lo": float(c.lo[i, j]), "hi": float(c.hi[i, j]), "factor": fac})
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "real_panel_srci.json").write_text(json.dumps({"variant": a.variant, "factors_file": a.factors, "results": res}, indent=1))
    L = ["| pair | data | stated | C(H=4) median over seeds | interval (median bounds) | excludes 0 in seeds | width |",
         "|---|---|---|---|---|---|---|"]
    for cause, effect in PAIRS:
        for kind, rate, k in cases:
            rs = [r for r in res if r.get("cause") == cause and r.get("effect") == effect and r["stated"] == f"{kind}-{rate}"]
            if not rs:
                continue
            lo, hi, C = (np.median([r[x] for r in rs]) for x in ("lo", "hi", "C"))
            ex = sum((r["lo"] > 0) or (r["hi"] < 0) for r in rs)
            L.append(f"| {cause} -> {effect} | {'REAL' if rs[0]['real'] else 'illustrative'} | {kind}-{rate} | {C:.3f} | "
                     f"[{lo:.3f}, {hi:.3f}] | {ex}/{len(rs)} | {hi - lo:.3f} |")
    (out / "real_panel_srci.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
