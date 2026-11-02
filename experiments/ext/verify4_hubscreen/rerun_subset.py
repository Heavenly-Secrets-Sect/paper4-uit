"""Skeptic: re-run a subset of D-07 development units with the candidate's driver and its stored factors,
compare to the stored runs.jsonl rows (reproducibility)."""
import json, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
ROOT = Path("/Users/kietnt/Desktop/Workspace/Paper4_UIT")
sys.path.insert(0, str(ROOT / "experiments/ext/r4hubscreen")); sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
import run_r4
from paper4.topology import load_bank

def main():
    cfg = json.loads((ROOT / "experiments/configs/ext_r4hubscreen_lag2.json").read_text())
    cfg = dict(cfg, T=[19, 25, 30], cells=[["extra", 0.2], ["missing", 0.2], ["reversed", 0.2]])
    fac = json.loads((ROOT / "results/ext_r4hubscreen_lag2/calibration.json").read_text())
    topos = load_bank("D-07", "development")
    picks = [(0, 0), (5, 1), (11, 2), (17, 0)]
    jobs = [(cfg, topos[t], t, r, "main", fac) for t, r in picks]
    with ProcessPoolExecutor(2) as ex:
        rows = [x for o in ex.map(run_r4.run_unit, jobs) for x in o]
    stored = {}
    for l in open(ROOT / "results/ext_r4hubscreen_lag2/runs.jsonl"):
        r = json.loads(l); stored[(r["method"], r["topology"], r["replicate"], r["T"], r["kind"])] = r
    n = same = 0; bad = []
    for r in rows:
        s = stored[(r["method"], r["topology"], r["replicate"], r["T"], r["kind"])]
        n += 1
        ok = s["status"] == r["status"] and (r["status"] != "ok" or (abs(s["iscore_nonnull_mean"] - r["iscore_nonnull_mean"]) < 1e-9 and s["n_covered_nonnull"] == r["n_covered_nonnull"]))
        same += ok
        if not ok: bad.append((r["method"], r["topology"], r["T"], r["kind"]))
    res = {"rows": n, "identical": same, "mismatch": bad[:20]}
    (ROOT / "results/ext_verify4_hubscreen/rerun_subset.json").write_text(json.dumps(res, indent=1))
    print(res)

if __name__ == "__main__":
    main()
