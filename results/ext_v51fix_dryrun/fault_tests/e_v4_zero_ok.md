# ext_v51_eval: confirmatory ruling v2 of tolerant_v5_1 (experiments/ext/v51fix/rule_p4h2_v2.py)

**SOFTWARE TEST ON D-07 DEVELOPMENT (ext_v51_eval). NOT A CONFIRMATORY RESULT.**

runs.jsonl sha256 f5a1a0c67aaa60def11b03fb5709c89af5c4df3c6dc0baad73f5d236fac7987d; 2520 rows; 20 topologies

## Validity

- V1 manifest config equals the frozen config file: PASS
- V2 bank/split/methods/frozen file/seed/grid: PASS
- V3 row count and one row per (key, method): PASS
- V4 calibration.json equals the frozen factors: PASS
- V5 every ok row carries its frozen width factor (and prescale 0.5 for v5_1): PASS
- V6 fingerprint fields of paper4.ext_v51.tolerant_v5_1 on every ok v5_1 row, absent on v4 rows: PASS

## Failures

- failed runs: {'tolerant_v5_1': 0, 'tolerant_v4': 60}; ceiling for tolerant_v5_1: 12 of 1260 -> PASS; per rule cell ceiling 3 of 60 (5%)

## Conditions

- C1 T=40 missing-0.2: cov ITT 0.922 (ok-only 0.922, 60/60 ok), IS 4.837 vs v4 7.765; v5_1 − v4 -2.928 [-3.438, -2.342] (p 0.0001; upper 97.5% -2.246, 98.33% -2.188) -> PASS
- C1 T=40 missing-0.5: cov ITT 0.939 (ok-only 0.939, 60/60 ok), IS 5.090 vs v4 7.528; v5_1 − v4 -2.438 [-2.826, -2.029] (p 0.0001; upper 97.5% -1.992, 98.33% -1.973) -> PASS
- C2 T=80 extra-0.2: cov ITT 0.927, IS 2.531 vs v4 2.528 (ratio 1.001); v5_1 − v4 +0.003 [-0.065, +0.081] -> PASS
- C2 T=80 extra-0.5: cov ITT 0.925, IS 2.666 vs v4 2.647 (ratio 1.007); v5_1 − v4 +0.019 [-0.036, +0.074] -> PASS
- C2 T=80 missing-0.2: cov ITT 0.949, IS 2.842 vs v4 3.277 (ratio 0.867); v5_1 − v4 -0.435 [-0.545, -0.335] -> PASS
- C2 T=80 missing-0.5: cov ITT 0.951, IS 3.100 vs v4 3.370 (ratio 0.920); v5_1 − v4 -0.270 [-0.395, -0.153] -> PASS
- C2 T=80 reversed-0.2: cov ITT 0.941, IS 2.793 vs v4 2.791 (ratio 1.001); v5_1 − v4 +0.002 [-0.051, +0.055] -> PASS
- C2 T=80 reversed-0.5: cov ITT 0.918, IS 3.047 vs v4 2.968 (ratio 1.026); v5_1 − v4 +0.078 [+0.012, +0.143] -> PASS
- C2 T=150 extra-0.2: cov ITT 0.963, IS 1.601 vs v4 1.581 (ratio 1.013); v5_1 − v4 +0.021 [-0.006, +0.044] -> PASS
- C2 T=150 extra-0.5: cov ITT 0.963, IS 1.676 vs v4 1.657 (ratio 1.011); v5_1 − v4 +0.019 [-0.003, +0.044] -> PASS
- C2 T=150 missing-0.2: cov ITT 0.966, IS 1.759 vs v4 2.057 (ratio 0.855); v5_1 − v4 -0.298 [-0.359, -0.241] -> PASS
- C2 T=150 missing-0.5: cov ITT 0.968, IS 1.986 vs v4 2.215 (ratio 0.896); v5_1 − v4 -0.230 [-0.300, -0.163] -> PASS
- C2 T=150 reversed-0.2: cov ITT 0.959, IS 1.828 vs v4 1.894 (ratio 0.965); v5_1 − v4 -0.066 [-0.098, -0.032] -> PASS
- C2 T=150 reversed-0.5: cov ITT 0.943, IS 2.033 vs v4 2.017 (ratio 1.008); v5_1 − v4 +0.016 [-0.040, +0.074] -> PASS
- C3 T=40 none-0.0: IS 4.372 vs v4 4.391 (ratio 0.996); v5_1 − v4 -0.018 [-0.163, +0.134] -> PASS
- C3 T=80 none-0.0: IS 2.535 vs v4 2.502 (ratio 1.013); v5_1 − v4 +0.032 [-0.025, +0.095] -> PASS
- C3 T=150 none-0.0: PROBLEM ['0 ok runs'] -> FAIL
- C3 T=40 extra-0.2: IS 4.625 vs v4 4.724 (ratio 0.979); v5_1 − v4 -0.099 [-0.226, +0.012] -> PASS
- C3 T=40 extra-0.5: IS 4.813 vs v4 4.858 (ratio 0.991); v5_1 − v4 -0.045 [-0.179, +0.044] -> PASS
- C3 T=40 reversed-0.2: IS 4.702 vs v4 4.784 (ratio 0.983); v5_1 − v4 -0.082 [-0.247, +0.060] -> PASS
- C3 T=40 reversed-0.5: IS 4.741 vs v4 4.779 (ratio 0.992); v5_1 − v4 -0.038 [-0.130, +0.044] -> PASS

## Summary

C1 2/2 (Holm over 2: 2/2); C2 12/12 (v5_1 significantly worse than v4 after Holm: 0/12); C3 6/7 (significantly worse after Holm: 0/7); validity PASS; failure ceiling PASS

-> **tolerant_v5_1 NOT CONFIRMED (DRY RUN on D-07 development)**

Reported variants (not the official verdict):
- C1 replaced by its Holm version (2 cells): NOT CONFIRMED
- Bonferroni overlay over 2 primary specs (C1 with 97.5% CI): NOT CONFIRMED
- Bonferroni overlay over 3 primary specs (C1 with 98.33% CI): NOT CONFIRMED

## Descriptive (pre-registered statements, no effect on the verdict)

- Coverage-gated cells (14) significantly below 0.90 after Holm (one-sided topology bootstrap, seed 2): 0/14; cells with ITT coverage < 0.93: ['40 missing-0.2 0.922', '80 extra-0.2 0.927', '80 extra-0.5 0.925', '80 reversed-0.5 0.918']
- Branch: 360/360 ok missing runs of v5_1 took the targeted branch; max r over all ok v5_1 runs 4.981 vs TAU 6.6083. With 14 nodes and lag_max 2, r <= (T - 2)/29 <= 5.10 at T <= 150, so the all-lag branch cannot be selected. The method evaluated here is therefore exactly 'v5 with de-duplicated targeted opening'.
- Tau fragility (stated before the run): TAU = 6.6083 came from a D-07H probe whose decisive CI bound at T = 100 (-0.0038) is >= 0 for 11% of probe bootstrap seeds (then TAU about 2.94 and T = 150 would take the all-lag branch). This run tests the frozen method only; the T = 150 behaviour under TAU about 2.94 is the D-07 sensitivity results/ext_v51fix_t150tau/ (descriptive, not tested here).
- v4 realisation: built-in methods are seeded by cell position (bug E1, not fixed). The tolerant_v4 rows of this run are the paper's P4-H2 v4 table; other P4-H2 configs with other cell lists give other v4 realisations.
