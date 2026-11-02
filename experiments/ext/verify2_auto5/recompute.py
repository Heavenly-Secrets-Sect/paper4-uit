"""Verifier (auto5, round 2): independent recomputation from runs.jsonl (own code, bootstrap seed 12345).
Writes results/ext_verify2_auto5/recompute.json"""
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
R = ROOT / "results"
def load(n): return [json.loads(l) for l in open(R / n / "runs.jsonl")]
rng0 = 12345
def cov(rows): return sum(r["n_covered_nonnull"] for r in rows) / sum(r["n_nonnull"] for r in rows)
def covp(rows, thr=0.9, B=4000):
    by = defaultdict(lambda: [0, 0])
    for r in rows: by[r["topology"]][0] += r["n_covered_nonnull"]; by[r["topology"]][1] += r["n_nonnull"]
    a = np.array([v[0] for v in by.values()], float); b = np.array([v[1] for v in by.values()], float)
    pk = np.random.default_rng(rng0).integers(0, len(a), (B, len(a)))
    return float(np.mean(a[pk].sum(1) / b[pk].sum(1) <= thr))
def paired(rows_m, rows_r, B=4000):
    km = {(r["topology"], r["replicate"]): r["iscore_nonnull_mean"] for r in rows_m}
    d = defaultdict(list)
    for r in rows_r:
        k = (r["topology"], r["replicate"])
        if k in km: d[r["topology"]].append(km[k] - r["iscore_nonnull_mean"])
    t = list(d); s = np.array([sum(d[x]) for x in t]); c = np.array([len(d[x]) for x in t])
    pk = np.random.default_rng(rng0).integers(0, len(t), (B, len(t)))
    bs = s[pk].sum(1) / c[pk].sum(1)
    return {"est": float(s.sum() / c.sum()), "lo": float(np.quantile(bs, .025)), "hi": float(np.quantile(bs, .975)),
            "p2": float(min(1, 2 * min(np.mean(bs <= 0), np.mean(bs >= 0)))), "p_le0": float(np.mean(bs <= 0)), "n": int(c.sum())}
def holm(ps, a=.05):
    o = np.argsort(ps); rej = [False] * len(ps)
    for k, i in enumerate(o):
        if ps[i] <= a / (len(ps) - k): rej[i] = True
        else: break
    return rej
def grp(rows, scen=None):
    g = defaultdict(list)
    for r in rows:
        if r["status"] != "ok": continue
        g[(r.get("scenario", "clean"), r["T"], r["kind"], r["rate"], r["method"])].append(r)
    return g
out = {}
# ---- a1
g = grp(load("ext_auto5_a1"))
cells = [("latent1", T, k, 0.2) for T in (80, 150) for k in ("missing", "reversed")]
a1 = {f"{c}": {"cov": cov(g[c + ("tolerant_auto3",)]), "p": covp(g[c + ("tolerant_auto3",)])} for c in cells}
out["a1_latent1"] = a1; out["a1_holm"] = sum(holm([v["p"] for v in a1.values()]))
op = {}
for sc in ("clean", "latent1", "latent3", "noise0.1"):
    for T in (80, 150):
        rs = g[(sc, T, "none", 0.0, "tolerant_auto3")]
        op[f"{sc}|{T}"] = float(np.mean([r.get("info_state") == "open" for r in rs]))
out["a1_gate_open_none"] = op
a1cells = {}
for sc in ("latent3", "noise0.1"):
    for m in ("tolerant_auto3", "tolerant_v4"):
        a1cells[f"{sc}|{m}"] = {f"{T}|{k}": round(cov(g[(sc, T, k, r, m)]), 3) for T in (80, 150) for k, r in (("none", 0.0), ("missing", .2), ("reversed", .2))}
out["a1_cells"] = a1cells
# ---- main
main = load("ext_auto5_main"); gm = grp(main)
gate = [r for r in load("ext_gate_auto3") if r["method"] == "tolerant_auto3"]; ga = grp(gate)
M = "tolerant_auto5"
C1 = {f"{T}|{k}|{r}": cov(gm[("clean", T, k, r, M)]) for T in (80, 150) for k in ("missing", "reversed") for r in (.2, .5)}
C3 = {f"{T}|ges": cov(gm[("clean", T, "ges", 0.0, M)]) for T in (80, 150)}
isv = lambda rows: float(np.mean([r["iscore_nonnull_mean"] for r in rows]))
C2 = {T: isv(gm[("clean", T, "none", 0.0, M)]) / isv(gm[("clean", T, "none", 0.0, "tolerant_v4")]) for T in (40, 80, 150)}
C3r = {T: isv(gm[("clean", T, "ges", 0.0, M)]) / isv(gm[("clean", T, "ges", 0.0, "tolerant_v4")]) for T in (80, 150)}
C4 = {f"40|missing|{r}": paired(gm[("clean", 40, "missing", r, M)], gm[("clean", 40, "missing", r, "pselect_union")]) for r in (.2, .5)}
ps = [covp(gm[("clean", T, k, r, M)]) for T in (80, 150) for k in ("missing", "reversed") for r in (.2, .5)] + \
     [covp(gm[("clean", T, "ges", 0.0, M)]) for T in (80, 150)]
out["main"] = {"C1": C1, "C2": C2, "C3_cov": C3, "C3_ratio": C3r, "C4": C4, "holm_cov_10": sum(holm(ps)), "cov_p": ps,
               "C4_holm_worse": sum(holm([v["p_le0"] for v in C4.values()]))}
# auto5 - auto3, 24 cells
allc = [(T, k, r) for T in (40, 80, 150) for k, r in (("none", 0.0), ("extra", .2), ("extra", .5), ("missing", .2), ("missing", .5), ("reversed", .2), ("reversed", .5), ("ges", 0.0))]
d53 = {f"{T}|{k}|{r}": paired(gm[("clean", T, k, r, M)], ga[("clean", T, k, r, "tolerant_auto3")]) for T, k, r in allc}
out["auto5_minus_auto3"] = {"lower_point": sum(v["est"] < 0 for v in d53.values()), "ci_below0": sum(v["hi"] < 0 for v in d53.values()),
                            "ci_above0": sum(v["lo"] > 0 for v in d53.values()),
                            "holm_sig_neg": sum(h and v["est"] < 0 for h, v in zip(holm([v["p2"] for v in d53.values()]), d53.values())),
                            "cells": d53}
dsm = {f"{T}|{k}|{r}": paired(gm[("clean", T, k, r, "tolerant_auto5_small")], gm[("clean", T, k, r, M)]) for T, k, r in allc if T > 40}
out["small_minus_auto5_T80_150"] = {"cells": dsm, "ci_above0": sum(v["lo"] > 0 for v in dsm.values()),
                                    "holm_sig_pos": sum(h and v["est"] > 0 for h, v in zip(holm([v["p2"] for v in dsm.values()]), dsm.values()))}
gop = {f"{T}|{k}|{r}": float(np.mean([x.get("info_state") == "open" for x in gm[("clean", T, k, r, M)]])) for T, k, r in allc}
out["auto5_gate_open"] = gop
# ---- fair
fr = load("ext_auto5_fair"); gf = grp(fr)
claim = [(T, k, r) for T in (80, 150) for k in ("missing", "reversed") for r in (.2, .5)]
fair = {}
for X in ("plugin", "ida_union", "bvar_minnesota", "pselect_union"):
    for suf in ("_calT", "_calT1"):
        res = {}
        allc7 = [(T, k, r) for T in (40, 80, 150) for k, r in (("none", 0.0), ("extra", .2), ("extra", .5), ("missing", .2), ("missing", .5), ("reversed", .2), ("reversed", .5))]
        for T, k, r in allc7:
            a = ga[("clean", T, k, r, "tolerant_auto3")]
            d = paired(a, gf[("clean", T, k, r, X + suf)])
            w = "W" if cov(a) >= .9 and d["hi"] < 0 else ("L" if d["lo"] > 0 else "T")
            res[f"{T}|{k}|{r}"] = (w, d)
        pc = [res[f"{T}|{k}|{r}"] for T, k, r in claim]
        fair[X + suf] = {"W": sum(v[0] == "W" for v in res.values()), "T": sum(v[0] == "T" for v in res.values()),
                         "L": sum(v[0] == "L" for v in res.values()), "claim_W": sum(v[0] == "W" for v in pc),
                         "holm8_W": sum(h and v[1]["est"] < 0 for h, v in zip(holm([v[1]["p2"] for v in pc]), pc)),
                         "holm21_W": sum(h and v[1]["est"] < 0 for h, v in zip(holm([v[1]["p2"] for v in res.values()]), res.values())),
                         "not_won_claim": {f"{T}|{k}|{r}": res[f"{T}|{k}|{r}"][1] for T, k, r in claim if res[f"{T}|{k}|{r}"][0] != "W"}}
out["fair"] = fair
none = {}
for T in (40, 80, 150):
    a = ga[("clean", T, "none", 0.0, "tolerant_auto3")]
    for X in ("ida_union_raw", "plugin_raw", "ida_union_calT", "plugin_calT"):
        none[f"{T}|{X}"] = paired(a, gf[("clean", T, "none", 0.0, X)])
    for X in ("plugin_raw", "ida_union_raw", "plugin_calT", "ida_union_calT"):
        none[f"{T}|cov|{X}"] = cov(gf[("clean", T, "none", 0.0, X)])
out["fair_none"] = none
# auto3 old seed vs new seed (a1 clean rows)
ga1 = grp(load("ext_auto5_a1"))
out["auto3_seed_check"] = {f"{T}|{k}": (cov(ga[("clean", T, k, r, "tolerant_auto3")]), cov(ga1[("clean", T, k, r, "tolerant_auto3")]),
                                        isv(ga[("clean", T, k, r, "tolerant_auto3")]), isv(ga1[("clean", T, k, r, "tolerant_auto3")]))
                           for T in (80, 150) for k, r in (("none", 0.0), ("missing", .2), ("reversed", .2))}
(R / "ext_verify2_auto5/recompute.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps({k: v for k, v in out.items() if k not in ("auto5_minus_auto3", "small_minus_auto5_T80_150")}, indent=1, default=str)[:9000])
print({k: v for k, v in out["auto5_minus_auto3"].items() if k != "cells"})
print({k: v for k, v in out["small_minus_auto5_T80_150"].items() if k != "cells"})
for k, v in out["small_minus_auto5_T80_150"]["cells"].items(): print(k, round(v["est"], 3), round(v["lo"], 3), round(v["hi"], 3))
