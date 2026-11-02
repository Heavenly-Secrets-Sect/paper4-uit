# ext_v51_eval: confirmatory ruling v2 of tolerant_v5_1 (experiments/ext/v51fix/rule_p4h2_v2.py)

**SOFTWARE TEST ON D-07 DEVELOPMENT (ext_v51_eval). NOT A CONFIRMATORY RESULT.**

runs.jsonl sha256 eb8daf319d4400152bc54cb2eecad04919810cd09990f0e6d03f80b7216b2236; 2520 rows; 20 topologies

## Validity

- V1 manifest config equals the frozen config file: PASS
- V2 bank/split/methods/frozen file/seed/grid: PASS
- V3 row count and one row per (key, method): PASS
- V4 calibration.json equals the frozen factors: PASS
- V5 every ok row carries its frozen width factor (and prescale 0.5 for v5_1): PASS
- V6 fingerprint fields of paper4.ext_v51.tolerant_v5_1 on every ok v5_1 row, absent on v4 rows: PASS

## Failures

- failed runs: {'tolerant_v5_1': 13, 'tolerant_v4': 0}; ceiling for tolerant_v5_1: 12 of 1260 -> FAIL; per rule cell ceiling 3 of 60 (5%)

## Conditions

- C1 T=40 missing-0.2: cov ITT 0.922 (ok-only 0.922, 60/60 ok), IS 4.837 vs v4 7.765; v5_1 − v4 -2.928 [-3.438, -2.342] (p 0.0001; upper 97.5% -2.246, 98.33% -2.188) -> PASS
- C1 T=40 missing-0.5: cov ITT 0.919 (ok-only 0.939, 59/60 ok), IS 5.112 vs v4 7.528; v5_1 − v4 -2.452 [-2.850, -2.042] (p 0.0001; upper 97.5% -1.997, 98.33% -1.985) -> PASS
- C2 T=80 extra-0.2: cov ITT 0.906, IS 2.549 vs v4 2.528 (ratio 1.008); v5_1 − v4 +0.007 [-0.064, +0.086] -> PASS
- C2 T=80 extra-0.5: cov ITT 0.903, IS 2.685 vs v4 2.647 (ratio 1.014); v5_1 − v4 +0.023 [-0.030, +0.076] -> PASS
- C2 T=80 missing-0.2: cov ITT 0.928, IS 2.857 vs v4 3.277 (ratio 0.872); v5_1 − v4 -0.434 [-0.547, -0.332] -> PASS
- C2 T=80 missing-0.5: cov ITT 0.930, IS 3.118 vs v4 3.370 (ratio 0.925); v5_1 − v4 -0.267 [-0.395, -0.148] -> PASS
- C2 T=80 reversed-0.2: cov ITT 0.920, IS 2.807 vs v4 2.791 (ratio 1.006); v5_1 − v4 +0.003 [-0.051, +0.055] -> PASS
- C2 T=80 reversed-0.5: cov ITT 0.897, IS 3.065 vs v4 2.968 (ratio 1.033); v5_1 − v4 +0.081 [+0.013, +0.145] -> FAIL
- C2 T=150 extra-0.2: cov ITT 0.963, IS 1.601 vs v4 1.581 (ratio 1.013); v5_1 − v4 +0.021 [-0.006, +0.044] -> PASS
- C2 T=150 extra-0.5: cov ITT 0.963, IS 1.676 vs v4 1.657 (ratio 1.011); v5_1 − v4 +0.019 [-0.003, +0.044] -> PASS
- C2 T=150 missing-0.2: cov ITT 0.966, IS 1.759 vs v4 2.057 (ratio 0.855); v5_1 − v4 -0.298 [-0.359, -0.241] -> PASS
- C2 T=150 missing-0.5: cov ITT 0.968, IS 1.986 vs v4 2.215 (ratio 0.896); v5_1 − v4 -0.230 [-0.300, -0.163] -> PASS
- C2 T=150 reversed-0.2: cov ITT 0.959, IS 1.828 vs v4 1.894 (ratio 0.965); v5_1 − v4 -0.066 [-0.098, -0.032] -> PASS
- C2 T=150 reversed-0.5: cov ITT 0.943, IS 2.033 vs v4 2.017 (ratio 1.008); v5_1 − v4 +0.016 [-0.040, +0.074] -> PASS
- C3 T=40 none-0.0: IS 4.371 vs v4 4.391 (ratio 0.996); v5_1 − v4 -0.019 [-0.167, +0.135] -> PASS
- C3 T=80 none-0.0: IS 2.550 vs v4 2.502 (ratio 1.019); v5_1 − v4 +0.032 [-0.025, +0.096] -> PASS
- C3 T=150 none-0.0: IS 1.572 vs v4 1.564 (ratio 1.006); v5_1 − v4 +0.009 [-0.024, +0.039] -> PASS
- C3 T=40 extra-0.2: IS 4.626 vs v4 4.724 (ratio 0.979); v5_1 − v4 -0.103 [-0.232, +0.010] -> PASS
- C3 T=40 extra-0.5: IS 4.830 vs v4 4.858 (ratio 0.994); v5_1 − v4 -0.036 [-0.171, +0.056] -> PASS
- C3 T=40 reversed-0.2: IS 4.709 vs v4 4.784 (ratio 0.984); v5_1 − v4 -0.077 [-0.246, +0.066] -> PASS
- C3 T=40 reversed-0.5: IS 4.759 vs v4 4.779 (ratio 0.996); v5_1 − v4 -0.038 [-0.131, +0.045] -> PASS

## Summary

C1 2/2 (Holm over 2: 2/2); C2 11/12 (v5_1 significantly worse than v4 after Holm: 0/12); C3 7/7 (significantly worse after Holm: 0/7); validity PASS; failure ceiling FAIL

-> **tolerant_v5_1 NOT CONFIRMED (DRY RUN on D-07 development)**

Reported variants (not the official verdict):
- C1 replaced by its Holm version (2 cells): NOT CONFIRMED
- Bonferroni overlay over 2 primary specs (C1 with 97.5% CI): NOT CONFIRMED
- Bonferroni overlay over 3 primary specs (C1 with 98.33% CI): NOT CONFIRMED

## Descriptive (pre-registered statements, no effect on the verdict)

- Coverage-gated cells (14) significantly below 0.90 after Holm (one-sided topology bootstrap, seed 2): 0/14; cells with ITT coverage < 0.93: ['40 missing-0.2 0.922', '40 missing-0.5 0.919', '80 extra-0.2 0.906', '80 extra-0.5 0.903', '80 missing-0.2 0.928', '80 reversed-0.2 0.920', '80 reversed-0.5 0.897']
- Branch: 357/357 ok missing runs of v5_1 took the targeted branch; max r over all ok v5_1 runs 4.981 vs TAU 6.6083. With 14 nodes and lag_max 2, r <= (T - 2)/29 <= 5.10 at T <= 150, so the all-lag branch cannot be selected. The method evaluated here is therefore exactly 'v5 with de-duplicated targeted opening'.
- Tau fragility (stated before the run): TAU = 6.6083 came from a D-07H probe whose decisive CI bound at T = 100 (-0.0038) is >= 0 for 11% of probe bootstrap seeds (then TAU about 2.94 and T = 150 would take the all-lag branch). This run tests the frozen method only; the T = 150 behaviour under TAU about 2.94 is the D-07 sensitivity results/ext_v51fix_t150tau/ (descriptive, not tested here).
- v4 realisation: built-in methods are seeded by cell position (bug E1, not fixed). The tolerant_v4 rows of this run are the paper's P4-H2 v4 table; other P4-H2 configs with other cell lists give other v4 realisations.
