# verify2_v51: independent recomputation (experiments/ext/verify2_v51/recompute.py)

## Pairing (exact equality of tolerant_v4 IS and covered counts)

- ev_vs_red: 1260/1260 (rows 1260 vs 1260)
- ev_vs_tlp: 1260/1260 (rows 1260 vs 1260)
- ev_vs_nar: 1260/1260 (rows 1260 vs 1260)
- ev_vs_abl: 1260/1260 (rows 1260 vs 1260)
- nar_vs_red: 1260/1260 (rows 1260 vs 1260)
- nar_vs_tlp: 1260/1260 (rows 1260 vs 1260)

## Win counts over 18 damaged cells (cov >= 0.90 and CI upper < 0), raw / Holm, bootstrap seeds 0, 11, 12

- v5 (round 1) vs pselect_cal: 18/18, 18/18, 18/18
- v5 (round 1) vs fullvar_cal: 18/18, 18/18, 18/18
- v5 (round 1) vs targeted_lp_cal: 13/11, 13/11, 13/11
- v5_1 vs pselect_cal: 18/18, 18/18, 18/18
- v5_1 vs fullvar_cal: 18/18, 18/18, 18/18
- v5_1 vs targeted_lp_cal: 13/12, 13/12, 13/12
- v5_1 vs tolerant_v4: 7/7, 7/7, 7/7

## Rule (b) recomputed (seed 0 / 11 / 12 for CI conditions)

- seed 0: C1 2/2 (Holm 2/2), C4a 2/2, C4b 2/2
- seed 11: C1 2/2 (Holm 2/2), C4a 2/2, C4b 2/2
- seed 12: C1 2/2 (Holm 2/2), C4a 2/2, C4b 2/2
- C2 12/12; min coverage 0.918, ratio range 0.8551–1.0264; significantly worse than v4: uncorrected 1/12, Holm 0/12
- C3 7/7; ratio range 0.979–1.013; worse after Holm 0/7
- C2 coverage margin: cells with cov < 0.93: [(80, 'extra', 0.2, 0.9272), (80, 'extra', 0.5, 0.925), (80, 'reversed', 0.5, 0.918)]

## v5_1 − v5 (round 1) and v5_1 − v5_cal2, missing cells (seed 0)

- T=40 missing-0.2: vs v5 +0.049 [-0.116, +0.255]; vs v5_cal2 -2.169 [-2.701, -1.579]
- T=40 missing-0.5: vs v5 -0.029 [-0.152, +0.103]; vs v5_cal2 -1.889 [-2.297, -1.479]
- T=80 missing-0.2: vs v5 +0.064 [-0.034, +0.154]; vs v5_cal2 -0.412 [-0.548, -0.291]
- T=80 missing-0.5: vs v5 -0.249 [-0.450, -0.079]; vs v5_cal2 -0.243 [-0.390, -0.100]
- T=150 missing-0.2: vs v5 -0.217 [-0.397, -0.106]; vs v5_cal2 -0.328 [-0.391, -0.261]
- T=150 missing-0.5: vs v5 -0.349 [-0.476, -0.235]; vs v5_cal2 -0.241 [-0.315, -0.176]

## Width factors (runner value) tolerant_v5 (ext_narrow_eval) vs tolerant_v5_1 (ext_v51_eval)

- 40|none: 2.8 vs 2.6
- 40|extra: 2.5 vs 2.6
- 40|missing: 2.4 vs 2.3
- 40|reversed: 2.8 vs 2.8
- 80|none: 2.5 vs 2.6
- 80|extra: 2.5 vs 2.4
- 80|missing: 2.5 vs 2.6
- 80|reversed: 2.7 vs 2.7
- 150|none: 2.3 vs 2.4
- 150|extra: 2.3 vs 2.4
- 150|missing: 2.5 vs 2.3
- 150|reversed: 2.5 vs 2.4

## a1 scenarios: v5_1 coverage (v4) per cell; one-sided p for cov < 0.90 (topology bootstrap, ratio of sums)

- latent1: cells cov >= 0.90: 9/9; significantly below 0.90 after Holm: 0/9; uncorrected p<0.025: 0/9
  - T=40 none-0.0: 0.9191 (v4 0.9353), IS 4.50 vs 4.52, p(cov<0.90) 0.9297
  - T=40 missing-0.2: 0.9385 (v4 0.9773), IS 5.12 vs 8.58, p(cov<0.90) 0.9998
  - T=40 reversed-0.2: 0.9304 (v4 0.9369), IS 4.71 vs 4.72, p(cov<0.90) 0.9947
  - T=80 none-0.0: 0.9288 (v4 0.9277), IS 2.81 vs 2.82, p(cov<0.90) 0.9972
  - T=80 missing-0.2: 0.9525 (v4 0.9666), IS 3.15 vs 3.54, p(cov<0.90) 1.0000
  - T=80 reversed-0.2: 0.9401 (v4 0.9466), IS 3.01 vs 3.02, p(cov<0.90) 1.0000
  - T=150 none-0.0: 0.9256 (v4 0.9250), IS 2.01 vs 2.05, p(cov<0.90) 0.9763
  - T=150 missing-0.2: 0.9558 (v4 0.9515), IS 2.15 vs 2.38, p(cov<0.90) 1.0000
  - T=150 reversed-0.2: 0.9358 (v4 0.9482), IS 2.19 vs 2.20, p(cov<0.90) 1.0000
- latent3: cells cov >= 0.90: 8/9; significantly below 0.90 after Holm: 0/9; uncorrected p<0.025: 1/9
  - T=40 none-0.0: 0.9142 (v4 0.9288), IS 4.77 vs 4.64, p(cov<0.90) 0.8855
  - T=40 missing-0.2: 0.9299 (v4 0.9746), IS 5.24 vs 8.43, p(cov<0.90) 0.9992
  - T=40 reversed-0.2: 0.9315 (v4 0.9353), IS 4.92 vs 4.87, p(cov<0.90) 0.9905
  - T=80 none-0.0: 0.9471 (v4 0.9488), IS 2.76 vs 2.78, p(cov<0.90) 1.0000
  - T=80 missing-0.2: 0.9606 (v4 0.9703), IS 3.21 vs 3.83, p(cov<0.90) 1.0000
  - T=80 reversed-0.2: 0.9617 (v4 0.9693), IS 3.06 vs 3.07, p(cov<0.90) 1.0000
  - T=150 none-0.0: 0.8749 (v4 0.8706), IS 2.97 vs 3.01, p(cov<0.90) 0.0205
  - T=150 missing-0.2: 0.9159 (v4 0.9266), IS 2.86 vs 3.05, p(cov<0.90) 0.9789
  - T=150 reversed-0.2: 0.9024 (v4 0.9245), IS 2.66 vs 2.67, p(cov<0.90) 0.6460
- noise0.1: cells cov >= 0.90: 4/9; significantly below 0.90 after Holm: 0/9; uncorrected p<0.025: 0/9
  - T=40 none-0.0: 0.8948 (v4 0.9094), IS 4.82 vs 4.85, p(cov<0.90) 0.3754
  - T=40 missing-0.2: 0.8997 (v4 0.9779), IS 5.32 vs 8.00, p(cov<0.90) 0.4888
  - T=40 reversed-0.2: 0.9094 (v4 0.9105), IS 5.00 vs 5.01, p(cov<0.90) 0.7391
  - T=80 none-0.0: 0.8954 (v4 0.8927), IS 2.95 vs 2.95, p(cov<0.90) 0.3579
  - T=80 missing-0.2: 0.9159 (v4 0.9423), IS 3.26 vs 3.47, p(cov<0.90) 0.9260
  - T=80 reversed-0.2: 0.8948 (v4 0.9040), IS 3.21 vs 3.18, p(cov<0.90) 0.3379
  - T=150 none-0.0: 0.9213 (v4 0.9207), IS 1.91 vs 1.89, p(cov<0.90) 0.9960
  - T=150 missing-0.2: 0.9164 (v4 0.9250), IS 2.24 vs 2.44, p(cov<0.90) 0.9619
  - T=150 reversed-0.2: 0.8878 (v4 0.9142), IS 2.31 vs 2.27, p(cov<0.90) 0.0795
