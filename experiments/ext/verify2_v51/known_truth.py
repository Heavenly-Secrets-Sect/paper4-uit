"""Skeptic check (verify2_v51), part 4: implementation of ext_v51 on known-truth cases.

A. Hand-made VAR, n = 3: show that a duplicated lag term halves the stored coefficient in
   fit_equations (the ext_narrow bug) and that dedup_terms restores it.
B. D-07H development (calibration bank, allowed for probes), T = 150 and T = 40, missing-0.5:
   same data, same public skeleton, same rng -> ext_narrow.tolerant_v5 (buggy) vs
   ext_v51.tolerant_v5_1; compare |C_hat - C_true| on non-null pairs (point error, no calibration).
C. Equivalences: no stated missing -> tolerant_v5_1 == ext_narrow.tolerant_v5_cal2 bit for bit;
   branch switch at r >= TAU; tolerant_sel_dd == tolerant_sel when no duplicate occurs.
Writes results/ext_verify2_v51/known_truth.json
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4 import ext_narrow as N  # noqa: E402
from paper4 import ext_v51 as V  # noqa: E402
from paper4.estimator import fit_equations  # noqa: E402
from paper4.generator import GeneratorConfig, build_dynamic_sem  # noqa: E402
from paper4.metrics import truth_effects  # noqa: E402
from paper4.skeleton import Skeleton, damage, true_skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

GEN = GeneratorConfig(lag_max=2, q0=0.3, cross_coef=(0.3, 0.8), self_coef=(0.2, 0.6), noise_var=(0.5, 1.5),
                      rho_max=0.9, burn_in=200)
out = {}

# ---------- A ----------
rng = np.random.default_rng(1)
T = 5000
x = np.zeros((T, 3))
for t in range(1, T):
    x[t, 0] = 0.5 * x[t - 1, 0] + rng.normal()
    x[t, 1] = 0.6 * x[t - 1, 0] + 0.3 * x[t - 1, 1] + rng.normal()
    x[t, 2] = 0.4 * x[t, 1] + rng.normal()
skel = Skeleton(3, oriented={(1, 2), (0, 1)})
opened = [(0, 1)]  # an "opened" pair that is also adjacent -> duplicated lag block in equation 1
raw = [N.opened_terms(skel, opened, j, 1) for j in range(3)]
dd = [V.dedup_terms(skel, opened, j, 1) for j in range(3)]
fr, fd = fit_equations(x, raw, 1), fit_equations(x, dd, 1)
out["A_hand_var"] = {"terms_eq1_raw": raw[1], "terms_eq1_dedup": dd[1],
                     "B_lag1_1<-0_true": 0.6, "B_lag1_1<-0_raw": float(fr.B[1, 1, 0]),
                     "B_lag1_1<-0_dedup": float(fd.B[1, 1, 0])}

# ---------- B / C ----------
topos = load_bank("D-07H", "development")
rowsB = []
for T in (40, 150):
    for i in range(6):
        seed = 8_880_000 + i   # not a probe / calibration seed
        sem = build_dynamic_sem(topos[i], GEN, np.random.default_rng([seed, 0]))
        truth = true_skeleton(sem)
        coef = {e: float(sem.B[lag, e[1], e[0]]) for e, lag in sem.edge_lag.items()}
        _, C_true, _, _ = truth_effects(sem, 4)
        nn = ~np.eye(sem.n, dtype=bool) & (np.abs(C_true) > 0.1)
        data = sem.simulate(T, np.random.default_rng([seed, 2, T]))
        sk = damage(truth, "missing", 0.5, np.random.default_rng([seed, 1, 2]), sem.edge_lag, coef)
        sk.log, sk.lag_hint = [], None
        a = N.tolerant_v5(data, sk, 2, 4, 49, np.random.default_rng(7))
        b = V.tolerant_v5_1(data, sk, 2, 4, 49, np.random.default_rng(7))
        # point estimate from the data fit (theta -> cumulative)
        from paper4.effects import cumulative
        Ca, Cb = cumulative(a.theta, 4), cumulative(b.theta, 4)
        rowsB.append({"T": T, "topo": topos[i].id, "status": [a.status, b.status],
                      "dup_data": b.info.get("n_dup_terms_data"), "targeted": b.info.get("v51_targeted"),
                      "abs_err_point_bug": float(np.mean(np.abs(Ca - C_true)[nn])),
                      "abs_err_point_dedup": float(np.mean(np.abs(Cb - C_true)[nn])),
                      "halfwidth_bug": float(np.mean(((a.hi - a.lo) / 2)[nn])),
                      "halfwidth_dedup": float(np.mean(((b.hi - b.lo) / 2)[nn])),
                      "cov_raw_bug": float(np.mean(((a.lo <= C_true) & (C_true <= a.hi))[nn])),
                      "cov_raw_dedup": float(np.mean(((b.lo <= C_true) & (C_true <= b.hi))[nn]))})
        if T == 40 and i < 2:
            # C1: no stated missing -> v5_1 equals v5_cal2 exactly
            skn = damage(truth, "reversed", 0.2, np.random.default_rng([seed, 1, 3]), sem.edge_lag, coef)
            skn.log, skn.lag_hint = [], None
            c1 = V.tolerant_v5_1(data, skn, 2, 4, 49, np.random.default_rng(9))
            c2 = N.tolerant_v5_cal2(data, skn, 2, 4, 49, np.random.default_rng(9))
            out.setdefault("C_no_missing_equals_v5_cal2", []).append(
                bool(np.array_equal(c1.lo, c2.lo) and np.array_equal(c1.hi, c2.hi)))
        if T == 150 and i == 0:
            # C2: branch switch: same skeleton at T = 220 -> r >= TAU -> all-lag branch
            data2 = sem.simulate(220, np.random.default_rng([seed, 2, 220]))
            s1 = V.tolerant_v5_1(data2, sk, 2, 4, 19, np.random.default_rng(3))
            s2 = N.tolerant_v5_cal2(data2, sk, 2, 4, 19, np.random.default_rng(3))
            out["C_branch_T220"] = {"ratio": s1.info["v51_ratio"], "targeted": s1.info["v51_targeted"],
                                    "equals_v5_cal2": bool(np.array_equal(s1.lo, s2.lo))}
out["B_rows"] = rowsB
for T in (40, 150):
    rr = [r for r in rowsB if r["T"] == T]
    out[f"B_summary_T{T}"] = {k: float(np.mean([r[k] for r in rr])) for k in
                              ("abs_err_point_bug", "abs_err_point_dedup", "halfwidth_bug", "halfwidth_dedup",
                               "cov_raw_bug", "cov_raw_dedup", "dup_data")}
    out[f"B_summary_T{T}"]["dedup_better_point_err"] = sum(r["abs_err_point_dedup"] < r["abs_err_point_bug"] for r in rr)
    out[f"B_summary_T{T}"]["n"] = len(rr)
(ROOT / "results/ext_verify2_v51").mkdir(parents=True, exist_ok=True)
(ROOT / "results/ext_verify2_v51/known_truth.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps({k: v for k, v in out.items() if k != "B_rows"}, indent=1, default=str))
