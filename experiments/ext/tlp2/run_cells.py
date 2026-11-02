"""Run experiments/run_experiment.py on a SUBSET of the damage cells, unchanged otherwise.

Why: the damaged skeleton of a kind is drawn from the stream rng([unit, 1, k_idx]) with k_idx its
position in ["none"] + damage.kinds, so the kinds list must stay [extra, missing, reversed] to pair
with a2_baselines / ext_tlp_eval. The runner then fits every method on every cell. The faithful
double bootstrap costs about 3-9 s per call, so one config cannot cover all cells within the
20-minute budget. This wrapper keeps the kinds list (hence identical skeletons and data) and only
skips the cells that are not listed in the config key

    "only_cells": [["none", 0.0], ["extra", 0.2], ...]

in the MAIN phase. The calibration phase is not filtered (every calibration cell is used, as in the
runner). Nothing else changes: same seeds, same methods, same scoring, same output files.

Usage: python experiments/ext/tlp2/run_cells.py --config experiments/configs/ext_tlp2_<x>.json --workers 3
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

import run_experiment as R  # noqa: E402

_orig_unit_skeletons = R.unit_skeletons
_orig_run_unit = R.run_unit


def unit_skeletons_filtered(sem, unit_seed, cfg):
    out = _orig_unit_skeletons(sem, unit_seed, cfg)   # drawn with the full kinds list: same skeletons
    keep = cfg.get("_only_cells")
    if keep is None:
        return out
    keep = {(k, float(r)) for k, r in keep}
    return {key: s for key, s in out.items() if (key[0], float(key[1])) in keep}


def run_unit_filtered(args):
    cfg, topo, t_idx, rep, calib_c, phase = args
    cfg = dict(cfg)
    cfg["_only_cells"] = cfg.get("only_cells") if phase == "main" else None
    return _orig_run_unit((cfg, topo, t_idx, rep, calib_c, phase))


# Applied at import, so it also holds in the spawned worker processes (they re-import this module).
R.unit_skeletons = unit_skeletons_filtered
R.run_unit = run_unit_filtered

if __name__ == "__main__":
    raise SystemExit(R.main())
