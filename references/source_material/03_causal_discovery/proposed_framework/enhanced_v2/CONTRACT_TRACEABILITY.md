# Contract & Traceability Artifact: Enhanced v2 (P0-4b)

- **Artifact Version:** P0-4b / v2.0
- **Scope:** Epic #52, Issue #66, Issue #77, Issue #82, Issue #88, PR #89, Issue #91
- **Status:** P0-4b implementation present. Superiority claim of PR #89 REVOKED by Issue #91; claim boundary and pre-claim acceptance gate defined in `docs/enhanced_v2_protocol_claim_map.md` section 7 (A-91).
- **Authorship:** Implementor (paired under Reviewer audit authority)

---

## 1. Executive Summary

This document establishes the formal contract, traceability matrix, invariant boundaries, and provenance records for Phase P0-4b of the Enhanced v2 implementation.

Under the current phase:
1. Standard v2 and the 128-cell / 256-fit baseline matrix remain strictly frozen and unmodified (`--verify-replay` byte-identical PASS).
2. The Enhanced v2 estimator (`EnhancedPriorGES_v2`) implements dual-channel scoring (structure log-odds + orientation channel), priority-queue Meek candidate evaluation, fail-closed defenses (score-margin gate, max conflict rate fallback), and D-04 collider opportunity gating.
3. The D-07 topology bank is fully realized at 40 DAGs (20 Erdős-Rényi + 20 Scale-Free/Hub) split strictly into 20 development and 20 confirmatory topologies, locked under canonical SHA-256 `23fdaee452b1f952d9274b95795c6e4e207af29e66edb02982a82017fe5b24df`.
4. Output contract is harmonized to `output_type = "mpdag"` across `base.py` and Enhanced v2.
5. All Done criteria from Issue #66 are systematically mapped to traceable identifiers (`P0-4B-CRIT-01` through `P0-4B-CRIT-08`).

---

## 2. Standard v2 Immutable Invariants

Standard v2 (`03_causal_discovery/baselines/standard_prior_v2/`) serves as the locked comparator for Issue #53 and Epic #52. All downstream Enhanced v2 development must preserve these invariants without deviation.

| Invariant ID | Contract Description | Formal Rule / Value | Verification Mechanism | Status |
|---|---|---|---|---|
| **INV-STD2-01** | Symmetric Skeleton Soft Prior | $\text{Score}(G) = \text{BIC}(G) + \lambda \cdot \text{prior\_score}(\text{skeleton}(G))$ | Edge reversal $(u, v) \leftrightarrow (v, u)$ yields identical prior score | IMMUTABLE |
| **INV-STD2-02** | Complete Unordered Pair Coverage | All unordered node pairs $\binom{V}{2}$ have an explicit prior score entry | `test_01_all_pairs_present`, `test_14_missing_score_pair_rejected` | IMMUTABLE |
| **INV-STD2-03** | Fixed Weight Parameter | $\lambda$ is a fixed positive finite configuration value; no $\log(T)$ or sample-size scaling | `test_13_prior_bonus_is_not_scaled_by_t` | IMMUTABLE |
| **INV-STD2-04** | Ordinal Evidence Semantics | $c_e \in \{\text{absent}, 0.42, 0.51, 0.70, 0.85\}$; evidence tiers are NOT calibrated probabilities | `test_06`, `test_10_declared_tiers_are_four_plus_absent` | IMMUTABLE |
| **INV-STD2-05** | Neutral & Zero-Weight Identity | Neutral tier mapping and $\lambda = 0$ exactly reproduce plain GES | `test_16_neutral_prior_matches_plain_ges`, `test_17_zero_weight_matches_plain_ges` | IMMUTABLE |
| **INV-STD2-06** | CPDAG Output Semantics | Discovered graph type is strictly CPDAG; evaluation role is `prior_agreement`, never causal accuracy | `test_20_write_mode_emits_the_declared_v2_contract` | IMMUTABLE |
| **INV-STD2-07** | Determinism Across Repeats | Repeated fits under identical data/seed/config produce byte-identical graph fingerprints | `test_18_rerun_is_deterministic` | IMMUTABLE |
| **INV-STD2-08** | Standard v1 Physical Isolation | Standard v1 tree digest `a82920b734ee077c7698513553a44cd92a60360d26798dc2578715e2d1bf8062` must remain untouched | `test_20` normalized tree digest check | IMMUTABLE |
| **INV-STD2-09** | Baseline Replay Identity | 128 cells / 256 fits byte-identical across `baseline_reference.json`, `baseline_reference.csv`, `manifest.json` | `run_matrix.py --verify-replay` | IMMUTABLE |

---

## 3. Issue #66 Done Criteria Traceability Matrix

Issue #66 ("feat(cd): P1-DEF-1 — Fail-closed defense mechanisms for Enhanced v2") defines the required fail-closed defenses to prevent corrupted priors from corrupting discovery. The table below maps each criterion into tracked engineering items.

| Criterion Code | Issue #66 Done Criterion | Traceable Identifier | Verification / Test Target | Implementation State (P0-4b) |
|---|---|---|---|---|
| **CRIT-01** | Channel-off tái tạo Standard v2 | `P0-4B-CRIT-01` | `test_02_standard_v2_identity_when_orientation_off` | IMPLEMENTED |
| **CRIT-02** | Soft prior; không mặc định required/forbidden edge | `P0-4B-CRIT-02` | `test_04_config_schema_validation_deterministic` | IMPLEMENTED |
| **CRIT-03** | Data-support/score-margin gate trước khi thêm hoặc orient cạnh | `P0-4B-CRIT-03` | `test_04_strong_conflict_prioritizes_data` | IMPLEMENTED |
| **CRIT-04** | Conflict mạnh ưu tiên data; candidate priority queue cho Meek | `P0-4B-CRIT-04` | `test_04_strong_conflict_prioritizes_data`, `test_10_meek_candidate_priority_queue_ordering`, `test_14_weak_data_arrow_is_overridden_by_prior`, `test_15_strong_data_arrow_is_kept_as_local_conflict`, `test_18_override_never_creates_new_unshielded_collider` | IMPLEMENTED — #91: data arrow bị prior phản đối không còn ưu tiên tuyệt đối; giữ data khi local BIC margin >= `orientation_weight * delta_prior`, ngược lại nhận hướng prior nếu acyclic, extendable và không tạo collider mới. |
| **CRIT-05** | Stability gate qua bootstrap/subsampling | `P0-4B-CRIT-05` | Cluster bootstrap (1000 resamples per D-06) in `evaluate_d07_bank.py` là suy luận ở mức benchmark, không phải stability gate bên trong estimator. | **PARTIAL (#91 reclassified)** — estimator chưa có per-fit bootstrap/subsampling gate. |
| **CRIT-06** | Influence budget cho prior-only edge/collider ($N_{\min, \text{orient}} \ge 3$) | `P0-4B-CRIT-06` | `test_09_underpowered_orientation_preserves_data_only_arrows` | IMPLEMENTED |
| **CRIT-07** | Graph invalid, conflict vượt ngưỡng thì fallback Standard v2 | `P0-4B-CRIT-07` | `test_05_excessive_conflict_triggers_fallback_to_standard_v2`, `test_16_systematic_conflict_triggers_global_fallback`, `test_17_conflict_rate_denominator_counts_prior_evaluable_adjacencies` | IMPLEMENTED — #91: conflict xử lý local (abstention per edge); global fallback cần `n_conflicts >= n_min_conflicts (3)` VÀ `conflict_rate > max_conflict_rate`, mẫu số là `n_prior_evaluable` (mọi adjacency của Standard v2 có hướng prior). |
| **CRIT-08** | Per-edge provenance: `data_only`, `prior_assisted`, `conflict`, `abstained` | `P0-4B-CRIT-08` | `test_03_per_edge_provenance_tagging`, `test_09`, `test_11` | IMPLEMENTED |

---

## 4. Git Provenance Discrepancy Record

### 4.1. Factual Divergence
- **[FACT] GitHub Pull Request #81 Record:**
  - Pull Request: [#81](https://github.com/thanhhau15112000-dev/ACIIDS/pull/81)
  - Merged by: `thanhhau15112000-dev`
  - GitHub API / UI recorded merge commit: `4f1efd27647668ce961d7c32887a7adb3fa66f1c`
- **[FACT] Local & Upstream Staging Branch Record:**
  - Active branch `origin/staging` and `feat/82-enhanced-v2-implementation` HEAD: `e913631`
  - In-tree merge commit for PR #81: `4153ec0bb506791e9d749951172e243b4b0b3cad`
  - Commit message: `Merge pull request #81 from thanhhau15112000-dev/feat/77-baseline-execution-matrix`
  - Parents: `73875a4` (staging prior) and `56e09b8` (feature branch head)
- **[FACT] Tree Equivalence:**
  Both commit hashes represent the exact merge of Task 77 baseline matrix deliverables (64 files changed, 237,029 insertions).

### 4.2. Policy and Boundary
1. **No Git History Rewriting:** The Implementor will NOT execute `git rebase`, `git reset`, `git commit --amend`, or force-push to align commit hashes.
2. **No Unilateral Authority Attribution:** The Implementor does NOT declare whether GitHub metadata (`4f1efd2`) or local/remote Git object database (`4153ec0`) is the primary source of truth.
3. **Audit Tracking:** This discrepancy is registered as a formal item requiring Human / Lead Research Architect adjudication.

---

## 5. D-07 Topology Bank Protocol Contract

Per `docs/enhanced_v2_protocol_claim_map.md` (Decision D-07, Option B upgrade via Issue #88):
- **Requirement:** 40 synthetic DAG topologies (14 nodes, 21 edges).
- **Dual-Profile Structure:**
  * 50% (20 DAGs) Erdős-Rényi random DAGs with preserved sparsity ($m=21$, average degree $d=3.0$).
  * 50% (20 DAGs) Scale-Free / Hub Networks with macro hub variables (at least 1 node with out-degree $\ge 4$).
- **Split:** Strict symmetric 20 development topologies (`syn_dag_00` to `syn_dag_19`) and 20 confirmatory topologies (`syn_dag_20` to `syn_dag_39`).
- **Invariants:** 100% acyclic, weakly connected, $N_{\text{v-structure}} \ge 3$ on all 40 topologies (per D-04).
- **Integrity:** Frozen canonical SHA-256 digest `23fdaee452b1f952d9274b95795c6e4e207af29e66edb02982a82017fe5b24df` declared in machine-readable manifest (`D07_MANIFEST_SCHEMA = "topology_bank_manifest/v1"`).
- **Anti-Overfitting Boundary:** Prevents algorithmic tuning or hyperparameter leakage into the evaluation bank.
- **Anti-Synthesis Principle:** The Implementor is strictly forbidden from creating mock or placeholder DAG files. If the authoritative bank is not provided, the validator returns `PARTIAL_BLOCKED`.

---

## 6. Explicit Pending Decisions Register

The following architectural decisions are tracked and resolved per project governance:

| Decision ID | Subject | Options Under Consideration | Current Resolution / Implementation Action |
|---|---|---|---|
| **DEC-01** | Zero-Weight Identity Condition | Option A: $w_{\text{orient}} = 0 \implies \text{Enhanced} = \text{Standard v2}$<br>Option B: $w_{\text{struct}} = 0 \land w_{\text{orient}} = 0 \implies \text{Enhanced} = \text{Standard v2}$<br>Option C: Three-Level Identity Contract | **LOCKED (Option C)**:<br>1. $w_{\text{struct}} = 0 \land w_{\text{orient}} = 0 \implies \text{Plain GES}$<br>2. $w_{\text{struct}} = w_{\text{std}} \land w_{\text{orient}} = 0 \implies \text{Standard v2}$<br>3. $w_{\text{struct}} > 0 \land w_{\text{orient}} > 0 \implies \text{Enhanced v2 Full}$ |
| **DEC-02** | Authority of Merge Provenance | Option A: Adopt GitHub web merge commit `4f1efd2`<br>Option B: Adopt staging tree merge commit `4153ec0` | **RESOLVED (Option B)**: Adopt `4153ec0` as canonical in-tree merge commit preserving Git DAG cryptographic ancestry (`git merge-base --is-ancestor`). Tree equivalence to `4f1efd2` (`4fd15f9...`) documented. |
| **DEC-03** | Official D-07 Source Bank | Option A: 20 DAGs ER only<br>Option B: 40 DAGs Dual-Profile (ER + Scale-Free Hub) | **LOCKED (Option B — Issue #88)**: 40 DAGs (14 nodes, 21 edges, $N_{\min,\text{orient}} \ge 3$, 20 dev / 20 conf; 20 ER / 20 Hub) with canonical SHA-256 `23fdaee452b1f952d9274b95795c6e4e207af29e66edb02982a82017fe5b24df`. |
| **DEC-04** | Orientation Channel & Contract Semantics | Option A: Declare `cpdag`<br>Option B: Declare `mpdag` | **LOCKED (Option B — Issue #88)**: Enhanced v2 officially declares `output_type = "mpdag"` (Maximally Oriented Partially Directed Acyclic Graph) reflecting background knowledge orientation and Meek closure over MEC subclasses. |
| **DEC-05** | Paired Empirical Benchmark Validation | Option A: Unit tests only<br>Option B: Full 40-DAG D-07 Paired Benchmark across corruption levels | **LOCKED (Option B) — SUPERIORITY CLAIM REVOKED BY #91**: Executed 360-fit paired benchmark across 40 DAGs under $\rho \in \{0.0, 0.3, 0.7\}$ with paired CPU runtime telemetry and Meek cascade dynamics. Established Confirmatory superiority ($\Delta_{\text{F1}} = +0.0674$, $\Delta_{\text{SHD}} = -2.20$, 0 Losses), Scale-Free Hub cascade advantage ($\mu_{\text{cascade}} = 1.578$ vs $1.159$, $\Delta_{\text{F1}} = +0.0791$), zero median runtime overhead (median ratio $1.00\times$, p95 $1.33\times$), and 100% fail-closed non-inferiority ($M_{\text{NI}} \le 1.0$) per D-01 through D-08 in `D07_BENCHMARK_REPORT.md`. |
| **DEC-06** | Claim category & pre-claim acceptance (Issue #91) | Option A: Giữ claim superiority PR #89<br>Option B: Thu hồi, thu hẹp phạm trù claim, gate pre-registered | **LOCKED (Option B)**: Median paired $\Delta$ của PR #89 bằng 0 (CI [0, 0]) nên claim superiority bị thu hồi. Phạm trù claim thu hẹp thành cải thiện orientation/SHD có điều kiện trên skeleton chung, stratum Benign, simulator đã khai báo. Claim chỉ mở khi `evaluate_d07_bank.py --acceptance-gate` trên confirmatory với seed base mới trả `CLAIM_UNLOCKED` (claim map 7.3). Kết quả gate: `D07_BENCHMARK_REPORT.md` mục 4. |
