"""R2-7 design step: choose and freeze the combined RQ4.4 flag on round-1 D-07 rows ONLY
(results/ext_metrics_pairs/pairs.npz, module tolerant_v4, seed_base 20261102). No new data.

Candidate feature sets (all observable: the module's own interval, its point estimate, T and the
stated damage kind):
  S1: log1p(rel_width), log1p(width), zero_in, log T, stated kind dummies (missing, reversed, extra)
  S2: S1 + log1p(width) * (log T - log 80) + log1p(rel_width) * (log T - log 80)
Selection: grouped 5-fold CV by topology (fold = topology index mod 5, as in round 1); criterion =
out-of-fold AUROC for `miss` on T in {80, 150} (round-1 primary set), tie (< 0.005) -> simpler set.
The chosen set is refitted on ALL round-1 rows (T 40/80/150 pooled) and frozen with its
standardisation in experiments/ext/revlag/frozen_flag.json, together with the binary threshold
p_hat > 0.10 (predicted miss probability above twice the nominal 0.05; fixed a priori, not tuned).

Run: python experiments/ext/revlag/flag_design.py
Writes experiments/ext/revlag/frozen_flag.json and results/ext_revlag_flagdesign/design.md
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from flaglib import FEATURE_SETS, auc, design_matrix, fit_logistic  # noqa: E402

z = np.load(ROOT / "results/ext_metrics_pairs/pairs.npz")
d = {k: z[k] for k in z.files}
methods = [str(m) for m in d["methods"]]
cells = [str(c) for c in d["cells"]]
mod = d["method"] == methods.index("tolerant_v4")
KC = {"none": 0, "extra": 1, "missing": 2, "reversed": 3}
stated = np.array([KC[c.split("|")[0]] for c in cells])[d["cell"].astype(int)]
rows = {"lo": d["lo"][mod], "hi": d["hi"][mod], "C_e": d["C_e"][mod], "T": d["T"][mod], "stated": stated[mod]}
y = ~((d["lo"] <= d["C_t"]) & (d["C_t"] <= d["hi"]))[mod]
topo = d["topo"][mod].astype(int)
fold = topo % 5
lines = ["# R2-7 design: combined flag chosen on round-1 D-07 rows (ext_metrics_pairs, tolerant_v4)", "",
         f"Rows: {mod.sum()} non-null pairs; miss base rate {y.mean():.4f}.", "",
         "| feature set | OOF AUROC T80/150 | OOF AUROC T40 | OOF AUROC all |", "|---|---|---|---|"]
res = {}
for name in FEATURE_SETS:
    X = design_matrix(rows, name)
    oof = np.zeros(len(y))
    for k in range(5):
        tr, te = fold != k, fold == k
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9
        w = fit_logistic(np.column_stack([np.ones(tr.sum()), (X[tr] - mu) / sd]), y[tr].astype(float))
        oof[te] = np.column_stack([np.ones(te.sum()), (X[te] - mu) / sd]) @ w
    a_hi = auc(oof[rows["T"] >= 80], y[rows["T"] >= 80])
    a_40 = auc(oof[rows["T"] == 40], y[rows["T"] == 40])
    res[name] = a_hi
    lines.append(f"| {name} | {a_hi:.4f} | {a_40:.4f} | {auc(oof, y):.4f} |")
best = "S1" if res["S2"] - res["S1"] < 0.005 else "S2"
X = design_matrix(rows, best)
mu, sd = X.mean(0), X.std(0) + 1e-9
w = fit_logistic(np.column_stack([np.ones(len(y)), (X - mu) / sd]), y.astype(float))
p = 1 / (1 + np.exp(-(np.column_stack([np.ones(len(y)), (X - mu) / sd]) @ w)))
flag = p > 0.10
lines += ["", f"Chosen: **{best}** (rule: S2 only if it beats S1 by >= 0.005 on T80/150 OOF AUROC).", "",
          "In-sample check of the frozen threshold p_hat > 0.10 (training rows, not an evaluation):"]
for lab, s in (("T80/150", rows["T"] >= 80), ("T40", rows["T"] == 40)):
    f = flag[s]
    lines.append(f"- {lab}: flagged {f.mean():.3f}; miss rate flagged {y[s][f].mean():.3f}, unflagged "
                 f"{y[s][~f].mean():.3f}")
frozen = {"_note": "Frozen RQ4.4 combined flag (R2-7, ID revlag). Fitted on round-1 D-07 development rows "
                   "(results/ext_metrics_pairs/pairs.npz, tolerant_v4, all T). Score = logistic(intercept + "
                   "sum w_k (x_k - mu_k) / sd_k). Binary flag: p_hat > threshold. Do not refit.",
          "feature_set": best, "features": design_matrix(rows, best, names_only=True), "mu": mu.tolist(),
          "sd": sd.tolist(), "weights": w.tolist(), "threshold": 0.10, "train_rows": int(len(y)),
          "train_oof_auc_T80_150": res[best]}
(Path(__file__).resolve().parent / "frozen_flag.json").write_text(json.dumps(frozen, indent=2))
lines += ["", "Frozen weights (standardised): " + ", ".join(
    f"{n} {v:+.3f}" for n, v in zip(["intercept"] + frozen["features"], w))]
out = ROOT / "results/ext_revlag_flagdesign"
out.mkdir(parents=True, exist_ok=True)
(out / "design.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
