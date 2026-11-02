"""Writes experiments/ext/baselines3/p4h2_spec_files.json: every file spec P7 depends on, its role, and its sha256 at
freeze time (the lead re-hashes all of them right before the run). Does not open any P4-H2 data file."""
import hashlib, json, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
FILES = {
 "experiments/run_experiment.py": "runner (unchanged; bug E1 not fixed, see doc)",
 "experiments/ext/baselines3/run_cells.py": "wrapper: cell subset with positions kept, skip_calibration, expected_modules guard, baselines3_manifest.json",
 "experiments/configs/ext_baselines3_p4h2.json": "frozen confirmatory config (bank P4-H2, split confirmatory)",
 "experiments/ext/baselines3/frozen_calibration_p7.json": "combined frozen width factors (all D-07H development)",
 "experiments/ext/baselines3/p7_win_set.json": "W_D07(m): comparisons tested on P4-H2 (from D-07 development, Holm)",
 "experiments/ext/baselines3/analyze.py": "scoring functions (imported by analyze_p4h2.py)",
 "experiments/ext/baselines3/analyze_p4h2.py": "confirmatory analyzer",
 "src/paper4/ext_baselines3.py": "pselect_union_v3, pselect_union_v3_cal, pselect_cal, fullvar_cal",
 "src/paper4/ext_baselines2.py": "bvar_minnesota_v2_cal",
 "src/paper4/ext_tlp.py": "targeted_lp, targeted_lp_cal (cache path)",
 "src/paper4/ext_tlp2.py": "tlp2_db_p3",
 "src/paper4/ext_v51.py": "tolerant_v5_1 (TAU = 6.6083)",
 "src/paper4/ext_narrow.py": "imported by ext_v51 (select_open, opened_terms, _prescale)",
 "src/paper4/__init__.py": "package",
 "src/paper4/methods.py": "tolerant_v3/v4, pselect_union, calibrate_width",
 "src/paper4/estimator.py": "fits and bootstrap", "src/paper4/metrics.py": "scoring", "src/paper4/generator.py": "data",
 "src/paper4/skeleton.py": "skeletons and damage", "src/paper4/effects.py": "IRF, C(H)", "src/paper4/topology.py": "bank loader",
 "src/paper4/diagnose.py": "structural_pvalues (pselect_union_v3, bvar seeds none)",
 "experiments/calibration/tolerant_v4_frozen.json": "provenance of mod|* (values copied into frozen_calibration_p7.json; not read at run time)",
 "experiments/ext/v51/frozen_v4_v51.json": "provenance of tolerant_v5_1|* (copied; not read at run time)",
 "results/ext_redteam_calbase/calibration.json": "provenance of pselect_cal|*, fullvar_cal|* (copied)",
 "results/ext_tlp_eval/calibration.json": "provenance of targeted_lp_cal|* (copied)",
 "results/ext_baselines2_eval/calibration.json": "provenance of bvar_minnesota_v2_cal|* (copied)",
 "results/ext_baselines3_cal/calibration.json": "provenance of pselect_union_v3_cal|* (copied)",
}
sha = lambda p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
others = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "src/paper4").glob("ext_*.py") if str(p.relative_to(ROOT)) not in FILES)
PY = "/Users/kietnt/miniconda3/bin/python"
man = {
 "spec": "P7 (R3-1, baselines3): tolerant_v4 and tolerant_v5_1 vs full-budget baseline envelope; docs/ext/baselines3.md",
 "frozen_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
 "files": {p: {"role": r, "sha256": sha(p)} for p, r in FILES.items()},
 "other_ext_modules_imported_by_runner": {p: sha(p) for p in others},
 "other_ext_modules_note": "The runner imports every src/paper4/ext_*.py. They cannot change P7 methods unless they register the same names (the wrapper aborts if any P7 method is registered by another module: expected_modules) or monkeypatch shared modules; the lead should hash all src/paper4/*.py at run time.",
 "data_not_opened": ["data/topology_bank/P4-H2/p4h2_manifest.json (lead hashes it; expected sha256 in data/topology_bank/PROVENANCE.md)"],
 "interpreter": PY + " (numpy 2.5.4); the D-07 dry run used /usr/bin/python3 (CLT, numpy 2.0.2); identical outputs on a D-07H check (results/ext_baselines3_budget/interpreter_check.json)",
 "commands": [
   f"{PY} experiments/ext/baselines3/run_cells.py --config experiments/configs/ext_baselines3_p4h2.json --workers 3",
   f"{PY} experiments/ext/baselines3/analyze_p4h2.py"],
 "precondition": "results/ext_baselines3_p4h2/ must not exist before the run (single run); if it is interrupted before runs.jsonl is written, rerun once with the same config and disclose",
 "expected_rows": 2400,
 "expected_runtime_workers3": "see docs/ext/baselines3.md section 6 (filled from the D-07 run)",
 "confirmatory_rule": "see docs/ext/baselines3.md section 3.5 / analyze_p4h2.py docstring",
}
(ROOT / "experiments/ext/baselines3/p4h2_spec_files.json").write_text(json.dumps(man, indent=1))
print(len(man["files"]), "files;", len(others), "other ext modules")
