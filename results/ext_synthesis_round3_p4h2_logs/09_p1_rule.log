# ext_v51fix_p4h2: confirmatory ruling v2 of tolerant_v5_1 (experiments/ext/v51fix/rule_p4h2_v2.py)

runs.jsonl sha256 c1cd6ffe2aed18126ce238c0fcf275b1473a234f38696af200704b91e4d2d937; 2520 rows; 20 topologies

## Validity

- V1 manifest config equals the frozen config file: PASS
- V2 bank/split/methods/frozen file/seed/grid: PASS
- V3 row count and one row per (key, method): PASS
- V4 calibration.json equals the frozen factors: PASS
- V5 every ok row carries its frozen width factor (and prescale 0.5 for v5_1): PASS
- V6 fingerprint fields of paper4.ext_v51.tolerant_v5_1 on every ok v5_1 row, absent on v4 rows: PASS

## Failures

- failed runs: {'tolerant_v5_1': 0, 'tolerant_v4': 0}; ceiling for tolerant_v5_1: 12 of 1260 -> PASS; per rule cell ceiling 3 of 60 (5%)

## Conditions

- C1 T=40 missing-0.2: cov ITT 0.928 (ok-only 0.928, 60/60 ok), IS 4.621 vs v4 7.813; v5_1 − v4 -3.192 [-3.539, -2.870] (p 0.0001; upper 97.5% -2.822, 98.33% -2.792) -> PASS
- C1 T=40 missing-0.5: cov ITT 0.947 (ok-only 0.947, 60/60 ok), IS 4.989 vs v4 7.536; v5_1 − v4 -2.547 [-2.761, -2.339] (p 0.0001; upper 97.5% -2.317, 98.33% -2.297) -> PASS
- C2 T=80 extra-0.2: cov ITT 0.932, IS 2.506 vs v4 2.488 (ratio 1.007); v5_1 − v4 +0.018 [-0.052, +0.092] -> PASS
- C2 T=80 extra-0.5: cov ITT 0.936, IS 2.522 vs v4 2.547 (ratio 0.990); v5_1 − v4 -0.024 [-0.076, +0.028] -> PASS
- C2 T=80 missing-0.2: cov ITT 0.963, IS 2.685 vs v4 3.128 (ratio 0.858); v5_1 − v4 -0.443 [-0.543, -0.335] -> PASS
- C2 T=80 missing-0.5: cov ITT 0.969, IS 2.893 vs v4 3.180 (ratio 0.910); v5_1 − v4 -0.287 [-0.394, -0.177] -> PASS
- C2 T=80 reversed-0.2: cov ITT 0.949, IS 2.728 vs v4 2.770 (ratio 0.985); v5_1 − v4 -0.042 [-0.122, +0.012] -> PASS
- C2 T=80 reversed-0.5: cov ITT 0.942, IS 2.911 vs v4 2.902 (ratio 1.003); v5_1 − v4 +0.008 [-0.038, +0.061] -> PASS
- C2 T=150 extra-0.2: cov ITT 0.960, IS 1.595 vs v4 1.569 (ratio 1.016); v5_1 − v4 +0.026 [-0.018, +0.078] -> PASS
- C2 T=150 extra-0.5: cov ITT 0.959, IS 1.622 vs v4 1.625 (ratio 0.998); v5_1 − v4 -0.003 [-0.028, +0.022] -> PASS
- C2 T=150 missing-0.2: cov ITT 0.964, IS 1.747 vs v4 1.979 (ratio 0.883); v5_1 − v4 -0.232 [-0.295, -0.169] -> PASS
- C2 T=150 missing-0.5: cov ITT 0.960, IS 1.991 vs v4 2.113 (ratio 0.942); v5_1 − v4 -0.122 [-0.280, +0.022] -> PASS
- C2 T=150 reversed-0.2: cov ITT 0.952, IS 1.837 vs v4 1.883 (ratio 0.975); v5_1 − v4 -0.047 [-0.100, +0.014] -> PASS
- C2 T=150 reversed-0.5: cov ITT 0.936, IS 1.997 vs v4 2.004 (ratio 0.997); v5_1 − v4 -0.007 [-0.055, +0.044] -> PASS
- C3 T=40 none-0.0: IS 4.244 vs v4 4.277 (ratio 0.992); v5_1 − v4 -0.033 [-0.112, +0.058] -> PASS
- C3 T=80 none-0.0: IS 2.366 vs v4 2.382 (ratio 0.993); v5_1 − v4 -0.016 [-0.069, +0.028] -> PASS
- C3 T=150 none-0.0: IS 1.559 vs v4 1.559 (ratio 1.000); v5_1 − v4 -0.001 [-0.024, +0.029] -> PASS
- C3 T=40 extra-0.2: IS 4.335 vs v4 4.325 (ratio 1.002); v5_1 − v4 +0.010 [-0.095, +0.104] -> PASS
- C3 T=40 extra-0.5: IS 4.518 vs v4 4.533 (ratio 0.997); v5_1 − v4 -0.015 [-0.097, +0.058] -> PASS
- C3 T=40 reversed-0.2: IS 4.515 vs v4 4.527 (ratio 0.997); v5_1 − v4 -0.012 [-0.087, +0.060] -> PASS
- C3 T=40 reversed-0.5: IS 5.025 vs v4 5.011 (ratio 1.003); v5_1 − v4 +0.014 [-0.063, +0.094] -> PASS

## Summary

C1 2/2 (Holm over 2: 2/2); C2 12/12 (v5_1 significantly worse than v4 after Holm: 0/12); C3 7/7 (significantly worse after Holm: 0/7); validity PASS; failure ceiling PASS

-> **tolerant_v5_1 CONFIRMED on P4-H2**

Reported variants (not the official verdict):
- C1 replaced by its Holm version (2 cells): CONFIRMED
- Bonferroni overlay over 2 primary specs (C1 with 97.5% CI): CONFIRMED
- Bonferroni overlay over 3 primary specs (C1 with 98.33% CI): CONFIRMED

## Descriptive (pre-registered statements, no effect on the verdict)

- Coverage-gated cells (14) significantly below 0.90 after Holm (one-sided topology bootstrap, seed 2): 0/14; cells with ITT coverage < 0.93: ['40 missing-0.2 0.928']
- Branch: 360/360 ok missing runs of v5_1 took the targeted branch; max r over all ok v5_1 runs 4.981 vs TAU 6.6083. With 14 nodes and lag_max 2, r <= (T - 2)/29 <= 5.10 at T <= 150, so the all-lag branch cannot be selected. The method evaluated here is therefore exactly 'v5 with de-duplicated targeted opening'.
- Tau fragility (stated before the run): TAU = 6.6083 came from a D-07H probe whose decisive CI bound at T = 100 (-0.0038) is >= 0 for 11% of probe bootstrap seeds (then TAU about 2.94 and T = 150 would take the all-lag branch). This run tests the frozen method only; the T = 150 behaviour under TAU about 2.94 is the D-07 sensitivity results/ext_v51fix_t150tau/ (descriptive, not tested here).
- v4 realisation: built-in methods are seeded by cell position (bug E1, not fixed). The tolerant_v4 rows of this run are the paper's P4-H2 v4 table; other P4-H2 configs with other cell lists give other v4 realisations.
