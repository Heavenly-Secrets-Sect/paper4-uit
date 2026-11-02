"""Write the three D-07 development evaluation configs of r4ngorient (docs/ext/r4ngorient.md, 5.3),
with the sha256 of experiments/ext/r4ngorient/frozen_ngorient.json."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
base = json.loads((ROOT / "experiments/configs/ext_v51_eval.json").read_text(encoding="utf-8"))
frozen = "experiments/ext/r4ngorient/frozen_ngorient.json"
sha = hashlib.sha256((ROOT / frozen).read_bytes()).hexdigest()
common = {"phase": "main", "bank": "D-07", "split": "development", "max_topologies": None, "replicates": 3,
          "damage": base["damage"], "H": 4, "n_boot": 199, "tau_effect": 0.1, "generator": base["generator"],
          "seed_base": 20261102, "methods": ["oracle", "tolerant_v5_1", "tolerant_ngA", "tolerant_ngB"],
          "stream_of": {"tolerant_ngA": "tolerant_v5_1", "tolerant_ngB": "tolerant_v5_1"},
          "calibrate_methods": ["tolerant_v5_1", "tolerant_ngA", "tolerant_ngB"],
          "frozen_calibration": frozen, "frozen_calibration_sha256": sha}
cfgs = {
    "gauss": {"T": [40, 80, 150], "shock": "gauss", "purpose": "r4ngorient no-harm grid G (Gaussian shocks)."},
    "ngmix": {"T": [40, 80, 150], "shock": "ng_mix", "purpose": "r4ngorient primary scenario (ng_mix shocks)."},
    "t10": {"T": [80, 150], "shock": "ng_t10", "only_cells": ["missing|0.2", "reversed|0.2"],
            "purpose": "r4ngorient descriptive stress (ng_t10 shocks)."},
}
for k, v in cfgs.items():
    cfg = {"name": f"ext_r4ngorient_{k}", **common, **v}
    (ROOT / f"experiments/configs/ext_r4ngorient_{k}.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")
print("frozen sha256", sha)
