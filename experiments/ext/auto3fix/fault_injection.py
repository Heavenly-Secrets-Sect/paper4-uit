"""Fault-injection test of check_p4h2_v2.py on copies of the stored D-07 dry-run rows (no new runs).

Injected faults (main = results/ext_gate_auto3, lat = results/ext_auto5_a1):
  A. 2 auto3 rows of clean T80 reversed-0.5 set to status 'underdetermined' (<= MAX_BAD: cell stays ruled, coverage drops);
  B. 4 auto3 rows of clean T150 missing-0.2 deleted (> MAX_BAD: cell must fail);
  C. 5 tolerant_v4 rows of clean T80 none set to 'bootstrap_failed' (paired n 55 < 57: C2 must fail);
  D. every auto3 row of latent1 T80 missing-0.2 deleted (0 ok runs: coverage 0, no crash).
Usage: python experiments/ext/auto3fix/fault_injection.py WORK_DIR
Writes WORK_DIR/{main,lat}/ and runs the checker in --test mode into results/ext_auto3fix_dryrun/fault_injection/.
"""
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
KEEP = ("method", "topology", "profile", "replicate", "T", "kind", "rate", "k", "scenario")


def main(work):
    work = Path(work)
    n = {"A": 0, "B": 0, "C": 0, "D": 0}
    for src, dst in (("results/ext_gate_auto3", "main"), ("results/ext_auto5_a1", "lat")):
        os.makedirs(work / dst, exist_ok=True)
        shutil.copy(ROOT / src / "manifest.json", work / dst / "manifest.json")
        out = []
        for line in open(ROOT / src / "runs.jsonl", encoding="utf-8"):
            r = json.loads(line)
            m, key = r["method"], (r.get("scenario", "clean"), r["T"], r["kind"], r["rate"])
            if dst == "main" and m == "tolerant_auto3" and key == ("clean", 80, "reversed", 0.5) and n["A"] < 2:
                n["A"] += 1
                r = {k: r[k] for k in KEEP}
                r["status"] = "underdetermined"
            elif dst == "main" and m == "tolerant_auto3" and key == ("clean", 150, "missing", 0.2) and n["B"] < 4:
                n["B"] += 1
                continue
            elif dst == "main" and m == "tolerant_v4" and key == ("clean", 80, "none", 0.0) and n["C"] < 5:
                n["C"] += 1
                r = {**r, "status": "bootstrap_failed"}
                r.pop("iscore_nonnull_mean")
            elif dst == "lat" and m == "tolerant_auto3" and key == ("latent1", 80, "missing", 0.2):
                n["D"] += 1
                continue
            out.append(r)
        with open(work / dst / "runs.jsonl", "w", encoding="utf-8") as fh:
            fh.writelines(json.dumps(r) + "\n" for r in out)
    print("injected:", n)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import check_p4h2_v2 as C
    outdir = ROOT / "results" / "ext_auto3fix_dryrun" / "fault_injection"
    C.main(["--test", str(work / "main"), str(work / "lat"), str(outdir)])
    (outdir / "injected.json").write_text(json.dumps(n, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
