"""Verifier: (a) with every gate forced closed, tolerant_ngA/ngB must equal tolerant_v5_1 bit for bit on the same
stream, in missing and reversed cells (non-trivial: steps 3/4 active). (b) unpatched, NG-A differs (sanity).
D-07H development, Gaussian data, seed_base 20261102 + 900000 (verifier-only units)."""
import sys, json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
import paper4.ext_r4ngorient as NG
from paper4.ext_v51 import tolerant_v5_1
from paper4.generator import build_dynamic_sem
from paper4.topology import load_bank
from run_experiment import generator_config, unit_skeletons, public

cfg = json.loads((ROOT / "experiments/configs/ext_r4ngorient_v2_gauss.json").read_text())
gen = generator_config(cfg)
topos = load_bank("D-07H", "development")[:4]
orig = NG.ng_evidence
closed = lambda x, y, **k: {"p": 0.5, "gate": False, "gate_p": 1.0, "R": 0.0, "se": float("nan"), "form": "none"}
rows = []
for t_idx, topo in enumerate(topos):
    unit = 20261102 + 900000 + 1000 * t_idx
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skels = unit_skeletons(sem, unit, cfg)
    for T in (40, 80):
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        for (kind, rate), full in skels.items():
            if kind not in ("missing", "reversed"):
                continue
            skel = public(full)
            ref = tolerant_v5_1(data, skel, 2, 4, 49, np.random.default_rng(5))
            NG.ng_evidence = closed
            a = NG.tolerant_ngA(data, skel, 2, 4, 49, np.random.default_rng(5))
            NG.ng_evidence = orig
            a2 = NG.tolerant_ngA(data, skel, 2, 4, 49, np.random.default_rng(5))
            same = ref.status == a.status == "ok" and np.array_equal(ref.lo, a.lo) and np.array_equal(ref.hi, a.hi) and np.array_equal(ref.C, a.C)
            diff2 = a2.status == "ok" and not (np.array_equal(ref.lo, a2.lo) and np.array_equal(ref.hi, a2.hi))
            rows.append({"topo": topo.id, "T": T, "cell": f"{kind}|{rate}", "targeted": a.info.get("v51_targeted"),
                         "n_repair": a.info.get("n_repair"), "pool": a.info.get("n_reversal_pool"),
                         "closed_identical": bool(same), "unpatched_differs": bool(diff2)})
            print(rows[-1])
summ = {"n": len(rows), "closed_identical": sum(r["closed_identical"] for r in rows),
        "unpatched_differs": sum(r["unpatched_differs"] for r in rows),
        "targeted_cases": sum(1 for r in rows if r["targeted"])}
print(summ)
(ROOT / "results/ext_verify4_ngorient/t3_crn_identity.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1))
