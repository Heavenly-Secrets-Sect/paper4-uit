"""V2 of docs/ext/r4ngorient.md: tolerant_v5_1 rows of ext_r4ngorient_gauss vs results/ext_v51_eval.
Also oracle rows vs any stored D-07 run with oracle on the same seeds (descriptive)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
run = sys.argv[1] if len(sys.argv) > 1 else "ext_r4ngorient_gauss"
FIELDS = ("status", "n_nonnull", "n_covered_nonnull", "iscore_nonnull_mean", "width_kept", "C_abs_err_nonnull")


def index(path, method):
    out = {}
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if r["method"] == method:
            out[(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])] = r
    return out


new = index(ROOT / "results" / run / "runs.jsonl", "tolerant_v5_1")
old = index(ROOT / "results/ext_v51_eval/runs.jsonl", "tolerant_v5_1")
shared = sorted(set(new) & set(old))
bad = []
for k in shared:
    a, b = new[k], old[k]
    for f in FIELDS:
        x, y = a.get(f), b.get(f)
        if isinstance(x, float) and isinstance(y, float):
            if abs(x - y) > 1e-9:
                bad.append((k, f, x, y))
        elif x != y:
            bad.append((k, f, x, y))
res = {"run": run, "n_new": len(new), "n_stored": len(old), "n_shared": len(shared), "n_mismatch_fields": len(bad),
       "examples": [list(map(str, b)) for b in bad[:10]], "PASS": len(shared) == len(new) == len(old) and not bad}
out = ROOT / "results" / run / "pairing.json"
out.write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res, indent=1))
