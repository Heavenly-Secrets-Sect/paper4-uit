# r4prepivot, part `secondary`

Run 2026-11-02T12:40:02Z – 2026-11-02T13:01:54Z, 1312.3 s, 720 datasets.
Pairing of tolerant_v5_1 rows with `ext_v51_eval`: 720/720 identical (different 0, not in stored 0) -> PASS.

| scenario | T | kind | rate | runs | cov v51 | cov pp | cov orig | IS v51 | IS pp | IS orig | ratio pp [2s 95% CI] | upper 1s | p(H0 >= 1.10) | NI raw / Holm | ratio orig | NI orig Holm | f_pp median [IQR] | f_orig median | f_v51 eff | width v51 / pp | pp ok |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | 60 | 0.920 | 0.898 | 0.898 | 4.37 | 4.46 | 4.38 | 1.019 [0.990, 1.045] | 1.041 | 5e-05 | Y / Y | 1.001 | Y | 1.147 [1.109, 1.190] | 1.155 | 1.300 | 2.77 / 2.44 | 60/60 |
| clean | 40 | extra | 0.2 | 60 | 0.914 | 0.879 | 0.886 | 4.63 | 4.88 | 4.74 | 1.055 [1.010, 1.093] | 1.087 | 0.0098 | Y / Y | 1.025 | Y | 1.121 [1.076, 1.163] | 1.163 | 1.300 | 2.91 / 2.46 | 60/60 |
| clean | 40 | extra | 0.5 | 60 | 0.920 | 0.879 | 0.902 | 4.81 | 5.02 | 4.88 | 1.043 [0.999, 1.083] | 1.077 | 0.0026 | Y / Y | 1.013 | Y | 1.110 [1.059, 1.142] | 1.180 | 1.300 | 3.21 / 2.75 | 60/60 |
| clean | 80 | extra | 0.2 | 60 | 0.927 | 0.902 | 0.908 | 2.53 | 2.67 | 2.62 | 1.057 [1.027, 1.089] | 1.084 | 0.0051 | Y / Y | 1.034 | Y | 1.086 [1.045, 1.127] | 1.106 | 1.200 | 1.73 / 1.58 | 60/60 |
| clean | 80 | extra | 0.5 | 60 | 0.925 | 0.893 | 0.905 | 2.67 | 2.81 | 2.73 | 1.055 [1.028, 1.081] | 1.076 | 0.0008 | Y / Y | 1.024 | Y | 1.068 [1.047, 1.090] | 1.121 | 1.200 | 1.88 / 1.66 | 60/60 |
| clean | 150 | none | 0.0 | 60 | 0.963 | 0.940 | 0.944 | 1.57 | 1.58 | 1.56 | 1.006 [0.986, 1.025] | 1.022 | 5e-05 | Y / Y | 0.994 | Y | 1.062 [1.033, 1.091] | 1.068 | 1.200 | 1.26 / 1.13 | 60/60 |
| clean | 150 | extra | 0.2 | 60 | 0.963 | 0.936 | 0.940 | 1.60 | 1.61 | 1.60 | 1.008 [0.983, 1.031] | 1.027 | 5e-05 | Y / Y | 0.999 | Y | 1.065 [1.036, 1.086] | 1.083 | 1.200 | 1.34 / 1.17 | 60/60 |
| clean | 150 | extra | 0.5 | 60 | 0.963 | 0.940 | 0.951 | 1.68 | 1.67 | 1.66 | 0.997 [0.973, 1.019] | 1.015 | 5e-05 | Y / Y | 0.990 | Y | 1.051 [1.025, 1.065] | 1.095 | 1.200 | 1.37 / 1.19 | 60/60 |
| clean | 150 | missing | 0.2 | 60 | 0.966 | 0.926 | 0.930 | 1.76 | 1.77 | 1.75 | 1.006 [0.974, 1.037] | 1.032 | 5e-05 | Y / Y | 0.996 | Y | 0.945 [0.920, 0.976] | 0.962 | 1.150 | 1.46 / 1.22 | 60/60 |
| clean | 150 | missing | 0.5 | 60 | 0.968 | 0.928 | 0.937 | 1.99 | 1.95 | 1.94 | 0.982 [0.950, 1.016] | 1.010 | 5e-05 | Y / Y | 0.975 | Y | 0.936 [0.898, 0.958] | 0.958 | 1.150 | 1.60 / 1.30 | 60/60 |
| clean | 150 | reversed | 0.2 | 60 | 0.959 | 0.910 | 0.911 | 1.83 | 1.92 | 1.90 | 1.048 [1.000, 1.095] | 1.087 | 0.0143 | Y / Y | 1.039 | Y | 0.959 [0.918, 0.995] | 0.959 | 1.200 | 1.44 / 1.14 | 60/60 |
| clean | 150 | reversed | 0.5 | 60 | 0.943 | 0.901 | 0.892 | 2.03 | 2.12 | 2.16 | 1.043 [1.005, 1.081] | 1.075 | 0.00265 | Y / Y | 1.062 | N | 1.002 [0.951, 1.080] | 0.980 | 1.200 | 1.49 / 1.19 | 60/60 |

Runtime per dataset (seconds, median [min, max]) and outer share:

- ['clean', 40, 'none', 0.0]: total 2.26 [2.02, 2.53], v5.1 alone 0.45, ratio 5.0x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 40, 'extra', 0.2]: total 2.37 [2.17, 2.68], v5.1 alone 0.46, ratio 5.1x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 40, 'extra', 0.5]: total 2.62 [2.47, 2.81], v5.1 alone 0.52, ratio 5.0x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 80, 'extra', 0.2]: total 2.65 [2.29, 2.88], v5.1 alone 0.52, ratio 5.1x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 80, 'extra', 0.5]: total 3.08 [2.93, 3.24], v5.1 alone 0.62, ratio 4.9x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 150, 'none', 0.0]: total 3.20 [2.99, 3.46], v5.1 alone 0.66, ratio 4.8x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 150, 'extra', 0.2]: total 3.32 [2.92, 3.59], v5.1 alone 0.67, ratio 4.9x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 150, 'extra', 0.5]: total 3.83 [3.29, 4.64], v5.1 alone 0.79, ratio 4.8x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 150, 'missing', 0.2]: total 17.60 [15.69, 18.78], v5.1 alone 3.36, ratio 5.2x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 150, 'missing', 0.5]: total 17.50 [15.93, 20.01], v5.1 alone 3.37, ratio 5.2x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 150, 'reversed', 0.2]: total 3.60 [3.17, 3.81], v5.1 alone 0.73, ratio 5.0x; inner worlds ok median 39; pp status {'ok': 60}
- ['clean', 150, 'reversed', 0.5]: total 3.51 [3.20, 3.68], v5.1 alone 0.71, ratio 4.9x; inner worlds ok median 39; pp status {'ok': 60}

Spearman correlations (run level):

- spearman_f_vs_k|extra+none: rho -0.168 (n 480)
- spearman_f_vs_k|extra+none|T40: rho -0.242 (n 180)
- spearman_f_vs_k|extra+none|T80: rho -0.127 (n 120)
- spearman_f_vs_k|extra+none|T150: rho -0.154 (n 180)
- spearman_f_vs_k|missing+none: rho -0.798 (n 240)
- spearman_f_vs_k|missing+none|T150: rho -0.714 (n 180)
- spearman_f_vs_k|reversed+none: rho -0.499 (n 240)
- spearman_f_vs_k|reversed+none|T150: rho -0.286 (n 180)
- spearman_f_vs_T: rho -0.599 (n 720)
