"""Independent skeptic recomputation of r4lfdropen claims (does not import their analyzer).

Writes results/ext_verify4_lfdropen/recompute.json.
"""
import json
import math
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "results"
REF, CAND = "tolerant_v5_1", "tolerant_v5_1_lfdr"


def load(n):
    return [json.loads(x) for x in open(RES / n / "runs.jsonl")]


def k(r):
    return (r.get("scenario", "clean"), r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])


def eq(a, b, ignore):
    diff = []
    for key in set(a) | set(b):
        if key in ignore:
            continue
        v, w = a.get(key, "<absent>"), b.get(key, "<absent>")
        if isinstance(v, float) and isinstance(w, float) and math.isnan(v) and math.isnan(w):
            continue
        if v != w:
            diff.append(key)
    return diff


def ident(ra, ma, rb, mb, sel, ignore=("method",)):
    A = {k(r): r for r in ra if r["method"] == ma and sel(r)}
    Bm = {k(r): r for r in rb if r["method"] == mb and sel(r)}
    com = set(A) & set(Bm)
    keys = Counter()
    same = 0
    for c in com:
        d = eq(A[c], Bm[c], set(ignore))
        if not d:
            same += 1
        for x in d:
            keys[x] += 1
    return {"n_a": len(A), "n_b": len(Bm), "common": len(com), "identical": same, "diff_keys": dict(keys)}


def cellstats(rows, m, sc, T, kind, rate):
    g = [r for r in rows if r["method"] == m and r.get("scenario", "clean") == sc and r["T"] == T and r["kind"] == kind and r["rate"] == rate]
    ok = [r for r in g if r["status"] == "ok"]
    return {"n": len(ok), "of": len(g),
            "cov": sum(r["n_covered_nonnull"] for r in ok) / max(1, sum(r["n_nonnull"] for r in ok)),
            "IS": float(np.mean([r["iscore_nonnull_mean"] for r in ok])) if ok else None,
            "width_med": float(np.median([r["width_kept"] for r in ok])) if ok else None,
            "abs_err_med": float(np.median([r["C_abs_err_nonnull"] for r in ok])) if ok else None,
            "cT": sorted({r.get("info_c_T") for r in ok if r.get("info_c_T") is not None})}


def pair_boot(rows, sc, T, kind, rate, B=20000, seed=20261104):
    idx = {(k(r), r["method"]): r for r in rows if r["status"] == "ok"}
    d = defaultdict(list)
    for (kk, m), r in idx.items():
        if m == CAND and kk[0] == sc and kk[3] == T and kk[4] == kind and kk[5] == rate and (kk, REF) in idx:
            d[kk[1]].append(r["iscore_nonnull_mean"] - idx[(kk, REF)]["iscore_nonnull_mean"])
    topos = sorted(d)
    s = np.array([sum(d[t]) for t in topos]); c = np.array([len(d[t]) for t in topos])
    rng = np.random.default_rng(seed)
    pk = rng.integers(0, len(topos), size=(B, len(topos)))
    bs = s[pk].sum(1) / c[pk].sum(1)
    est = s.sum() / c.sum()
    pl = (1 + (bs >= 0).sum()) / (B + 1); pg = (1 + (bs <= 0).sum()) / (B + 1)
    # also an independent check with a different seed and a paired t-test on topology means
    rng2 = np.random.default_rng(7)
    pk2 = rng2.integers(0, len(topos), size=(B, len(topos)))
    bs2 = s[pk2].sum(1) / c[pk2].sum(1)
    tm = s / c
    tstat = tm.mean() / (tm.std(ddof=1) / math.sqrt(len(tm)))
    return {"est": float(est), "lo": float(np.quantile(bs, .025)), "hi": float(np.quantile(bs, .975)),
            "p2": float(min(1, 2 * min(pl, pg))), "n_pairs": int(c.sum()), "n_topo": len(topos),
            "lo_seed7": float(np.quantile(bs2, .025)), "hi_seed7": float(np.quantile(bs2, .975)),
            "t_topo_means": float(tstat)}


def holm(ps, a=0.05):
    o = np.argsort(ps); rej = [False] * len(ps)
    for rank, i in enumerate(o):
        if ps[i] <= a / (len(ps) - rank):
            rej[i] = True
        else:
            break
    return rej


def fam(rows, sc, cells):
    out = []
    for T, kind, rate in cells:
        out.append({"sc": sc, "T": T, "kind": kind, "rate": rate, "cand": cellstats(rows, CAND, sc, T, kind, rate),
                    "ref": cellstats(rows, REF, sc, T, kind, rate), "pair": pair_boot(rows, sc, T, kind, rate)})
    rj = holm([c["pair"]["p2"] for c in out])
    for c, r in zip(out, rj):
        c["holm"] = bool(r)
        c["holm_worse"] = bool(r and c["pair"]["est"] > 0)
        c["holm_better"] = bool(r and c["pair"]["est"] < 0)
    return out


def main():
    O = {}
    ev = load("ext_r4lfdropen_eval"); lat = load("ext_r4lfdropen_latent")
    O["V1_eval"] = ident(ev, CAND, ev, REF, lambda r: r["kind"] != "missing")
    O["V1_eval_ignore_crn"] = ident(ev, CAND, ev, REF, lambda r: r["kind"] != "missing", ("method", "info_lfdr_crn"))
    O["V1_latent_ignore_crn"] = ident(lat, CAND, lat, REF, lambda r: r["kind"] != "missing", ("method", "info_lfdr_crn"))
    st = load("ext_v51_eval")
    O["V2"] = ident(ev, REF, st, REF, lambda r: True)
    O["V3"] = []
    for nm, Ts in (("ext_v51_a1", (80, 150)), ("ext_v51_a1t40", (40,))):
        s = load(nm)
        O["V3"].append({nm: ident(lat, REF, s, REF, lambda r, Ts=Ts: r.get("scenario") == "latent1" and r["T"] in Ts and r["kind"] in ("none", "missing"))})
    # missing-cell diffs: which keys differ (sanity: candidate actually differs there)
    O["missing_cells_diff"] = ident(ev, CAND, ev, REF, lambda r: r["kind"] == "missing", ("method", "info_lfdr_crn"))["identical"]
    prim = fam(ev, "clean", [(T, "missing", r) for T in (40, 80, 150) for r in (0.2, 0.5)])
    O["primary"] = prim
    O["primary_counts"] = {"win_holm": sum(c["holm_better"] and c["cand"]["cov"] >= .9 for c in prim),
                           "loss_holm": sum(c["holm_worse"] for c in prim),
                           "raw_ci_better": sum(c["pair"]["hi"] < 0 for c in prim),
                           "raw_ci_worse": sum(c["pair"]["lo"] > 0 for c in prim),
                           "cov_all_ge_090": all(c["cand"]["cov"] >= .9 for c in prim),
                           "fails": [c["cand"]["of"] - c["cand"]["n"] for c in prim]}
    nh = fam(lat, "latent1", [(T, "missing", 0.2) for T in (40, 80, 150)])
    for c in nh:
        c["ratio"] = c["cand"]["IS"] / c["ref"]["IS"]
        c["pass"] = ((c["ref"]["cov"] < .9 or c["cand"]["cov"] >= .9) and c["ratio"] <= 1.05 and not c["holm_worse"]
                     and c["cand"]["of"] - c["cand"]["n"] <= 3)
    O["noharm"] = nh
    O["noharm_counts"] = {"pass": sum(c["pass"] for c in nh), "worse_holm": sum(c["holm_worse"] for c in nh)}
    # open counts and floor share
    oc = {}
    for T in (40, 80, 150):
        for rate in (0.2, 0.5):
            g = {m: [r for r in ev if r["method"] == m and r["T"] == T and r["kind"] == "missing" and r["rate"] == rate and r["status"] == "ok"] for m in (REF, CAND)}
            cand = g[CAND]
            floor_share = float(np.mean([r["info_n_open"] == r["info_lfdr_k_floor"] for r in cand]))
            oc[f"{T}|{rate}"] = {"v51_data": float(np.mean([r["info_n_open"] for r in g[REF]])),
                                 "lfdr_data": float(np.mean([r["info_n_open"] for r in cand])),
                                 "v51_draw": float(np.mean([r["info_n_open_boot_mean"] for r in g[REF]])),
                                 "lfdr_draw": float(np.mean([r["info_n_open_boot_mean"] for r in cand])),
                                 "lfdr_floor_share": floor_share,
                                 "lfdr_mean_k": float(np.mean([r["info_lfdr_k_floor"] for r in cand])),
                                 "lfdr_mean_m": float(np.mean([r["info_lfdr_m"] for r in cand]))}
    O["open_counts"] = oc
    # recall of truly missing pairs (candidate data fit), v5_1 data fit recomputed from logged p's
    logs = {}
    for line in open(RES / "ext_r4lfdropen_eval" / "skeletons.jsonl"):
        s = json.loads(line)
        if s["kind"] == "missing":
            logs[(s["topology"], s["replicate"], s["rate"])] = {"%d-%d" % tuple(sorted(e["pair"])) for e in s["log"]}
    rec = defaultdict(lambda: defaultdict(list))
    for r in ev:
        if r["method"] != CAND or r["kind"] != "missing" or r["status"] != "ok":
            continue
        tr = logs[(r["topology"], r["replicate"], r["rate"])]
        p = r["info_lfdr_p_data"]
        kk = int(r["info_lfdr_k_floor"])
        order = sorted(p, key=lambda x: p[x])  # stable on ties may differ from screen order
        n_sig = sum(1 for v in p.values() if v < 0.10)
        K = min(len(p), max(int(math.ceil(3 * kk)), n_sig))
        v51_open = set(order[:K]); topk = set(order[:kk])
        g = rec[f"{r['T']}|{r['rate']}"]
        g["lfdr_data"].append(len(tr & set(r["info_lfdr_open_data"])) / len(tr))
        g["lfdr_draw"].append(np.mean([r["info_lfdr_open_freq"].get(t, 0.0) for t in tr]))
        g["v51_data_from_logged_p"].append(len(tr & v51_open) / len(tr))
        g["topk_recall"].append(len(tr & topk) / len(tr))
        g["v51_K_from_p"].append(K)
        g["true_in_offskel"].append(len(tr & set(p)) / len(tr))
    O["recall"] = {kk: {a: float(np.mean(b)) for a, b in v.items()} for kk, v in sorted(rec.items())}
    # v5_1 logged n_open vs K recomputed from candidate's logged p (same data => same screen)
    chk = []
    vrows = {k(r): r for r in ev if r["method"] == REF and r["kind"] == "missing"}
    for r in ev:
        if r["method"] == CAND and r["kind"] == "missing":
            p = r["info_lfdr_p_data"]; kk = int(r["info_lfdr_k_floor"])
            K = min(len(p), max(int(math.ceil(3 * kk)), sum(1 for v in p.values() if v < .1)))
            chk.append(K == vrows[k(r)]["info_n_open"])
    O["v51_n_open_matches_K_from_logged_p"] = [int(sum(chk)), len(chk)]
    # width ratio before / after calibration: raw = width / (c_T*0.5)? width already prescaled*c_T
    wr = {}
    for T in (40, 80, 150):
        for rate in (0.2, 0.5):
            a = cellstats(ev, CAND, "clean", T, "missing", rate); b = cellstats(ev, REF, "clean", T, "missing", rate)
            ca, cb = a["cT"][0], b["cT"][0]
            wr[f"{T}|{rate}"] = {"after": a["width_med"] / b["width_med"],
                                 "before_approx": (a["width_med"] / ca) / (b["width_med"] / cb),
                                 "abs_err_med": [a["abs_err_med"], b["abs_err_med"]], "cT": [ca, cb]}
    O["width_ratio"] = wr
    # secondary families
    sec = {}
    tot_w = tot_b = tot_n = 0
    for nm in ("ext_r4lfdropen_scen", "ext_r4lfdropen_lag1", "ext_r4lfdropen_lag4"):
        rows = load(nm)
        cfg = json.loads((RES / nm / "manifest.json").read_text())
        scs = [s["name"] for s in cfg["config"].get("scenarios") or [{"name": "clean"}]]
        sec[nm] = {"seconds": cfg["seconds"], "n_rows": cfg["n_rows"], "fams": {}}
        for sc in scs:
            f = fam(rows, sc, [(T, "missing", r) for T in cfg["config"]["T"] for r in cfg["config"]["damage"]["rates"]])
            sec[nm]["fams"][sc] = [{"T": c["T"], "rate": c["rate"], "est": c["pair"]["est"], "ci": [c["pair"]["lo"], c["pair"]["hi"]],
                                    "p2": c["pair"]["p2"], "worse": c["holm_worse"], "better": c["holm_better"],
                                    "cov": [c["cand"]["cov"], c["ref"]["cov"]], "fail": [c["cand"]["of"] - c["cand"]["n"], c["ref"]["of"] - c["ref"]["n"]]} for c in f]
            tot_w += sum(c["holm_worse"] for c in f); tot_b += sum(c["holm_better"] for c in f); tot_n += len(f)
    sec["totals"] = {"worse": tot_w, "better": tot_b, "cells": tot_n}
    O["secondary"] = sec
    O["runtimes"] = {nm: json.loads((RES / nm / "manifest.json").read_text())["seconds"] for nm in ("ext_r4lfdropen_eval", "ext_r4lfdropen_latent")}
    (RES / "ext_verify4_lfdropen").mkdir(exist_ok=True)
    (RES / "ext_verify4_lfdropen" / "recompute.json").write_text(json.dumps(O, indent=1, default=float))
    print(json.dumps({k_: O[k_] for k_ in ("V1_eval", "V1_eval_ignore_crn", "V1_latent_ignore_crn", "V2", "V3", "missing_cells_diff", "primary_counts", "noharm_counts", "open_counts", "recall", "v51_n_open_matches_K_from_logged_p", "width_ratio", "runtimes")}, indent=1, default=float))
    for c in prim + nh:
        print(c["sc"], c["T"], c["rate"], round(c["cand"]["cov"], 3), round(c["ref"]["cov"], 3), round(c["cand"]["IS"], 3), round(c["ref"]["IS"], 3),
              {a: round(b, 4) for a, b in c["pair"].items()}, c["holm"], c.get("ratio"))
    print(json.dumps(sec["totals"]))
    for nm in sec:
        if nm != "totals":
            print(nm, sec[nm]["seconds"], {sc: [(x["T"], x["rate"], round(x["est"], 3), round(x["p2"], 4), x["worse"], x["better"]) for x in v] for sc, v in sec[nm]["fams"].items()})


if __name__ == "__main__":
    main()
