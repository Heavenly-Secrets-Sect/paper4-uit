# Research context for Paper 4

**Status:** baseline notes. Candidate framing and questions below remain open.

## Research lineage

Paper 1 produced a text-derived causal prior. Paper 2 studied the use of that prior in structure learning, especially the separate skeleton and orientation channels. The current planning sequence proposes a later paper on what happens when a skeleton is still wrong at the point where effects are estimated.

## Candidate problem statement

A future Paper 4 might study the bias and uncertainty of dynamic effect estimates when the supplied skeleton has controlled false, missing, or reversed edges. The planning document lists coefficient/intensity error, lag error, interval coverage and width, edge-level error cost, and reliability diagnostics as candidate outcomes. None is an approved method or claim in this baseline.

A Dynamic SEM generator with known truth is a candidate basis for the primary evaluation. The model family, temporal assumptions, lag range, estimator, interval construction, and comparison methods have not been selected.

## Evidence and interpretation boundaries

- Coverage and estimation-error claims require a generator or another source with verified effects. The existing financial panel does not supply causal ground truth.
- The documented core14 panel has 14 variables and a defensible 19-quarter window; seven banking variables are simulated-calibrated. Treat any later analysis as semi-synthetic or descriptive according to its exact inputs.
- Results on the real/semi-synthetic panel must not be described as causal effect accuracy without independently verified truth and identification assumptions.
- The current planning draft assigns structural quality metrics such as skeleton F1 and SHD to Paper 3, and effect-estimation outcomes to Paper 4. This separation is provisional; a later protocol should prevent duplicate primary claims if the split is retained.

## Scope boundary with Paper 3

The current planning draft proposes that Paper 4 run independently from controlled skeletons and its own generated data, without consuming Paper 3 outputs. Any later integration in Paper 5 is only a future possibility, after both papers have stable outputs.

## Source workspace

See [data inventory](../data/README.md) and [source references](../references/README.md) for the ACIIDS workspace paths behind these notes.
