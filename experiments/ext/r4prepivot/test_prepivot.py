"""Known-truth and invariance tests for src/paper4/ext_r4prepivot.py (D-07H development only for data).

Run: /Users/kietnt/miniconda3/bin/python experiments/ext/r4prepivot/test_prepivot.py
Writes results/ext_r4prepivot_tests/tests.json. Exit code 1 if any test fails.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import R, ROOT  # noqa: E402
from paper4 import estimator, ext_v51, methods  # noqa: E402
from paper4 import ext_r4prepivot as P  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

RESULTS = {}


def check(name, cond, detail=""):
    RESULTS[name] = {"pass": bool(cond), "detail": detail}
    print(("PASS " if cond else "FAIL ") + name + (f"  {detail}" if detail else ""))


def t1_t_quantile():
    vals = {(0.975, 18): 2.100922, (0.975, 4): 2.776445, (0.975, 1000): 1.962339}
    err = max(abs(P.t_quantile(p, df) - v) for (p, df), v in vals.items())
    check("t_quantile matches tables (1e-5)", err < 1e-5, f"max err {err:.2e}")
    check("z_ref(19) = 2.1555", abs(P.z_ref(19) - 2.155500) < 1e-5, f"{P.z_ref(19):.6f}")


def t2_roots_known():
    C0 = np.array([[1.0, 0.5], [0.05, 2.0]])
    inner = np.stack([C0 + d for d in (np.array([[0, 1], [0, 0]]), np.array([[0, -1], [0, 0]]),
                                       np.array([[2, 3], [0, 0]]))]).astype(float)
    nn, al = P.roots_for(C0, inner)
    # pair (0,1): mean offset 1, sd = std([1,-1,3]) = 2 -> r = 0.5 ; pair (0,0): offset 2/3, sd 1.1547 -> 0.57735
    # pair (1,0), (1,1): sd 0 -> skipped. nn = off-diagonal with |C0| > 0.1 -> only (0,1).
    check("roots_for known values", np.allclose(sorted(al), sorted([0.5, (2 / 3) / np.std([0, 0, 2], ddof=1)]))
          and np.allclose(nn, [0.5]), f"nn {nn.tolist()} all {al.tolist()}")


def t3_perfect_bootstrap_gives_f1():
    """Exact bootstrap: estimate ~ N(C0, s^2) and its 19 inner draws ~ N(estimate, s^2): f ~ 1."""
    rng = np.random.default_rng(1)
    fs = []
    for rep in range(200):
        C0 = rng.normal(size=(14, 14)) * 2
        s = rng.uniform(0.2, 1.0, size=(14, 14))
        roots = []
        for b in range(39):
            centre = C0 + s * rng.normal(size=(14, 14))    # outer-world estimate from x_b
            inner = centre + s * rng.normal(size=(19, 14, 14))  # its bootstrap: same law
            roots.append(P.roots_for(C0, inner)[0])
        fs.append(P.c_from_roots(np.concatenate(roots)) / P.z_ref(19))
    m = float(np.mean(fs))
    check("perfectly calibrated bootstrap -> mean f within 0.98..1.02", 0.98 < m < 1.02,
          f"mean f {m:.4f}, sd {np.std(fs):.4f}; with 1.96 instead: {m * P.z_ref(19) / P.Z:.4f}")


def t4_biased_bootstrap_widens():
    """Inner sd half the true sampling sd -> f ~ 2."""
    rng = np.random.default_rng(2)
    C0 = rng.normal(size=(14, 14))
    roots = []
    for b in range(39):
        centre = C0 + rng.normal(size=(14, 14))          # outer-world estimate, true sd 1
        inner = centre + 0.5 * rng.normal(size=(19, 14, 14))
        roots.append(P.roots_for(C0, inner)[0])
    f = P.c_from_roots(np.concatenate(roots)) / P.z_ref(19)
    target = (1.959964 * np.sqrt(1 + 0.25)) / (P.z_ref(19) * 0.5)  # approx: (|N(0,1.25)| 95% q) / (0.5 sd)
    check("under-dispersed bootstrap -> f near 2.0..2.4", 1.9 < f < 2.6, f"f {f:.3f}, rough target {target:.3f}")


def t5_widen():
    lo, hi = np.array([0.0, -2.0]), np.array([2.0, 0.0])
    a, b = P.widen(lo, hi, 1.5)
    check("widen keeps midpoint, scales half-width", np.allclose(a, [-0.5, -2.5]) and np.allclose(b, [2.5, 0.5]))


def dataset(kind, rate, T=40, t_idx=0):
    cfg = json.loads((ROOT / "experiments/configs/ext_v51_eval.json").read_text(encoding="utf-8"))
    cfg["seed_base"] = 7_750_000
    topo = load_bank("D-07H", "development")[t_idx]
    unit = cfg["seed_base"] + 1000 * t_idx
    sem = build_dynamic_sem(topo, R.generator_config(cfg), np.random.default_rng([unit, 0]))
    full = R.unit_skeletons(sem, unit, cfg)[(kind, rate)]
    return sem.simulate(T, np.random.default_rng([unit, 2, T])), full


def t6_outer_identical_and_no_leak():
    data, full = dataset("missing", 0.5)
    pub = R.public(full)
    a = ext_v51.tolerant_v5_1(data, pub, 2, 4, 199, np.random.default_rng(5))
    core = P.prepivot_core(data, pub, 2, 4, 199, np.random.default_rng(5))
    v = core["v51"]
    same = np.array_equal(a.lo, v.lo) and np.array_equal(a.hi, v.hi) and np.array_equal(a.C, v.C)
    check("outer draws of prepivot_core identical to tolerant_v5_1", same)
    mid, half = (core["lo0"] + core["hi0"]) / 2, (core["hi0"] - core["lo0"]) / 2
    check("v5.1 prescaled interval = 0.5 x unscaled outer interval",
          np.allclose(v.lo, mid - 0.5 * half) and np.allclose(v.hi, mid + 0.5 * half))
    # leakage: the private log and lag hints are not read (public() strips them; also scramble them)
    leaky = full.copy()
    leaky.log = [{"junk": 1}]
    r1 = P.tolerant_v5_1_pp(data, R.public(full), 2, 4, 199, np.random.default_rng(6))
    r2 = P.tolerant_v5_1_pp(data, R.public(leaky), 2, 4, 199, np.random.default_rng(6))
    check("output unchanged when the private log changes", np.array_equal(r1.lo, r2.lo) and np.array_equal(r1.hi, r2.hi),
          f"f_d {r1.info['f_d']:.4f}")
    # determinism
    r3 = P.tolerant_v5_1_pp(data, R.public(full), 2, 4, 199, np.random.default_rng(6))
    check("deterministic given the rng seed", np.array_equal(r1.lo, r3.lo))
    check("bootstrap_C restored after calls", methods.bootstrap_C is estimator.bootstrap_C
          and ext_v51.bootstrap_C is estimator.bootstrap_C)
    c6 = P.prepivot_core(data, R.public(full), 2, 4, 199, np.random.default_rng(6))
    m6, h6 = (c6["lo0"] + c6["hi0"]) / 2, (c6["hi0"] - c6["lo0"]) / 2
    check("final interval = unscaled outer interval widened by f_d",
          np.allclose(r1.lo, m6 - r1.info["f_d"] * h6) and np.allclose(r1.hi, m6 + r1.info["f_d"] * h6))


def t7_restore_on_exception():
    rec = P._Recorder(0)
    try:
        with rec.patched():
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    check("bootstrap_C restored after an exception", methods.bootstrap_C is estimator.bootstrap_C
          and ext_v51.bootstrap_C is estimator.bootstrap_C)


def t8_reversed_branch_runs():
    data, full = dataset("reversed", 0.5, T=80, t_idx=1)
    r = P.tolerant_v5_1_pp(data, R.public(full), 2, 4, 199, np.random.default_rng(7))
    check("reversed branch (v3) runs, 39 inner worlds", r.status == "ok" and r.info["n_inner_ok"] == 39,
          f"status {r.status}, f_d {r.info.get('f_d')}")


if __name__ == "__main__":
    for f in (t1_t_quantile, t2_roots_known, t3_perfect_bootstrap_gives_f1, t4_biased_bootstrap_widens, t5_widen,
              t6_outer_identical_and_no_leak, t7_restore_on_exception, t8_reversed_branch_runs):
        f()
    dst = ROOT / "results" / "ext_r4prepivot_tests"
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "tests.json").write_text(json.dumps(RESULTS, indent=1), encoding="utf-8")
    n_fail = sum(not v["pass"] for v in RESULTS.values())
    print(f"{len(RESULTS) - n_fail}/{len(RESULTS)} passed")
    sys.exit(1 if n_fail else 0)
