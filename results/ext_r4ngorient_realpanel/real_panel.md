# Panel thật 14 × 19: non-Gaussianity của phần dư cấu trúc (mô tả, không rule)

Sinh bởi experiments/ext/r4ngorient/real_panel.py. Cửa sổ 2020Q2..2024Q4, transform của signal_quality.py (18 dòng), lag_max 1, m = 17 dòng phần dư. Skeleton: 21 cạnh prior Paper 1. Kiểm tra chéo với candidate_quarterly_matrix_raw.csv: max |Δ| = 0.00e+00. MC: 10000 lần, seed 20261104.

## Nút real / derived_from_real (macro, stock)

| node | nature | số term | fallback | skew | exkurt | JB | p tiệm cận | p MC | p MC Holm (14) | p SW | p SW Holm (14) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| macro_gdp_yoy_pct | real | 4 | - | -0.83 | +2.82 | 7.59 | 0.022 | 0.028 | 0.395 | 0.012 | 0.175 |
| macro_cpi_avg_pct | real | 6 | - | -0.86 | +1.92 | 4.70 | 0.095 | 0.079 | 0.896 | 0.143 | 1.000 |
| macro_policy_rate_pct | real | 11 | - | +0.17 | -0.01 | 0.08 | 0.959 | 0.936 | 1.000 | 0.821 | 1.000 |
| stock_adj_close_last_vnd | real | 3 | - | +0.42 | -0.95 | 1.14 | 0.566 | 0.365 | 1.000 | 0.266 | 1.000 |
| stock_return_qoq_pct | derived_from_real | 3 | - | +0.59 | -0.33 | 1.05 | 0.591 | 0.412 | 1.000 | 0.479 | 1.000 |
| stock_avg_daily_volume_cp | real | 5 | - | +0.76 | -0.42 | 1.76 | 0.415 | 0.231 | 1.000 | 0.122 | 1.000 |
| stock_avg_daily_trade_value_vnd | real | 5 | - | +0.71 | -0.18 | 1.43 | 0.489 | 0.297 | 1.000 | 0.327 | 1.000 |

## Nút banking simulated_calibrated / derived_from_simulated (phản ánh simulator, không phải thực tế)

| node | nature | số term | fallback | skew | exkurt | JB | p tiệm cận | p MC | p MC Holm (14) | p SW | p SW Holm (14) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bank_npl_ratio | simulated_calibrated | 9 | - | +0.61 | -0.10 | 1.06 | 0.588 | 0.495 | 1.000 | 0.528 | 1.000 |
| bank_car_ratio | simulated_calibrated | 5 | - | +0.84 | +1.37 | 3.35 | 0.187 | 0.076 | 0.896 | 0.301 | 1.000 |
| bank_nim_ratio | simulated_calibrated | 8 | - | +0.21 | +0.42 | 0.25 | 0.881 | 0.888 | 1.000 | 0.396 | 1.000 |
| bank_roe_ratio | simulated_calibrated | 8 | - | +0.93 | +0.96 | 3.09 | 0.214 | 0.075 | 0.896 | 0.126 | 1.000 |
| bank_ldr_ratio | simulated_calibrated | 3 | - | -0.31 | -0.52 | 0.46 | 0.793 | 0.747 | 1.000 | 0.465 | 1.000 |
| bank_provision_coverage_proxy_pct | derived_from_simulated | 4 | - | -0.77 | +1.99 | 4.50 | 0.105 | 0.052 | 0.682 | 0.145 | 1.000 |
| bank_z_score | derived_from_simulated | 3 | - | +0.68 | +0.25 | 1.34 | 0.513 | 0.226 | 1.000 | 0.141 | 1.000 |

## Power Monte Carlo của JB (mức 0.05, critical value MC), mẫu iid

| m | crit | laplace | t5 | skewexp | uniform | t10 |
|---|---|---|---|---|---|---|
| 17 | 3.51 | 0.275 | 0.202 | 0.558 | 0.004 | 0.114 |
| 18 | 3.51 | 0.282 | 0.216 | 0.583 | 0.004 | 0.123 |

Thêm (mô tả): gate của module mở ở 4/21 cạnh khai báo trên các phần dư này. Không đọc chiều từ panel thật: m = 17 quá nhỏ, và 7 nút banking là dữ liệu mô phỏng.
