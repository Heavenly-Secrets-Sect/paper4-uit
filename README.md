# Paper4_UIT baseline context

**Status:** context baseline only. The research direction, model, estimator, hypotheses, and evaluation protocol are not approved yet.

This local repository is a clean place to collect context for Paper 4. It contains no experiment implementation and does not lock a Dynamic SEM design.

## Start here

- [Research context](docs/research_context.md)
- [Data inventory](data/README.md)
- [Open questions](docs/open_questions.md)
- [Source references](references/README.md)

## Working boundary

The current planning candidate is to study how errors in a supplied causal skeleton affect dynamic effect estimates and their uncertainty. The current planning draft tentatively assigns effect-estimation outcomes under controlled skeleton damage to Paper 4, separate from Paper 3's candidate skeleton-selection topic. This division is provisional.

The candidate plan says Paper 4 can develop in parallel using its own controlled skeleton damage; it does not require Paper 3 outputs. A future combined analysis belongs to Paper 5 and is outside this baseline.

## Data handling

The main candidate for coverage evaluation is synthetic dynamic data with known generated truth. The existing 14-node, 19-quarter financial case study has no causal ground truth and includes simulated-calibrated banking variables. Do not use it to establish effect-estimator coverage or causal accuracy.

This repository records source paths and evidence limits only. It does not copy raw workbooks or commit new data.

## Provenance

The context was assembled from the ACIIDS workspace at `G:\Documents\ACIIDS`, branch `feat/109-demov6-authors`. Source paths are recorded in the docs. The planning documents in that workspace are intentionally uncommitted; this repository does not edit or replace them.
