# RQ4.4: truth-free reliability flags for the module (`tolerant_v3_cal`)

Outcome `unreliable`: estimate off by > 50% of |C_true| or interval misses C_true. AUROC on confirmatory topologies; the combined flag is a logistic model fitted on development topologies.

Base rate of unreliable pairs (test): 0.231 over 11950 pairs.

| T | damage | rate | base rate | rel_width | struct_sens | method_sens | zero_in | combined |
|---|---|---|---|---|---|---|---|---|
| all | all | all | 0.231 | 0.834 | 0.548 | 0.504 | 0.712 | 0.834 |
| 80 | none | 0.0 | 0.203 | 0.744 | 0.500 | 0.511 | 0.649 | 0.743 |
| 80 | missing | 0.2 | 0.324 | 0.796 | 0.571 | 0.484 | 0.600 | 0.803 |
| 80 | missing | 0.5 | 0.326 | 0.820 | 0.368 | 0.426 | 0.586 | 0.824 |
| 80 | reversed | 0.2 | 0.247 | 0.803 | 0.497 | 0.496 | 0.665 | 0.801 |
| 80 | reversed | 0.5 | 0.269 | 0.848 | 0.526 | 0.487 | 0.669 | 0.847 |
| 150 | none | 0.0 | 0.115 | 0.771 | 0.500 | 0.532 | 0.716 | 0.770 |
| 150 | missing | 0.2 | 0.203 | 0.846 | 0.509 | 0.502 | 0.753 | 0.853 |
| 150 | missing | 0.5 | 0.232 | 0.857 | 0.340 | 0.400 | 0.752 | 0.860 |
| 150 | reversed | 0.2 | 0.186 | 0.867 | 0.568 | 0.542 | 0.777 | 0.866 |
| 150 | reversed | 0.5 | 0.202 | 0.862 | 0.599 | 0.540 | 0.759 | 0.862 |

Logistic weights (intercept, log1p rel_width, log1p struct_sens, log1p method_sens, zero_in): [-4.895, 2.609, 1.054, -0.292, -0.022]
