"""Helpers of revlag3 for the frozen RQ4.4 flag (experiments/ext/revlag/frozen_flag.json, unchanged):
row loading with the TRAINING encoding of the stated kind, and an evaluation that adds 1/width as a
comparator and an auto-compatible score with the stated dummies removed.

Encoding. The flag was fitted (flag_design.py) with stated = the cell's damage kind (none / extra /
missing / reversed). The round-2 runner stored stated = width_key(damage), which is "none" when the
stated k is 0 (e.g. a reversed cell where no contemporaneous edge could be reversed): 0.56% of the
fresh rows. ``load3`` uses ``stated_kind`` when the run has it (run_pairs3.py), otherwise derives it
from the cell name; the GES cell (composite record) keeps width_key, as there is no cell kind.

Statistics reuse experiments/ext/revlag/analyze_flag.py and flaglib.py (unchanged, sha256 pinned):
topology-cluster bootstrap, 2000 resamples, seed 20261103.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "ext" / "revlag"))
from analyze_flag import Clus, auc_reps, ci, flag_stats, p_le  # noqa: E402
from flaglib import score  # noqa: E402

KC = {"none": 0, "extra": 1, "missing": 2, "reversed": 3}


def load3(run: str, method: str = "tolerant_v4", encoding: str = "train") -> dict:
    z = np.load(ROOT / "results" / run / "pairs.npz")
    d = {k: z[k] for k in z.files}
    methods = [str(m) for m in d["methods"]]
    cells = [str(c) for c in d["cells"]]
    sel = d["method"] == methods.index(method)
    keys = ("topo", "rep", "scen", "T", "cell", "C_t", "C_e", "lo", "hi", "stated")
    rows = {k: d[k][sel] for k in keys}
    if "aux" in d:
        rows["aux"] = d["aux"][sel]
    if encoding == "train":
        if "stated_kind" in d:
            rows["stated"] = d["stated_kind"][sel]
        else:
            cell_kind = np.array([KC.get(c.split("|")[0], -1) for c in cells])
            ck = cell_kind[rows["cell"].astype(int)]
            rows["stated"] = np.where(ck >= 0, ck, rows["stated"]).astype(float)
    rows["scen_names"] = [str(s) for s in d["scenarios"]]
    rows["cells"] = cells
    return rows


def evaluate3(rows: dict, sel, frozen: dict, label: str, nostated: bool = False) -> dict:
    r = {k: (v[sel] if isinstance(v, np.ndarray) else v) for k, v in rows.items()}
    if nostated:
        r = dict(r, stated=np.zeros(len(r["T"])))
    y = (~((r["lo"] <= r["C_t"]) & (r["C_t"] <= r["hi"]))).astype(float)
    p = score(r, frozen)
    width = r["hi"] - r["lo"]
    relw = width / (np.abs(r["C_e"]) + 1e-9)
    invw = 1.0 / np.maximum(width, 1e-12)
    cl = Clus(r["topo"])
    pos = cl.pos(r["topo"])
    a_p, rp = auc_reps(p, y, pos, cl.W)
    a_r, rr = auc_reps(relw, y, pos, cl.W)
    a_i, ri = auc_reps(invw, y, pos, cl.W)
    fs = flag_stats((p > frozen["threshold"]).astype(float), y, pos, cl.W, len(cl.topos))
    return dict(label=label, n=int(len(y)), n_topo=int(len(cl.topos)), miss_rate=float(y.mean()),
                auc_p=a_p, auc_p_ci=ci(rp), p_auc_le_065=p_le(rp, 0.65), p_auc_le_05=p_le(rp, 0.5),
                auc_rel=a_r, auc_rel_ci=ci(rr), d_auc=a_p - a_r, d_auc_ci=ci(rp - rr), p_d_le0=p_le(rp - rr, 0.0),
                auc_inv=a_i, auc_inv_ci=ci(ri), d_inv=a_p - a_i, d_inv_ci=ci(rp - ri), p_dinv_le0=p_le(rp - ri, 0.0),
                **fs)


HDR = ["| tập | n | miss | AUROC(p_hat) [CI] | AUROC(rel_width) [CI] | AUROC(1/width) [CI] | p_hat − rel_width [CI] | "
       "p_hat − 1/width [CI] | flagged | miss cờ / không cờ | ratio [CI] |",
       "|---|---|---|---|---|---|---|---|---|---|---|"]


def fmt3(e: dict) -> str:
    return (f"| {e['label']} | {e['n']} | {e['miss_rate']:.3f} | {e['auc_p']:.3f} [{e['auc_p_ci'][0]:.3f}, {e['auc_p_ci'][1]:.3f}] | "
            f"{e['auc_rel']:.3f} [{e['auc_rel_ci'][0]:.3f}, {e['auc_rel_ci'][1]:.3f}] | "
            f"{e['auc_inv']:.3f} [{e['auc_inv_ci'][0]:.3f}, {e['auc_inv_ci'][1]:.3f}] | "
            f"{e['d_auc']:+.3f} [{e['d_auc_ci'][0]:+.3f}, {e['d_auc_ci'][1]:+.3f}] | "
            f"{e['d_inv']:+.3f} [{e['d_inv_ci'][0]:+.3f}, {e['d_inv_ci'][1]:+.3f}] | {e['share']:.3f} | "
            f"{e['miss_flagged']:.3f} / {e['miss_unflagged']:.3f} | {e['ratio']:.2f} [{e['ratio_ci'][0]:.2f}, {e['ratio_ci'][1]:.2f}] |")
