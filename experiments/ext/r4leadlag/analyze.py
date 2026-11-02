"""Pre-registered analysis of the r4leadlag evaluation (rule: docs/ext/r4leadlag.md, section 3).

Inputs: results/ext_r4leadlag_eval_{clean,latent,noise}/runs.jsonl (this round) and, for the pairing check,
results/ext_v51_eval, results/ext_v51_a1, results/ext_v51_a1t40 (stored tolerant_v5_1 rows).
Output: results/ext_r4leadlag_rule/{ruling.md, ruling.json}.

Run: python experiments/ext/r4leadlag/analyze.py
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "results"
OUT = RES / "ext_r4leadlag_rule"
REF = "tolerant_v5_1"
VARIANTS = {"A": "tolerant_v5_1_leadlag", "D": "tolerant_v5_1_leadlag_skel"}
RUNS = ["ext_r4leadlag_eval_clean", "ext_r4leadlag_eval_latent", "ext_r4leadlag_eval_noise"]
B_MAIN, SEED_MAIN = 20_000, 20261104
B_AUC = 2_000
PRIMARY = [(sc, T, r) for sc in ("latent1", "latent3") for r in (0.2, 0.5) for T in (80, 150)]
NOHARM = ([("clean", T, r) for T in (40, 80, 150) for r in (0.2, 0.5)]
          + [(sc, 40, r) for sc in ("latent1", "latent3") for r in (0.2, 0.5)])
NOISE = [("noise0.1", T, 0.2) for T in (80, 150)]
NEG = ("E0", "EL")   # true missing edges (contemporaneous or lagged)


def load(name):
    p = RES / name / "runs.jsonl"
    return [json.loads(l) for l in open(p)] if p.exists() else []


def key(r):
    return (r.get("scenario", "clean"), r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])


def holm(p, alpha=0.05):
    order = np.argsort(p)
    rej = [False] * len(p)
    for rank, i in enumerate(order):
        if p[i] <= alpha / (len(p) - rank):
            rej[i] = True
        else:
            break
    return rej


def same_row(x, y):
    if x["status"] != y["status"]:
        return False
    if x["status"] != "ok":
        return True
    return (abs(x["iscore_nonnull_mean"] - y["iscore_nonnull_mean"]) < 1e-12
            and x["n_covered_nonnull"] == y["n_covered_nonnull"] and x["n_nonnull"] == y["n_nonnull"])


def by_method(rows):
    d = defaultdict(dict)
    for r in rows:
        d[r["method"]][key(r)] = r
    return d


def cell_keys(D, sc, T, kind, rate):
    return sorted(k for k in D[REF] if k[0] == sc and k[3] == T and k[4] == kind and k[5] == rate)


def coverage_itt(D, m, keys):
    """Pooled non-null coverage; a failed run counts its non-null pairs (from any ok row of the key) as uncovered."""
    cov = tot = fail = 0
    for k in keys:
        r = D[m].get(k)
        nn = next((D[x][k]["n_nonnull"] for x in D if k in D[x] and D[x][k]["status"] == "ok"), 0)
        if r is None or r["status"] != "ok":
            fail += 1
            tot += nn
            continue
        cov += r["n_covered_nonnull"]
        tot += r["n_nonnull"]
    return (cov / tot if tot else float("nan")), fail


def paired(D, m, keys, B=B_MAIN, seed=SEED_MAIN):
    d = defaultdict(list)
    for k in keys:
        a, b = D[m].get(k), D[REF].get(k)
        if a and b and a["status"] == "ok" and b["status"] == "ok":
            d[k[1]].append(a["iscore_nonnull_mean"] - b["iscore_nonnull_mean"])
    topos = list(d)
    sums = np.array([np.sum(d[t]) for t in topos])
    cnts = np.array([len(d[t]) for t in topos])
    est = float(sums.sum() / cnts.sum())
    rng = np.random.default_rng(seed)
    pick = rng.integers(0, len(topos), size=(B, len(topos)))
    boot = sums[pick].sum(1) / cnts[pick].sum(1)
    lo, hi = np.quantile(boot, (0.025, 0.975))
    p_less = (1 + int((boot >= 0).sum())) / (B + 1)
    p_greater = (1 + int((boot <= 0).sum())) / (B + 1)
    is_m = float(np.mean([D[m][k]["iscore_nonnull_mean"] for k in keys if D[m].get(k) and D[m][k]["status"] == "ok"
                          and D[REF].get(k) and D[REF][k]["status"] == "ok"]))
    is_r = float(np.mean([D[REF][k]["iscore_nonnull_mean"] for k in keys if D[m].get(k) and D[m][k]["status"] == "ok"
                          and D[REF][k]["status"] == "ok"]))
    return {"est": est, "lo": float(lo), "hi": float(hi), "p_less": p_less, "p_greater": p_greater,
            "p_two": min(1.0, 2 * min(p_less, p_greater)), "n": int(cnts.sum()), "IS_m": is_m, "IS_ref": is_r,
            "ratio": is_m / is_r}


def auroc(pos, neg):
    if not pos or not neg:
        return None
    pos, neg = np.asarray(pos), np.asarray(neg)
    return float((pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean())


def auroc_cluster(items, B=B_AUC, seed=SEED_MAIN):
    """items: list of (topology, label 1/0, score). AUROC with topology-cluster bootstrap 95% CI."""
    pos = [s for _, y, s in items if y == 1]
    neg = [s for _, y, s in items if y == 0]
    est = auroc(pos, neg)
    if est is None or len(pos) < 10 or len(neg) < 10:
        return {"auroc": est, "lo": None, "hi": None, "n_pos": len(pos), "n_neg": len(neg), "estimable": False}
    by = defaultdict(list)
    for t, y, s in items:
        by[t].append((y, s))
    topos = list(by)
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(B):
        pk = rng.integers(0, len(topos), len(topos))
        p_ = [s for i in pk for y, s in by[topos[i]] if y == 1]
        n_ = [s for i in pk for y, s in by[topos[i]] if y == 0]
        a = auroc(p_, n_)
        if a is not None:
            bs.append(a)
    lo, hi = np.quantile(bs, (0.025, 0.975))
    return {"auroc": est, "lo": float(lo), "hi": float(hi), "n_pos": len(pos), "n_neg": len(neg), "estimable": True}


def gate_items(D, m, sc_list, T, rates, source="gate_p", neg=NEG):
    """(topology, 1 for co-child C / 0 for true missing edge, score = -p_Q) on the data-level gate log."""
    items = []
    for k, r in D[m].items():
        if k[0] not in sc_list or k[3] != T or k[4] != "missing" or k[5] not in rates or r["status"] != "ok":
            continue
        logs = r.get(f"info_{source}") or []
        cls = r.get(f"cls_{source}") or []
        for entry, c in zip(logs, cls):
            pq = entry[3] if source == "gate_p" else entry[4]
            if c == "C":
                items.append((k[1], 1, -pq))
            elif c in neg:
                items.append((k[1], 0, -pq))
    return items


def confusion(D, m, sc_list, Ts, rates):
    tab = defaultdict(lambda: [0, 0])   # class -> [labelled, examined]
    draws = []
    for k, r in D[m].items():
        if k[0] not in sc_list or k[3] not in Ts or k[4] != "missing" or k[5] not in rates or r["status"] != "ok":
            continue
        for (u, v, p0, pq), c in zip(r.get("info_gate_p") or [], r.get("cls_gate_p") or []):
            tab[c][1] += 1
            tab[c][0] += int(pq < 0.05)
        draws.append((r.get("info_gate_draw_labelled_mean") or 0.0, r.get("info_gate_draw_any_label_share") or 0.0,
                      r.get("info_gate_draw_repaired_mean") or 0.0))
    dr = np.array(draws) if draws else np.zeros((0, 3))
    return {"by_class": {c: {"labelled": a, "examined": b, "rate": a / b if b else None} for c, (a, b) in sorted(tab.items())},
            "draw_labelled_mean": float(dr[:, 0].mean()) if len(dr) else None,
            "draw_any_label_share": float(dr[:, 1].mean()) if len(dr) else None,
            "draw_repaired_mean": float(dr[:, 2].mean()) if len(dr) else None}


def cochild(D, m, keys):
    n = c = 0
    s = 0.0
    nn = cn = 0
    for k in keys:
        r = D[m].get(k)
        if not r or r["status"] != "ok" or "cc_n" not in r:
            continue
        n += r["cc_n"]; c += r["cc_n_cov"]; s += r["cc_is_sum"]
        nn += r["cc_n_nonnull"]; cn += r["cc_n_cov_nonnull"]
    return {"cov_all": c / n if n else None, "IS_all": s / n if n else None,
            "cov_nonnull": cn / nn if nn else None, "n_pairs": n, "n_nonnull": nn}


def main():
    rows = {name: load(name) for name in RUNS}
    allrows = [r for v in rows.values() for r in v]
    D = by_method(allrows)
    out = {"validity": {}, "pairing": {}, "cells": {}, "rule": {}, "auroc": {}, "confusion": {}, "cochild": {}}
    L = ["# r4leadlag: ruling (generated by experiments/ext/r4leadlag/analyze.py)", ""]

    # V1: identical to v5_1 where no missing edge is stated
    for tag, m in VARIANTS.items():
        same = tot = 0
        for k, r in D[REF].items():
            if k[4] == "missing":
                continue
            tot += 1
            same += int(k in D[m] and same_row(D[m][k], r))
        out["validity"][tag] = {"identical": same, "of": tot, "pass": same == tot and tot > 0}
        L.append(f"- V1 {tag} ({m}): rows identical to {REF} in cells without stated missing edges: {same}/{tot} -> "
                 f"{'PASS' if same == tot and tot > 0 else 'FAIL'}")

    # Pairing with stored v5_1 rows
    stored = {"ext_v51_eval": ("clean",), "ext_v51_a1": ("latent1", "latent3", "noise0.1"),
              "ext_v51_a1t40": ("latent1", "latent3", "noise0.1")}
    for run, scs in stored.items():
        st = {key(r): r for r in load(run) if r["method"] == REF}
        common = [k for k in st if k in D[REF] and k[0] in scs]
        ident = sum(same_row(D[REF][k], st[k]) for k in common)
        out["pairing"][run] = {"common": len(common), "identical": ident}
        L.append(f"- Pairing: {REF} rows identical to stored {run}: {ident}/{len(common)} shared keys")
    L.append("")

    # Cells
    def stats(sc, T, rate, m):
        keys = cell_keys(D, sc, T, "missing", rate)
        cov, fail = coverage_itt(D, m, keys)
        return keys, cov, fail

    for tag, m in VARIANTS.items():
        res = {}
        for sc, T, rate in PRIMARY + NOHARM + NOISE:
            keys, cov, fail = stats(sc, T, rate, m)
            cov_ref, fail_ref = coverage_itt(D, REF, keys)
            p = paired(D, m, keys)
            res[f"{sc}|{T}|{rate}"] = {"cov": cov, "fail": fail, "cov_ref": cov_ref, "fail_ref": fail_ref, **p,
                                       "n_keys": len(keys)}
        out["cells"][tag] = res
        prim = [res[f"{sc}|{T}|{r}"] for sc, T, r in PRIMARY]
        hp = holm([c["p_two"] for c in prim])
        wins = [bool(h and c["est"] < 0 and c["cov"] >= 0.90) for h, c in zip(hp, prim)]
        cov_ok = all(c["cov"] >= 0.90 for c in prim)
        nh = [res[f"{sc}|{T}|{r}"] for sc, T, r in NOHARM]
        hn = holm([c["p_two"] for c in nh])
        harm = []
        for (sc, T, r), c, h in zip(NOHARM, nh, hn):
            bad = []
            if c["ratio"] > 1.05:
                bad.append(f"ratio {c['ratio']:.3f}")
            if h and c["est"] > 0:
                bad.append("Holm-significant worsening")
            if c["cov_ref"] >= 0.90 and c["cov"] < 0.90:
                bad.append(f"coverage {c['cov']:.3f} < 0.90 (v5_1 {c['cov_ref']:.3f})")
            if bad:
                harm.append(f"{sc} T{T} m{r}: " + ", ".join(bad))
        retained = sum(wins) >= 2 and cov_ok and not harm and out["validity"][tag]["pass"]
        out["rule"][tag] = {"wins": sum(wins), "win_cells": [f"{sc}|{T}|{r}" for (sc, T, r), w in zip(PRIMARY, wins) if w],
                            "holm_primary_rejected": sum(hp), "coverage_all_primary_ge_0.90": cov_ok,
                            "noharm_violations": harm, "holm_noharm_rejected": sum(hn), "RETAINED": retained}

        L += [f"## Variant {tag}: `{m}`", "",
              "| scenario | T | stated | cov v5_1 | cov cand | fail cand | IS v5_1 | IS cand | ratio | dIS [95% CI] | p two-sided | Holm | role |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for group, cells_, hh, role in ((PRIMARY, prim, hp, "primary"), (NOHARM, nh, hn, "no-harm")):
            for (sc, T, r), c, h in zip(group, cells_, hh):
                L.append(f"| {sc} | {T} | missing-{r} | {c['cov_ref']:.3f} | {c['cov']:.3f} | {c['fail']} | {c['IS_ref']:.3f} | "
                         f"{c['IS_m']:.3f} | {c['ratio']:.3f} | {c['est']:+.3f} [{c['lo']:+.3f}, {c['hi']:+.3f}] | "
                         f"{c['p_two']:.4f} | {'rej' if h else '–'} | {role} |")
        for sc, T, r in NOISE:
            c = res[f"{sc}|{T}|{r}"]
            L.append(f"| {sc} | {T} | missing-{r} | {c['cov_ref']:.3f} | {c['cov']:.3f} | {c['fail']} | {c['IS_ref']:.3f} | "
                     f"{c['IS_m']:.3f} | {c['ratio']:.3f} | {c['est']:+.3f} [{c['lo']:+.3f}, {c['hi']:+.3f}] | "
                     f"{c['p_two']:.4f} | n/a | descriptive |")
        rr = out["rule"][tag]
        L += ["", f"- Wins (Holm 0.05 over 8, est < 0, coverage >= 0.90): {rr['wins']}/8 {rr['win_cells']}; "
                  f"Holm rejections over 8 (any sign): {rr['holm_primary_rejected']}",
              f"- Coverage >= 0.90 in all 8 primary cells: {rr['coverage_all_primary_ge_0.90']}",
              f"- No-harm (10 cells; Holm over 10 rejections any sign: {rr['holm_noharm_rejected']}): "
              f"{'none violated' if not rr['noharm_violations'] else '; '.join(rr['noharm_violations'])}",
              f"- **Verdict {tag}: {'RETAINED (exploratory)' if retained else 'NOT RETAINED'}**", ""]

        # gate diagnostics
        a150 = auroc_cluster(gate_items(D, m, ("latent1", "latent3"), 150, (0.2, 0.5)))
        a150_e0 = auroc_cluster(gate_items(D, m, ("latent1", "latent3"), 150, (0.2, 0.5), neg=("E0",)))
        a150_all = auroc_cluster(gate_items(D, m, ("latent1", "latent3"), 150, (0.2, 0.5), source="gate_scores"))
        a80 = auroc_cluster(gate_items(D, m, ("latent1", "latent3"), 80, (0.2, 0.5)))
        informative = bool(a150["estimable"] and a150["lo"] > 0.5)
        out["auroc"][tag] = {"T150_examined": a150, "T150_examined_E0only": a150_e0, "T150_all_nonadjacent": a150_all,
                             "T80_examined": a80, "informative": informative}

        def fa(a):
            return ("not estimable" if not a["estimable"] else f"{a['auroc']:.3f} [{a['lo']:.3f}, {a['hi']:.3f}]") + \
                f" (C {a['n_pos']}, edges {a['n_neg']})"
        L += [f"- AUROC of the label score (-p_Q), co-child C vs true missing edge (E0/EL), pairs examined by the gate on the data, "
              f"latent1+latent3, missing-0.2/0.5: T150 {fa(a150)}; T80 {fa(a80)}; T150 vs E0 only {fa(a150_e0)}; "
              f"T150 all non-adjacent pairs {fa(a150_all)}",
              f"- **Gate informative (T150 lower bound > 0.5): {'yes' if informative else 'NO -> gate not informative'}**", ""]
        conf = {}
        for lab, scs, Ts, rates in (("latent T80/150", ("latent1", "latent3"), (80, 150), (0.2, 0.5)),
                                    ("latent T40", ("latent1", "latent3"), (40,), (0.2, 0.5)),
                                    ("clean all T", ("clean",), (40, 80, 150), (0.2, 0.5)),
                                    ("noise0.1", ("noise0.1",), (80, 150), (0.2,))):
            cf = confusion(D, m, scs, Ts, rates)
            conf[lab] = cf
            parts = ", ".join(f"{c} {v['labelled']}/{v['examined']}" for c, v in cf["by_class"].items())
            L.append(f"- Labels on the data ({lab}; labelled/examined by truth class): {parts}; per draw: labelled "
                     f"{cf['draw_labelled_mean']:.2f}, draws with a label {cf['draw_any_label_share']:.2f}, repaired {cf['draw_repaired_mean']:.2f}"
                     if cf["draw_labelled_mean"] is not None else f"- Labels ({lab}): none")
        out["confusion"][tag] = conf
        L.append("")

    # Holm overlay over both variants' primary cells (16)
    allp = [out["cells"][t][f"{sc}|{T}|{r}"] for t in VARIANTS for sc, T, r in PRIMARY]
    h16 = holm([c["p_two"] for c in allp])
    w16 = sum(bool(h and c["est"] < 0 and c["cov"] >= 0.90) for h, c in zip(h16, allp))
    out["rule"]["overlay_holm16_wins"] = w16
    L.append(f"- Overlay: wins over both variants' 16 primary cells with Holm over 16: {w16}")

    # co-child pairs and oracle (descriptive)
    L += ["", "## Co-child pairs (descriptive): coverage all / non-null, mean IS per co-child pair", "",
          "| scenario | T | stated | oracle | v5_1 | A | D |", "|---|---|---|---|---|---|---|"]
    for sc in ("latent1", "latent3"):
        for T in (40, 80, 150):
            for r in (0.2, 0.5):
                keys = cell_keys(D, sc, T, "missing", r)
                cs = []
                for m in ("oracle", REF, VARIANTS["A"], VARIANTS["D"]):
                    c = cochild(D, m, keys)
                    out["cochild"][f"{sc}|{T}|{r}|{m}"] = c
                    cs.append("–" if c["cov_all"] is None else
                              f"{c['cov_all']:.3f} / {c['cov_nonnull'] if c['cov_nonnull'] is not None else float('nan'):.3f} / {c['IS_all']:.2f}")
                L.append(f"| {sc} | {T} | missing-{r} | " + " | ".join(cs) + " |")
    L += ["", "## Oracle (descriptive): coverage / IS", ""]
    for sc in ("latent1", "latent3"):
        for T in (40, 80, 150):
            for r in (0.2, 0.5):
                keys = cell_keys(D, sc, T, "missing", r)
                ok = [D["oracle"][k] for k in keys if k in D.get("oracle", {}) and D["oracle"][k]["status"] == "ok"]
                if ok:
                    cv = sum(x["n_covered_nonnull"] for x in ok) / sum(x["n_nonnull"] for x in ok)
                    L.append(f"- {sc} T{T} missing-{r}: oracle cov {cv:.3f}, IS {np.mean([x['iscore_nonnull_mean'] for x in ok]):.3f}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ruling.md").write_text("\n".join(L) + "\n")
    (OUT / "ruling.json").write_text(json.dumps(out, indent=1, default=float))
    print("\n".join(L))


if __name__ == "__main__":
    main()
