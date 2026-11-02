"""Descriptive check on the real 14 x 19 panel (read-only, no ground truth): does tolerant_v5_1 /
tolerant_v5_1_hs run at lag_max 1 and 2 on the 21-edge prior, which equations are reduced, and how wide
are the intervals. Columns are z-scored. Width factors: T19 factors of results/ext_r4hubscreen_lag{1,2}
(the candidate uses f_v51 if nothing is reduced, f_red otherwise, as in run_r4.py).

Inputs (read-only): ACIIDS/02_observational_data/processed/{core14_provenance.json,
candidate_quarterly_matrix_raw.csv}, ACIIDS/01_paper1_foundation/prior_graph/prior_graph_final_278.json
(induced subgraph on the 14 nodes, as experiments/ext/llm/common.py; reimplemented here so that no LLM
client module is imported).

Run: python experiments/ext/r4hubscreen/real_panel.py -> results/ext_r4hubscreen_real/real.{md,json}
"""
import csv
import json
import sys
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4 import methods as M  # noqa: E402
from paper4.estimator import parent_terms  # noqa: E402
from paper4.ext_r4hubscreen import tolerant_v5_1_hs  # noqa: E402
from paper4.ext_v51 import tolerant_v5_1  # noqa: E402
from paper4.skeleton import Skeleton  # noqa: E402

ACIIDS = Path("/Users/kietnt/Desktop/Workspace/ACIIDS")
PROV = ACIIDS / "02_observational_data" / "processed" / "core14_provenance.json"
MATRIX = ACIIDS / "02_observational_data" / "processed" / "candidate_quarterly_matrix_raw.csv"
PRIOR = ACIIDS / "01_paper1_foundation" / "prior_graph" / "prior_graph_final_278.json"
OUT = ROOT / "results" / "ext_r4hubscreen_real"


def load():
    prov = json.loads(PROV.read_text(encoding="utf-8"))
    nodes, quarters = prov["nodes"], prov["windows"]["defensible"]["quarters"]
    rows = {r["quarter"]: r for r in csv.DictReader(MATRIX.open(encoding="utf-8"))}
    X = np.array([[float(rows[q][n]) for n in nodes] for q in quarters])
    X = (X - X.mean(0)) / X.std(0, ddof=1)
    edges = []
    for k in json.loads(PRIOR.read_text(encoding="utf-8")):
        s, t = k.split("|")
        if s in nodes and t in nodes:
            edges.append((nodes.index(s), nodes.index(t)))
    assert len(nodes) == 14 and len(quarters) == 19 and len(edges) == 21
    return X, nodes, edges


def main():
    warnings.filterwarnings("ignore")
    OUT.mkdir(parents=True, exist_ok=True)
    X, nodes, edges = load()
    deg = np.zeros(14, int)
    for u, v in edges:
        deg[u] += 1; deg[v] += 1
    stated = [("none", {"kind": "none", "rate": 0.0, "k": 0}), ("missing", {"kind": "missing", "rate": 0.2, "k": 4}),
              ("extra", {"kind": "extra", "rate": 0.2, "k": 4}), ("reversed", {"kind": "reversed", "rate": 0.2, "k": 2})]
    lines = ["# Real panel 14 x 19 (z-scored), prior 21 edges: descriptive run of v5_1 and the candidate", "",
             f"Node degrees in the prior: {dict(zip([n.split('_', 1)[1][:14] for n in nodes], deg.tolist()))}", "",
             "| lag_max | stated | max |base terms| (m) | v5_1 status | candidate status | reduced (data eq / draws) | "
             "reduced nodes | median width v5_1 | median width cand | share excl. 0 v5_1 | share excl. 0 cand |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    J = []
    for lag in (1, 2):
        cal = json.loads((ROOT / "results" / f"ext_r4hubscreen_lag{lag}" / "calibration.json").read_text())
        for c_idx, (name, dmg) in enumerate(stated):
            skel = Skeleton(14, oriented=set(edges), damage=dmg)
            wk = M.width_key(dmg)
            fv, fr = cal["v51"].get(f"19|{wk}"), cal["red"].get(f"19|{wk}")
            a = tolerant_v5_1(X, skel, lag, 4, 199, np.random.default_rng([20261102, 99, lag, c_idx]))
            b = tolerant_v5_1_hs(X, skel, lag, 4, 199, np.random.default_rng([20261102, 99, lag, c_idx]))
            red = b.info.get("hs_reduced", 0)
            a = M.calibrate_width(a, fv, "v51")
            b = M.calibrate_width(b, fr if red or fv is None else fv, "hs")
            off = ~np.eye(14, dtype=bool)

            def desc(r):
                if r.status != "ok":
                    return None, None
                w = (r.hi - r.lo)[off]
                ex = ((r.lo > 0) | (r.hi < 0))[off]
                return float(np.median(w)), float(ex.mean())

            wa, ea = desc(a)
            wb, eb = desc(b)
            mx = max(len(parent_terms(skel, j, lag)) for j in range(14))
            rec = {"lag": lag, "stated": name, "max_terms": mx, "m": 19 - lag, "v51": a.status, "cand": b.status,
                   "reduced": red, "eq_data": b.info.get("hs_eq_data"), "draws_red": b.info.get("hs_draws_reduced"),
                   "nodes": [nodes[i] for i in b.info.get("hs_nodes_data", [])], "width_v51": wa, "width_cand": wb,
                   "excl0_v51": ea, "excl0_cand": eb, "factor_v51": fv, "factor_red": fr}
            J.append(rec)
            f = lambda x: "–" if x is None else f"{x:.2f}"  # noqa: E731
            lines.append(f"| {lag} | {name} | {mx} ({19 - lag}) | {a.status} | {b.status} | {red} ({rec['eq_data']} / "
                         f"{rec['draws_red']}) | {', '.join(rec['nodes']) or '–'} | {f(wa)} | {f(wb)} | {f(ea)} | {f(eb)} |")
    lines += ["", "Descriptive only: no ground truth; the banking nodes are simulated_calibrated (core14_provenance.json)."]
    (OUT / "real.json").write_text(json.dumps(J, indent=1))
    (OUT / "real.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
