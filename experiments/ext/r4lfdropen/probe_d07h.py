"""Design probe on D-07H development only (calibration-phase seeds): data-fit open counts of v5_1's rule
and of the lfdr rule, recall of the truly missing pairs, EM parameters, and the wall time of one full
call of each method (n_boot 199). Writes results/ext_r4lfdropen_probe/probe.json.
Run: /Users/kietnt/miniconda3/bin/python experiments/ext/r4lfdropen/probe_d07h.py [n_topologies]
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

import run_experiment as RE  # noqa: E402
from paper4 import ext_narrow, ext_r4lfdropen as L, ext_v51  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

n_topo = int(sys.argv[1]) if len(sys.argv) > 1 else 4
cfg = json.loads((ROOT / "experiments/configs/ext_v51_eval.json").read_text())
gen = RE.generator_config(cfg)
topos = load_bank("D-07H", "development")[:n_topo]
rows = []
for t_idx, topo in enumerate(topos):
    unit = cfg["seed_base"] + 500_000 + 1000 * t_idx
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skels = RE.unit_skeletons(sem, unit, cfg)
    for T in (40, 80, 150):
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        for c_idx, cell in enumerate(skels):
            if cell[0] != "missing":
                continue
            full = skels[cell]
            sk = RE.public(full)
            k = sk.damage["k"]
            truth = {L._pkey(*e["pair"]) for e in full.log}
            v51 = {L._pkey(u, v) for u, v in ext_narrow.select_open(data, sk, 2, k, 3.0, 0.10)}
            op, tests, P, em = L.select_open_lfdr(data, sk, 2, k, None)
            mine = {L._pkey(u, v) for u, v in op}
            Pm = {L._pkey(u, v): float(P[i]) for i, (_, u, v) in enumerate(tests)}
            row = {"topology": topo.id, "T": T, "kind": cell[0], "rate": cell[1], "k": k, "m": len(tests),
                   "n_open_v51": len(v51), "n_open_lfdr": len(mine), "recall_v51": len(truth & v51) / len(truth),
                   "recall_lfdr": len(truth & mine) / len(truth), "mu": em["mu"], "s": em["s"], "pi0": em["pi0"],
                   "P_true_mean": float(np.mean([Pm.get(t, float("nan")) for t in truth])),
                   "sumP_nonforced": float(P[k:].sum())}
            if t_idx < 2:
                t0 = time.perf_counter()
                a = ext_v51.tolerant_v5_1(data, sk, 2, 4, 199, np.random.default_rng([unit, 3, T, c_idx, RE.ext_seed("tolerant_v5_1")]))
                t1 = time.perf_counter()
                b = L.tolerant_v5_1_lfdr(data, sk, 2, 4, 199, np.random.default_rng([unit, 3, T, c_idx, RE.ext_seed(L.NAME)]))
                t2 = time.perf_counter()
                row.update({"sec_v51": t1 - t0, "sec_lfdr": t2 - t1, "boot_open_v51": a.info.get("n_open_boot_mean"),
                            "boot_open_lfdr": b.info.get("n_open_boot_mean"),
                            "halfwidth_ratio_med": float(np.median((b.hi - b.lo)[~np.eye(14, dtype=bool)] /
                                                                   np.maximum((a.hi - a.lo)[~np.eye(14, dtype=bool)], 1e-12)))})
            rows.append(row)
            print({k_: (round(v, 3) if isinstance(v, float) else v) for k_, v in row.items()})
out = ROOT / "results/ext_r4lfdropen_probe"
out.mkdir(parents=True, exist_ok=True)
summ = {}
for T in (40, 80, 150):
    for rate in (0.2, 0.5):
        g = [r for r in rows if r["T"] == T and r["rate"] == rate]
        summ[f"{T}|{rate}"] = {key: float(np.mean([r[key] for r in g])) for key in
                               ("n_open_v51", "n_open_lfdr", "recall_v51", "recall_lfdr", "mu", "s", "P_true_mean")}
        for key in ("sec_v51", "sec_lfdr", "boot_open_v51", "boot_open_lfdr", "halfwidth_ratio_med"):
            v = [r[key] for r in g if r.get(key) is not None]
            summ[f"{T}|{rate}"][key] = float(np.mean(v)) if v else None
(out / "probe.json").write_text(json.dumps({"rows": rows, "summary": summ}, indent=2))
for kk, v in summ.items():
    print(kk, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items()})
