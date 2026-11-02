"""Verifier: re-run the bias=0 identity on other D-07H development units / rng seeds (not the candidate's unit 0 / seed 5)."""
import json, sys
import numpy as np
ROOT = "/Users/kietnt/Desktop/Workspace/Paper4_UIT"
sys.path.insert(0, ROOT + "/src"); sys.path.insert(0, ROOT + "/experiments")
import run_experiment as R
from paper4 import ext_r4kilianbab as K
from paper4.ext_v51 import tolerant_v5_1
from paper4.generator import build_dynamic_sem
from paper4.topology import load_bank
CFG = json.loads(open(ROOT + "/experiments/configs/ext_v51_eval.json").read())
K.stage1_bias.__defaults__ = (0,)
res = {}
for t_idx, seed in ((3, 91), (7, 17)):
    topo = load_bank("D-07H", "development")[t_idx]
    unit = 888001 + 1000 * t_idx
    sem = build_dynamic_sem(topo, R.generator_config(CFG), np.random.default_rng([unit, 0]))
    skels = R.unit_skeletons(sem, unit, CFG)
    for T in (40, 80):
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        for (kind, rate), full in skels.items():
            skel = R.public(full); K._CACHE.clear()
            a = tolerant_v5_1(data, skel, 2, 4, 49, np.random.default_rng(seed))
            b = K.r4kilianbab_bab(data, skel, 2, 4, 49, np.random.default_rng(seed))
            same = a.status == b.status and (a.status != "ok" or (np.array_equal(a.lo, b.lo) and np.array_equal(a.hi, b.hi)))
            res[f"u{t_idx}|T{T}|{kind}|{rate}"] = {"same": bool(same), "status": [a.status, b.status],
                                                  "targeted": b.info.get("v51_targeted") if b.status == "ok" else None}
res["all_same"] = all(v["same"] for v in res.values() if isinstance(v, dict))
json.dump(res, open(ROOT + "/results/ext_verify4_kilianbab/identity2.json", "w"), indent=1)
print(json.dumps(res, indent=0))
