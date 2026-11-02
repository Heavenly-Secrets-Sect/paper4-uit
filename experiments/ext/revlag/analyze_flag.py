"""R2-7: one-shot evaluation of the frozen RQ4.4 flag (experiments/ext/revlag/frozen_flag.json)
on the FRESH D-07 development runs (seed_base 30261102), exactly as pre-registered in
docs/ext/revlag.md, section (c). The model is NOT refitted.

Rows: tolerant_v4, non-null pairs. miss = C_true outside [lo, hi]. Score = p_hat of the frozen
logistic. Topology-cluster bootstrap (20 clusters), 2000 resamples, percentile CI, seed 20261103;
one-sided p = share of resamples on the H0 side (floor 1/2000).

Run:  python experiments/ext/revlag/analyze_flag.py
Writes results/ext_revlag_fresh/flag_eval.{md,json}.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from flaglib import score  # noqa: E402

B, SEED = 2000, 20261103
FROZEN_SHA = "7da8843fab352e798bec6471497192cfba201c0fa64ea333d2a4510938c37df3"


def holm(p):
    p = np.asarray(p, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    run = 0.0
    for r, idx in enumerate(order):
        run = max(run, (len(p) - r) * p[idx])
        adj[idx] = min(1.0, run)
    return adj


def load(run, method="tolerant_v4"):
    z = np.load(ROOT / "results" / run / "pairs.npz")
    d = {k: z[k] for k in z.files}
    methods = [str(m) for m in d["methods"]]
    sel = d["method"] == methods.index(method)
    rows = {k: d[k][sel] for k in ("topo", "rep", "scen", "T", "cell", "C_t", "C_e", "lo", "hi", "stated")}
    rows["scen_names"] = [str(s) for s in d["scenarios"]]
    rows["cells"] = [str(c) for c in d["cells"]]
    return rows


class Clus:
    def __init__(self, topo):
        self.topos = np.array(sorted(set(topo.astype(int))))
        rng = np.random.default_rng(SEED)
        idx = rng.integers(0, len(self.topos), size=(B, len(self.topos)))
        self.W = np.stack([np.bincount(r, minlength=len(self.topos)) for r in idx]).astype(float)

    def pos(self, topo):
        return np.searchsorted(self.topos, topo.astype(int))


def auc_reps(s, y, pos, W):
    """Point AUROC and cluster-bootstrap replicates (row weight = multiplicity of its topology)."""
    u, inv = np.unique(s, return_inverse=True)
    def one(w):
        P = np.bincount(inv, weights=w * y, minlength=len(u))
        N = np.bincount(inv, weights=w * (1 - y), minlength=len(u))
        tp, tn = P.sum(), N.sum()
        if tp == 0 or tn == 0:
            return np.nan
        below = np.cumsum(N) - N
        return float((P * (below + 0.5 * N)).sum() / (tp * tn))
    point = one(np.ones(len(s)))
    reps = np.array([one(W[b][pos]) for b in range(W.shape[0])])
    return point, reps


def ci(r):
    r = r[np.isfinite(r)]
    return float(np.quantile(r, 0.025)), float(np.quantile(r, 0.975))


def p_le(r, thr):
    r = r[np.isfinite(r)]
    return max(float(np.mean(r <= thr)), 1 / B)


def flag_stats(flag, y, pos, W, K):
    def sums(x):
        return np.bincount(pos, weights=x, minlength=K)
    fm, fn, um, un = sums(flag * y), sums(flag), sums((1 - flag) * y), sums(1 - flag)
    share = fn.sum() / (fn.sum() + un.sum())
    with np.errstate(invalid="ignore", divide="ignore"):
        ratio = (fm.sum() / fn.sum()) / (um.sum() / un.sum())
        reps = ((W @ fm) / (W @ fn)) / ((W @ um) / (W @ un))
    return dict(share=float(share), miss_flagged=float(fm.sum() / max(fn.sum(), 1)),
                miss_unflagged=float(um.sum() / max(un.sum(), 1)), ratio=float(ratio), ratio_ci=ci(reps),
                p_ratio_le1=p_le(reps, 1.0))


def evaluate(rows, sel, frozen, label):
    r = {k: (v[sel] if isinstance(v, np.ndarray) else v) for k, v in rows.items()}
    y = (~((r["lo"] <= r["C_t"]) & (r["C_t"] <= r["hi"]))).astype(float)
    p = score(r, frozen)
    width = r["hi"] - r["lo"]
    relw = width / (np.abs(r["C_e"]) + 1e-9)
    cl = Clus(r["topo"])
    pos = cl.pos(r["topo"])
    a_p, rp = auc_reps(p, y, pos, cl.W)
    a_r, rr = auc_reps(relw, y, pos, cl.W)
    fs = flag_stats((p > frozen["threshold"]).astype(float), y, pos, cl.W, len(cl.topos))
    return dict(label=label, n=int(len(y)), n_topo=int(len(cl.topos)), miss_rate=float(y.mean()), auc_p=a_p,
                auc_p_ci=ci(rp), p_auc_le_065=p_le(rp, 0.65), p_auc_le_05=p_le(rp, 0.5), auc_rel=a_r,
                auc_rel_ci=ci(rr), d_auc=a_p - a_r, d_auc_ci=ci(rp - rr), p_d_le0=p_le(rp - rr, 0.0), **fs)


def fmt(e):
    return (f"| {e['label']} | {e['n']} | {e['miss_rate']:.3f} | {e['auc_p']:.3f} [{e['auc_p_ci'][0]:.3f}, {e['auc_p_ci'][1]:.3f}] | "
            f"{e['auc_rel']:.3f} [{e['auc_rel_ci'][0]:.3f}, {e['auc_rel_ci'][1]:.3f}] | {e['d_auc']:+.3f} "
            f"[{e['d_auc_ci'][0]:+.3f}, {e['d_auc_ci'][1]:+.3f}] | {e['share']:.3f} | {e['miss_flagged']:.3f} / "
            f"{e['miss_unflagged']:.3f} | {e['ratio']:.2f} [{e['ratio_ci'][0]:.2f}, {e['ratio_ci'][1]:.2f}] |")


def main():
    fpath = HERE / "frozen_flag.json"
    sha = hashlib.sha256(fpath.read_bytes()).hexdigest()
    assert sha == FROZEN_SHA, f"frozen flag changed: {sha}"
    frozen = json.loads(fpath.read_text())
    out = ROOT / "results/ext_revlag_fresh"
    clean = load("ext_revlag_fresh")
    res = {"frozen_sha256": sha}
    hi = clean["T"] >= 80
    lo = clean["T"] == 40
    res["clean_T80_150"] = evaluate(clean, hi, frozen, "clean T80/150 (7 cell)")
    res["clean_T40"] = evaluate(clean, lo, frozen, "clean T40 (7 cell)")
    res["clean_all"] = evaluate(clean, np.ones(len(clean["T"]), bool), frozen, "clean all T (mô tả)")
    e1, e3 = res["clean_T80_150"], res["clean_T40"]
    F1 = e1["auc_p_ci"][0] > 0.65
    F2 = e1["d_auc_ci"][0] > 0
    F3 = e3["auc_p_ci"][0] > 0.65
    F4h = e1["share"] <= 0.5 and e1["ratio"] >= 2 and e1["ratio_ci"][0] > 1
    F4l = e3["share"] <= 0.5 and e3["ratio"] >= 2 and e3["ratio_ci"][0] > 1
    ps = [e1["p_auc_le_065"], e1["p_d_le0"], e3["p_auc_le_065"], e1["p_ratio_le1"], e3["p_ratio_le1"]]
    ph = holm(ps)
    holm_pass = [ph[0] < 0.05, ph[1] < 0.05, ph[2] < 0.05,
                 ph[3] < 0.05 and e1["share"] <= 0.5 and e1["ratio"] >= 2,
                 ph[4] < 0.05 and e3["share"] <= 0.5 and e3["ratio"] >= 2]
    verdict = all([F1, F2, F3, F4h, F4l])
    res["rule"] = dict(F1=F1, F2=F2, F3=F3, F4_T80_150=F4h, F4_T40=F4l, p=ps, p_holm=ph.tolist(),
                       n_pass_holm=int(sum(holm_pass)), holm_pass=holm_pass, verdict="ĐẠT" if verdict else "KHÔNG ĐẠT")
    # per-cell description
    res["clean_cells"] = []
    for c, cname in enumerate(clean["cells"]):
        sel = hi & (clean["cell"] == c)
        res["clean_cells"].append(evaluate(clean, sel, frozen, f"clean T80/150 {cname}"))
    # secondary scenarios
    sec = []
    ges = load("ext_revlag_fresh_ges")
    ges_all = np.ones(len(ges["T"]), bool)
    sec.append(evaluate(ges, ges_all, frozen, "GES all T"))
    extra = [evaluate(ges, ges["T"] == T, frozen, f"GES T{T}") for T in (40, 80, 150)]
    a1 = load("ext_revlag_fresh_a1")
    for s_idx, sname in enumerate(a1["scen_names"]):
        sec.append(evaluate(a1, a1["scen"] == s_idx, frozen, f"{sname} T80/150 (3 cell)"))
    ph2 = holm([e["p_auc_le_05"] for e in sec])
    for e, a in zip(sec, ph2):
        e["p_auc_le_05_holm"] = float(a)
        e["transfers"] = bool(e["auc_p_ci"][0] > 0.5)
        e["transfers_holm"] = bool(a < 0.05)
    res["secondary"] = sec
    res["ges_by_T"] = extra
    res["n_transfer"] = int(sum(e["transfers"] for e in sec))
    res["n_transfer_holm"] = int(sum(e["transfers_holm"] for e in sec))
    hdr = ["| tập | n | miss rate | AUROC(p_hat) [CI] | AUROC(rel_width) [CI] | delta AUROC [CI] | flagged share | "
           "miss flagged / unflagged | ratio [CI] |", "|---|---|---|---|---|---|---|---|---|"]
    rr = res["rule"]
    L = ["# R2-7: frozen RQ4.4 flag, one-shot evaluation on fresh D-07 development (seed_base 30261102)", "",
         f"frozen_flag.json sha256 {sha} (unchanged, not refitted). Rows: tolerant_v4, non-null pairs. "
         "CI: topology-cluster bootstrap, 20 clusters, 2000 resamples, seed 20261103.", "", "## Rule F1-F4", ""] + hdr + \
        [fmt(e1), fmt(e3), fmt(res["clean_all"])] + \
        ["", f"- F1 (AUROC lower CI > 0.65, T80/150): {F1}", f"- F2 (delta AUROC vs rel_width lower CI > 0, T80/150): {F2}",
         f"- F3 (AUROC lower CI > 0.65, T40): {F3}", f"- F4 T80/150 (share <= 0.5, ratio >= 2, ratio lower CI > 1): {F4h}",
         f"- F4 T40: {F4l}",
         f"- one-sided p [F1, F2, F3, F4hi, F4lo] = {[round(x, 4) for x in ps]}; Holm = {[round(float(x), 4) for x in ph]}; "
         f"conditions passing after Holm: {rr['n_pass_holm']}/5", "",
         f"**Verdict cờ RQ4.4: {rr['verdict']}**", "", "## Theo cell (clean, T80/150; mô tả)", ""] + hdr + \
        [fmt(e) for e in res["clean_cells"]] + \
        ["", "## Phụ: GES, latent, noise (mô tả; 'chuyển được' = AUROC(p_hat) lower CI > 0.5)", ""] + hdr + \
        [fmt(e) for e in sec] + [fmt(e) for e in extra] + \
        ["", "Chuyển được: " + ", ".join(f"{e['label']}: {e['transfers']} (Holm p {e['p_auc_le_05_holm']:.4f})" for e in sec),
         f"", f"Số kịch bản chuyển được: {res['n_transfer']}/5 chưa hiệu chỉnh; {res['n_transfer_holm']}/5 sau Holm."]
    (out / "flag_eval.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "flag_eval.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else o))
    print("\n".join(L))


if __name__ == "__main__":
    main()
