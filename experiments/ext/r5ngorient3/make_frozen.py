"""Frozen width factors of r5ngorient3: experiments/ext/v51/frozen_v4_v51.json verbatim, plus
tolerant_ngA3|* = tolerant_ngA|* = tolerant_v5_1|* (no re-tune, synthesis_round4.md section 4.2 factor rule).
Writes experiments/ext/r5ngorient3/frozen_r5ngorient3.json and prints its sha256."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
src = json.loads((ROOT / "experiments/ext/v51/frozen_v4_v51.json").read_text(encoding="utf-8"))
out = {"_note": "r5ngorient3: tolerant_ngA3|* = tolerant_ngA|* = tolerant_v5_1|* (frozen, no re-tune); rest = "
                "experiments/ext/v51/frozen_v4_v51.json verbatim."}
out.update({k: v for k, v in src.items() if not k.startswith("_")})
for k, v in list(src.items()):
    if k.startswith("tolerant_v5_1|"):
        rest = k[len("tolerant_v5_1"):]
        out["tolerant_ngA3" + rest] = v
        out["tolerant_ngA" + rest] = v
p = ROOT / "experiments/ext/r5ngorient3/frozen_r5ngorient3.json"
p.write_text(json.dumps(out, indent=2), encoding="utf-8")
print(hashlib.sha256(p.read_bytes()).hexdigest())
