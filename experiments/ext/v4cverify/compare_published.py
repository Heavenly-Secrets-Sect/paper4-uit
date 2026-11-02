"""R3-7: compare my recompute (results/ext_v4cverify_recompute/recompute.json) with analyze.py's
results/ext_v4c_eval/analysis.json cell by cell. Writes results/ext_v4cverify_recompute/compare_published.txt."""
import json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
R = ROOT / "results"
mine = json.loads((R / "ext_v4cverify_recompute/recompute.json").read_text())
pub = json.loads((R / "ext_v4c_eval/analysis.json").read_text())
L = []
def nm(T, k, r): return f"T{T} {k}" if k == "none" else f"T{T} {k}-{r}"
# part B cells
dest, dci, cls_mis, holm_mis, dp = [], [], [], [], []
for key, s in pub["partB"].items():
    c, X, T, k, r = key.split("|")
    m = next(x for x in mine["partB_cells"][f"({c}) {X}"] if x["cell"] == nm(int(T), k, float(r)))
    dest.append(abs(m["diff"] - s["diff"]["est"]))
    dci.append(max(abs(m["ci"][0] - s["diff"]["lo"]), abs(m["ci"][1] - s["diff"]["hi"])))
    dp.append(abs(m["p_less"] - s["diff"]["p_less"]))
    if m["class"] != s["cls"]:
        cls_mis.append((key, m["class"], s["cls"], m["ci"], [s["diff"]["lo"], s["diff"]["hi"]]))
    if m["W_holm"] != s["win_holm"]:
        holm_mis.append((key, m["W_holm"], s["win_holm"], m["p_less"], s["diff"]["p_less"]))
L.append(f"partB: {len(dest)} cells; max |est diff| {max(dest):.2e}; max |CI bound diff| {max(dci):.4f} "
         f"(median {np.median(dci):.4f}); max |p diff| {max(dp):.4f}")
L.append(f"class mismatches: {len(cls_mis)} {cls_mis}")
L.append(f"W_holm mismatches: {len(holm_mis)} {holm_mis}")
# rule A
for cond in ("cond1",):
    for s in pub["ruleA"][cond]:
        m = next(x for x in mine["ruleA"]["C1"] if x["cell"] == nm(s["T"], s["kind"], s["rate"]))
        L.append(f"C1 {m['cell']}: ratio mine {m['ratio']:.6f} pub {s['ratio']:.6f}; ratioCI mine "
                 f"[{m['ratio_ci'][0]:.4f},{m['ratio_ci'][1]:.4f}] pub [{s['lo']:.4f},{s['hi']:.4f}]; p_TOST mine {m['p_tost']:.4f} pub {s['p_tost']:.4f}; "
                 f"TOST-Holm mine {m['tost_holm']} pub {s['equiv_holm']}")
L.append("ruleA keys: " + ", ".join(pub["ruleA"].keys()))
L.append("pub cond2: " + json.dumps(pub["ruleA"].get("cond2"), default=str)[:1500])
(R / "ext_v4cverify_recompute/compare_published.txt").write_text("\n".join(L) + "\n")
print("\n".join(L))

# ---- appended: CI-diff detail and width definition ----
L2 = []
big = []
for key, s in pub["partB"].items():
    c, X, T, k, r = key.split("|")
    m = next(x for x in mine["partB_cells"][f"({c}) {X}"] if x["cell"] == nm(int(T), k, float(r)))
    d = max(abs(m["ci"][0] - s["diff"]["lo"]), abs(m["ci"][1] - s["diff"]["hi"]))
    w = s["diff"]["hi"] - s["diff"]["lo"]
    if d > 0.03:
        big.append((key, round(d, 4), round(d / w, 3), round(min(abs(s["diff"]["lo"]), abs(s["diff"]["hi"])), 3)))
L2.append(f"cells with CI bound diff > 0.03: {len(big)}; max relative (diff / CI width) {max(b[2] for b in big):.3f}; "
          f"min distance of nearest published bound to 0 among them {min(b[3] for b in big):.3f}")
L2.append("  " + "; ".join(str(b) for b in sorted(big, key=lambda b: b[3])[:10]))
rows = [json.loads(l) for l in open(R / "ext_v4c_eval/runs.jsonl")]
for meth in ("tolerant_v4", "tolerant_v4c"):
    for rate in (0.2, 0.5):
        rr = [x for x in rows if x["method"] == meth and x["T"] == 40 and x["kind"] == "missing" and x["rate"] == rate]
        mean = np.mean([x["width_kept"] for x in rr]); med = np.median([x["width_kept"] for x in rr])
        wt = sum(x["width_kept"] * x["n_kept"] for x in rr) / sum(x["n_kept"] for x in rr)
        L2.append(f"width {meth} T40 missing-{rate}: mean {mean:.3f}, median {med:.3f}, n_kept-weighted {wt:.3f}")
(R / "ext_v4cverify_recompute/compare_published.txt").open("a").write("\n".join(L2) + "\n")
print("\n".join(L2))
