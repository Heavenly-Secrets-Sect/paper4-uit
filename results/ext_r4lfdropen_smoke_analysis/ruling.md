# r4lfdropen ruling

Verdict: **INVALID (validity V1 failed)**

Summary: {"V1_pass": false, "wins_holm": 0, "wins_raw_ci": 0, "of": 6, "losses_holm": 1, "cov_all_primary_ge_090": false, "fail_ceiling_primary": true, "noharm_pass": false, "noharm_cells_pass": 0, "noharm_worse_holm": 0}

## Validity

- V1_eval_identity_nonmissing: {"n_a": 20, "n_b": 20, "common": 20, "identical": 0, "pass": false}
- V1_latent_identity_none: null
- V2_v51_vs_stored_eval: null

## Primary: missing cells, lfdr − v5_1 (B = 20000, seed 20261104, Holm 0.05 over 6)

| T | rate | cov lfdr | cov v5_1 | cov oracle | IS lfdr | IS v5_1 | IS oracle | dIS [95% CI] | p2 | Holm | WIN | fail lfdr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40 | 0.2 | 0.925 | 0.940 | 0.836 | 5.011 | 4.133 | 3.054 | +0.877 [+0.707, +1.047] | 0.00010 | rej | LOSS | 0/2 |
| 40 | 0.5 | 0.866 | 0.910 | 0.836 | 4.907 | 5.308 | 3.054 | -0.401 [-1.582, +0.781] | 0.49018 | – | – | 0/2 |
| 80 | 0.2 | 0.940 | 0.955 | 0.985 | 2.631 | 2.442 | 1.118 | +0.189 [-0.558, +0.936] | 0.51237 | – | – | 0/2 |
| 80 | 0.5 | 0.866 | 0.940 | 0.985 | 3.791 | 2.934 | 1.118 | +0.857 [-0.492, +2.206] | 0.51237 | – | – | 0/2 |
| 150 | 0.2 | – | – | – | – | – | – | – | nan | – | – | 0/0 |
| 150 | 0.5 | – | – | – | – | – | – | – | nan | – | – | 0/0 |

## No-harm: latent1 × missing-0.2 (Holm 0.05 over 3)

| T | cov lfdr | cov v5_1 | IS lfdr | IS v5_1 | ratio | dIS [95% CI] | p2 | Holm worse | pass |
|---|---|---|---|---|---|---|---|---|---|

## Secondary (descriptive)

### Width factors (runner value; effective = value × 0.5)

| T|kind | v5_1 frozen | v5_1 re-tuned (raw) | lfdr used | lfdr re-tuned (raw) |
|---|---|---|---|---|
| 40|none | 2.6 | 1.9 | 1.9 | 1.9 |
| 40|extra | 2.6 | 2.2 | 2.2 | 2.2 |
| 40|missing | 2.3 | 2.1 | 2.9 | 2.9 |
| 40|reversed | 2.8 | 2.2 | 2.2 | 2.2 |
| 80|none | 2.6 | 2.0 | 2.0 | 2.0 |
| 80|extra | 2.4 | 2.1 | 2.1 | 2.1 |
| 80|missing | 2.6 | 2.3 | 2.3 | 2.3 |
| 80|reversed | 2.7 | 2.2 | 2.2 | 2.2 |
| 150|none | 2.4 | None | None | None |
| 150|extra | 2.4 | None | None | None |
| 150|missing | 2.3 | None | None | None |
| 150|reversed | 2.4 | None | None | None |

### Opened lag blocks (data fit; mean over draws)

| T|rate | v5_1 data | lfdr data | drop | v5_1 draws | lfdr draws | drop | lfdr data q0/25/50/75/100 |
|---|---|---|---|---|---|---|---|
| 40|0.2 | 12.000 | 4.000 | 0.667 | 17.829 | 6.075 | 0.659 | [4.0, 4.0, 4.0, 4.0, 4.0] |
| 40|0.5 | 33.000 | 11.000 | 0.667 | 34.673 | 16.080 | 0.536 | [11.0, 11.0, 11.0, 11.0, 11.0] |
| 80|0.2 | 20.500 | 6.000 | 0.707 | 27.266 | 6.985 | 0.744 | [6.0, 6.0, 6.0, 6.0, 6.0] |
| 80|0.5 | 33.000 | 14.500 | 0.561 | 38.927 | 16.470 | 0.577 | [13.0, 13.75, 14.5, 15.25, 16.0] |
| 150|0.2 | – | – | – | – | – | – | None |
| 150|0.5 | – | – | – | – | – | – | None |

### Recall of the truly missing pairs

| T|rate | v5_1 data | lfdr data | lfdr draw avg | mean P of true pairs |
|---|---|---|---|---|
| 40|0.2 | 0.875 | 0.500 | 0.474 | 0.336 |
| 40|0.5 | 0.773 | 0.591 | 0.488 | 0.343 |
| 80|0.2 | 1.000 | 0.875 | 0.778 | 0.871 |
| 80|0.5 | 0.955 | 0.773 | 0.712 | 0.766 |

Logged open sets vs recomputation: {"logged_open_set_matches_recomputation": 8, "of": 8}

### All 21 a2 cells (lfdr − v5_1, Holm 0.05 over 21; descriptive)

| T | kind | rate | cov lfdr | cov v5_1 | IS lfdr | IS v5_1 | dIS [CI] | Holm |
|---|---|---|---|---|---|---|---|---|
| 40 | none | 0.0 | 0.910 | 0.985 | 2.798 | 2.942 | -0.145 [-0.274, -0.015] | rej |
| 40 | extra | 0.2 | 0.940 | 0.955 | 3.423 | 3.647 | -0.224 [-0.417, -0.031] | rej |
| 40 | extra | 0.5 | 0.925 | 0.970 | 3.287 | 3.482 | -0.195 [-0.375, -0.015] | rej |
| 40 | missing | 0.2 | 0.925 | 0.940 | 5.011 | 4.133 | +0.877 [+0.707, +1.047] | rej |
| 40 | missing | 0.5 | 0.866 | 0.910 | 4.907 | 5.308 | -0.401 [-1.582, +0.781] | – |
| 40 | reversed | 0.2 | 0.910 | 0.970 | 3.148 | 3.598 | -0.450 [-0.514, -0.386] | rej |
| 40 | reversed | 0.5 | 0.925 | 0.940 | 4.250 | 4.269 | -0.020 [-0.574, +0.534] | – |
| 80 | none | 0.0 | 0.925 | 0.985 | 1.929 | 2.058 | -0.129 [-0.141, -0.116] | rej |
| 80 | extra | 0.2 | 0.940 | 0.970 | 2.208 | 2.282 | -0.074 [-0.075, -0.073] | rej |
| 80 | extra | 0.5 | 0.925 | 0.940 | 2.483 | 2.457 | +0.026 [-0.026, +0.077] | – |
| 80 | missing | 0.2 | 0.940 | 0.955 | 2.631 | 2.442 | +0.189 [-0.558, +0.936] | – |
| 80 | missing | 0.5 | 0.866 | 0.940 | 3.791 | 2.934 | +0.857 [-0.492, +2.206] | – |
| 80 | reversed | 0.2 | 0.970 | 0.985 | 1.795 | 1.990 | -0.195 [-0.314, -0.077] | rej |
| 80 | reversed | 0.5 | 0.970 | 1.000 | 1.770 | 2.118 | -0.348 [-0.377, -0.319] | rej |
| 150 | none | 0.0 | – | – | – | – | – | – |
| 150 | extra | 0.2 | – | – | – | – | – | – |
| 150 | extra | 0.5 | – | – | – | – | – | – |
| 150 | missing | 0.2 | – | – | – | – | – | – |
| 150 | missing | 0.5 | – | – | – | – | – | – |
| 150 | reversed | 0.2 | – | – | – | – | – | – |
| 150 | reversed | 0.5 | – | – | – | – | – | – |
