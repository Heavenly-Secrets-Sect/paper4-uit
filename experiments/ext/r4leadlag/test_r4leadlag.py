"""Known-truth and identity tests of src/paper4/ext_r4leadlag.py (D-07H development data only).

Run: /Users/kietnt/miniconda3/bin/python experiments/ext/r4leadlag/test_r4leadlag.py
Writes results/ext_r4leadlag_tests/tests.json.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from scipy import stats  # noqa: E402

import run_experiment as RE  # noqa: E402
from paper4 import ext_r4leadlag as LL  # noqa: E402
from paper4.ext_v51 import tolerant_v5_1  # noqa: E402
from paper4.generator import build_dynamic_sem, add_latent  # noqa: E402
from paper4.skeleton import damage, true_skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

OUT = ROOT / "results" / "ext_r4leadlag_tests"
CFG = json.loads((ROOT / "experiments" / "configs" / "ext_r4leadlag_eval_clean.json").read_text())


def t_chi2():
    xs = [0.1, 1, 3, 7.5, 15.5, 21.03, 40]
    err = max(abs(LL.chi2_sf_even(x, df) - stats.chi2.sf(x, df)) for x in xs for df in (2, 8, 12))
    return {"max_abs_err_vs_scipy": err, "ok": err < 1e-12}


def t_size(n_sim=4000):
    """Independent white noise: rejection rate of the gate at 0.05 (m, M as on the grid)."""
    rng = np.random.default_rng(11)
    out = {}
    for m, M in ((38, 4), (78, 4), (148, 6)):
        rej = 0
        for _ in range(n_sim):
            a, b = rng.normal(size=m), rng.normal(size=m)
            rej += LL.haugh_q(a, b, M)[1] < 0.05
        out[f"m{m}_M{M}"] = rej / n_sim
    # contemporaneous dependence only (missing edge): r_v = 0.6 r_u + e
    for m, M in ((78, 4), (148, 6)):
        rej = 0
        for _ in range(n_sim):
            a = rng.normal(size=m)
            b = 0.6 * a + rng.normal(size=m)
            rej += LL.haugh_q(a, b, M)[1] < 0.05
        out[f"contemp_m{m}_M{M}"] = rej / n_sim
    # persistent common cause: L AR(1) phi 0.8, r_u = L + e_u, r_v = L + e_v (power)
    for m, M in ((78, 4), (148, 6)):
        rej = 0
        for _ in range(n_sim // 4):
            L = np.zeros(m + 50)
            e = rng.normal(size=m + 50)
            for t in range(1, m + 50):
                L[t] = 0.8 * L[t - 1] + e[t]
            L = L[50:] * 0.5
            a, b = L + rng.normal(size=m), L + rng.normal(size=m)
            rej += LL.haugh_q(a, b, M)[1] < 0.05
        out[f"latent_ar08_m{m}_M{M}"] = rej / (n_sim // 4)
    ok = all(abs(out[k] - 0.05) < 0.02 for k in out if k.startswith("m") or k.startswith("contemp"))
    return {**out, "ok": ok}


def units(n_units=4):
    topos = load_bank("D-07H", "development")[:n_units]
    gen = RE.generator_config(CFG)
    for t_idx, topo in enumerate(topos):
        unit = CFG["seed_base"] + 500_000 + 1000 * t_idx
        sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
        yield unit, sem


def same(a, b):
    if a.status != b.status:
        return False
    if a.status != "ok":
        return True
    return bool(np.array_equal(a.lo, b.lo) and np.array_equal(a.hi, b.hi) and np.array_equal(a.C, b.C))


def t_identity():
    """Gate disabled -> bit-identical to tolerant_v5_1 on missing cells; k_miss = 0 -> identical always."""
    res = {"disabled_missing": [0, 0], "kmiss0": [0, 0], "enabled_missing_differs": [0, 0]}  # [hits, of]; last: differs when fired
    old = LL.ALPHA_GATE
    for unit, sem in units():
        truth = true_skeleton(sem)
        coef = {e: float(sem.B[lag, e[1], e[0]]) for e, lag in sem.edge_lag.items()}
        sem_l = add_latent(sem, 1, np.random.default_rng([unit, 5]))
        for T in (40, 80):
            data = sem_l.simulate(T, np.random.default_rng([unit, 2, T]))
            for kind, rate in (("missing", 0.5), ("reversed", 0.5), ("extra", 0.2), ("none", 0.0)):
                k_idx = ["none", "extra", "missing", "reversed"].index(kind)
                skel = RE.public(damage(truth, kind, rate, np.random.default_rng([unit, 1, k_idx]), sem.edge_lag, coef))
                ref = tolerant_v5_1(data, skel, 2, 4, 49, np.random.default_rng([unit, 9, T]))
                if kind == "missing":
                    LL.ALPHA_GATE = -1.0
                    got = LL.tolerant_v5_1_leadlag(data, skel, 2, 4, 49, np.random.default_rng([unit, 9, T]))
                    gotd = LL.tolerant_v5_1_leadlag_skel(data, skel, 2, 4, 49, np.random.default_rng([unit, 9, T]))
                    LL.ALPHA_GATE = old
                    res["disabled_missing"][0] += same(ref, got) + same(ref, gotd)
                    res["disabled_missing"][1] += 2
                    got2 = LL.tolerant_v5_1_leadlag(data, skel, 2, 4, 49, np.random.default_rng([unit, 9, T]))
                    fired = got2.info.get("gate_n_labelled", 0) > 0 or (got2.info.get("gate_draw_labelled_mean") or 0) > 0
                    res["enabled_missing_differs"][0] += int(fired and not same(ref, got2))
                    res["enabled_missing_differs"][1] += int(fired)
                else:
                    got = LL.tolerant_v5_1_leadlag(data, skel, 2, 4, 49, np.random.default_rng([unit, 9, T]))
                    gotd = LL.tolerant_v5_1_leadlag_skel(data, skel, 2, 4, 49, np.random.default_rng([unit, 9, T]))
                    res["kmiss0"][0] += same(ref, got) + same(ref, gotd)
                    res["kmiss0"][1] += 2
    LL.ALPHA_GATE = old
    ok = res["disabled_missing"][0] == res["disabled_missing"][1] and res["kmiss0"][0] == res["kmiss0"][1]
    return {**res, "ok": ok}


def t_leak():
    """Output does not depend on the private log or lag hints (public() strips them; check anyway)."""
    unit, sem = next(units(1))
    truth = true_skeleton(sem)
    coef = {e: float(sem.B[lag, e[1], e[0]]) for e, lag in sem.edge_lag.items()}
    full = damage(truth, "missing", 0.5, np.random.default_rng([unit, 1, 2]), sem.edge_lag, coef)
    data = add_latent(sem, 3, np.random.default_rng([unit, 5])).simulate(80, np.random.default_rng([unit, 2, 80]))
    a = LL.tolerant_v5_1_leadlag(data, RE.public(full), 2, 4, 49, np.random.default_rng(3))
    s2 = RE.public(full)
    s2.log = [{"pair": [0, 1], "true_lag": 0}]
    b = LL.tolerant_v5_1_leadlag(data, s2, 2, 4, 49, np.random.default_rng(3))
    return {"ok": same(a, b)}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = {"chi2": t_chi2(), "size_power": t_size(), "identity": t_identity(), "leak": t_leak()}
    res["all_ok"] = all(v["ok"] for v in res.values() if isinstance(v, dict))
    (OUT / "tests.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item()))
    print(json.dumps(res, indent=1, default=lambda o: o.item()))


if __name__ == "__main__":
    main()
