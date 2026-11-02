"""Small known-truth check of pselect_union_v3 (verify3_baselines3). Synthetic 5-node topology built here
(not from any bank). Checks: coverage of C(H) on non-null pairs with the true skeleton and with one true edge
removed (stated missing k=1), re-selection of the removed pair, budget accounting, blindness to stated damage,
and that _cal has same midpoint and half the width."""
import json, sys
import numpy as np
ROOT = "/Users/kietnt/Desktop/Workspace/Paper4_UIT/"
sys.path.insert(0, ROOT + "src"); sys.path.insert(0, ROOT + "experiments")
import run_experiment as R
from paper4.topology import Topology
from paper4.generator import build_dynamic_sem
from paper4.skeleton import true_skeleton
from paper4.metrics import truth_effects
from paper4 import ext_baselines3 as E
cfg = json.load(open(ROOT + "experiments/configs/ext_baselines3_eval.json"))
gen = R.generator_config(cfg)
topo = Topology("verify", "kt", "dev", "er", ("a", "b", "c", "d", "e"),
                (("a", "b"), ("b", "c"), ("a", "d"), ("d", "e")), "x")
H, p = 4, gen.lag_max
out = {"runs": []}
cov = {"true": [0, 0], "missing1": [0, 0], "missing1_pair": [0, 0]}
resel = 0
for rep in range(int(sys.argv[1]) if len(sys.argv) > 1 else 12):
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([777, rep]))
    data = sem.simulate(300, np.random.default_rng([777, rep, 2]))
    _, C, _, _ = truth_effects(sem, H)
    nonnull = ~np.eye(sem.n, dtype=bool) & (np.abs(C) > 0.1)
    ts = R.public(true_skeleton(sem))
    r = E.pselect_union_v3(data, ts, p, H, 199, None)
    inside = (r.lo <= C) & (C <= r.hi)
    cov["true"][0] += int(inside[nonnull].sum()); cov["true"][1] += int(nonnull.sum())
    # remove the a->b edge (parent a=0, child b=1 by node order) from the public skeleton; state missing k=1
    d = ts.copy()
    e = next(x for x in sorted(d.oriented) if set(x) == {0, 1})
    d.oriented.discard(e); d.damage = {"kind": "missing", "rate": 0.2, "k": 1}
    r2 = E.pselect_union_v3(data, d, p, H, 199, None)
    d0 = d.copy(); d0.damage = {}
    r3 = E.pselect_union_v3(data, d0, p, H, 199, None)
    blind = bool(np.array_equal(r2.lo, r3.lo) and np.array_equal(r2.hi, r3.hi))
    rc = E.pselect_union_v3_cal(data, d, p, H, 199, None)
    midok = bool(np.allclose((rc.lo + rc.hi) / 2, (r2.lo + r2.hi) / 2) and np.allclose(rc.hi - rc.lo, 0.5 * (r2.hi - r2.lo)))
    inside2 = (r2.lo <= C) & (C <= r2.hi)
    cov["missing1"][0] += int(inside2[nonnull].sum()); cov["missing1"][1] += int(nonnull.sum())
    # C[cause, effect]? check both orientations of the a-b pair that are non-null
    for (i, j) in [(0, 1), (1, 0)]:
        if nonnull[i, j]:
            cov["missing1_pair"][0] += int(inside2[i, j]); cov["missing1_pair"][1] += 1
    out["runs"].append({"rep": rep, "status": [r.status, r2.status], "info_true": r.info, "info_missing": r2.info,
                        "blind": blind, "cal_ok": midok, "draws_ok": r2.info["n_draws"] <= 199 * r2.info["n_members_ok"]
                        and r2.info["n_draws"] >= 0.25 * 199 * r2.info["n_members_ok"]})
out["coverage"] = {k: (v[0] / v[1] if v[1] else None, v) for k, v in cov.items()}
out["all_blind"] = all(x["blind"] for x in out["runs"]); out["all_cal_ok"] = all(x["cal_ok"] for x in out["runs"])
out["all_draws_ok"] = all(x["draws_ok"] for x in out["runs"])
out["mean_selected_true"] = float(np.mean([x["info_true"]["n_selected"] for x in out["runs"]]))
json.dump(out, open(ROOT + "results/ext_verify3_baselines3/known_truth.json", "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in out.items() if k != "runs"}, indent=1, default=str))
print(out["runs"][0])
