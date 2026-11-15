"""Guard for E1 (frozen spec docs/ext/p4h6_e1.md).
Usage: python experiments/ext/p4h6/e1/guard_e1.py --phase pre_cal|pre_eval|post
pre_cal : stage-1 hashes hold, no E1 output exists.
pre_eval: stage-1 and stage-2 hashes hold, the calibration output exists, no P4-H6 development output exists.
post    : the four evaluation runs exist and are the only P4-H6 development manifests; hashes still hold."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BANK_SHA = "2102a388f0bb369f3f1cc1fd3c31ccec56236530a888889f453b589891d2c481"
EVALS = [f"ext_p4h6_e1_r{i}" for i in range(4)]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check_spec(name, bad):
    p = ROOT / f"experiments/ext/p4h6/e1/{name}"
    if not p.exists():
        bad.append(f"missing {name}")
        return
    for path, h in json.loads(p.read_text())["files"].items():
        if sha(path) != h:
            bad.append(f"hash mismatch {path}")


def dev_manifests():
    out = []
    for m in (ROOT / "results").glob("*/manifest.json"):
        try:
            d = json.loads(m.read_text())
            c = d.get("config", d)
        except Exception:
            continue
        if isinstance(c, dict) and c.get("bank") == "P4-H6" and c.get("split") == "development":
            out.append(m.parent.name)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True, choices=["pre_cal", "pre_eval", "post"])
    a = ap.parse_args()
    bad = []
    check_spec("spec_stage1.json", bad)
    if a.phase in ("pre_eval", "post"):
        check_spec("spec_stage2.json", bad)
    if sha("data/topology_bank/P4-H6/p4h6_manifest.json") != BANK_SHA:
        bad.append("P4-H6 manifest hash mismatch")
    devs = dev_manifests()
    cal = (ROOT / "results/ext_p4h6_e1_cal").exists()
    if a.phase == "pre_cal":
        if cal or devs or (ROOT / "results/ext_p4h6_e1_analysis").exists():
            bad.append(f"E1 outputs exist: cal={cal} dev={devs}")
    elif a.phase == "pre_eval":
        if not cal:
            bad.append("calibration output missing")
        if devs:
            bad.append(f"P4-H6 development manifests exist: {devs}")
    else:
        if sorted(devs) != sorted(EVALS):
            bad.append(f"unexpected P4-H6 development manifests: {devs}")
    print("\n".join(bad) if bad else f"E1 GUARD {a.phase.upper()} PASS (P4-H6 development manifests: {devs})")
    sys.exit(1 if bad else 0)


main()
