"""Confirmatory rule of tolerant_v5_1 on P4-H2, version 2 (docs/ext/v51fix.md, "Frozen spec for P4-H2, v2").
Supersedes experiments/ext/v51/rule_p4h2.py. Self-contained (numpy and the standard library only; it imports
nothing from the repo). Frozen before the run; do not change after the run.

Fixes against version 1 (round-2 verifier, docs/ext/synthesis_round2.md table 3.2, P1):
 (1) no import of experiments/ext/v51/common.py; every file the run and the rule depend on is listed with its
     sha256 in experiments/ext/v51fix/p4h2_spec_files.json and checked by preflight_p4h2.py;
 (2) validity checks that the rows come from paper4.ext_v51.tolerant_v5_1 with the frozen factors
     (fingerprint fields, per-row width factor, calibration.json against the frozen file, manifest config);
     the module identity itself (``__module__ == 'paper4.ext_v51'``, no overriding registration) is checked
     before the run by preflight_p4h2.py;
 (3) a cell with 0 ok runs no longer crashes: it fails its condition (NOT CONFIRMED); failure ceilings;
     the coverage gate counts failed runs of tolerant_v5_1 as covering none of their non-null pairs;
 (4) the all-lag branch (r >= TAU) is reported as unreachable and checked per run; tau fragility is stated.
 The multiplicity overlay across primary specs asked by the lead (section 3.3) is reported, not used for the
 official verdict.

Official use (only after preflight PASS and the single sealed run):
    /Users/kietnt/miniconda3/bin/python experiments/ext/v51fix/rule_p4h2_v2.py
    -> results/ext_v51fix_p4h2/ruling_v2.md, ruling_v2.json
Software test on D-07 development (no P4-H2 access):
    python experiments/ext/v51fix/rule_p4h2_v2.py --dev-dryrun [--results-root DIR] [--out-dir DIR]
"""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
M, REF = "tolerant_v5_1", "tolerant_v4"
TAU = 6.6083
FROZEN = "experiments/ext/v51/frozen_v4_v51.json"
OFFICIAL = {"run": "ext_v51fix_p4h2", "config": "experiments/configs/ext_v51fix_p4h2.json", "bank": "P4-H2",
            "split": "confirmatory", "frozen_in_config": FROZEN}
DRYRUN = {"run": "ext_v51_eval", "config": "experiments/configs/ext_v51_eval.json", "bank": "D-07",
          "split": "development", "frozen_in_config": "experiments/calibration/tolerant_v4_frozen.json"}
TS = (40, 80, 150)
CELLS = [("none", 0.0)] + [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]
DAMAGED = [c for c in CELLS if c[0] != "none"]
C1_CELLS = [(40, "missing", 0.2), (40, "missing", 0.5)]
C2_CELLS = [(T, k, r) for T in (80, 150) for k, r in DAMAGED]
C3_CELLS = [(T, "none", 0.0) for T in TS] + [(40, k, r) for k in ("extra", "reversed") for r in (0.2, 0.5)]
FAIL_TOTAL_SHARE, FAIL_CELL_SHARE = 0.01, 0.05   # ceilings on failed tolerant_v5_1 runs (overall, per rule cell)
BONF_M = (2, 3)                                   # primary specs with a p-value component (lead, section 3.3)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def key(r):
    return (r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])


def width_key(r):
    return r["kind"] if r["kind"] != "none" and (r.get("k") or 0) > 0 else "none"


def holm(pvals, alpha=0.025):
    order = np.argsort(pvals)
    m = len(pvals)
    rej = [False] * m
    for rank, i in enumerate(order):
        if pvals[i] <= alpha / (m - rank):
            rej[i] = True
        else:
            break
    return rej


def paired(rows_ok, T, kind, rate):
    """Paired IS difference v5_1 − v4 over runs with both ok; CI as the runner (1000 topology resamples,
    seed 0, rng.choice loop) with the 95% and Bonferroni quantiles from the same draws; one-sided p
    (10 000 resamples, seed 1). None if fewer than 2 topologies have a pair."""
    d = defaultdict(list)
    for k, r in rows_ok[M].items():
        if k[2] == T and k[3] == kind and k[4] == rate and k in rows_ok[REF]:
            d[k[0]].append(r["iscore_nonnull_mean"] - rows_ok[REF][k]["iscore_nonnull_mean"])
    if len(d) < 2:
        return None
    rng = np.random.default_rng(0)
    topos = list(d)
    est = float(np.mean([v for t in topos for v in d[t]]))
    boots = [np.mean([v for i in rng.choice(len(topos), len(topos)) for v in d[topos[i]]]) for _ in range(1000)]
    lo, hi = np.quantile(boots, (0.025, 0.975))
    bonf = {m: float(np.quantile(boots, 1 - 0.025 / m)) for m in BONF_M}
    rng2 = np.random.default_rng(1)
    sums = np.array([np.sum(d[t]) for t in topos])
    cnts = np.array([len(d[t]) for t in topos])
    picks = rng2.integers(0, len(topos), size=(10_000, len(topos)))
    b2 = sums[picks].sum(1) / cnts[picks].sum(1)
    return {"est": est, "lo": float(lo), "hi": float(hi), "hi_bonf": bonf,
            "p_less": (1 + int((b2 >= 0).sum())) / 10_001, "p_greater": (1 + int((b2 <= 0).sum())) / 10_001,
            "n_pairs": int(cnts.sum()), "n_topologies": len(topos)}


def cov_below_p(rows_cell, nonnull_of):
    """One-sided p for pooled ITT coverage < 0.90 (topology bootstrap of sums, 10 000, seed 2)."""
    cov, den = defaultdict(float), defaultdict(float)
    for r in rows_cell:
        t = r["topology"]
        if r["status"] == "ok":
            cov[t] += r["n_covered_nonnull"]
            den[t] += r["n_nonnull"]
        else:
            den[t] += nonnull_of.get((r["topology"], r["replicate"]), 0)
    topos = [t for t in den if den[t] > 0]
    if len(topos) < 2:
        return 1.0
    c = np.array([cov[t] for t in topos])
    n = np.array([den[t] for t in topos])
    picks = np.random.default_rng(2).integers(0, len(topos), size=(10_000, len(topos)))
    b = c[picks].sum(1) / n[picks].sum(1)
    return (1 + int((b >= 0.90).sum())) / 10_001


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev-dryrun", action="store_true", help="software test on results/ext_v51_eval (D-07 development)")
    ap.add_argument("--results-root", default=str(ROOT / "results"))
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args(argv)
    spec = DRYRUN if a.dev_dryrun else OFFICIAL
    run_dir = Path(a.results_root) / spec["run"]
    out_dir = Path(a.out_dir) if a.out_dir else (ROOT / "results" / ("ext_v51fix_dryrun" if a.dev_dryrun else spec["run"]))
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = [json.loads(line) for line in open(run_dir / "runs.jsonl")]
    manifest = json.loads((run_dir / "manifest.json").read_text())
    cfg_file = json.loads((ROOT / spec["config"]).read_text())
    frozen = {k: v for k, v in json.loads((ROOT / FROZEN).read_text()).items() if not k.startswith("_")}
    calib = json.loads((run_dir / "calibration.json").read_text())

    # ---------------- validity ----------------
    V = {}
    cfg = manifest["config"]
    V["V1 manifest config equals the frozen config file"] = cfg == cfg_file
    V["V2 bank/split/methods/frozen file/seed/grid"] = (
        cfg.get("bank") == spec["bank"] and cfg.get("split") == spec["split"] and cfg.get("methods") == [REF, M]
        and cfg.get("frozen_calibration") == spec["frozen_in_config"] and cfg.get("seed_base") == 20261102
        and cfg.get("T") == list(TS) and cfg.get("n_boot") == 199 and cfg.get("H") == 4
        and cfg.get("calibrate_methods") == [M]
        and cfg.get("damage") == {"kinds": ["extra", "missing", "reversed"], "rates": [0.2, 0.5]})
    n_topo = len(manifest.get("topologies", []))
    expected = 2 * n_topo * cfg.get("replicates", 0) * len(TS) * len(CELLS)
    keys = defaultdict(set)
    dup = 0
    for r in rows:
        if key(r) in keys[r["method"]]:
            dup += 1
        keys[r["method"]].add(key(r))
    V["V3 row count and one row per (key, method)"] = (len(rows) == expected == manifest.get("n_rows") and dup == 0
                                                     and keys[M] == keys[REF] and set(keys) == {M, REF})
    if a.dev_dryrun:   # the D-07 run used tolerant_v4_frozen.json + runner-tuned v5_1 factors; frozen_v4_v51 copies both
        V["V4 calibration.json equals the frozen factors"] = all(abs(calib.get(k, -1) - v) < 1e-12 for k, v in frozen.items()
                                                                 if k.startswith(("mod|", f"{M}|")))
    else:
        V["V4 calibration.json equals the frozen factors"] = all(abs(calib.get(k, -1) - v) < 1e-12 for k, v in frozen.items())
    bad_c = 0
    for r in rows:
        if r["status"] != "ok":
            continue
        want = frozen.get(f"mod|{r['T']}|{width_key(r)}") if r["method"] == REF else frozen.get(f"{M}|{r['T']}|{width_key(r)}")
        if want is None or r.get("info_c_T") is None or abs(r["info_c_T"] - want) > 1e-12:
            bad_c += 1
        if r["method"] == M and r.get("info_prescale") != 0.5:
            bad_c += 1
    V["V5 every ok row carries its frozen width factor (and prescale 0.5 for v5_1)"] = bad_c == 0
    fp_bad = sum(1 for r in rows if r["status"] == "ok" and (
        (r["method"] == M and (r.get("info_v51_targeted") is None or r.get("info_v51_ratio") is None))
        or (r["method"] == REF and any(k.startswith("info_v51_") for k in r))))
    V["V6 fingerprint fields of paper4.ext_v51.tolerant_v5_1 on every ok v5_1 row, absent on v4 rows"] = fp_bad == 0
    valid = all(V.values())

    # ---------------- failures ----------------
    by_cell = defaultdict(list)
    for r in rows:
        by_cell[(r["method"], r["T"], r["kind"], r["rate"])].append(r)
    rows_ok = {m: {key(r): r for r in rows if r["method"] == m and r["status"] == "ok"
                   and r.get("iscore_nonnull_mean") is not None} for m in (M, REF)}
    nonnull_of = {(r["topology"], r["replicate"]): r["n_nonnull"] for r in rows if r["status"] == "ok" and "n_nonnull" in r}
    fails = {m: sum(1 for r in rows if r["method"] == m and r["status"] != "ok") for m in (M, REF)}
    n_m = sum(1 for r in rows if r["method"] == M)
    f_total_ok = fails[M] <= int(FAIL_TOTAL_SHARE * n_m)

    def stats(m, T, kind, rate):
        g = by_cell[(m, T, kind, rate)]
        ok = [r for r in g if r["status"] == "ok" and r.get("iscore_nonnull_mean") is not None]
        if not ok:
            return {"n_ok": 0, "n": len(g), "cov_ok": None, "cov_itt": None, "IS": None}
        den_fail = sum(nonnull_of.get((r["topology"], r["replicate"]), 0) for r in g if r not in ok)
        cov_num = sum(r["n_covered_nonnull"] for r in ok)
        den_ok = sum(r["n_nonnull"] for r in ok)
        return {"n_ok": len(ok), "n": len(g), "cov_ok": cov_num / den_ok, "cov_itt": cov_num / (den_ok + den_fail),
                "IS": float(np.mean([r["iscore_nonnull_mean"] for r in ok])),
                "targeted_share": (float(np.mean([r["info_v51_targeted"] for r in ok if r.get("info_v51_targeted") is not None]))
                                   if m == M else None),
                "ratio_max": (max((r["info_v51_ratio"] for r in ok if r.get("info_v51_ratio") is not None), default=None)
                              if m == M else None)}

    def cell_ok(T, kind, rate):
        s, v = stats(M, T, kind, rate), stats(REF, T, kind, rate)
        n_fail = s["n"] - s["n_ok"]
        reasons = []
        if s["n_ok"] == 0 or v["n_ok"] == 0:
            reasons.append("0 ok runs")
        if n_fail > int(FAIL_CELL_SHARE * s["n"]):
            reasons.append(f"{n_fail}/{s['n']} failed v5_1 runs > ceiling")
        return s, v, reasons

    out = [f"# {spec['run']}: confirmatory ruling v2 of {M} (experiments/ext/v51fix/rule_p4h2_v2.py)", ""]
    if a.dev_dryrun:
        out += ["**SOFTWARE TEST ON D-07 DEVELOPMENT (ext_v51_eval). NOT A CONFIRMATORY RESULT.**", ""]
    out += [f"runs.jsonl sha256 {sha256(run_dir / 'runs.jsonl')}; {len(rows)} rows; {n_topo} topologies", "", "## Validity", ""]
    out += [f"- {k}: {'PASS' if v else 'FAIL'}" for k, v in V.items()]
    out += ["", "## Failures", "", f"- failed runs: {fails}; ceiling for {M}: {int(FAIL_TOTAL_SHARE * n_m)} of {n_m} "
            f"-> {'PASS' if f_total_ok else 'FAIL'}; per rule cell ceiling {int(FAIL_CELL_SHARE * 60)} of 60 (5%)", ""]

    res = {"validity": V, "failed_runs": fails, "fail_total_ok": f_total_ok, "cells": {}}
    out.append("## Conditions")
    out.append("")
    # C1
    c1, c1p, c1_bonf = [], [], {m: [] for m in BONF_M}
    for c in C1_CELLS:
        s, v, why = cell_ok(*c)
        p = paired(rows_ok, *c)
        if p is None:
            why.append("fewer than 2 topologies with a pair")
        ok = not why and s["cov_itt"] >= 0.90 and p["hi"] < 0
        c1.append(ok)
        c1p.append(p["p_less"] if (not why and s["cov_itt"] >= 0.90) else 1.0)
        for m in BONF_M:
            c1_bonf[m].append(bool(not why and s["cov_itt"] >= 0.90 and p["hi_bonf"][m] < 0))
        res["cells"][f"C1|{c}"] = {"v51": s, "v4": v, "paired": p, "problems": why, "pass": ok}
        out.append(f"- C1 T={c[0]} {c[1]}-{c[2]}: " + (f"PROBLEM {why} -> FAIL" if why else
                   f"cov ITT {s['cov_itt']:.3f} (ok-only {s['cov_ok']:.3f}, {s['n_ok']}/{s['n']} ok), IS {s['IS']:.3f} vs v4 {v['IS']:.3f}; "
                   f"v5_1 − v4 {p['est']:+.3f} [{p['lo']:+.3f}, {p['hi']:+.3f}] (p {p['p_less']:.4f}; upper 97.5% {p['hi_bonf'][2]:+.3f}, "
                   f"98.33% {p['hi_bonf'][3]:+.3f}) -> {'PASS' if ok else 'FAIL'}"))
    # C2, C3
    cond = {"C2": (C2_CELLS, True), "C3": (C3_CELLS, False)}
    cres, cworse = {}, {}
    for name, (cells, gate) in cond.items():
        flags, pw = [], []
        for c in cells:
            s, v, why = cell_ok(*c)
            p = paired(rows_ok, *c)
            ok = not why and (not gate or s["cov_itt"] >= 0.90) and s["IS"] <= 1.05 * v["IS"]
            flags.append(ok)
            pw.append(p["p_greater"] if p else 1.0)
            res["cells"][f"{name}|{c}"] = {"v51": s, "v4": v, "paired": p, "problems": why, "pass": ok}
            out.append(f"- {name} T={c[0]} {c[1]}-{c[2]}: " + (f"PROBLEM {why} -> FAIL" if why else
                       (f"cov ITT {s['cov_itt']:.3f}, " if gate else "") +
                       f"IS {s['IS']:.3f} vs v4 {v['IS']:.3f} (ratio {s['IS'] / v['IS']:.3f}); "
                       + (f"v5_1 − v4 {p['est']:+.3f} [{p['lo']:+.3f}, {p['hi']:+.3f}]" if p else "no pairs")
                       + f" -> {'PASS' if ok else 'FAIL'}"))
        cres[name], cworse[name] = flags, holm(pw)
    c1h = holm(c1p)
    verdict = valid and f_total_ok and all(c1) and all(cres["C2"]) and all(cres["C3"])
    rest = valid and f_total_ok and all(cres["C2"]) and all(cres["C3"])

    # descriptive: coverage margins, branch check
    gated = C1_CELLS + C2_CELLS
    pcov = []
    for c in gated:
        pcov.append(cov_below_p(by_cell[(M,) + c], nonnull_of))
    below_h = holm(pcov)
    def _cov(c):
        return res["cells"][("C1|" if c in C1_CELLS else "C2|") + str(c)]["v51"]["cov_itt"]

    margins = [f"{c[0]} {c[1]}-{c[2]} " + ("no ok run" if _cov(c) is None else f"{_cov(c):.3f}")
               for c in gated if _cov(c) is None or _cov(c) < 0.93]
    miss_rows = [r for r in rows_ok[M].values() if r["kind"] == "missing"]
    n_targeted = sum(1 for r in miss_rows if r.get("info_v51_targeted") == 1)
    rmax = max((r.get("info_v51_ratio") or 0 for r in rows_ok[M].values()), default=0)
    branch_all_targeted = n_targeted == len(miss_rows)
    out += ["", "## Summary", "",
            f"C1 {sum(c1)}/2 (Holm over 2: {sum(c1h)}/2); C2 {sum(cres['C2'])}/12 (v5_1 significantly worse than v4 after Holm: "
            f"{sum(cworse['C2'])}/12); C3 {sum(cres['C3'])}/7 (significantly worse after Holm: {sum(cworse['C3'])}/7); "
            f"validity {'PASS' if valid else 'FAIL'}; failure ceiling {'PASS' if f_total_ok else 'FAIL'}",
            "",
            f"-> **{M} {'CONFIRMED' if verdict else 'NOT CONFIRMED'}" + (" on P4-H2**" if not a.dev_dryrun else " (DRY RUN on D-07 development)**"),
            "",
            "Reported variants (not the official verdict):",
            f"- C1 replaced by its Holm version (2 cells): {'CONFIRMED' if rest and all(c1h) else 'NOT CONFIRMED'}",
            f"- Bonferroni overlay over 2 primary specs (C1 with 97.5% CI): {'CONFIRMED' if rest and all(c1_bonf[2]) else 'NOT CONFIRMED'}",
            f"- Bonferroni overlay over 3 primary specs (C1 with 98.33% CI): {'CONFIRMED' if rest and all(c1_bonf[3]) else 'NOT CONFIRMED'}",
            "",
            "## Descriptive (pre-registered statements, no effect on the verdict)", "",
            f"- Coverage-gated cells (14) significantly below 0.90 after Holm (one-sided topology bootstrap, seed 2): {sum(below_h)}/14; "
            f"cells with ITT coverage < 0.93: {margins if margins else 'none'}",
            f"- Branch: {n_targeted}/{len(miss_rows)} ok missing runs of v5_1 took the targeted branch; max r over all ok v5_1 runs "
            f"{rmax:.3f} vs TAU {TAU}. With 14 nodes and lag_max 2, r <= (T - 2)/29 <= 5.10 at T <= 150, so the all-lag branch "
            f"cannot be selected. " + ("The method evaluated here is therefore exactly 'v5 with de-duplicated targeted opening'."
                                       if branch_all_targeted and rmax < TAU else
                                       "WARNING: the all-lag branch was used; the paper's description must mention the switch."),
            "- Tau fragility (stated before the run): TAU = 6.6083 came from a D-07H probe whose decisive CI bound at T = 100 "
            "(-0.0038) is >= 0 for 11% of probe bootstrap seeds (then TAU about 2.94 and T = 150 would take the all-lag branch). "
            "This run tests the frozen method only; the T = 150 behaviour under TAU about 2.94 is the D-07 sensitivity "
            "results/ext_v51fix_t150tau/ (descriptive, not tested here).",
            "- v4 realisation: built-in methods are seeded by cell position (bug E1, not fixed). The tolerant_v4 rows of this "
            "run are the paper's P4-H2 v4 table; other P4-H2 configs with other cell lists give other v4 realisations."]
    res.update({"C1": c1, "C1_holm": c1h, "C1_bonf2": c1_bonf[2], "C1_bonf3": c1_bonf[3], "C2": cres["C2"],
                "C2_worse_holm": cworse["C2"], "C3": cres["C3"], "C3_worse_holm": cworse["C3"], "valid": valid,
                "verdict": "CONFIRMED" if verdict else "NOT CONFIRMED", "dry_run_on_D07": a.dev_dryrun,
                "cov_below_090_holm": below_h, "branch_targeted": [n_targeted, len(miss_rows)], "ratio_max": rmax,
                "runs_sha256": sha256(run_dir / "runs.jsonl")})
    (out_dir / "ruling_v2.md").write_text("\n".join(out) + "\n")
    (out_dir / "ruling_v2.json").write_text(json.dumps(res, indent=1, default=str))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
