"""Write spec_stage1.json or spec_stage2.json (sha256 of every file that determines the E1 numbers).
Stage 1 (before the calibration run): code, spec doc, calibration config, R0 factors, topology loader. Stage 2 (before the evaluation): the
generated factor files R1 to R3 and the four evaluation configs, plus the calibration outputs."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ap = argparse.ArgumentParser()
ap.add_argument("--stage", type=int, required=True, choices=[1, 2])
a = ap.parse_args()
if a.stage == 1:
    files = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "src" / "paper4").glob("*.py"))
    files += ["experiments/run_experiment.py", "experiments/ext/revlag/run_pairs.py", "experiments/ext/r4ngorient/run_ng.py",
              "experiments/ext/r4ngorient/laws.py", "experiments/ext/v51/frozen_v4_v51.json", "experiments/calibration/tolerant_v4_frozen.json",
              "experiments/ext/p4h6/e1/run_e1_cal.py", "experiments/ext/p4h6/e1/make_rules_e1.py", "experiments/ext/p4h6/e1/run_e1.py",
              "experiments/ext/p4h6/e1/analyze_e1.py", "experiments/ext/p4h6/e1/guard_e1.py", "experiments/configs/ext_p4h6_e1_cal.json",
              "docs/ext/p4h6_e1.md"]
else:
    files = ["results/ext_p4h6_e1_cal/calpairs.json", "results/ext_p4h6_e1_cal/replication.json",
             "experiments/ext/p4h6/e1/factors_r1.json", "experiments/ext/p4h6/e1/factors_r2.json", "experiments/ext/p4h6/e1/factors_r3.json"]
    files += [f"experiments/configs/ext_p4h6_e1_r{i}.json" for i in range(4)]
spec = {"id": f"p4h6_e1_stage{a.stage}", "frozen_utc": datetime.now(timezone.utc).isoformat(), "bank": "P4-H6",
        "files": {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in files}}
(ROOT / f"experiments/ext/p4h6/e1/spec_stage{a.stage}.json").write_text(json.dumps(spec, indent=1) + "\n", encoding="utf-8")
print(a.stage, len(files), "files hashed")
