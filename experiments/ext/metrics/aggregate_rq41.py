"""RQ4.1 error characterisation from the stored run-level results (no new runs).

Reads results/{a2_baselines, a2b_pselect, rq42_v4, rq42_v4_heldout, a2_heldout, a1_latent_noise, a3_ges}/runs.jsonl
and writes results/ext_metrics_rq41/{tables.md, cells.json}.

Per (source, scenario, T, damage kind, rate, method):
- abs / rel error of C(H): median over runs of the run's median over non-null pairs
- sign error: mean over runs of the share of kept non-null pairs with the wrong sign
- lost: pooled share of non-null pairs with estimate exactly 0
- mean-lag error: median over runs of the run's median |mean lag error|
- peak-lag hit: mean over runs of the share of kept non-null pairs whose peak lag is right
- coverage: pooled over non-null pairs; width: median over runs of the median width (kept pairs)
- IS: mean over runs of the mean interval score of non-null pairs
Run-level rows only carry medians, so these are medians of medians, as in every summary.md.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "ext_metrics_rq41"

SOURCES = {
    "a2_baselines": None, "a2b_pselect": {"pselect_union"}, "rq42_v4": None, "rq42_v4_heldout": None,
    "a2_heldout": None, "a1_latent_noise": None, "a3_ges": None,
}
METRICS = ("abs", "rel", "sign", "lost", "mlag", "peak", "cov", "width", "IS")


def load(name, keep=None):
    rows = []
    with open(ROOT / "results" / name / "runs.jsonl", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["status"] != "ok" or (keep and r["method"] not in keep):
                continue
            rows.append(r)
    return rows


def stats(g):
    def med(k):
        v = [r[k] for r in g if r.get(k) is not None]
        return float(np.median(v)) if v else None

    def mean(k):
        v = [r[k] for r in g if r.get(k) is not None]
        return float(np.mean(v)) if v else None

    def pooled(num, den):
        d = sum(r.get(den) or 0 for r in g)
        return sum(r.get(num) or 0 for r in g) / d if d else None

    return {"n_runs": len(g), "abs": med("C_abs_err_nonnull"), "rel": med("C_rel_err_nonnull"),
            "sign": mean("C_sign_err_kept"), "lost": pooled("n_lost", "n_nonnull"), "mlag": med("mean_lag_abs_err"),
            "peak": mean("peak_lag_hit_kept"), "cov": pooled("n_covered_nonnull", "n_nonnull"),
            "width": med("width_kept"), "IS": mean("iscore_nonnull_mean")}


def fmt(v, d=3):
    return "–" if v is None else f"{v:.{d}f}"


def table(cells, src, methods, scen="clean", Ts=None, kinds=None, title=""):
    keys = sorted({(k[2], k[3], k[4]) for k in cells if k[0] == src and k[1] == scen},
                  key=lambda x: (x[0], ["none", "extra", "missing", "reversed", "ges"].index(x[1]), x[2]))
    lines = [f"### {title}", "", "| T | damage | rate | method | abs | rel | sign | lost | mean-lag | peak hit | cov | width | IS |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for T, kind, rate in keys:
        if (Ts and T not in Ts) or (kinds and kind not in kinds):
            continue
        for m in methods:
            s = cells.get((src, scen, T, kind, rate, m))
            if s is None:
                continue
            lines.append(f"| {T} | {kind} | {rate:.1f} | {m} | {fmt(s['abs'])} | {fmt(s['rel'])} | {fmt(s['sign'])} | "
                         f"{fmt(s['lost'])} | {fmt(s['mlag'])} | {fmt(s['peak'])} | {fmt(s['cov'])} | {fmt(s['width'])} | "
                         f"{fmt(s['IS'], 2)} |")
    return "\n".join(lines)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    groups = defaultdict(list)
    for src, keep in SOURCES.items():
        for r in load(src, keep):
            groups[(src, r.get("scenario", "clean"), r["T"], r["kind"], r["rate"], r["method"])].append(r)
    cells = {k: stats(g) for k, g in groups.items()}
    # D-07 development, seeds 20261102: a2_baselines plus pselect_union from a2b_pselect under one source
    for k, s in list(cells.items()):
        if k[0] == "a2b_pselect":
            cells[("a2_baselines",) + k[1:]] = s
    (OUT / "cells.json").write_text(json.dumps({"|".join(map(str, k)): v for k, v in cells.items()}, indent=1),
                                    encoding="utf-8")
    pub = ["oracle", "plugin", "inflate", "lp_allpast", "bagging", "ida_union", "bvar_minnesota", "pselect_union",
           "tolerant_v4"]
    parts = ["# RQ4.1 error characterisation from stored run-level results", "", __doc__.split("\n\n", 1)[1], "",
             table(cells, "a2_baselines", pub, title="D-07 development (a2_baselines + a2b_pselect), T = 40/80/150"),
             "", table(cells, "rq42_v4", ["oracle", "plugin", "inflate", "lp_allpast", "tolerant_v4"], Ts=[300],
                       title="D-07 development, T = 300 (rq42_v4, seed_base 20261101: a different sample)"),
             "", table(cells, "rq42_v4_heldout", ["oracle", "plugin", "inflate", "lp_allpast", "tolerant_v4"],
                       title="P4-H1 confirmatory (rq42_v4_heldout, stored; read only)"),
             "", table(cells, "a2_heldout", pub, title="P4-H1 development (a2_heldout, stored; read only)"),
             "", table(cells, "a3_ges", pub, title="GES skeletons (a3_ges, D-07 development)")]
    for sc in ("clean", "latent1", "latent3", "noise0.1", "noise0.3"):
        parts += ["", table(cells, "a1_latent_noise", pub, scen=sc, title=f"a1_latent_noise, scenario {sc}")]
    (OUT / "tables.md").write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"{len(cells)} cells -> {OUT}")


if __name__ == "__main__":
    main()
