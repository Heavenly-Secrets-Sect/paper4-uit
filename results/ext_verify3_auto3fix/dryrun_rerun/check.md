# Confirmatory check of tolerant_auto3, corrected spec v2 (TEST on arbitrary run directories, no verdict authority)

Runs: results/ext_gate_auto3, results/ext_auto5_a1. Failed/absent runs count as uncovered; a ruled cell fails when auto3 has > 3 failed/absent runs.

## Integrity

- I1: OK: skipped in dry/test mode (D-07 configs differ from the P4-H2 ones)
- I2: OK: 20 topologies, same in both runs, no duplicate rows
- I3: OK: 2880 ok auto3 rows checked; 0 mismatches
- I4: OK: 2879 ok tolerant_v4 rows checked; 0 mismatches
- I5: OK: 0 units with non-constant n_nonnull

## Rule

- C1: clean|80|missing|0.2 0.951 (ok-only 0.951; auto3 ok 60/60, bad 0; p 0.0000); clean|80|missing|0.5 0.949 (ok-only 0.949; auto3 ok 60/60, bad 0; p 0.0000); clean|80|reversed|0.2 0.932 (ok-only 0.932; auto3 ok 60/60, bad 0; p 0.0005); clean|80|reversed|0.5 0.903 (ok-only 0.903; auto3 ok 60/60, bad 0; p 0.3850); clean|150|missing|0.2 0.980 (ok-only 0.980; auto3 ok 60/60, bad 0; p 0.0000); clean|150|missing|0.5 0.980 (ok-only 0.980; auto3 ok 60/60, bad 0; p 0.0000); clean|150|reversed|0.2 0.971 (ok-only 0.971; auto3 ok 60/60, bad 0; p 0.0000); clean|150|reversed|0.5 0.966 (ok-only 0.966; auto3 ok 60/60, bad 0; p 0.0000) -> PASS
- C2: T40 ratio 1.124 (paired n 60; unpaired 1.124); T80 ratio 1.071 (paired n 60; unpaired 1.071); T150 ratio 1.195 (paired n 60; unpaired 1.195) -> PASS
- C3: T80 cov 0.941 (ok-only 0.941, bad 0) ratio 0.955 (paired n 60); T150 cov 0.955 (ok-only 0.955, bad 0) ratio 0.968 (paired n 60) -> PASS
- L1: latent1|80|missing|0.2 0.956 (ok-only 0.956; auto3 ok 60/60, bad 0; p 0.0000); latent1|80|reversed|0.2 0.937 (ok-only 0.937; auto3 ok 60/60, bad 0; p 0.0000); latent1|150|missing|0.2 0.977 (ok-only 0.977; auto3 ok 60/60, bad 0; p 0.0000); latent1|150|reversed|0.2 0.970 (ok-only 0.970; auto3 ok 60/60, bad 0; p 0.0000) -> PASS
- Holm (alpha 0.05) over the 14 coverage cells, H0 'cov <= 0.90' rejected: 13/14; not rejected: clean|80|reversed|0.5
- **CONFIRMED**

Fragility (recorded before P4-H2, docs/ext/auto3fix.md 1.2): on the D-07 dry run, C1 at T80 reversed-0.5 was 0.903, the only one of 14 coverage cells Holm could not reject (13/14); a NOT CONFIRMED from that cell alone is not evidence that auto3 got worse, and a CONFIRMED does not rule out true coverage below 0.90 there.

## n_ok / n_exp per method and cell

### main run

| cell | plugin | tolerant_auto3 | tolerant_auto3_nogate | tolerant_v4 |
|---|---|---|---|---|
| clean|40|extra|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|40|extra|0.5 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|40|ges|0.0 | 60/60 | 60/60 | 59/60 | 59/60 |
| clean|40|missing|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|40|missing|0.5 | 60/60 | 60/60 | 57/60 | 60/60 |
| clean|40|none|0.0 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|40|reversed|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|40|reversed|0.5 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|80|extra|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|80|extra|0.5 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|80|ges|0.0 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|80|missing|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|80|missing|0.5 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|80|none|0.0 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|80|reversed|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|80|reversed|0.5 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|150|extra|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|150|extra|0.5 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|150|ges|0.0 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|150|missing|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|150|missing|0.5 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|150|none|0.0 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|150|reversed|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|150|reversed|0.5 | 60/60 | 60/60 | 60/60 | 60/60 |

### latent run

| cell | oracle | plugin | tolerant_auto3 | tolerant_v4 |
|---|---|---|---|---|
| clean|80|missing|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|80|none|0.0 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|80|reversed|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|150|missing|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|150|none|0.0 | 60/60 | 60/60 | 60/60 | 60/60 |
| clean|150|reversed|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| latent1|80|missing|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| latent1|80|none|0.0 | 60/60 | 60/60 | 60/60 | 60/60 |
| latent1|80|reversed|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| latent1|150|missing|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| latent1|150|none|0.0 | 60/60 | 60/60 | 60/60 | 60/60 |
| latent1|150|reversed|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| latent3|80|missing|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| latent3|80|none|0.0 | 60/60 | 60/60 | 60/60 | 60/60 |
| latent3|80|reversed|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| latent3|150|missing|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| latent3|150|none|0.0 | 60/60 | 60/60 | 60/60 | 60/60 |
| latent3|150|reversed|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| noise0.1|80|missing|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| noise0.1|80|none|0.0 | 60/60 | 60/60 | 60/60 | 60/60 |
| noise0.1|80|reversed|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| noise0.1|150|missing|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |
| noise0.1|150|none|0.0 | 60/60 | 60/60 | 60/60 | 60/60 |
| noise0.1|150|reversed|0.2 | 60/60 | 60/60 | 60/60 | 60/60 |

