"""Design probe for the text-informed module, on the CALIBRATION bank only (D-07H development).

Run before the pre-registration in docs/ext/textinfo.md, to choose between targeted lag opening and
all lags, and the weight temperature gamma. Intervals are uncalibrated (raw percentile), so the
comparison is between variants at equal footing, not against v4's calibrated numbers.

Run:  python experiments/ext/textinfo/probe_textinfo.py  (writes results/ext_textinfo_probe/)
"""
from __future__ import annotations

import json
import sys
import warnings
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_experiment import generator_config, unit_skeletons  # noqa: E402
from run_textinfo import synthetic_text  # noqa: E402

from paper4 import methods as M  # noqa: E402
from paper4.ext_textinfo import textinfo  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.metrics import evaluate  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

CFG = {"generator": {"lag_max": 2, "q0": 0.3, "cross_coef": [0.3, 0.8], "self_coef": [0.2, 0.6],
                     "noise_var": [0.5, 1.5], "rho_max": 0.9, "burn_in": 200},
       "damage": {"kinds": ["missing", "reversed"], "rates": [0.2, 0.5]}}
SEED = 77_700_000
VARIANTS = {  # name: (open_mode, open_mult, gamma)
    "targeted_m3_g1": ("targeted", 3.0, 1.0),
    "targeted_m5_g1": ("targeted", 5.0, 1.0),
    "all_g1": ("all", 3.0, 1.0),
    "all_g05": ("all", 3.0, 0.5),
}


def unit(args):
    warnings.filterwarnings("ignore")
    t_idx, topo = args
    u = SEED + t_idx
    sem = build_dynamic_sem(topo, generator_config(CFG), np.random.default_rng([u, 0]))
    skels = unit_skeletons(sem, u, CFG)
    noise = {k: np.random.default_rng([u, 77, i]).normal(size=91) for i, k in enumerate(["none", "missing", "reversed"])}
    su, sn = np.random.default_rng([u, 78]).random(91), np.random.default_rng([u, 79]).choice((-1.0, 1.0), 91)
    rows = []
    for T in (80, 150):
        data = sem.simulate(T, np.random.default_rng([u, 2, T]))
        for (kind, rate), skel in skels.items():
            res = {"v3": M.tolerant_v3(data, skel, 2, 4, 199, np.random.default_rng([u, 3, T, 6]))}
            for name, (mode, mult, g) in VARIANTS.items():
                if kind != "missing" and mode == "targeted":
                    continue
                for a in (0.5, 0.9):
                    s = skel.copy()
                    s.damage = dict(skel.damage)
                    s.damage["text"] = synthetic_text(skel, kind, sem, a, noise[kind], su, sn, 0.1)
                    res[f"{name}@a{a}"] = textinfo(data, s, 2, 4, 199, np.random.default_rng([u, 3, T, 201]),
                                                   open_mode=mode, open_mult=mult, gamma=g)
            for name, r in res.items():
                e = evaluate(sem, r, 4)
                e.update({"T": T, "kind": kind, "rate": rate, "variant": name, "topology": topo.id})
                rows.append(e)
    return rows


def main():
    topos = load_bank("D-07H", "development")[:10]
    rows = []
    with ProcessPoolExecutor(3) as pool:
        for r in pool.map(unit, list(enumerate(topos))):
            rows.extend(r)
    out = ROOT / "results" / "ext_textinfo_probe"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "runs.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    g = defaultdict(list)
    for r in rows:
        if r["status"] == "ok":
            g[(r["T"], r["kind"], r["rate"], r["variant"])].append(r)
    lines = ["# ext_textinfo_probe (D-07H development, 10 topologies x 1, uncalibrated)", "",
             "| T | damage | rate | variant | n | cov | IS | lost |", "|---|---|---|---|---|---|---|---|"]
    for k in sorted(g):
        v = g[k]
        cov = sum(x["n_covered_nonnull"] for x in v) / sum(x["n_nonnull"] for x in v)
        lost = sum(x["n_lost"] for x in v) / sum(x["n_nonnull"] for x in v)
        lines.append(f"| {k[0]} | {k[1]} | {k[2]} | {k[3]} | {len(v)} | {cov:.3f} | "
                     f"{np.mean([x['iscore_nonnull_mean'] for x in v]):.3f} | {lost:.3f} |")
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
