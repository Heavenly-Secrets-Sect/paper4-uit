# Identity check tolerant_v5_1_hs vs tolerant_v5_1 (D-07H development, replicate 7, n_boot 99)

- unit test csis_reduce: {'cap_full': 15, 'kept_short': [(0, 1), (3, 1)], 'pass': True}
- runs: 128; without reduction: 112; identical among them: 112 -> **PASS**
- runs with reduction: 16; v5_1 failed among them: 3; hs failed overall: 0
- mean seconds per run: v5_1 0.19, hs 0.17

| lag | T | cell | runs | reduced | v5_1 ok | hs ok | identical (non-reduced) |
|---|---|---|---|---|---|---|---|
| 1 | 19 | extra-0.2 | 8 | 0 | 8 | 8 | 8/8 |
| 1 | 19 | missing-0.2 | 8 | 0 | 8 | 8 | 8/8 |
| 1 | 19 | none-0.0 | 8 | 0 | 8 | 8 | 8/8 |
| 1 | 19 | reversed-0.2 | 8 | 0 | 8 | 8 | 8/8 |
| 2 | 25 | extra-0.2 | 8 | 0 | 8 | 8 | 8/8 |
| 2 | 25 | missing-0.2 | 8 | 8 | 5 | 8 | 0/0 |
| 2 | 25 | none-0.0 | 8 | 0 | 8 | 8 | 8/8 |
| 2 | 25 | reversed-0.2 | 8 | 0 | 8 | 8 | 8/8 |
| 2 | 30 | extra-0.2 | 8 | 0 | 8 | 8 | 8/8 |
| 2 | 30 | missing-0.2 | 8 | 8 | 8 | 8 | 0/0 |
| 2 | 30 | none-0.0 | 8 | 0 | 8 | 8 | 8/8 |
| 2 | 30 | reversed-0.2 | 8 | 0 | 8 | 8 | 8/8 |
| 2 | 40 | extra-0.2 | 8 | 0 | 8 | 8 | 8/8 |
| 2 | 40 | missing-0.2 | 8 | 0 | 8 | 8 | 8/8 |
| 2 | 40 | none-0.0 | 8 | 0 | 8 | 8 | 8/8 |
| 2 | 40 | reversed-0.2 | 8 | 0 | 8 | 8 | 8/8 |
