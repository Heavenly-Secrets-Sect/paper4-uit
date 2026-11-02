"""Run a config through the unmodified runner (experiments/run_experiment.py) on a SUBSET of the damage
cells while keeping every cell's POSITION, and optionally with a frozen calibration only.

Why (bug E1, docs/ext/synthesis_round2.md section 6): built-in methods and runner-seeded ext methods draw
from rng([unit, 3, T, c_idx, tag]) with c_idx the position of the cell in ["none"] + kinds x rates, and
the damaged skeletons from rng([unit, 1, k_idx]) with k_idx the position of the kind. Filtering the cell
dict (as experiments/ext/tlp2/run_cells.py does) shifts c_idx and changes the draws. Here the cell dict is
left untouched: in a cell that is not listed every method returns a cheap ``skipped_cell`` failure
WITHOUT computing anything, and the rows of unlisted cells are dropped from the output. Listed cells are
therefore computed with exactly the draws of a full-grid run of the same kinds list, which makes rows
pairable with stored a2-grid runs (D-07) and makes the P4-H2 rows of this config equal to the rows of
any other P4-H2 config with the same kinds list and seed_base (e.g. ext_v51_p4h2) at the same cells.

The cell test reads ``skel.damage['kind']`` / ``['rate']`` inside the HARNESS (public, stated
information), never inside a method. Methods are called exactly as by the runner.

Config keys read by this wrapper (ignored by the runner):
  "only_cells":      [[kind, rate], ...] cells of the MAIN phase to compute (default: all)
  "cal_only_cells":  [[kind, rate], ...] cells of the CALIBRATION phase to compute (default: all)
  "skip_calibration": true -> the runner's calibration phase is not run; every width factor must come
                      from "frozen_calibration" (the wrapper checks that each needed key exists first)
  "expected_modules": {method: module} -> abort unless each ext method is registered by that module
                      (guards against a later ext_* module silently overriding a name, bug E4)

Also writes results/<name>/baselines3_manifest.json: interpreter, numpy version, workers, sha256 of the
frozen calibration file and of every module of the methods used, the keys taken from the frozen file
(E5/E6 mitigation).

Usage: python experiments/ext/baselines3/run_cells.py --config <cfg.json> --workers 3
       python experiments/ext/baselines3/run_cells.py --config <cfg.json> --workers 3 --calibration-only
"""
import argparse
import hashlib
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

import run_experiment as R  # noqa: E402
from paper4 import methods as M  # noqa: E402

_KEEP = None          # set of (kind, rate) to compute in the current phase, or None = all


def _listed(skel) -> bool:
    if _KEEP is None:
        return True
    d = skel.damage or {}
    return (d.get("kind", "none"), round(float(d.get("rate", 0.0) or 0.0), 6)) in _KEEP


def _guard(fn, name):
    def wrapped(data, skel, *a, **k):
        if not _listed(skel):
            return M._failed(name, "skipped_cell")
        return fn(data, skel, *a, **k)
    wrapped.__wrapped__ = fn
    return wrapped


def _cellset(lst):
    return None if lst is None else {(k, round(float(r), 6)) for k, r in lst}


_orig_run_unit = R.run_unit


def run_unit_cells(args):
    global _KEEP
    cfg, topo, t_idx, rep, calib_c, phase = args
    _KEEP = _cellset(cfg.get("only_cells") if phase == "main" else cfg.get("cal_only_cells"))
    out = _orig_run_unit(args)
    if _KEEP is not None and phase == "main":
        out["rows"] = [r for r in out["rows"] if (r["kind"], round(float(r["rate"]), 6)) in _KEEP]
    _KEEP = None
    return out


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def install():
    """Patch the runner in this process (workers inherit it through fork)."""
    ext = R.ext_methods()
    R._EXT = {name: _guard(fn, name) for name, fn in ext.items()}
    M.plugin = _guard(M.plugin, "plugin")
    M.tolerant_v3 = _guard(M.tolerant_v3, "tolerant_v3")
    R.run_unit = run_unit_cells
    return ext


def check_frozen(cfg) -> dict:
    frozen = json.loads((ROOT / cfg["frozen_calibration"]).read_text(encoding="utf-8"))
    listed = cfg.get("only_cells") or [["none", 0.0]] + [[k, r] for k in cfg["damage"]["kinds"]
                                                          for r in cfg["damage"]["rates"]]
    # a damaged cell whose stated count rounds to 0 is keyed "none" by width_key, so "none" is always needed
    kinds = sorted({k for k, _ in listed} | {"none"})
    need = []
    for T in cfg["T"]:
        for kind in kinds:
            if "tolerant_v4" in cfg["methods"]:
                need.append(f"mod|{T}|{kind}")
            for m in cfg.get("calibrate_methods", []):
                need.append(f"{m}|{T}|{kind}")
    miss = [k for k in need if k not in frozen]
    if miss:
        raise SystemExit(f"frozen calibration lacks keys {miss}")
    return {k: frozen[k] for k in need}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--calibration-only", action="store_true")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    mp.set_start_method("fork", force=True)
    ext = install()
    for name, mod in (cfg.get("expected_modules") or {}).items():
        got = ext[name].__module__ if name in ext else None
        if got != mod:
            raise SystemExit(f"method {name} registered by {got}, expected {mod}")
    out = ROOT / "results" / cfg["name"]
    out.mkdir(parents=True, exist_ok=True)
    if a.calibration_only:
        t0 = time.perf_counter()
        cal = R.calibrate(cfg, a.workers)
        (out / "calibration.json").write_text(json.dumps(cal, indent=2), encoding="utf-8")
        (out / "calibration_run.json").write_text(json.dumps({"seconds": round(time.perf_counter() - t0, 1),
                                                              "workers": a.workers, "config": cfg}, indent=2))
        print(json.dumps(cal, indent=1))
        return 0
    used = {}
    if cfg.get("skip_calibration"):
        used = check_frozen(cfg)
        R.calibrate = lambda c, w: {}
    used_mods = sorted({ext[m].__module__ for m in cfg["methods"] if m in ext})
    files = {"experiments/run_experiment.py": _sha(ROOT / "experiments/run_experiment.py"),
             "experiments/ext/baselines3/run_cells.py": _sha(Path(__file__).resolve())}
    for mod in used_mods + ["paper4.methods", "paper4.estimator", "paper4.metrics", "paper4.generator",
                            "paper4.skeleton", "paper4.effects", "paper4.topology", "paper4.diagnose"]:
        rel = "src/" + mod.replace(".", "/") + ".py"
        files[rel] = _sha(ROOT / rel)
    if cfg.get("frozen_calibration"):
        files[cfg["frozen_calibration"]] = _sha(ROOT / cfg["frozen_calibration"])
    man = {"python": sys.executable, "numpy": np.__version__, "workers": a.workers,
           "start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "method_modules": {m: ext[m].__module__ for m in cfg["methods"] if m in ext},
           "frozen_keys_used": used, "sha256": files}
    (out / "baselines3_manifest.json").write_text(json.dumps(man, indent=2), encoding="utf-8")
    rc = R.main(["--config", a.config, "--workers", str(a.workers)])
    man["end_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (out / "baselines3_manifest.json").write_text(json.dumps(man, indent=2), encoding="utf-8")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
