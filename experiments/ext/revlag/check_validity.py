"""Validity condition of ext_revlag_lag (docs/ext/revlag.md, "Điều kiện hợp lệ"): the oracle and
tolerant_v4 rows must equal the round-1 rows of results/ext_metrics_pairs/pairs.npz exactly
(C_e, lo, hi of every non-null pair). Writes results/ext_revlag_lag/validity.txt."""
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
a = dict(np.load(ROOT / "results/ext_metrics_pairs/pairs.npz"))
b = dict(np.load(ROOT / "results/ext_revlag_lag/pairs.npz"))
ma, mb = [str(m) for m in a["methods"]], [str(m) for m in b["methods"]]
key = ("topo", "rep", "T", "cell", "j", "i")
lines, ok_all = [], True
for name in ("oracle", "tolerant_v4"):
    sa = a["method"] == ma.index(name)
    sb = b["method"] == mb.index(name)
    ka = np.stack([a[k][sa] for k in key], 1)
    kb = np.stack([b[k][sb] for k in key], 1)
    oa = np.lexsort(ka.T[::-1]); ob = np.lexsort(kb.T[::-1])
    same_keys = ka.shape == kb.shape and np.array_equal(ka[oa], kb[ob])
    mism = -1
    if same_keys:
        diff = np.zeros(len(oa), bool)
        for f in ("C_e", "lo", "hi", "C_t"):
            diff |= a[f][sa][oa] != b[f][sb][ob]
        mism = int(diff.sum())
    ok = same_keys and mism == 0
    ok_all &= ok
    lines.append(f"{name}: round1 rows {sa.sum()}, round2 rows {sb.sum()}, same keys {same_keys}, "
                 f"rows with any C_e/lo/hi/C_t difference {mism} -> {'IDENTICAL' if ok else 'MISMATCH'}")
lines.append(f"VALID: {ok_all}")
(ROOT / "results/ext_revlag_lag/validity.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
