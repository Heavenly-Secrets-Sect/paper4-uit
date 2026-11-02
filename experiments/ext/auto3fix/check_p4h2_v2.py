"""FROZEN confirmatory analysis of tolerant_auto3 on P4-H2, corrected spec of round 3 (ID auto3fix).

Replaces experiments/ext/auto5/check_p4h2.py (left unchanged). Rule text: docs/ext/auto3fix.md,
section 1.1, recorded 2026-11-02T06:02Z before this script was written. Thresholds and cells are
those of the round-2 spec (B1 C1-C3 + L1); what is new:

* a failed run (status != ok) or an absent row counts as covering NO non-null pair: its n_nonnull
  (taken from any ok row of the same topology x replicate, which depends only on the truth) stays in
  the denominator of the pooled coverage;
* a ruled cell fails when tolerant_auto3 has more than MAX_BAD = 3 failed/absent runs (5% of 60) or
  no ok run at all (no crash);
* IS ratios (C2, C3) are taken over units where both tolerant_auto3 and tolerant_v4 are ok; a cell
  with fewer than n_exp - MAX_BAD such units fails;
* n_ok / n_exp of every method in every cell is reported;
* integrity checks I1-I5 (config identity, topology set, width-table and frozen-factor trace in the
  rows, constant n_nonnull); a failed check makes the verdict NOT CONFIRMED (integrity).

CONFIRMED iff C1, C2, C3, L1 all hold and every integrity check passes:
  C1 coverage >= 0.90 in missing/reversed x 0.2/0.5 at T = 80 and 150 (config 1, 8 cells);
  C2 IS(none) <= 1.35 x IS(tolerant_v4) at T = 40, 80, 150 (config 1);
  C3 GES cell at T = 80, 150: coverage >= 0.90 and IS <= 1.10 x IS(tolerant_v4) (config 1);
  L1 latent1: coverage >= 0.90 in missing-0.2 and reversed-0.2 at T = 80 and 150 (config 2).
Reported, not ruled: one-sided cluster-bootstrap p for H0 'coverage <= 0.90' (2000 resamples of
topologies, seed 0; failed units included as uncovered) and Holm (alpha 0.05) over the 14 coverage
cells; ok-only coverage and unpaired IS ratios (the round-2 definitions).

Run on P4-H2 (after the two frozen configs, by the lead only):
    python experiments/ext/auto3fix/check_p4h2_v2.py
    -> results/ext_auto3fix_p4h2_check/{check.md, check.json}
Dry run on the stored D-07 development rows (NOT a confirmation):
    python experiments/ext/auto3fix/check_p4h2_v2.py --dry-run   -> results/ext_auto3fix_dryrun/
Test on arbitrary run directories (no verdict authority):
    python experiments/ext/auto3fix/check_p4h2_v2.py --test MAIN_DIR LAT_DIR OUT_DIR
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
CFG1 = ROOT / "experiments" / "configs" / "ext_auto3fix_p4h2_auto3.json"
CFG2 = ROOT / "experiments" / "configs" / "ext_auto3fix_p4h2_auto3_latent1.json"
WIDTH = ROOT / "experiments" / "ext" / "gate" / "width_table.json"
FROZEN = ROOT / "experiments" / "calibration" / "tolerant_v4_frozen.json"
M, V4 = "tolerant_auto3", "tolerant_v4"
MAX_BAD = 3
THR = 0.90
N_BOOT = 2000

C1_CELLS = [("clean", T, k, r) for T in (80, 150) for k in ("missing", "reversed") for r in (0.2, 0.5)]
C2_CELLS = [("clean", T, "none", 0.0) for T in (40, 80, 150)]
C3_CELLS = [("clean", T, "ges", 0.0) for T in (80, 150)]
L1_CELLS = [("latent1", T, k, 0.2) for T in (80, 150) for k in ("missing", "reversed")]


def load_rows(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


def is_ok(r: dict) -> bool:
    return r.get("status") == "ok" and r.get("iscore_nonnull_mean") is not None


class Run:
    """Rows of one run indexed by cell and unit, with the expected unit set from its manifest."""

    def __init__(self, run_dir: Path):
        self.dir = run_dir
        self.manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        self.rows = load_rows(run_dir / "runs.jsonl")
        self.topos = [t["id"] for t in self.manifest["topologies"]]
        self.reps = int(self.manifest["config"]["replicates"])
        self.units = [(t, r) for t in self.topos for r in range(self.reps)]
        self.cell = defaultdict(dict)       # (sc, T, kind, rate, method) -> {(topo, rep): row}
        self.duplicates = 0
        self.nn = defaultdict(set)          # (topo, rep) -> set of n_nonnull seen on ok rows
        for r in self.rows:
            k = (r.get("scenario", "clean"), r["T"], r["kind"], float(r["rate"]), r["method"])
            u = (r["topology"], r["replicate"])
            if u in self.cell[k]:
                self.duplicates += 1
            self.cell[k][u] = r
            if is_ok(r):
                self.nn[u].add(int(r["n_nonnull"]))

    def n_nonnull(self, u):
        s = self.nn.get(u)
        return next(iter(s)) if s and len(s) == 1 else None

    def counts(self, cellkey, method):
        d = self.cell.get((*cellkey, method), {})
        n_ok = sum(1 for u in self.units if u in d and is_ok(d[u]))
        n_fail = sum(1 for u in self.units if u in d and not is_ok(d[u]))
        return {"n_exp": len(self.units), "n_ok": n_ok, "n_fail": n_fail, "n_absent": len(self.units) - n_ok - n_fail}


def topo_arrays_cov(run: Run, cellkey, method=M):
    """Per topology (manifest order): covered pairs, non-null pairs incl. failed units, bad units,
    ok-only covered and ok-only non-null. ``None`` in den_ok_missing flags a unit whose denominator
    cannot be built."""
    d = run.cell.get((*cellkey, method), {})
    ti = {t: i for i, t in enumerate(run.topos)}
    nt = len(run.topos)
    num, den, bad, den_ok = np.zeros(nt), np.zeros(nt), np.zeros(nt), np.zeros(nt)
    undefined = 0
    for u in run.units:
        i = ti[u[0]]
        r = d.get(u)
        if r is not None and is_ok(r):
            num[i] += r["n_covered_nonnull"]
            den[i] += r["n_nonnull"]
            den_ok[i] += r["n_nonnull"]
        else:
            bad[i] += 1
            nn = run.n_nonnull(u)
            if nn is None:
                undefined += 1
            else:
                den[i] += nn
    return {"num": num, "den": den, "bad": bad, "den_ok": den_ok, "undefined": undefined}


def topo_arrays_is(run: Run, cellkey, m=M, ref=V4):
    """Per topology: sum of IS of m and of ref over units where both are ok, number of such units;
    and the unpaired ok-only sums (round-2 definition)."""
    dm = run.cell.get((*cellkey, m), {})
    dr = run.cell.get((*cellkey, ref), {})
    ti = {t: i for i, t in enumerate(run.topos)}
    nt = len(run.topos)
    sm, sr, npair = np.zeros(nt), np.zeros(nt), np.zeros(nt)
    um, nm, ur, nr = np.zeros(nt), np.zeros(nt), np.zeros(nt), np.zeros(nt)
    for u in run.units:
        i = ti[u[0]]
        a, b = dm.get(u), dr.get(u)
        if a is not None and is_ok(a):
            um[i] += a["iscore_nonnull_mean"]
            nm[i] += 1
        if b is not None and is_ok(b):
            ur[i] += b["iscore_nonnull_mean"]
            nr[i] += 1
        if a is not None and b is not None and is_ok(a) and is_ok(b):
            sm[i] += a["iscore_nonnull_mean"]
            sr[i] += b["iscore_nonnull_mean"]
            npair[i] += 1
    return {"sm": sm, "sr": sr, "npair": npair, "um": um, "nm": nm, "ur": ur, "nr": nr}


def build(main: Run, lat: Run) -> dict:
    """Per-topology aggregates of every ruled cell (shared by the check and the fragility bootstrap).
    Both runs must list the same topologies in the same order (they do on P4-H2 and on D-07)."""
    A = {"n_exp": {}, "cov": {}, "is": {}}
    for ck in C1_CELLS + C3_CELLS:
        A["cov"][ck] = topo_arrays_cov(main, ck)
        A["n_exp"][ck] = len(main.units)
    for ck in L1_CELLS:
        A["cov"][ck] = topo_arrays_cov(lat, ck)
        A["n_exp"][ck] = len(lat.units)
    for ck in C2_CELLS + C3_CELLS:
        A["is"][ck] = topo_arrays_is(main, ck)
        A["n_exp"][ck] = len(main.units)
    return A


def evaluate(A: dict, pick=None) -> dict:
    """Apply the rule to aggregates; ``pick`` = topology indices of a bootstrap resample (None = all)."""
    sel = (lambda x: x) if pick is None else (lambda x: x[pick])

    def cov_cell(ck):
        c = A["cov"][ck]
        num, den, bad = sel(c["num"]).sum(), sel(c["den"]).sum(), int(sel(c["bad"]).sum())
        cov = float(num / den) if den > 0 else 0.0
        den_ok = sel(c["den_ok"]).sum()
        ok = c["undefined"] == 0 and bad <= MAX_BAD and den > 0 and cov >= THR
        return {"cov": cov, "cov_ok_only": float(num / den_ok) if den_ok > 0 else float("nan"),
                "n_bad": bad, "undefined": int(c["undefined"]), "ok": bool(ok)}

    def is_cell(ck, limit):
        s = A["is"][ck]
        npair = int(sel(s["npair"]).sum())
        n_exp = A["n_exp"][ck]
        ratio = float(sel(s["sm"]).sum() / sel(s["sr"]).sum()) if npair > 0 else float("nan")
        nm, nr = sel(s["nm"]).sum(), sel(s["nr"]).sum()
        unpaired = float((sel(s["um"]).sum() / nm) / (sel(s["ur"]).sum() / nr)) if nm > 0 and nr > 0 else float("nan")
        ok = npair >= n_exp - MAX_BAD and npair > 0 and ratio <= limit
        return {"ratio": ratio, "ratio_unpaired": unpaired, "n_pair": npair, "ok": bool(ok)}

    c1 = {ck: cov_cell(ck) for ck in C1_CELLS}
    c2 = {ck: is_cell(ck, 1.35) for ck in C2_CELLS}
    c3 = {}
    for ck in C3_CELLS:
        cv, isr = cov_cell(ck), is_cell(ck, 1.10)
        c3[ck] = {**cv, **{k: v for k, v in isr.items() if k != "ok"}, "ok_cov": cv["ok"], "ok_is": isr["ok"],
                  "ok": cv["ok"] and isr["ok"]}
    l1 = {ck: cov_cell(ck) for ck in L1_CELLS}
    R = {"C1": all(x["ok"] for x in c1.values()), "C2": all(x["ok"] for x in c2.values()),
         "C3": all(x["ok"] for x in c3.values()), "L1": all(x["ok"] for x in l1.values())}
    return {"C1": c1, "C2": c2, "C3": c3, "L1": l1, "R": R, "rule_holds": all(R.values())}


def coverage_p(A: dict, ck, seed=0) -> float:
    c = A["cov"][ck]
    rng = np.random.default_rng(seed)
    nt = len(c["num"])
    pick = rng.integers(0, nt, size=(N_BOOT, nt))
    den = c["den"][pick].sum(1)
    boots = np.where(den > 0, c["num"][pick].sum(1) / np.where(den > 0, den, 1), 0.0)
    return float(np.mean(boots <= THR))


def holm(pvals, alpha=0.05):
    p = np.asarray(pvals, float)
    rej = np.zeros(len(p), bool)
    for rank, i in enumerate(np.argsort(p)):
        if p[i] <= alpha / (len(p) - rank):
            rej[i] = True
        else:
            break
    return rej.tolist()


def integrity(main: Run, lat: Run, dry: bool) -> list[dict]:
    width = json.loads(WIDTH.read_text(encoding="utf-8"))
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    out = []
    # I1 config identity
    if dry:
        out.append({"check": "I1", "ok": True, "note": "skipped in dry/test mode (D-07 configs differ from the P4-H2 ones)"})
    else:
        bad = []
        for run, path in ((main, CFG1), (lat, CFG2)):
            cfg = json.loads(path.read_text(encoding="utf-8"))
            mc = run.manifest["config"]
            if mc != cfg or mc.get("bank") != "P4-H2" or mc.get("split") != "confirmatory":
                bad.append(run.dir.name)
        out.append({"check": "I1", "ok": not bad, "note": f"manifest config != frozen config or not P4-H2/confirmatory: {bad}" if bad else "manifest configs equal the frozen configs; P4-H2/confirmatory"})
    # I2 topology set and duplicates
    probs = []
    for run in (main, lat):
        if len(run.topos) != 20:
            probs.append(f"{run.dir.name}: {len(run.topos)} topologies")
        extra = {r["topology"] for r in run.rows} - set(run.topos)
        if extra:
            probs.append(f"{run.dir.name}: rows of unlisted topologies {sorted(extra)[:3]}")
        if run.duplicates:
            probs.append(f"{run.dir.name}: {run.duplicates} duplicate rows")
    if main.topos != lat.topos:
        probs.append("the two runs list different topologies")
    out.append({"check": "I2", "ok": not probs, "note": "; ".join(probs) or "20 topologies, same in both runs, no duplicate rows"})
    # I3 auto3 width trace
    probs, n = [], 0
    for run in (main, lat):
        for r in run.rows:
            if r["method"] == M and is_ok(r):
                n += 1
                st = r.get("info_state")
                key = "closed" if st == "undiagnosable" else st
                want = width.get(f"{key}|{r['T']}")
                if st not in ("closed", "open", "undiagnosable") or want is None or r.get("info_c_T") != want:
                    probs.append((run.dir.name, r["topology"], r["replicate"], r["T"], r["kind"], st, r.get("info_c_T")))
    out.append({"check": "I3", "ok": not probs and n > 0, "note": f"{n} ok auto3 rows checked; {len(probs)} mismatches" + (f", e.g. {probs[:2]}" if probs else "")})
    # I4 v4 frozen-factor trace
    probs, n = [], 0
    for run in (main, lat):
        for r in run.rows:
            if r["method"] == V4 and is_ok(r):
                n += 1
                c = r.get("info_c_T")
                if r["kind"] == "ges":
                    good = c in {v for k, v in frozen.items() if k.startswith(f"mod|{r['T']}|")}
                else:  # runner: methods.width_key(stated damage) -> 'none' when the stated k is 0
                    wk = "none" if int(r.get("k", 0)) == 0 else r["kind"]
                    good = c == frozen.get(f"mod|{r['T']}|{wk}")
                if not good:
                    probs.append((run.dir.name, r["topology"], r["replicate"], r["T"], r["kind"], c))
    out.append({"check": "I4", "ok": not probs and n > 0, "note": f"{n} ok tolerant_v4 rows checked; {len(probs)} mismatches" + (f", e.g. {probs[:2]}" if probs else "")})
    # I5 constant n_nonnull per unit
    probs = [(run.dir.name, u, sorted(s)) for run in (main, lat) for u, s in run.nn.items() if len(s) != 1]
    out.append({"check": "I5", "ok": not probs, "note": f"{len(probs)} units with non-constant n_nonnull" + (f", e.g. {probs[:2]}" if probs else "")})
    return out


def cell_name(ck):
    sc, T, k, r = ck
    return f"{sc}|{T}|{k}|{r}"


def ok_table(run: Run) -> list[dict]:
    keys = sorted({k[:4] for k in run.cell}, key=lambda k: (k[0], k[1], k[2], k[3]))
    methods = sorted({k[4] for k in run.cell})
    return [{"cell": cell_name(ck), **{m: run.counts(ck, m) for m in methods}} for ck in keys]


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", help="stored D-07 development rows (not a confirmation)")
    g.add_argument("--test", nargs=3, metavar=("MAIN_DIR", "LAT_DIR", "OUT_DIR"), help="arbitrary run dirs (no verdict authority)")
    a = ap.parse_args(argv)
    if a.dry_run:
        mdir, ldir, out, mode = ROOT / "results/ext_gate_auto3", ROOT / "results/ext_auto5_a1", ROOT / "results/ext_auto3fix_dryrun", "DRY RUN on D-07 development rows, NOT a confirmation"
    elif a.test:
        mdir, ldir, out, mode = Path(a.test[0]), Path(a.test[1]), Path(a.test[2]), "TEST on arbitrary run directories, no verdict authority"
    else:
        mdir, ldir, out, mode = ROOT / "results/ext_auto3fix_p4h2_auto3", ROOT / "results/ext_auto3fix_p4h2_auto3_latent1", ROOT / "results/ext_auto3fix_p4h2_check", "P4-H2 confirmatory"
    dry = bool(a.dry_run or a.test)
    main_run, lat_run = Run(mdir), Run(ldir)
    checks = integrity(main_run, lat_run, dry)
    A = build(main_run, lat_run)
    E = evaluate(A)
    cov_cells = C1_CELLS + C3_CELLS + L1_CELLS
    pv = {ck: coverage_p(A, ck) for ck in cov_cells}
    rej = holm([pv[ck] for ck in cov_cells])
    integ_ok = all(c["ok"] for c in checks)
    confirmed = E["rule_holds"] and integ_ok
    verdict = "CONFIRMED" if confirmed else ("NOT CONFIRMED (integrity)" if not integ_ok else "NOT CONFIRMED")
    cnt = lambda run, ck, m=M: run.counts(ck, m)  # noqa: E731

    def jcell(d, run):
        return [{"cell": cell_name(ck), **v, "p_cov_le_0.90": pv.get(ck), **{f"{m}_counts": cnt(run, ck, m) for m in (M, V4)}}
                for ck, v in d.items()]

    J = {"mode": mode, "runs": [str(mdir.relative_to(ROOT)) if mdir.is_relative_to(ROOT) else str(mdir),
                                 str(ldir.relative_to(ROOT)) if ldir.is_relative_to(ROOT) else str(ldir)],
         "max_bad": MAX_BAD, "integrity": checks,
         "C1": jcell(E["C1"], main_run), "C2": jcell(E["C2"], main_run), "C3": jcell(E["C3"], main_run),
         "L1": jcell(E["L1"], lat_run), "conditions": E["R"], "rule_holds": E["rule_holds"],
         "holm_rejected": int(sum(rej)), "holm_n": len(rej),
         "holm_not_rejected": [cell_name(ck) for ck, r in zip(cov_cells, rej) if not r],
         "ok_counts": {"main": ok_table(main_run), "latent": ok_table(lat_run)}, "verdict": verdict}

    def f_cov(ck, x, run):
        c = cnt(run, ck)
        return (f"{cell_name(ck)} {x['cov']:.3f} (ok-only {x['cov_ok_only']:.3f}; auto3 ok {c['n_ok']}/{c['n_exp']}, "
                f"bad {x['n_bad']}; p {pv[ck]:.4f})")

    L = [f"# Confirmatory check of tolerant_auto3, corrected spec v2 ({mode})", "",
         f"Runs: {J['runs'][0]}, {J['runs'][1]}. Failed/absent runs count as uncovered; a ruled cell fails when auto3 has > {MAX_BAD} failed/absent runs.", "",
         "## Integrity", ""] + [f"- {c['check']}: {'OK' if c['ok'] else 'FAIL'}: {c['note']}" for c in checks] + [
         "", "## Rule", "",
         "- C1: " + "; ".join(f_cov(ck, x, main_run) for ck, x in E["C1"].items()) + f" -> {'PASS' if E['R']['C1'] else 'FAIL'}",
         "- C2: " + "; ".join(f"T{ck[1]} ratio {x['ratio']:.3f} (paired n {x['n_pair']}; unpaired {x['ratio_unpaired']:.3f})" for ck, x in E["C2"].items()) + f" -> {'PASS' if E['R']['C2'] else 'FAIL'}",
         "- C3: " + "; ".join(f"T{ck[1]} cov {x['cov']:.3f} (ok-only {x['cov_ok_only']:.3f}, bad {x['n_bad']}) ratio {x['ratio']:.3f} (paired n {x['n_pair']})" for ck, x in E["C3"].items()) + f" -> {'PASS' if E['R']['C3'] else 'FAIL'}",
         "- L1: " + "; ".join(f_cov(ck, x, lat_run) for ck, x in E["L1"].items()) + f" -> {'PASS' if E['R']['L1'] else 'FAIL'}",
         f"- Holm (alpha 0.05) over the {len(rej)} coverage cells, H0 'cov <= 0.90' rejected: {sum(rej)}/{len(rej)}"
         + (f"; not rejected: {', '.join(J['holm_not_rejected'])}" if J["holm_not_rejected"] else ""),
         f"- **{verdict}**", "",
         "Fragility (recorded before P4-H2, docs/ext/auto3fix.md 1.2): on the D-07 dry run, C1 at T80 reversed-0.5 was 0.903, "
         "the only one of 14 coverage cells Holm could not reject (13/14); a NOT CONFIRMED from that cell alone is not evidence "
         "that auto3 got worse, and a CONFIRMED does not rule out true coverage below 0.90 there.", "",
         "## n_ok / n_exp per method and cell", ""]
    for name, run in (("main", main_run), ("latent", lat_run)):
        tab = J["ok_counts"][name]
        methods = [m for m in tab[0] if m != "cell"] if tab else []
        L += [f"### {name} run", "", "| cell | " + " | ".join(methods) + " |", "|---|" + "---|" * len(methods)]
        for row in tab:
            L.append(f"| {row['cell']} | " + " | ".join(f"{row[m]['n_ok']}/{row[m]['n_exp']}" for m in methods) + " |")
        L.append("")
    out.mkdir(parents=True, exist_ok=True)
    (out / "check.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "check.json").write_text(json.dumps(J, indent=1, default=float), encoding="utf-8")
    print("\n".join(L[: L.index("## n_ok / n_exp per method and cell")]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
