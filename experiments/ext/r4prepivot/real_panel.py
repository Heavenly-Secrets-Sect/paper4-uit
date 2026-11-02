"""Descriptive check on the real 14 x 19 panel (read-only from ACIIDS). No truth, no coverage.

Data: ACIIDS/02_observational_data/processed/candidate_quarterly_matrix_raw.csv, nodes and the
"defensible" window (2020Q2..2024Q4) from core14_provenance.json, columns z-scored. Skeleton: the
21-edge prior (induced subgraph of prior_graph_final_278.json on the 14 nodes), all edges oriented.
lag_max = 1, H = 4, n_boot = 199. Stated damage: none, missing 0.2 (k 4), missing 0.5 (k 11),
reversed 0.2 (k 4), counts as floor(rate * 21 + 0.5) (skeleton.py accounting).
Reports f_pp, f_orig, v5.1's effective bank factor for (lag_max 1, T 19) from
results/ext_region51_lag1/calibration.json, and the median width of both intervals over off-diagonal
pairs. Writes results/ext_r4prepivot_realpanel/real_panel.json and .md.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT  # noqa: E402
from paper4 import methods as M  # noqa: E402
from paper4.ext_r4prepivot import prepivot_core, result_from_core  # noqa: E402
from paper4.skeleton import Skeleton, _creates_cycle  # noqa: E402

ACIIDS = Path("/Users/kietnt/Desktop/Workspace/ACIIDS")
PROV = ACIIDS / "02_observational_data/processed/core14_provenance.json"
MATRIX = ACIIDS / "02_observational_data/processed/candidate_quarterly_matrix_raw.csv"
PRIOR = ACIIDS / "01_paper1_foundation/prior_graph/prior_graph_final_278.json"


def main():
    prov = json.loads(PROV.read_text(encoding="utf-8"))
    nodes, quarters = prov["nodes"], prov["windows"]["defensible"]["quarters"]
    rows = {r["quarter"]: r for r in csv.DictReader(MATRIX.open(encoding="utf-8"))}
    X = np.array([[float(rows[q][n]) for n in nodes] for q in quarters])
    X = (X - X.mean(axis=0)) / X.std(axis=0, ddof=1)
    g = json.loads(PRIOR.read_text(encoding="utf-8"))
    edges = [(nodes.index(k.split("|")[0]), nodes.index(k.split("|")[1])) for k in g
             if k.split("|")[0] in nodes and k.split("|")[1] in nodes]
    assert len(edges) == 21 and not _creates_cycle(set(edges), 14)
    cal = json.loads((ROOT / "results/ext_region51_lag1/calibration.json").read_text(encoding="utf-8"))
    out = {"T": X.shape[0], "n": X.shape[1], "lag_max": 1, "H": 4, "n_boot": 199, "cases": []}
    off = ~np.eye(14, dtype=bool)
    for i, (kind, rate, k) in enumerate((("none", 0.0, 0), ("missing", 0.2, 4), ("missing", 0.5, 11),
                                         ("reversed", 0.2, 4))):
        skel = Skeleton(14, oriented=set(edges), damage={"kind": kind, "rate": rate, "k": k})
        core = prepivot_core(X, skel, 1, 4, 199, np.random.default_rng([20261105, i]))
        rec = {"kind": kind, "rate": rate, "k": k, "v51_status": core["v51"].status, "pp_status": core.get("status")}
        fac = cal.get(f"tolerant_v5_1|19|{M.width_key(skel.damage)}")
        rec["f_v51_eff"] = fac * 0.5 if fac else None
        if core["v51"].status == "ok":
            v = M.calibrate_width(core["v51"], fac, "tolerant_v5_1")
            rec["width_v51_median"] = float(np.median((v.hi - v.lo)[off]))
            rec["n_inner_ok"] = core.get("n_inner_ok")
            for which in ("pp", "orig"):
                r = result_from_core(core, f"pp_{which}", which)
                rec[f"f_{which}"] = r.info.get("f_d") if r.status == "ok" else None
                rec[f"width_{which}_median"] = float(np.median((r.hi - r.lo)[off])) if r.status == "ok" else None
            rec["seconds"] = (core["seconds_outer"] or 0) + (core["seconds_inner"] or 0)
        out["cases"].append(rec)
    dst = ROOT / "results/ext_r4prepivot_realpanel"
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "real_panel.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = ["# r4prepivot: real 14 x 19 panel (descriptive)", "",
         "| stated | k | v5.1 status | pp status | inner ok | f_pp | f_orig | f_v51 eff (lag1, T19) | median width v51 | pp | orig | s |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    f = lambda x, d=3: "–" if x is None else f"{x:.{d}f}"  # noqa: E731
    for c in out["cases"]:
        L.append(f"| {c['kind']}-{c['rate']} | {c['k']} | {c['v51_status']} | {c['pp_status']} | {c.get('n_inner_ok')} | "
                 f"{f(c.get('f_pp'))} | {f(c.get('f_orig'))} | {f(c.get('f_v51_eff'))} | {f(c.get('width_v51_median'), 2)} | "
                 f"{f(c.get('width_pp_median'), 2)} | {f(c.get('width_orig_median'), 2)} | {f(c.get('seconds'), 1)} |")
    (dst / "real_panel.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
