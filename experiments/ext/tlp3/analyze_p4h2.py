"""Analyzer of the P5 (TLP baseline) confirmatory spec of docs/ext/tlp3.md, section 3. It replaces
experiments/ext/tlp2/score.py for P4-H2 (that script must not be used for P4-H2).

Differences from score.py, fixed before P4-H2 (docs/ext/tlp3.md section 2):
- A' REQUIRES Holm: a v4 win counts toward A/A' only if it holds in the gate view AND its Holm-adjusted
  p (12 cells, per version) is < 0.05. Losses (X wins) are counted raw, without Holm, in both views.
- no claim B, no pairing check against round 1, no db90 block (nothing of D-07 is read);
- failed runs: a cell with fewer than 90% paired ok runs (of topologies x replicates in the manifest) is
  INCOMPLETE and the spec is then NOT CONFIRMED; failed rows count as uncovered (all their non-null
  pairs) in the pooled coverage of that method;
- every bootstrap has its own seed [0, T, cell index, version index], so the result does not depend on
  the order in which cells are evaluated;
- confirmatory mode checks that results/<run>/manifest.json carries exactly the frozen config.

Usage (P4-H2, the only confirmatory call):
  python3 experiments/ext/tlp3/analyze_p4h2.py --run ext_tlp3_p4h2 --out results/ext_tlp3_p4h2_verdict
Development / plumbing checks (never confirmatory):
  python3 experiments/ext/tlp3/analyze_p4h2.py --dev --runs-files results/ext_tlp2_t80a/runs.jsonl ... --out ...
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
CONFIG = "experiments/configs/ext_tlp3_p4h2.json"
REF = "tolerant_v4"
VERSIONS = ["targeted_lp", "tlp2_db", "tlp2_db_p3"]
TS = (80, 150)
DAMAGED = [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]
NB = 10000
GATE = 0.90
ALPHA_HOLM = 0.05
MIN_OK_SHARE = 0.90
P1_RUN = "ext_v51_p4h2"   # descriptive v4 realisation check (same kinds/rates list -> same c_idx)


def key(r):
    return (r["topology"], r["replicate"], r["T"], r["kind"], float(r["rate"]))


def boot_diff(diffs_by_topo, seed):
    topos = sorted(diffs_by_topo)
    vals = [np.array(diffs_by_topo[t]) for t in topos]
    sums = np.array([v.sum() for v in vals])
    cnts = np.array([len(v) for v in vals])
    est = sums.sum() / cnts.sum()
    rng = np.random.default_rng(seed)
    pick = rng.integers(0, len(topos), size=(NB, len(topos)))
    b = sums[pick].sum(axis=1) / cnts[pick].sum(axis=1)
    lo, hi = np.quantile(b, (0.025, 0.975))
    p = min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean()))
    return float(est), float(lo), float(hi), max(p, 1.0 / NB)


def holm(pvals):
    m = len(pvals)
    order = np.argsort(pvals, kind="stable")
    adj = np.empty(m)
    run = 0.0
    for rank, i in enumerate(order):
        run = max(run, (m - rank) * pvals[i])
        adj[i] = min(1.0, run)
    return adj


def load_rows(paths):
    rows = []
    for p in paths:
        with open(p, encoding="utf-8") as fh:
            rows += [json.loads(line) for line in fh]
    return [r for r in rows if r.get("scenario", "clean") == "clean" and "@" not in r["method"]]


def analyse(rows, expected_units, mode):
    idx = {}
    dup = 0
    for r in rows:
        k = key(r) + (r["method"],)
        dup += k in idx
        idx[k] = r
    # non-null pair count of each (unit, cell) depends on the truth only: take it from any ok row
    nn = {}
    for r in rows:
        if r["status"] == "ok" and "n_nonnull" in r:
            nn.setdefault(key(r), r["n_nonnull"])
    n_exp = len(expected_units)
    need = math.ceil(MIN_OK_SHARE * n_exp)
    res = {"mode": mode, "n_rows": len(rows), "duplicates": dup, "expected_runs_per_cell": n_exp,
           "min_ok_pairs_per_cell": need, "cells": {}, "failures": {}}
    for m in [REF] + VERSIONS:
        res["failures"][m] = sum(1 for r in rows if r["method"] == m and r["status"] != "ok")

    def cov(T, kind, rate, m):
        num = den = 0
        for (topo, rep) in expected_units:
            k = (topo, rep, T, kind, rate)
            if k not in nn:
                continue
            den += nn[k]
            r = idx.get(k + (m,))
            if r is not None and r["status"] == "ok":
                num += r.get("n_covered_nonnull", 0)
        return num / den if den else float("nan")

    for T in TS:
        for ci, (kind, rate) in enumerate([("none", 0.0)] + DAMAGED):
            c = {"methods": {}, "comps": {}}
            for m in [REF] + VERSIONS:
                g = [idx.get((t, rp, T, kind, rate, m)) for (t, rp) in expected_units]
                ok = [r for r in g if r is not None and r["status"] == "ok"]
                c["methods"][m] = {"n_ok": len(ok), "cov": cov(T, kind, rate, m),
                                   "IS": float(np.mean([r["iscore_nonnull_mean"] for r in ok])) if ok else None,
                                   "width": float(np.median([r["width_kept"] for r in ok if r.get("width_kept") is not None]))
                                   if ok else None}
            for xi, X in enumerate(VERSIONS):
                diffs = defaultdict(list)
                for (t, rp) in expected_units:
                    a, b = idx.get((t, rp, T, kind, rate, REF)), idx.get((t, rp, T, kind, rate, X))
                    if a is not None and b is not None and a["status"] == "ok" and b["status"] == "ok":
                        diffs[t].append(a["iscore_nonnull_mean"] - b["iscore_nonnull_mean"])
                n_pair = sum(len(v) for v in diffs.values())
                comp = {"n_pairs": n_pair, "complete": n_pair >= need}
                if diffs:
                    est, lo, hi, p = boot_diff(diffs, [0, T, ci, xi])
                    comp.update({"d": est, "lo": lo, "hi": hi, "p": p})
                c["comps"][X] = comp
            res["cells"][f"{T}|{kind}|{rate}"] = c
    return res


def verdict(cs, X, view):
    m, comp = cs["methods"], cs["comps"][X]
    if "d" not in comp:
        return "missing"
    g_v4 = (m[REF]["cov"] >= GATE) if view == "gate" else True
    g_x = (m[X]["cov"] >= GATE) if view == "gate" else True
    if g_v4 and comp["hi"] < 0:
        return "v4"
    if g_x and comp["lo"] > 0:
        return "X"
    return "tie"


def decide(res):
    fam = [f"{T}|{k}|{r}" for T in TS for k, r in DAMAGED]
    per, incomplete = {}, []
    for X in VERSIONS:
        ps = np.array([res["cells"][c]["comps"][X].get("p", 1.0) for c in fam])
        adj = holm(ps)
        cells = {}
        for c, a in zip(fam, adj):
            cs = res["cells"][c]
            if not cs["comps"][X]["complete"]:
                incomplete.append(f"{X}@{c}")
            g, pu = verdict(cs, X, "gate"), verdict(cs, X, "pure")
            cells[c] = {"gate": g, "pure": pu, "p": cs["comps"][X].get("p"), "p_holm": float(a)}
        per[X] = {
            "n": len(fam),
            "v4_wins_gate": sum(v["gate"] == "v4" for v in cells.values()),
            "v4_wins_gate_holm": sum(v["gate"] == "v4" and v["p_holm"] < ALPHA_HOLM for v in cells.values()),
            "v4_wins_pure": sum(v["pure"] == "v4" for v in cells.values()),
            "v4_wins_pure_holm": sum(v["pure"] == "v4" and v["p_holm"] < ALPHA_HOLM for v in cells.values()),
            "X_wins_gate": sum(v["gate"] == "X" for v in cells.values()),
            "X_wins_gate_holm": sum(v["gate"] == "X" and v["p_holm"] < ALPHA_HOLM for v in cells.values()),
            "X_wins_pure": sum(v["pure"] == "X" for v in cells.values()),
            "X_wins_pure_holm": sum(v["pure"] == "X" and v["p_holm"] < ALPHA_HOLM for v in cells.values()),
            "cells": cells,
        }
    if incomplete:
        return "NOT CONFIRMED (incomplete: " + ", ".join(incomplete) + ")", per
    if all(v["v4_wins_gate_holm"] == 12 and v["X_wins_gate"] == 0 and v["X_wins_pure"] == 0 for v in per.values()):
        return "CONFIRMED-A", per
    if all(v["v4_wins_gate_holm"] >= 10 and v["X_wins_gate"] == 0 and v["X_wins_pure"] == 0 for v in per.values()):
        return "CONFIRMED-A'", per
    return "NOT CONFIRMED", per


def v4_realisation_check(rows):
    p = ROOT / f"results/{P1_RUN}/runs.jsonl"
    if not p.exists():
        return {"status": f"results/{P1_RUN}/runs.jsonl not available"}
    other = {}
    for line in p.open(encoding="utf-8"):
        r = json.loads(line)
        if r["method"] == REF and r["T"] in TS:
            other[key(r)] = r
    same = tot = 0
    for r in rows:
        if r["method"] == REF and r["status"] == "ok" and key(r) in other and other[key(r)]["status"] == "ok":
            tot += 1
            o = other[key(r)]
            same += (r["iscore_nonnull_mean"] == o["iscore_nonnull_mean"]
                     and r["n_covered_nonnull"] == o["n_covered_nonnull"])
    return {"status": "compared", "identical": same, "compared": tot}


def render(res):
    L = [f"# P5 TLP spec (docs/ext/tlp3.md): {res['mode']}", "",
         f"Rows {res['n_rows']}, duplicates {res['duplicates']}, expected runs per cell {res['expected_runs_per_cell']}, "
         f"min paired ok runs per cell {res['min_ok_pairs_per_cell']}. Failed rows by method: {res['failures']}.",
         f"Config check: {res.get('config_check')}. v4 realisation vs {P1_RUN}: {res.get('v4_realisation')}.", "",
         "| cell | v4 cov / IS | targeted_lp | tlp2_db | tlp2_db_p3 |", "|---|---|---|---|---|"]
    for c, cs in res["cells"].items():
        m = cs["methods"]
        f = lambda x: "–" if m[x]["IS"] is None else f"{m[x]['cov']:.3f} / {m[x]['IS']:.2f} (ok {m[x]['n_ok']})"  # noqa: E731
        L.append(f"| {c} | {f(REF)} | {f('targeted_lp')} | {f('tlp2_db')} | {f('tlp2_db_p3')} |")
    L += ["", "## v4 − X, IS, 95% CI (topology bootstrap 10000), p two-sided, Holm p within 12 damaged cells", "",
          "| cell | − targeted_lp | − tlp2_db | − tlp2_db_p3 |", "|---|---|---|---|"]
    per = res["claim"][1]
    for c, cs in res["cells"].items():
        out = []
        for X in VERSIONS:
            v = cs["comps"][X]
            if "d" not in v:
                out.append("–")
                continue
            h = per[X]["cells"].get(c)
            tail = f" pH={h['p_holm']:.4f} gate={h['gate']} pure={h['pure']}" if h else ""
            out.append(f"{v['d']:+.2f} [{v['lo']:+.2f}, {v['hi']:+.2f}] p={v['p']:.4f}{tail}")
        L.append(f"| {c} | " + " | ".join(out) + " |")
    L += ["", "## Counts over the 12 damaged cells (raw / Holm)", "",
          "| X | v4 wins gate | v4 wins gate Holm | v4 wins pure | v4 wins pure Holm | X wins gate | X wins gate Holm | X wins pure | X wins pure Holm |",
          "|---|---|---|---|---|---|---|---|---|"]
    for X, v in per.items():
        L.append(f"| {X} | {v['v4_wins_gate']} | {v['v4_wins_gate_holm']} | {v['v4_wins_pure']} | {v['v4_wins_pure_holm']} | "
                 f"{v['X_wins_gate']} | {v['X_wins_gate_holm']} | {v['X_wins_pure']} | {v['X_wins_pure_holm']} |")
    L += ["", f"## Verdict: **{res['claim'][0]}**", ""]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=None, help="results/<run>/ (confirmatory mode)")
    ap.add_argument("--dev", action="store_true", help="development/plumbing mode: no config check, never confirmatory")
    ap.add_argument("--runs-files", nargs="*", default=None)
    ap.add_argument("--out", required=True)
    cli = ap.parse_args()
    if cli.dev:
        paths = [ROOT / p for p in cli.runs_files]
        rows = load_rows(paths)
        units = sorted({(r["topology"], r["replicate"]) for r in rows})
        res = analyse(rows, units, "DEVELOPMENT / NOT CONFIRMATORY")
        res["config_check"] = "skipped (dev mode)"
    else:
        run_dir = ROOT / "results" / cli.run
        man = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        frozen = json.loads((ROOT / CONFIG).read_text(encoding="utf-8"))
        rows = load_rows([run_dir / "runs.jsonl"])
        units = [(t["id"], rep) for t in man["topologies"] for rep in range(frozen["replicates"])]
        res = analyse(rows, units, "CONFIRMATORY P4-H2")
        res["config_check"] = "identical" if man["config"] == frozen else "MISMATCH"
        res["seconds"] = man.get("seconds")
    res["claim"] = decide(res)
    if res["config_check"] == "MISMATCH":
        res["claim"] = ("INVALID (manifest config differs from " + CONFIG + ")", res["claim"][1])
    res["v4_realisation"] = v4_realisation_check(rows) if not cli.dev else "skipped (dev mode)"
    out = ROOT / cli.out
    out.mkdir(parents=True, exist_ok=True)
    (out / "verdict.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    (out / "verdict.md").write_text(render(res), encoding="utf-8")
    print(render(res))


if __name__ == "__main__":
    main()
