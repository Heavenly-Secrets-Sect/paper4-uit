"""Code check of the composition in src/paper4/ext_r5v52.py (before registration; D-07H development only).

For units seed_base + 800 000 + 1000 * topology + replicate of D-07H development (2 topologies x 1 replicate),
shocks gauss and ng_mix, T in {19, 25, 80, 150}, all 7 cells, n_boot 49, every method on v5_1's stream:
  (a) v5_2 with no reduction at all (hs_reduced = hs_ev_reduced = 0) == tolerant_ngA3 (status, raw C/lo/hi);
  (b) v5_2 with no gate open (data and draws)                       == tolerant_v5_1_hs2 (status, raw C/lo/hi,
      hs_reduced, hs_eq_total, hs_draws_reduced);
  (c) both                                                          == tolerant_v5_1;
  (d) ext_r5ngorient3's three rebound names are the original objects after every call.
No truth, IS or coverage is computed. Writes results/ext_r5v52_check/check_compose.json.
"""
from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
for p in ("src", "experiments", "experiments/ext/r4ngorient"):
    sys.path.insert(0, str(ROOT / p))
import laws  # noqa: E402
from run_experiment import ext_seed, generator_config, public, unit_skeletons  # noqa: E402
from paper4 import estimator as E  # noqa: E402
from paper4 import ext_narrow as N  # noqa: E402
from paper4 import ext_r5ngorient3 as A  # noqa: E402
from paper4.ext_r5hubscreen2 import tolerant_v5_1_hs2  # noqa: E402
from paper4.ext_r5v52 import tolerant_v5_2  # noqa: E402
from paper4.ext_v51 import tolerant_v5_1  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

CFG = json.loads((ROOT / "experiments/configs/ext_r5v52_gauss.json").read_text())


def same(a, b):
    if a.status != b.status:
        return False
    if a.status != "ok":
        return True
    return np.array_equal(a.C, b.C) and np.array_equal(a.lo, b.lo) and np.array_equal(a.hi, b.hi)


def main():
    warnings.filterwarnings("ignore")
    gen = generator_config(CFG)
    topos = load_bank("D-07H", "development")[:2]
    tag = ext_seed("tolerant_v5_1")
    orig = (E.fit_equations, N.select_open, E.bootstrap_C)
    out = {"n": 0, "a": [0, 0], "b": [0, 0], "c": [0, 0], "both_active": 0, "restored": True, "mismatch": [],
           "seconds": {}}
    secs = {"v51": 0.0, "ngA3": 0.0, "hs2": 0.0, "v52": 0.0}
    for t_idx, topo in enumerate(topos):
        unit = CFG["seed_base"] + 800_000 + 1000 * t_idx
        sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
        skels = unit_skeletons(sem, unit, dict(CFG, damage={"kinds": ["extra", "missing", "reversed"],
                                                               "rates": [0.2, 0.5]}))
        for shock in ("gauss", "ng_mix"):
            law = laws.node_laws(shock, unit, sem.n)
            for T in (19, 25, 80, 150):
                R = np.random.default_rng([unit, 2, T])
                data = sem.simulate(T, R) if shock == "gauss" else laws.simulate(sem, T, R, law)
                for c_idx, ((kind, rate), full) in enumerate(skels.items()):
                    skel = public(full)
                    rng = lambda: np.random.default_rng([unit, 3, T, c_idx, tag])  # noqa: E731
                    res = {}
                    for key, fn in (("v51", tolerant_v5_1), ("ngA3", A.tolerant_ngA3), ("hs2", tolerant_v5_1_hs2),
                                    ("v52", tolerant_v5_2)):
                        t0 = time.perf_counter()
                        res[key] = fn(data, skel, 2, 4, 49, rng())
                        secs[key] += time.perf_counter() - t0
                    if not (A.fit_equations is orig[0] and A.select_open is orig[1] and A.bootstrap_C is orig[2]):
                        out["restored"] = False
                    v = res["v52"]
                    diag = v.info.pop("ng_diag", None) or {}
                    data_g = sum(1 for r in list(diag.get("data_cands", [])) + list(diag.get("data_pool", [])) if r[2])
                    no_gate = (diag.get("n_gate_draws", [0, 0])[1] == 0) and data_g == 0
                    no_red = v.info.get("hs_reduced", 0) == 0 and v.info.get("hs_ev_reduced", 0) == 0
                    out["n"] += 1
                    out["both_active"] += int((not no_gate) and v.info.get("hs_reduced", 0) == 1)
                    case = [shock, topo.id, T, kind, rate, v.status]
                    if no_red:
                        ok = same(v, res["ngA3"])
                        out["a"][0] += 1; out["a"][1] += int(ok)
                        if not ok:
                            out["mismatch"].append(case + ["a"])
                    if no_gate:
                        h = res["hs2"]
                        ok = same(v, h) and all(v.info.get(k) == h.info.get(k)
                                                for k in ("hs_reduced", "hs_eq_total", "hs_draws_reduced"))
                        out["b"][0] += 1; out["b"][1] += int(ok)
                        if not ok:
                            out["mismatch"].append(case + ["b"])
                    if no_red and no_gate:
                        ok = same(v, res["v51"])
                        out["c"][0] += 1; out["c"][1] += int(ok)
                        if not ok:
                            out["mismatch"].append(case + ["c"])
    out["seconds"] = {k: round(s, 1) for k, s in secs.items()}
    out["PASS"] = bool(out["restored"] and not out["mismatch"])
    dst = ROOT / "results/ext_r5v52_check"
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "check_compose.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
