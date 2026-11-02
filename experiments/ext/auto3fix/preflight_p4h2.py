"""Preflight of the corrected tolerant_auto3 P4-H2 spec (ID auto3fix, docs/ext/auto3fix.md 1.1).

Run by the lead IMMEDIATELY before the two P4-H2 configs. It reads code, configs and the two frozen
JSON tables only; it never loads a topology bank and never simulates data.

Checks (prints PREFLIGHT OK only if all hold; exit code 1 otherwise):
  P1 the runner's ext_methods()['tolerant_auto3'] comes from paper4.ext_gate (guard against bug E4);
  P2 no other ext_* module registers tolerant_auto3, and no ext_* module registers a built-in name the
     configs use (plugin, oracle, tolerant_v3, tolerant_v4): the runner lets an ext method override a
     built-in of the same name;
  P3 the width table and the frozen v4 factors have exactly the pinned contents;
  P4 the two configs are the frozen ones (name, bank P4-H2 / confirmatory, methods, frozen
     calibration, seed_base, grid), and differ from the round-2 configs only in name and purpose;
  P5 the ACIIDS GES used by the GES cell imports;
  P6 (optional, --hashes FILE) the sha256 of every file of experiments/ext/auto3fix/p4h2_spec_files.json
     equals the lead's recorded hash. FILE is JSON {path: sha256} or sha256sum text "<sha>  <path>".
It also prints the interpreter, numpy version and the sha256 of every spec file (bug E6: the runner's
manifest does not record them).

Usage: python experiments/ext/auto3fix/preflight_p4h2.py [--hashes FILE] [--out FILE.json]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
import pkgutil
import platform
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPEC = ROOT / "experiments" / "ext" / "auto3fix" / "p4h2_spec_files.json"
CFG1 = ROOT / "experiments" / "configs" / "ext_auto3fix_p4h2_auto3.json"
CFG2 = ROOT / "experiments" / "configs" / "ext_auto3fix_p4h2_auto3_latent1.json"
OLD1 = ROOT / "experiments" / "configs" / "ext_auto5_p4h2_auto3.json"
OLD2 = ROOT / "experiments" / "configs" / "ext_auto5_p4h2_auto3_latent1.json"
WIDTH_EXPECTED = {"closed|150": 1.3, "closed|40": 1.5, "closed|80": 1.3, "nogate|150": 1.2, "nogate|40": 1.0,
                  "nogate|80": 1.2, "open|150": 1.3, "open|40": 1.0, "open|80": 1.2}
FROZEN_EXPECTED = {"mod|40|none": 1.4, "mod|40|extra": 1.3, "mod|40|missing": 1.0, "mod|40|reversed": 1.4,
                   "mod|80|none": 1.3, "mod|80|extra": 1.3, "mod|80|missing": 1.3, "mod|80|reversed": 1.4,
                   "mod|150|none": 1.2, "mod|150|extra": 1.2, "mod|150|missing": 1.2, "mod|150|reversed": 1.3,
                   "mod|300|none": 1.1, "mod|300|extra": 1.1, "mod|300|missing": 1.1, "mod|300|reversed": 1.3}
BUILTIN_USED = ("plugin", "oracle", "tolerant_v3", "tolerant_v4")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def spec_paths() -> list[Path]:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    out = []
    for group in spec["files"].values():
        for f in group:
            p = Path(f["path"])
            out.append(p if p.is_absolute() else ROOT / p)
    return out


def read_hashes(path: Path) -> dict:
    txt = path.read_text(encoding="utf-8")
    try:
        d = json.loads(txt)
        return {str(k): v for k, v in d.items()}
    except json.JSONDecodeError:
        d = {}
        for line in txt.splitlines():
            if line.strip():
                h, p = line.split(None, 1)
                d[p.strip().lstrip("*")] = h
        return d


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hashes")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    res = {"python": sys.executable, "python_version": platform.python_version(), "platform": platform.platform()}
    import numpy
    res["numpy"] = numpy.__version__
    checks = []

    # P1 / P2: method provenance as the runner sees it
    spec = importlib.util.spec_from_file_location("p4_runner", ROOT / "experiments" / "run_experiment.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)  # adds src/ to sys.path; main() is not called
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        ext = runner.ext_methods()
    res["ext_load_warnings"] = [str(x.message) for x in w]
    fn = ext.get("tolerant_auto3")
    checks.append({"check": "P1", "ok": fn is not None and fn.__module__ == "paper4.ext_gate",
                   "note": f"tolerant_auto3 -> {getattr(fn, '__module__', None)}.{getattr(fn, '__name__', None)}"})
    import paper4
    owners, probs = {}, []
    for mod in sorted(pkgutil.iter_modules(paper4.__path__), key=lambda m: m.name):
        if not mod.name.startswith("ext_"):
            continue
        try:
            names = list(importlib.import_module(f"paper4.{mod.name}").METHODS)
        except Exception as exc:  # noqa: BLE001  (the runner skips such modules too)
            owners[mod.name] = f"NOT LOADED: {exc!r}"
            continue
        owners[mod.name] = names
        if "tolerant_auto3" in names and mod.name != "ext_gate":
            probs.append(f"{mod.name} also registers tolerant_auto3")
        for b in BUILTIN_USED:
            if b in names:
                probs.append(f"{mod.name} registers built-in name {b}")
    res["ext_modules"] = owners
    checks.append({"check": "P2", "ok": not probs, "note": "; ".join(probs) or f"{len(owners)} ext modules, no collision"})

    # P3 frozen tables
    import paper4.ext_gate as G
    width = json.loads(G.WIDTH_TABLE.read_text(encoding="utf-8"))
    frozen = json.loads((ROOT / "experiments/calibration/tolerant_v4_frozen.json").read_text(encoding="utf-8"))
    fz = {k: v for k, v in frozen.items() if not k.startswith("_")}
    ok3 = (G.WIDTH_TABLE.resolve() == (ROOT / "experiments/ext/gate/width_table.json").resolve()
           and width == WIDTH_EXPECTED and fz == FROZEN_EXPECTED
           and (G.ALPHA_GATE, G.Q_BH, G.FLIP_PROB) == (0.10, 0.10, 0.2))
    checks.append({"check": "P3", "ok": ok3, "note": f"width table {G.WIDTH_TABLE}; alpha_gate {G.ALPHA_GATE}, q {G.Q_BH}, flip {G.FLIP_PROB}"})

    # P4 configs
    c1, c2 = (json.loads(p.read_text(encoding="utf-8")) for p in (CFG1, CFG2))
    o1, o2 = (json.loads(p.read_text(encoding="utf-8")) for p in (OLD1, OLD2))
    strip = lambda c: {k: v for k, v in c.items() if k not in ("name", "purpose")}  # noqa: E731
    probs = []
    for c, name, methods, T in ((c1, "ext_auto3fix_p4h2_auto3", ["plugin", "tolerant_v4", "tolerant_auto3"], [40, 80, 150]),
                                (c2, "ext_auto3fix_p4h2_auto3_latent1", ["oracle", "plugin", "tolerant_v4", "tolerant_auto3"], [80, 150])):
        if c["name"] != name or c["bank"] != "P4-H2" or c["split"] != "confirmatory" or c["methods"] != methods \
                or c["T"] != T or c["seed_base"] != 20261102 or c["replicates"] != 3 or c["n_boot"] != 199 \
                or c["frozen_calibration"] != "experiments/calibration/tolerant_v4_frozen.json" \
                or c.get("calibrate_methods"):
            probs.append(f"{name}: unexpected content")
    if c1["damage"] != {"kinds": ["extra", "missing", "reversed"], "rates": [0.2, 0.5]} or c1.get("learned") != {"algorithm": "ges"}:
        probs.append("config 1 grid changed")
    if c2["damage"] != {"kinds": ["missing", "reversed"], "rates": [0.2]} or [s["name"] for s in c2["scenarios"]] != ["clean", "latent1"]:
        probs.append("config 2 grid changed")
    if strip(c1) != strip(o1) or strip(c2) != strip(o2) or list(c1) != list(o1) or list(c2) != list(o2):
        probs.append("new configs differ from the round-2 configs beyond name/purpose")
    checks.append({"check": "P4", "ok": not probs, "note": "; ".join(probs) or "configs as frozen (round-2 content, new name/purpose)"})

    # P5 GES import
    try:
        from paper4.learned import _ges_class
        g = _ges_class()
        checks.append({"check": "P5", "ok": True, "note": f"GES class {g.__module__}.{g.__name__} from {sys.modules[g.__module__].__file__}"})
    except Exception as exc:  # noqa: BLE001
        checks.append({"check": "P5", "ok": False, "note": f"GES import failed: {exc!r}"})

    # spec hashes (+ P6)
    hashes = {}
    for p in spec_paths():
        rel = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
        hashes[rel] = sha256(p) if p.exists() else "MISSING"
    res["sha256"] = hashes
    missing = [k for k, v in hashes.items() if v == "MISSING"]
    if missing:
        checks.append({"check": "P0", "ok": False, "note": f"spec files missing: {missing}"})
    if a.hashes:
        want = read_hashes(Path(a.hashes))
        diff = [k for k, v in hashes.items() if want.get(k) != v]
        checks.append({"check": "P6", "ok": not diff, "note": f"{len(hashes) - len(diff)}/{len(hashes)} hashes match" + (f"; differ: {diff}" if diff else "")})
    res["checks"] = checks
    res["ok"] = all(c["ok"] for c in checks)
    for k in ("python", "python_version", "numpy", "platform"):
        print(f"{k}: {res[k]}")
    for c in checks:
        print(f"{c['check']}: {'OK' if c['ok'] else 'FAIL'}: {c['note']}")
    if res["ext_load_warnings"]:
        print("ext load warnings:", res["ext_load_warnings"])
    print("PREFLIGHT OK" if res["ok"] else "PREFLIGHT FAILED")
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1), encoding="utf-8")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
