# RQ4.4 for the module (`tolerant_v4`): truth-free flags for interval misses

Pre-registered in docs/ext/metrics.md before the run. AUROC: higher signal = higher risk. 95% CIs: bootstrap over the 20 topologies (1000 resamples). Stratified AUROC: pair-weighted mean of AUROCs within (T, damage cell), over strata where the signal varies.

## miss, T in (80, 150)

Pairs: 25956; base rate: 0.045

| signal | defined | AUROC pooled [95% CI] | AUROC stratified [95% CI] | R1 verdict |
|---|---|---|---|---|
| rel_width | 1.00 | 0.660 [0.619, 0.702] | 0.656 [0.616, 0.695] (14 strata) | useful |
| width | 1.00 | 0.368 [0.326, 0.417] | 0.333 [0.289, 0.379] (14 strata) | inverse |
| zero_in | 1.00 | 0.623 [0.592, 0.655] | 0.608 [0.580, 0.638] (14 strata) | predictive |
| struct_sens | 1.00 | 0.496 [0.467, 0.528] | 0.538 [0.504, 0.571] (8 strata) | no |
| resid_lb | 1.00 | 0.453 [0.421, 0.485] | 0.452 [0.421, 0.483] (14 strata) | inverse |
| rx_pair | 1.00 | 0.514 [0.489, 0.538] | 0.497 [0.476, 0.518] (14 strata) | no |
| rx_end | 1.00 | 0.507 [0.481, 0.540] | 0.486 [0.466, 0.508] (14 strata) | no |
| coef_stab | 1.00 | 0.491 [0.464, 0.517] | 0.493 [0.466, 0.520] (14 strata) | no |
| lag_stab | 0.47 | 0.549 [0.493, 0.592] | 0.552 [0.506, 0.588] (14 strata) | no |
| n_repair | 1.00 | 0.479 [0.460, 0.504] | 0.467 [0.431, 0.504] (4 strata) | no |
| n_pool | 1.00 | 0.511 [0.492, 0.531] | 0.508 [0.457, 0.564] (4 strata) | no |
| n_resid_bh | 1.00 | 0.486 [0.459, 0.520] | 0.496 [0.474, 0.518] (14 strata) | no |
| combined (grouped 5-fold CV, out-of-fold) | 1.00 | 0.741 [0.702, 0.776] | 0.728 | R2: ΔAUROC vs rel_width = +0.081 [+0.044, +0.119] → adds information |

Standardised logistic weights fitted on all pairs (descriptive): intercept -3.48, log1p_rel_width +0.24, log1p_width -0.75, log1p_struct_sens +0.29, log1p_resid_lb -0.17, log1p_coef_stab -0.08, log1p_lag_stab +0.10, rx_pair -0.07, rx_end -0.06, zero_in +0.28, n_repair -0.09, n_pool +0.01, n_resid_bh +0.03, na_coef_stab +0.00, na_lag_stab +0.35, logT -0.38, stated_missing -0.11, stated_reversed -0.10, stated_extra -0.05

R3, flag `rel_width > 2`: flagged 0.429 of pairs; miss rate flagged 0.069 vs unflagged 0.026; ratio 2.60 [2.05, 3.38] → usable.

Conditional coverage of the module by quintile of rel_width:

| quintile | rel_width range | pairs | coverage | median width |
|---|---|---|---|---|
| 1 | 0.32–1.08 | 5191 | 0.975 | 1.377 |
| 2 | 1.08–1.50 | 5191 | 0.975 | 1.663 |
| 3 | 1.50–2.11 | 5191 | 0.969 | 1.858 |
| 4 | 2.11–3.55 | 5191 | 0.953 | 2.058 |
| 5 | 3.55–6724.97 | 5192 | 0.904 | 2.099 |

## large_err, T in (80, 150)

Pairs: 25956; base rate: 0.217

| signal | defined | AUROC pooled [95% CI] | AUROC stratified [95% CI] | R1 verdict |
|---|---|---|---|---|
| rel_width | 1.00 | 0.858 [0.844, 0.871] | 0.843 [0.828, 0.858] (14 strata) | useful |
| width | 1.00 | 0.584 [0.561, 0.606] | 0.513 [0.487, 0.538] (14 strata) | no |
| zero_in | 1.00 | 0.757 [0.748, 0.766] | 0.734 [0.721, 0.748] (14 strata) | useful |
| struct_sens | 1.00 | 0.572 [0.553, 0.590] | 0.498 [0.476, 0.517] (8 strata) | no |
| resid_lb | 1.00 | 0.513 [0.495, 0.531] | 0.497 [0.477, 0.519] (14 strata) | no |
| rx_pair | 1.00 | 0.579 [0.559, 0.599] | 0.560 [0.538, 0.582] (14 strata) | predictive |
| rx_end | 1.00 | 0.601 [0.586, 0.616] | 0.512 [0.499, 0.526] (14 strata) | no |
| coef_stab | 1.00 | 0.512 [0.498, 0.526] | 0.503 [0.489, 0.518] (14 strata) | no |
| lag_stab | 0.47 | 0.588 [0.560, 0.616] | 0.567 [0.530, 0.606] (14 strata) | predictive |
| n_repair | 1.00 | 0.562 [0.548, 0.577] | 0.515 [0.492, 0.537] (4 strata) | no |
| n_pool | 1.00 | 0.504 [0.494, 0.514] | 0.522 [0.482, 0.565] (4 strata) | no |
| n_resid_bh | 1.00 | 0.571 [0.551, 0.590] | 0.516 [0.501, 0.530] (14 strata) | predictive |
| combined (grouped 5-fold CV, out-of-fold) | 1.00 | 0.860 [0.844, 0.874] | 0.841 | R2: ΔAUROC vs rel_width = +0.002 [-0.001, +0.004] → no added information |

Standardised logistic weights fitted on all pairs (descriptive): intercept -1.63, log1p_rel_width +2.06, log1p_width -0.09, log1p_struct_sens +0.24, log1p_resid_lb +0.01, log1p_coef_stab +0.02, log1p_lag_stab +0.02, rx_pair +0.02, rx_end +0.02, zero_in +0.08, n_repair -0.26, n_pool -0.05, n_resid_bh +0.20, na_coef_stab +0.00, na_lag_stab -0.13, logT -0.14, stated_missing -0.10, stated_reversed -0.10, stated_extra +0.04

R3, flag `rel_width > 2`: flagged 0.429 of pairs; large_err rate flagged 0.424 vs unflagged 0.063; ratio 6.76 [6.05, 7.59] → usable.

## miss, T in (40,)

Pairs: 12978; base rate: 0.062

| signal | defined | AUROC pooled [95% CI] | AUROC stratified [95% CI] | R1 verdict |
|---|---|---|---|---|
| rel_width | 1.00 | 0.595 [0.569, 0.628] | 0.606 [0.578, 0.638] (7 strata) | predictive |
| width | 1.00 | 0.181 [0.150, 0.214] | 0.208 [0.173, 0.241] (7 strata) | inverse |
| zero_in | 1.00 | 0.537 [0.522, 0.550] | 0.539 [0.522, 0.555] (7 strata) | predictive |
| struct_sens | 1.00 | 0.426 [0.399, 0.458] | 0.604 [0.570, 0.646] (4 strata) | inverse |
| resid_lb | 1.00 | 0.455 [0.399, 0.527] | 0.500 [0.447, 0.565] (7 strata) | no |
| rx_pair | 1.00 | 0.497 [0.476, 0.521] | 0.506 [0.478, 0.536] (7 strata) | no |
| rx_end | 1.00 | 0.390 [0.350, 0.441] | 0.503 [0.466, 0.547] (7 strata) | inverse |
| coef_stab | 0.43 | 0.505 [0.457, 0.554] | 0.499 [0.448, 0.548] (5 strata) | no |
| lag_stab | 0.07 | 0.647 [0.495, 0.750] | 0.723 [0.488, 0.786] (5 strata) | no |
| n_repair | 1.00 | 0.396 [0.380, 0.419] | – | inverse |
| n_pool | 1.00 | 0.546 [0.525, 0.570] | 0.519 [0.454, 0.583] (2 strata) | no |
| n_resid_bh | 1.00 | 0.387 [0.352, 0.430] | 0.489 [0.458, 0.525] (7 strata) | inverse |
| combined (grouped 5-fold CV, out-of-fold) | 1.00 | 0.847 [0.815, 0.878] | 0.824 | R2: ΔAUROC vs rel_width = +0.252 [+0.200, +0.296] → adds information |

Standardised logistic weights fitted on all pairs (descriptive): intercept -3.89, log1p_rel_width +0.27, log1p_width -1.84, log1p_struct_sens +0.42, log1p_resid_lb +0.03, log1p_coef_stab +0.05, log1p_lag_stab +0.14, rx_pair -0.10, rx_end +0.05, zero_in +0.36, n_repair +0.06, n_pool +0.17, n_resid_bh +0.49, na_coef_stab +0.54, na_lag_stab +0.34, logT +0.00, stated_missing -0.95, stated_reversed -0.21, stated_extra +0.08

R3, flag `rel_width > 2`: flagged 0.855 of pairs; miss rate flagged 0.065 vs unflagged 0.040; ratio 1.64 [1.19, 2.45] → not usable.

Conditional coverage of the module by quintile of rel_width:

| quintile | rel_width range | pairs | coverage | median width |
|---|---|---|---|---|
| 1 | 0.82–2.23 | 2596 | 0.962 | 2.922 |
| 2 | 2.23–3.24 | 2595 | 0.956 | 3.359 |
| 3 | 3.24–5.05 | 2596 | 0.941 | 3.891 |
| 4 | 5.05–10.80 | 2595 | 0.919 | 4.436 |
| 5 | 10.80–21502.22 | 2596 | 0.914 | 4.428 |

## large_err, T in (40,)

Pairs: 12978; base rate: 0.508

| signal | defined | AUROC pooled [95% CI] | AUROC stratified [95% CI] | R1 verdict |
|---|---|---|---|---|
| rel_width | 1.00 | 0.772 [0.747, 0.796] | 0.751 [0.726, 0.775] (7 strata) | useful |
| width | 1.00 | 0.565 [0.538, 0.590] | 0.500 [0.471, 0.528] (7 strata) | no |
| zero_in | 1.00 | 0.579 [0.562, 0.593] | 0.565 [0.550, 0.578] (7 strata) | predictive |
| struct_sens | 1.00 | 0.580 [0.564, 0.596] | 0.511 [0.489, 0.534] (4 strata) | no |
| resid_lb | 1.00 | 0.533 [0.513, 0.551] | 0.486 [0.465, 0.502] (7 strata) | no |
| rx_pair | 1.00 | 0.532 [0.504, 0.560] | 0.528 [0.506, 0.551] (7 strata) | predictive |
| rx_end | 1.00 | 0.577 [0.557, 0.597] | 0.488 [0.472, 0.503] (7 strata) | no |
| coef_stab | 0.43 | 0.498 [0.468, 0.532] | 0.496 [0.466, 0.532] (5 strata) | no |
| lag_stab | 0.07 | 0.555 [0.505, 0.611] | 0.560 [0.509, 0.616] (5 strata) | predictive |
| n_repair | 1.00 | 0.585 [0.571, 0.598] | – | no |
| n_pool | 1.00 | 0.478 [0.470, 0.485] | 0.502 [0.476, 0.525] (2 strata) | inverse |
| n_resid_bh | 1.00 | 0.579 [0.562, 0.597] | 0.493 [0.476, 0.508] (7 strata) | no |
| combined (grouped 5-fold CV, out-of-fold) | 1.00 | 0.788 [0.762, 0.813] | 0.764 | R2: ΔAUROC vs rel_width = +0.016 [+0.010, +0.022] → adds information |

Standardised logistic weights fitted on all pairs (descriptive): intercept +0.29, log1p_rel_width +1.85, log1p_width -0.01, log1p_struct_sens +0.53, log1p_resid_lb -0.07, log1p_coef_stab +0.01, log1p_lag_stab +0.05, rx_pair +0.02, rx_end -0.22, zero_in -0.07, n_repair -0.12, n_pool -0.06, n_resid_bh +0.07, na_coef_stab +0.11, na_lag_stab +0.01, logT -0.00, stated_missing -0.16, stated_reversed -0.17, stated_extra +0.05

R3, flag `rel_width > 2`: flagged 0.855 of pairs; large_err rate flagged 0.553 vs unflagged 0.238; ratio 2.32 [1.96, 2.76] → usable.

