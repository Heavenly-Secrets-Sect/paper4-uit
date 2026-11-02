"""Apply the pre-registered rule of docs/ext/r4kilianbab.md (section 4) to results/ext_r4kilianbab_eval,
mechanically, and write the diagnostics the doc requires. Secondary scenarios (results/ext_r4kilianbab_a1)
are described if present.

Run: python experiments/ext/r4kilianbab/analyze.py -> results/ext_r4kilianbab_eval/{ruling.md, ruling.json}
                                                     results/ext_r4kilianbab_a1/{describe.md, describe.json}
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "results"
RUN, RUN_A1 = "ext_r4kilianbab_eval", "ext_r4kilianbab_a1"
REF = "tolerant_v5_1"
K1, KBC, K0 = "r4kilianbab_bab", "r4kilianbab_babbc", "r4kilianbab_babraw"
ARMS = [K1, KBC, K0]
TS = [40, 80, 150]
CELLS = [("none", 0.0)] + [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]
PRIMARY = [(T, k, r) for T in (40, 80) for k in ("missing", "reversed") for r in (0.2, 0.5)]
ALL = [(T, k, r) for T in TS for k, r in CELLS]
OTHER = [c for c in ALL if c not in PRIMARY]
TRIP = (80, "reversed", 0.5)
B, SEED = 20000, 20261104
OCAL = {40: "14", 80: "13", 150: "12"}


def load(name):
    return [json.loads(line) for line in open(RES / name / "runs.jsonl")]


def key(r):
    return (r.get("scenario", "clean"), r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])


def holm(p, alpha=0.05):
    order = np.argsort(p)
    m = len(p)
    rej = [False] * m
    for rank, i in enumerate(order):
        if p[i] <= alpha / (m - rank):
            rej[i] = True
        else:
            break
    return rej


def group(rows, m, T, kind, rate, sc="clean"):
    return [r for r in rows if r["method"] == m and r["T"] == T and r["kind"] == kind and r["rate"] == rate
            and r.get("scenario", "clean") == sc]


def stats(rows, m, T, kind, rate, sc="clean"):
    g = group(rows, m, T, kind, rate, sc)
    ok = [r for r in g if r["status"] == "ok"]
    if not ok:
        return {"n_ok": 0, "n": len(g)}
    out = {"n_ok": len(ok), "n": len(g),
           "cov": sum(r["n_covered_nonnull"] for r in ok) / sum(r["n_nonnull"] for r in ok),
           "IS": float(np.mean([r["iscore_nonnull_mean"] for r in ok])),
           "width": float(np.median([r["width_kept"] for r in ok if r.get("width_kept") is not None]))}
    if m == "oracle":
        tag = OCAL[T]
        out["cov_ocal"] = sum(r[f"ocal{tag}_n_covered_nonnull"] for r in ok) / sum(r["n_nonnull"] for r in ok)
        out["IS_ocal"] = float(np.mean([r[f"ocal{tag}_iscore_nonnull_mean"] for r in ok]))
    if "x_med_shrink_mid" in ok[0]:
        out["med_shrink_mid"] = float(np.median([r["x_med_shrink_mid"] for r in ok]))
        out["med_shrink_C"] = float(np.median([r["x_med_shrink_C"] for r in ok]))
        out["med_err_C"] = float(np.median([r["x_med_err_C"] for r in ok]))
        t0 = sum(r["x_n_miss_toward0"] for r in ok)
        aw = sum(r["x_n_miss_away"] for r in ok)
        out["miss_toward0"], out["miss_away"] = t0, aw
        out["share_miss_toward0"] = t0 / (t0 + aw) if t0 + aw else None
    for k in ("info_c_T", "info_bab_d", "info_bab_absbias_mean", "info_bab_absbias_lag1", "info_bab_absbias_lag2",
              "info_bab_bias_own_lag1", "info_bab_bias_own_lag2", "info_bab_absbias_cross_lag1", "info_bab_absbias_cross_lag2",
              "info_bab_share_draws_shrunk", "info_bab_share_draws_uncorrected", "info_bab_mean_d_draws",
              "info_bc_share_skipped", "info_bc_share_capped", "info_bc_mean_abs_z0", "info_bc_mean_z0"):
        v = [r[k] for r in ok if r.get(k) is not None]
        if v:
            out[k] = float(np.mean(v))
    if "info_bab_data_flag" in ok[0]:
        f = np.array([r["info_bab_data_flag"] for r in ok])
        out["share_data_shrunk"] = float(np.mean(f == 1))
        out["share_data_uncorrected"] = float(np.mean(f == 2))
    return out


def paired(rows, m, T, kind, rate, sc="clean"):
    idx = {(key(r), r["method"]): r for r in rows if r["status"] == "ok" and r.get("iscore_nonnull_mean") is not None}
    d = defaultdict(list)
    for (k, meth), r in idx.items():
        if meth == m and k[0] == sc and k[3] == T and k[4] == kind and k[5] == rate:
            o = idx.get((k, REF))
            if o:
                d[k[1]].append(r["iscore_nonnull_mean"] - o["iscore_nonnull_mean"])
    if not d:
        return None
    topos = sorted(d)
    sums = np.array([np.sum(d[t]) for t in topos])
    cnts = np.array([len(d[t]) for t in topos])
    est = float(sums.sum() / cnts.sum())
    rng = np.random.default_rng(SEED)
    picks = rng.integers(0, len(topos), size=(B, len(topos)))
    boot = sums[picks].sum(1) / cnts[picks].sum(1)
    lo, hi = np.quantile(boot, (0.025, 0.975))
    return {"est": est, "lo": float(lo), "hi": float(hi),
            "p_less": float((1 + (boot >= 0).sum()) / (B + 1)), "p_greater": float((1 + (boot <= 0).sum()) / (B + 1)),
            "n_pairs": int(cnts.sum()), "n_clusters": len(topos)}


def identity(rows, old):
    a = {key(r): r for r in rows if r["method"] == REF}
    b = {key(r): r for r in old if r["method"] == REF}
    common = set(a) & set(b)
    same = 0
    for k in common:
        x, y = a[k], b[k]
        if x["status"] != y["status"]:
            continue
        if x["status"] != "ok" or (abs(x["iscore_nonnull_mean"] - y["iscore_nonnull_mean"]) < 1e-12
                                   and x["n_covered_nonnull"] == y["n_covered_nonnull"] and x["n_nonnull"] == y["n_nonnull"]):
            same += 1
    return {"n_new": len(a), "n_old": len(b), "common": len(common), "identical": same,
            "ok": len(a) == len(b) == len(common) == same and len(a) > 0}


def f(x, d=3):
    return "–" if x is None else f"{x:.{d}f}"


def rule(rows):
    S = {(m, *c): stats(rows, m, *c) for m in [REF, *ARMS, "oracle"] for c in ALL}
    P = {(m, *c): paired(rows, m, *c) for m in ARMS for c in ALL}
    verdict = {}
    for arm in (K1, KBC):
        pl = [P[(arm, *c)]["p_less"] for c in PRIMARY]
        pg = [P[(arm, *c)]["p_greater"] for c in PRIMARY]
        rej_l, rej_g = holm(pl), holm(pg)
        pg_o = [P[(arm, *c)]["p_greater"] for c in OTHER]
        rej_go = holm(pg_o)
        wins_raw, wins, prim = 0, 0, []
        for i, c in enumerate(PRIMARY):
            s, s0 = S[(arm, *c)], S[(REF, *c)]
            okn = s["n_ok"] >= s0["n_ok"]
            win = rej_l[i] and s["cov"] >= 0.90 and okn
            wins_raw += int(pl[i] <= 0.05 and s["cov"] >= 0.90 and okn)
            wins += int(win)
            prim.append({"cell": c, "win": win, "holm_less": rej_l[i], "holm_greater": rej_g[i], "cov": s["cov"],
                         "ok_ge_ref": okn, **P[(arm, *c)]})
        cond1 = wins >= 3
        cond2 = all(S[(arm, *c)]["cov"] >= 0.90 for c in PRIMARY)
        cond3 = not any(rej_g)
        other = []
        for i, c in enumerate(OTHER):
            s, s0 = S[(arm, *c)], S[(REF, *c)]
            ratio = s["IS"] / s0["IS"]
            cov_ok = s["cov"] >= 0.90 or s0["cov"] < 0.90
            other.append({"cell": c, "ratio": ratio, "ratio_ok": ratio <= 1.05, "holm_greater": rej_go[i], "cov": s["cov"],
                          "cov_ref": s0["cov"], "cov_ok": cov_ok, **P[(arm, *c)]})
        cond4 = all(o["ratio_ok"] and not o["holm_greater"] and o["cov_ok"] for o in other)
        cond5 = all(S[(arm, *c)]["n_ok"] >= S[(REF, *c)]["n_ok"] for c in ALL)
        trip = rej_g[PRIMARY.index(TRIP)]
        retained = cond1 and cond2 and cond3 and cond4 and cond5 and not trip
        verdict[arm] = {"wins_holm": wins, "wins_raw": wins_raw, "cond1_wins_ge3": cond1, "cond2_cov_primary": cond2,
                        "cond3_no_primary_worse": cond3, "n_primary_worse_holm": int(sum(rej_g)),
                        "n_primary_worse_raw": int(sum(p <= 0.05 for p in pg)), "cond4_noharm_other": cond4,
                        "n_other_ratio_fail": sum(not o["ratio_ok"] for o in other),
                        "n_other_worse_holm": sum(o["holm_greater"] for o in other),
                        "n_other_worse_raw": int(sum(p <= 0.05 for p in pg_o)),
                        "n_other_cov_fail": sum(not o["cov_ok"] for o in other), "cond5_failures": cond5,
                        "tripwire": bool(trip), "tripwire_p_greater": pg[PRIMARY.index(TRIP)],
                        "verdict": "RETAINED (exploratory)" if retained else ("REJECTED (tripwire)" if trip else "NOT RETAINED"),
                        "primary": prim, "other": other}
    # K0
    cov_all = all(S[(K0, *c)]["cov"] >= 0.90 for c in ALL)
    ni = [P[(K0, *c)]["hi"] < 0.05 * S[(REF, *c)]["IS"] for c in PRIMARY]
    verdict[K0] = {"cov_all_21": cov_all, "n_cov_fail": sum(S[(K0, *c)]["cov"] < 0.90 for c in ALL),
                   "noninferior_primary": int(sum(ni)), "noninferior_cells": [list(c) for c, x in zip(PRIMARY, ni) if x],
                   "verdict": "RETAINED (factor-free)" if cov_all and sum(ni) >= 6 else "NOT RETAINED"}
    # family overlay
    fam = [(arm, c, P[(arm, *c)]["p_less"]) for arm in (K1, KBC) for c in PRIMARY]
    rej = holm([x[2] for x in fam])
    overlay = {"n_tests": len(fam), "rejected": int(sum(rej)),
               "by_arm": {arm: int(sum(r for (a, _, _), r in zip(fam, rej) if a == arm)) for arm in (K1, KBC)}}
    sel = None
    kept = [a for a in (K1, KBC) if verdict[a]["verdict"].startswith("RETAINED")]
    if len(kept) == 1:
        sel = kept[0]
    elif len(kept) == 2:
        w = {a: verdict[a]["wins_holm"] for a in kept}
        if w[K1] != w[KBC]:
            sel = max(w, key=w.get)
        else:
            mis = {a: np.mean([S[(a, *c)]["IS"] for c in PRIMARY]) for a in kept}
            sel = KBC if mis[KBC] < mis[K1] else K1
    return S, P, verdict, overlay, sel


def main():
    rows = load(RUN)
    old = load("ext_v51_eval")
    ident = identity(rows, old)
    S, P, V, overlay, sel = rule(rows)
    cal = json.loads((RES / RUN / "calibration.json").read_text())
    man = json.loads((RES / RUN / "manifest.json").read_text())
    L = [f"# {RUN}: ruling of r4kilianbab (generated by experiments/ext/r4kilianbab/analyze.py)", "",
         f"Rows {man['n_rows']}, runtime {man['seconds']} s (calibration {man['seconds_calibration']} s), workers {man['workers']}.", "",
         "## Pairing / reproducibility", "",
         f"- tolerant_v5_1 rows of this run vs results/ext_v51_eval: {ident['identical']}/{ident['common']} identical "
         f"({ident['n_new']} vs {ident['n_old']} rows) -> **{ident['ok']}**", "",
         "## Width factors (effective = runner factor x 0.5; K0 has none)", "",
         "| T | kind | v5_1 | K1 | KBC | K1 − v5_1 |", "|---|---|---|---|---|---|"]
    fac = {}
    for T in TS:
        for k in ("none", "extra", "missing", "reversed"):
            v = [cal.get(f"{m}|{T}|{k}") for m in (REF, K1, KBC)]
            e = [x * 0.5 if x is not None else None for x in v]
            fac[f"{T}|{k}"] = dict(zip(("v5_1", "K1", "KBC"), e))
            L.append(f"| {T} | {k} | {f(e[0], 2)} | {f(e[1], 2)} | {f(e[2], 2)} | {e[1] - e[0]:+.2f} |")
    L += ["", "## Cells: coverage / IS (n ok) per method; oracle_cal = oracle x 1.4/1.3/1.2", "",
          "| T | cell | v5_1 | K1 | KBC | K0 | oracle | oracle_cal |", "|---|---|---|---|---|---|---|---|"]
    for c in ALL:
        cs = []
        for m in [REF, *ARMS, "oracle"]:
            s = S[(m, *c)]
            cs.append(f"{f(s.get('cov'))} / {f(s.get('IS'), 2)} ({s['n_ok']})")
        so = S[("oracle", *c)]
        cs.append(f"{f(so.get('cov_ocal'))} / {f(so.get('IS_ocal'), 2)}")
        L.append(f"| {c[0]} | {c[1]}-{c[2]} | " + " | ".join(cs) + " |")
    L += ["", "## Paired dIS = arm − v5_1 [95% cluster CI], p one-sided (less / greater); B = 20000, seed 20261104", "",
          "| T | cell | primary | K1 | KBC | K0 |", "|---|---|---|---|---|---|"]
    for c in ALL:
        cs = []
        for m in ARMS:
            p = P[(m, *c)]
            cs.append(f"{p['est']:+.3f} [{p['lo']:+.3f}, {p['hi']:+.3f}] p<{p['p_less']:.4f} p>{p['p_greater']:.4f}")
        L.append(f"| {c[0]} | {c[1]}-{c[2]} | {'yes' if c in PRIMARY else ''} | " + " | ".join(cs) + " |")
    L += ["", "## Verdicts (rule of docs/ext/r4kilianbab.md section 4)", ""]
    for arm in (K1, KBC):
        v = V[arm]
        L.append(f"- **{arm}**: WIN {v['wins_holm']}/8 after Holm (raw {v['wins_raw']}/8); coverage >= 0.90 in all 8 primary: "
                 f"{v['cond2_cov_primary']}; primary significantly worse: {v['n_primary_worse_holm']}/8 after Holm (raw {v['n_primary_worse_raw']}/8); "
                 f"no-harm other 13: {v['cond4_noharm_other']} (IS ratio > 1.05: {v['n_other_ratio_fail']}/13; worse after Holm: "
                 f"{v['n_other_worse_holm']}/13, raw {v['n_other_worse_raw']}/13; coverage gate fails: {v['n_other_cov_fail']}/13); "
                 f"failures <= v5_1 in all 21: {v['cond5_failures']}; tripwire T80 reversed-0.5: {v['tripwire']} "
                 f"(p> = {v['tripwire_p_greater']:.4f}) -> **{v['verdict']}**")
    v0 = V[K0]
    L.append(f"- **{K0}**: coverage >= 0.90 in all 21: {v0['cov_all_21']} (fails {v0['n_cov_fail']}/21); non-inferior "
             f"{v0['noninferior_primary']}/8 -> **{v0['verdict']}**")
    L.append(f"- Family overlay (Holm 0.05 over {overlay['n_tests']} primary tests of K1 + KBC): rejected {overlay['rejected']} "
             f"(K1 {overlay['by_arm'][K1]}, KBC {overlay['by_arm'][KBC]}).")
    L.append(f"- Selected arm (R5): {sel}")
    # diagnostics
    L += ["", "## Kilian diagnostics (K-core, mean over ok runs)", "",
          "| T | cell | |bias| lag1 | |bias| lag2 | own-lag1 bias | own-lag2 bias | cross |bias| lag1 | data shrunk | data uncorrected | draws shrunk | draws uncorrected | mean d draws |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in ALL:
        s = S[(K1, *c)]
        L.append(f"| {c[0]} | {c[1]}-{c[2]} | {f(s.get('info_bab_absbias_lag1'), 4)} | {f(s.get('info_bab_absbias_lag2'), 4)} | "
                 f"{f(s.get('info_bab_bias_own_lag1'), 4)} | {f(s.get('info_bab_bias_own_lag2'), 4)} | {f(s.get('info_bab_absbias_cross_lag1'), 4)} | "
                 f"{f(s.get('share_data_shrunk'))} | {f(s.get('share_data_uncorrected'))} | {f(s.get('info_bab_share_draws_shrunk'))} | "
                 f"{f(s.get('info_bab_share_draws_uncorrected'))} | {f(s.get('info_bab_mean_d_draws'))} |")
    L += ["", "## Centring on non-null pairs: median over runs of the run median of sign(C_true)·(x − C_true) "
          "(negative = toward 0); x = interval midpoint (mid) or point estimate (C); share of misses on the zero side", "",
          "| T | cell | v5_1 mid | K1 mid | KBC mid | oracle mid | v5_1 C | K1 C | v5_1 miss→0 | K1 miss→0 | KBC miss→0 | K0 miss→0 | oracle miss→0 |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in ALL:
        g = lambda m, k: S[(m, *c)].get(k)  # noqa: E731
        L.append(f"| {c[0]} | {c[1]}-{c[2]} | {f(g(REF, 'med_shrink_mid'))} | {f(g(K1, 'med_shrink_mid'))} | {f(g(KBC, 'med_shrink_mid'))} | "
                 f"{f(g('oracle', 'med_shrink_mid'))} | {f(g(REF, 'med_shrink_C'))} | {f(g(K1, 'med_shrink_C'))} | "
                 f"{f(g(REF, 'share_miss_toward0'), 2)} ({g(REF, 'miss_toward0')}/{g(REF, 'miss_toward0') + g(REF, 'miss_away')}) | "
                 f"{f(g(K1, 'share_miss_toward0'), 2)} ({g(K1, 'miss_toward0')}/{g(K1, 'miss_toward0') + g(K1, 'miss_away')}) | "
                 f"{f(g(KBC, 'share_miss_toward0'), 2)} | {f(g(K0, 'share_miss_toward0'), 2)} | {f(g('oracle', 'share_miss_toward0'), 2)} |")
    L += ["", "## KBC: BC bookkeeping (mean over ok runs)", "", "| T | cell | share pairs skipped (ties) | share capped | mean |z0| | mean z0 |",
          "|---|---|---|---|---|---|"]
    for c in ALL:
        s = S[(KBC, *c)]
        L.append(f"| {c[0]} | {c[1]}-{c[2]} | {f(s.get('info_bc_share_skipped'))} | {f(s.get('info_bc_share_capped'))} | "
                 f"{f(s.get('info_bc_mean_abs_z0'))} | {f(s.get('info_bc_mean_z0'))} |")
    # predictions
    pa = fac["40|missing"]["K1"] - fac["40|missing"]["v5_1"]
    pb = {f"{c}": P[(K1, *c)]["est"] < 0 for c in PRIMARY}
    pc = {f"{c}": P[(K1, *c)]["lo"] <= 0 <= P[(K1, *c)]["hi"] for c in ALL if c[0] == 150}
    pe = {f"{c}": (S[(REF, *c)]["med_shrink_mid"], S[(K1, *c)]["med_shrink_mid"], S[(REF, *c)]["share_miss_toward0"]) for c in PRIMARY}
    L += ["", "## Pre-registered predictions (descriptive)", "",
          f"- P-a: K1 effective factor at T40 missing − v5_1's = {pa:+.2f} (prediction <= −0.10): {'held' if pa <= -0.10 else 'did not hold'}",
          f"- P-b: K1 dIS < 0 in {sum(pb.values())}/8 primary cells (point estimates)",
          f"- P-c: K1 CI contains 0 in {sum(pc.values())}/7 T150 cells",
          f"- P-d: tripwire fired for K1: {V[K1]['tripwire']}, KBC: {V[KBC]['tripwire']}",
          "- P-e: see centring table (v5_1 mid negative and miss share > 0.5 at T 40/80?: "
          f"{sum(1 for v in pe.values() if v[0] < 0 and (v[2] or 0) > 0.5)}/8 primary cells; K1 mid closer to 0 than v5_1 in "
          f"{sum(1 for v in pe.values() if abs(v[1]) < abs(v[0]))}/8)"]
    (RES / RUN / "ruling.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    js = {"identity_v51": ident, "factors_effective": fac, "verdict": V, "overlay": overlay, "selected": sel,
          "cells": {f"{m}|{c[0]}|{c[1]}|{c[2]}": S[(m, *c)] for m in [REF, *ARMS, "oracle"] for c in ALL},
          "paired": {f"{m}|{c[0]}|{c[1]}|{c[2]}": P[(m, *c)] for m in ARMS for c in ALL},
          "predictions": {"P-a": pa, "P-b": pb, "P-c": pc, "P-e": pe}}
    (RES / RUN / "ruling.json").write_text(json.dumps(js, indent=1, default=str), encoding="utf-8")
    print("\n".join(L))
    if (RES / RUN_A1 / "runs.jsonl").exists():
        secondary()


def secondary():
    rows = load(RUN_A1)
    old = [r for r in load("ext_v51_a1") if r.get("scenario") in ("latent1", "noise0.1")]
    ident = identity(rows, old)
    L = [f"# {RUN_A1}: secondary scenarios (descriptive no-harm; generated by experiments/ext/r4kilianbab/analyze.py)", "",
         f"- tolerant_v5_1 rows vs results/ext_v51_a1 (latent1, noise0.1): {ident['identical']}/{ident['common']} identical "
         f"({ident['n_new']} vs {ident['n_old']}) -> **{ident['ok']}**", "",
         "| scenario | T | cell | v5_1 cov / IS | K1 cov / IS | KBC cov / IS | K0 cov / IS | oracle cov | K1 − v5_1 [CI] | KBC − v5_1 [CI] |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    out = {"identity_v51": ident, "cells": {}}
    pg = []
    for sc in ("latent1", "noise0.1"):
        for T in (80, 150):
            for kind, rate in (("none", 0.0), ("missing", 0.2), ("reversed", 0.2)):
                st = {m: stats(rows, m, T, kind, rate, sc) for m in [REF, *ARMS, "oracle"]}
                pp = {m: paired(rows, m, T, kind, rate, sc) for m in (K1, KBC)}
                out["cells"][f"{sc}|{T}|{kind}|{rate}"] = {"stats": st, "paired": pp}
                pg.append((sc, T, kind, rate, pp[K1]["p_greater"], pp[KBC]["p_greater"]))
                L.append(f"| {sc} | {T} | {kind}-{rate} | " + " | ".join(f"{f(st[m].get('cov'))} / {f(st[m].get('IS'), 2)}" for m in [REF, *ARMS])
                         + f" | {f(st['oracle'].get('cov'))} | " + " | ".join(f"{pp[m]['est']:+.3f} [{pp[m]['lo']:+.3f}, {pp[m]['hi']:+.3f}]" for m in (K1, KBC)) + " |")
    for j, arm in ((4, K1), (5, KBC)):
        rej = holm([x[j] for x in pg])
        raw = sum(x[j] <= 0.05 for x in pg)
        L.append(f"\n- {arm}: significantly worse than v5_1 after Holm over 12 cells: {sum(rej)}/12 (raw {raw}/12)")
        out[f"worse_holm_{arm}"] = int(sum(rej))
        out[f"worse_raw_{arm}"] = int(raw)
    (RES / RUN_A1 / "describe.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (RES / RUN_A1 / "describe.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
