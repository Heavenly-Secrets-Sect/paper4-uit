# E1 on P4-H6 development: one global width factor

**Verdict: A single global width factor is sufficient (on P4-H6 development)**
V0 integrity: PASS {"r0": {"rows": 1260, "ok": 1260, "topologies": 20}, "r1": {"rows": 1260, "ok": 1260, "topologies": 20}, "r2": {"rows": 1260, "ok": 1260, "topologies": 20}, "r3": {"rows": 1260, "ok": 1260, "topologies": 20}}

- R1 pooled coverage (T in 80,150; 7 cells) 0.9586; R0 0.9566; difference +0.0020
- V1 R1 lower 97.5% bound 0.9477 (>= 0.90) and min cell 0.9340 (>= 0.85): PASS
- V2 difference +0.0020 (>= -0.01), lower 97.5% bound +0.0007 (>= -0.03): PASS
- V3 interval-score ratio R1/R0 1.0050, upper 97.5% bound 1.0094 (<= 1.10): PASS

## Descriptive (not part of the verdict)

| rule | pooled coverage T80,150 | pooled IS T80,150 | T40 coverage | T40 IS |
|---|---|---|---|---|
| R0 | 0.9566 | 2.1475 | 0.9321 | 4.5096 |
| R1 | 0.9586 | 2.1582 | 0.9271 | 4.5105 |
| R2 | 0.9584 | 2.1532 | 0.9336 | 4.5400 |
| R3 | 0.9609 | 2.1611 | 0.9300 | 4.5066 |

| T | cell | R0 | R1 | R2 | R3 |
|---|---|---|---|---|---|
| 40 | none 0.0 | 0.921 | 0.913 | 0.921 | 0.913 |
| 40 | extra 0.2 | 0.925 | 0.917 | 0.925 | 0.917 |
| 40 | extra 0.5 | 0.930 | 0.926 | 0.930 | 0.926 |
| 40 | missing 0.2 | 0.930 | 0.944 | 0.949 | 0.938 |
| 40 | missing 0.5 | 0.944 | 0.957 | 0.962 | 0.951 |
| 40 | reversed 0.2 | 0.938 | 0.921 | 0.930 | 0.934 |
| 40 | reversed 0.5 | 0.937 | 0.912 | 0.919 | 0.931 |
| 80 | none 0.0 | 0.946 | 0.941 | 0.946 | 0.941 |
| 80 | extra 0.2 | 0.932 | 0.941 | 0.946 | 0.941 |
| 80 | extra 0.5 | 0.938 | 0.948 | 0.951 | 0.948 |
| 80 | missing 0.2 | 0.966 | 0.962 | 0.966 | 0.957 |
| 80 | missing 0.5 | 0.960 | 0.954 | 0.960 | 0.946 |
| 80 | reversed 0.2 | 0.955 | 0.942 | 0.951 | 0.955 |
| 80 | reversed 0.5 | 0.951 | 0.934 | 0.943 | 0.951 |
| 150 | none 0.0 | 0.966 | 0.972 | 0.966 | 0.972 |
| 150 | extra 0.2 | 0.965 | 0.971 | 0.965 | 0.971 |
| 150 | extra 0.5 | 0.965 | 0.972 | 0.965 | 0.972 |
| 150 | missing 0.2 | 0.971 | 0.978 | 0.977 | 0.977 |
| 150 | missing 0.5 | 0.975 | 0.982 | 0.979 | 0.979 |
| 150 | reversed 0.2 | 0.957 | 0.967 | 0.957 | 0.977 |
| 150 | reversed 0.5 | 0.944 | 0.956 | 0.944 | 0.966 |
