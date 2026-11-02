# POST HOC (descriptive, not a rule): strongest baseline per missing cell, all stored versions

Pairing check (tolerant_v4 rows equal to ext_baselines2_eval; sources with mismatches are dropped): ext_baselines2_eval: 0 mismatches, a2b_pselect: 0 mismatches, a2_baselines: 0 mismatches, ext_redteam_calbase: 0 mismatches, ext_tlp_eval: 0 mismatches, ext_narrow_eval: 0 mismatches

## T = 40, missing-0.2: tolerant_v4 cov 0.983, IS 7.77

| method | cov | IS | v4 - X [95% CI] | p two-sided |
|---|---|---|---|---|
| targeted_lp_cal | 0.953 | 4.75 | +3.01 [+2.63, +3.42] | 0.0005 |
| tolerant_v5 | 0.933 | 4.79 | +2.98 [+2.48, +3.44] | 0.0005 |
| targeted_lp | 0.864 | 5.15 | +2.61 [+1.93, +3.26] | 0.0005 |
| bvar_minnesota_v2_cal | 0.950 | 5.25 | +2.52 [+2.14, +2.88] | 0.0005 |
| bvar_minnesota_v2 | 0.742 | 6.86 | +0.91 [+0.00, +1.77] | 0.0505 |
| pselect_union | 0.862 | 6.96 | +0.80 [+0.16, +1.39] | 0.0190 |
| pselect_cal | 0.965 | 7.74 | +0.02 [-0.33, +0.40] | 0.9308 |
| fullvar_cal | 0.972 | 7.84 | -0.07 [-0.23, +0.07] | 0.3094 |
| bvar_cal | 0.926 | 8.59 | -0.82 [-1.27, -0.38] | 0.0005 |
| bvar_minnesota | 0.641 | 10.17 | -2.40 [-3.70, -1.20] | 0.0005 |
| ida_union | 0.722 | 10.36 | -2.59 [-3.46, -1.71] | 0.0005 |
| plugin | 0.654 | 11.80 | -4.04 [-5.23, -2.83] | 0.0005 |
| pselect_union_v2 | 0.688 | 13.18 | -5.41 [-7.45, -3.41] | 0.0005 |
| pselect_union_v2_cal | 0.942 | 16.81 | -9.04 [-10.01, -8.05] | 0.0005 |
| ida_cal | 0.927 | 23.50 | -15.73 [-17.53, -14.17] | 0.0005 |

Strongest baseline by IS: **targeted_lp_cal**; strongest with coverage >= 0.90: **targeted_lp_cal**.

## T = 40, missing-0.5: tolerant_v4 cov 0.978, IS 7.53

| method | cov | IS | v4 - X [95% CI] | p two-sided |
|---|---|---|---|---|
| targeted_lp_cal | 0.935 | 5.02 | +2.51 [+2.15, +2.86] | 0.0005 |
| tolerant_v5 | 0.944 | 5.12 | +2.41 [+2.06, +2.76] | 0.0005 |
| bvar_minnesota_v2_cal | 0.910 | 5.51 | +2.02 [+1.47, +2.57] | 0.0005 |
| targeted_lp | 0.826 | 5.88 | +1.65 [+0.96, +2.28] | 0.0005 |
| pselect_union | 0.853 | 6.63 | +0.90 [+0.30, +1.50] | 0.0060 |
| bvar_cal | 0.919 | 7.39 | +0.14 [-0.52, +0.76] | 0.6798 |
| pselect_cal | 0.968 | 7.46 | +0.07 [-0.32, +0.45] | 0.7398 |
| fullvar_cal | 0.954 | 7.76 | -0.23 [-0.53, +0.04] | 0.1065 |
| bvar_minnesota_v2 | 0.621 | 10.20 | -2.67 [-3.99, -1.42] | 0.0005 |
| pselect_union_v2 | 0.717 | 11.35 | -3.82 [-5.05, -2.65] | 0.0005 |
| bvar_minnesota | 0.481 | 14.98 | -7.45 [-8.95, -5.99] | 0.0005 |
| pselect_union_v2_cal | 0.954 | 15.77 | -8.25 [-8.89, -7.59] | 0.0005 |
| ida_union | 0.393 | 26.92 | -19.39 [-21.07, -17.70] | 0.0005 |
| plugin | 0.353 | 28.21 | -20.68 [-22.40, -18.99] | 0.0005 |
| ida_cal | 0.550 | 32.21 | -24.68 [-26.55, -22.88] | 0.0005 |

Strongest baseline by IS: **targeted_lp_cal**; strongest with coverage >= 0.90: **targeted_lp_cal**.

## T = 80, missing-0.2: tolerant_v4 cov 0.959, IS 3.28

| method | cov | IS | v4 - X [95% CI] | p two-sided |
|---|---|---|---|---|
| tolerant_v5 | 0.942 | 2.78 | +0.50 [+0.34, +0.67] | 0.0005 |
| targeted_lp | 0.930 | 3.48 | -0.20 [-0.39, -0.02] | 0.0320 |
| targeted_lp_cal | 0.954 | 3.48 | -0.21 [-0.36, -0.05] | 0.0085 |
| fullvar_cal | 0.963 | 3.50 | -0.22 [-0.33, -0.12] | 0.0005 |
| pselect_union | 0.921 | 3.74 | -0.46 [-0.70, -0.23] | 0.0005 |
| pselect_cal | 0.958 | 3.96 | -0.68 [-0.87, -0.49] | 0.0005 |
| pselect_union_v2 | 0.877 | 4.41 | -1.14 [-1.69, -0.63] | 0.0005 |
| pselect_union_v2_cal | 0.940 | 4.49 | -1.22 [-1.62, -0.82] | 0.0005 |
| bvar_minnesota_v2_cal | 0.958 | 4.86 | -1.58 [-1.93, -1.27] | 0.0005 |
| lp_allpast | 0.836 | 5.69 | -2.41 [-2.86, -2.00] | 0.0005 |
| bvar_minnesota_v2 | 0.719 | 6.48 | -3.20 [-3.84, -2.59] | 0.0005 |
| bvar_cal | 0.937 | 7.73 | -4.46 [-4.88, -4.06] | 0.0005 |
| bvar_minnesota | 0.676 | 8.62 | -5.34 [-6.05, -4.69] | 0.0005 |
| ida_union | 0.711 | 10.63 | -7.35 [-8.12, -6.57] | 0.0005 |
| plugin | 0.647 | 11.68 | -8.41 [-9.26, -7.56] | 0.0005 |
| ida_cal | 0.906 | 19.10 | -15.82 [-17.11, -14.56] | 0.0005 |

Strongest baseline by IS: **targeted_lp**; strongest with coverage >= 0.90: **targeted_lp**.

## T = 80, missing-0.5: tolerant_v4 cov 0.957, IS 3.37

| method | cov | IS | v4 - X [95% CI] | p two-sided |
|---|---|---|---|---|
| tolerant_v5 | 0.921 | 3.35 | +0.02 [-0.18, +0.22] | 0.8203 |
| fullvar_cal | 0.952 | 3.82 | -0.45 [-0.59, -0.31] | 0.0005 |
| targeted_lp_cal | 0.929 | 4.02 | -0.65 [-0.81, -0.48] | 0.0005 |
| pselect_cal | 0.941 | 4.13 | -0.76 [-0.91, -0.60] | 0.0005 |
| targeted_lp | 0.901 | 4.16 | -0.79 [-1.03, -0.57] | 0.0005 |
| pselect_union | 0.882 | 4.46 | -1.09 [-1.39, -0.79] | 0.0005 |
| pselect_union_v2 | 0.878 | 4.56 | -1.19 [-1.62, -0.77] | 0.0005 |
| pselect_union_v2_cal | 0.937 | 4.56 | -1.19 [-1.49, -0.89] | 0.0005 |
| bvar_minnesota_v2_cal | 0.958 | 4.58 | -1.21 [-1.42, -1.00] | 0.0005 |
| lp_allpast | 0.838 | 5.72 | -2.35 [-2.78, -1.97] | 0.0005 |
| bvar_cal | 0.953 | 6.28 | -2.91 [-3.10, -2.75] | 0.0005 |
| bvar_minnesota_v2 | 0.606 | 8.86 | -5.49 [-6.56, -4.47] | 0.0005 |
| bvar_minnesota | 0.492 | 13.39 | -10.02 [-11.08, -8.90] | 0.0005 |
| ida_union | 0.370 | 27.88 | -24.51 [-25.90, -23.15] | 0.0005 |
| plugin | 0.337 | 28.78 | -25.41 [-26.84, -23.99] | 0.0005 |
| ida_cal | 0.525 | 30.67 | -27.30 [-29.37, -25.45] | 0.0005 |

Strongest baseline by IS: **fullvar_cal**; strongest with coverage >= 0.90: **fullvar_cal**.

## T = 150, missing-0.2: tolerant_v4 cov 0.968, IS 2.06

| method | cov | IS | v4 - X [95% CI] | p two-sided |
|---|---|---|---|---|
| tolerant_v5 | 0.973 | 1.98 | +0.08 [-0.09, +0.20] | 0.3239 |
| pselect_union_v2 | 0.965 | 2.15 | -0.10 [-0.30, +0.08] | 0.3019 |
| pselect_union_v2_cal | 0.965 | 2.15 | -0.10 [-0.30, +0.07] | 0.3009 |
| targeted_lp | 0.930 | 2.28 | -0.22 [-0.38, -0.06] | 0.0100 |
| pselect_union | 0.953 | 2.31 | -0.25 [-0.42, -0.09] | 0.0015 |
| targeted_lp_cal | 0.976 | 2.35 | -0.29 [-0.39, -0.20] | 0.0005 |
| fullvar_cal | 0.980 | 2.59 | -0.53 [-0.65, -0.43] | 0.0005 |
| pselect_cal | 0.980 | 2.62 | -0.56 [-0.72, -0.41] | 0.0005 |
| lp_allpast | 0.902 | 2.74 | -0.68 [-0.90, -0.47] | 0.0005 |
| bvar_minnesota_v2_cal | 0.968 | 3.71 | -1.65 [-1.89, -1.44] | 0.0005 |
| bvar_minnesota_v2 | 0.793 | 4.45 | -2.40 [-2.99, -1.81] | 0.0005 |
| bvar_cal | 0.967 | 5.84 | -3.79 [-4.15, -3.50] | 0.0005 |
| bvar_minnesota | 0.771 | 5.90 | -3.85 [-4.66, -3.07] | 0.0005 |
| ida_union | 0.716 | 10.71 | -8.65 [-9.58, -7.73] | 0.0005 |
| plugin | 0.656 | 11.47 | -9.42 [-10.37, -8.46] | 0.0005 |
| ida_cal | 0.886 | 15.80 | -13.74 [-14.73, -12.78] | 0.0005 |

Strongest baseline by IS: **pselect_union_v2**; strongest with coverage >= 0.90: **pselect_union_v2**.

## T = 150, missing-0.5: tolerant_v4 cov 0.962, IS 2.22

| method | cov | IS | v4 - X [95% CI] | p two-sided |
|---|---|---|---|---|
| pselect_union_v2 | 0.967 | 2.29 | -0.07 [-0.24, +0.08] | 0.4124 |
| pselect_union_v2_cal | 0.967 | 2.29 | -0.07 [-0.24, +0.08] | 0.3864 |
| tolerant_v5 | 0.960 | 2.34 | -0.12 [-0.26, +0.02] | 0.0925 |
| targeted_lp_cal | 0.962 | 2.59 | -0.38 [-0.49, -0.26] | 0.0005 |
| targeted_lp | 0.905 | 2.66 | -0.44 [-0.63, -0.25] | 0.0005 |
| lp_allpast | 0.900 | 2.88 | -0.67 [-0.92, -0.41] | 0.0005 |
| pselect_cal | 0.952 | 2.89 | -0.68 [-0.80, -0.54] | 0.0005 |
| fullvar_cal | 0.961 | 2.91 | -0.70 [-0.82, -0.59] | 0.0005 |
| pselect_union | 0.908 | 3.11 | -0.89 [-1.19, -0.61] | 0.0005 |
| bvar_minnesota_v2_cal | 0.962 | 3.63 | -1.42 [-1.58, -1.26] | 0.0005 |
| bvar_cal | 0.972 | 4.97 | -2.75 [-2.87, -2.63] | 0.0005 |
| bvar_minnesota_v2 | 0.682 | 6.65 | -4.44 [-5.51, -3.39] | 0.0005 |
| bvar_minnesota | 0.569 | 10.18 | -7.96 [-9.24, -6.76] | 0.0005 |
| ida_union | 0.357 | 28.33 | -26.12 [-27.57, -24.68] | 0.0005 |
| plugin | 0.328 | 29.07 | -26.86 [-28.39, -25.30] | 0.0005 |
| ida_cal | 0.501 | 29.30 | -27.08 [-29.02, -25.25] | 0.0005 |

Strongest baseline by IS: **pselect_union_v2**; strongest with coverage >= 0.90: **pselect_union_v2**.

Holm (two-sided 0.05) over all 94 comparisons above: rejected = T40 m0.2 pselect_union_v2, T40 m0.2 pselect_union_v2_cal, T40 m0.2 bvar_minnesota_v2_cal, T40 m0.2 ida_union, T40 m0.2 bvar_minnesota, T40 m0.2 plugin, T40 m0.2 bvar_cal, T40 m0.2 ida_cal, T40 m0.2 targeted_lp, T40 m0.2 targeted_lp_cal, T40 m0.2 tolerant_v5, T40 m0.5 pselect_union_v2, T40 m0.5 pselect_union_v2_cal, T40 m0.5 bvar_minnesota_v2, T40 m0.5 bvar_minnesota_v2_cal, T40 m0.5 ida_union, T40 m0.5 bvar_minnesota, T40 m0.5 plugin, T40 m0.5 ida_cal, T40 m0.5 targeted_lp, T40 m0.5 targeted_lp_cal, T40 m0.5 tolerant_v5, T80 m0.2 pselect_union_v2, T80 m0.2 pselect_union_v2_cal, T80 m0.2 bvar_minnesota_v2, T80 m0.2 bvar_minnesota_v2_cal, T80 m0.2 pselect_union, T80 m0.2 ida_union, T80 m0.2 bvar_minnesota, T80 m0.2 lp_allpast, T80 m0.2 plugin, T80 m0.2 pselect_cal, T80 m0.2 bvar_cal, T80 m0.2 ida_cal, T80 m0.2 fullvar_cal, T80 m0.2 tolerant_v5, T80 m0.5 pselect_union_v2, T80 m0.5 pselect_union_v2_cal, T80 m0.5 bvar_minnesota_v2, T80 m0.5 bvar_minnesota_v2_cal, T80 m0.5 pselect_union, T80 m0.5 ida_union, T80 m0.5 bvar_minnesota, T80 m0.5 lp_allpast, T80 m0.5 plugin, T80 m0.5 pselect_cal, T80 m0.5 bvar_cal, T80 m0.5 ida_cal, T80 m0.5 fullvar_cal, T80 m0.5 targeted_lp, T80 m0.5 targeted_lp_cal, T150 m0.2 bvar_minnesota_v2, T150 m0.2 bvar_minnesota_v2_cal, T150 m0.2 ida_union, T150 m0.2 bvar_minnesota, T150 m0.2 lp_allpast, T150 m0.2 plugin, T150 m0.2 pselect_cal, T150 m0.2 bvar_cal, T150 m0.2 ida_cal, T150 m0.2 fullvar_cal, T150 m0.2 targeted_lp_cal, T150 m0.5 bvar_minnesota_v2, T150 m0.5 bvar_minnesota_v2_cal, T150 m0.5 pselect_union, T150 m0.5 ida_union, T150 m0.5 bvar_minnesota, T150 m0.5 lp_allpast, T150 m0.5 plugin, T150 m0.5 pselect_cal, T150 m0.5 bvar_cal, T150 m0.5 ida_cal, T150 m0.5 fullvar_cal, T150 m0.5 targeted_lp, T150 m0.5 targeted_lp_cal, T150 m0.2 pselect_union

## tolerant_v5 - pselect_union_v2(_cal), missing cells (IS difference, 95% CI)

| T | cell | v5 cov | v5 IS | v5 - pselect_v2 | v5 - pselect_v2_cal |
|---|---|---|---|---|---|
| 40 | missing-0.2 | 0.933 | 4.79 | -8.39 [-10.25, -6.58] | -12.02 [-13.08, -10.94] |
| 40 | missing-0.5 | 0.944 | 5.12 | -6.23 [-7.51, -5.04] | -10.65 [-11.41, -9.87] |
| 80 | missing-0.2 | 0.942 | 2.78 | -1.64 [-2.19, -1.13] | -1.72 [-2.15, -1.32] |
| 80 | missing-0.5 | 0.921 | 3.35 | -1.21 [-1.67, -0.78] | -1.21 [-1.55, -0.88] |
| 150 | missing-0.2 | 0.973 | 1.98 | -0.18 [-0.41, +0.06] | -0.18 [-0.40, +0.07] |
| 150 | missing-0.5 | 0.960 | 2.34 | +0.05 [-0.10, +0.20] | +0.05 [-0.10, +0.20] |
