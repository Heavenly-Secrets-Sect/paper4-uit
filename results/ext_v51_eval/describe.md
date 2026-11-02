# ext_v51_eval: descriptive extras (experiments/ext/v51/describe_eval.py)

## Missing cells: duplicated lag terms removed on the data fit / summed over all bootstrap draws, opened pairs (data / mean per draw)

| T | cell | dup terms data | dup terms total | n_open | n_open per draw |
|---|---|---|---|---|---|
| 40 | missing-0.2 | 3.1 | 1504 (runs with any: 1.00) | 13.0 | 22.7 |
| 40 | missing-0.5 | 8.7 | 3152 (runs with any: 1.00) | 33.2 | 38.9 |
| 80 | missing-0.2 | 5.2 | 2386 (runs with any: 1.00) | 14.2 | 23.7 |
| 80 | missing-0.5 | 13.7 | 4956 (runs with any: 1.00) | 33.2 | 39.0 |
| 150 | missing-0.2 | 6.4 | 2619 (runs with any: 1.00) | 16.3 | 26.5 |
| 150 | missing-0.5 | 16.7 | 5993 (runs with any: 1.00) | 35.6 | 43.3 |

## Null-pair interval score (iscore_null_mean), mean over runs

| T | cell | v4 | v5_1 |
|---|---|---|---|
| 40 | none-0.0 | 1.840 | 1.732 |
| 40 | extra-0.2 | 1.908 | 1.909 |
| 40 | extra-0.5 | 2.248 | 2.249 |
| 40 | missing-0.2 | 4.777 | 2.388 |
| 40 | missing-0.5 | 4.835 | 2.839 |
| 40 | reversed-0.2 | 1.881 | 1.894 |
| 40 | reversed-0.5 | 1.943 | 1.921 |
| 80 | none-0.0 | 0.847 | 0.841 |
| 80 | extra-0.2 | 0.950 | 0.899 |
| 80 | extra-0.5 | 1.123 | 1.057 |
| 80 | missing-0.2 | 2.027 | 1.445 |
| 80 | missing-0.5 | 2.077 | 1.623 |
| 80 | reversed-0.2 | 0.938 | 0.905 |
| 80 | reversed-0.5 | 0.941 | 0.911 |
| 150 | none-0.0 | 0.552 | 0.552 |
| 150 | extra-0.2 | 0.614 | 0.615 |
| 150 | extra-0.5 | 0.719 | 0.721 |
| 150 | missing-0.2 | 1.314 | 0.944 |
| 150 | missing-0.5 | 1.360 | 1.078 |
| 150 | reversed-0.2 | 0.642 | 0.602 |
| 150 | reversed-0.5 | 0.653 | 0.610 |
