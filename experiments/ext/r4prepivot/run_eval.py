"""Evaluation driver for r4prepivot. One config = one part.

Config keys: name, base_config (runner config of the stored run being paired with), factors (path of
the v5.1 width-factor JSON used for the tolerant_v5_1 comparator), bank, split, replicates (list of
replicate indices), cells ([T, kind, rate] list), scenarios (runner scenario dicts), b_o, b_i.

Run: /Users/kietnt/miniconda3/bin/python experiments/ext/r4prepivot/run_eval.py \
        --config experiments/configs/ext_r4prepivot_<part>.json --workers 3
Writes results/<name>/rows.jsonl and manifest.json (timing, config, topology hashes).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, load_cfg, run_dataset  # noqa: E402
from paper4.topology import load_bank  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args(argv)
    spec = json.loads(Path(a.config).read_text(encoding="utf-8"))
    assert spec["bank"] in ("D-07",) and spec["split"] == "development", "evaluation only on D-07 development"
    factors = json.loads((ROOT / spec["factors"]).read_text(encoding="utf-8"))
    cfg = load_cfg(spec["base_config"], factors)
    assert cfg["bank"] == spec["bank"] and cfg["split"] == spec["split"]
    topos = load_bank(spec["bank"], spec["split"])
    out = ROOT / "results" / spec["name"]
    out.mkdir(parents=True, exist_ok=True)
    jobs = [(cfg, topo, t_idx, rep, T, kind, float(rate), sc, spec["b_o"], spec["b_i"])
            for sc in spec["scenarios"] for (T, kind, rate) in spec["cells"]
            for t_idx, topo in enumerate(topos) for rep in spec["replicates"]]
    start = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    t0 = time.perf_counter()
    n = 0
    with open(out / "rows.jsonl", "w", encoding="utf-8") as fh, ProcessPoolExecutor(a.workers) as pool:
        for rows in pool.map(run_dataset, jobs, chunksize=1):
            for r in rows:
                fh.write(json.dumps(r) + "\n")
            n += 1
            if n % 60 == 0:
                print(f"{n}/{len(jobs)} datasets, {time.perf_counter() - t0:.0f} s", flush=True)
    manifest = {"spec": spec, "start_utc": start, "end_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "seconds": round(time.perf_counter() - t0, 1), "n_datasets": len(jobs), "workers": a.workers,
                "python": sys.executable,
                "topologies": [{"id": t.id, "sha256": t.sha256} for t in topos]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"{len(jobs)} datasets in {manifest['seconds']} s -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
