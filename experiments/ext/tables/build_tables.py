"""R3-8 manuscript tables (hướng `tables`). Definitions: docs/ext/bang_ban_thao.md section 0 (written first).

Reads stored D-07 development rows only (no runner call, no bank read). Writes results/ext_tables_main/.
Usage: python3 experiments/ext/tables/build_tables.py
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "ext_tables_main"
B, SEED = 20000, 20261102
ALPHA = 0.05
MIN_OK = 54
TS = [40, 80, 150]
CELLS = [("none", 0.0), ("extra", 0.2), ("extra", 0.5), ("missing", 0.2), ("missing", 0.5),
         ("reversed", 0.2), ("reversed", 0.5)]

# (source run, methods taken from it)
SOURCES = [
    ("a2_baselines", ["tolerant_v4", "oracle", "plugin", "inflate", "bagging", "lp_allpast", "ida_union", "bvar_minnesota"]),
    ("a2b_pselect", ["tolerant_v4", "pselect_union"]),
    ("ext_redteam_calbase", ["tolerant_v4", "pselect_cal", "bvar_cal", "ida_cal", "fullvar_cal"]),
    ("ext_tlp_eval", ["tolerant_v4", "targeted_lp", "targeted_lp_cal"]),
    ("ext_baselines2_eval", ["tolerant_v4", "pselect_union_v2", "pselect_union_v2_cal", "bvar_minnesota_v2",
                             "bvar_minnesota_v2_cal"]),
    ("ext_v4c_eval", ["tolerant_v4", "tolerant_v4c", "pselect_union_c2", "ida_union_c2", "bvar_minnesota_c2"]),
    ("ext_v51_eval", ["tolerant_v4", "tolerant_v5_1"]),
]
TLP2_RUNS = ["ext_tlp2_t40", "ext_tlp2_t80a", "ext_tlp2_t80b", "ext_tlp2_t80c", "ext_tlp2_t150a", "ext_tlp2_t150b",
             "ext_tlp2_t150c", "ext_tlp2_t150d"]
TLP2_METHODS = ["tlp2_db", "tlp2_db_p3", "tlp2_lp_cal"]
B3 = ("ext_baselines3_eval", ["tolerant_v4", "tolerant_v5_1", "pselect_union_v3", "pselect_union_v3_cal", "pselect_cal",
                              "fullvar_cal", "targeted_lp", "targeted_lp_cal", "bvar_minnesota_v2_cal"])

CANDIDATES = ["plugin", "inflate", "bagging", "lp_allpast", "ida_union", "bvar_minnesota", "pselect_union",
              "pselect_cal", "bvar_cal", "ida_cal", "fullvar_cal", "targeted_lp", "targeted_lp_cal",
              "pselect_union_v2", "pselect_union_v2_cal", "bvar_minnesota_v2", "bvar_minnesota_v2_cal",
              "pselect_union_c2", "ida_union_c2", "bvar_minnesota_c2", "tlp2_db", "tlp2_db_p3", "tlp2_lp_cal",
              "pselect_union_v3", "pselect_union_v3_cal"]

BUDGET_DRAWS = {
    "plugin": "199 residual-bootstrap refits", "inflate": "199 (plugin draws, widened)",
    "bagging": "≤199 perturbed-skeleton refits", "lp_allpast": "0 (analytic Newey–West)",
    "ida_union": "≤16 members × max(10, 199 // members)", "ida_cal": "như ida_union", "ida_union_c2": "như ida_union",
    "bvar_minnesota": "199 posterior draws", "bvar_cal": "199 posterior draws", "bvar_minnesota_c2": "199 posterior draws",
    "bvar_minnesota_v2": "199 posterior draws", "bvar_minnesota_v2_cal": "199 posterior draws",
    "pselect_union": "≤16 graphs × max(10, 199 // graphs)", "pselect_cal": "≤16 graphs × max(10, 199 // graphs)",
    "pselect_union_c2": "≤16 graphs × max(10, 199 // graphs)",
    "pselect_union_v2": "info_n_draws", "pselect_union_v2_cal": "info_n_draws",
    "pselect_union_v3": "info_n_draws", "pselect_union_v3_cal": "info_n_draws",
    "fullvar_cal": "199 bootstrap refits", "targeted_lp": "199 VAR-sieve draws", "targeted_lp_cal": "199 VAR-sieve draws",
    "tlp2_lp_cal": "199 VAR-sieve draws", "tlp2_db": "200 × 100 (MSDB)", "tlp2_db_p3": "200 × 100 (MSDB)",
    "tolerant_v4": "199 refits", "tolerant_v5_1": "199 refits (re-selection mỗi draw)", "tolerant_v4c": "199 refits",
}
TIMING_KEY = {"pselect_union_v3_cal": "pselect_union_v3", "targeted_lp_cal": "targeted_lp",
              "bvar_minnesota_v2_cal": "bvar_minnesota_v2"}


def rkey(r):
    return (r["topology"], int(r["replicate"]), int(r["T"]), r["kind"], round(float(r["rate"]), 6))


def load_rows(run, methods):
    out = {}
    with open(ROOT / "results" / run / "runs.jsonl", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["method"] in methods and r.get("scenario", "clean") == "clean":
                out[(r["method"],) + rkey(r)] = r
    return out


def v4_sig(r):
    return (r["status"], r.get("iscore_nonnull_mean"), r.get("n_covered_nonnull"))


def build_index():
    checks = {}
    ref = None
    idx = {}            # (method, unit...) -> row
    src_of = {}         # (method, T, kind, rate) -> source
    allsrc = SOURCES + [(r, ["tolerant_v4"] + TLP2_METHODS) for r in TLP2_RUNS] + [B3]
    for run, methods in allsrc:
        rows = load_rows(run, set(methods))
        v4 = {k[1:]: v4_sig(v) for k, v in rows.items() if k[0] == "tolerant_v4"}
        if ref is None:
            ref = v4
            checks[run] = {"n_v4": len(v4), "mismatch_vs_a2_baselines": 0}
        else:
            common = [u for u in v4 if u in ref]
            mm = sum(1 for u in common if v4[u] != ref[u])
            checks[run] = {"n_v4": len(v4), "n_common": len(common), "mismatch_vs_a2_baselines": mm}
        tlp2_run = run in TLP2_RUNS
        for k, r in rows.items():
            m = k[0]
            if m == "tolerant_v4" and (tlp2_run or run == B3[0]):
                continue            # v4 rows of tlp2 runs differ by E1 (c_idx); b3 v4 checked, a2 copy kept
            cell = (k[3], k[4], k[5])
            if run == B3[0]:
                if m == "tolerant_v5_1":
                    continue        # keep ext_v51_eval rows (checked identical below)
                idx[k] = r
                src_of[(m,) + cell] = run
            else:
                if (m,) + cell in src_of and src_of[(m,) + cell] == B3[0]:
                    continue
                if k in idx and m == "tolerant_v4":
                    continue
                idx[k] = r
                src_of[(m,) + cell] = run
    # table 2 uses stored rows only (section 0.3): a copy of idx without the ext_baselines3_eval overrides
    idx_stored = dict(idx)
    for run, methods in SOURCES:
        rows = load_rows(run, set(methods) - {"tolerant_v4"})
        for k, r in rows.items():
            if k[0] in ("pselect_cal", "fullvar_cal", "targeted_lp", "targeted_lp_cal", "bvar_minnesota_v2_cal"):
                idx_stored[k] = r
    # b3 v5_1 vs ext_v51_eval identity
    b3 = load_rows(B3[0], {"tolerant_v5_1"})
    mm = sum(1 for k, r in b3.items() if k in idx and v4_sig(idx[k]) != v4_sig(r))
    checks["ext_baselines3_eval:tolerant_v5_1_vs_ext_v51_eval"] = {"n": len(b3), "mismatch": mm}
    return idx, idx_stored, src_of, checks


class Paired:
    def __init__(self, idx):
        self.idx = idx
        self.topos = sorted({k[1] for k in idx})
        self.tpos = {t: i for i, t in enumerate(self.topos)}
        self.reps = sorted({k[2] for k in idx})
        self.ix = np.random.default_rng(SEED).integers(0, len(self.topos), size=(B, len(self.topos)))
        self.nonnull = {}
        for k, r in idx.items():
            if r["status"] == "ok" and r.get("n_nonnull") is not None:
                self.nonnull.setdefault(k[1:], r["n_nonnull"])

    def units(self, T, kind, rate):
        return [(t, rp, T, kind, rate) for t in self.topos for rp in self.reps if (t, rp, T, kind, rate) in self.nonnull]

    def cell(self, m, T, kind, rate):
        us = self.units(T, kind, rate)
        got = [self.idx.get((m,) + u) for u in us]
        if all(g is None for g in got):
            return None
        ok = [g for g in got if g is not None and g["status"] == "ok" and g.get("iscore_nonnull_mean") is not None]
        num = sum(g["n_covered_nonnull"] for g in ok)
        den = sum(self.nonnull[u] for u in us)
        widths = [g["width_kept"] for g in ok if g.get("width_kept") is not None]
        return {"n_runs": len(us), "n_ok": len(ok), "cov": num / den if den else float("nan"),
                "IS": float(np.mean([g["iscore_nonnull_mean"] for g in ok])) if ok else float("nan"),
                "width_median": float(np.median(widths)) if widths else float("nan"),
                "n_draws_mean": (float(np.mean([g["info_n_draws"] for g in ok if g.get("info_n_draws") is not None]))
                                 if any(g.get("info_n_draws") is not None for g in ok) else None)}

    def diff(self, a, b, T, kind, rate):
        sums, cnts = np.zeros(len(self.topos)), np.zeros(len(self.topos))
        for t in self.topos:
            for rp in self.reps:
                x = self.idx.get((a, t, rp, T, kind, rate))
                y = self.idx.get((b, t, rp, T, kind, rate))
                if x and y and x["status"] == "ok" and y["status"] == "ok" and x.get("iscore_nonnull_mean") is not None \
                        and y.get("iscore_nonnull_mean") is not None:
                    sums[self.tpos[t]] += x["iscore_nonnull_mean"] - y["iscore_nonnull_mean"]
                    cnts[self.tpos[t]] += 1
        if cnts.sum() == 0:
            return None
        est = float(sums.sum() / cnts.sum())
        with np.errstate(invalid="ignore", divide="ignore"):
            boots = sums[self.ix].sum(1) / cnts[self.ix].sum(1)
        boots = boots[np.isfinite(boots)]
        lo, hi = np.quantile(boots, (0.025, 0.975))
        pW = (1 + int((boots >= 0).sum())) / (len(boots) + 1)
        pL = (1 + int((boots <= 0).sum())) / (len(boots) + 1)
        return {"a": a, "b": b, "T": T, "kind": kind, "rate": rate, "n": int(cnts.sum()), "est": est,
                "lo": float(lo), "hi": float(hi), "p2": min(1.0, 2 * min(pW, pL)),
                "raw": "W" if hi < 0 else ("L" if lo > 0 else "T")}


def holm(comps, alpha=ALPHA, key="p2", out="holm", neg="W"):
    order = sorted(range(len(comps)), key=lambda i: (comps[i][key], i))
    m = len(order)
    rej = set()
    for r, i in enumerate(order):
        if comps[i][key] <= alpha / (m - r):
            rej.add(i)
        else:
            break
    for i, c in enumerate(comps):
        pos = "L" if neg == "W" else "W"
        c[out] = (neg if c["est"] < 0 else pos) if i in rej else "T"
        c["holm_family_size"] = m
    return comps


def counts(comps, col):
    return {k: sum(1 for c in comps if c[col] == k) for k in ("W", "T", "L")}


def fmt_d(c):
    return f"{c['est']:+.2f} [{c['lo']:+.2f}, {c['hi']:+.2f}]"


def cname(kind, rate):
    return "none" if kind == "none" else f"{kind}-{rate}"


# ------------------------------------------------------------------------------------------- table 1
def table1(P, src_of, timing):
    rows, comps = [], []
    for T in TS:
        for kind, rate in CELLS:
            stats = {}
            for m in CANDIDATES:
                c = P.cell(m, T, kind, rate)
                if c is not None and c["n_ok"] >= MIN_OK:
                    stats[m] = c
            X = min(stats, key=lambda m: stats[m]["IS"])
            el = [m for m in stats if stats[m]["cov"] >= 0.90]
            X90 = min(el, key=lambda m: stats[m]["IS"]) if el else None
            second = sorted(stats, key=lambda m: stats[m]["IS"])[:3]
            row = {"T": T, "kind": kind, "rate": rate, "X": X, "X90": X90, "top3": second,
                   "stats": {m: stats[m] for m in set(second) | {X} | ({X90} if X90 else set())},
                   "src": {m: src_of.get((m, T, kind, rate)) for m in set(second) | {X} | ({X90} if X90 else set())},
                   "v4": P.cell("tolerant_v4", T, kind, rate), "v5_1": P.cell("tolerant_v5_1", T, kind, rate),
                   "n_candidates": len(stats)}
            for ref in ([X] + ([X90] if X90 and X90 != X else [])):
                for mod in ("tolerant_v4", "tolerant_v5_1"):
                    d = P.diff(mod, ref, T, kind, rate)
                    d["role"] = "X" if ref == X else "X90"
                    comps.append(d)
            rows.append(row)
    holm(comps)
    return rows, comps


# ------------------------------------------------------------------------------------------- table 2
def table2(P):
    meths = ["tolerant_v4c", "tolerant_v5_1", "fullvar_cal", "pselect_cal"]
    stats, comps = {}, []
    for T in TS:
        for kind, rate in CELLS:
            for m in ["tolerant_v4"] + meths:
                stats[f"{m}|{T}|{kind}|{rate}"] = P.cell(m, T, kind, rate)
            for m in meths:
                comps.append(P.diff(m, "tolerant_v4", T, kind, rate))
    holm(comps)
    return stats, comps


# ------------------------------------------------------------------------------------------- table 5
def table5(P):
    pts = ["plugin", "inflate", "bagging", "lp_allpast"]
    stats, comps, skipped = {}, [], []
    for T in TS:
        for kind, rate in CELLS:
            for m in ["oracle", "tolerant_v4", "tolerant_v5_1"] + pts:
                stats[f"{m}|{T}|{kind}|{rate}"] = P.cell(m, T, kind, rate)
            for mod in ("tolerant_v4", "tolerant_v5_1"):
                for p in pts:
                    c = stats[f"{p}|{T}|{kind}|{rate}"]
                    if c is None or c["n_ok"] < MIN_OK:
                        skipped.append(f"{mod}-{p}|{T}|{kind}|{rate}")
                        continue
                    comps.append(P.diff(mod, p, T, kind, rate))
    holm(comps)
    return stats, comps, skipped


# ------------------------------------------------------------------------------------------- table 3, 4 (pairs)
class Boot:      # same construction as experiments/ext/revlag/analyze_lag.py
    def __init__(self, topos, b=2000, seed=20261103):
        self.topos = np.array(sorted(set(topos)))
        idx = np.random.default_rng(seed).integers(0, len(self.topos), size=(b, len(self.topos)))
        self.W = np.stack([np.bincount(r, minlength=len(self.topos)) for r in idx]).astype(float)
        self.b = b

    def ratio(self, topo, num, den=None):
        den = np.ones(len(num)) if den is None else den
        pos = np.searchsorted(self.topos, topo)
        sn = np.bincount(pos, weights=num, minlength=len(self.topos))
        sd = np.bincount(pos, weights=den, minlength=len(self.topos))
        point = sn.sum() / sd.sum() if sd.sum() > 0 else np.nan
        with np.errstate(invalid="ignore", divide="ignore"):
            reps = (self.W @ sn) / (self.W @ sd)
        return float(point), reps[np.isfinite(reps)]


def gtest(boot, topo, x):
    g, reps = boot.ratio(topo, x)
    lo, hi = np.quantile(reps, (0.025, 0.975))
    p2 = min(1.0, 2 * min(max(np.mean(reps <= 0), 1 / boot.b), max(np.mean(reps >= 0), 1 / boot.b)))
    return {"g": g, "est": g, "lo": float(lo), "hi": float(hi), "p2": float(p2),
            "raw": "L" if hi < 0 else ("W" if lo > 0 else "T")}


def load_pairs():
    z = np.load(ROOT / "results" / "ext_revlag_lag" / "pairs.npz")
    methods = [str(m) for m in z["methods"]]
    cells = [str(c) for c in z["cells"]]
    d = {k: z[k] for k in ("topo", "rep", "T", "cell", "method", "j", "i", "C_t", "lo", "hi", "dC", "role", "direct_lag")}
    return d, methods, cells


def table3_4():
    d, methods, cells = load_pairs()
    mv4, mor = methods.index("tolerant_v4"), methods.index("oracle")
    key = lambda s: list(zip(d["topo"][s], d["rep"][s], d["T"][s], d["cell"][s], d["j"][s], d["i"][s]))
    s4, so = d["method"] == mv4, d["method"] == mor
    k4, ko = key(s4), key(so)
    pos_o = {k: n for n, k in enumerate(ko)}
    order = np.array([pos_o[k] for k in k4])
    lo_o, hi_o = d["lo"][so][order], d["hi"][so][order]
    C = d["C_t"][s4]
    T = d["T"][s4].astype(int)
    cell = d["cell"][s4].astype(int)
    topo = d["topo"][s4].astype(int)
    dC = d["dC"][s4]
    role = d["role"][s4].astype(int)
    dl = d["direct_lag"][s4]
    cov4 = ((d["lo"][s4] <= C) & (C <= d["hi"][s4])).astype(float)
    covr = ((lo_o <= C) & (C <= hi_o)).astype(float)
    fac = np.vectorize({40: 1.4, 80: 1.3, 150: 1.2}.get)(T)
    mid, half = (lo_o + hi_o) / 2, (hi_o - lo_o) / 2
    covc = ((mid - fac * half <= C) & (C <= mid + fac * half)).astype(float)
    boot = Boot(topo)
    t3 = {}
    fam = defaultdict(list)
    for Tv in TS:
        for kind, rate in CELLS:
            cn = f"{kind}|{rate}"
            ci_ = cells.index(cn)
            base = (T == Tv) & (cell == ci_)
            for grp, sel in (("affected", base & (dC >= 0.05)), ("unaffected", base & (dC < 0.05))):
                n = int(sel.sum())
                ent = {"n": n}
                if n:
                    ent.update({"cov_v4": float(cov4[sel].mean()), "cov_oraw": float(covr[sel].mean()),
                                "cov_ocal": float(covc[sel].mean())})
                    for ref, cr in (("ocal", covc), ("oraw", covr)):
                        gt = gtest(boot, topo[sel], (cov4 - cr)[sel])
                        gt.update({"T": Tv, "kind": kind, "rate": rate, "grp": grp, "ref": ref})
                        ent[f"g_{ref}"] = gt
                        if grp == "affected" and kind in ("missing", "reversed"):
                            fam[("affected", ref)].append(gt)
                        if grp == "unaffected":
                            fam[("unaffected", ref)].append(gt)
                t3[f"{Tv}|{cn}|{grp}"] = ent
    for k, comps in fam.items():
        holm(comps, neg="L")          # coverage gap: negative = v4 covers less (L)
    fam_counts = {f"{k[0]}|{k[1]}": {"n": len(v), "raw": {c: sum(1 for x in v if x["raw"] == c) for c in "WTL"},
                                    "holm": {c: sum(1 for x in v if x["holm"] == c) for c in "WTL"}}
                  for k, v in fam.items()}
    # table 4 supplement: deleted-edge coverage, lag 0 vs lag 1-2 (role 2 damaged, missing cells), v4
    t4 = []
    for Tv in TS:
        for rate in (0.2, 0.5):
            ci_ = cells.index(f"missing|{rate}")
            sel = (T == Tv) & (cell == ci_) & (role == 2)
            l0 = sel & (dl == 0)
            l12 = sel & (dl >= 1)
            # difference of pooled shares via cluster bootstrap of the two ratios on the same resamples
            c0, r0 = boot.ratio(topo[l0], cov4[l0])
            c1, r1 = boot.ratio(topo[l12], cov4[l12])
            # recompute aligned replicate vectors (no finite filtering, to keep alignment)
            pos0 = np.searchsorted(boot.topos, topo[l0])
            pos1 = np.searchsorted(boot.topos, topo[l12])
            n0 = np.bincount(pos0, weights=cov4[l0], minlength=len(boot.topos))
            d0 = np.bincount(pos0, minlength=len(boot.topos)).astype(float)
            n1 = np.bincount(pos1, weights=cov4[l12], minlength=len(boot.topos))
            d1 = np.bincount(pos1, minlength=len(boot.topos)).astype(float)
            with np.errstate(invalid="ignore", divide="ignore"):
                reps = (boot.W @ n0) / (boot.W @ d0) - (boot.W @ n1) / (boot.W @ d1)
            reps = reps[np.isfinite(reps)]
            lo, hi = np.quantile(reps, (0.025, 0.975))
            p2 = min(1.0, 2 * min(max(np.mean(reps <= 0), 1 / boot.b), max(np.mean(reps >= 0), 1 / boot.b)))
            t4.append({"T": Tv, "rate": rate, "cov_lag0": c0, "n_lag0": int(l0.sum()), "cov_lag12": c1,
                       "n_lag12": int(l12.sum()), "est": c0 - c1, "lo": float(lo), "hi": float(hi), "p2": float(p2),
                       "raw": "L" if hi < 0 else ("W" if lo > 0 else "T")})
    holm(t4, neg="L")                 # lag0 - lag12 < 0: lag-0 covered less (L)
    return t3, fam_counts, t4


def null_cov(idx):
    """DEVIATION from section 0.4: a2_baselines rows carry no n_null. Null pairs are read from the same-seed
    results/ext_revlag_lag/nullpairs.jsonl: share of null pairs whose interval contains 0 (1 - false-signal share)
    and mean null-pair IS. `idx` unused."""
    agg = defaultdict(lambda: [0, 0, 0.0])
    cells = [f"{k}|{r}" for k, r in CELLS]
    z = np.load(ROOT / "results" / "ext_revlag_lag" / "pairs.npz")
    cell_names = [str(c) for c in z["cells"]]
    with open(ROOT / "results" / "ext_revlag_lag" / "nullpairs.jsonl", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["status"] != "ok" or r["method"] not in ("tolerant_v4", "oracle"):
                continue
            a = agg[(r["method"], int(r["T"]), cell_names[int(r["cell"])])]
            a[0] += r["n_null"]
            a[1] += r["n_null_excl0"]
            a[2] += r["is_null_sum"]
    out = {}
    for (m, T, cn), (n, ex, iss) in agg.items():
        out[f"{m}|{T}|{cn}"] = {"n_null": n, "share_contains0": 1 - ex / n if n else None,
                                "false_signal": ex / n if n else None, "IS_null": iss / n if n else None}
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    idx, idx_stored, src_of, checks = build_index()
    P = Paired(idx)
    P_stored = Paired(idx_stored)
    timing = json.load(open(ROOT / "results" / "ext_baselines3_budget" / "timing.json"))["summary"]
    t1_rows, t1_comps = table1(P, src_of, timing)
    t2_stats, t2_comps = table2(P_stored)
    t5_stats, t5_comps, t5_skipped = table5(P)
    t3, t3_counts, t4_lag0 = table3_4()
    nul = null_cov(idx)
    res = {"checks": checks, "B": B, "seed": SEED,
           "t1": {"rows": t1_rows, "comps": t1_comps,
                  "counts": {mod: {"raw": counts([c for c in t1_comps if c["a"] == mod], "raw"),
                                   "holm": counts([c for c in t1_comps if c["a"] == mod], "holm")}
                             for mod in ("tolerant_v4", "tolerant_v5_1")}},
           "t2": {"stats": t2_stats, "comps": t2_comps,
                  "counts": {m: {"raw": counts([c for c in t2_comps if c["a"] == m], "raw"),
                                 "holm": counts([c for c in t2_comps if c["a"] == m], "holm")}
                             for m in ("tolerant_v4c", "tolerant_v5_1", "fullvar_cal", "pselect_cal")}},
           "t3": {"cells": t3, "family_counts": t3_counts, "null": nul},
           "t4_lag0": {"rows": t4_lag0, "raw": counts(t4_lag0, "raw"), "holm": counts(t4_lag0, "holm")},
           "t5": {"stats": t5_stats, "comps": t5_comps, "skipped": t5_skipped,
                  "counts": {f"{mod}-{p}": {"raw": counts([c for c in t5_comps if c["a"] == mod and c["b"] == p], "raw"),
                                            "holm": counts([c for c in t5_comps if c["a"] == mod and c["b"] == p], "holm")}
                             for mod in ("tolerant_v4", "tolerant_v5_1")
                             for p in ("plugin", "inflate", "bagging", "lp_allpast")}},
           "timing": {k: v["median_seconds"] for k, v in timing.items()}}
    with open(OUT / "tables.json", "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=float)
    print(json.dumps(checks, indent=1))
    print("t1", res["t1"]["counts"])
    print("t2", res["t2"]["counts"])
    print("t3", t3_counts)
    print("t4", res["t4_lag0"]["raw"], res["t4_lag0"]["holm"])
    print("t5", res["t5"]["counts"], "skipped", len(t5_skipped))


if __name__ == "__main__":
    main()
