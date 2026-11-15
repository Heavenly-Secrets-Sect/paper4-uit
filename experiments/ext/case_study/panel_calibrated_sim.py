"""Panel-calibrated simulation (feedback point 1, second half): the regime of the real panel, with a known truth.

A dynamic SEM is fitted to the real 14 x 19 panel under the 21-edge prior skeleton (own lag, lag of every connected
pair, contemporaneous parents; OLS per equation; lagged part shrunk until the companion radius is below 0.9).
That fitted model is the ground truth. Series of length 19 are simulated from it, the stated skeleton is damaged
(none, missing 0.2, missing 0.5), the method is run, and the interval is compared with the model's own C(H).

DISCLOSURE: the seven bank variables of the panel are simulated-calibrated, so this truth model is a model fitted to
a panel that is partly simulated. It shows how the method behaves in the n = 14, T = 19 regime of the case study with
the covariance structure of that panel. All draws come from ONE fixed truth model: this is not the topology-level
guarantee (that one is about new topologies) and it does not say anything about real causal effects.
Output: results/ext_case_study/panel_calibrated_sim.{json,md}
"""
import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))
from real_panel_srci import load_panel  # noqa: E402

from paper4 import methods as M  # noqa: E402
from paper4.effects import companion_radius  # noqa: E402
from paper4.estimator import fit_equations, parent_terms  # noqa: E402
from paper4.ext_v51 import tolerant_v5_1  # noqa: E402
from paper4.generator import DynamicSEM, GeneratorConfig  # noqa: E402
from paper4.metrics import evaluate  # noqa: E402
from paper4.skeleton import Skeleton, damage, true_skeleton  # noqa: E402

CASES = [("none", 0.0, 0), ("missing", 0.2, 4), ("missing", 0.5, 11)]


def build_truth():
    nodes, quarters, X, edges, nature = load_panel()
    skel = Skeleton(14, oriented=set(edges), damage={"kind": "none", "rate": 0.0, "k": 0})
    terms = [parent_terms(skel, j, 1) for j in range(14)]
    fit = fit_equations(X, terms, 1)
    assert fit.status == "ok"
    B = fit.B.copy()
    shrink = 1.0
    while companion_radius(B) >= 0.9:
        B[1:] *= 0.95
        shrink *= 0.95
    nv = (fit.residuals ** 2).sum(axis=0) / np.maximum(fit.dof, 1)
    sem = DynamicSEM("panel_fit", tuple(nodes), B, nv, {e: 0 for e in edges}, GeneratorConfig(lag_max=1), shrink,
                     {"companion_radius": float(companion_radius(B))})
    return sem


def one_draw(args):
    s, factors, variant = args
    sem = build_truth()
    rng = np.random.default_rng([20261115, 9, s])
    data = sem.simulate(19, rng)
    truth = true_skeleton(sem)
    coef = {e: float(sem.B[lag, e[1], e[0]]) for e, lag in sem.edge_lag.items()}
    rows = []
    for k_idx, (kind, rate, k) in enumerate(CASES):
        skel = truth.copy() if kind == "none" else damage(truth, kind, rate, np.random.default_rng([20261115, 10, s, k_idx]), sem.edge_lag, coef)
        key = M.width_key(skel.damage)
        for name in ("plugin", "srci"):
            r_rng = np.random.default_rng([20261115, 11, s, k_idx])
            if name == "plugin":
                res = M.plugin(data, skel, 1, 4, 199, r_rng)
            else:
                res = tolerant_v5_1(data, skel, 1, 4, 199, r_rng)
                res = M.calibrate_width(res, factors[key], "srci")
            row = evaluate(sem, res, 4, tau_effect=0.1)
            row.update({"draw": s, "case": f"{kind}-{rate}", "method": name, "factor": factors[key] if name == "srci" else None})
            rows.append(row)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=400)
    ap.add_argument("--factors", default=None, help="frozen factor file (T = 19 cells); default: shipped calibration")
    ap.add_argument("--variant", default="marginal", choices=["marginal", "pac", "shipped"])
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--out", default=str(ROOT / "results/ext_case_study"))
    a = ap.parse_args(argv)
    shipped = json.loads((ROOT / "results/ext_region51_lag1/calibration.json").read_text())
    if a.variant == "shipped" or not a.factors:
        factors = {k: shipped[f"tolerant_v5_1|19|{k}"] for k in ("none", "missing", "reversed")}
    else:
        fr = json.loads(Path(a.factors).read_text())["factors"]
        factors = {k: fr[f"tolerant_v5_1|19|{k}|beta0.1"][a.variant] for k in ("none", "missing", "reversed")}
    sem = build_truth()
    print("truth model: companion radius %.3f, lagged shrink %.3f" % (sem.meta["companion_radius"], sem.shrink), flush=True)
    jobs = [(s, factors, a.variant) for s in range(a.draws)]
    rows = []
    with ProcessPoolExecutor(a.workers) as pool:
        for out in pool.map(one_draw, jobs):
            rows += out
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "panel_calibrated_sim.json").write_text(json.dumps({"variant": a.variant, "factors": factors, "rows": rows}))
    L = ["| stated | method | fits ok | coverage of non-null pairs | draws with <=10% pairs missed | median width | mean width | median IS | mean IS |", "|---|---|---|---|---|---|---|---|---|---|"]
    for case in [f"{k}-{r}" for k, r, _ in CASES]:
        for name in ("plugin", "srci"):
            rs = [r for r in rows if r["case"] == case and r["method"] == name]
            ok = [r for r in rs if r["status"] == "ok"]
            if not ok:
                L.append(f"| {case} | {name} | 0/{len(rs)} | - | - | - | - | - | - |")
                continue
            cov = sum(r["n_covered_nonnull"] for r in ok) / sum(r["n_nonnull"] for r in ok)
            hit = np.mean([(1 - r["n_covered_nonnull"] / r["n_nonnull"]) <= 0.10 for r in ok])
            L.append(f"| {case} | {name} | {len(ok)}/{len(rs)} | {cov:.3f} | {hit:.3f} | {np.median([r['width_kept'] for r in ok]):.2f} | "
                     f"{np.mean([r['width_kept'] for r in ok]):.2f} | {np.median([r['iscore_nonnull_mean'] for r in ok]):.2f} | "
                     f"{np.mean([r['iscore_nonnull_mean'] for r in ok]):.2f} |")
    (out_dir / "panel_calibrated_sim.md").write_text(f"Truth model: companion radius {sem.meta['companion_radius']:.3f}, lagged shrink {sem.shrink:.3f}; variant {a.variant}; {a.draws} draws.\n\n" + "\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
