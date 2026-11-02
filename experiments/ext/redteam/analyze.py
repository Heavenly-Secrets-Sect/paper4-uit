"""Red team: analysis of E3 (results/ext_redteam_calbase), P1 and P2 (out/*.npz)."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
from paper4.metrics import interval_score

def e3():
    rows = [json.loads(l) for l in open(ROOT / "results/ext_redteam_calbase/runs.jsonl")]
    cal = json.loads((ROOT / "results/ext_redteam_calbase/calibration.json").read_text())
    print("calibration factors:", {k: v for k, v in cal.items() if "|" in k and not k[0].isdigit()})
    ok = [r for r in rows if r["status"] == "ok"]
    fails = defaultdict(int)
    for r in rows:
        if r["status"] != "ok": fails[(r["method"], r["T"], r["status"])] += 1
    print("failures:", dict(fails))
    g = defaultdict(list)
    for r in ok: g[(r["T"], r["kind"], r["rate"], r["method"])].append(r)
    idx = {(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"], r["method"]): r["iscore_nonnull_mean"] for r in ok}
    rng = np.random.default_rng(0)
    meths = ["plugin", "tolerant_v4", "pselect_cal", "bvar_cal", "ida_cal", "fullvar_cal"]
    for T in (40, 80, 150):
        for kind, rate in [("none", 0.0), ("extra", 0.2), ("extra", 0.5), ("missing", 0.2), ("missing", 0.5), ("reversed", 0.2), ("reversed", 0.5)]:
            parts = []
            for m in meths:
                gm = g[(T, kind, rate, m)]
                if not gm: parts.append(f"{m} -"); continue
                cov = sum(r["n_covered_nonnull"] for r in gm) / sum(r["n_nonnull"] for r in gm)
                isc = np.mean([r["iscore_nonnull_mean"] for r in gm])
                w = np.median([r["width_kept"] for r in gm if r.get("width_kept") is not None])
                s = f"{m} {cov:.3f}/{isc:.2f}/w{w:.2f}"
                if m not in ("tolerant_v4",):
                    by = defaultdict(list)
                    for (t, rep, TT, k, ra, mm), v in idx.items():
                        if mm == "tolerant_v4" and TT == T and k == kind and ra == rate and (t, rep, TT, k, ra, m) in idx:
                            by[t].append(v - idx[(t, rep, TT, k, ra, m)])
                    topos = list(by)
                    est = np.mean([d for t in topos for d in by[t]])
                    boots = [np.mean([d for i in rng.choice(len(topos), len(topos)) for d in by[topos[i]]]) for _ in range(2000)]
                    lo, hi = np.quantile(boots, [0.025, 0.975])
                    s += f" dIS(v4-{m}) {est:+.2f} [{lo:+.2f},{hi:+.2f}]"
                parts.append(s)
            print(f"T={T} {kind}-{rate}: " + " | ".join(parts))
    # reproducibility: tolerant_v4 rows vs a2b_pselect
    A = {}
    for l in open(ROOT / "results/a2b_pselect/runs.jsonl"):
        r = json.loads(l)
        if r["method"] == "tolerant_v4": A[(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])] = r
    same = diff = 0
    for r in rows:
        if r["method"] == "tolerant_v4":
            a = A[(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])]
            if a.get("iscore_nonnull_mean") == r.get("iscore_nonnull_mean") and a.get("n_covered_nonnull") == r.get("n_covered_nonnull"): same += 1
            else: diff += 1
    print(f"tolerant_v4 rows identical to a2b_pselect: {same}, differing: {diff}")

def p1():
    R = np.load(HERE / "out/p1.npz")["recs"]
    M = ["plugin", "tolerant_v4", "bvar_minnesota", "pselect_union"]
    CELLS = {3: "missing-0.2", 4: "missing-0.5", 5: "reversed-0.2", 6: "reversed-0.5"}
    ins = (R[:, 7] <= R[:, 6]) & (R[:, 6] <= R[:, 8])
    isc = interval_score(R[:, 7], R[:, 8], R[:, 6])
    wid = R[:, 8] - R[:, 7]
    print("P1 pair-level: coverage / mean IS / median width / n pairs, by category (affected | unaffected non-null | null)")
    for T in (40, 80, 150):
        for c, lab in CELLS.items():
            parts = []
            for mi, m in enumerate(M):
                sel = (R[:, 2] == T) & (R[:, 3] == c) & (R[:, 4] == mi)
                s = []
                for cat in (2, 1, 0):
                    k = sel & (R[:, 5] == cat)
                    s.append(f"{ins[k].mean():.3f}/{isc[k].mean():.2f}/{np.median(wid[k]):.2f}/n{k.sum()}" if k.any() else "-")
                parts.append(f"{m}: " + " | ".join(s))
            print(f"T={T} {lab}\n   " + "\n   ".join(parts))

def p2():
    R = np.load(HERE / "out/p2.npz")["recs"]
    M = ["tolerant_v3", "pselect_union"]
    kinds = {"none": [0], "missing": [3, 4], "reversed": [5, 6]}
    grid = np.round(np.arange(0.5, 1.51, 0.1), 2)
    print("P2 (D-07H development, calibration seeds): pooled non-null coverage vs width factor c")
    for mi, m in enumerate(M):
        for T in (40, 80, 150):
            for kind, cs in kinds.items():
                sel = (R[:, 2] == T) & np.isin(R[:, 3], cs) & (R[:, 4] == mi) & (R[:, 5] > 0)
                mid, half = (R[sel, 7] + R[sel, 8]) / 2, (R[sel, 8] - R[sel, 7]) / 2
                dist = np.abs(R[sel, 6] - mid)
                cov = np.array([(dist <= c * half).mean() for c in grid])
                target = min(0.95, cov.max() - 0.005)
                cstar = grid[np.argmax(cov >= target)] if (cov >= target).any() else None
                print(f"{m} T={T} {kind}: c* (grid from 0.5) = {cstar}; cov at c=0.5..1.5: " + " ".join(f"{v:.3f}" for v in cov))

if __name__ == "__main__":
    {"e3": e3, "p1": p1, "p2": p2}[sys.argv[1]]()
