"""Design probe (D-07H development only): the gate's evidence counts (n_bh, k_storey) against the true
number of missing pairs, per T and cell, on the runner's calibration units. No bootstrap.
Run: python experiments/ext/auto5/probe_budget.py  -> results/ext_auto5_probe/budget.md"""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
from run_experiment import generator_config, public, unit_skeletons  # noqa
from paper4.generator import build_dynamic_sem  # noqa
from paper4.topology import load_bank  # noqa
from paper4.ext_gate import diagnose_gate  # noqa
from paper4.ext_narrow import screen_pairs  # noqa
from paper4.skeleton import Skeleton  # noqa
cfg = json.loads((ROOT / "experiments/configs/ext_auto5_eval.json").read_text())
cal = cfg["calibration"]; assert cal["bank"] == "D-07H" and cal["split"] == "development"
ccfg = dict(cfg, damage={"kinds": cal["kinds"], "rates": cal["rates"]})
gen = generator_config(cfg)
acc = defaultdict(list)
for t_idx, topo in enumerate(load_bank(cal["bank"], cal["split"])):
    unit = cfg["seed_base"] + 500_000 + 1000 * t_idx
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skels = unit_skeletons(sem, unit, ccfg)
    for T in cfg["T"]:
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        for (kind, rate), full in skels.items():
            true_miss = len(full.log) if kind == "missing" else 0   # truth used for this probe table only
            s = public(full); base = Skeleton(s.n, set(s.oriented), set(s.undetermined))
            d = diagnose_gate(data, base, gen.lag_max)
            sp = screen_pairs(data, base, gen.lag_max)
            acc[(T, kind, rate)].append((d["n_bh"], d["k_storey"], d["m_out"], sum(p < 0.10 for p, _, _ in sp), true_miss,
                                         d["p_gate"] is not None and d["p_gate"] <= 0.10))
L = ["| T | cell | gate open | mean n_bh | mean k_storey | mean m_out | mean #screen p<0.10 | true missing |", "|---|---|---|---|---|---|---|---|"]
for (T, k, r), v in sorted(acc.items()):
    a = np.array([[x if x is not None else np.nan for x in row] for row in v], float)
    L.append(f"| {T} | {k} {r} | {np.mean(a[:,5]):.2f} | {np.mean(a[:,0]):.1f} | {np.mean(a[:,1]):.1f} | {np.mean(a[:,2]):.1f} | {np.mean(a[:,3]):.1f} | {np.nanmean(a[:,4]) if not np.all(np.isnan(a[:,4])) else float('nan'):.1f} |")
out = ROOT / "results/ext_auto5_probe"; out.mkdir(parents=True, exist_ok=True)
(out / "budget.md").write_text("\n".join(L) + "\n"); print("\n".join(L))
