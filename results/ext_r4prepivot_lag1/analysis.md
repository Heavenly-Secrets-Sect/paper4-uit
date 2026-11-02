# r4prepivot, part `lag1`

Run 2026-11-02T13:02:06Z – 2026-11-02T13:16:39Z, 872.9 s, 600 datasets.
Pairing of tolerant_v5_1 rows with `ext_region51_lag1`: 600/600 identical (different 0, not in stored 0) -> PASS.

| scenario | T | kind | rate | runs | cov v51 | cov pp | cov orig | IS v51 | IS pp | IS orig | ratio pp [2s 95% CI] | upper 1s | p(H0 >= 1.10) | NI raw / Holm | ratio orig | NI orig Holm | f_pp median [IQR] | f_orig median | f_v51 eff | width v51 / pp | pp ok |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 19 | none | 0.0 | 60 | 0.939 | 0.888 | 0.883 | 7.26 | 7.36 | 7.37 | 1.014 [0.971, 1.053] | 1.047 | 5e-05 | Y / Y | 1.016 | Y | 1.228 [1.091, 1.292] | 1.217 | 1.500 | 5.03 / 4.07 | 60/60 |
| clean | 19 | missing | 0.2 | 60 | 0.933 | 0.838 | 0.850 | 7.75 | 9.08 | 8.78 | 1.171 [1.088, 1.256] | 1.242 | 0.9513 | N / N | 1.134 | N | 0.761 [0.682, 0.842] | 0.800 | 1.050 | 5.52 / 3.97 | 60/60 |
| clean | 19 | missing | 0.5 | 60 | 0.963 | 0.860 | 0.873 | 8.38 | 8.61 | 8.39 | 1.028 [0.941, 1.123] | 1.107 | 0.06685 | N / N | 1.002 | N | 0.697 [0.627, 0.783] | 0.715 | 1.050 | 6.08 / 4.10 | 60/60 |
| clean | 19 | reversed | 0.2 | 60 | 0.966 | 0.867 | 0.866 | 11.11 | 13.77 | 13.17 | 1.239 [0.863, 1.698] | 1.645 | 0.647 | N / N | 1.185 | N | 1.105 [0.938, 1.178] | 1.081 | 1.750 | 6.54 / 4.00 | 60/60 |
| clean | 19 | reversed | 0.5 | 60 | 0.957 | 0.811 | 0.806 | 15.69 | 18.49 | 17.80 | 1.322 [0.965, 1.558] | 1.523 | 0.8922 | N / N | 1.272 | N | 1.034 [0.722, 1.164] | 0.976 | 1.750 | 6.18 / 3.58 | 57/60 |
| clean | 25 | none | 0.0 | 60 | 0.970 | 0.913 | 0.910 | 5.76 | 5.11 | 5.08 | 0.888 [0.826, 0.960] | 0.947 | 5e-05 | Y / Y | 0.883 | Y | 1.236 [1.131, 1.301] | 1.186 | 1.900 | 4.86 / 3.05 | 60/60 |
| clean | 25 | missing | 0.2 | 60 | 0.966 | 0.857 | 0.863 | 6.20 | 6.40 | 6.31 | 1.033 [0.956, 1.111] | 1.098 | 0.0455 | Y / N | 1.018 | N | 0.893 [0.836, 0.953] | 0.911 | 1.500 | 5.08 / 3.05 | 60/60 |
| clean | 25 | missing | 0.5 | 60 | 0.973 | 0.863 | 0.870 | 6.54 | 6.15 | 6.06 | 0.940 [0.867, 1.012] | 1.002 | 5e-05 | Y / Y | 0.927 | Y | 0.896 [0.819, 0.949] | 0.910 | 1.500 | 5.53 / 3.19 | 60/60 |
| clean | 25 | reversed | 0.2 | 60 | 0.975 | 0.896 | 0.891 | 6.12 | 5.38 | 5.38 | 0.880 [0.817, 0.952] | 0.939 | 5e-05 | Y / Y | 0.881 | Y | 1.155 [1.045, 1.227] | 1.113 | 1.900 | 5.15 / 3.16 | 60/60 |
| clean | 25 | reversed | 0.5 | 60 | 0.971 | 0.875 | 0.866 | 6.17 | 5.72 | 5.75 | 0.926 [0.855, 1.010] | 0.996 | 0.0002 | Y / Y | 0.931 | Y | 1.137 [1.054, 1.234] | 1.100 | 1.900 | 5.20 / 3.05 | 60/60 |

Runtime per dataset (seconds, median [min, max]) and outer share:

- ['clean', 19, 'none', 0.0]: total 1.27 [1.11, 1.50], v5.1 alone 0.25, ratio 5.0x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 19, 'missing', 0.2]: total 8.06 [6.84, 10.62], v5.1 alone 1.56, ratio 5.2x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 19, 'missing', 0.5]: total 18.53 [8.07, 28.94], v5.1 alone 3.33, ratio 5.6x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 19, 'reversed', 0.2]: total 1.34 [0.98, 3.67], v5.1 alone 0.26, ratio 5.0x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 19, 'reversed', 0.5]: total 1.47 [0.74, 3.62], v5.1 alone 0.28, ratio 5.3x; inner worlds ok median 39; pp status {'bootstrap_failed': 2, 'ok': 57, 'prepivot_failed': 1}
- ['clean', 25, 'none', 0.0]: total 1.13 [1.02, 1.24], v5.1 alone 0.22, ratio 5.0x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 25, 'missing', 0.2]: total 6.10 [5.81, 6.99], v5.1 alone 1.18, ratio 5.2x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 25, 'missing', 0.5]: total 4.29 [3.60, 6.23], v5.1 alone 0.85, ratio 5.0x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 25, 'reversed', 0.2]: total 0.82 [0.67, 0.95], v5.1 alone 0.16, ratio 5.0x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 25, 'reversed', 0.5]: total 0.84 [0.80, 0.94], v5.1 alone 0.17, ratio 5.1x; inner worlds ok median 39; pp status {'ok': 60}

Spearman correlations (run level):

- spearman_f_vs_k|missing+none: rho -0.718 (n 360)
- spearman_f_vs_k|missing+none|T19: rho -0.778 (n 180)
- spearman_f_vs_k|missing+none|T25: rho -0.683 (n 180)
- spearman_f_vs_k|reversed+none: rho -0.296 (n 357)
- spearman_f_vs_k|reversed+none|T19: rho -0.397 (n 177)
- spearman_f_vs_k|reversed+none|T25: rho -0.211 (n 180)
- spearman_f_vs_T: rho 0.261 (n 597)
