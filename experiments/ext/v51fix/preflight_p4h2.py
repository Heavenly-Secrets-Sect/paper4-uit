"""Preflight guard for the P4-H2 run of tolerant_v5_1, spec v2 (docs/ext/v51fix.md, "Frozen spec for P4-H2, v2").
Run it immediately before the sealed run; run the sealed run only if it prints "PREFLIGHT PASS" and exits 0.
It never loads a topology bank (no P4-H2 access) and never runs a method.

Checks:
 A. sha256 of every file in experiments/ext/v51fix/p4h2_spec_files.json equals the value recorded at freeze;
 B. method identity through the runner's own loader (bug E4): experiments/run_experiment.ext_methods()
    maps "tolerant_v5_1" to paper4.ext_v51.tolerant_v5_1 (``__module__ == 'paper4.ext_v51'``, same object);
    no ext_* module other than ext_v51 registers "tolerant_v5_1"; no ext_* module registers "tolerant_v4" or
    any other built-in name; ext_v51 loaded without error; TAU == 6.6083, PRESCALE == 0.5; every helper
    ext_v51 uses is the original object of its source module (no monkeypatching by another ext module);
 C. config and frozen factors: bank P4-H2 / confirmatory, methods, grid, seed, frozen file; mod|* factors of
    the frozen file equal experiments/calibration/tolerant_v4_frozen.json; 12 tolerant_v5_1 factors present;
 D. all-lag branch unreachable: for n = 14 and lag_max = 2, max r = (T - lag_max)/(1 + n*lag_max) < TAU at
    every T of the config (analytic; the analyzer re-checks r per run after the run);
 E. single run: results/ext_v51fix_p4h2/runs.jsonl does not exist yet, and the superseded spec's output
    results/ext_v51_p4h2 does not exist;
 F. interpreter: records sys.executable, numpy version, platform; WARN (not FAIL) if numpy != 2.5.4.
Writes results/ext_v51fix_p4h2_preflight/preflight.json (or --out).

Use: /Users/kietnt/miniconda3/bin/python experiments/ext/v51fix/preflight_p4h2.py
"""
import argparse
import hashlib
import importlib
import importlib.util
import json
import pkgutil
import platform
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPEC = ROOT / "experiments/ext/v51fix/p4h2_spec_files.json"
CONFIG = "experiments/configs/ext_v51fix_p4h2.json"
FROZEN = "experiments/ext/v51/frozen_v4_v51.json"
V4_FROZEN = "experiments/calibration/tolerant_v4_frozen.json"
BUILTIN = {"plugin", "inflate", "oracle", "bagging", "soft", "tolerant", "tolerant_v3", "tolerant_v4", "tolerant_v3_cal",
           "ida_union", "bvar_minnesota", "pselect_union", "tolerant_auto", "lp_allpast"}
EXPECTED_NUMPY = "2.5.4"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "results/ext_v51fix_p4h2_preflight/preflight.json"))
    ap.add_argument("--skip-hash", action="store_true", help="only for the pre-freeze self-test; never for the sealed run")
    a = ap.parse_args(argv)
    checks, warn = {}, []

    # A. hashes
    spec = json.loads(SPEC.read_text())
    mism = []
    for f in spec["files"]:
        if f.get("sha256_at_freeze") is None:   # hashed by the lead only (sealed bank): not opened here
            continue
        p = ROOT / f["path"]
        if not p.exists():
            mism.append(f"{f['path']}: missing")
        elif f.get("sha256_at_freeze") and sha256(p) != f["sha256_at_freeze"]:
            mism.append(f"{f['path']}: sha256 changed")
    checks["A hashes of spec files equal the freeze"] = True if a.skip_hash else not mism
    if a.skip_hash:
        warn.append("hash check skipped (--skip-hash): self-test only")

    # B. method identity through the runner's loader
    sys.path.insert(0, str(ROOT / "src"))
    spec_r = importlib.util.spec_from_file_location("run_experiment_preflight", ROOT / "experiments/run_experiment.py")
    R = importlib.util.module_from_spec(spec_r)
    spec_r.loader.exec_module(R)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        ext = R.ext_methods()
    load_warn = [str(x.message) for x in w if "not loaded" in str(x.message)]
    import paper4
    import paper4.ext_v51 as V51
    import paper4.ext_narrow as NAR
    import paper4.methods as METH
    import paper4.estimator as EST
    import paper4.effects as EFF
    import paper4.skeleton as SKL
    per_module, ext_hashes = {}, {}
    for mod in sorted(pkgutil.iter_modules(paper4.__path__), key=lambda m: m.name):
        if mod.name.startswith("ext_"):
            ext_hashes[mod.name] = sha256(ROOT / "src/paper4" / f"{mod.name}.py")
            try:
                per_module[mod.name] = sorted(importlib.import_module(f"paper4.{mod.name}").METHODS)
            except Exception as exc:  # noqa: BLE001
                per_module[mod.name] = f"LOAD ERROR {exc!r}"
    fn = ext.get("tolerant_v5_1")
    regs_v51 = [m for m, names in per_module.items() if isinstance(names, list) and "tolerant_v5_1" in names]
    regs_builtin = {m: sorted(set(names) & BUILTIN) for m, names in per_module.items()
                    if isinstance(names, list) and set(names) & BUILTIN}
    checks["B1 runner maps tolerant_v5_1 to paper4.ext_v51.tolerant_v5_1"] = (
        fn is not None and fn.__module__ == "paper4.ext_v51" and fn is V51.tolerant_v5_1)
    checks["B2 only ext_v51 registers tolerant_v5_1"] = regs_v51 == ["ext_v51"]
    checks["B3 no ext module registers a built-in name (tolerant_v4 etc.)"] = not regs_builtin
    checks["B4 ext_v51 loaded without error"] = not any("ext_v51 " in s or "ext_v51:" in s for s in load_warn) and \
        isinstance(per_module.get("ext_v51"), list)
    checks["B5 TAU == 6.6083 and PRESCALE == 0.5"] = V51.TAU == 6.6083 and NAR.PRESCALE == 0.5
    src_of = {"irf": EFF, "bootstrap_C": EST, "fit_equations": EST, "percentile_interval": EST, "_prescale": NAR,
              "opened_terms": NAR, "select_open": NAR, "ALPHA": METH, "MethodResult": METH, "_failed": METH,
              "_flip_from": METH, "_too_few": METH, "contemporaneous_pool": METH, "repair_candidates": METH,
              "stated_counts": METH, "tolerant": METH, "Skeleton": SKL, "_creates_cycle": SKL}
    patched = [n for n, mod in src_of.items() if getattr(V51, n) is not getattr(mod, n)]
    patched += [n for n in ("tolerant", "repair_candidates", "stated_counts")
                if getattr(METH, n).__module__ != "paper4.methods"]
    patched += [n for n in ("fit_equations", "bootstrap_C", "percentile_interval") if getattr(EST, n).__module__ != "paper4.estimator"]
    patched += [n for n in ("opened_terms", "select_open", "_prescale") if getattr(NAR, n).__module__ != "paper4.ext_narrow"]
    checks["B6 helpers used by ext_v51 are the original objects"] = not patched
    if load_warn:
        warn.append(f"ext modules not loaded (other names): {load_warn}")

    # C. config and frozen factors
    cfg = json.loads((ROOT / CONFIG).read_text())
    checks["C1 config: P4-H2 confirmatory, methods, grid, seed, frozen file"] = (
        cfg["name"] == "ext_v51fix_p4h2" and cfg["bank"] == "P4-H2" and cfg["split"] == "confirmatory"
        and cfg["methods"] == ["tolerant_v4", "tolerant_v5_1"] and cfg["calibrate_methods"] == ["tolerant_v5_1"]
        and cfg["frozen_calibration"] == FROZEN and cfg["T"] == [40, 80, 150] and cfg["seed_base"] == 20261102
        and cfg["n_boot"] == 199 and cfg["H"] == 4 and cfg["replicates"] == 3 and cfg["max_topologies"] is None
        and cfg["damage"] == {"kinds": ["extra", "missing", "reversed"], "rates": [0.2, 0.5]}
        and cfg["generator"]["lag_max"] == 2 and cfg["calibration"]["bank"] == "D-07H"
        and cfg["calibration"]["split"] == "development")
    fz = json.loads((ROOT / FROZEN).read_text())
    v4 = json.loads((ROOT / V4_FROZEN).read_text())
    kinds = ("none", "extra", "missing", "reversed")
    checks["C2 mod|* factors equal tolerant_v4_frozen.json"] = all(
        fz.get(f"mod|{T}|{k}") == v4.get(f"mod|{T}|{k}") and v4.get(f"mod|{T}|{k}") is not None for T in (40, 80, 150) for k in kinds)
    checks["C3 12 tolerant_v5_1 factors present"] = all(isinstance(fz.get(f"tolerant_v5_1|{T}|{k}"), (int, float))
                                                       for T in (40, 80, 150) for k in kinds)
    other = [k for k in fz if not k.startswith(("_", "mod|", "tolerant_v5_1|"))]
    checks["C4 frozen file overrides nothing else (bug E5)"] = not other

    # D. analytic bound on r
    n, lag = 14, cfg["generator"]["lag_max"]
    rmax = {T: (T - lag) / (1 + n * lag) for T in cfg["T"]}
    checks["D all-lag branch unreachable for n = 14 at every T of the config"] = all(r < V51.TAU for r in rmax.values())

    # E. single run
    checks["E1 results/ext_v51fix_p4h2/runs.jsonl does not exist yet"] = not (ROOT / "results/ext_v51fix_p4h2/runs.jsonl").exists()
    checks["E2 superseded spec output results/ext_v51_p4h2 does not exist"] = not (ROOT / "results/ext_v51_p4h2").exists()

    # F. interpreter
    import numpy
    interp = {"executable": sys.executable, "python": sys.version, "numpy": numpy.__version__, "platform": platform.platform()}
    if numpy.__version__ != EXPECTED_NUMPY:
        warn.append(f"numpy {numpy.__version__} != {EXPECTED_NUMPY} (the interpreter of the D-07 evaluation runs)")

    ok = all(checks.values())
    rep = {"when_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "pass": ok, "checks": checks,
           "hash_mismatches": mism, "warnings": warn, "interpreter": interp, "ext_modules_registrations": per_module,
           "ext_modules_sha256": ext_hashes, "r_max_analytic": rmax, "patched_helpers": patched,
           "builtin_overrides": regs_builtin}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(rep, indent=1))
    for k, v in checks.items():
        print(f"{'PASS' if v else 'FAIL'}  {k}")
    for m in mism:
        print(f"  mismatch: {m}")
    for x in warn:
        print(f"WARN  {x}")
    print(f"PREFLIGHT {'PASS' if ok else 'FAIL'} -> {a.out}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
