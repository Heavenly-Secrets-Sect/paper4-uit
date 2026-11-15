# E2 on P4-H6: frozen tolerant_v5_1 under non-Gaussian shocks

**Verdict: CONFIRMED on the sealed bank P4-H6**
V0 integrity: PASS {"gauss": {"rows": 1260, "ok": 1260, "need": 1260, "topologies": 20}, "ng_mix": {"rows": 1260, "ok": 1260, "need": 1260, "topologies": 20}, "ng_t10": {"rows": 1260, "ok": 1260, "need": 1260, "topologies": 20}}

## ng_mix
- pooled coverage (T in 80,150; 7 cells) 0.9538; gauss 0.9499; diff +0.0039
- V1 lower 97.5% bound 0.9479 (>= 0.90): PASS
- V2 min cell coverage 0.9207 (>= 0.85): PASS
- V3 diff +0.0039 (>= -0.03), lower 97.5% bound -0.0019 (>= -0.05): PASS
- verdict ng_mix: PASS

## ng_t10
- pooled coverage (T in 80,150; 7 cells) 0.9524; gauss 0.9499; diff +0.0024
- V1 lower 97.5% bound 0.9429 (>= 0.90): PASS
- V2 min cell coverage 0.9243 (>= 0.85): PASS
- V3 diff +0.0024 (>= -0.03), lower 97.5% bound -0.0065 (>= -0.05): PASS
- verdict ng_t10: PASS

## Descriptive: coverage per (T, cell) for every shock (not part of the verdict)

| T | cell | gauss | ng_mix | ng_t10 |
|---|---|---|---|---|
| 40 | none 0.0 | 0.917 | 0.896 | 0.916 |
| 40 | extra 0.2 | 0.926 | 0.905 | 0.923 |
| 40 | extra 0.5 | 0.927 | 0.920 | 0.927 |
| 40 | missing 0.2 | 0.920 | 0.925 | 0.915 |
| 40 | missing 0.5 | 0.947 | 0.937 | 0.930 |
| 40 | reversed 0.2 | 0.927 | 0.915 | 0.927 |
| 40 | reversed 0.5 | 0.917 | 0.904 | 0.912 |
| 80 | none 0.0 | 0.949 | 0.961 | 0.958 |
| 80 | extra 0.2 | 0.934 | 0.949 | 0.944 |
| 80 | extra 0.5 | 0.934 | 0.954 | 0.947 |
| 80 | missing 0.2 | 0.967 | 0.970 | 0.968 |
| 80 | missing 0.5 | 0.958 | 0.972 | 0.963 |
| 80 | reversed 0.2 | 0.944 | 0.951 | 0.951 |
| 80 | reversed 0.5 | 0.935 | 0.946 | 0.954 |
| 150 | none 0.0 | 0.956 | 0.951 | 0.955 |
| 150 | extra 0.2 | 0.958 | 0.954 | 0.954 |
| 150 | extra 0.5 | 0.961 | 0.955 | 0.958 |
| 150 | missing 0.2 | 0.963 | 0.964 | 0.964 |
| 150 | missing 0.5 | 0.965 | 0.965 | 0.961 |
| 150 | reversed 0.2 | 0.940 | 0.941 | 0.931 |
| 150 | reversed 0.5 | 0.934 | 0.921 | 0.924 |
