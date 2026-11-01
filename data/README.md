# Data inventory for Paper 4

This inventory describes candidate source artifacts from the original ACIIDS project. Selected supporting documents are included in [the source snapshots](../references/source_material/README.md); datasets and raw workbooks are not included. Confirm provenance and license before bringing data into this repository.

| Source path relative to ACIIDS | Contents | Baseline handling |
|---|---|---|
| `01_paper1_foundation/canonical_nodes/canonical_node_set.csv` | Canonical node identifiers | Frozen source; reference its version/hash if later imported. |
| `01_paper1_foundation/prior_graph/prior_graph_final_278.json` | Text-derived prior graph | Context/possible future input; not an effect truth set. |
| `03_causal_discovery/evaluation/topology_bank/` and `topology_bank_heldout/` | Existing static synthetic DAG banks | Paper 2 structure-learning context; they do not by themselves define a dynamic SEM generator. |
| `02_observational_data/processed/` | Derived financial panel and provenance reports | Case-study candidate only; no causal effect ground truth. |
| `02_observational_data/raw/` | Source workbooks | Keep out of this repository unless rights and an explicit data policy are established. |
| Future Paper 4 synthetic data | Dynamic time series with generated effects and controlled skeleton damage | Not present in this context baseline; its model and generator are open decisions. |

The documented core14 grid spans 14 nodes and 22 quarters, with a 19-quarter defensible window from 2020Q2 through 2024Q4. Seven banking variables are marked simulated-calibrated. It is not suitable as ground truth for interval coverage.

## Included data

- `data/topology_bank/`: verbatim copies of the static DAG banks D-07 and D-07H (40 topologies each, 14 nodes, 21 edges), with their manifests. See [PROVENANCE.md](topology_bank/PROVENANCE.md). They define the true graph of each simulated dynamic SEM; they are synthetic and contain no financial data.

No financial or raw data are included.
