# Topology bank provenance

Verbatim copies of the static DAG banks built for Paper 2. Paper 4 turns each topology into a dynamic SEM (lags and coefficients are drawn by `src/paper4/generator.py`); the files here are never modified.

| Bank | Copied from (relative to ACIIDS) | Topologies | Manifest SHA-256 |
|---|---|---|---|
| D-07 | `03_causal_discovery/evaluation/topology_bank/` | 40 (20 development / 20 confirmatory; 20 Erdős–Rényi / 20 scale-free hub) | `23fdaee452b1f952d9274b95795c6e4e207af29e66edb02982a82017fe5b24df` |
| D-07H | `03_causal_discovery/evaluation/topology_bank_heldout/` | 40 (same split and profile counts) | `f420c56ca97da2741816e964e7f709a7246a34a265193643acaa090e22b29ecf` |

- Source: ACIIDS commit `5c69b38ff9fff4ba10dfba34f9e05ec32cc02881` (last commit touching both bank directories), copied on 2026-11-01 from checkout `fa8d14f05b49523f1747d49bd4f6c9e02aa6b4a7`.
- Every topology has 14 nodes (the core14 node set) and 21 edges. Each file's SHA-256 is listed in its bank manifest, and `paper4.topology.load_bank` checks it on every load.
- The D-07 manifest hash equals the frozen value recorded in the Paper 2 enhanced_v2 README.
- `D-07/generate_d07_bank.py` is the generator script of D-07, kept for reference (SHA-256 `e3572b446f00ad27d467ba8627d0608984bb5af1005d4622e2ffa5d3b34c1586`). It was run once with a new seed to generate P4-H1 (below); D-07 itself is never regenerated.

**Exposure.** Paper 2 has already reported results on the D-07 confirmatory split (see the D-07 benchmark report under `references/`). The Paper 4 pilot uses the development split only. Which split serves a Paper 4 confirmatory analysis is a protocol decision that has not been made.

## P4-H1 (generated for Paper 4)

- **What:** 40 topologies (20 development / 20 confirmatory; 20 Erdős–Rényi / 20 scale-free hub), 14 nodes, 21 edges.
- **How:** generated on 2026-11-01 by `D-07/generate_d07_bank.py --seed 20261102 --bank-dir P4-H1 --manifest-name p4h1_manifest.json --decision-id P4-H1`. Same generator as D-07, new seed.
- **Manifest SHA-256:** `4f1329e28c7dfb9da75a1ee9a6a38a2a23c27c3fda039630d3856b2b6c80484b`.
- **Reserved:** frozen-module held-out checks only. No Paper 4 method may be designed or tuned on it. Each use is logged in `docs/decision_rules.md`.
