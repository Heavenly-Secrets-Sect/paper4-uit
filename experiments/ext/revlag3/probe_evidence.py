"""R3-4 design probe, D-07H development ONLY: is the likelihood evidence dl_e of
src/paper4/ext_revlag3.py informative about which pool pairs are the reversed ones?
Truth (damage log) is used here only to score the probe, never by the method.

Run: python experiments/ext/revlag3/probe_evidence.py [--topologies 20]
Writes results/ext_revlag3_probe/evidence.{md,json}.
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
from paper4 import methods as M
from paper4.ext_revlag3 import orientation_evidence, log_odds
from paper4.estimator import fit_equations, parent_terms
from paper4.generator import build_dynamic_sem
from paper4.topology import load_bank
from run_experiment import generator_config, unit_skeletons, public
sys.path.insert(0, str(ROOT / "experiments/ext/revlag"))
from flaglib import auc

ap = argparse.ArgumentParser(); ap.add_argument("--topologies", type=int, default=20); a = ap.parse_args()
cfg = json.loads((ROOT / "experiments/configs/ext_revlag_probe.json").read_text())
cfg["damage"] = {"kinds": ["reversed"], "rates": [0.2, 0.5]}
gen = generator_config(cfg)
topos = load_bank("D-07H", "development")[: a.topologies]
rec = []
for t_idx, topo in enumerate(topos):
    unit = cfg["seed_base"] + 1000 * t_idx
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skels = unit_skeletons(sem, unit, cfg)
    for T in (40, 80, 150):
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        for (kind, rate), full in skels.items():
            if kind != "reversed":
                continue
            skel = public(full)
            k = M.stated_counts(skel.damage)["reversed"]
            if k == 0:
                continue
            rev = {(v, u) for e in full.log for u, v in [e["pair"]]}   # edges as they appear in the damaged skeleton
            fit0 = fit_equations(data, [parent_terms(skel, j, 2) for j in range(skel.n)], 2)
            pool = M.contemporaneous_pool(data, fit0, k)
            dl = orientation_evidence(data, skel, pool, 2, False)
            lo = log_odds(dl, k, len(pool))
            p = np.exp(lo) / (1 + np.exp(lo))
            for e, d, pp in zip(pool, dl, p):
                rec.append({"topo": t_idx, "T": T, "rate": rate, "k": k, "n_pool": len(pool),
                            "is_rev": e in rev, "dl": float(d), "p": float(pp), "prior": k / len(pool)})
            rec.append({"topo": t_idx, "T": T, "rate": rate, "k": k, "summary": True,
                        "rev_in_pool": sum(e in rev for e in pool), "n_rev": len(rev)})
out = ROOT / "results/ext_revlag3_probe"; out.mkdir(parents=True, exist_ok=True)
(out / "evidence.json").write_text(json.dumps(rec))
L = ["# R3-4 probe (D-07H development): orientation evidence dl on pool pairs", "",
     "| T | rate | n pool pairs | share reversed | rev pairs in pool / all rev | AUROC(dl) rev vs not | mean dl rev | mean dl not | mean p rev | mean p not | mean prior |",
     "|---|---|---|---|---|---|---|---|---|---|---|"]
for T in (40, 80, 150):
    for rate in (0.2, 0.5):
        r = [x for x in rec if x["T"] == T and x["rate"] == rate and not x.get("summary")]
        s = [x for x in rec if x["T"] == T and x["rate"] == rate and x.get("summary")]
        if not r:
            continue
        y = np.array([x["is_rev"] for x in r]); d = np.array([x["dl"] for x in r]); p = np.array([x["p"] for x in r])
        L.append(f"| {T} | {rate} | {len(r)} | {y.mean():.3f} | {sum(x['rev_in_pool'] for x in s)}/{sum(x['n_rev'] for x in s)} | "
                 f"{auc(d, y):.3f} | {d[y].mean():+.2f} | {d[~y].mean():+.2f} | {p[y].mean():.3f} | {p[~y].mean():.3f} | "
                 f"{np.mean([x['prior'] for x in r]):.3f} |")
(out / "evidence.md").write_text("\n".join(L) + "\n"); print("\n".join(L))
