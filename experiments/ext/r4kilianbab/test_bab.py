"""Known-truth and identity checks of src/paper4/ext_r4kilianbab.py (D-07H development only).

1. Identity: with the stage-1 bias forced to zero (B1 = 0, no random numbers consumed), the K1 arm
   must reproduce ``tolerant_v5_1``'s interval exactly in every cell kind (same rng seed): this checks
   that steps (1)-(4) and the bootstrap are v5_1's, line for line.
2. Known bias: AR(1) x_t = 0.9 x_{t-1} + e_t (n = 1 node, lag_max 1), T = 40. Stage-1 bias of the own
   lag vs Monte Carlo bias of LS (1000 series) and Kendall/Pope's -(1 + 3 rho)/T.
3. Stationarity shrink: a bias that would push a near-unit-root B over 1 is shrunk to radius < 1;
   a non-stationary B is left uncorrected.
4. BC: when z0 = 0 (C_hat at the median of symmetric draws) the BC endpoints equal the percentile ones;
   tied draws fall back to percentile.
5. Timing of one K-core call vs one v5_1 call at T = 40 and 80 (missing-0.2, reversed-0.5).

Run: python experiments/ext/r4kilianbab/test_bab.py  -> results/ext_r4kilianbab_tests/tests.json
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

import run_experiment as R  # noqa: E402
from paper4 import ext_r4kilianbab as K  # noqa: E402
from paper4.effects import companion_radius  # noqa: E402
from paper4.estimator import fit_equations  # noqa: E402
from paper4.ext_v51 import tolerant_v5_1  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

OUT = ROOT / "results" / "ext_r4kilianbab_tests"
OUT.mkdir(parents=True, exist_ok=True)
CFG = json.loads((ROOT / "experiments/configs/ext_v51_eval.json").read_text())


def unit_data(t_idx, T, seed_base=777001):
    """A D-07H development unit (own seed base, never the calibration seeds)."""
    topo = load_bank("D-07H", "development")[t_idx]
    gen = R.generator_config(CFG)
    unit = seed_base + 1000 * t_idx
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skels = R.unit_skeletons(sem, unit, CFG)
    data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
    return sem, skels, data


def test_identity():
    res = {}
    orig = K.B1
    K.B1 = 0
    # stage1_bias has b1 = B1 as default bound at definition time: patch the default
    K.stage1_bias.__defaults__ = (0,)
    try:
        for T in (40, 80):
            _, skels, data = unit_data(0, T)
            for (kind, rate), full in skels.items():
                skel = R.public(full)
                K._CACHE.clear()
                a = tolerant_v5_1(data, skel, 2, 4, 49, np.random.default_rng(5))
                b = K.r4kilianbab_bab(data, skel, 2, 4, 49, np.random.default_rng(5))
                same = a.status == b.status and (a.status != "ok" or (np.array_equal(a.lo, b.lo) and np.array_equal(a.hi, b.hi)))
                res[f"T{T}|{kind}|{rate}"] = {"identical_interval": bool(same), "status": [a.status, b.status],
                                             "bias_zero": b.info.get("bab_absbias_mean") == 0.0 if b.status == "ok" else None}
    finally:
        K.B1 = orig
        K.stage1_bias.__defaults__ = (orig,)
    return res


def test_ar1():
    rho, T, sims = 0.9, 40, 1000
    rng = np.random.default_rng(11)
    terms = [[(0, 1)]]

    def sim(r):
        x = np.zeros((T + 100, 1))
        e = r.standard_normal(T + 100)
        for t in range(1, T + 100):
            x[t, 0] = rho * x[t - 1, 0] + e[t]
        return x[100:]

    est = [fit_equations(sim(rng), terms, 1).B[1, 0, 0] for _ in range(sims)]
    mc_bias = float(np.mean(est) - rho)
    data = sim(np.random.default_rng(12))
    fit = fit_equations(data, terms, 1)
    bias_hat, ok = K.stage1_bias(data, fit, 1, np.random.default_rng(13), b1=999)
    stage1 = [float(K.stage1_bias(sim(np.random.default_rng(100 + s)), fit_equations(sim(np.random.default_rng(100 + s)), terms, 1),
                                  1, np.random.default_rng(200 + s), b1=199)[0][1, 0, 0]) for s in range(50)]
    return {"rho": rho, "T": T, "mc_bias_LS": mc_bias, "kendall_pope_approx": -(1 + 3 * rho) / T,
            "stage1_bias_one_series_b999": float(bias_hat[1, 0, 0]), "stage1_bias_mean_over_50_series_b199": float(np.mean(stage1)),
            "ok": ok}


def test_shrink():
    B = np.zeros((2, 1, 1))
    B[1, 0, 0] = 0.97
    bias = np.zeros_like(B)
    bias[1, 0, 0] = -0.05     # correction would give 1.02
    Bc, d, flag = K.kilian_correct(B, bias)
    B2 = B.copy()
    B2[1, 0, 0] = 1.01
    Bn, dn, fn = K.kilian_correct(B2, bias)
    return {"radius_after": companion_radius(Bc), "d": d, "flag": flag, "expected_d_max": 0.59,
            "nonstat_untouched": bool(np.array_equal(Bn, B2) and fn == 2)}


def test_bc():
    rng = np.random.default_rng(3)
    d = rng.standard_normal((999, 2, 2))
    C_hat = np.median(d, axis=0)
    lo, hi, info = K.bc_interval(d, C_hat)
    plo, phi = K.percentile_interval(d)
    d2 = d.copy()
    d2[:300, 0, 0] = 0.0
    lo2, hi2, info2 = K.bc_interval(d2, C_hat + 1.0)
    plo2, phi2 = K.percentile_interval(d2)
    return {"max_abs_diff_z0_0": float(max(np.abs(lo - plo).max(), np.abs(hi - phi).max())),
            "tie_pair_is_percentile": bool(lo2[0, 0] == plo2[0, 0] and hi2[0, 0] == phi2[0, 0]),
            "shifted_pairs_capped_share": info2["bc_share_capped"], "skipped_share": info2["bc_share_skipped"]}


def test_timing():
    out = {}
    for T in (40, 80):
        _, skels, data = unit_data(1, T)
        for cell in (("missing", 0.2), ("reversed", 0.5)):
            skel = R.public(skels[cell])
            t0 = time.perf_counter()
            tolerant_v5_1(data, skel, 2, 4, 199, np.random.default_rng(1))
            t1 = time.perf_counter()
            K._CACHE.clear()
            r = K.r4kilianbab_bab(data, skel, 2, 4, 199, np.random.default_rng(1))
            t2 = time.perf_counter()
            out[f"T{T}|{cell[0]}|{cell[1]}"] = {"v51_s": round(t1 - t0, 2), "bab_s": round(t2 - t1, 2),
                                                "bab_info": {k: v for k, v in r.info.items() if k.startswith("bab_")}}
    return out


if __name__ == "__main__":
    res = {"identity": test_identity(), "ar1": test_ar1(), "shrink": test_shrink(), "bc": test_bc(),
           "timing": test_timing()}
    res["identity_all"] = all(v["identical_interval"] for v in res["identity"].values())
    (OUT / "tests.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=1))
