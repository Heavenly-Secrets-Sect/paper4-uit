"""Red team: re-run single units of finished configs with the CURRENT code and compare row by row
with the stored runs.jsonl. Read-only on everything except stdout.

Usage: python experiments/ext/redteam/repro_check.py <result_name> <T> <method,method,...> [t_idx rep]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))
import run_experiment as R  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

name, T, methods = sys.argv[1], int(sys.argv[2]), sys.argv[3].split(",")
t_idx, rep = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (0, 0)
res = ROOT / "results" / name
man = json.loads((res / "manifest.json").read_text())
cfg = dict(man["config"])
cfg["T"] = [T]
cfg["methods"] = methods
cfg.pop("misstated", None)
calib = json.loads((res / "calibration.json").read_text()) if (res / "calibration.json").exists() else {}
topo = load_bank(cfg["bank"], cfg["split"])[t_idx]
out = R.run_unit((cfg, topo, t_idx, rep, calib, "main"))
stored = {}
for line in open(res / "runs.jsonl"):
    r = json.loads(line)
    if r["topology"] == topo.id and r["replicate"] == rep and r["T"] == T and r["method"] in methods:
        stored[(r.get("scenario", "clean"), r["kind"], r["rate"], r["method"])] = r
n_eq = n_diff = n_missing = 0
for r in out["rows"]:
    key = (r.get("scenario", "clean"), r["kind"], r["rate"], r["method"])
    s = stored.get(key)
    if s is None:
        n_missing += 1
        continue
    bad = []
    for k, v in r.items():
        if k == "scenario":
            continue
        sv = s.get(k)
        if isinstance(v, float) and isinstance(sv, (int, float)):
            if abs(v - sv) > 1e-9 * max(1, abs(sv)):
                bad.append((k, sv, v))
        elif v != sv and not (isinstance(v, float) and sv is None):
            bad.append((k, sv, v))
    if bad:
        n_diff += 1
        print("DIFF", key, bad[:4])
    else:
        n_eq += 1
print(f"{name} T={T} topo={topo.id} rep={rep}: identical rows {n_eq}, differing {n_diff}, not in stored {n_missing}")
