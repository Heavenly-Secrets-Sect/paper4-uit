# Enhanced v2 (P0-4a Skeleton)

Enhanced v2 represents the proposed confidence-aware and orientation-integrated causal discovery framework for Paper 2 (Epic #52, Issue #66, Issue #82).

## Status

- **Phase:** P0-4 (Dual-Channel Architecture & Fail-Closed Defenses)
- **Output Contract:** Officially outputs `output_type = "mpdag"` (Maximally Oriented Partially Directed Acyclic Graph).
- **Topology Bank D-07 (Option B):** 40 independent synthetic DAGs (14 nodes, 21 edges) generated with dual-profile (20 Erdős-Rényi + 20 Scale-Free Hub), split strictly 20 development / 20 confirmatory with frozen manifest SHA-256 `23fdaee452b1f952d9274b95795c6e4e207af29e66edb02982a82017fe5b24df`.

## Isolation Boundaries

1. **Isolation from Standard v2:**
   - Standard v2 located at `03_causal_discovery/baselines/standard_prior_v2/` is read-only and preserved byte-for-byte.
   - All Standard v2 invariants (symmetric skeleton soft-prior, score-equivalence, CPDAG output, ordinal evidence tiers) remain strictly immutable.
2. **Isolation from Baseline Matrix:**
   - The frozen 128-cell / 256-fit baseline matrix and runtime sidecars (`03_causal_discovery/experiments/baseline_matrix/results/`) remain untouched.
   - Replay checks (`--verify-replay`) continue to verify byte identity independently.
3. **Harmonized Contract:**
   - Orientation channel respects Meek closure over MEC subclasses, declaring `output_type = "mpdag"`.
   - Issue #66 fail-closed defenses: data-support margin gate, strong conflict data priority, bounded influence budget, and fallback to Standard v2.

## Traceability & Architecture Decisions

Detailed contract mapping, Issue #66 criteria tracing, and decision records are documented in:
- [`CONTRACT_TRACEABILITY.md`](./CONTRACT_TRACEABILITY.md)

Key decisions resolved per Issue #88:
1. Three-level identity contract ($w_{\text{struct}}=0 \land w_{\text{orient}}=0 \implies$ Plain GES; $w_{\text{struct}}=w_{\text{std}} \land w_{\text{orient}}=0 \implies$ Standard v2; $w_{\text{struct}}>0 \land w_{\text{orient}}>0 \implies$ Enhanced v2).
2. D-07 Topology Bank upgraded to 40 DAGs with dual-profile (Erdős-Rényi + Scale-Free Hub).
3. Contract harmonized to MPDAG output semantics.

## Usage

Run non-writing contract and preflight audit:

```powershell
python 03_causal_discovery/proposed_framework/enhanced_v2/scripts/run_enhanced_v2.py --check
```

Validate D-07 topology bank gate only:

```powershell
python 03_causal_discovery/proposed_framework/enhanced_v2/scripts/run_enhanced_v2.py --validate-bank
```

Run empirical benchmark across 40 DAGs of D-07 Bank:

```powershell
python 03_causal_discovery/proposed_framework/enhanced_v2/scripts/evaluate_d07_bank.py --corruption 0.0
```

Run the Issue #91 pre-registered acceptance gate (confirmatory split, fresh data seeds):

```powershell
python 03_causal_discovery/proposed_framework/enhanced_v2/scripts/evaluate_d07_bank.py --acceptance-gate --split confirmatory --replicates 5 --seed-base 20271000
```

Claim boundary: the superiority claim of PR #89 is revoked (Issue #91). The only admissible claim category and the gate rules are in `docs/enhanced_v2_protocol_claim_map.md` section 7 (A-91). Results, limitations and the gate verdict are documented in:
- [`D07_BENCHMARK_REPORT.md`](./D07_BENCHMARK_REPORT.md)
- `results/issue94_case_study_b8.json` — Issue #94: Enhanced v2 on Battery 8 (14 x 19 LOQO case study, `case_study_only`); reading rules in claim map section 10 (A-94)
- [`PRIOR_UTILITY_MAP.md`](./PRIOR_UTILITY_MAP.md) — Issue #96 P0-2 / P0-3: relative effect size and decision map from the #93 lanes (`EXPLORATORY_ONLY`, no new runs)
- [`TEXT_LIKE_PRIOR_ERRORS.md`](./TEXT_LIKE_PRIOR_ERRORS.md) — Issue #97: skeleton prior errors shaped like text extraction (shortcut, confounder, omission) vs random swap at the same damage (`EXPLORATORY_ONLY`, development split, seed base 20273000); reading rules in claim map section 12 (A-97)
