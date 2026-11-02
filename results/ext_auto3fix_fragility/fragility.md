# D2: fragility of the P2 verdict (descriptive; topology bootstrap of stored D-07 rows)

- full sample: CONFIRMED (corrected rule)
- P(CONFIRMED) over 2000 topology resamples: 0.616
- P(condition fails): C1 0.385, C2 0.000, C3 0.000, L1 0.000
- P(cell fails), cells failing in >= 0.5% of resamples: clean|80|reversed|0.5 0.385
- P(T80 reversed-0.5 is the only failing cell): 0.384
- T80 reversed-0.5 coverage: full 0.903; bootstrap 2.5/50/97.5%: 0.880 / 0.903 / 0.925; P(cov < 0.90) 0.385

Optimistic: D-07 helped select auto3; no shift between D-07H, D-07 and P4-H2; P4-H2 uses name-based bootstrap seeds (the D-07 auto3 rows used round-1 seeds).
