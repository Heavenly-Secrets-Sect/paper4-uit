"""Lead guard for the single P4-H2 run (docs/ext/synthesis_round3.md, section 3).

Covers the gaps the round-3 verifiers left to the lead:
  G1  interpreter is /Users/kietnt/miniconda3/bin/python with numpy 2.5.4, cwd is the repo root
  G2  PAPER4_TOPOLOGY_ROOT and PAPER4_ACIIDS_ROOT are unset (topology.bank_root / learned honour them)
  G3  the set of src/paper4/*.py equals the set frozen in p4h2_plan_files.json (no new or missing ext_*.py)
  G4  every file in p4h2_plan_files.json (all src/paper4/*.py, runner, every file of the P1, P2 and P7 spec
      manifests, the three spec docs, ACIIDS GES files) has the sha256 frozen in the plan
  G5  every file still has the sha256 recorded by its OWN spec at freeze time
      (P7: baselines3 manifest; P1: v51fix manifest; P2: results/ext_auto3fix_dryrun/spec_sha256_at_writing.txt)
  G6  the four P4-H2 configs say bank P4-H2 / split confirmatory and seed_base 20261102
  G7  (pre) no output directory of any P4-H2 spec exists, and no results/*/manifest.json has bank P4-H2
      (post) exactly the expected run directories have bank P4-H2 manifests
  G8  sha256 of data/topology_bank/P4-H2/p4h2_manifest.json equals the value in PROVENANCE.md
      (raw bytes only; skipped with --test, which never touches P4-H2)

Usage (from the repo root, see the plan for the full sequence):
  /Users/kietnt/miniconda3/bin/python experiments/ext/synthesis_round3/lead_guard.py --phase pre
  /Users/kietnt/miniconda3/bin/python experiments/ext/synthesis_round3/lead_guard.py --phase post
  python3 experiments/ext/synthesis_round3/lead_guard.py --phase pre --test     # self-test, no P4-H2
  python3 experiments/ext/synthesis_round3/lead_guard.py --freeze              # (re)write the plan hashes

Exit code 0 and the line 'LEAD GUARD PASS' only if every check passes.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import sys
import time
from pathlib import Path

REPO = Path("/Users/kietnt/Desktop/Workspace/Paper4_UIT")
HERE = REPO / "experiments/ext/synthesis_round3"
PLAN = HERE / "p4h2_plan_files.json"
INTERP = "/Users/kietnt/miniconda3/bin/python"
NUMPY = "2.5.4"
P4H2_MANIFEST = "data/topology_bank/P4-H2/p4h2_manifest.json"
P4H2_EXPECTED = "0b7e6579ae85379149c115a18a38eb7178e71f7decc9a15c1a6c5eadaaa1c7d8"
ENV_VARS = ["PAPER4_TOPOLOGY_ROOT", "PAPER4_ACIIDS_ROOT"]

SPEC_MANIFESTS = {
    "P1": "experiments/ext/v51fix/p4h2_spec_files.json",
    "P2": "experiments/ext/auto3fix/p4h2_spec_files.json",
    "P7": "experiments/ext/baselines3/p4h2_spec_files.json",
}
P2_WRITING_HASHES = "results/ext_auto3fix_dryrun/spec_sha256_at_writing.txt"
SPEC_DOCS = ["docs/ext/v51fix.md", "docs/ext/auto3fix.md", "docs/ext/baselines3.md"]
LEAD_FILES = ["experiments/ext/synthesis_round3/v4_identity.py"]
CONFIGS = {
    "P1": "experiments/configs/ext_v51fix_p4h2.json",
    "P2c1": "experiments/configs/ext_auto3fix_p4h2_auto3.json",
    "P2c2": "experiments/configs/ext_auto3fix_p4h2_auto3_latent1.json",
    "P7": "experiments/configs/ext_baselines3_p4h2.json",
}
RUN_DIRS = ["results/ext_v51fix_p4h2", "results/ext_auto3fix_p4h2_auto3",
            "results/ext_auto3fix_p4h2_auto3_latent1", "results/ext_baselines3_p4h2"]
OTHER_OUTPUTS = ["results/ext_v51fix_p4h2_preflight", "results/ext_auto3fix_p4h2_check",
                 "results/ext_auto3fix_p4h2_check_preflight.json", "results/ext_synthesis_round3_p4h2_v4identity"]
# superseded or excluded specs: must never have outputs
FORBIDDEN = ["results/ext_v51_p4h2", "results/ext_auto5_p4h2_auto3", "results/ext_auto5_p4h2_auto3_latent1",
             "results/ext_baselines2_p4h2", "results/ext_tlp2_p4h2", "results/ext_tlp3_p4h2",
             "results/ext_tlp3_p4h2_verdict", "results/ext_revlag_p4h2", "results/ext_revlag3_p4h2"]


def sha(path: str) -> str:
    p = Path(path) if os.path.isabs(path) else REPO / path
    if not p.exists():
        return "MISSING"
    return hashlib.sha256(p.read_bytes()).hexdigest()


def spec_freeze_hashes() -> dict[str, dict[str, str]]:
    """Hashes each spec recorded for itself at freeze time."""
    out: dict[str, dict[str, str]] = {}
    m = json.loads((REPO / SPEC_MANIFESTS["P7"]).read_text())
    d = {p: v["sha256"] for p, v in m["files"].items()}
    d.update(m.get("other_ext_modules_imported_by_runner", {}))
    out["P7"] = d
    m = json.loads((REPO / SPEC_MANIFESTS["P1"]).read_text())
    d = {f["path"]: f["sha256_at_freeze"] for f in m["files"] if f.get("sha256_at_freeze")}
    d.update(m.get("other_ext_modules_at_freeze_informational", {}))
    out["P1"] = d
    d = {}
    for line in (REPO / P2_WRITING_HASHES).read_text().splitlines():
        if line.strip():
            s, p = line.split(None, 1)
            d[p.strip()] = s
    out["P2"] = d
    return out


def plan_file_list() -> list[str]:
    files = set(sorted(str(Path(p).relative_to(REPO)) for p in glob.glob(str(REPO / "src/paper4/*.py"))))
    files.add("experiments/run_experiment.py")
    for spec in spec_freeze_hashes().values():
        files.update(spec)
    files.update(SPEC_MANIFESTS.values())
    files.add(P2_WRITING_HASHES)
    files.update(SPEC_DOCS)
    files.update(CONFIGS.values())
    files.update(LEAD_FILES)
    files.discard(P4H2_MANIFEST)
    return sorted(files)


def freeze() -> None:
    files = plan_file_list()
    hashes = {f: sha(f) for f in files}
    missing = [f for f, h in hashes.items() if h == "MISSING"]
    if missing:
        sys.exit(f"cannot freeze, missing files: {missing}")
    plan = {
        "id": "synthesis_round3",
        "doc": "docs/ext/synthesis_round3.md (section 3: final P4-H2 run plan)",
        "frozen_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "interpreter": {"path": INTERP, "numpy": NUMPY},
        "env_must_be_unset": ENV_VARS,
        "src_paper4_py_set": sorted(f for f in files if f.startswith("src/paper4/") and f.count("/") == 2),
        "p4h2_bank_manifest": {"path": P4H2_MANIFEST, "expected_sha256": P4H2_EXPECTED,
                               "source": "data/topology_bank/PROVENANCE.md; hashed by the lead guard only"},
        "spec_manifests": SPEC_MANIFESTS,
        "configs": CONFIGS,
        "run_dirs": RUN_DIRS,
        "other_outputs": OTHER_OUTPUTS,
        "forbidden_outputs": FORBIDDEN,
        "excluded_specs": {
            "P3/P4 (revlag3)": "incomplete: no spec manifest, no rule section in docs/ext/revlag3.md (verify3_revlag3)",
            "P5 (tlp3)": "incomplete: analyzer/doc coverage ambiguity and realisation check on superseded run (verify3_tlp3)",
            "P6 (baselines2)": "superseded by P7",
        },
        "commands": [
            "cd /Users/kietnt/Desktop/Workspace/Paper4_UIT && unset PAPER4_TOPOLOGY_ROOT PAPER4_ACIIDS_ROOT",
            "/Users/kietnt/miniconda3/bin/python experiments/ext/synthesis_round3/lead_guard.py --phase pre",
            "/Users/kietnt/miniconda3/bin/python experiments/ext/v51fix/preflight_p4h2.py",
            "/Users/kietnt/miniconda3/bin/python experiments/ext/auto3fix/preflight_p4h2.py --hashes results/ext_auto3fix_dryrun/spec_sha256_at_writing.txt --out results/ext_auto3fix_p4h2_check_preflight.json",
            "/Users/kietnt/miniconda3/bin/python experiments/run_experiment.py --config experiments/configs/ext_v51fix_p4h2.json --workers 3",
            "/Users/kietnt/miniconda3/bin/python experiments/run_experiment.py --config experiments/configs/ext_auto3fix_p4h2_auto3.json --workers 3",
            "/Users/kietnt/miniconda3/bin/python experiments/run_experiment.py --config experiments/configs/ext_auto3fix_p4h2_auto3_latent1.json --workers 3",
            "/Users/kietnt/miniconda3/bin/python experiments/ext/baselines3/run_cells.py --config experiments/configs/ext_baselines3_p4h2.json --workers 3",
            "/Users/kietnt/miniconda3/bin/python experiments/ext/synthesis_round3/lead_guard.py --phase post",
            "/Users/kietnt/miniconda3/bin/python experiments/ext/v51fix/rule_p4h2_v2.py",
            "/Users/kietnt/miniconda3/bin/python experiments/ext/auto3fix/check_p4h2_v2.py",
            "/Users/kietnt/miniconda3/bin/python experiments/ext/baselines3/analyze_p4h2.py",
            "/Users/kietnt/miniconda3/bin/python experiments/ext/synthesis_round3/v4_identity.py",
        ],
        "files": hashes,
    }
    PLAN.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print(f"froze {len(hashes)} files -> {PLAN.relative_to(REPO)}")


def p4h2_manifests_present() -> list[str]:
    found = []
    for mf in glob.glob(str(REPO / "results/*/manifest.json")):
        try:
            cfg = json.loads(Path(mf).read_text()).get("config", {})
        except Exception:
            continue
        if cfg.get("bank") == "P4-H2":
            found.append(str(Path(mf).parent.relative_to(REPO)))
    return sorted(found)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["pre", "post"])
    ap.add_argument("--test", action="store_true", help="self-test: skip G8 and interpreter pin, write elsewhere")
    ap.add_argument("--freeze", action="store_true")
    a = ap.parse_args()
    if a.freeze:
        freeze()
        return 0
    if not a.phase:
        ap.error("--phase required")
    plan = json.loads(PLAN.read_text())
    checks = []

    def add(name, ok, note=""):
        checks.append({"check": name, "ok": bool(ok), "note": note})

    import numpy  # noqa: E402
    exe = os.path.realpath(sys.executable)
    ok_interp = exe == os.path.realpath(INTERP) and numpy.__version__ == NUMPY
    add("G1 interpreter", ok_interp or a.test,
        f"{sys.executable} (python {sys.version.split()[0]}, numpy {numpy.__version__})" + (" [not enforced in --test]" if a.test else ""))
    add("G1 cwd", Path.cwd().resolve() == REPO.resolve(), str(Path.cwd()))

    env_set = [v for v in ENV_VARS if v in os.environ]
    add("G2 env", not env_set, f"set: {env_set}" if env_set else "unset")

    now_set = sorted(str(Path(p).relative_to(REPO)) for p in glob.glob(str(REPO / "src/paper4/*.py")))
    add("G3 src/paper4/*.py set", now_set == plan["src_paper4_py_set"],
        f"new: {sorted(set(now_set) - set(plan['src_paper4_py_set']))}; missing: {sorted(set(plan['src_paper4_py_set']) - set(now_set))}")

    cur = {f: sha(f) for f in plan["files"]}
    diff = [f for f, h in plan["files"].items() if cur[f] != h]
    add("G4 plan hashes", not diff, f"{len(cur) - len(diff)}/{len(cur)} match" + (f"; differ: {diff}" if diff else ""))

    for spec, d in spec_freeze_hashes().items():
        dd = [p for p, h in d.items() if sha(p) != h]
        add(f"G5 {spec} own freeze hashes", not dd, f"{len(d) - len(dd)}/{len(d)} match" + (f"; differ: {dd}" if dd else ""))

    bad_cfg = []
    for k, c in CONFIGS.items():
        cfg = json.loads((REPO / c).read_text())
        if not (cfg.get("bank") == "P4-H2" and cfg.get("split") == "confirmatory" and cfg.get("seed_base") == 20261102):
            bad_cfg.append(k)
    add("G6 configs", not bad_cfg, f"bad: {bad_cfg}" if bad_cfg else "4/4 P4-H2 confirmatory, seed_base 20261102")

    present = [p for p in p4h2_manifests_present()]
    exists = lambda p: (REPO / p).exists()  # noqa: E731
    forb = [p for p in FORBIDDEN if exists(p)]
    if a.phase == "pre":
        pre_out = [p for p in RUN_DIRS + OTHER_OUTPUTS if exists(p)]
        add("G7 outputs absent", not pre_out and not forb, f"exist: {pre_out + forb}" if (pre_out or forb) else "none exist")
        add("G7 no P4-H2 manifests", not present, f"found: {present}" if present else "none")
    else:
        add("G7 run dirs present", all(exists(p + "/runs.jsonl") for p in RUN_DIRS),
            str({p: exists(p + "/runs.jsonl") for p in RUN_DIRS}))
        add("G7 P4-H2 manifests == run dirs", present == sorted(RUN_DIRS) and not forb,
            f"found: {present}; forbidden present: {forb}")

    if a.test:
        add("G8 P4-H2 bank manifest", True, "skipped in --test (P4-H2 not touched)")
    else:
        prov = (REPO / "data/topology_bank/PROVENANCE.md").read_text()
        raw = (REPO / P4H2_MANIFEST).read_bytes()
        h_raw = hashlib.sha256(raw).hexdigest()
        h_lf = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
        add("G8 P4-H2 bank manifest", P4H2_EXPECTED in prov and P4H2_EXPECTED in (h_raw, h_lf),
            f"raw {h_raw}; lf {h_lf}; expected {P4H2_EXPECTED} (in PROVENANCE.md: {P4H2_EXPECTED in prov})")

    ok = all(c["ok"] for c in checks)
    outdir = REPO / ("results/ext_synthesis_round3_guardtest" if a.test else "results/ext_synthesis_round3_p4h2_guard")
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / f"{a.phase}.json"
    if out.exists() and not a.test:
        print(f"{out} already exists: guard phase '{a.phase}' was already run; stop and report", file=sys.stderr)
        return 2
    res = {"phase": a.phase, "test": a.test, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "plan_sha256": sha(str(PLAN)), "ok": ok, "checks": checks, "sha256": cur}
    out.write_text(json.dumps(res, indent=2), encoding="utf-8")
    (outdir / f"hashes_{a.phase}.txt").write_text("".join(f"{h}  {f}\n" for f, h in sorted(cur.items())), encoding="utf-8")
    for c in checks:
        print(("PASS " if c["ok"] else "FAIL ") + c["check"] + ": " + c["note"][:300])
    print("LEAD GUARD PASS" if ok else "LEAD GUARD FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
