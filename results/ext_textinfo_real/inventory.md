# ext_textinfo_real: side information the real case would provide (descriptive, no ground truth)

Core nodes: 14. Prior edges with both ends in the core: **21** (of 42). Core pairs outside the prior: **70**. Chunks: 278; relations: 124 (82 accepted, 42 rejected), 77 of them between two distinct core nodes.

## Doubt signals on the prior edges

| signal | edges |
|---|---|
| confidence < 0.6 | 12 |
| single distinct source | 12 |
| conflicted | 6 |
| >= 1 verifier-rejected relation on the pair | 11 |
| relation also extracted in the opposite direction | 4 |
| accepted instances with opposite signs | 3 |
| **any doubt signal** | **20 / 21** |
| no doubt signal | 1 |
| distinct composite doubt values (ties reduce ranking resolution) | 12 |

## Suspicion signals on core pairs outside the prior

| signal | pairs |
|---|---|
| co-mentioned in >= 1 chunk (stored `candidate_nodes`) | 19 |
| co-mentioned in >= 1 chunk (keyword lexicon) | 35 |
| **co-mentioned by either** | **41 / 70** |
| >= 1 relation extracted on the pair but rejected | 2 |
| >= 1 relation accepted on the pair but absent from the final prior | 1 |
| distinct composite suspicion values | 44 |

## Sign and lag hints (prior edges)

- Sign hint (positive/negative): 16 / 21 edges; the rest are `policy_shock` (a label, not a sign).
- Lag hint `immediate` on >= 1 accepted relation: 19 edges; `1_quarter`: 2 edges; everything else `unknown`. Lag hints are therefore almost uninformative.

## Mentions per core node (chunks, candidate_nodes or lexicon)

| node | chunks |
|---|---|
| bank_npl_ratio | 69 |
| bank_car_ratio | 25 |
| bank_nim_ratio | 58 |
| bank_roe_ratio | 37 |
| bank_ldr_ratio | 40 |
| bank_provision_coverage_proxy_pct | 33 |
| bank_z_score | 2 |
| macro_gdp_yoy_pct | 28 |
| macro_cpi_avg_pct | 22 |
| macro_policy_rate_pct | 80 |
| stock_adj_close_last_vnd | 18 |
| stock_return_qoq_pct | 23 |
| stock_avg_daily_volume_cp | 31 |
| stock_avg_daily_trade_value_vnd | 39 |

## Prior edges by doubt (highest first)

| edge | conf | sources | conflicted | rejected | reverse | sign | doubt |
|---|---|---|---|---|---|---|---|
| bank_nim_ratio->bank_car_ratio | 0.42 | 1 | False | 4 | 3 | positive | 2.08 |
| bank_ldr_ratio->macro_policy_rate_pct | 0.42 | 1 | False | 1 | 1 | positive | 1.83 |
| macro_policy_rate_pct->bank_nim_ratio | 0.7 | 4 | True | 3 | 1 | - | 1.8 |
| bank_npl_ratio->bank_provision_coverage_proxy_pct | 0.85 | 4 | True | 4 | 0 | negative | 1.4 |
| macro_cpi_avg_pct->stock_avg_daily_trade_value_vnd | 0.42 | 1 | False | 1 | 0 | negative | 1.33 |
| macro_cpi_avg_pct->stock_avg_daily_volume_cp | 0.42 | 1 | False | 1 | 0 | negative | 1.33 |
| macro_policy_rate_pct->stock_return_qoq_pct | 0.42 | 1 | False | 1 | 0 | - | 1.33 |
| bank_provision_coverage_proxy_pct->bank_roe_ratio | 0.7 | 2 | True | 1 | 0 | positive | 1.3 |
| macro_policy_rate_pct->stock_adj_close_last_vnd | 0.7 | 6 | True | 2 | 0 | negative | 1.3 |
| bank_nim_ratio->bank_npl_ratio | 0.42 | 1 | False | 0 | 0 | negative | 1.08 |
| bank_nim_ratio->bank_roe_ratio | 0.42 | 1 | False | 0 | 0 | positive | 1.08 |
| bank_roe_ratio->bank_z_score | 0.42 | 1 | False | 0 | 0 | positive | 1.08 |
| macro_cpi_avg_pct->bank_npl_ratio | 0.42 | 1 | False | 0 | 0 | positive | 1.08 |
| macro_gdp_yoy_pct->bank_car_ratio | 0.42 | 1 | False | 0 | 0 | negative | 1.08 |
| macro_policy_rate_pct->stock_avg_daily_volume_cp | 0.42 | 1 | False | 0 | 0 | negative | 1.08 |
| macro_policy_rate_pct->bank_npl_ratio | 0.7 | 3 | True | 1 | 0 | - | 1.05 |
| macro_policy_rate_pct->stock_avg_daily_trade_value_vnd | 0.7 | 4 | True | 0 | 0 | negative | 1.05 |
| macro_policy_rate_pct->macro_gdp_yoy_pct | 0.51 | 1 | False | 0 | 0 | - | 0.99 |
| macro_policy_rate_pct->macro_cpi_avg_pct | 0.85 | 2 | False | 0 | 4 | - | 0.65 |
| bank_ldr_ratio->bank_nim_ratio | 0.7 | 2 | False | 1 | 0 | negative | 0.55 |
| bank_npl_ratio->bank_roe_ratio | 0.7 | 2 | False | 0 | 0 | negative | 0.3 |

## Top 15 non-prior pairs by suspicion

| pair | co-mention (cand) | co-mention (lex) | rejected | accepted-not-in-prior | tf-idf | suspicion |
|---|---|---|---|---|---|---|
| bank_nim_ratio--bank_provision_coverage_proxy_pct | 4 | 12 | 0 | 1 | 0.178 | 4.07 |
| bank_npl_ratio--bank_ldr_ratio | 4 | 12 | 1 | 0 | 0.139 | 4.031 |
| bank_npl_ratio--bank_car_ratio | 8 | 15 | 0 | 0 | 0.269 | 3.853 |
| stock_avg_daily_volume_cp--stock_avg_daily_trade_value_vnd | 2 | 29 | 0 | 0 | 0.762 | 3.561 |
| bank_car_ratio--bank_roe_ratio | 4 | 12 | 0 | 0 | 0.316 | 3.208 |
| bank_roe_ratio--bank_ldr_ratio | 3 | 9 | 0 | 0 | 0.152 | 2.69 |
| bank_car_ratio--bank_provision_coverage_proxy_pct | 2 | 8 | 0 | 0 | 0.16 | 2.357 |
| stock_return_qoq_pct--stock_avg_daily_trade_value_vnd | 3 | 2 | 0 | 0 | 0.165 | 2.101 |
| bank_ldr_ratio--macro_gdp_yoy_pct | 4 | 1 | 0 | 0 | 0.108 | 2.064 |
| bank_car_ratio--bank_ldr_ratio | 1 | 9 | 0 | 0 | 0.144 | 1.989 |
| stock_adj_close_last_vnd--stock_return_qoq_pct | 0 | 6 | 0 | 0 | 0.655 | 1.628 |
| stock_adj_close_last_vnd--stock_avg_daily_trade_value_vnd | 1 | 3 | 0 | 0 | 0.135 | 1.521 |
| bank_ldr_ratio--stock_avg_daily_volume_cp | 0 | 6 | 0 | 0 | 0.21 | 1.183 |
| bank_roe_ratio--stock_return_qoq_pct | 2 | 0 | 0 | 0 | 0.058 | 1.157 |
| bank_roe_ratio--macro_gdp_yoy_pct | 2 | 0 | 0 | 0 | 0.056 | 1.154 |
