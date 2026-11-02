"""D3 (docs/ext/auto3fix.md 1.3): tolerant_auto3 vs tolerant_v5_1 on the stored a2-grid rows of D-07
development. Descriptive, no rule. auto3 rows: results/ext_gate_auto3; v5_1 rows: results/ext_v51_eval.
Pairing check first: tolerant_v4 rows of the two runs must have equal iscore_nonnull_mean on every
common key (same data, skeleton and v4 seed). Paired IS difference auto3 - v5_1 per cell, 95% CI and
two-sided p from a cluster bootstrap over topologies (2000, seed 0), Holm over the 21 cells.
Output: results/ext_auto3fix_v51pair/{pairs.json, pairs.md}.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_p4h2_v2 as C  # noqa: E402

ROOT = C.ROOT
CELLS = [(T, k, r) for T in (40, 80, 150) for k, r in [("none", 0.0)] + [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]]


def idx(path, methods):
    d = defaultdict(dict)
    for r in C.load_rows(path):
        if r["method"] in methods and r.get("scenario", "clean") == "clean":
            d[r["method"]][(r["topology"], r["replicate"], r["T"], r["kind"], float(r["rate"]))] = r
    return d


def boot(diffs_by_topo, seed=0, n=2000):
    topos = list(diffs_by_topo)
    s = np.array([sum(diffs_by_topo[t]) for t in topos])
    c = np.array([len(diffs_by_topo[t]) for t in topos])
    rng = np.random.default_rng(seed)
    pick = rng.integers(0, len(topos), (n, len(topos)))
    b = s[pick].sum(1) / c[pick].sum(1)
    lo, hi = np.quantile(b, (0.025, 0.975))
    return float(s.sum() / c.sum()), float(lo), float(hi), float(min(1.0, 2 * min(np.mean(b <= 0), np.mean(b >= 0)))), int(c.sum())


def cov(rows):
    den = sum(r["n_nonnull"] for r in rows)
    return sum(r["n_covered_nonnull"] for r in rows) / den if den else float("nan")


def main():
    A = idx(ROOT / "results/ext_gate_auto3/runs.jsonl", {"tolerant_auto3", "tolerant_v4"})
    V = idx(ROOT / "results/ext_v51_eval/runs.jsonl", {"tolerant_v5_1", "tolerant_v4"})
    common = set(A["tolerant_v4"]) & set(V["tolerant_v4"])
    same = sum(1 for k in common if A["tolerant_v4"][k].get("status") == V["tolerant_v4"][k].get("status")
               and A["tolerant_v4"][k].get("iscore_nonnull_mean") == V["tolerant_v4"][k].get("iscore_nonnull_mean"))
    pairing = {"common_keys": len(common), "v4_identical": same, "ok": same == len(common) == 1260}
    out = ROOT / "results" / "ext_auto3fix_v51pair"
    out.mkdir(parents=True, exist_ok=True)
    if not pairing["ok"]:
        (out / "pairs.json").write_text(json.dumps({"pairing": pairing}, indent=1))
        print("pairing check failed", pairing)
        return
    res = []
    for T, k, r in CELLS:
        keys = [x for x in common if x[2:] == (T, k, r)]
        a = [A["tolerant_auto3"][x] for x in keys if x in A["tolerant_auto3"] and C.is_ok(A["tolerant_auto3"][x])]
        v = [V["tolerant_v5_1"][x] for x in keys if x in V["tolerant_v5_1"] and C.is_ok(V["tolerant_v5_1"][x])]
        d = defaultdict(list)
        for x in keys:
            ra, rv = A["tolerant_auto3"].get(x), V["tolerant_v5_1"].get(x)
            if ra and rv and C.is_ok(ra) and C.is_ok(rv):
                d[x[0]].append(ra["iscore_nonnull_mean"] - rv["iscore_nonnull_mean"])
        est, lo, hi, p, n = boot(d)
        res.append({"cell": f"{T}|{k}|{r}", "cov_auto3": cov(a), "cov_v51": cov(v), "n_ok_auto3": len(a), "n_ok_v51": len(v),
                    "IS_auto3": float(np.mean([x["iscore_nonnull_mean"] for x in a])),
                    "IS_v51": float(np.mean([x["iscore_nonnull_mean"] for x in v])),
                    "diff": est, "lo": lo, "hi": hi, "p": p, "n_pairs": n,
                    "call": "auto3 better" if hi < 0 else ("auto3 worse" if lo > 0 else "tie")})
    rej = C.holm([x["p"] for x in res])
    for x, h in zip(res, rej):
        x["holm"] = bool(h)

    def tally(sub):
        return {"better": sum(x["call"] == "auto3 better" for x in sub), "tie": sum(x["call"] == "tie" for x in sub),
                "worse": sum(x["call"] == "auto3 worse" for x in sub),
                "holm_better": sum(x["holm"] and x["diff"] < 0 for x in sub), "holm_worse": sum(x["holm"] and x["diff"] > 0 for x in sub)}

    groups = {"all21": res, "T40": [x for x in res if x["cell"].startswith("40|")],
              "T80_150": [x for x in res if not x["cell"].startswith("40|")],
              "missing_reversed_T80_150": [x for x in res if not x["cell"].startswith("40|") and ("missing" in x["cell"] or "reversed" in x["cell"])]}
    J = {"pairing": pairing, "cells": res, "tally": {g: tally(s) for g, s in groups.items()}}
    (out / "pairs.json").write_text(json.dumps(J, indent=1), encoding="utf-8")
    L = ["# D3: tolerant_auto3 vs tolerant_v5_1 on stored D-07 a2-grid rows (descriptive, no rule)", "",
         f"Pairing: tolerant_v4 rows identical on {same}/{len(common)} common keys (ext_gate_auto3 vs ext_v51_eval).",
         "auto3 does not read the stated damage; v5_1 does. auto3 rows use round-1 bootstrap seeds.", "",
         "| cell | cov auto3 | cov v5_1 | IS auto3 | IS v5_1 | auto3 - v5_1 [95% CI] | p | Holm(21) | call |", "|---|---|---|---|---|---|---|---|---|"]
    for x in res:
        L.append(f"| {x['cell']} | {x['cov_auto3']:.3f} | {x['cov_v51']:.3f} | {x['IS_auto3']:.2f} | {x['IS_v51']:.2f} | "
                 f"{x['diff']:+.2f} [{x['lo']:+.2f}, {x['hi']:+.2f}] | {x['p']:.4f} | {'yes' if x['holm'] else 'no'} | {x['call']} |")
    L += [""] + [f"- {g}: better/tie/worse {t['better']}/{t['tie']}/{t['worse']}; Holm better {t['holm_better']}, Holm worse {t['holm_worse']}" for g, t in J["tally"].items()]
    (out / "pairs.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
