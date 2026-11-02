"""R2-3c: apply the pre-registered rule of docs/ext/auto5.md section 3.3 to results/ext_auto5_main.

C1 coverage >= 0.90 in missing/reversed x 0.2/0.5 at T = 80, 150; C2 IS(none) <= 1.35 x v4 at T = 40,
80, 150; C3 GES at T = 80, 150: coverage >= 0.90 and IS <= 1.10 x v4; C4 at T = 40 missing-0.2 and
missing-0.5: lower 95% CI bound of paired IS(m) - IS(pselect_union) <= 0 (bootstrap over topologies).
Ruled for tolerant_auto5; tolerant_auto5_small is scored the same way for the report only.

Run: python experiments/ext/auto5/check_main.py -> results/ext_auto5_main/rule_check.{md,json}
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stats5 as S  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "ext_auto5_main"
CELLS = [("none", 0.0), ("extra", 0.2), ("extra", 0.5), ("missing", 0.2), ("missing", 0.5),
         ("reversed", 0.2), ("reversed", 0.5), ("ges", 0.0)]
TS = (40, 80, 150)


def one_sided_worse(idx, sel, m, ref, seed=0):
    """p for H0 'm is not worse than ref': share of bootstrap means of IS(m) - IS(ref) that are <= 0."""
    d = defaultdict(list)
    for k, ms in idx.items():
        if sel(k) and m in ms and ref in ms:
            d[k[1]].append(ms[m]["iscore_nonnull_mean"] - ms[ref]["iscore_nonnull_mean"])
    topos = list(d)
    sums = np.array([sum(d[t]) for t in topos])
    cnts = np.array([len(d[t]) for t in topos])
    rng = np.random.default_rng(seed)
    pick = rng.integers(0, len(topos), size=(S.N_BOOT, len(topos)))
    boots = sums[pick].sum(1) / cnts[pick].sum(1)
    return float(np.mean(boots <= 0))


def main():
    rows = S.load(OUT / "runs.jsonl")
    gate = [r for r in S.load(ROOT / "results" / "ext_gate_auto3" / "runs.jsonl") if r["method"] == "tolerant_auto3"]
    chk = {}
    for m, src in (("plugin", "a2_baselines"), ("pselect_union", "a2b_pselect"), ("plugin", "ext_gate_auto3")):
        mine = {S.key(r): r["iscore_nonnull_mean"] for r in rows if r["method"] == m and r["status"] == "ok"}
        ref = {S.key(r): r["iscore_nonnull_mean"] for r in S.load(ROOT / "results" / src / "runs.jsonl")
               if r["method"] == m and r["status"] == "ok"}
        common = set(mine) & set(ref)
        chk[f"{m} vs {src}"] = {"identical": sum(abs(mine[k] - ref[k]) < 1e-9 for k in common), "compared": len(common),
                                "mine": len(mine)}
    idx = S.index(rows + gate)
    grp = defaultdict(list)
    for r in rows + gate:
        grp[(r["T"], r["kind"], r["rate"], r["method"])].append(r)

    def cs(T, kind, rate, m):
        g = grp[(T, kind, rate, m)]
        ok = [r for r in g if r["status"] == "ok"]
        return {"ok": f"{len(ok)}/{len(g)}", "cov": S.coverage(ok),
                "IS": float(np.mean([r["iscore_nonnull_mean"] for r in ok])) if ok else None}

    meths = ["plugin", "pselect_union", "tolerant_v4", "tolerant_auto3", "tolerant_auto5", "tolerant_auto5_small"]
    J = {"pairing": chk, "cells": {}, "rule": {}}
    L = ["# R2-3c: tolerant_auto5 (B1 v5), D-07 development", "", f"Pairing: {json.dumps(chk)}", "",
         "`tolerant_auto3`: rows of results/ext_gate_auto3 (same data and skeletons, round-1 bootstrap seed).", "",
         "## Coverage / IS", "", "| T | cell | " + " | ".join(meths) + " |", "|---|---|" + "---|" * len(meths)]
    for T in TS:
        for kind, rate in CELLS:
            key = f"{T}|{kind}|{rate}"
            c = {m: cs(T, kind, rate, m) for m in meths}
            sel = lambda k, T=T, kind=kind, rate=rate: k[3] == T and k[4] == kind and k[5] == rate  # noqa: E731
            for m in ("tolerant_auto5", "tolerant_auto5_small"):
                for ref in ("tolerant_v4", "plugin", "pselect_union", "tolerant_auto3", "tolerant_auto5"):
                    if ref != m:
                        c[f"{m}-{ref}"] = S.paired(idx, sel, m, ref)
                a = [r for r in grp[(T, kind, rate, m)] if r["status"] == "ok"]
                c[f"{m}_gate_open"] = float(np.mean([r.get("info_state") == "open" for r in a])) if a else None
                no = [r.get("info_n_open") for r in a if r.get("info_n_open") is not None]
                c[f"{m}_n_open"] = float(np.mean(no)) if no else None
                c[f"{m}_branches"] = {b: sum(r.get("info_branch") == b for r in a) for b in ("closed", "open_tgt", "open_all")}
            J["cells"][key] = c
            L.append(f"| {T} | {kind} {rate} | " + " | ".join(
                "–" if c[m]["cov"] != c[m]["cov"] else f"{c[m]['cov']:.3f} / {c[m]['IS']:.2f}" for m in meths) + " |")
    L += ["", "## Paired IS differences (95% CI clustered by topology); gate open rate; mean opened pairs", "",
          "| T | cell | auto5 - v4 | auto5 - plugin | auto5 - pselect | auto5 - auto3 | small - v4 | small - pselect | small - auto5 | auto5 gate open | auto5 n_open |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for key, c in J["cells"].items():
        T, kind, rate = key.split("|")
        L.append(f"| {T} | {kind} {rate} | {S.fmt(c['tolerant_auto5-tolerant_v4'])} | {S.fmt(c['tolerant_auto5-plugin'])} | "
                 f"{S.fmt(c['tolerant_auto5-pselect_union'])} | {S.fmt(c['tolerant_auto5-tolerant_auto3'])} | "
                 f"{S.fmt(c['tolerant_auto5_small-tolerant_v4'])} | {S.fmt(c['tolerant_auto5_small-pselect_union'])} | "
                 f"{S.fmt(c['tolerant_auto5_small-tolerant_auto5'])} | {c['tolerant_auto5_gate_open']:.2f} | "
                 + ("–" if c["tolerant_auto5_n_open"] is None else f"{c['tolerant_auto5_n_open']:.1f}") + " |")

    for m in ("tolerant_auto5", "tolerant_auto5_small"):
        R = {}
        c1 = []
        for T in (80, 150):
            for kind in ("missing", "reversed"):
                for rate in (0.2, 0.5):
                    a = [r for r in grp[(T, kind, rate, m)] if r["status"] == "ok"]
                    cov, p = S.coverage_test(a)
                    c1.append({"cell": f"{T}|{kind}|{rate}", "cov": cov, "p": p, "ok": cov >= 0.90})
        c3 = []
        for T in (80, 150):
            a = [r for r in grp[(T, "ges", 0.0, m)] if r["status"] == "ok"]
            cov, p = S.coverage_test(a)
            ratio = J["cells"][f"{T}|ges|0.0"][m]["IS"] / J["cells"][f"{T}|ges|0.0"]["tolerant_v4"]["IS"]
            c3.append({"T": T, "cov": cov, "p": p, "ratio": ratio, "ok": cov >= 0.90 and ratio <= 1.10})
        rej = S.holm([x["p"] for x in c1] + [x["p"] for x in c3])
        c2 = [{"T": T, "ratio": J["cells"][f"{T}|none|0.0"][m]["IS"] / J["cells"][f"{T}|none|0.0"]["tolerant_v4"]["IS"]} for T in TS]
        for x in c2:
            x["ok"] = x["ratio"] <= 1.35
        c4 = []
        for rate in (0.2, 0.5):
            d = J["cells"][f"40|missing|{rate}"][f"{m}-pselect_union"]
            sel = lambda k, rate=rate: k[3] == 40 and k[4] == "missing" and k[5] == rate  # noqa: E731
            c4.append({"cell": f"40|missing|{rate}", **d, "p_worse": one_sided_worse(idx, sel, m, "pselect_union"),
                       "ok": d["lo"] <= 0, "ok_point": d["est"] <= 0})
        rej4 = S.holm([x["p_worse"] for x in c4])
        R = {"C1": {"cells": c1, "pass": all(x["ok"] for x in c1)}, "C2": {"cells": c2, "pass": all(x["ok"] for x in c2)},
             "C3": {"cells": c3, "pass": all(x["ok"] for x in c3)}, "C4": {"cells": c4, "pass": all(x["ok"] for x in c4)},
             "holm_cov_rejected": int(sum(rej)), "holm_cov_n": len(rej), "holm_c4_worse_rejected": int(sum(rej4))}
        R["retained"] = all(R[k]["pass"] for k in ("C1", "C2", "C3", "C4"))
        J["rule"][m] = R
        tag = "RULED" if m == "tolerant_auto5" else "REPORT ONLY (ablation)"
        L += ["", f"## Rule for `{m}` ({tag})", ""]
        L.append(f"- C1 (8 cells cov >= 0.90): " + "; ".join(f"{x['cell']} {x['cov']:.3f}{'' if x['ok'] else ' FAIL'}" for x in c1)
                 + f" -> {'PASS' if R['C1']['pass'] else 'FAIL'} ({sum(x['ok'] for x in c1)}/8)")
        L.append(f"- C2 (IS none <= 1.35 x v4): " + "; ".join(f"T{x['T']} {x['ratio']:.3f}" for x in c2) + f" -> {'PASS' if R['C2']['pass'] else 'FAIL'}")
        L.append(f"- C3 (GES): " + "; ".join(f"T{x['T']} cov {x['cov']:.3f}, ratio {x['ratio']:.3f}" for x in c3) + f" -> {'PASS' if R['C3']['pass'] else 'FAIL'}")
        L.append(f"- C4 (T40 missing vs pselect_union, CI lower bound <= 0): " + "; ".join(
            f"{x['cell']} {x['est']:+.2f} [{x['lo']:+.2f}, {x['hi']:+.2f}], one-sided p(worse) {x['p_worse']:.4f}" for x in c4)
                 + f" -> {'PASS' if R['C4']['pass'] else 'FAIL'}; strict point-estimate reading: {sum(x['ok_point'] for x in c4)}/2")
        L.append(f"- Multiplicity: coverage cells (C1 + C3) with H0 'cov <= 0.90' rejected after Holm (alpha 0.05): "
                 f"{R['holm_cov_rejected']}/{R['holm_cov_n']}; C4 cells where 'not worse' is rejected after Holm: {R['holm_c4_worse_rejected']}/2")
        L.append(f"- **VERDICT: {'RETAINED' if R['retained'] else 'REJECTED'}**")
    (OUT / "rule_check.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (OUT / "rule_check.json").write_text(json.dumps(J, indent=1), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
