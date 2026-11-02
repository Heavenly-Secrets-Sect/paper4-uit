"""Score the pre-registered descriptive rule of docs/ext/tlp2.md (R2-8) from the runs of the
ext_tlp2_* evaluation configs. Writes results/ext_tlp2_rules/rules.md and rules.json.

Rule summary (the doc is authoritative):
- versions X: targeted_lp (round 1, single-level), tlp2_db (faithful MSDB, p = 2q), tlp2_db_p3
  (MSDB, p = q + 1; T >= 80 only), tlp2_lp_cal (calibrated single-level, adaptation, not published).
- per cell: d = mean paired IS(v4) - IS(X) over runs, 95% percentile CI and two-sided p-value from
  a bootstrap that resamples topologies (10000 resamples, seed 0).
- gate view: v4 wins if cov(v4) >= 0.90 and CI upper < 0; X wins if cov(X) >= 0.90 and CI lower > 0.
- pure-IS view: the same without the coverage conditions.
- Holm: within each (version, view, family), family = the damaged cells at T >= 80 (12) and,
  separately, all damaged cells run (18, or 12 for tlp2_db_p3); a win survives Holm if its
  direction holds and its Holm-adjusted p < 0.05 (plus the coverage condition in the gate view).
Usage: python experiments/ext/tlp2/score.py
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

RUNS = ["t40", "t80a", "t80b", "t80c", "t150a", "t150b", "t150c", "t150d"]
REF = "tolerant_v4"
VERSIONS = ["targeted_lp", "tlp2_db", "tlp2_db_p3", "tlp2_lp_cal"]
PUBLISHED = ["targeted_lp", "tlp2_db", "tlp2_db_p3"]
CELLS = [("none", 0.0)] + [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]
NB = 10000
GATE = 0.90


def load():
    rows, missing_runs = [], []
    for tag in RUNS:
        p = ROOT / f"results/ext_tlp2_{tag}/runs.jsonl"
        if not p.exists():
            missing_runs.append(tag)
            continue
        rows += [json.loads(line) for line in p.open()]
    return rows, missing_runs


def key(r):
    return (r["topology"], r["replicate"], r["T"], r["kind"], float(r["rate"]))


def boot_diff(diffs_by_topo, rng):
    topos = list(diffs_by_topo)
    vals = [np.array(diffs_by_topo[t]) for t in topos]
    sums = np.array([v.sum() for v in vals])
    cnts = np.array([len(v) for v in vals])
    est = sums.sum() / cnts.sum()
    pick = rng.integers(0, len(topos), size=(NB, len(topos)))
    b = sums[pick].sum(axis=1) / cnts[pick].sum(axis=1)
    lo, hi = np.quantile(b, (0.025, 0.975))
    p = min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean()))
    return float(est), float(lo), float(hi), max(p, 1.0 / NB)


def holm(pvals):
    """Holm-adjusted p-values (step-down, monotone)."""
    m = len(pvals)
    order = np.argsort(pvals)
    adj = np.empty(m)
    run = 0.0
    for rank, i in enumerate(order):
        run = max(run, (m - rank) * pvals[i])
        adj[i] = min(1.0, run)
    return adj


def pooled_cov(rs):
    d = sum(r.get("n_nonnull", 0) for r in rs)
    return sum(r.get("n_covered_nonnull", 0) for r in rs) / d if d else float("nan")


def db90_is10(rows):
    """Interval score at the paper's own level (alpha = 0.10) for tlp2_db90, from the stored lo/hi
    and the truth rebuilt from the same seeds as the runner."""
    from paper4.generator import build_dynamic_sem
    from paper4.metrics import interval_score, truth_effects
    from paper4.topology import load_bank
    from run_experiment import generator_config
    cfg = json.loads((ROOT / "experiments/configs/ext_tlp2_t80a.json").read_text())
    gen = generator_config(cfg)
    topos = load_bank(cfg["bank"], cfg["split"])
    idx = {t.id: i for i, t in enumerate(topos)}
    truth = {}
    out = defaultdict(list)
    for r in rows:
        if r["method"] != "tlp2_db90" or r["status"] != "ok":
            continue
        tk = (r["topology"], r["replicate"])
        if tk not in truth:
            t_idx = idx[r["topology"]]
            unit = cfg["seed_base"] + 1000 * t_idx + r["replicate"]
            sem = build_dynamic_sem(topos[t_idx], gen, np.random.default_rng([unit, 0]))
            _, C_t, _, _ = truth_effects(sem, cfg["H"])
            nn = ~np.eye(sem.n, dtype=bool) & (np.abs(C_t) > cfg["tau_effect"])
            truth[tk] = (C_t, nn)
        C_t, nn = truth[tk]
        lo, hi = np.array(r["info_lo"]), np.array(r["info_hi"])
        out[(r["T"], r["kind"], float(r["rate"]))].append(float(interval_score(lo, hi, C_t, 0.10)[nn].mean()))
    return {k: float(np.mean(v)) for k, v in out.items()}


def main():
    global RUNS
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="*", default=None, help="run tags (default: the eight evaluation runs)")
    ap.add_argument("--out", default="results/ext_tlp2_rules")
    cli = ap.parse_args()
    if cli.runs:
        RUNS = cli.runs
    rows, missing_runs = load()
    ok = [r for r in rows if r["status"] == "ok"]
    idx = {}
    dup = 0
    for r in rows:
        k = key(r) + (r["method"],)
        dup += k in idx
        idx[k] = r
    res = {"missing_runs": missing_runs, "n_rows": len(rows), "n_failed": len(rows) - len(ok), "duplicates": dup}

    # pairing check against round 1 (ext_tlp_eval): frozen v4 must be identical run by run
    r1 = {key(r) + (r["method"],): r for r in map(json.loads, (ROOT / "results/ext_tlp_eval/runs.jsonl").open())}
    same = tot = 0
    tl_diff = []
    for k, r in idx.items():
        if k[-1] == REF and k in r1 and r["status"] == "ok":
            tot += 1
            same += abs(r["iscore_nonnull_mean"] - r1[k]["iscore_nonnull_mean"]) < 1e-9
        if k[-1] == "targeted_lp" and k in r1 and r["status"] == "ok" and r1[k]["status"] == "ok":
            tl_diff.append(r["iscore_nonnull_mean"] - r1[k]["iscore_nonnull_mean"])
    res["pairing_v4_identical"] = [same, tot]
    res["targeted_lp_vs_round1_mean_is_diff"] = float(np.mean(tl_diff)) if tl_diff else None
    res["targeted_lp_vs_round1_n"] = len(tl_diff)

    # per-cell statistics
    rng = np.random.default_rng(0)
    cellstats = {}
    by = defaultdict(list)
    for r in ok:
        by[(r["T"], r["kind"], float(r["rate"]), r["method"])].append(r)
    meth_all = [REF] + VERSIONS + ["tlp2_db90"]
    for T in (40, 80, 150):
        for kind, rate in CELLS:
            c = {}
            for m in meth_all:
                g = by.get((T, kind, rate, m), [])
                if g:
                    c[m] = {"n": len(g), "cov": pooled_cov(g), "IS": float(np.mean([x["iscore_nonnull_mean"] for x in g])),
                            "width": float(np.median([x["width_kept"] for x in g if x.get("width_kept") is not None])),
                            "lost": sum(x["n_lost"] for x in g) / max(1, sum(x["n_nonnull"] for x in g)),
                            "v_mean": float(np.mean([x["info_v_mean"] for x in g])) if "info_v_mean" in g[0] else None}
            comps = {}
            for X in VERSIONS + ["tlp2_db@targeted_lp", "tlp2_db_p3@targeted_lp"]:
                a, b = (REF, X) if "@" not in X else tuple(X.split("@"))
                diffs = defaultdict(list)
                for r in by.get((T, kind, rate, a), []):
                    o = idx.get(key(r) + (b,))
                    if o is not None and o["status"] == "ok":
                        diffs[r["topology"]].append(r["iscore_nonnull_mean"] - o["iscore_nonnull_mean"])
                if diffs:
                    est, lo, hi, p = boot_diff(diffs, rng)
                    comps[X] = {"d": est, "lo": lo, "hi": hi, "p": p, "n": sum(len(v) for v in diffs.values())}
            if c:
                cellstats[f"{T}|{kind}|{rate}"] = {"methods": c, "comps": comps}
    res["cells"] = cellstats

    # verdicts
    def verdict(cs, X, view):
        m, comp = cs["methods"], cs["comps"].get(X)
        if comp is None:
            return None
        g_v4 = (m[REF]["cov"] >= GATE) if view == "gate" else True
        g_x = (m[X]["cov"] >= GATE) if view == "gate" else True
        if g_v4 and comp["hi"] < 0:
            return "v4"
        if g_x and comp["lo"] > 0:
            return "X"
        return "tie"

    counts = {}
    for X in VERSIONS:
        for view in ("gate", "pure"):
            for fam_name, fam_T in (("T>=80", (80, 150)), ("all", (40, 80, 150))):
                fam = [f"{T}|{k}|{r}" for T in fam_T for k, r in CELLS if k != "none"
                       and f"{T}|{k}|{r}" in cellstats and X in cellstats[f"{T}|{k}|{r}"]["comps"]]
                if not fam:
                    continue
                v = {c: verdict(cellstats[c], X, view) for c in fam}
                adj = holm(np.array([cellstats[c]["comps"][X]["p"] for c in fam]))
                holm_v4 = sum(v[c] == "v4" and a < 0.05 for c, a in zip(fam, adj))
                holm_x = sum(v[c] == "X" and a < 0.05 for c, a in zip(fam, adj))
                counts[f"{X}|{view}|{fam_name}"] = {
                    "n_cells": len(fam), "v4_wins": sum(x == "v4" for x in v.values()),
                    "X_wins": sum(x == "X" for x in v.values()), "ties": sum(x == "tie" for x in v.values()),
                    "v4_wins_holm": int(holm_v4), "X_wins_holm": int(holm_x),
                    "per_cell": {c: [v[c], round(float(a), 5)] for c, a in zip(fam, adj)}}
    # undamaged cells (R3-style, no family claim): verdicts per cell
    none_cells = {}
    for T in (40, 80, 150):
        c = f"{T}|none|0.0"
        if c in cellstats:
            none_cells[c] = {X: {"gate": verdict(cellstats[c], X, "gate"), "pure": verdict(cellstats[c], X, "pure")}
                             for X in VERSIONS if X in cellstats[c]["comps"]}
    res["counts"] = counts
    res["none_cells"] = none_cells

    # handicap question: does a faithful double bootstrap beat round-1 targeted_lp? (cov(X) >= 0.90 and CI upper < 0)
    hc = {}
    for X in ("tlp2_db", "tlp2_db_p3"):
        cl = []
        for c, cs in cellstats.items():
            comp = cs["comps"].get(f"{X}@targeted_lp")
            if comp is None:
                continue
            better = cs["methods"][X]["cov"] >= GATE and comp["hi"] < 0
            worse = comp["lo"] > 0
            cl.append((c, "better" if better else ("worse" if worse else "tie")))
        hc[X] = {"n": len(cl), "better": sum(v == "better" for _, v in cl), "worse": sum(v == "worse" for _, v in cl),
                 "cells": dict(cl)}
    res["handicap"] = hc

    # claim A (pre-registered)
    def claim(versions):
        per = {}
        for X in versions:
            g = counts.get(f"{X}|gate|T>=80")
            pu = counts.get(f"{X}|pure|T>=80")
            if g is None:
                per[X] = None
                continue
            per[X] = {"gate": g["v4_wins"], "gate_holm": g["v4_wins_holm"], "n": g["n_cells"],
                      "losses_gate": g["X_wins"], "losses_pure": pu["X_wins"]}
        if any(v is None or v["n"] < 12 for v in per.values()):
            return "incomplete", per
        if all(v["gate"] == 12 and v["gate_holm"] == 12 and v["losses_pure"] == 0 for v in per.values()):
            return "A (unqualified)", per
        if all(v["gate"] >= 10 and v["losses_gate"] == 0 and v["losses_pure"] == 0 for v in per.values()):
            return "A' (qualified: most cells, never loses)", per
        return "not supported", per
    res["claim_A"] = claim(PUBLISHED)
    res["claim_B_cal"] = claim(["tlp2_lp_cal"])
    try:
        res["db90_is_alpha10"] = {f"{T}|{k}|{r}": v for (T, k, r), v in db90_is10(rows).items()}
    except Exception as exc:  # noqa: BLE001
        res["db90_is_alpha10"] = {"error": repr(exc)}

    out = ROOT / cli.out
    out.mkdir(parents=True, exist_ok=True)
    (out / "rules.json").write_text(json.dumps(res, indent=2))
    (out / "rules.md").write_text(render(res))
    print(render(res))


def f3(x):
    return "–" if x is None else f"{x:.3f}"


def render(res):
    L = ["# ext_tlp2: rule of docs/ext/tlp2.md (R2-8)", "",
         f"Rows {res['n_rows']}, failed {res['n_failed']}, duplicates {res['duplicates']}, missing runs {res['missing_runs']}.",
         f"Pairing: frozen tolerant_v4 IS identical to ext_tlp_eval in {res['pairing_v4_identical'][0]}/{res['pairing_v4_identical'][1]} runs. "
         f"targeted_lp vs round 1 (seed by name since round 2): mean IS diff {res['targeted_lp_vs_round1_mean_is_diff']} over {res['targeted_lp_vs_round1_n']} runs.", "",
         "## Per cell: coverage / IS (pooled non-null coverage; mean non-null interval score)", "",
         "| cell | v4 | targeted_lp | tlp2_db | tlp2_db_p3 | tlp2_lp_cal | tlp2_db90 (cov / width) |", "|---|---|---|---|---|---|---|"]
    for c, cs in res["cells"].items():
        m = cs["methods"]
        def cell(x):
            return f"{m[x]['cov']:.3f} / {m[x]['IS']:.2f}" if x in m else "–"
        d90 = f"{m['tlp2_db90']['cov']:.3f} / {m['tlp2_db90']['width']:.2f}" if "tlp2_db90" in m else "–"
        L.append(f"| {c} | {cell(REF)} | {cell('targeted_lp')} | {cell('tlp2_db')} | {cell('tlp2_db_p3')} | {cell('tlp2_lp_cal')} | {d90} |")
    L += ["", "## Paired IS difference v4 − X, 95% CI (topology bootstrap, 10000), p two-sided", "",
          "| cell | − targeted_lp | − tlp2_db | − tlp2_db_p3 | − tlp2_lp_cal | tlp2_db − targeted_lp | tlp2_db_p3 − targeted_lp |",
          "|---|---|---|---|---|---|---|"]
    for c, cs in res["cells"].items():
        def d(x):
            v = cs["comps"].get(x)
            return "–" if v is None else f"{v['d']:+.2f} [{v['lo']:+.2f}, {v['hi']:+.2f}] p={v['p']:.4f}"
        L.append(f"| {c} | {d('targeted_lp')} | {d('tlp2_db')} | {d('tlp2_db_p3')} | {d('tlp2_lp_cal')} | "
                 f"{d('tlp2_db@targeted_lp')} | {d('tlp2_db_p3@targeted_lp')} |")
    L += ["", "## Cell counts (damaged cells)", "",
          "| version | view | family | cells | v4 wins | v4 wins (Holm) | X wins | X wins (Holm) | ties |", "|---|---|---|---|---|---|---|---|---|"]
    for k, v in res["counts"].items():
        X, view, fam = k.split("|")
        L.append(f"| {X} | {view} | {fam} | {v['n_cells']} | {v['v4_wins']} | {v['v4_wins_holm']} | {v['X_wins']} | {v['X_wins_holm']} | {v['ties']} |")
    L += ["", "## Undamaged cells (no family claim)", ""]
    for c, v in res["none_cells"].items():
        L.append(f"- {c}: " + "; ".join(f"{X} gate={w['gate']} pure={w['pure']}" for X, w in v.items()))
    L += ["", "## Handicap question (X vs round-1 targeted_lp; better = cov(X) >= 0.90 and CI upper < 0)", ""]
    for X, v in res["handicap"].items():
        L.append(f"- {X}: {v['n']} cells, better {v['better']}, worse {v['worse']}: {v['cells']}")
    L += ["", f"## Claim A (published TLP versions, T >= 80): **{res['claim_A'][0]}**", "", f"`{json.dumps(res['claim_A'][1])}`", "",
          f"Claim B (calibrated adaptation tlp2_lp_cal, T >= 80): **{res['claim_B_cal'][0]}** `{json.dumps(res['claim_B_cal'][1])}`", "",
          "## tlp2_db90 interval score at alpha = 0.10 (its own level; descriptive)", ""]
    for c, v in res["db90_is_alpha10"].items():
        L.append(f"- {c}: {v if isinstance(v, str) else round(v, 3)}")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
