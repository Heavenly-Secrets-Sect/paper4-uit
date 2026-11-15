"""Guard for the single E2 run on P4-H6: verify every frozen file hash and the sealed bank manifest, and that no P4-H6 output
exists (pre) or exactly the expected ones exist (post).
Usage: python experiments/ext/p4h6/e2/guard_e2.py --phase pre|post
docs/ext/p4h6_e2.md is hashed here and must stay unchanged; results are recorded only in docs/decision_rules.md."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BANK_SHA = "2102a388f0bb369f3f1cc1fd3c31ccec56236530a888889f453b589891d2c481"
RUNS = ["ext_p4h6_e2_gauss", "ext_p4h6_e2_ngmix", "ext_p4h6_e2_ngt10"]
OUTS = RUNS + ["ext_p4h6_e2_analysis"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True, choices=["pre", "post"])
    a = ap.parse_args()
    bad = []
    spec = json.loads((ROOT / "experiments/ext/p4h6/e2/spec_files.json").read_text())
    for path, h in spec["files"].items():
        if sha(path) != h:
            bad.append(f"hash mismatch {path}")
    if sha("data/topology_bank/P4-H6/p4h6_manifest.json") != BANK_SHA:
        bad.append("P4-H6 manifest hash mismatch")
    mans = []
    for m in (ROOT / "results").glob("*/manifest.json"):
        try:
            d = json.loads(m.read_text())
            c = d.get("config", d)
        except Exception:
            continue
        if isinstance(c, dict) and c.get("bank") == "P4-H6":
            mans.append(m.parent.name)
    outs = [d for d in OUTS if (ROOT / "results" / d).exists()]
    if a.phase == "pre":
        if mans:
            bad.append(f"P4-H6 manifests exist: {mans}")
        if outs:
            bad.append(f"outputs exist: {outs}")
    else:
        if sorted(mans) != sorted(RUNS):
            bad.append(f"unexpected P4-H6 manifests: {mans}")
    print("\n".join(bad) if bad else f"E2 GUARD {a.phase.upper()} PASS (manifests with bank P4-H6: {mans})")
    sys.exit(1 if bad else 0)


main()
