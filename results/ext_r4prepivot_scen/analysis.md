# r4prepivot, part `scen`

Run 2026-11-02T13:16:39Z – 2026-11-02T13:30:10Z, 811.1 s, 720 datasets.
Pairing of tolerant_v5_1 rows with `ext_v51_a1`: 720/720 identical (different 0, not in stored 0) -> PASS.

| scenario | T | kind | rate | runs | cov v51 | cov pp | cov orig | IS v51 | IS pp | IS orig | ratio pp [2s 95% CI] | upper 1s | p(H0 >= 1.10) | NI raw / Holm | ratio orig | NI orig Holm | f_pp median [IQR] | f_orig median | f_v51 eff | width v51 / pp | pp ok |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| latent1 | 80 | none | 0.0 | 60 | 0.929 | 0.883 | 0.888 | 2.81 | 2.97 | 2.93 | 1.055 [1.007, 1.098] | 1.091 | 0.0203 | Y / N | 1.041 | Y | 1.105 [1.076, 1.131] | 1.112 | 1.300 | 1.92 / 1.62 | 60/60 |
| latent1 | 80 | missing | 0.2 | 60 | 0.953 | 0.873 | 0.887 | 3.15 | 3.42 | 3.35 | 1.084 [1.012, 1.159] | 1.147 | 0.323 | N / N | 1.062 | N | 0.930 [0.902, 0.961] | 0.969 | 1.300 | 2.42 / 1.72 | 60/60 |
| latent1 | 80 | reversed | 0.2 | 60 | 0.940 | 0.866 | 0.863 | 3.01 | 3.30 | 3.28 | 1.094 [1.018, 1.180] | 1.165 | 0.4117 | N / N | 1.089 | N | 1.034 [0.976, 1.074] | 1.031 | 1.350 | 2.12 / 1.57 | 60/60 |
| latent1 | 150 | none | 0.0 | 60 | 0.926 | 0.903 | 0.904 | 2.01 | 2.10 | 2.09 | 1.043 [1.013, 1.071] | 1.067 | 5e-05 | Y / Y | 1.037 | Y | 1.065 [1.048, 1.101] | 1.095 | 1.200 | 1.34 / 1.22 | 60/60 |
| latent1 | 150 | missing | 0.2 | 60 | 0.956 | 0.909 | 0.913 | 2.15 | 2.26 | 2.22 | 1.048 [1.014, 1.082] | 1.076 | 0.00105 | Y / Y | 1.030 | Y | 0.952 [0.926, 0.983] | 0.978 | 1.150 | 1.53 / 1.30 | 60/60 |
| latent1 | 150 | reversed | 0.2 | 60 | 0.936 | 0.873 | 0.875 | 2.19 | 2.41 | 2.37 | 1.100 [1.054, 1.143] | 1.135 | 0.494 | N / N | 1.082 | N | 0.949 [0.917, 0.996] | 0.963 | 1.200 | 1.50 / 1.22 | 60/60 |
| noise0.1 | 80 | none | 0.0 | 60 | 0.895 | 0.845 | 0.837 | 2.95 | 3.27 | 3.33 | 1.106 [1.068, 1.142] | 1.137 | 0.6243 | N / N | 1.127 | N | 1.100 [1.077, 1.124] | 1.081 | 1.300 | 1.81 / 1.54 | 60/60 |
| noise0.1 | 80 | missing | 0.2 | 60 | 0.916 | 0.804 | 0.808 | 3.26 | 4.17 | 4.12 | 1.279 [1.181, 1.374] | 1.359 | 0.9998 | N / N | 1.263 | N | 0.940 [0.917, 0.972] | 0.950 | 1.300 | 2.15 / 1.56 | 60/60 |
| noise0.1 | 80 | reversed | 0.2 | 60 | 0.895 | 0.811 | 0.804 | 3.21 | 3.75 | 3.88 | 1.170 [1.109, 1.228] | 1.219 | 0.9888 | N / N | 1.210 | N | 1.034 [1.001, 1.102] | 1.021 | 1.350 | 2.06 / 1.60 | 60/60 |
| noise0.1 | 150 | none | 0.0 | 60 | 0.921 | 0.888 | 0.887 | 1.91 | 2.03 | 2.01 | 1.064 [1.040, 1.085] | 1.082 | 0.0002 | Y / Y | 1.055 | Y | 1.063 [1.043, 1.097] | 1.071 | 1.200 | 1.25 / 1.12 | 60/60 |
| noise0.1 | 150 | missing | 0.2 | 60 | 0.916 | 0.864 | 0.863 | 2.24 | 2.53 | 2.52 | 1.129 [1.091, 1.165] | 1.159 | 0.936 | N / N | 1.124 | N | 0.958 [0.929, 0.999] | 0.961 | 1.150 | 1.40 / 1.19 | 60/60 |
| noise0.1 | 150 | reversed | 0.2 | 60 | 0.888 | 0.818 | 0.810 | 2.31 | 2.77 | 2.81 | 1.198 [1.149, 1.247] | 1.239 | 1 | N / N | 1.214 | N | 0.997 [0.962, 1.018] | 0.994 | 1.200 | 1.35 / 1.12 | 60/60 |

Runtime per dataset (seconds, median [min, max]) and outer share:

- ['latent1', 80, 'none', 0.0]: total 1.17 [1.10, 1.40], v5.1 alone 0.24, ratio 4.9x; inner worlds ok median 39; pp status {'ok': 60}
- ['latent1', 80, 'missing', 0.2]: total 7.22 [6.40, 8.71], v5.1 alone 1.37, ratio 5.3x; inner worlds ok median 39; pp status {'ok': 60}
- ['latent1', 80, 'reversed', 0.2]: total 1.39 [1.17, 1.63], v5.1 alone 0.29, ratio 4.8x; inner worlds ok median 39; pp status {'ok': 60}
- ['latent1', 150, 'none', 0.0]: total 1.74 [1.68, 1.83], v5.1 alone 0.36, ratio 4.9x; inner worlds ok median 39; pp status {'ok': 60}
- ['latent1', 150, 'missing', 0.2]: total 7.20 [6.43, 8.95], v5.1 alone 1.36, ratio 5.3x; inner worlds ok median 39; pp status {'ok': 60}
- ['latent1', 150, 'reversed', 0.2]: total 1.47 [1.32, 1.54], v5.1 alone 0.30, ratio 5.0x; inner worlds ok median 39; pp status {'ok': 60}
- ['noise0.1', 80, 'none', 0.0]: total 1.29 [0.97, 1.54], v5.1 alone 0.25, ratio 5.1x; inner worlds ok median 39; pp status {'ok': 60}
- ['noise0.1', 80, 'missing', 0.2]: total 6.36 [5.90, 6.93], v5.1 alone 1.21, ratio 5.3x; inner worlds ok median 39; pp status {'ok': 60}
- ['noise0.1', 80, 'reversed', 0.2]: total 1.33 [1.20, 1.38], v5.1 alone 0.26, ratio 5.1x; inner worlds ok median 39; pp status {'ok': 60}
- ['noise0.1', 150, 'none', 0.0]: total 1.52 [1.41, 1.71], v5.1 alone 0.31, ratio 4.9x; inner worlds ok median 39; pp status {'ok': 60}
- ['noise0.1', 150, 'missing', 0.2]: total 7.60 [6.43, 9.56], v5.1 alone 1.45, ratio 5.2x; inner worlds ok median 39; pp status {'ok': 60}
- ['noise0.1', 150, 'reversed', 0.2]: total 1.72 [1.53, 1.99], v5.1 alone 0.35, ratio 5.0x; inner worlds ok median 39; pp status {'ok': 60}

Spearman correlations (run level):

- spearman_f_vs_k|missing+none: rho -0.824 (n 480)
- spearman_f_vs_k|missing+none|T80: rho -0.855 (n 240)
- spearman_f_vs_k|missing+none|T150: rho -0.783 (n 240)
- spearman_f_vs_k|reversed+none: rho -0.580 (n 480)
- spearman_f_vs_k|reversed+none|T80: rho -0.488 (n 240)
- spearman_f_vs_k|reversed+none|T150: rho -0.739 (n 240)
- spearman_f_vs_T: rho -0.139 (n 720)
