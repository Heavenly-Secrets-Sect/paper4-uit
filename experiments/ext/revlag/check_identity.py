"""Validity check of ext_revlag.tolerant_v4L (D-07H development only, never D-07).

With the same random stream as the runner gives tolerant_v3 (rng(6)), tolerant_v4L must return
the same C, lo, hi as tolerant_v4 (bit-identical), and the same theta when no structure is drawn.
When structure is drawn, cumulative(theta_v4L) must equal C.

Run: python experiments/ext/revlag/check_identity.py
Writes results/ext_revlag_identity/check.txt
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
from paper4 import methods as M  # noqa: E402
from paper4.effects import cumulative  # noqa: E402
from paper4.ext_revlag import frozen_factor, tolerant_v4L_draws  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.topology import load_bank  # noqa: E402
from run_experiment import generator_config, public, unit_skeletons  # noqa: E402

cfg = json.loads((ROOT / "experiments/configs/ext_revlag_probe.json").read_text())
gen = generator_config(cfg)
lines, bad, n = [], 0, 0
for t_idx, topo in enumerate(load_bank("D-07H", "development")[:2]):
    unit = cfg["seed_base"] + 1000 * t_idx
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skels = unit_skeletons(sem, unit, cfg)
    for T in (40, 80):
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        for c_idx, ((kind, rate), full) in enumerate(skels.items()):
            skel = public(full)
            rng = lambda tag: np.random.default_rng([unit, 3, T, c_idx, tag])  # noqa: E731
            v4 = M.calibrate_width(M.tolerant_v3(data, skel, 2, cfg["H"], cfg["n_boot"], rng(6)),
                                   frozen_factor(T, skel.damage), "tolerant_v4")
            v4L, _ = tolerant_v4L_draws(data, skel, 2, cfg["H"], cfg["n_boot"], rng(6))
            n += 1
            if v4.status != "ok" or v4L.status != "ok":
                ok = v4.status == v4L.status
                lines.append(f"{topo.id} T={T} {kind}|{rate}: status {v4.status}/{v4L.status} ok={ok}")
                bad += not ok
                continue
            same = all(np.array_equal(getattr(v4, a), getattr(v4L, a)) for a in ("C", "lo", "hi"))
            structure = v4L.info["lag_from_draws"]
            theta_ok = (np.allclose(cumulative(v4L.theta, cfg["H"]), v4L.C) if structure
                        else np.array_equal(v4.theta, v4L.theta))
            bad += not (same and theta_ok)
            lines.append(f"{topo.id} T={T} {kind}|{rate}: C/lo/hi identical={same}; structure drawn={structure}; "
                         f"theta check={theta_ok}")
lines.append(f"runs: {n}; failures: {bad}")
out = ROOT / "results" / "ext_revlag_identity"
out.mkdir(parents=True, exist_ok=True)
(out / "check.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
