"""P4-H1 held-out replication of the frozen RQ4.4 flag (rule F1-F4 of docs/ext/revlag.md, unchanged).
Rows: tolerant_v4 of results/ext_p4h1_rq44_{dev,conf}/pairs.npz pooled (40 topology clusters; conf topo ids
offset by 100), stated encoding = width_key as stored (same as the D-07 verdict). Frozen flag sha256 pinned.
Bootstrap: topology clusters, 2000 resamples, seed 20261103 (Clus of analyze_flag.py). Holm over 5 conditions.
Run: python experiments/ext/p4h1/rq44/analyze_p4h1_rq44.py
Writes results/ext_p4h1_rq44/{flag_eval.md, flag_eval.json}.
"""
import hashlib, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "experiments/ext/revlag3"))
sys.path.insert(0, str(ROOT / "experiments/ext/revlag"))
from flag3 import HDR, evaluate3, fmt3, load3  # noqa: E402
from analyze_flag import FROZEN_SHA, holm  # noqa: E402

MIN_CLUSTERS = 8


def pooled():
    a = load3("ext_p4h1_rq44_dev", encoding="round2")
    b = load3("ext_p4h1_rq44_conf", encoding="round2")
    assert a["cells"] == b["cells"]
    r = {}
    for k, v in a.items():
        r[k] = np.concatenate([v, b[k]]) if isinstance(v, np.ndarray) else v
    r["topo"] = np.concatenate([a["topo"], b["topo"] + 100])
    r["split"] = np.concatenate([np.zeros(len(a["T"])), np.ones(len(b["T"]))])
    return r


def main():
    fpath = ROOT / "experiments/ext/revlag/frozen_flag.json"
    sha = hashlib.sha256(fpath.read_bytes()).hexdigest()
    assert sha == FROZEN_SHA
    frozen = json.loads(fpath.read_text())
    rows = pooled()
    res = {"frozen_sha256": sha}
    hi, lo = rows["T"] >= 80, rows["T"] == 40
    e1 = evaluate3(rows, hi, frozen, "P4-H1 pooled T80/150 (7 cell)")
    e3 = evaluate3(rows, lo, frozen, "P4-H1 pooled T40 (7 cell)")
    ok_clusters = e1["n_topo"] >= MIN_CLUSTERS and e3["n_topo"] >= MIN_CLUSTERS
    F = {"F1": e1["auc_p_ci"][0] > 0.65, "F2": e1["d_auc_ci"][0] > 0, "F3": e3["auc_p_ci"][0] > 0.65,
         "F4_T80_150": e1["share"] <= 0.5 and e1["ratio"] >= 2 and e1["ratio_ci"][0] > 1,
         "F4_T40": e3["share"] <= 0.5 and e3["ratio"] >= 2 and e3["ratio_ci"][0] > 1}
    ps = [e1["p_auc_le_065"], e1["p_d_le0"], e3["p_auc_le_065"], e1["p_ratio_le1"], e3["p_ratio_le1"]]
    ph = holm(ps)
    hp = [ph[0] < .05, ph[1] < .05, ph[2] < .05, ph[3] < .05 and e1["share"] <= .5 and e1["ratio"] >= 2,
          ph[4] < .05 and e3["share"] <= .5 and e3["ratio"] >= 2]
    verdict = "TÁI LẬP ĐẠT" if (all(F.values()) and ok_clusters) else "TÁI LẬP KHÔNG ĐẠT"
    res["rule"] = dict(F=F, p=ps, p_holm=ph.tolist(), holm_pass=[bool(x) for x in hp], n_pass_raw=int(sum(F.values())),
                       n_pass_holm=int(sum(hp)), verdict=verdict)
    res["primary"] = [e1, e3]
    desc = [evaluate3(rows, rows["T"] == T, frozen, f"pooled T{T}") for T in (40, 80, 150)]
    desc += [evaluate3(rows, hi & (rows["cell"] == c), frozen, f"pooled T80/150 {cn}") for c, cn in enumerate(rows["cells"])]
    desc += [evaluate3(rows, lo & (rows["cell"] == c), frozen, f"pooled T40 {cn}") for c, cn in enumerate(rows["cells"])]
    for s, sn in ((0, "development"), (1, "confirmatory")):
        m = rows["split"] == s
        desc += [evaluate3(rows, hi & m, frozen, f"{sn} T80/150"), evaluate3(rows, lo & m, frozen, f"{sn} T40")]
    res["descriptive"] = desc
    # per-split F1-F4 reading (descriptive)
    ps_rule = {}
    for s, sn in ((0, "development"), (1, "confirmatory")):
        a, b = desc[-4 + 2 * s], desc[-3 + 2 * s]
        ps_rule[sn] = {"F1": a["auc_p_ci"][0] > .65, "F2": a["d_auc_ci"][0] > 0, "F3": b["auc_p_ci"][0] > .65,
                       "F4hi": a["share"] <= .5 and a["ratio"] >= 2 and a["ratio_ci"][0] > 1,
                       "F4lo": b["share"] <= .5 and b["ratio"] >= 2 and b["ratio_ci"][0] > 1}
    res["per_split_rule_descriptive"] = ps_rule
    L = ["# RQ4.4 P4-H1: frozen flag, held-out replication (seed_base 80261102)", "",
         f"frozen_flag.json sha256 {sha} (not refitted). tolerant_v4, 40 topology clusters (20 dev + 20 conf), "
         "bootstrap 2000, seed 20261103.", "", "## Rule F1-F4 (primary, pooled)", ""] + HDR + [fmt3(e1), fmt3(e3)] + \
        ["", *[f"- {k}: {v}" for k, v in F.items()], f"- clusters >= {MIN_CLUSTERS}: {ok_clusters} ({e1['n_topo']}, {e3['n_topo']})",
         f"- one-sided p [F1,F2,F3,F4hi,F4lo] = {[round(x, 4) for x in ps]}; Holm = {[round(float(x), 4) for x in ph]}; "
         f"conditions passing after Holm: {res['rule']['n_pass_holm']}/5; raw: {res['rule']['n_pass_raw']}/5", "",
         f"**Verdict: {verdict}**", "", "## Descriptive (pooled by T, by cell, by split)", ""] + HDR + [fmt3(e) for e in desc] + \
        ["", f"Per-split rule reading (descriptive): {json.dumps(ps_rule)}"]
    out = ROOT / "results/ext_p4h1_rq44"; out.mkdir(parents=True, exist_ok=True)
    (out / "flag_eval.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "flag_eval.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else o))
    print("\n".join(L))


if __name__ == "__main__":
    main()
