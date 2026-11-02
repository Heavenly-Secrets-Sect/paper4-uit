# Skeptic re-check of revlag (b) and (c)

- validity oracle: rows r1 38934 r2 38934, same keys True, differing values 0
- validity tolerant_v4: rows r1 38934 r2 38934, same keys True, differing values 0

| cell | T | n kept damaged | hit v4 | hit v4L | delta |
|---|---|---|---|---|---|
| reversed|0.2 | 40 | 73 | 0.027 | 0.151 | +0.123 |
| reversed|0.2 | 80 | 73 | 0.027 | 0.110 | +0.082 |
| reversed|0.2 | 150 | 73 | 0.014 | 0.123 | +0.110 |
| reversed|0.5 | 40 | 193 | 0.016 | 0.259 | +0.244 |
| reversed|0.5 | 80 | 193 | 0.047 | 0.347 | +0.301 |
| reversed|0.5 | 150 | 193 | 0.052 | 0.321 | +0.269 |

reversed|0.2 T80 damaged pairs come from 20 of 20 topologies; pairs where v4L hits and v4 misses: 6, reverse: 0

| set | n | miss | AUROC p_hat | AUROC rel_width | flagged | miss flagged | miss unflagged | ratio |
|---|---|---|---|---|---|---|---|---|
| T80/150 | 26082 | 0.047 | 0.730 | 0.657 | 0.082 | 0.161 | 0.037 | 4.32 |
| T40 | 13041 | 0.072 | 0.824 | 0.590 | 0.193 | 0.246 | 0.031 | 7.95 |

stated (width_key) == cell kind on fresh clean rows: 0.9944
unit-seed overlap fresh vs main: 0, fresh vs calibration(+500000): 0
