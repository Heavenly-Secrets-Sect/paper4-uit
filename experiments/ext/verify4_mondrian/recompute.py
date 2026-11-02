"""Independent recomputation of r4mondrian numbers (skeptic). Own code; reads their npz/jsonl only."""
import json, math, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results/ext_verify4_mondrian"
KINDS = ["none", "extra", "missing", "reversed"]
CELLS = [("none", 0.0)] + [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]
rep = {}

# ---- V1 independent
def load(p): return [json.loads(x) for x in open(p)]
drv = load(ROOT / "results/ext_r4mondrian_eval/runs.jsonl")
sto = [r for r in load(ROOT / "results/ext_v51_eval/runs.jsonl") if r["method"] == "tolerant_v5_1"]
k = lambda r: (r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])
A = {k(r): r for r in drv}; Bm = {k(r): r for r in sto}
fields = ["status", "n_nonnull", "n_covered_nonnull", "iscore_nonnull_mean", "coverage_nonnull", "C_abs_err_nonnull", "iscore_null_mean", "n_covered_null"]
same_all = sum(all(A[x].get(f) == Bm[x].get(f) for f in fields) for x in set(A) & set(Bm))
rep["V1"] = {"n_drv": len(A), "n_sto": len(Bm), "common": len(set(A) & set(Bm)), "exact_equal_8fields": same_all}

# ---- q table from calibration pairs (own conformal quantile)
C = dict(np.load(ROOT / "results/ext_r4mondrian_cal/pairs.npz"))
s = np.abs(C["C_t"] - C["mid"]) / C["h"]
assert (C["h"] > 0).all()
def cq(x, a=0.05):
    x = np.sort(x); n = len(x); kk = math.ceil((n + 1) * (1 - a) - 1e-9)
    return x[kk - 1] if kk <= n else np.inf
myq = {}
for T in (40, 80, 150):
    for kc, kind in enumerate(KINDS):
        m = (C["T"] == T) & (C["stated"] == kc) & (C["rep"] == 0)
        R = C["R"][m].astype(bool)
        q0 = cq(s[m]); merged = min(R.sum(), (~R).sum()) < 50
        myq[f"{T}|{kind}"] = {"all": q0, "R": q0 if merged else cq(s[m][R]), "S": q0 if merged else cq(s[m][~R]), "NR": int(R.sum()), "NS": int((~R).sum())}
their = json.load(open(ROOT / "experiments/ext/r4mondrian/q_table.json"))
rep["q_maxdiff"] = max(abs(myq[f"{T}|{kd}"][c] - their[f"{T}|{kd}|{c}"]["q"]) for T in (40, 80, 150) for kd in KINDS for c in ("all", "R", "S"))
rep["q"] = {kk: {a: float(b) for a, b in v.items()} for kk, v in myq.items()}
# V2 own grid rule
fz = json.load(open(ROOT / "experiments/ext/v51/frozen_v4_v51.json"))
grid = np.round(np.arange(1.0, 10.01, 0.1), 2); v2 = 0
for T in (40, 80, 150):
    for kc, kind in enumerate(KINDS):
        m = (C["T"] == T) & (C["stated"] == kc) & (C["rep"] == 0)
        d = np.abs(C["C_t"][m] - C["mid"][m]); hh = 0.5 * C["h"][m]
        cov = np.array([(d <= g * hh).mean() for g in grid]); tgt = min(0.95, cov.max() - 0.005)
        v2 += abs(grid[np.argmax(cov >= tgt)] - fz[f"tolerant_v5_1|{T}|{kind}"]) < 1e-9
rep["V2"] = int(v2)
# calibration seeds: confirm calibration pairs come from D-07H; topology ids
rep["cal_manifest_bank"] = json.load(open(ROOT / "results/ext_r4mondrian_cal/manifest.json"))["config"]["bank"]

# ---- eval recompute
P = dict(np.load(ROOT / "results/ext_r4mondrian_eval/pairs.npz"))
Ct, mid, h = P["C_t"], P["mid"], P["h"]
def qarr(c):
    out = np.empty(len(Ct))
    for T in (40, 80, 150):
        for kc, kind in enumerate(KINDS):
            m = (P["T"] == T) & (P["stated"] == kc); out[m] = myq[f"{T}|{kind}"][c]
    return out
q0, qR, qS = qarr("all"), qarr("R"), qarr("S")
half = {"M0": q0 * h, "M2": np.where(P["R"].astype(bool), qR, qS) * h}
LO = {"v51": P["lo51"], "M0": mid - half["M0"], "M2": mid - half["M2"]}
HI = {"v51": P["hi51"], "M0": mid + half["M0"], "M2": mid + half["M2"]}
IS = {m: (HI[m] - LO[m]) + 40 * np.maximum(LO[m] - Ct, 0) + 40 * np.maximum(Ct - HI[m], 0) for m in LO}
CV = {m: (LO[m] <= Ct) & (Ct <= HI[m]) for m in LO}
# check pairs-based v51 IS vs stored rows per run
stored_is = {(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"]): r["iscore_nonnull_mean"] for r in sto}
topo_ids = json.load(open(ROOT / "results/ext_r4mondrian_eval/manifest.json"))["topologies"]
maxdev = 0.0
def boot(topo, x, B=20000, seed=20261104):
    ids = np.unique(topo); sx = np.array([x[topo == t].sum() for t in ids]); sw = np.array([(topo == t).sum() for t in ids])
    rng = np.random.default_rng(seed); pk = rng.integers(0, len(ids), (B, len(ids)))
    b = sx[pk].sum(1) / sw[pk].sum(1)
    pl = (1 + (b >= 0).sum()) / (B + 1); pg = (1 + (b <= 0).sum()) / (B + 1)
    return float(sx.sum() / sw.sum()), float(np.quantile(b, .025)), float(np.quantile(b, .975)), float(min(1, 2 * min(pl, pg)))
cells = []
for T in (40, 80, 150):
    for c, (kind, rate) in enumerate(CELLS):
        m = (P["T"] == T) & (P["cell"] == c)
        rid = P["topo"][m] * 10 + P["rep"][m]; ur, inv = np.unique(rid, return_inverse=True)
        rt = ur // 10
        per = {mm: np.bincount(inv, IS[mm][m]) / np.bincount(inv) for mm in IS}
        for u, val in zip(ur, per["v51"]):
            key = (topo_ids[u // 10]["id"], int(u % 10), T, kind, rate)
            maxdev = max(maxdev, abs(val - stored_is[key]))
        row = {"T": T, "cell": f"{kind}-{rate}", "cov": {mm: float(CV[mm][m].mean()) for mm in CV}, "IS": {mm: float(per[mm].mean()) for mm in per}}
        for tag, a, b in (("M2_v51", "M2", "v51"), ("M2_M0", "M2", "M0"), ("M0_v51", "M0", "v51")):
            row[tag] = boot(rt, per[a] - per[b])
        row["p_M2_v51_alt_seeds"] = [boot(rt, per["M2"] - per["v51"], seed=sd)[3] for sd in (1, 2, 3, 4, 5, 20261105, 777, 2024, 31337, 99)]
        # M0 coverage CI (cluster by topology), deviation from 0.95
        cvv = CV["M0"][m].astype(float) - 0.95
        row["M0_cov_ci"] = boot(P["topo"][m], cvv)
        cells.append(row)
rep["max_dev_pairs_IS_v51_vs_stored"] = maxdev
def holm(p, a=.05):
    o = np.argsort(p); rej = np.zeros(len(p), bool)
    for r, i in enumerate(o):
        if p[i] <= a / (len(p) - r): rej[i] = True
        else: break
    return rej
dam = [r for r in cells if not r["cell"].startswith("none")]
hv = holm(np.array([r["M2_v51"][3] for r in dam])); hm = holm(np.array([r["M2_M0"][3] for r in dam]))
rep["holm18_v51_rej"] = [(r["T"], r["cell"], round(r["M2_v51"][0], 4)) for r, x in zip(dam, hv) if x]
rep["holm18_M0_rej"] = [(r["T"], r["cell"]) for r, x in zip(dam, hm) if x]
p21 = np.array([r["M2_v51"][3] for r in cells]); h21 = holm(p21)
rep["holm21_rej"] = [(r["T"], r["cell"], r["M2_v51"][0]) for r, x in zip(cells, h21) if x]
rep["min_p21"] = float(p21.min()); rep["thr21"] = 0.05 / 21
# seed sensitivity of holm21 for the borderline cell
alt = np.array([r["p_M2_v51_alt_seeds"] for r in cells])  # cells x seeds
rep["holm21_worse_by_seed"] = []
for j in range(alt.shape[1]):
    hj = holm(alt[:, j]); rep["holm21_worse_by_seed"].append(int(sum(1 for r, x in zip(cells, hj) if x and r["M2_v51"][0] > 0)))
rep["T40rev05_p_alt"] = [r for r in cells if r["T"] == 40 and r["cell"] == "reversed-0.5"][0]["p_M2_v51_alt_seeds"]
rep["M0_isratio_max"] = max(abs(r["IS"]["M0"] / r["IS"]["v51"] - 1) for r in cells)
rep["M0_dcov_max"] = max(abs(r["cov"]["M0"] - r["cov"]["v51"]) for r in cells)
rep["M2_cov_range"] = [min(r["cov"]["M2"] for r in cells), max(r["cov"]["M2"] for r in cells)]
rep["M2_isratio_max"] = max(r["IS"]["M2"] / r["IS"]["v51"] for r in cells)
rep["M0_cov_excl_095"] = sum(1 for r in cells if not (r["M0_cov_ci"][1] <= 0 <= r["M0_cov_ci"][2]))
# pooled-by-(T,kind) M0 coverage (the actual conformal target group pools both rates)
pooled = {}
for T in (40, 80, 150):
    for kc, kind in enumerate(KINDS):
        m = (P["T"] == T) & (P["stated"] == kc)
        e = boot(P["topo"][m], CV["M0"][m].astype(float) - 0.95)
        pooled[f"{T}|{kind}"] = [round(e[0] + .95, 4), round(e[1] + .95, 4), round(e[2] + .95, 4)]
rep["M0_cov_pooled_by_T_kind"] = pooled
rep["cells"] = cells
json.dump(rep, open(OUT / "recompute.json", "w"), indent=1, default=float)
for kk, v in rep.items():
    if kk != "cells" and kk != "q": print(kk, v)
for r in cells:
    print(r["T"], r["cell"], {m: round(v, 3) for m, v in r["cov"].items()}, {m: round(v, 3) for m, v in r["IS"].items()},
          "M2-v51 %+.3f [%+.3f,%+.3f] p%.4f" % tuple(r["M2_v51"]), "M2-M0 %+.3f p%.4f" % (r["M2_M0"][0], r["M2_M0"][3]))
