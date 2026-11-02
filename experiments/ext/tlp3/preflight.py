"""Preflight for the P5 (TLP) P4-H2 spec of docs/ext/tlp3.md. Run it IMMEDIATELY before
`run_experiment.py --config experiments/configs/ext_tlp3_p4h2.json`. It runs no method and reads no
data of any bank; it only imports the runner and its extension registry.

Checks (exit code 1 if any fails, and then the P4-H2 run must not start):
1. the runner's registry resolves every extension method of the config to the frozen module
   (targeted_lp -> paper4.ext_tlp; tlp2_db, tlp2_db_p3 -> paper4.ext_tlp2) -- bug E4: the runner
   imports every src/paper4/ext_*.py and a later module could silently overwrite a name;
2. no method name of the config is defined by more than one ext_* module;
3. the config file still names the frozen methods, grid, bank and frozen calibration;
4. sha256 of every file in experiments/ext/tlp3/p4h2_spec_files.json (written, not compared: the lead
   compares against the hash manifest made right before the run) plus every paper4 module that is
   loaded once the registry is imported (all ext_* modules included).

Usage: python3 experiments/ext/tlp3/preflight.py [--out results/ext_tlp3_preflight/preflight.json]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import pkgutil
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

CONFIG = "experiments/configs/ext_tlp3_p4h2.json"
EXPECTED_MODULE = {"targeted_lp": "paper4.ext_tlp", "tlp2_db": "paper4.ext_tlp2", "tlp2_db_p3": "paper4.ext_tlp2"}
EXPECTED_CFG = {
    "methods": ["tolerant_v4", "targeted_lp", "tlp2_db", "tlp2_db_p3"],
    "T": [80, 150],
    "damage": {"kinds": ["extra", "missing", "reversed"], "rates": [0.2, 0.5]},
    "bank": "P4-H2", "split": "confirmatory", "replicates": 3, "H": 4, "n_boot": 199,
    "seed_base": 20261102, "frozen_calibration": "experiments/calibration/tolerant_v4_frozen.json",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/ext_tlp3_preflight/preflight.json")
    cli = ap.parse_args()
    fails, out = [], {}

    cfg = json.loads((ROOT / CONFIG).read_text(encoding="utf-8"))
    for k, v in EXPECTED_CFG.items():
        if cfg.get(k) != v:
            fails.append(f"config key {k!r} = {cfg.get(k)!r}, expected {v!r}")
    if cfg.get("learned") or cfg.get("scenarios") or cfg.get("misstated") or cfg.get("calibrate_methods"):
        fails.append("config has learned/scenarios/misstated/calibrate_methods, which the spec does not allow")

    import paper4
    defined = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for mod in sorted(pkgutil.iter_modules(paper4.__path__), key=lambda m: m.name):
            if mod.name.startswith("ext_"):
                try:
                    m = importlib.import_module(f"paper4.{mod.name}")
                except Exception as exc:  # noqa: BLE001
                    out.setdefault("ext_import_errors", {})[mod.name] = repr(exc)
                    continue
                for name in getattr(m, "METHODS", {}):
                    defined.setdefault(name, []).append(m.__name__)
        import run_experiment as R
        reg = R.ext_methods()
    for name, want in EXPECTED_MODULE.items():
        got = reg[name].__module__ if name in reg else None
        if got != want:
            fails.append(f"registry: {name} -> {got}, expected {want}")
        if len(defined.get(name, [])) != 1:
            fails.append(f"method {name} defined by {defined.get(name)}")
    out["registry"] = {name: reg[name].__module__ for name in EXPECTED_MODULE if name in reg}
    out["duplicate_names_any_module"] = {k: v for k, v in defined.items() if len(v) > 1}

    spec = json.loads((ROOT / "experiments/ext/tlp3/p4h2_spec_files.json").read_text(encoding="utf-8"))
    out["spec_files_sha256"] = {f: (sha(ROOT / f) if (ROOT / f).exists() else "MISSING") for f in spec["files"]}
    for f, h in out["spec_files_sha256"].items():
        if h == "MISSING":
            fails.append(f"spec file missing: {f}")
    loaded = sorted(m for m in sys.modules if m == "paper4" or m.startswith("paper4."))
    out["loaded_paper4_modules_sha256"] = {
        m: sha(Path(sys.modules[m].__file__)) for m in loaded if getattr(sys.modules[m], "__file__", None)}
    import numpy
    out["python"] = sys.executable
    out["python_version"] = sys.version
    out["numpy"] = numpy.__version__
    out["fails"] = fails
    out["ok"] = not fails
    p = ROOT / cli.out
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"ok": out["ok"], "fails": fails, "registry": out["registry"],
                      "duplicate_names_any_module": out["duplicate_names_any_module"]}, indent=2))
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
