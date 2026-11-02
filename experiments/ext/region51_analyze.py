"""Usable-region map for tolerant_v5_1 vs tolerant_v4 (docs/ext/region51.md, rule written before the runs)."""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRID = {1: [19, 25, 30, 40], 2: [19, 25, 30, 40, 60], 4: [40, 60, 80, 150]}
CELLS = [("none", 0.0), ("missing", 0.2), ("missing", 0.5), ("reversed", 0.2), ("reversed", 0.5)]
METHODS = ["plugin", "tolerant_v4", "tolerant_v5_1"]


def load(lag):
    rows = [json.loads(l) for l in open(ROOT / f"results/ext_region51_lag{lag}/runs.jsonl")]
    g = defaultdict(list)
    for r in rows:
        g[(r["method"], r["T"], r["kind"], r["rate"])].append(r)
    return g


def cell_stats(rs):
    ok = [r for r in rs if r["status"] == "ok"]
    den = sum(r["n_nonnull"] for r in ok)
    cov = sum(r["n_covered_nonnull"] for r in ok) / den if den else float("nan")
    iss = [r["iscore_nonnull_mean"] for r in ok if r.get("iscore_nonnull_mean") is not None]
    return len(ok), len(rs), cov, (sum(iss) / len(iss) if iss else float("nan"))


def paired_plugin_check(lag):
    old = {(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"]): r
           for r in map(json.loads, open(ROOT / f"results/rq42_region_lag{lag}/runs.jsonl")) if r["method"] == "plugin"}
    new = {(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"]): r
           for r in map(json.loads, open(ROOT / f"results/ext_region51_lag{lag}/runs.jsonl")) if r["method"] == "plugin"}
    same = sum(1 for k, r in new.items() if k in old and old[k].get("iscore_nonnull_mean") == r.get("iscore_nonnull_mean")
               and old[k]["status"] == r["status"])
    return same, len(new)


out = ["# Vùng dùng được: v5.1 so với v4 (sinh bởi experiments/ext/region51_analyze.py)", ""]
summary = {}
for lag, Ts in GRID.items():
    g = load(lag)
    same, tot = paired_plugin_check(lag)
    out += [f"## lag_max = {lag}", "", f"Kiểm tra ghép cặp với rq42_region_lag{lag}: plugin trùng {same}/{tot} dòng.", "",
            "Mỗi ô: coverage / IS (số run ok/60); **U** = dùng được theo định nghĩa ghi trước, x = không.", "",
            "| T | method | " + " | ".join(f"{k}-{r}" for k, r in CELLS) + " |", "|---|---|" + "---|" * len(CELLS)]
    usable = {}
    for T in Ts:
        okn, totn, _, oracle_is = cell_stats(g[("oracle", T, "none", 0.0)])
        for m in METHODS:
            cells = []
            for k, r in CELLS:
                n_ok, n, cov, IS = cell_stats(g[(m, T, k, r)])
                u = n_ok >= 57 and cov >= 0.90 and IS <= 3 * oracle_is
                usable[(m, T, k, r)] = u
                cells.append(f"{cov:.2f} / {IS:.2f} ({n_ok}/{n}) {'**U**' if u else 'x'}" if n_ok else f"– ({n_ok}/{n}) x")
            out.append(f"| {T} | {m} | " + " | ".join(cells) + " |")
    out += [""]
    for m in ("tolerant_v4", "tolerant_v5_1"):
        for kind in ("none", "missing", "reversed"):
            rates = [0.0] if kind == "none" else [0.2, 0.5]
            ok_T = [T for T in Ts if all(usable[(m, T, kind, r)] for r in rates)]
            tmin = next((T for T in Ts if all(t in ok_T for t in Ts if t >= T)), None)
            summary[(lag, m, kind)] = tmin
    out += [f"T tối thiểu (lag_max {lag}): " + "; ".join(f"{m} {kind}: {summary[(lag, m, kind)]}"
            for m in ("tolerant_v4", "tolerant_v5_1") for kind in ("none", "missing", "reversed")), ""]
dst = ROOT / "results/ext_region51/region_map.md"
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
