# R3-4: feasible reversal comparators vs tolerant_v4 on reversal-affected pairs (ext_revlag3_probe)

Rows per method: {'oracle': 3522, 'tolerant_v4': 3522, 'tolerant_v4R': 3522, 'tolerant_v4Rmap': 3522}; paired rows (all methods ok): 3522.

## R1: coverage trên cặp affected (dC >= 0.05), method mới − v4 (ghép cặp)

| method | cell | T | n aff | cov v4 | cov new | cov oracle_cal | delta [CI] | p một phía | p Holm (4) | p Holm (8) | closed share [CI] | gap new − oracle_cal [CI] | đạt |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tolerant_v4R | reversed|0.2 | 80 | 87 | 0.770 | 0.759 | 0.931 | -0.011 [-0.063, +0.041] | 0.7545 | 1.0000 | 1.0000 | -0.07 [-0.72, 0.38] | -0.172 [-0.315, -0.030] | no |
| tolerant_v4R | reversed|0.2 | 150 | 87 | 0.862 | 0.793 | 0.954 | -0.069 [-0.134, -0.011] | 0.9940 | 1.0000 | 1.0000 | -0.75 [-6.00, 2.50] | -0.161 [-0.316, -0.038] | no |
| tolerant_v4R | reversed|0.2 | 40 | 87 | 0.816 | 0.862 | 0.954 | +0.046 [-0.021, +0.116] | 0.1355 | - | - | 0.33 [-0.25, 0.64] | -0.092 [-0.154, -0.041] | (T40, báo) |
| tolerant_v4R | reversed|0.5 | 80 | 207 | 0.865 | 0.826 | 0.937 | -0.039 [-0.102, +0.006] | 0.9525 | 1.0000 | 1.0000 | -0.53 [-1.89, 0.12] | -0.111 [-0.201, -0.033] | no |
| tolerant_v4R | reversed|0.5 | 150 | 207 | 0.870 | 0.836 | 0.981 | -0.034 [-0.071, +0.000] | 0.9825 | 1.0000 | 1.0000 | -0.30 [-1.00, 0.00] | -0.145 [-0.238, -0.061] | no |
| tolerant_v4R | reversed|0.5 | 40 | 207 | 0.850 | 0.874 | 0.942 | +0.024 [-0.031, +0.074] | 0.2240 | - | - | 0.26 [-0.53, 0.78] | -0.068 [-0.138, -0.013] | (T40, báo) |
| tolerant_v4Rmap | reversed|0.2 | 80 | 87 | 0.770 | 0.770 | 0.931 | +0.000 [-0.053, +0.043] | 0.6115 | 1.0000 | 1.0000 | 0.00 [-0.67, 0.45] | -0.161 [-0.304, -0.029] | no |
| tolerant_v4Rmap | reversed|0.2 | 150 | 87 | 0.862 | 0.759 | 0.954 | -0.103 [-0.215, -0.020] | 1.0000 | 1.0000 | 1.0000 | -1.12 [-9.00, 4.00] | -0.195 [-0.338, -0.061] | no |
| tolerant_v4Rmap | reversed|0.2 | 40 | 87 | 0.816 | 0.828 | 0.954 | +0.011 [-0.056, +0.062] | 0.4295 | - | - | 0.08 [-0.57, 0.42] | -0.126 [-0.220, -0.052] | (T40, báo) |
| tolerant_v4Rmap | reversed|0.5 | 80 | 207 | 0.865 | 0.821 | 0.937 | -0.043 [-0.101, +0.010] | 0.9525 | 1.0000 | 1.0000 | -0.60 [-2.20, 0.18] | -0.116 [-0.200, -0.037] | no |
| tolerant_v4Rmap | reversed|0.5 | 150 | 207 | 0.870 | 0.807 | 0.981 | -0.063 [-0.139, +0.010] | 0.9600 | 1.0000 | 1.0000 | -0.57 [-2.21, 0.08] | -0.174 [-0.274, -0.072] | no |
| tolerant_v4Rmap | reversed|0.5 | 40 | 207 | 0.850 | 0.865 | 0.942 | +0.014 [-0.055, +0.085] | 0.4025 | - | - | 0.16 [-1.11, 0.72] | -0.077 [-0.151, -0.020] | (T40, báo) |

## R2: không làm tệ (mọi cặp non-null của cell reversed)

| method | cell | T | n | cov v4 | cov new | IS v4 | IS new | ratio | R2a (≤1.05) | R2b (cov ≥ 0.90, T≥80) | IS delta [CI] |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tolerant_v4R | reversed|0.2 | 40 | 587 | 0.923 | 0.940 | 4.469 | 4.427 | 0.991 | yes | - | -0.042 [-0.202, +0.109] |
| tolerant_v4R | reversed|0.2 | 80 | 587 | 0.939 | 0.922 | 2.752 | 2.823 | 1.026 | yes | yes | +0.071 [-0.148, +0.338] |
| tolerant_v4R | reversed|0.2 | 150 | 587 | 0.968 | 0.937 | 1.957 | 1.858 | 0.950 | yes | yes | -0.098 [-0.196, +0.014] |
| tolerant_v4R | reversed|0.5 | 40 | 587 | 0.906 | 0.917 | 4.589 | 4.792 | 1.044 | yes | - | +0.203 [-0.117, +0.592] |
| tolerant_v4R | reversed|0.5 | 80 | 587 | 0.932 | 0.906 | 2.950 | 3.113 | 1.055 | NO | yes | +0.163 [-0.189, +0.664] |
| tolerant_v4R | reversed|0.5 | 150 | 587 | 0.937 | 0.911 | 2.183 | 2.127 | 0.974 | yes | yes | -0.057 [-0.266, +0.265] |
| tolerant_v4Rmap | reversed|0.2 | 40 | 587 | 0.923 | 0.906 | 4.469 | 4.825 | 1.080 | NO | - | +0.356 [-0.023, +0.795] |
| tolerant_v4Rmap | reversed|0.2 | 80 | 587 | 0.939 | 0.918 | 2.752 | 2.915 | 1.059 | NO | yes | +0.163 [-0.146, +0.557] |
| tolerant_v4Rmap | reversed|0.2 | 150 | 587 | 0.968 | 0.932 | 1.957 | 2.100 | 1.073 | NO | yes | +0.144 [-0.158, +0.564] |
| tolerant_v4Rmap | reversed|0.5 | 40 | 587 | 0.906 | 0.898 | 4.589 | 5.392 | 1.175 | NO | - | +0.804 [+0.309, +1.406] |
| tolerant_v4Rmap | reversed|0.5 | 80 | 587 | 0.932 | 0.899 | 2.950 | 3.553 | 1.204 | NO | NO | +0.603 [-0.065, +1.525] |
| tolerant_v4Rmap | reversed|0.5 | 150 | 587 | 0.937 | 0.910 | 2.183 | 2.545 | 1.165 | NO | yes | +0.361 [-0.094, +0.881] |

## Verdict theo rule ghi trước

- **tolerant_v4R**: R1 0/4 cell (Holm 4: 0/4; Holm 8 qua hai method: 0/4); R2a KHÔNG đạt; R2b đạt; IS tệ hơn có ý nghĩa sau Holm (6 cell): 0/6. Câu trả lời: **KHÔNG GIẢM**. Version: **LOẠI**.
- **tolerant_v4Rmap**: R1 0/4 cell (Holm 4: 0/4; Holm 8 qua hai method: 0/4); R2a KHÔNG đạt; R2b KHÔNG đạt; IS tệ hơn có ý nghĩa sau Holm (6 cell): 0/6. Câu trả lời: **KHÔNG GIẢM**. Version: **LOẠI**.

## Mô tả (không quyết định verdict)

Cặp affected (theta 0.05): median |C − C_true| và median width.

| cell | T | n | err v4 | err tolerant_v4R | err tolerant_v4Rmap | err oracle | width v4 | width tolerant_v4R | width tolerant_v4Rmap | cov oracle raw |
|---|---|---|---|---|---|---|---|---|---|---|
| reversed|0.2 | 40 | 87 | 0.690 | 0.674 | 0.597 | 0.330 | 2.817 | 2.923 | 3.029 | 0.874 |
| reversed|0.2 | 80 | 87 | 0.485 | 0.528 | 0.480 | 0.225 | 2.027 | 1.802 | 1.834 | 0.874 |
| reversed|0.2 | 150 | 87 | 0.498 | 0.358 | 0.265 | 0.118 | 1.622 | 1.376 | 1.270 | 0.920 |
| reversed|0.5 | 40 | 207 | 0.651 | 0.668 | 0.564 | 0.307 | 2.996 | 3.059 | 2.958 | 0.865 |
| reversed|0.5 | 80 | 207 | 0.469 | 0.433 | 0.356 | 0.210 | 2.148 | 1.953 | 1.912 | 0.889 |
| reversed|0.5 | 150 | 207 | 0.415 | 0.337 | 0.295 | 0.138 | 1.719 | 1.420 | 1.422 | 0.952 |

Sensitivity theta (delta coverage new − v4 trên cặp affected, T 80/150):

| method | theta | cell | T | n | delta [CI] |
|---|---|---|---|---|---|
| tolerant_v4R | 0.02 | reversed|0.2 | 80 | 87 | -0.011 [-0.063, +0.041] |
| tolerant_v4R | 0.02 | reversed|0.2 | 150 | 87 | -0.069 [-0.134, -0.011] |
| tolerant_v4R | 0.02 | reversed|0.5 | 80 | 208 | -0.038 [-0.101, +0.005] |
| tolerant_v4R | 0.02 | reversed|0.5 | 150 | 208 | -0.034 [-0.071, +0.000] |
| tolerant_v4R | 0.1 | reversed|0.2 | 80 | 87 | -0.011 [-0.063, +0.041] |
| tolerant_v4R | 0.1 | reversed|0.2 | 150 | 87 | -0.069 [-0.134, -0.011] |
| tolerant_v4R | 0.1 | reversed|0.5 | 80 | 207 | -0.039 [-0.102, +0.006] |
| tolerant_v4R | 0.1 | reversed|0.5 | 150 | 207 | -0.034 [-0.071, +0.000] |
| tolerant_v4Rmap | 0.02 | reversed|0.2 | 80 | 87 | +0.000 [-0.053, +0.043] |
| tolerant_v4Rmap | 0.02 | reversed|0.2 | 150 | 87 | -0.103 [-0.215, -0.020] |
| tolerant_v4Rmap | 0.02 | reversed|0.5 | 80 | 208 | -0.043 [-0.100, +0.010] |
| tolerant_v4Rmap | 0.02 | reversed|0.5 | 150 | 208 | -0.062 [-0.137, +0.010] |
| tolerant_v4Rmap | 0.1 | reversed|0.2 | 80 | 87 | +0.000 [-0.053, +0.043] |
| tolerant_v4Rmap | 0.1 | reversed|0.2 | 150 | 87 | -0.103 [-0.215, -0.020] |
| tolerant_v4Rmap | 0.1 | reversed|0.5 | 80 | 207 | -0.043 [-0.101, +0.010] |
| tolerant_v4Rmap | 0.1 | reversed|0.5 | 150 | 207 | -0.063 [-0.139, +0.010] |

Cặp unaffected (non-null, dC < 0.05): coverage.

| cell | T | n | cov v4 | cov tolerant_v4R | cov tolerant_v4Rmap | cov oracle_cal |
|---|---|---|---|---|---|---|
| reversed|0.2 | 40 | 500 | 0.942 | 0.954 | 0.920 | 0.944 |
| reversed|0.2 | 80 | 500 | 0.968 | 0.950 | 0.944 | 0.970 |
| reversed|0.2 | 150 | 500 | 0.986 | 0.962 | 0.962 | 0.980 |
| reversed|0.5 | 40 | 380 | 0.937 | 0.939 | 0.916 | 0.947 |
| reversed|0.5 | 80 | 380 | 0.968 | 0.950 | 0.942 | 0.979 |
| reversed|0.5 | 150 | 380 | 0.974 | 0.953 | 0.966 | 0.974 |
