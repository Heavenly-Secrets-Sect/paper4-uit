"""Shared helpers of the revlag RQ4.4 flag: features, logistic fit, AUROC (no truth in features)."""
import numpy as np

FEATURE_SETS = {
    "S1": ["log1p_rel_width", "log1p_width", "zero_in", "logT", "stated_missing", "stated_reversed", "stated_extra"],
    "S2": ["log1p_rel_width", "log1p_width", "zero_in", "logT", "stated_missing", "stated_reversed", "stated_extra",
           "log1p_width_x_logT", "log1p_rel_width_x_logT"],
}


def design_matrix(rows, name, names_only=False):
    """rows: dict with lo, hi, C_e (module output), T, stated (0 none, 1 extra, 2 missing, 3 reversed)."""
    feats = FEATURE_SETS[name]
    if names_only:
        return list(feats)
    width = rows["hi"] - rows["lo"]
    relw = width / (np.abs(rows["C_e"]) + 1e-9)
    lt = np.log(rows["T"])
    lt_c = lt - np.log(80.0)
    v = {"log1p_rel_width": np.log1p(np.maximum(relw, 0)), "log1p_width": np.log1p(np.maximum(width, 0)),
         "zero_in": ((rows["lo"] <= 0) & (0 <= rows["hi"])).astype(float), "logT": lt,
         "stated_missing": (rows["stated"] == 2).astype(float), "stated_reversed": (rows["stated"] == 3).astype(float),
         "stated_extra": (rows["stated"] == 1).astype(float)}
    v["log1p_width_x_logT"] = v["log1p_width"] * lt_c
    v["log1p_rel_width_x_logT"] = v["log1p_rel_width"] * lt_c
    return np.column_stack([v[f] for f in feats])


def fit_logistic(X, y, l2=1e-3, iters=60):
    w = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(X @ w, -30, 30)))
        g = X.T @ (p - y) + l2 * w
        Hm = (X * (p * (1 - p))[:, None]).T @ X + l2 * np.eye(len(w))
        w -= np.linalg.solve(Hm, g)
    return w


def score(rows, frozen):
    X = design_matrix(rows, frozen["feature_set"])
    Z = (X - np.array(frozen["mu"])) / np.array(frozen["sd"])
    return 1 / (1 + np.exp(-(frozen["weights"][0] + Z @ np.array(frozen["weights"][1:]))))


def auc(s, y, w=None):
    """Mann-Whitney AUROC with average ranks for ties; optional per-row weights."""
    y = np.asarray(y, bool)
    w = np.ones(len(s)) if w is None else w
    u, inv = np.unique(s, return_inverse=True)
    P = np.bincount(inv, weights=w * y, minlength=len(u))
    N = np.bincount(inv, weights=w * ~y, minlength=len(u))
    tp, tn = P.sum(), N.sum()
    if tp == 0 or tn == 0:
        return np.nan
    below = np.cumsum(N) - N
    return float((P * (below + 0.5 * N)).sum() / (tp * tn))
