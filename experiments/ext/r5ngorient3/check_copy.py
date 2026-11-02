"""Code check of r5ngorient3 (docs/ext/r5ngorient3.md, section 3), run before registration.

On D-07H development (seed_base 70261102 + 700 000, distinct from every calibration/evaluation unit of this
direction), shock ng_mix, 2 units, T 80 and 150, every cell:
  (a) copy fidelity: ext_r5ngorient3.copy_with_v2_evidence == ext_r4ngorient.tolerant_ngA bit for bit
      (status, lo, hi, C), same rng stream;
  (b) identity: tolerant_ngA3 == tolerant_v5_1 bit for bit in none/extra cells;
  (c) runtime of tolerant_ngA3 relative to tolerant_v5_1 and tolerant_ngA.
No truth, IS or coverage is computed. Writes results/ext_r5ngorient3_check/check_copy.json.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "experiments" / "ext" / "r4ngorient"))
import laws  # noqa: E402
from paper4.ext_r4ngorient import tolerant_ngA  # noqa: E402
from paper4.ext_r5ngorient3 import copy_with_v2_evidence, tolerant_ngA3  # noqa: E402
from paper4.ext_v51 import tolerant_v5_1  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.topology import load_bank  # noqa: E402
from run_experiment import ext_seed, generator_config, public, unit_skeletons  # noqa: E402


def same(a, b) -> bool:
    if a.status != b.status:
        return False
    if a.status != "ok":
        return True
    return bool(np.array_equal(a.lo, b.lo) and np.array_equal(a.hi, b.hi) and np.array_equal(a.C, b.C))


def main():
    cfg = json.loads((ROOT / "experiments/configs/ext_r5ngorient3_ngmix.json").read_text(encoding="utf-8"))
    cfg = {**cfg, "bank": "D-07H", "split": "development"}
    gen = generator_config(cfg)
    H, lag_max, n_boot = cfg["H"], gen.lag_max, cfg["n_boot"]
    topos = load_bank("D-07H", "development")[:2]
    out = {"copy": [0, 0], "identity_none_extra": [0, 0], "seconds": {"v5_1": 0.0, "ngA": 0.0, "ngA3": 0.0},
           "mismatch": []}
    seed = ext_seed("tolerant_v5_1")
    for t_idx, topo in enumerate(topos):
        unit = 70261102 + 700_000 + 1000 * t_idx
        sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
        skels = unit_skeletons(sem, unit, cfg)
        node_law = laws.node_laws("ng_mix", unit, sem.n)
        for T in (80, 150):
            data = laws.simulate(sem, T, np.random.default_rng([unit, 2, T]), node_law)
            for c_idx, ((kind, rate), full) in enumerate(skels.items()):
                skel = public(full)
                rng = lambda: np.random.default_rng([unit, 3, T, c_idx, seed])  # noqa: E731
                t0 = time.perf_counter(); r51 = tolerant_v5_1(data, skel, lag_max, H, n_boot, rng())
                t1 = time.perf_counter(); rA = tolerant_ngA(data, skel, lag_max, H, n_boot, rng())
                t2 = time.perf_counter(); rC = copy_with_v2_evidence(data, skel, lag_max, H, n_boot, rng())
                t3 = time.perf_counter(); r3 = tolerant_ngA3(data, skel, lag_max, H, n_boot, rng())
                t4 = time.perf_counter()
                out["seconds"]["v5_1"] += t1 - t0
                out["seconds"]["ngA"] += t2 - t1
                out["seconds"]["ngA3"] += t4 - t3
                ok = same(rA, rC)
                out["copy"][0] += 1
                out["copy"][1] += int(ok)
                if not ok:
                    out["mismatch"].append(["copy", t_idx, T, kind, rate])
                if kind in ("none", "extra"):
                    ok2 = same(r51, r3)
                    out["identity_none_extra"][0] += 1
                    out["identity_none_extra"][1] += int(ok2)
                    if not ok2:
                        out["mismatch"].append(["identity", t_idx, T, kind, rate])
    out["PASS"] = bool(out["copy"][0] == out["copy"][1] and out["identity_none_extra"][0] == out["identity_none_extra"][1])
    res = ROOT / "results" / "ext_r5ngorient3_check"
    res.mkdir(parents=True, exist_ok=True)
    (res / "check_copy.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
