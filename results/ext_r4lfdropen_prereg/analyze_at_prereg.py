"""Analyzer of the r4lfdropen direction (rule in docs/ext/r4lfdropen.md, section 2).

Reads results/ext_r4lfdropen_{eval,latent}/ (ruling) and, if present, results/ext_r4lfdropen_{scen,lag1,lag4}/
(secondary, descriptive). Writes results/<out>/ruling.json, ruling.md, secondary.json.

Run: /Users/kietnt/miniconda3/bin/python experiments/ext/r4lfdropen/analyze.py [--eval NAME] [--latent NAME] [--out NAME]
"""
import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
RES = ROOT / "results"
REF, CAND = "tolerant_v5_1", "tolerant_v5_1_lfdr"
B, SEED = 20000, 20261104
ALPHA = 0.05


def load(name):
    p = RES / name / "runs.jsonl"
    return [json.loads(x) for x in open(p)] if p.exists() else None


def skel_log(name):
    out = {}
    for line in open(RES / name / "skeletons.jsonl"):
        s = json.loads(line)
        if s.get("kind") == "missing" and "log" in s:
            out[(s["topology"], s["replicate"], s["rate"])] = {"%d-%d" % tuple(sorted(e["pair"])) for e in s["log"]}
    return out


def key(r):
    return (r.get("scenario", "clean"), r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])


def strip(r, drop_info=()):
    return {k: v for k, v in r.items() if k != "method" and k not in drop_info}


def same_row(a, b):
    """Exact equality of every field of ``a`` (except method and the candidate-only info keys)."""
    for k, v in a.items():
        if k == "method":
            continue
        w = b.get(k, "<absent>")
        if isinstance(v, float) and isinstance(w, float) and math.isnan(v) and math.isnan(w):
            continue
        if v != w:
            return False
    return True


def identity(rows_a, ma, rows_b, mb, sel):
    A = {key(r): r for r in rows_a if r["method"] == ma and sel(r)}
    Bm = {key(r): r for r in rows_b if r["method"] == mb and sel(r)}
    common = set(A) & set(Bm)
    same = sum(1 for k in common if same_row(A[k], Bm[k]))
    return {"n_a": len(A), "n_b": len(Bm), "common": len(common), "identical": same,
            "pass": len(A) == len(Bm) == len(common) == same and len(A) > 0}


def cell(rows, m, sc, T, kind, rate):
    g = [r for r in rows if r["method"] == m and r.get("scenario", "clean") == sc and r["T"] == T
         and r["kind"] == kind and r["rate"] == rate]
    ok = [r for r in g if r["status"] == "ok"]
    if not ok:
        return {"n": 0, "of": len(g), "fail": len(g)}
    w = [r["width_kept"] for r in ok if r.get("width_kept") is not None]
    out = {"n": len(ok), "of": len(g), "fail": len(g) - len(ok),
           "cov": sum(r["n_covered_nonnull"] for r in ok) / sum(r["n_nonnull"] for r in ok),
           "IS": float(np.mean([r["iscore_nonnull_mean"] for r in ok])),
           "width": float(np.median(w)) if w else None,
           "abs_err": float(np.median([r["C_abs_err_nonnull"] for r in ok]))}
    for k in ("info_n_open", "info_n_open_boot_mean", "info_c_T", "info_n_repair", "info_lfdr_mu", "info_lfdr_s"):
        v = [r[k] for r in ok if r.get(k) is not None]
        out[k] = float(np.mean(v)) if v else None
    return out


def paired(rows, sc, T, kind, rate, m=CAND, ref=REF):
    idx = {(key(r), r["method"]): r for r in rows if r["status"] == "ok" and r.get("iscore_nonnull_mean") is not None}
    d = defaultdict(list)
    for (k, meth), r in idx.items():
        if meth == m and k[0] == sc and k[3] == T and k[4] == kind and k[5] == rate:
            o = idx.get((k, ref))
            if o:
                d[k[1]].append(r["iscore_nonnull_mean"] - o["iscore_nonnull_mean"])
    if not d:
        return None
    topos = sorted(d)
    sums = np.array([np.sum(d[t]) for t in topos])
    cnts = np.array([len(d[t]) for t in topos])
    rng = np.random.default_rng(SEED)
    picks = rng.integers(0, len(topos), size=(B, len(topos)))
    boots = sums[picks].sum(1) / cnts[picks].sum(1)
    est = float(sums.sum() / cnts.sum())
    lo, hi = np.quantile(boots, (0.025, 0.975))
    p_less = (1 + int((boots >= 0).sum())) / (B + 1)
    p_greater = (1 + int((boots <= 0).sum())) / (B + 1)
    return {"est": est, "lo": float(lo), "hi": float(hi), "p2": min(1.0, 2 * min(p_less, p_greater)),
            "p_less": p_less, "p_greater": p_greater, "n_pairs": int(cnts.sum()), "n_topo": len(topos)}


def holm(ps, alpha=ALPHA):
    order = np.argsort(ps)
    m = len(ps)
    rej = [False] * m
    for rank, i in enumerate(order):
        if ps[i] <= alpha / (m - rank):
            rej[i] = True
        else:
            break
    return rej


def recall_block(rows, logs, sc="clean"):
    """Recall of the truly missing pairs: candidate on the data fit and draw average, P of true pairs."""
    out = {}
    for r in rows:
        if r["method"] != CAND or r["kind"] != "missing" or r["status"] != "ok" or r.get("scenario", "clean") != sc:
            continue
        if r.get("info_lfdr_open_data") is None:
            continue
        truth = logs[(r["topology"], r["replicate"], r["rate"])]
        op = set(r["info_lfdr_open_data"])
        fr = r["info_lfdr_open_freq"]
        P = r["info_lfdr_P_data"]
        g = out.setdefault((r["T"], r["rate"]), {"rec_data": [], "rec_draw": [], "P_true": [], "P_true_min": []})
        g["rec_data"].append(len(truth & op) / len(truth))
        g["rec_draw"].append(float(np.mean([fr.get(t, 0.0) for t in truth])))
        g["P_true"].append(float(np.mean([P.get(t, 0.0) for t in truth])))
    return {f"{T}|{rate}": {k: float(np.mean(v)) for k, v in g.items() if v} for (T, rate), g in sorted(out.items())}


def v51_recall(cfg_name, logs):
    """v5_1's data-fit open set recomputed (deterministic screen) on regenerated data; also re-derives the
    candidate's data-fit open set and compares it with the logged one."""
    import run_experiment as RE
    from paper4 import ext_narrow, ext_r4lfdropen as L
    from paper4.generator import build_dynamic_sem
    from paper4.topology import load_bank
    cfg = json.loads((ROOT / "experiments/configs" / f"{cfg_name}.json").read_text())
    gen = RE.generator_config(cfg)
    topos = load_bank(cfg["bank"], cfg["split"])[: cfg.get("max_topologies") or None]
    lag = gen.lag_max
    out, match, total = defaultdict(list), 0, 0
    logged = {(r["topology"], r["replicate"], r["T"], r["rate"]): r.get("info_lfdr_open_data")
              for r in load(cfg_name) if r["method"] == CAND and r["kind"] == "missing" and r["status"] == "ok"
              and r.get("scenario", "clean") == "clean"}
    for t_idx, topo in enumerate(topos):
        for rep in range(cfg["replicates"]):
            unit = cfg["seed_base"] + 1000 * t_idx + rep
            sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
            skels = RE.unit_skeletons(sem, unit, cfg)
            for T in cfg["T"]:
                data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
                for (kind, rate), full in skels.items():
                    if kind != "missing":
                        continue
                    sk = RE.public(full)
                    k = sk.damage["k"]
                    truth = logs[(topo.id, rep, rate)]
                    try:
                        v = {L._pkey(u, w) for u, w in ext_narrow.select_open(data, sk, lag, k, 3.0, 0.10)}
                        op, *_ = L.select_open_lfdr(data, sk, lag, k, None)
                    except ValueError:
                        continue
                    out[(T, rate)].append((len(truth & v) / len(truth), len(v)))
                    lg = logged.get((topo.id, rep, T, rate))
                    if lg is not None:
                        total += 1
                        match += int(sorted(lg) == sorted(L._pkey(u, w) for u, w in op))
    return ({f"{T}|{rate}": {"rec_data_v51": float(np.mean([a for a, _ in g])), "n_open_v51_recomputed": float(np.mean([b for _, b in g]))}
             for (T, rate), g in sorted(out.items())}, {"logged_open_set_matches_recomputation": match, "of": total})


def open_distribution(rows, m, sc, T, rate):
    v = [r["info_n_open"] for r in rows if r["method"] == m and r["kind"] == "missing" and r["rate"] == rate and r["T"] == T
         and r.get("scenario", "clean") == sc and r["status"] == "ok" and r.get("info_n_open") is not None]
    b = [r["info_n_open_boot_mean"] for r in rows if r["method"] == m and r["kind"] == "missing" and r["rate"] == rate
         and r["T"] == T and r.get("scenario", "clean") == sc and r["status"] == "ok" and r.get("info_n_open_boot_mean") is not None]
    q = lambda x: [float(np.quantile(x, a)) for a in (0, 0.25, 0.5, 0.75, 1)] if x else None  # noqa: E731
    return {"data_mean": float(np.mean(v)) if v else None, "data_q": q(v),
            "draw_mean": float(np.mean(b)) if b else None, "draw_q": q(b)}


def family(rows, sc, cells):
    res = []
    for T, kind, rate in cells:
        res.append({"scenario": sc, "T": T, "kind": kind, "rate": rate, "cand": cell(rows, CAND, sc, T, kind, rate),
                    "ref": cell(rows, REF, sc, T, kind, rate), "oracle": cell(rows, "oracle", sc, T, kind, rate),
                    "pair": paired(rows, sc, T, kind, rate)})
    ps = [c["pair"]["p2"] if c["pair"] else 1.0 for c in res]
    for c, rj in zip(res, holm(ps)):
        c["holm_reject"] = bool(rj)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", default="ext_r4lfdropen_eval")
    ap.add_argument("--latent", default="ext_r4lfdropen_latent")
    ap.add_argument("--out", default="ext_r4lfdropen_analysis")
    ap.add_argument("--stored-eval", default="ext_v51_eval")
    ap.add_argument("--no-recompute", action="store_true")
    a = ap.parse_args()
    out_dir = RES / a.out
    out_dir.mkdir(parents=True, exist_ok=True)
    ev, lat = load(a.eval), load(a.latent)
    R = {"eval": a.eval, "latent": a.latent, "B": B, "seed": SEED}

    # --- validity ---
    nonmiss = lambda r: r["kind"] != "missing"  # noqa: E731
    R["V1_eval_identity_nonmissing"] = identity(ev, CAND, ev, REF, nonmiss)
    R["V1_latent_identity_none"] = identity(lat, CAND, lat, REF, nonmiss) if lat else None
    st = load(a.stored_eval)
    R["V2_v51_vs_stored_eval"] = identity(ev, REF, st, REF, lambda r: True) if st else None
    v3 = []
    for nm, Ts in (("ext_v51_a1", (80, 150)), ("ext_v51_a1t40", (40,))):
        s = load(nm)
        if s and lat:
            sel = lambda r, Ts=Ts: r.get("scenario") == "latent1" and r["T"] in Ts and r["kind"] in ("none", "missing")  # noqa: E731
            v3.append({"stored": nm, **identity(lat, REF, s, REF, sel)})
    R["V3_v51_latent_vs_stored"] = v3
    v1_pass = R["V1_eval_identity_nonmissing"]["pass"] and (R["V1_latent_identity_none"] or {}).get("pass", False)

    # --- primary ---
    prim = family(ev, "clean", [(T, "missing", rate) for T in (40, 80, 150) for rate in (0.2, 0.5)])
    for c in prim:
        c["win"] = bool(c["pair"] and c["holm_reject"] and c["pair"]["est"] < 0 and c["cand"].get("cov", 0) >= 0.90)
        c["loss"] = bool(c["pair"] and c["holm_reject"] and c["pair"]["est"] > 0)
    R["primary"] = prim
    n_win = sum(c["win"] for c in prim)
    n_raw_win = sum(1 for c in prim if c["pair"] and c["pair"]["hi"] < 0 and c["cand"].get("cov", 0) >= 0.90)
    cov_all = all(c["cand"].get("cov", 0) >= 0.90 for c in prim)
    fail_ok = all(c["cand"]["fail"] <= 3 for c in prim)

    # --- no-harm (latent1 x missing-0.2) ---
    nh = family(lat, "latent1", [(T, "missing", 0.2) for T in (40, 80, 150)]) if lat else []
    for c in nh:
        cr, cc = c["ref"].get("cov"), c["cand"].get("cov")
        c["cov_ok"] = bool(cc is not None and (cr is None or cr < 0.90 or cc >= 0.90))
        c["ratio"] = c["cand"]["IS"] / c["ref"]["IS"] if c["cand"].get("IS") and c["ref"].get("IS") else None
        c["ratio_ok"] = bool(c["ratio"] is not None and c["ratio"] <= 1.05)
        c["worse_holm"] = bool(c["pair"] and c["holm_reject"] and c["pair"]["est"] > 0)
        c["fail_ok"] = c["cand"]["fail"] <= 3
    R["noharm"] = nh
    nh_ok = bool(nh) and all(c["cov_ok"] and c["ratio_ok"] and not c["worse_holm"] and c["fail_ok"] for c in nh)

    R["summary"] = {"V1_pass": v1_pass, "wins_holm": n_win, "wins_raw_ci": n_raw_win, "of": len(prim),
                    "losses_holm": sum(c["loss"] for c in prim), "cov_all_primary_ge_090": cov_all,
                    "fail_ceiling_primary": fail_ok, "noharm_pass": nh_ok,
                    "noharm_cells_pass": sum(1 for c in nh if c["cov_ok"] and c["ratio_ok"] and not c["worse_holm"] and c["fail_ok"]),
                    "noharm_worse_holm": sum(c["worse_holm"] for c in nh)}
    retained = v1_pass and n_win >= 2 and cov_all and fail_ok and nh_ok
    R["verdict"] = "INVALID (validity V1 failed)" if not v1_pass else ("RETAINED (exploratory)" if retained else "NOT RETAINED")

    # --- secondary (descriptive) ---
    S = {}
    cal = json.loads((RES / a.eval / "calibration.json").read_text())
    raw_p = RES / a.eval / "calibration_raw.json"
    raw = json.loads(raw_p.read_text()) if raw_p.exists() else {}
    S["factors"] = {f"{T}|{k}": {"v5_1_frozen": cal.get(f"{REF}|{T}|{k}"), "v5_1_retuned_raw": raw.get(f"{REF}|{T}|{k}"),
                                 "lfdr": cal.get(f"{CAND}|{T}|{k}"), "lfdr_retuned_raw": raw.get(f"{CAND}|{T}|{k}")}
                    for T in (40, 80, 150) for k in ("none", "extra", "missing", "reversed")}
    S["open_counts"] = {f"{T}|{rate}": {"v5_1": open_distribution(ev, REF, "clean", T, rate),
                                        "lfdr": open_distribution(ev, CAND, "clean", T, rate)}
                        for T in (40, 80, 150) for rate in (0.2, 0.5)}
    for kk, v in S["open_counts"].items():
        a_, b_ = v["v5_1"], v["lfdr"]
        v["drop_data"] = 1 - b_["data_mean"] / a_["data_mean"] if a_["data_mean"] else None
        v["drop_draw"] = 1 - b_["draw_mean"] / a_["draw_mean"] if a_["draw_mean"] else None
    logs = skel_log(a.eval)
    S["recall_lfdr"] = recall_block(ev, logs)
    if not a.no_recompute:
        S["recall_v51"], S["open_set_check"] = v51_recall(a.eval, logs)
    S["all_cells"] = family(ev, "clean", [(T, k, r) for T in (40, 80, 150) for k, r in
                                          [("none", 0.0)] + [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]])
    if lat:
        S["recall_lfdr_latent1"] = recall_block(lat, skel_log(a.latent), "latent1")
        S["open_counts_latent1"] = {f"{T}|0.2": {"v5_1": open_distribution(lat, REF, "latent1", T, 0.2),
                                                 "lfdr": open_distribution(lat, CAND, "latent1", T, 0.2)} for T in (40, 80, 150)}
    sec_runs = {}
    for nm in ("ext_r4lfdropen_scen", "ext_r4lfdropen_lag1", "ext_r4lfdropen_lag4"):
        rows = load(nm)
        if rows is None:
            continue
        cfg = json.loads((RES / nm / "manifest.json").read_text())["config"]
        scs = [s["name"] for s in cfg.get("scenarios") or [{"name": "clean"}]]
        fams = {}
        for sc in scs:
            fams[sc] = family(rows, sc, [(T, "missing", r) for T in cfg["T"] for r in cfg["damage"]["rates"]])
        info = {"families": fams}
        cal_p = RES / nm / "calibration.json"
        if cal_p.exists():
            c2 = json.loads(cal_p.read_text())
            info["factors"] = {k: v for k, v in c2.items() if k.startswith("tolerant_v5_1") and "missing" in k}
        if any(s == "clean" for s in scs):
            info["open_counts"] = {f"{T}|{r}": {"v5_1": open_distribution(rows, REF, "clean", T, r),
                                                "lfdr": open_distribution(rows, CAND, "clean", T, r)}
                                   for T in cfg["T"] for r in cfg["damage"]["rates"]}
            info["recall_lfdr"] = recall_block(rows, skel_log(nm))
        sec_runs[nm] = info
    S["secondary_runs"] = sec_runs
    (out_dir / "ruling.json").write_text(json.dumps(R, indent=2, default=float))
    (out_dir / "secondary.json").write_text(json.dumps(S, indent=2, default=float))
    (out_dir / "ruling.md").write_text(render(R, S))
    print(render(R, S))


def f3(x):
    return "–" if x is None else f"{x:.3f}"


def fp(c):
    p = c["pair"]
    return "–" if not p else f"{p['est']:+.3f} [{p['lo']:+.3f}, {p['hi']:+.3f}]"


def render(R, S):
    L = ["# r4lfdropen ruling", "", f"Verdict: **{R['verdict']}**", "", "Summary: " + json.dumps(R["summary"]), "",
         "## Validity", ""]
    for k in ("V1_eval_identity_nonmissing", "V1_latent_identity_none", "V2_v51_vs_stored_eval"):
        L.append(f"- {k}: {json.dumps(R[k])}")
    for v in R["V3_v51_latent_vs_stored"]:
        L.append(f"- V3 {v['stored']}: {json.dumps(v)}")
    L += ["", "## Primary: missing cells, lfdr − v5_1 (B = 20000, seed 20261104, Holm 0.05 over 6)", "",
          "| T | rate | cov lfdr | cov v5_1 | cov oracle | IS lfdr | IS v5_1 | IS oracle | dIS [95% CI] | p2 | Holm | WIN | fail lfdr |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in R["primary"]:
        L.append(f"| {c['T']} | {c['rate']} | {f3(c['cand'].get('cov'))} | {f3(c['ref'].get('cov'))} | {f3(c['oracle'].get('cov'))} | "
                 f"{f3(c['cand'].get('IS'))} | {f3(c['ref'].get('IS'))} | {f3(c['oracle'].get('IS'))} | {fp(c)} | "
                 f"{(c['pair'] or {}).get('p2', float('nan')):.5f} | {'rej' if c['holm_reject'] else '–'} | "
                 f"{'WIN' if c['win'] else ('LOSS' if c['loss'] else '–')} | "
                 f"{c['cand']['fail']}/{c['cand']['of']} |")
    L += ["", "## No-harm: latent1 × missing-0.2 (Holm 0.05 over 3)", "",
          "| T | cov lfdr | cov v5_1 | IS lfdr | IS v5_1 | ratio | dIS [95% CI] | p2 | Holm worse | pass |", "|---|---|---|---|---|---|---|---|---|---|"]
    for c in R["noharm"]:
        L.append(f"| {c['T']} | {f3(c['cand'].get('cov'))} | {f3(c['ref'].get('cov'))} | {f3(c['cand'].get('IS'))} | {f3(c['ref'].get('IS'))} | "
                 f"{f3(c['ratio'])} | {fp(c)} | {(c['pair'] or {}).get('p2', float('nan')):.5f} | {'yes' if c['worse_holm'] else 'no'} | "
                 f"{'PASS' if c['cov_ok'] and c['ratio_ok'] and not c['worse_holm'] and c['fail_ok'] else 'FAIL'} |")
    L += ["", "## Secondary (descriptive)", "", "### Width factors (runner value; effective = value × 0.5)", "",
          "| T|kind | v5_1 frozen | v5_1 re-tuned (raw) | lfdr used | lfdr re-tuned (raw) |", "|---|---|---|---|---|"]
    for k, v in S["factors"].items():
        L.append(f"| {k} | {v['v5_1_frozen']} | {v['v5_1_retuned_raw']} | {v['lfdr']} | {v['lfdr_retuned_raw']} |")
    L += ["", "### Opened lag blocks (data fit; mean over draws)", "",
          "| T|rate | v5_1 data | lfdr data | drop | v5_1 draws | lfdr draws | drop | lfdr data q0/25/50/75/100 |", "|---|---|---|---|---|---|---|---|"]
    for k, v in S["open_counts"].items():
        L.append(f"| {k} | {f3(v['v5_1']['data_mean'])} | {f3(v['lfdr']['data_mean'])} | {f3(v['drop_data'])} | "
                 f"{f3(v['v5_1']['draw_mean'])} | {f3(v['lfdr']['draw_mean'])} | {f3(v['drop_draw'])} | {v['lfdr']['data_q']} |")
    L += ["", "### Recall of the truly missing pairs", "", "| T|rate | v5_1 data | lfdr data | lfdr draw avg | mean P of true pairs |", "|---|---|---|---|---|"]
    for k, v in S["recall_lfdr"].items():
        rv = (S.get("recall_v51") or {}).get(k, {})
        L.append(f"| {k} | {f3(rv.get('rec_data_v51'))} | {f3(v.get('rec_data'))} | {f3(v.get('rec_draw'))} | {f3(v.get('P_true'))} |")
    if S.get("open_set_check"):
        L.append(f"\nLogged open sets vs recomputation: {json.dumps(S['open_set_check'])}")
    L += ["", "### All 21 a2 cells (lfdr − v5_1, Holm 0.05 over 21; descriptive)", "",
          "| T | kind | rate | cov lfdr | cov v5_1 | IS lfdr | IS v5_1 | dIS [CI] | Holm |", "|---|---|---|---|---|---|---|---|---|"]
    ps = [c["pair"]["p2"] if c["pair"] else 1.0 for c in S["all_cells"]]
    for c, rj in zip(S["all_cells"], holm(ps)):
        L.append(f"| {c['T']} | {c['kind']} | {c['rate']} | {f3(c['cand'].get('cov'))} | {f3(c['ref'].get('cov'))} | "
                 f"{f3(c['cand'].get('IS'))} | {f3(c['ref'].get('IS'))} | {fp(c)} | {'rej' if rj else '–'} |")
    for nm, info in S["secondary_runs"].items():
        L += ["", f"### {nm} (descriptive; Holm 0.05 within each scenario family)", "",
              "| scenario | T | rate | cov lfdr | cov v5_1 | IS lfdr | IS v5_1 | dIS [CI] | Holm | fail lfdr/v5_1 |", "|---|---|---|---|---|---|---|---|---|---|"]
        for sc, fam in info["families"].items():
            for c in fam:
                L.append(f"| {sc} | {c['T']} | {c['rate']} | {f3(c['cand'].get('cov'))} | {f3(c['ref'].get('cov'))} | "
                         f"{f3(c['cand'].get('IS'))} | {f3(c['ref'].get('IS'))} | {fp(c)} | {'rej' if c['holm_reject'] else '–'} | "
                         f"{c['cand']['fail']}/{c['ref']['fail']} |")
        if info.get("factors"):
            L.append(f"\nFactors: {json.dumps(info['factors'])}")
        if info.get("open_counts"):
            L.append("\nOpen counts (data mean v5_1 → lfdr; draw mean): " + "; ".join(
                f"{k}: {f3(v['v5_1']['data_mean'])}→{f3(v['lfdr']['data_mean'])}, {f3(v['v5_1']['draw_mean'])}→{f3(v['lfdr']['draw_mean'])}"
                for k, v in info["open_counts"].items()))
            L.append("\nRecall lfdr: " + json.dumps(info.get("recall_lfdr")))
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
