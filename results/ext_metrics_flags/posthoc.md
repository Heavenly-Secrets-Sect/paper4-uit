# Post-hoc descriptives (not pre-registered)

## T in (80, 150)

AUROC of `1/width` (direction reversed post hoc): 0.632

Miss rate of the module by quintile of interval width:

| quintile | width range | miss rate | median abs C_true |
|---|---|---|---|
| 1 | 0.21-1.20 | 0.070 | 0.816 |
| 2 | 1.20-1.58 | 0.060 | 1.102 |
| 3 | 1.58-1.99 | 0.045 | 1.226 |
| 4 | 1.99-2.63 | 0.033 | 1.333 |
| 5 | 2.63-9.95 | 0.015 | 1.554 |

Miss rate by |C_true| tercile:

| tercile | abs C range | miss rate |
|---|---|---|
| 1 | 0.10-0.92 | 0.030 |
| 2 | 0.92-1.44 | 0.049 |
| 3 | 1.44-8.85 | 0.055 |

Share of all module misses by damage kind and role:

| kind | role | pairs | misses | miss rate | share of misses |
|---|---|---|---|---|---|
| none | untouched | 3708 | 191 | 0.052 | 0.165 |
| extra | damaged | 248 | 4 | 0.016 | 0.003 |
| extra | downstream | 2664 | 113 | 0.042 | 0.097 |
| extra | untouched | 4504 | 206 | 0.046 | 0.178 |
| missing | damaged | 1788 | 83 | 0.046 | 0.072 |
| missing | downstream | 2252 | 59 | 0.026 | 0.051 |
| missing | untouched | 3376 | 144 | 0.043 | 0.124 |
| reversed | damaged | 532 | 64 | 0.120 | 0.055 |
| reversed | downstream | 1110 | 120 | 0.108 | 0.104 |
| reversed | untouched | 5774 | 175 | 0.030 | 0.151 |

## T in (40,)

AUROC of `1/width` (direction reversed post hoc): 0.819

Miss rate of the module by quintile of interval width:

| quintile | width range | miss rate | median abs C_true |
|---|---|---|---|
| 1 | 0.22-2.25 | 0.190 | 0.894 |
| 2 | 2.25-3.14 | 0.072 | 1.142 |
| 3 | 3.14-4.31 | 0.025 | 1.271 |
| 4 | 4.31-6.21 | 0.015 | 1.354 |
| 5 | 6.21-30.99 | 0.007 | 1.356 |

Miss rate by |C_true| tercile:

| tercile | abs C range | miss rate |
|---|---|---|
| 1 | 0.10-0.92 | 0.035 |
| 2 | 0.92-1.44 | 0.060 |
| 3 | 1.44-8.85 | 0.090 |

Share of all module misses by damage kind and role:

| kind | role | pairs | misses | miss rate | share of misses |
|---|---|---|---|---|---|
| none | untouched | 1854 | 121 | 0.065 | 0.151 |
| extra | damaged | 124 | 7 | 0.056 | 0.009 |
| extra | downstream | 1332 | 107 | 0.080 | 0.134 |
| extra | untouched | 2252 | 200 | 0.089 | 0.250 |
| missing | damaged | 894 | 27 | 0.030 | 0.034 |
| missing | downstream | 1126 | 17 | 0.015 | 0.021 |
| missing | untouched | 1688 | 28 | 0.017 | 0.035 |
| reversed | damaged | 266 | 56 | 0.211 | 0.070 |
| reversed | downstream | 555 | 63 | 0.114 | 0.079 |
| reversed | untouched | 2887 | 174 | 0.060 | 0.217 |

