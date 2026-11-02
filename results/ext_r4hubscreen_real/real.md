# Real panel 14 x 19 (z-scored), prior 21 edges: descriptive run of v5_1 and the candidate

Node degrees in the prior: {'npl_ratio': 5, 'car_ratio': 2, 'nim_ratio': 5, 'roe_ratio': 4, 'ldr_ratio': 2, 'provision_cove': 2, 'z_score': 1, 'gdp_yoy_pct': 2, 'cpi_avg_pct': 4, 'policy_rate_pc': 9, 'adj_close_last': 1, 'return_qoq_pct': 1, 'avg_daily_volu': 2, 'avg_daily_trad': 2}

| lag_max | stated | max |base terms| (m) | v5_1 status | candidate status | reduced (data eq / draws) | reduced nodes | median width v5_1 | median width cand | share excl. 0 v5_1 | share excl. 0 cand |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | none | 11 (18) | ok | ok | 0 (0 / 0) | – | 2.42 | 2.42 | 0.01 | 0.01 |
| 1 | missing | 11 (18) | ok | ok | 0 (0 / 0) | – | 4.68 | 4.68 | 0.00 | 0.00 |
| 1 | extra | 11 (18) | ok | ok | 0 (0 / 0) | – | 2.15 | 2.15 | 0.02 | 0.02 |
| 1 | reversed | 11 (18) | ok | ok | 0 (0 / 0) | – | 2.20 | 2.20 | 0.01 | 0.01 |
| 2 | none | 21 (17) | underdetermined | ok | 1 (1 / 199) | macro_policy_rate_pct | – | 2.84 | – | 0.00 |
| 2 | missing | 21 (17) | underdetermined | ok | 1 (13 / 199) | bank_npl_ratio, bank_nim_ratio, bank_roe_ratio, macro_cpi_avg_pct, macro_policy_rate_pct, stock_avg_daily_volume_cp | – | 7.30 | – | 0.01 |
| 2 | extra | 21 (17) | underdetermined | ok | 1 (1 / 199) | macro_policy_rate_pct | – | 4.77 | – | 0.00 |
| 2 | reversed | 21 (17) | underdetermined | ok | 1 (1 / 199) | macro_policy_rate_pct | – | 2.12 | – | 0.01 |

Descriptive only: no ground truth; the banking nodes are simulated_calibrated (core14_provenance.json).
