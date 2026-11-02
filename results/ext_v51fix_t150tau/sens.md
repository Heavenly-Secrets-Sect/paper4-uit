# v51fix: tau sensitivity at T = 150 (experiments/ext/v51fix/tau_sens.py)

D-07 development. tolerant_v5_1_t294 = tolerant_v5_1 with TAU 2.9370 (docs/ext/v51fix.md 1.C). Paired IS differences, 95% CI clustered by topology (1000, seed 0); one-sided p (10 000, seed 1); Holm 0.025 over 7 cells per direction.

Identity of tolerant_v4 rows (T = 150) with ext_v51_eval: 420/420 at 1e-12, counts identical 420, max |ΔIS| 0.00e+00 -> paired exact **True**

Width factors at T = 150 (runner value; effective = x 0.5): none t294 2.4 / v5_1 2.4, extra t294 2.4 / v5_1 2.4, missing t294 2.5 / v5_1 2.3, reversed t294 2.5 / v5_1 2.4

| cell | v4 cov / IS | v5_1 cov / IS | t294 cov / IS | t294 targeted share, r | t294 − v5_1 [CI] (p worse) | t294 − v4 [CI] (p worse / p better) | Holm: t294 worse than v5_1 / better | Holm: t294 worse than v4 / better |
|---|---|---|---|---|---|---|---|---|
| none-0.0 | 0.964 / 1.564 | 0.963 / 1.572 | 0.964 / 1.576 | 0.00, 4.85 | +0.00 [-0.02, +0.03] (0.4018) | +0.01 [-0.02, +0.04] (0.2129 / 0.7872) | 0 / 0 | 0 / 0 |
| extra-0.2 | 0.965 / 1.581 | 0.963 / 1.601 | 0.965 / 1.587 | 0.00, 4.81 | -0.01 [-0.05, +0.02] (0.7967) | +0.01 [-0.03, +0.04] (0.3575 / 0.6426) | 0 / 0 | 0 / 0 |
| extra-0.5 | 0.967 / 1.657 | 0.963 / 1.676 | 0.969 / 1.656 | 0.00, 4.73 | -0.02 [-0.05, +0.01] (0.9051) | -0.00 [-0.03, +0.03] (0.5171 / 0.4830) | 0 / 0 | 0 / 0 |
| missing-0.2 | 0.968 / 2.057 | 0.966 / 1.759 | 0.974 / 2.085 | 0.00, 4.90 | +0.33 [+0.27, +0.39] (0.0001) | +0.03 [+0.00, +0.06] (0.0295 / 0.9706) | 1 / 0 | 0 / 0 |
| missing-0.5 | 0.962 / 2.215 | 0.968 / 1.986 | 0.975 / 2.262 | 0.00, 4.98 | +0.28 [+0.20, +0.35] (0.0001) | +0.05 [+0.01, +0.09] (0.0051 / 0.9950) | 1 / 0 | 0 / 0 |
| reversed-0.2 | 0.970 / 1.894 | 0.959 / 1.828 | 0.962 / 1.861 | 0.00, 4.85 | +0.03 [+0.01, +0.06] (0.0048) | -0.03 [-0.06, -0.01] (0.9952 / 0.0049) | 1 / 0 | 0 / 0 |
| reversed-0.5 | 0.959 / 2.017 | 0.943 / 2.033 | 0.954 / 2.031 | 0.00, 4.85 | -0.00 [-0.06, +0.05] (0.5136) | +0.01 [-0.03, +0.07] (0.3356 / 0.6645) | 0 / 0 | 0 / 0 |

## Pre-registered descriptive outputs (1.C)

1. Share of t294 missing runs in the targeted branch at T = 150: [0.0, 0.0] (0.00 = 100% all-lag).
3. C2 re-applied to t294 at T = 150 (6 damaged cells): 6/6 (no failing cell); C3 at T = 150 none: PASS.
   t294 significantly worse than v4 after Holm (7 cells): 0/7; better: 0/7. t294 significantly worse than v5_1 after Holm: 3/7; better: 0/7.
4. Interpretation rule: **T = 150 missing advantage depends on TAU > 4.94** (t294 − v5_1 has CI lower bound > 0 and is significant after Holm in both missing cells).
5. Non-missing cells: same code path for t294 and v5_1 (bootstrap stream by name and calibration differ): none-0.0 +0.004, extra-0.2 -0.014, extra-0.5 -0.020, reversed-0.2 +0.033, reversed-0.5 -0.003.
