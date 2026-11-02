"""Driver of the r4leadlag runs: the runner's own functions with the worker patches of worker.py.

  python experiments/ext/r4leadlag/drive.py calibrate --workers 3
      tunes the width factors of tolerant_v5_1_leadlag on the calibration block of
      experiments/configs/ext_r4leadlag_eval_clean.json (clean D-07H development), writes
      results/ext_r4leadlag_cal/{calibration.json, manifest.json}, and
      experiments/ext/r4leadlag/frozen_r4leadlag.json = experiments/ext/v51/frozen_v4_v51.json (verbatim keys)
      + the new tolerant_v5_1_leadlag|T|kind keys.
  python experiments/ext/r4leadlag/drive.py run --config experiments/configs/ext_r4leadlag_eval_<x>.json --workers 3
      the runner's main phase with the frozen factors of the config (no re-calibration); writes
      results/<name>/{runs.jsonl, skeletons.jsonl, calibration.json, summary.md, manifest.json}.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import worker as W  # noqa: E402

RE = W.RE
ROOT = W.ROOT
from paper4.topology import load_bank  # noqa: E402

FROZEN_V51 = ROOT / "experiments" / "ext" / "v51" / "frozen_v4_v51.json"
FROZEN_LL = HERE / "frozen_r4leadlag.json"
CLEAN_CFG = ROOT / "experiments" / "configs" / "ext_r4leadlag_eval_clean.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def calibrate(workers: int) -> None:
    cfg = json.loads(CLEAN_CFG.read_text())
    out = ROOT / "results" / "ext_r4leadlag_cal"
    out.mkdir(parents=True, exist_ok=True)
    W.patch()
    RE.run_unit = W.run_unit_ll           # RE.calibrate maps RE.run_unit over the calibration units
    start = time.perf_counter()
    cal = RE.calibrate(cfg, workers)
    secs = round(time.perf_counter() - start, 1)
    (out / "calibration.json").write_text(json.dumps(cal, indent=2))
    mine = {k: v for k, v in cal.items() if k.split("|")[0] in W.NAMES}
    frozen = json.loads(FROZEN_V51.read_text())
    merged = {"_note": "r4leadlag: keys of experiments/ext/v51/frozen_v4_v51.json verbatim (tolerant_v4 mod|*, "
                       "tolerant_v5_1|*), plus tolerant_v5_1_leadlag(_skel)|T|kind tuned by drive.py calibrate on clean "
                       "D-07H development (results/ext_r4leadlag_cal/calibration.json).",
              **{k: v for k, v in frozen.items() if not k.startswith("_")}, **mine}
    FROZEN_LL.write_text(json.dumps(merged, indent=2))
    same = {k: (v, frozen.get("tolerant_v5_1|" + k.split("|", 1)[1])) for k, v in mine.items()}
    manifest = {"config": str(CLEAN_CFG.relative_to(ROOT)), "seconds": secs, "workers": workers,
                "calibration_bank": cfg["calibration"], "v51_frozen_sha256": sha(FROZEN_V51),
                "leadlag_vs_v51_factor": same}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


def run(config: Path, workers: int) -> None:
    cfg = json.loads(config.read_text())
    assert cfg["bank"] == "D-07" and cfg["split"] == "development", "evaluation is D-07 development only"
    assert cfg["calibration"]["bank"] == "D-07H" and cfg["calibration"]["split"] == "development"
    out = ROOT / "results" / cfg["name"]
    out.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    frozen = json.loads((ROOT / cfg["frozen_calibration"]).read_text())
    calib_c = {k: v for k, v in frozen.items() if not k.startswith("_")}
    (out / "calibration.json").write_text(json.dumps(calib_c, indent=2))
    topologies = load_bank(cfg["bank"], cfg["split"])[: cfg.get("max_topologies") or None]
    jobs = [(cfg, topo, t_idx, rep, calib_c, "main")
            for t_idx, topo in enumerate(topologies) for rep in range(cfg["replicates"])]
    rows, skels = [], []
    with ProcessPoolExecutor(workers) as pool:
        for res in pool.map(W.run_unit_ll, jobs):
            rows.extend(res["rows"])
            skels.extend(res["skeletons"])
    with open(out / "runs.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    with open(out / "skeletons.jsonl", "w", encoding="utf-8") as fh:
        for s in skels:
            fh.write(json.dumps(s) + "\n")
    (out / "summary.md").write_text(RE.summarize(rows, cfg), encoding="utf-8")
    files = ["src/paper4/ext_r4leadlag.py", "src/paper4/ext_v51.py", "src/paper4/ext_narrow.py",
             "src/paper4/methods.py", "src/paper4/estimator.py", "experiments/run_experiment.py",
             "experiments/ext/r4leadlag/worker.py", "experiments/ext/r4leadlag/drive.py", cfg["frozen_calibration"]]
    manifest = {"config": cfg, "seconds": round(time.perf_counter() - start, 1), "n_rows": len(rows),
                "workers": workers, "driver": "experiments/ext/r4leadlag/drive.py",
                "sha256": {f: sha(ROOT / f) for f in files},
                "topologies": [{"id": t.id, "profile": t.profile, "sha256": t.sha256} for t in topologies]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"{len(rows)} rows in {manifest['seconds']} s -> {out}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["calibrate", "run"])
    ap.add_argument("--config")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    if a.mode == "calibrate":
        calibrate(a.workers)
    else:
        run(Path(a.config).resolve(), a.workers)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
