# Confirmatory check of tolerant_auto3 (DRY RUN on D-07 development rows, NOT a confirmation)

Runs: ext_gate_auto3, ext_auto5_a1

- C1: 80|missing|0.2 0.951; 80|missing|0.5 0.949; 80|reversed|0.2 0.932; 80|reversed|0.5 0.903; 150|missing|0.2 0.980; 150|missing|0.5 0.980; 150|reversed|0.2 0.971; 150|reversed|0.5 0.966 -> PASS
- C2: T40 1.124; T80 1.071; T150 1.195 -> PASS
- C3: T80 cov 0.941 ratio 0.955; T150 cov 0.955 ratio 0.968 -> PASS
- L1: latent1|80|missing|0.2 0.956; latent1|80|reversed|0.2 0.937; latent1|150|missing|0.2 0.977; latent1|150|reversed|0.2 0.970 -> PASS
- Holm (alpha 0.05) over the 14 coverage cells, H0 'cov <= 0.90' rejected: 13/14
- **CONFIRMED**
