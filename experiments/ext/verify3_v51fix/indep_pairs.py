"""Independent recomputation (verify3_v51fix) of v51fix pairings; no repo imports."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
R = ROOT / "results"
def load(run): return [json.loads(l) for l in open(R / run / "runs.jsonl")]
def key(r): return (r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])
CELLS = [("none", 0.0)] + [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]
cells = [(T, k, r) for T in (40, 80, 150) for k, r in CELLS]
def holm(p, a=0.025):
    o = np.argsort(p); m = len(p); rej = [False]*m
    for i, j in enumerate(o):
        if p[j] <= a/(m-i): rej[j] = True
        else: break
    return rej
ev = load("ext_v51_eval")
idx = defaultdict(dict)
for r in ev:
    if r["method"] in ("tolerant_v4", "tolerant_v5_1"): idx[r["method"]][key(r)] = r
src = {"ext_v4c_eval": ["tolerant_v4c", "pselect_union_c2", "bvar_minnesota_c2"],
       "ext_baselines2_eval": ["pselect_union_v2", "pselect_union_v2_cal", "bvar_minnesota_v2_cal", "bvar_minnesota_v2"]}
out = {}
for run, ms in src.items():
    oth = load(run)
    v4o = {key(r): r for r in oth if r["method"] == "tolerant_v4"}
    nid = sum(1 for k, r in idx["tolerant_v4"].items() if k in v4o and r["status"] == v4o[k]["status"] and
              (r["status"] != "ok" or (abs(r["iscore_nonnull_mean"] - v4o[k]["iscore_nonnull_mean"]) < 1e-12 and r["n_covered_nonnull"] == v4o[k]["n_covered_nonnull"])))
    out[f"identity_{run}"] = [nid, len(idx["tolerant_v4"]), len(v4o)]
    for r in oth:
        if r["method"] in ms: idx[r["method"]][key(r)] = r
    for X in ms:
        st = {"cells": {}}
        pw, pl, rw, rl = [], [], [], []
        for c in cells:
            def cov(m):
                g = [r for k, r in idx[m].items() if k[2:] == c and r["status"] == "ok"]
                return sum(r["n_covered_nonnull"] for r in g)/sum(r["n_nonnull"] for r in g), float(np.mean([r["iscore_nonnull_mean"] for r in g])), len(g)
            cm, cx = cov("tolerant_v5_1"), cov(X)
            d = defaultdict(list)
            for k, r in idx["tolerant_v5_1"].items():
                if k[2:] == c and r["status"] == "ok" and k in idx[X] and idx[X][k]["status"] == "ok":
                    d[k[0]].append(r["iscore_nonnull_mean"] - idx[X][k]["iscore_nonnull_mean"])
            tp = sorted(d)
            sums = np.array([sum(d[t]) for t in tp]); cn = np.array([len(d[t]) for t in tp])
            # independent: vectorized topology bootstrap (different stream than theirs) for CI and p
            pk = np.random.default_rng(12345).integers(0, len(tp), size=(20000, len(tp)))
            b = sums[pk].sum(1)/cn[pk].sum(1)
            est = sums.sum()/cn.sum(); lo, hi = np.quantile(b, (0.025, 0.975))
            p_less = (1+(b >= 0).sum())/(len(b)+1); p_gr = (1+(b <= 0).sum())/(len(b)+1)
            rw.append(cm[0] >= .9 and hi < 0); rl.append(cx[0] >= .9 and lo > 0)
            pw.append(p_less if cm[0] >= .9 else 1.0); pl.append(p_gr if cx[0] >= .9 else 1.0)
            st["cells"][f"{c}"] = {"v51_cov": cm[0], "v51_IS": cm[1], "X_cov": cx[0], "X_IS": cx[1], "n_ok_X": cx[2],
                                   "est": est, "lo": lo, "hi": hi, "p_less": p_less, "p_greater": p_gr, "n_pairs": int(cn.sum())}
        hw, hl = holm(pw), holm(pl)
        st["v51_wins_raw"], st["v51_wins_holm"], st["X_wins_raw"], st["X_wins_holm"] = sum(rw), sum(hw), sum(rl), sum(hl)
        st["X_wins_cells_raw"] = [str(c) for c, f in zip(cells, rl) if f]
        st["X_wins_cells_holm"] = [str(c) for c, f in zip(cells, hl) if f]
        st["v51_wins_cells_holm"] = [str(c) for c, f in zip(cells, hw) if f]
        out[X] = st
OUT = R / "ext_verify3_v51fix"; OUT.mkdir(parents=True, exist_ok=True)
(OUT / "indep_pairs.json").write_text(json.dumps(out, indent=1, default=float))
for k, v in out.items():
    if k.startswith("identity"): print(k, v); continue
    print(k, "v51 wins", v["v51_wins_raw"], "/", v["v51_wins_holm"], " X wins", v["X_wins_raw"], "/", v["X_wins_holm"], v["X_wins_cells_raw"], v["X_wins_cells_holm"])
    for c in ["(40, 'missing', 0.2)", "(40, 'missing', 0.5)", "(80, 'missing', 0.2)", "(80, 'missing', 0.5)", "(150, 'missing', 0.2)", "(150, 'missing', 0.5)", "(40, 'extra', 0.2)", "(40, 'extra', 0.5)", "(80, 'none', 0.0)"]:
        s = v["cells"][c]; print("  ", c, f"{s['est']:+.3f} [{s['lo']:+.3f},{s['hi']:+.3f}] p<{s['p_less']:.4f} p>{s['p_greater']:.4f} covM {s['v51_cov']:.3f} covX {s['X_cov']:.3f} nX {s['n_ok_X']} np {s['n_pairs']}")
