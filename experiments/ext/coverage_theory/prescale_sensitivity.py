"""Pre-scale sensitivity (feedback point 3), exploratory, offline from the P4-H7 unit dumps.

The dumps were made with the shipped pre-scale kappa0 = 0.5, so a dumped half-width is 0.5 * half_raw.
A rule with pre-scale kappa and raw factor c multiplies the dumped half-width by m = 2 * kappa * c.
For every kappa the shipped pooled rule (target = min(0.95, max coverage - 0.005), grid c = 1.0 .. 10.0 step 0.1,
first c reaching the target) is tuned on the CALIBRATION split and evaluated on the DESIGN split.
Also reported: S3 = no pre-scale constant, kappa = 1 with the effective grid 0.3 .. 5.0 step 0.05.
Output: results/ext_p4h7_design/prescale_sensitivity.md
"""
import collections
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]


def load(path):
    by = collections.defaultdict(lambda: [[], []])
    for r in json.loads(Path(path).read_text())["records"]:
        by[r["cell"]][0] += r["dist"]
        by[r["cell"]][1] += r["half"]
    return {c: (np.array(d), np.array(h)) for c, (d, h) in by.items()}


def tune(dist, half, grid_mult):
    cov = np.array([(dist <= m * half).mean() for m in grid_mult])
    target = min(0.95, cov.max() - 0.005)
    return grid_mult[int(np.argmax(cov >= target))], bool(cov.max() - 0.005 < 0.95), float(cov.max())


def main():
    cal = load(ROOT / "results/ext_p4h7_cal/units.json")
    des = load(ROOT / "results/ext_p4h7_design/units.json")
    grid = np.round(np.arange(1.0, 10.01, 0.1), 2)
    arms = [(f"kappa={k}", k, 2 * k * grid) for k in (0.25, 0.5, 1.0, 2.0)]
    arms.append(("S3: no constant, effective grid 0.3-5.0 step 0.05", 1.0, 2 * np.round(np.arange(0.3, 5.001, 0.05), 3)))
    lines = ["| arm | mean effective factor | floor binds | cap binds | coverage (design) | mean IS | mean width |", "|---|---|---|---|---|---|---|"]
    for name, k, mults in arms:
        eff, floor, cap, covs, iss, wid = [], 0, 0, [], [], []
        for cell, (dc, hc) in cal.items():
            m, capped, _ = tune(dc, hc, mults)
            eff.append(m / 2)  # effective factor on the raw half-width (kappa * c)
            floor += m == mults[0]
            cap += (m == mults[-1])
            dd, hd = des[cell]
            covs.append(float(np.mean(dd <= m * hd)))
            iss.append(float(np.mean(2 * m * hd + 40 * np.maximum(dd - m * hd, 0))))
            wid.append(float(np.mean(2 * m * hd)))
        n = len(cal)
        lines.append(f"| {name} | {np.mean(eff):.3f} | {floor}/{n} | {cap}/{n} | {np.mean(covs):.4f} | {np.mean(iss):.3f} | {np.mean(wid):.3f} |")
    out = ROOT / "results/ext_p4h7_design/prescale_sensitivity.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
