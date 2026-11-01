# Paper4_UIT baseline context

**Status:** context baseline only. The research direction, model, estimator, hypotheses, and evaluation protocol are not approved yet.

This repository collects context for Paper 4 and holds the first experiment code (see "Experiment code" below). The code fills the plan's open choices with provisional defaults; it does not lock a Dynamic SEM design.

## Start here

- [Research context](docs/research_context.md)
- [Experiment workflow and code map](docs/experiment_workflow.md)
- [Data inventory](data/README.md)
- [Open questions](docs/open_questions.md)
- [Source references](references/README.md)

## Working boundary

The current planning candidate is to study how errors in a supplied causal skeleton affect dynamic effect estimates and their uncertainty. The current planning draft tentatively assigns effect-estimation outcomes under controlled skeleton damage to Paper 4, separate from Paper 3's candidate skeleton-selection topic. This division is provisional.

The candidate plan says Paper 4 can develop in parallel using its own controlled skeleton damage; it does not require Paper 3 outputs. A future combined analysis belongs to Paper 5 and is outside this baseline.

## Data handling

The main candidate for coverage evaluation is synthetic dynamic data with known generated truth. The existing 14-node, 19-quarter financial case study has no causal ground truth and includes simulated-calibrated banking variables. Do not use it to establish effect-estimator coverage or causal accuracy.

Selected planning and provenance documents are included under references/source_material. Raw workbooks and data artifacts are not included in this baseline.

## Provenance

The context was assembled from the ACIIDS workspace on branch feat/109-demov6-authors. Tracked source snapshots came from commit 5874b5be1689d596b91c55140a1e837b3e53d980. Selected copies are included under references/source_material. The two planning DOCX copies were uncommitted in ACIIDS at capture time; the originals there remain unchanged.

## Experiment code (scaffold)

The implementation follows section 5.2 of the plan: a dynamic SEM generator with known truth (B1), controlled skeleton damage (B3), interval methods for RQ4.2 (baselines b0–b5 and the tolerant module, `src/paper4/methods.py`), and a runner that fits every method on the same data and summarises coverage, width and interval score. Decision rules for the method comparison are fixed in [docs/decision_rules.md](docs/decision_rules.md) before running. Choices the plan leaves open use provisional defaults listed in [open questions](docs/open_questions.md); they are not approved decisions.

```bash
pip install -r requirements.txt                     # numpy only
python -m unittest discover -s tests                # recovery and invariant tests
python experiments/run_experiment.py --config experiments/configs/rq41_pilot.json   # RQ4.1 errors
python experiments/run_experiment.py --config experiments/configs/rq42_v4.json      # RQ4.2 methods (module v4)
python experiments/check_rules.py results/rq42_v4 --module tolerant_v4               # apply the decision rules
python experiments/run_edge_cost.py                                                  # RQ4.3 edge cost map
python experiments/run_flags.py                                                      # RQ4.4 reliability flags
```

Topologies come from `data/topology_bank/`, verbatim copies of the Paper 2 banks D-07 and D-07H ([provenance](data/topology_bank/PROVENANCE.md)), verified against their manifests on every load. Development uses the D-07 development split; held-out checks used each confirmatory split once, as logged in [docs/decision_rules.md](docs/decision_rules.md). Results are summarised in docs/ket_qua_rq42.md, ket_qua_rq43.md and ket_qua_rq44.md.

