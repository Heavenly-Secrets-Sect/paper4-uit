"""P4-H8 flag, version 2: pooled over lags 1 to 3, train on the calibration dumps, freeze, evaluate once per lag
(protocol: docs/ext/p4h8_flag_spec_v2.md).

    python p4h8_flag_model_v2.py train
    python p4h8_flag_model_v2.py eval        (after the freeze and after the three test dumps exist)
Cells where the lag's frozen guarantee factor is infinite or above 10 (abstentions) have no defined final interval, so their
pairs are left out of training and evaluation; they are listed in the output.
"""
import argparse
import collections
import hashlib
import json
import math
import pickle
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "experiments/ext/revlag"))
import flaglib  # noqa: E402

D = REPO / "results/ext_p4h8_flag_v2"
OLD = REPO / "experiments/ext/revlag/frozen_flag.json"
MODEL = REPO / "experiments/calibration/p4h8_flag_v2_model.pkl"
FROZEN = REPO / "experiments/calibration/p4h8_flag_v2_frozen.json"
KIND = {"none": 0, "extra": 1, "missing": 2, "reversed": 3}


def load(path, lag):
    d = np.load(path, allow_pickle=True)
    names = [str(x) for x in d["features"]]
    X = d["X"]
    cell = np.array([str(c) for c in d["cell"]])
    fac_all = json.loads((REPO / f"experiments/calibration/p4h8_frozen_lag{lag}.json").read_text())["factors"]
    fac = np.array([fac_all[f"{c}|beta0.1"]["marginal"] for c in cell], dtype=float)
    finite = np.isfinite(fac) & (fac <= 10)
    abst = sorted({c for c, f in zip(cell, finite) if not f})
    col = {n: X[:, i] for i, n in enumerate(names)}
    T = np.round(np.exp(col["logT"])).astype(int)
    mid, half, dist = col["mid"], col["half"], col["dist"]
    f = np.where(finite, fac, 1.0)
    lo, hi = mid - f * half, mid + f * half
    y = (dist > f * half).astype(int)
    kind = np.array([KIND[c.split("|")[2]] for c in cell])
    base = [n for n in names if n != "dist"]
    feats = np.column_stack([col[n] for n in base] + [hi - lo, np.log1p((hi - lo) / (np.abs(mid) + 1e-9)),
                                                        ((lo <= 0) & (0 <= hi)).astype(float), f])
    fnames = base + ["final_width", "log1p_final_relwidth", "zero_in_final", "factor"]
    kcol = {0: np.zeros(len(y)), 1: col["k_extra"], 2: col["k_miss"], 3: col["k_rev"]}
    kk = np.array([kcol[k][i] for i, k in enumerate(kind)])
    # damage level inside (topology, T, kind): lower stated count = rate 0.2, higher = rate 0.5
    g = d["group"]
    ks = collections.defaultdict(set)
    for i in range(len(y)):
        ks[(g[i], T[i], kind[i])].add(kk[i])
    level = np.empty(len(y), dtype=object)
    for i in range(len(y)):
        s = sorted(ks[(g[i], T[i], kind[i])])
        level[i] = "-" if kind[i] == 0 else ("low" if kk[i] == s[0] else "high")
    rows = {"lo": lo, "hi": hi, "C_e": mid, "T": T.astype(float), "stated": kind}
    return {"X": feats, "fn": fnames, "y": y, "g": g, "T": T, "kind": kind, "level": level, "keep": finite,
            "width": hi - lo, "rows": rows, "abstain_cells": abst}


def fit(kind, par, X, y):
    if kind == "logit":
        sc = StandardScaler().fit(X)
        return (kind, sc, LogisticRegression(C=par["C"], max_iter=500).fit(sc.transform(X), y))
    return (kind, None, HistGradientBoostingClassifier(max_depth=par["max_depth"], learning_rate=par["learning_rate"],
                                                       max_iter=200, random_state=0).fit(X, y))


def predict(m, X):
    kind, sc, clf = m
    return clf.predict_proba(sc.transform(X) if sc is not None else X)[:, 1]


def old_scores(rows):
    return flaglib.score(rows, json.loads(OLD.read_text()))


def cluster_boot(score_list, y, g, sel, n_boot=1000, seed=0):
    rng = np.random.default_rng(seed)
    ug = np.unique(g[sel])
    idx = {u: np.where(sel & (g == u))[0] for u in ug}
    out = []
    for _ in range(n_boot):
        ii = np.concatenate([idx[u] for u in rng.choice(ug, len(ug))])
        out.append([flaglib.auc(s[ii], y[ii]) for s in score_list])
    return np.array(out)


def train():
    parts = {k: load(D / f"lag{k}_calibration.npz", k) for k in (1, 2, 3)}
    X = np.vstack([p["X"][p["keep"]] for p in parts.values()])
    y = np.concatenate([p["y"][p["keep"]] for p in parts.values()])
    g = np.concatenate([p["g"][p["keep"]] for p in parts.values()])
    fn = parts[1]["fn"]
    rng = np.random.default_rng(0)
    ug = np.unique(g)
    sub = np.isin(g, rng.choice(ug, int(0.4 * len(ug)), replace=False))
    grid = [("logit", {"C": 1.0}), ("gbm", {"max_depth": 3, "learning_rate": 0.1}), ("gbm", {"max_depth": 5, "learning_rate": 0.05}),
            ("gbm", {"max_depth": 5, "learning_rate": 0.1})]
    res, best = [], None
    gkf = GroupKFold(n_splits=5)
    for kind, par in grid:
        aucs = []
        for tr, va in gkf.split(X[sub], y[sub], g[sub]):
            m = fit(kind, par, X[sub][tr], y[sub][tr])
            aucs.append(flaglib.auc(predict(m, X[sub][va]), y[sub][va]))
        res.append((kind, par, float(np.mean(aucs))))
        if best is None or res[-1][2] > best[2]:
            best = res[-1]
        print(res[-1], flush=True)
    m = fit(best[0], best[1], X, y)
    MODEL.write_bytes(pickle.dumps({"model": m, "features": fn}))
    meta = {"_note": "P4-H8 flag v2 (docs/ext/p4h8_flag_spec_v2.md); fitted on the calibration dumps of lags 1-3 only.",
            "selected": {"kind": best[0], "params": best[1], "cv_auroc_on_40pct_sample": best[2]}, "cv_all": res, "features": fn,
            "model_sha256": hashlib.sha256(MODEL.read_bytes()).hexdigest(), "n_pairs_train": int(len(y)),
            "miss_rate_train": float(y.mean()), "abstain_cells": {str(k): p["abstain_cells"] for k, p in parts.items()}}
    des = {}
    for k in (1, 2, 3):
        p = load(D / f"lag{k}_design.npz", k)
        kp = p["keep"]
        des[k] = {"new": flaglib.auc(predict(m, p["X"][kp]), p["y"][kp]), "old": flaglib.auc(old_scores({a: b[kp] for a, b in p["rows"].items()}), p["y"][kp]),
                  "neg_width": flaglib.auc(-p["width"][kp], p["y"][kp])}
    meta["design_auroc"] = des
    FROZEN.write_text(json.dumps(meta, indent=2))
    print(json.dumps({"selected": meta["selected"], "design_auroc": des}, indent=2))


def evaluate():
    pk = pickle.loads(MODEL.read_bytes())
    meta = json.loads(FROZEN.read_text())
    assert hashlib.sha256(MODEL.read_bytes()).hexdigest() == meta["model_sha256"], "model changed after the freeze"
    tests = {1: D / "lag1_test.npz", 2: D / "lag2_test.npz", 3: D / "lag3_test.npz"}
    lines, rec = [], {}
    kname = {0: "none", 1: "extra", 2: "missing", 3: "reversed"}
    for lag, path in tests.items():
        p = load(path, lag)
        kp = p["keep"]
        X, y, g, T, kind, level = p["X"][kp], p["y"][kp], p["g"][kp], p["T"][kp], p["kind"][kp], p["level"][kp]
        rows = {a: b[kp] for a, b in p["rows"].items()}
        sn, so, sw = predict(pk["model"], X), old_scores(rows), -p["width"][kp]
        lines += [f"\n## Lag {lag} (pairs {len(y)}, miss rate {y.mean():.3f}; abstaining cells left out: {', '.join(p['abstain_cells']) or 'none'})\n",
                  "T group criterion (new minus old flag, 95% topology cluster bootstrap):\n",
                  "| T group | pairs | AUROC new | AUROC old | AUROC -width | new - old [95% CI] | criterion (+0.03, CI above 0) |", "|---|---|---|---|---|---|---|"]
        groups = {"T 19-30": (T <= 30), "T 40": (T == 40), "T 80-150": (T >= 80)}
        ok_all = []
        for nm, sel in groups.items():
            if sel.sum() == 0:
                continue
            a_new, a_old, a_w = (flaglib.auc(s[sel], y[sel]) for s in (sn, so, sw))
            bs = cluster_boot([sn, so], y, g, sel)
            diff = bs[:, 0] - bs[:, 1]
            lo, hi = np.nanpercentile(diff, [2.5, 97.5])
            ok = (a_new - a_old) >= 0.03 and lo > 0
            ok_all.append(ok)
            rec[f"lag{lag}|{nm}"] = {"new": a_new, "old": a_old, "neg_width": a_w, "diff": a_new - a_old, "ci": [lo, hi], "ok": bool(ok)}
            lines.append(f"| {nm} | {sel.sum()} | {a_new:.3f} | {a_old:.3f} | {a_w:.3f} | {a_new - a_old:+.3f} [{lo:+.3f}, {hi:+.3f}] | {'met' if ok else 'not met'} |")
        lines.append(f"\nCriterion at lag {lag}: {'MET' if all(ok_all) else 'NOT MET'}.\n")
        lines += ["Per scenario (AUROC new / old; pairs; miss rate):\n", "| T | kind | level | pairs | miss % | new | old |", "|---|---|---|---|---|---|---|"]
        for t in sorted(set(T)):
            for k in (0, 1, 2, 3):
                for lv in (["-"] if k == 0 else ["low", "high"]):
                    m = (T == t) & (kind == k) & (level == lv)
                    if m.sum() < 200 or y[m].sum() < 20 or y[m].sum() == m.sum():
                        if m.sum():
                            lines.append(f"| {t} | {kname[k]} | {lv} | {m.sum()} | {100 * y[m].mean():.1f} | too few missed pairs | |")
                        continue
                    rec[f"lag{lag}|{t}|{kname[k]}|{lv}"] = {"new": flaglib.auc(sn[m], y[m]), "old": flaglib.auc(so[m], y[m])}
                    lines.append(f"| {t} | {kname[k]} | {lv} | {m.sum()} | {100 * y[m].mean():.1f} | {rec[f'lag{lag}|{t}|{kname[k]}|{lv}']['new']:.3f} | {rec[f'lag{lag}|{t}|{kname[k]}|{lv}']['old']:.3f} |")
    out = D / "test_eval_v2"
    out.with_suffix(".md").write_text("\n".join(lines) + "\n")
    out.with_suffix(".json").write_text(json.dumps(rec, indent=2))
    print("\n".join(lines))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["train", "eval"])
    a = ap.parse_args()
    train() if a.mode == "train" else evaluate()
