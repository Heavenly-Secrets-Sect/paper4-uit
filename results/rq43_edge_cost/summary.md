# RQ4.3: cost of one wrong edge, by role relative to the target pair

Point estimate (`plugin`) on a series of T = 2000, H = 4. Cost of a wrong edge for a target pair = |C_hat(damaged) - C_hat(true skeleton)| / |C_true|. Cells: median relative shift / share of pairs shifted by more than 20%.

| damage | edge lag | role | all | Erdos-Renyi | scale-free hub | development | confirmatory |
|---|---|---|---|---|---|---|---|
| missing | contemporaneous | on_path | 0.929 / 0.81 (n=1628) | 0.935 / 0.82 (n=1194) | 0.904 / 0.77 (n=434) | 0.925 / 0.81 (n=911) | 0.931 / 0.81 (n=717) |
| missing | contemporaneous | into_source | 0.097 / 0.19 (n=420) | 0.105 / 0.23 (n=328) | 0.075 / 0.08 (n=92) | 0.099 / 0.19 (n=242) | 0.095 / 0.20 (n=178) |
| missing | contemporaneous | into_target | 0.034 / 0.12 (n=938) | 0.032 / 0.11 (n=707) | 0.052 / 0.15 (n=231) | 0.042 / 0.14 (n=460) | 0.031 / 0.10 (n=478) |
| missing | contemporaneous | other | 0.000 / 0.00 (n=12159) | 0.000 / 0.00 (n=7690) | 0.001 / 0.00 (n=4469) | 0.000 / 0.00 (n=6380) | 0.000 / 0.00 (n=5779) |
| missing | lagged | on_path | 0.805 / 0.73 (n=3870) | 0.817 / 0.72 (n=2621) | 0.761 / 0.74 (n=1249) | 0.745 / 0.71 (n=1997) | 0.868 / 0.74 (n=1873) |
| missing | lagged | into_source | 0.074 / 0.16 (n=1127) | 0.089 / 0.20 (n=792) | 0.054 / 0.05 (n=335) | 0.078 / 0.17 (n=550) | 0.069 / 0.15 (n=577) |
| missing | lagged | into_target | 0.058 / 0.23 (n=2073) | 0.048 / 0.19 (n=1505) | 0.090 / 0.32 (n=568) | 0.058 / 0.23 (n=998) | 0.059 / 0.22 (n=1075) |
| missing | lagged | other | 0.000 / 0.01 (n=29004) | 0.000 / 0.01 (n=17104) | 0.001 / 0.00 (n=11900) | 0.000 / 0.01 (n=14607) | 0.000 / 0.01 (n=14397) |
| reversed | contemporaneous | on_path | 0.527 / 0.77 (n=1408) | 0.524 / 0.79 (n=1051) | 0.536 / 0.72 (n=357) | 0.517 / 0.78 (n=791) | 0.535 / 0.76 (n=617) |
| reversed | contemporaneous | into_source | 0.141 / 0.40 (n=391) | 0.105 / 0.35 (n=309) | 0.267 / 0.59 (n=82) | 0.139 / 0.37 (n=224) | 0.141 / 0.44 (n=167) |
| reversed | contemporaneous | into_target | 0.046 / 0.09 (n=475) | 0.046 / 0.08 (n=381) | 0.044 / 0.14 (n=94) | 0.044 / 0.10 (n=227) | 0.051 / 0.08 (n=248) |
| reversed | contemporaneous | other | 0.002 / 0.03 (n=9116) | 0.001 / 0.03 (n=5890) | 0.004 / 0.02 (n=3226) | 0.002 / 0.03 (n=4782) | 0.001 / 0.03 (n=4334) |

## Stability of the role map

- Spearman correlation of median cost by (damage, lag, role), development vs confirmatory topologies: 0.99 over 12 cells
- Erdos-Renyi vs scale-free hub: 0.97 over 12 cells
