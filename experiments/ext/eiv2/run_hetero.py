"""Driver for the eiv2 heterogeneous-noise run (experiments/configs/ext_eiv2_hetero.json).

The shared runner (experiments/run_experiment.py, not modified) adds measurement noise with one
ratio for every series. This driver reuses the runner unchanged (calibration, units, skeletons,
seeds, scoring, summary) and only replaces, inside the runner module, the function that adds the
noise: a scenario with a NEGATIVE ``meas_noise`` = -r gets heterogeneous noise with mean ratio r
(experiments/ext/eiv2/hetero.py: ratios evenly spaced on [0, 2r], randomly permuted over the
series with the same rng that then draws the noise, i.e. rng([unit, 6, T])). A positive value
keeps the runner's homogeneous noise, bit-for-bit.

The replacement is made at import time of this file, so worker processes (spawn) that import it
as their main module also get it; a worker without it would add NaN noise (sqrt of a negative
variance) and every method would fail loudly.

Run:  python experiments/ext/eiv2/run_hetero.py --config experiments/configs/ext_eiv2_hetero.json --workers 3
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(HERE))

import run_experiment as RE  # noqa: E402
from hetero import add_hetero_noise  # noqa: E402

_homogeneous = RE.add_measurement_noise


def add_noise(data, ratio, rng):
    if ratio is not None and ratio < 0:
        return add_hetero_noise(data, -ratio, rng)[0]
    return _homogeneous(data, ratio, rng)


RE.add_measurement_noise = add_noise

if __name__ == "__main__":
    raise SystemExit(RE.main())
