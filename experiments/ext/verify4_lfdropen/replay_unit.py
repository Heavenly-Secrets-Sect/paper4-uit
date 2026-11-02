"""Replay units of ext_r4lfdropen_eval with the current code (D-07 development, same seeds) and compare
with the stored rows bit for bit. Also replays with the candidate's step (2) monkeypatched to v5_1's
rule (must equal v5_1 in the missing cells).  Writes results/ext_verify4_lfdropen/replay.json.
Usage: python replay_unit.py T_IDX REP T
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import run_experiment as RE  # noqa: E402
from paper4 import ext_narrow, ext_r4lfdropen as L  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

t_idx, rep, T = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
cfg = json.loads((ROOT / "experiments/configs/ext_r4lfdropen_eval.json").read_text())
cfg = dict(cfg, T=[T], methods=["tolerant_v5_1", "tolerant_v5_1_lfdr"])
calib = json.loads((ROOT / "results/ext_r4lfdropen_eval/calibration.json").read_text())
topo = load_bank(cfg["bank"], cfg["split"])[t_idx]
out = RE.run_unit((cfg, topo, t_idx, rep, calib, "main"))
stored = {(r["method"], r["kind"], r["rate"]): r for r in map(json.loads, open(ROOT / "results/ext_r4lfdropen_eval/runs.jsonl"))
          if r["topology"] == topo.id and r["replicate"] == rep and r["T"] == T}
res = {"topology": topo.id, "rep": rep, "T": T, "replay_vs_stored": {}}
for r in out["rows"]:
    s = stored[(r["method"], r["kind"], r["rate"])]
    diff = [k for k in set(r) | set(s) if r.get(k) != s.get(k)]
    res["replay_vs_stored"][f"{r['method']}|{r['kind']}|{r['rate']}"] = diff

# monkeypatch: candidate with v5_1's selection rule -> must equal v5_1 in missing cells


def sel_v51(data, skel, lag_max, k_miss, bern_rng=None):
    tests = ext_narrow.screen_pairs(data, skel, lag_max)
    op = ext_narrow.select_open(data, skel, lag_max, k_miss, 3.0, 0.10)
    P, em = L.lfdr_posterior([t[0] for t in tests], k_miss)
    return op, tests, P, em


L.select_open_lfdr = sel_v51
cfg2 = dict(cfg, damage={"kinds": cfg["damage"]["kinds"], "rates": cfg["damage"]["rates"]})
out2 = RE.run_unit((cfg2, topo, t_idx, rep, calib, "main"))
rows = {(r["method"], r["kind"], r["rate"]): r for r in out2["rows"]}
res["patched_equals_v51"] = {}
skip = {"method", "info_lfdr_crn", "info_c_T", "width_kept", "iscore_nonnull_mean", "iscore_nonnull_median",
        "n_covered_nonnull", "n_covered_kept", "coverage_nonnull", "n_covered_null", "iscore_null_mean", "n_covered_null_reach"}
for (m, kind, rate), r in rows.items():
    if m != "tolerant_v5_1_lfdr" or kind != "missing":
        continue
    v = rows[("tolerant_v5_1", kind, rate)]
    # c_T differs (3.6 vs 2.3) so compare only calibration-free fields + info shared keys
    diff = [k for k in set(v) if k not in skip and not k.startswith("info_lfdr") and k in r and r[k] != v[k]]
    res["patched_equals_v51"][f"{kind}|{rate}"] = diff
(ROOT / "results/ext_verify4_lfdropen").mkdir(exist_ok=True)
p = ROOT / f"results/ext_verify4_lfdropen/replay_{t_idx}_{rep}_{T}.json"
p.write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
