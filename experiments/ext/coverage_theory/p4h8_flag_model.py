"""P4-H8 flag: train on the calibration dump, freeze, evaluate once on the test dump (protocol: docs/ext/p4h8_flag_spec.md).

    python p4h8_flag_model.py train  --calibration results/ext_p4h8_flag/calibration.npz --design results/ext_p4h8_flag/design.npz
    python p4h8_flag_model.py eval   --test results/ext_p4h8_flag/test.npz          (after freezing and after the test dump)
"""
import argparse
import hashlib
import json
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

FROZEN_FACTORS = REPO / "experiments/calibration/p4h8_frozen_lag1.json"
FROZEN_FLAG = REPO / "experiments/calibration/p4h8_flag_frozen.json"
MODEL = REPO / "experiments/calibration/p4h8_flag_model.pkl"
OLD = REPO / "experiments/ext/revlag/frozen_flag.json"
KIND = {"none": 0, "extra": 1, "missing": 2, "reversed": 3}


def load(path):
    d = np.load(path, allow_pickle=True)
    names = [str(x) for x in d["features"]]
    X = d["X"]
    cell = np.array([str(c) for c in d["cell"]])
    fac_all = json.loads(FROZEN_FACTORS.read_text())["factors"]
    fac = np.array([fac_all[f"{c}|beta0.1"]["marginal"] for c in cell], dtype=float)
    col = {n: X[:, i] for i, n in enumerate(names)}
    T = np.exp(col["logT"])
    mid, half, dist = col["mid"], col["half"], col["dist"]
    lo, hi = mid - fac * half, mid + fac * half
    y = (dist > fac * half).astype(int)
    kind = np.array([KIND[c.split("|")[2]] for c in cell])
    final = {"mid": mid, "lo": lo, "hi": hi, "width": hi - lo, "T": np.round(T), "kind": kind, "fac": fac}
    feats = np.column_stack([col[n] for n in names if n != "dist"] + [hi - lo, np.log1p((hi - lo) / (np.abs(mid) + 1e-9)),
                                                                         ((lo <= 0) & (0 <= hi)).astype(float), fac])
    fnames = [n for n in names if n != "dist"] + ["final_width", "log1p_final_relwidth", "zero_in_final", "factor"]
    return feats, fnames, y, d["group"], final


def old_scores(final):
    rows = {"lo": final["lo"], "hi": final["hi"], "C_e": final["mid"], "T": final["T"], "stated": final["kind"]}
    return flaglib.score(rows, json.loads(OLD.read_text()))


def cv_select(X, y, g):
    gkf = GroupKFold(n_splits=5)
    grid = [("logit", {"C": c}) for c in (0.01, 0.1, 1.0)] + [("gbm", {"max_depth": d, "learning_rate": lr})
                                                             for d in (3, 5) for lr in (0.05, 0.1)]
    best, res = None, []
    for kind, par in grid:
        aucs = []
        for tr, va in gkf.split(X, y, g):
            m = fit(kind, par, X[tr], y[tr])
            aucs.append(flaglib.auc(predict(m, X[va]), y[va]))
        res.append((kind, par, float(np.mean(aucs))))
        if best is None or res[-1][2] > best[2]:
            best = res[-1]
    return best, res


def fit(kind, par, X, y):
    if kind == "logit":
        sc = StandardScaler().fit(X)
        return (kind, sc, LogisticRegression(C=par["C"], max_iter=500).fit(sc.transform(X), y))
    return (kind, None, HistGradientBoostingClassifier(max_depth=par["max_depth"], learning_rate=par["learning_rate"],
                                                       max_iter=200, random_state=0).fit(X, y))


def predict(m, X):
    kind, sc, clf = m
    return clf.predict_proba(sc.transform(X) if sc is not None else X)[:, 1]


def groups_T(T):
    return np.where(T <= 30, 0, np.where(T == 40, 1, 2))


def boot_auc(score, y, g, groupsel, n_boot=1000, seed=0):
    rng = np.random.default_rng(seed)
    ug = np.unique(g)
    idx = {u: np.where(g == u)[0] for u in ug}
    out = []
    for _ in range(n_boot):
        pick = rng.choice(ug, len(ug))
        ii = np.concatenate([idx[u] for u in pick])
        out.append([flaglib.auc(s[ii][groupsel[ii]], y[ii][groupsel[ii]]) for s in score])
    return np.array(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["train", "eval"])
    ap.add_argument("--calibration")
    ap.add_argument("--design")
    ap.add_argument("--test")
    a = ap.parse_args()
    if a.mode == "train":
        X, fn, y, g, final = load(a.calibration)
        best, res = cv_select(X, y, g)
        m = fit(best[0], best[1], X, y)
        MODEL.write_bytes(pickle.dumps({"model": m, "features": fn}))
        out = {"_note": "P4-H8 frozen flag (docs/ext/p4h8_flag_spec.md); fitted on the calibration dump only.",
               "selected": {"kind": best[0], "params": best[1], "cv_auroc": best[2]}, "cv_all": res, "features": fn,
               "model_sha256": hashlib.sha256(MODEL.read_bytes()).hexdigest(), "n_pairs_train": int(len(y)),
               "miss_rate_train": float(y.mean())}
        if a.design:
            Xd, _, yd, gd, fd = load(a.design)
            out["design_auroc"] = {"new": flaglib.auc(predict(m, Xd), yd), "old": flaglib.auc(old_scores(fd), yd),
                                   "neg_width": flaglib.auc(-fd["width"], yd)}
        FROZEN_FLAG.write_text(json.dumps(out, indent=2))
        print(json.dumps({k: out[k] for k in ("selected", "design_auroc") if k in out}, indent=2))
        return
    pk = pickle.loads(MODEL.read_bytes())
    meta = json.loads(FROZEN_FLAG.read_text())
    assert hashlib.sha256(MODEL.read_bytes()).hexdigest() == meta["model_sha256"], "model changed after the freeze"
    X, fn, y, g, final = load(a.test)
    assert fn == pk["features"]
    scores = {"new": predict(pk["model"], X), "old": old_scores(final), "neg_width": -final["width"],
              "neg_relwidth": -np.log1p(final["width"] / (np.abs(final["mid"]) + 1e-9))}
    gT = groups_T(final["T"])
    names = ["all", "T 19-30", "T 40", "T 80-150"]
    sel = [np.ones(len(y), bool)] + [gT == k for k in range(3)]
    lines = ["| T group | pairs | miss rate | AUROC new | AUROC old flag | AUROC -width | AUROC -relwidth | new - old [95% CI] | lift top decile (new) |",
             "|---|---|---|---|---|---|---|---|---|"]
    rec = {}
    for nm, s in zip(names, sel):
        a_ = {k: flaglib.auc(v[s], y[s]) for k, v in scores.items()}
        bs = boot_auc([scores["new"], scores["old"]], y, g, s)
        diff = bs[:, 0] - bs[:, 1]
        lo, hi = np.nanpercentile(diff, [2.5, 97.5])
        thr = np.quantile(scores["new"][s], 0.9)
        lift = y[s][scores["new"][s] >= thr].mean() / y[s].mean()
        rec[nm] = {"auroc": a_, "diff": float(a_["new"] - a_["old"]), "diff_ci": [float(lo), float(hi)], "lift": float(lift)}
        lines.append(f"| {nm} | {s.sum()} | {y[s].mean():.3f} | {a_['new']:.3f} | {a_['old']:.3f} | {a_['neg_width']:.3f} | "
                     f"{a_['neg_relwidth']:.3f} | {a_['new'] - a_['old']:+.3f} [{lo:+.3f}, {hi:+.3f}] | {lift:.2f} |")
    ok = all(rec[k]["diff"] >= 0.03 and rec[k]["diff_ci"][0] > 0 for k in names[1:])
    lines.append(f"\nCriterion (+0.03 AUROC with CI above 0 in each T group): {'MET' if ok else 'NOT MET'}.")
    out = REPO / "results/ext_p4h8_flag/test_eval"
    out.with_suffix(".md").write_text("\n".join(lines) + "\n")
    out.with_suffix(".json").write_text(json.dumps(rec, indent=2))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
