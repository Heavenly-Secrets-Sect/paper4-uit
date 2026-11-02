"""Validity checks of the revlag3 D-07 runs (pre-registered in docs/ext/revlag3.md):
1. oracle / tolerant_v4 rows equal (C_e, lo, hi, C_t; exact) to results/ext_revlag_lag/pairs.npz on the same keys.
2. tolerant_auto3 per-run pooled coverage counts and mean interval score equal results/ext_gate_auto3/runs.jsonl;
   tolerant_v5_1 equal results/ext_v51_eval/runs.jsonl (|diff| <= 1e-9).
Run:  python experiments/ext/revlag3/check3.py --run ext_revlag3_rev|ext_revlag3_flag
Writes results/<run>/validity.txt.
"""
import argparse, json
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
KEY = ("topo", "rep", "scen", "T", "cell", "j", "i")
TAU = 0.1


def npz(run):
    z = np.load(ROOT / "results" / run / "pairs.npz")
    return {k: z[k] for k in z.files}


def rows_of(d, method):
    ms = [str(m) for m in d["methods"]]
    if method not in ms:
        return None
    s = d["method"] == ms.index(method)
    return {k: d[k][s] for k in KEY + ("C_e", "lo", "hi", "C_t")}


def keyed(r):
    k = np.stack([r[c] for c in KEY], 1)
    o = np.lexsort(k.T[::-1])
    return k[o], {c: r[c][o] for c in ("C_e", "lo", "hi", "C_t")}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", required=True); a = ap.parse_args()
    d = npz(a.run); ref = npz("ext_revlag_lag")
    cells = [str(c) for c in d["cells"]]
    L = [f"# validity of {a.run}"]
    for m in ("oracle", "tolerant_v4"):
        r = rows_of(d, m)
        if r is None:
            continue
        q = rows_of(ref, m)
        cset = np.unique(r["cell"])
        q = {k: v[np.isin(q["cell"], cset)] for k, v in q.items()}
        k1, v1 = keyed(r); k2, v2 = keyed(q)
        same_keys = k1.shape == k2.shape and bool((k1 == k2).all())
        ndiff = int(sum((~((v1[c] == v2[c]) | (np.isnan(v1[c]) & np.isnan(v2[c])))).sum() for c in v1)) if same_keys else -1
        L.append(f"{m}: rows {len(k1)} vs ext_revlag_lag {len(k2)}; same keys {same_keys}; differing values {ndiff}")
    man = json.loads((ROOT / "results" / a.run / "manifest.json").read_text())
    topo_ids = [t["id"] for t in man["topologies"]]
    for m, refrun in (("tolerant_auto3", "ext_gate_auto3"), ("tolerant_v5_1", "ext_v51_eval")):
        r = rows_of(d, m)
        if r is None:
            continue
        mine = defaultdict(lambda: [0, 0])
        cov = (r["lo"] <= r["C_t"]) & (r["C_t"] <= r["hi"])
        for t, rep, T, c, cv in zip(r["topo"].astype(int), r["rep"].astype(int), r["T"].astype(int), r["cell"].astype(int), cov):
            kind, rate = cells[c].split("|")
            key = (topo_ids[t], rep, T, kind, float(rate))
            mine[key][0] += int(cv); mine[key][1] += 1
        theirs = {}
        for line in open(ROOT / "results" / refrun / "runs.jsonl"):
            x = json.loads(line)
            if x["method"] == m and x.get("scenario", "clean") == "clean" and x["kind"] != "ges" and x["status"] == "ok":
                theirs[(x["topology"], x["replicate"], x["T"], x["kind"], float(x["rate"]))] = (x["n_covered_nonnull"], x["n_nonnull"])
        common = set(mine) & set(theirs)
        nd = sum(1 for k in common if tuple(mine[k]) != tuple(theirs[k]))
        L.append(f"{m}: runs here {len(mine)}, in {refrun} {len(theirs)}, common {len(common)}, "
                 f"runs with different (covered, n_nonnull): {nd}")
    fails = [s for s in man["status_counts"] if s["status"] != "ok"]
    L.append(f"failed runs (status != ok): {fails if fails else 'none'}")
    L.append(f"method modules: {man['method_modules']}; python {man['python']}; numpy {man['numpy']}; workers {man['workers']}; seconds {man['seconds']}")
    (ROOT / "results" / a.run / "validity.txt").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
