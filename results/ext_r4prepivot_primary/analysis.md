# r4prepivot, part `primary`

Run 2026-11-02T12:18:48Z – 2026-11-02T12:39:43Z, 1255.9 s, 540 datasets.
Pairing of tolerant_v5_1 rows with `ext_v51_eval`: 540/540 identical (different 0, not in stored 0) -> PASS.

| scenario | T | kind | rate | runs | cov v51 | cov pp | cov orig | IS v51 | IS pp | IS orig | ratio pp [2s 95% CI] | upper 1s | p(H0 >= 1.10) | NI raw / Holm | ratio orig | NI orig Holm | f_pp median [IQR] | f_orig median | f_v51 eff | width v51 / pp | pp ok |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | missing | 0.2 | 60 | 0.922 | 0.828 | 0.840 | 4.84 | 5.79 | 5.56 | 1.196 [1.102, 1.294] | 1.278 | 0.9779 | N / N | 1.149 | N | 0.822 [0.768, 0.886] | 0.858 | 1.150 | 3.29 / 2.38 | 60/60 |
| clean | 40 | missing | 0.5 | 60 | 0.939 | 0.816 | 0.837 | 5.09 | 6.28 | 5.97 | 1.234 [1.112, 1.371] | 1.347 | 0.9868 | N / N | 1.172 | N | 0.751 [0.714, 0.787] | 0.792 | 1.150 | 3.79 / 2.45 | 60/60 |
| clean | 40 | reversed | 0.2 | 60 | 0.928 | 0.863 | 0.859 | 4.70 | 5.09 | 5.01 | 1.082 [0.993, 1.172] | 1.156 | 0.3224 | N / N | 1.066 | N | 1.052 [0.982, 1.130] | 1.056 | 1.400 | 3.10 / 2.36 | 60/60 |
| clean | 40 | reversed | 0.5 | 60 | 0.920 | 0.843 | 0.834 | 4.74 | 5.36 | 5.33 | 1.130 [1.043, 1.226] | 1.210 | 0.7105 | N / N | 1.124 | N | 1.038 [0.958, 1.110] | 1.034 | 1.400 | 3.28 / 2.43 | 60/60 |
| clean | 80 | missing | 0.2 | 60 | 0.949 | 0.860 | 0.870 | 2.84 | 3.23 | 3.16 | 1.138 [1.058, 1.215] | 1.203 | 0.8197 | N / N | 1.113 | N | 0.938 [0.901, 0.969] | 0.959 | 1.300 | 2.19 / 1.59 | 60/60 |
| clean | 80 | missing | 0.5 | 60 | 0.951 | 0.855 | 0.871 | 3.10 | 3.53 | 3.43 | 1.139 [1.065, 1.214] | 1.202 | 0.8446 | N / N | 1.106 | N | 0.921 [0.893, 0.944] | 0.962 | 1.300 | 2.42 / 1.72 | 60/60 |
| clean | 80 | reversed | 0.2 | 60 | 0.941 | 0.876 | 0.873 | 2.79 | 3.07 | 3.06 | 1.098 [1.043, 1.152] | 1.143 | 0.4588 | N / N | 1.096 | N | 1.034 [0.996, 1.066] | 1.015 | 1.350 | 2.05 / 1.58 | 60/60 |
| clean | 80 | reversed | 0.5 | 60 | 0.918 | 0.846 | 0.834 | 3.05 | 3.53 | 3.60 | 1.160 [1.105, 1.213] | 1.205 | 0.9854 | N / N | 1.182 | N | 1.031 [0.986, 1.079] | 1.011 | 1.350 | 2.03 / 1.51 | 60/60 |
| clean | 80 | none | 0.0 | 60 | 0.939 | 0.904 | 0.900 | 2.53 | 2.66 | 2.64 | 1.051 [1.006, 1.097] | 1.089 | 0.01875 | Y / N | 1.041 | Y | 1.098 [1.063, 1.142] | 1.100 | 1.300 | 1.85 / 1.56 | 60/60 |

Runtime per dataset (seconds, median [min, max]) and outer share:

- ['clean', 40, 'missing', 0.2]: total 6.74 [4.71, 9.44], v5.1 alone 1.21, ratio 5.6x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 40, 'missing', 0.5]: total 10.38 [8.17, 13.10], v5.1 alone 1.88, ratio 5.5x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 40, 'reversed', 0.2]: total 2.05 [1.74, 2.26], v5.1 alone 0.40, ratio 5.1x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 40, 'reversed', 0.5]: total 2.28 [2.08, 2.74], v5.1 alone 0.45, ratio 5.1x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 80, 'missing', 0.2]: total 13.28 [10.18, 18.58], v5.1 alone 2.57, ratio 5.2x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 80, 'missing', 0.5]: total 17.64 [16.17, 19.64], v5.1 alone 3.36, ratio 5.3x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 80, 'reversed', 0.2]: total 3.26 [2.84, 3.52], v5.1 alone 0.64, ratio 5.1x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 80, 'reversed', 0.5]: total 3.03 [2.71, 3.94], v5.1 alone 0.62, ratio 4.9x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 80, 'none', 0.0]: total 2.82 [2.46, 3.57], v5.1 alone 0.59, ratio 4.8x; inner worlds ok median 39; pp status {'ok': 60}

Spearman correlations (run level):

- spearman_f_vs_k|missing+none: rho -0.616 (n 300)
- spearman_f_vs_k|missing+none|T40: rho -0.450 (n 120)
- spearman_f_vs_k|missing+none|T80: rho -0.745 (n 180)
- spearman_f_vs_k|reversed+none: rho -0.264 (n 300)
- spearman_f_vs_k|reversed+none|T40: rho -0.204 (n 120)
- spearman_f_vs_k|reversed+none|T80: rho -0.341 (n 180)
- spearman_f_vs_T: rho 0.313 (n 540)

## Ruling

pairing PASS; non-inferior (Holm 0.05 over 9) 0/9 (raw one-sided 95% bound < 1.10: 1/9); coverage >= 0.90 in 1/9; failure cap (<= 3 failed of 60) PASS -> tolerant_v5_1_pp NOT RETAINED (sensitivity analysis only). Secondary (design as proposed, descriptive): non-inferior Holm 1/9, coverage >= 0.90 in 0/9.
