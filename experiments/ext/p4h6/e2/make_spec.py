"""Write experiments/ext/p4h6/e2/spec_files.json: sha256 of every file that determines the E2 numbers. Run once, before the guard."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
files = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "src" / "paper4").glob("*.py"))
files += ["experiments/run_experiment.py", "experiments/ext/revlag/run_pairs.py",
          "experiments/ext/r4ngorient/run_ng.py", "experiments/ext/r4ngorient/laws.py",
          "experiments/ext/v51/frozen_v4_v51.json", "experiments/calibration/tolerant_v4_frozen.json",
          "experiments/ext/p4h6/e2/run_e2.py", "experiments/ext/p4h6/e2/analyze_e2.py", "experiments/ext/p4h6/e2/guard_e2.py",
          "experiments/configs/ext_p4h6_e2_gauss.json", "experiments/configs/ext_p4h6_e2_ngmix.json",
          "experiments/configs/ext_p4h6_e2_ngt10.json", "docs/ext/p4h6_e2.md"]
spec = {"id": "p4h6_e2", "frozen_utc": datetime.now(timezone.utc).isoformat(), "bank": "P4-H6", "seed_base": 90261113,
        "files": {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in files}}
(ROOT / "experiments/ext/p4h6/e2/spec_files.json").write_text(json.dumps(spec, indent=1) + "\n", encoding="utf-8")
print(len(files), "files hashed")
