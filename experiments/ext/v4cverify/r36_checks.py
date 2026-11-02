"""R3-7 / R3-6 helper: (1) v5/v4 IS ratio range on non-missing cells of results/ext_narrow_eval
(the 0.987 vs 0.985 wording in v4c.md); (2) eiv2 condition-1 Holm count (cov > 0.90 significant),
recomputed with my own code from results/ext_eiv2_eval/runs.jsonl (cluster bootstrap by topology,
B = 2000, default_rng(0) as pre-registered in eiv2.md, plus seeds 1..4).
Writes results/ext_v4cverify_recompute/r36_checks.txt."""
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
R = Path(__file__).resolve().parents[3] / "results"
L = []
# (1)
d = defaultdict(dict)
for l in open(R / "ext_narrow_eval/runs.jsonl"):
    r = json.loads(l)
    if r["kind"] == "missing" or r["status"] != "ok":
        continue
    d[(r["T"], r["kind"], r["rate"])].setdefault(r["method"], []).append(r["iscore_nonnull_mean"])
rat = {k: np.mean(v["tolerant_v5"]) / np.mean(v["tolerant_v4"]) for k, v in d.items()}
kmin = min(rat, key=rat.get); kmax = max(rat, key=rat.get)
L.append(f"narrow_eval v5/v4 IS ratio, non-missing cells ({len(rat)}): min {rat[kmin]:.4f} at {kmin}, max {rat[kmax]:.4f} at {kmax}")
# (2)
rows = [json.loads(l) for l in open(R / "ext_eiv2_eval/runs.jsonl")]
rows = [r for r in rows if r["method"] == "tolerant_eiv2" and r["scenario"] in ("noise0.1", "noise0.3")]
topos = sorted({r["topology"] for r in rows})
ti = {t: i for i, t in enumerate(topos)}
cells = sorted({(r["scenario"], r["T"], r["kind"]) for r in rows})
for seed in (0, 1, 2, 3, 4):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(topos), size=(2000, len(topos)))
    ps, covs, plo = [], [], []
    for c in cells:
        cov_n = np.zeros(len(topos)); n = np.zeros(len(topos))
        for r in rows:
            if (r["scenario"], r["T"], r["kind"]) == c:
                cov_n[ti[r["topology"]]] += r["n_covered_nonnull"]; n[ti[r["topology"]]] += r["n_nonnull"]
        covs.append(cov_n.sum() / n.sum())
        b = cov_n[idx].sum(1) / n[idx].sum(1)
        ps.append(np.mean(b <= 0.90)); plo.append(np.mean(b >= 0.90))
    def holm(p, a=0.05):
        o = np.argsort(p); k = 0
        for j, i in enumerate(o):
            if p[i] <= a / (len(p) - j): k += 1
            else: break
        return k
    above_noise03 = None
    L.append(f"eiv2 seed {seed}: pass(point) {sum(c >= 0.90 for c in covs)}/12; Holm above 0.90: {holm(ps)}/12; "
             f"Holm below 0.90: {holm(plo)}/12; unadjusted above {sum(p <= 0.05 for p in ps)}")
    if seed == 0:
        o = np.argsort(ps); rej = set()
        for j, i in enumerate(o):
            if ps[i] <= 0.05 / (12 - j): rej.add(i)
            else: break
        L.append("  Holm-above cells (seed 0): " + ", ".join(f"{cells[i][0]} T{cells[i][1]} {cells[i][2]}" for i in sorted(rej)))
(R / "ext_v4cverify_recompute/r36_checks.txt").write_text("\n".join(L) + "\n")
print("\n".join(L))
