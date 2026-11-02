"""Verifier (tlp2, round 2): reproduce rows of results/ext_tlp2_t80b from the current code, and
test the c_idx explanation of the pairing failure. Writes results/ext_verify2_tlp2/reproduce_rows.json."""
import json, sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments")); sys.path.insert(0, str(ROOT / "experiments/ext/tlp2"))
import run_cells  # noqa: F401  (patches run_experiment)
import run_experiment as R
from paper4.topology import load_bank

out = {}
cfg = json.loads((ROOT / "experiments/configs/ext_tlp2_t80b.json").read_text())
cfg["methods"] = ["tolerant_v4", "targeted_lp", "tlp2_db", "tlp2_db_p3"]
calib = json.loads((ROOT / "results/ext_tlp2_t80b/calibration.json").read_text())
topos = load_bank(cfg["bank"], cfg["split"])
t_idx, rep = 3, 1
res = R.run_unit((cfg, topos[t_idx], t_idx, rep, calib, "main"))
mine = {(r["kind"], r["rate"], r["method"]): r["iscore_nonnull_mean"] for r in res["rows"]}
stored = {}
for l in (ROOT / "results/ext_tlp2_t80b/runs.jsonl").open():
    r = json.loads(l)
    if r["topology"] == topos[t_idx].id and r["replicate"] == rep:
        stored[(r["kind"], r["rate"], r["method"])] = r["iscore_nonnull_mean"]
r1 = {}
for l in (ROOT / "results/ext_tlp_eval/runs.jsonl").open():
    r = json.loads(l)
    if r["topology"] == topos[t_idx].id and r["replicate"] == rep and r["T"] == 80:
        r1[(r["kind"], float(r["rate"]), r["method"])] = r["iscore_nonnull_mean"]
out["filtered_rerun_vs_stored"] = {"|".join(map(str, k)): [mine[k], stored.get(k), abs(mine[k] - stored.get(k, 1e9)) < 1e-12] for k in mine}
# unfiltered (original runner, full cell list) v4 only -> should equal round-1 ext_tlp_eval
cfg2 = dict(cfg); cfg2.pop("only_cells"); cfg2["methods"] = ["tolerant_v4"]
res2 = run_cells._orig_run_unit((cfg2, topos[t_idx], t_idx, rep, calib, "main"))
full = {(r["kind"], float(r["rate"]), r["method"]): r["iscore_nonnull_mean"] for r in res2["rows"]}
out["unfiltered_v4_vs_round1"] = {"|".join(map(str, k)): [v, r1.get(k), abs(v - r1.get(k, 1e9)) < 1e-12] for k, v in full.items()}
out["unit"] = {"topology": topos[t_idx].id, "replicate": rep, "T": 80}
p = ROOT / "results/ext_verify2_tlp2"; p.mkdir(parents=True, exist_ok=True)
(p / "reproduce_rows.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=1))
