# ext_textinfo verdict (pre-registered rule, docs/ext/textinfo.md section 5)

Inputs: /Users/kietnt/Desktop/Workspace/Paper4_UIT/results/ext_textinfo_t80, /Users/kietnt/Desktop/Workspace/Paper4_UIT/results/ext_textinfo_t150. Reference `tolerant_v4`. Paired CIs resample topologies (1000 draws).

### `textinfo`

Condition 1 (a = 0.9): cells with upper CI < 0 and coverage >= 0.90.

| T | damage | rate | cov | IS | v4 IS | diff vs v4 [95% CI] | win |
|---|---|---|---|---|---|---|---|
| 80 | extra | 0.2 | 0.946 | 2.528 | 2.528 | +0.000 [+0.000, +0.000] | no |
| 80 | extra | 0.5 | 0.948 | 2.647 | 2.647 | +0.000 [+0.000, +0.000] | no |
| 80 | missing | 0.2 | 0.944 | 3.002 | 3.277 | -0.275 [-0.406, -0.132] | yes |
| 80 | missing | 0.5 | 0.958 | 3.399 | 3.370 | +0.029 [-0.109, +0.194] | no |
| 80 | reversed | 0.2 | 0.933 | 2.737 | 2.791 | -0.054 [-0.093, -0.008] | yes |
| 80 | reversed | 0.5 | 0.917 | 2.944 | 2.968 | -0.025 [-0.096, +0.046] | no |
| 150 | extra | 0.2 | 0.965 | 1.581 | 1.581 | +0.000 [+0.000, +0.000] | no |
| 150 | extra | 0.5 | 0.967 | 1.657 | 1.657 | +0.000 [+0.000, +0.000] | no |
| 150 | missing | 0.2 | 0.965 | 1.823 | 2.057 | -0.234 [-0.308, -0.157] | yes |
| 150 | missing | 0.5 | 0.971 | 2.124 | 2.215 | -0.092 [-0.147, -0.034] | yes |
| 150 | reversed | 0.2 | 0.975 | 1.861 | 1.894 | -0.033 [-0.065, +0.002] | no |
| 150 | reversed | 0.5 | 0.966 | 1.985 | 2.017 | -0.032 [-0.084, +0.013] | no |

Wins: **4 / 12** (need >= 6) -> condition 1 NOT met.

Condition 2 (a = 0.5): IS ratio to v4 in every cell <= 1.05.

| T | damage | rate | IS a=0.5 | v4 IS | ratio | ok |
|---|---|---|---|---|---|---|
| 80 | none | 0.0 | 2.502 | 2.502 | 1.000 | yes |
| 80 | extra | 0.2 | 2.528 | 2.528 | 1.000 | yes |
| 80 | extra | 0.5 | 2.647 | 2.647 | 1.000 | yes |
| 80 | missing | 0.2 | 3.259 | 3.277 | 0.994 | yes |
| 80 | missing | 0.5 | 3.406 | 3.370 | 1.011 | yes |
| 80 | reversed | 0.2 | 2.795 | 2.791 | 1.001 | yes |
| 80 | reversed | 0.5 | 3.015 | 2.968 | 1.016 | yes |
| 150 | none | 0.0 | 1.564 | 1.564 | 1.000 | yes |
| 150 | extra | 0.2 | 1.581 | 1.581 | 1.000 | yes |
| 150 | extra | 0.5 | 1.657 | 1.657 | 1.000 | yes |
| 150 | missing | 0.2 | 1.893 | 2.057 | 0.920 | yes |
| 150 | missing | 0.5 | 2.123 | 2.215 | 0.958 | yes |
| 150 | reversed | 0.2 | 1.894 | 1.894 | 1.000 | yes |
| 150 | reversed | 0.5 | 2.031 | 2.017 | 1.007 | yes |

Condition 2 MET.

**Verdict for `textinfo`: REJECTED.**

### `textinfo_all`

Condition 1 (a = 0.9): cells with upper CI < 0 and coverage >= 0.90.

| T | damage | rate | cov | IS | v4 IS | diff vs v4 [95% CI] | win |
|---|---|---|---|---|---|---|---|
| 80 | extra | 0.2 | 0.946 | 2.528 | 2.528 | +0.000 [+0.000, +0.000] | no |
| 80 | extra | 0.5 | 0.948 | 2.647 | 2.647 | +0.000 [+0.000, +0.000] | no |
| 80 | missing | 0.2 | 0.957 | 3.276 | 3.277 | -0.001 [-0.019, +0.026] | no |
| 80 | missing | 0.5 | 0.960 | 3.365 | 3.370 | -0.005 [-0.041, +0.027] | no |
| 80 | reversed | 0.2 | 0.933 | 2.737 | 2.791 | -0.054 [-0.093, -0.008] | yes |
| 80 | reversed | 0.5 | 0.917 | 2.944 | 2.968 | -0.025 [-0.096, +0.046] | no |
| 150 | extra | 0.2 | 0.965 | 1.581 | 1.581 | +0.000 [+0.000, +0.000] | no |
| 150 | extra | 0.5 | 0.967 | 1.657 | 1.657 | +0.000 [+0.000, +0.000] | no |
| 150 | missing | 0.2 | 0.968 | 2.053 | 2.057 | -0.003 [-0.008, -0.000] | yes |
| 150 | missing | 0.5 | 0.965 | 2.212 | 2.215 | -0.003 [-0.025, +0.017] | no |
| 150 | reversed | 0.2 | 0.975 | 1.861 | 1.894 | -0.033 [-0.065, +0.002] | no |
| 150 | reversed | 0.5 | 0.966 | 1.985 | 2.017 | -0.032 [-0.084, +0.013] | no |

Wins: **2 / 12** (need >= 6) -> condition 1 NOT met.

Condition 2 (a = 0.5): IS ratio to v4 in every cell <= 1.05.

| T | damage | rate | IS a=0.5 | v4 IS | ratio | ok |
|---|---|---|---|---|---|---|
| 80 | none | 0.0 | 2.502 | 2.502 | 1.000 | yes |
| 80 | extra | 0.2 | 2.528 | 2.528 | 1.000 | yes |
| 80 | extra | 0.5 | 2.647 | 2.647 | 1.000 | yes |
| 80 | missing | 0.2 | 3.274 | 3.277 | 0.999 | yes |
| 80 | missing | 0.5 | 3.375 | 3.370 | 1.002 | yes |
| 80 | reversed | 0.2 | 2.795 | 2.791 | 1.001 | yes |
| 80 | reversed | 0.5 | 3.015 | 2.968 | 1.016 | yes |
| 150 | none | 0.0 | 1.564 | 1.564 | 1.000 | yes |
| 150 | extra | 0.2 | 1.581 | 1.581 | 1.000 | yes |
| 150 | extra | 0.5 | 1.657 | 1.657 | 1.000 | yes |
| 150 | missing | 0.2 | 2.054 | 2.057 | 0.999 | yes |
| 150 | missing | 0.5 | 2.221 | 2.215 | 1.003 | yes |
| 150 | reversed | 0.2 | 1.894 | 1.894 | 1.000 | yes |
| 150 | reversed | 0.5 | 2.031 | 2.017 | 1.007 | yes |

Condition 2 MET.

**Verdict for `textinfo_all`: REJECTED.**

## Descriptive (not part of the verdict)

### S1: text vs no text (`textinfo@a0.9` minus `textinfo_null`), missing and reversed cells

| T | damage | rate | diff [95% CI] |
|---|---|---|---|
| 80 | missing | 0.2 | -0.083 [-0.183, +0.010] |
| 80 | missing | 0.5 | +0.039 [-0.085, +0.215] |
| 80 | reversed | 0.2 | -0.039 [-0.071, -0.010] |
| 80 | reversed | 0.5 | -0.080 [-0.143, -0.025] |
| 150 | missing | 0.2 | -0.016 [-0.098, +0.042] |
| 150 | missing | 0.5 | -0.016 [-0.050, +0.020] |
| 150 | reversed | 0.2 | -0.032 [-0.046, -0.019] |
| 150 | reversed | 0.5 | -0.073 [-0.115, -0.034] |

Cells with upper CI < 0: 4 / 8.

### S2: mean IS difference vs v4 by text quality (coverage in brackets)

| T | damage | rate | method | a=0.5 | a=0.7 | a=0.9 | monotone |
|---|---|---|---|---|---|---|---|
| 80 | missing | 0.2 | textinfo | -0.019 (0.933) | -0.232 (0.942) | -0.275 (0.944) | yes |
| 80 | missing | 0.5 | textinfo | +0.036 (0.959) | +0.031 (0.961) | +0.029 (0.958) | yes |
| 80 | reversed | 0.2 | textinfo | +0.004 (0.927) | -0.022 (0.929) | -0.054 (0.933) | yes |
| 80 | reversed | 0.5 | textinfo | +0.047 (0.914) | +0.005 (0.915) | -0.025 (0.917) | yes |
| 150 | missing | 0.2 | textinfo | -0.164 (0.962) | -0.171 (0.962) | -0.234 (0.965) | yes |
| 150 | missing | 0.5 | textinfo | -0.092 (0.970) | -0.089 (0.970) | -0.092 (0.971) | no |
| 150 | reversed | 0.2 | textinfo | +0.000 (0.970) | -0.018 (0.971) | -0.033 (0.975) | yes |
| 150 | reversed | 0.5 | textinfo | +0.014 (0.960) | +0.004 (0.962) | -0.032 (0.966) | yes |
| 80 | missing | 0.2 | textinfo_all | -0.004 (0.958) | -0.001 (0.958) | -0.001 (0.957) | no |
| 80 | missing | 0.5 | textinfo_all | +0.005 (0.962) | +0.009 (0.960) | -0.005 (0.960) | no |
| 80 | reversed | 0.2 | textinfo_all | +0.004 (0.927) | -0.022 (0.929) | -0.054 (0.933) | yes |
| 80 | reversed | 0.5 | textinfo_all | +0.047 (0.914) | +0.005 (0.915) | -0.025 (0.917) | yes |
| 150 | missing | 0.2 | textinfo_all | -0.002 (0.968) | -0.003 (0.967) | -0.003 (0.968) | yes |
| 150 | missing | 0.5 | textinfo_all | +0.006 (0.962) | +0.006 (0.963) | -0.003 (0.965) | no |
| 150 | reversed | 0.2 | textinfo_all | +0.000 (0.970) | -0.018 (0.971) | -0.033 (0.975) | yes |
| 150 | reversed | 0.5 | textinfo_all | +0.014 (0.960) | +0.004 (0.962) | -0.032 (0.966) | yes |

### `textinfo_null` (targeted opening, no text) vs v4

| T | damage | rate | cov | diff vs v4 [95% CI] |
|---|---|---|---|---|
| 80 | missing | 0.2 | 0.935 | -0.192 [-0.349, -0.049] |
| 80 | missing | 0.5 | 0.963 | -0.010 [-0.105, +0.067] |
| 80 | reversed | 0.2 | 0.930 | -0.014 [-0.057, +0.028] |
| 80 | reversed | 0.5 | 0.913 | +0.055 [-0.012, +0.120] |
| 150 | missing | 0.2 | 0.966 | -0.218 [-0.310, -0.115] |
| 150 | missing | 0.5 | 0.967 | -0.076 [-0.116, -0.038] |
| 150 | reversed | 0.2 | 0.971 | -0.001 [-0.029, +0.032] |
| 150 | reversed | 0.5 | 0.958 | +0.041 [-0.002, +0.083] |
