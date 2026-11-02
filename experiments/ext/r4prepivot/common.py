"""Shared driver for direction r4prepivot (docs/ext/r4prepivot.md).

Re-uses the runner's own functions (generator_config, unit_skeletons, public, ext_seed, add_latent,
add_measurement_noise) so that data, damaged skeletons and v5.1's bootstrap stream are exactly those
of the runner call being paired with. One dataset -> one call of ``prepivot_core`` -> three rows:
tolerant_v5_1 (bank factor, must pair with stored rows), tolerant_v5_1_pp (primary),
tolerant_v5_1_pp_orig (secondary, the design as proposed).

``cfg`` is the config of the stored run being paired with, plus "_factors": a dict of v5.1 width
factors (runner keys ``tolerant_v5_1|T|kind``; effective factor = value x 0.5).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

import run_experiment as R  # noqa: E402
from paper4 import methods as M  # noqa: E402
from paper4.ext_r4prepivot import prepivot_core, result_from_core  # noqa: E402
from paper4.generator import add_latent, add_measurement_noise, build_dynamic_sem  # noqa: E402
from paper4.metrics import evaluate  # noqa: E402

FROZEN = json.loads((ROOT / "experiments/ext/v51/frozen_v4_v51.json").read_text(encoding="utf-8"))
KEEP = ("method", "status", "topology", "profile", "replicate", "T", "kind", "rate", "k", "scenario",
        "n_nonnull", "n_lost", "n_covered_nonnull", "coverage_nonnull", "width_kept", "iscore_nonnull_mean",
        "iscore_nonnull_median", "n_null", "n_covered_null", "iscore_null_mean", "C_abs_err_nonnull")


def load_cfg(name: str, factors: dict | None = None) -> dict:
    cfg = json.loads((ROOT / "experiments/configs" / f"{name}.json").read_text(encoding="utf-8"))
    cfg["_factors"] = factors if factors is not None else FROZEN
    return cfg


def cell_index(cfg: dict) -> dict:
    """(kind, rate) -> c_idx exactly as the runner enumerates cells (dict order of unit_skeletons)."""
    keys = [("none", 0.0)] + [(k, r) for k in cfg["damage"]["kinds"] for r in cfg["damage"]["rates"]]
    return {k: i for i, k in enumerate(keys)}


def run_dataset(args):
    """args = (cfg, topo, t_idx, rep, T, kind, rate, scenario dict, b_o, b_i). Returns rows."""
    cfg, topo, t_idx, rep, T, kind, rate, sc, b_o, b_i = args
    gen = R.generator_config(cfg)
    H, lag_max, n_boot = cfg["H"], gen.lag_max, cfg["n_boot"]
    unit = cfg["seed_base"] + 1000 * t_idx + rep
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skels = R.unit_skeletons(sem, unit, cfg)
    sem_s = add_latent(sem, sc.get("latent", 0), np.random.default_rng([unit, 5]),
                       n_children=sc.get("latent_children", 3))
    c_idx = cell_index(cfg)[(kind, rate)]
    data = sem_s.simulate(T, np.random.default_rng([unit, 2, T]))
    data = add_measurement_noise(data, sc.get("meas_noise", 0.0), np.random.default_rng([unit, 6, T]))
    skel = R.public(skels[(kind, rate)])
    rng = np.random.default_rng([unit, 3, T, c_idx, R.ext_seed("tolerant_v5_1")])
    t0 = time.perf_counter()
    core = prepivot_core(data, skel, lag_max, H, n_boot, rng, b_o=b_o, b_i=b_i)
    sec = time.perf_counter() - t0
    fkey = f"tolerant_v5_1|{T}|{M.width_key(skel.damage)}"
    fac = cfg["_factors"].get(fkey)
    v_cal = M.calibrate_width(core["v51"], fac, "tolerant_v5_1")
    rows = []
    for res in (v_cal, result_from_core(core, "tolerant_v5_1_pp", "pp"),
                result_from_core(core, "tolerant_v5_1_pp_orig", "orig")):
        row = evaluate(sem_s, res, H, tau_effect=cfg["tau_effect"])
        out = {k: row.get(k) for k in KEEP}
        out.update({k: v for k, v in row.items() if k.startswith("info_") and not isinstance(v, (list, dict))})
        out.update({"topology": topo.id, "profile": topo.profile, "replicate": rep, "T": T, "kind": kind,
                    "rate": rate, "k": skel.damage.get("k", 0), "scenario": sc.get("name", "clean"),
                    "t_idx": t_idx, "lag_max": lag_max, "f_v51_eff": (fac * 0.5) if fac else None,
                    "seconds_total": sec, "seconds_outer": core.get("seconds_outer"),
                    "seconds_inner": core.get("seconds_inner")})
        rows.append(out)
    return rows
