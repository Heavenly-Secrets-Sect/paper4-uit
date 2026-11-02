"""POST HOC, descriptive only (written after the ruling; not part of the pre-registered rule).
Tail of the IS distribution on rescued runs at T <= 25, and the v5_1-ok runs that hs2 changed.
Writes results/ext_r5hubscreen2_ruling/posthoc.md.
"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "results"
rows = [json.loads(l) for l in open(RES / "ext_r5hubscreen2_p2" / "runs.jsonl")]
idx = defaultdict(dict)
for r in rows:
    idx[(r["topology"], r["replicate"], r["T"], r["kind"])][r["method"]] = r
L = ["# r5hubscreen2 POST HOC (descriptive, written after the ruling)", "",
     "## Rescued runs at T <= 25: IS tail (hs2 vs plugin_hs_cal, same runs)", "",
     "| T | cell | n | hs2 mean / median / max / #IS>50 | plugin_hs_cal mean / median / max / #IS>50 | hs2 mean without its top 3 runs | runs where hs2 IS < plugin_hs_cal IS |",
     "|---|---|---|---|---|---|---|"]
for T in (19, 25):
    for k in ("missing", "reversed", "extra"):
        a, b = [], []
        for key, d in idx.items():
            if key[2] != T or key[3] != k:
                continue
            h, p = d.get("tolerant_v5_1_hs2"), d.get("plugin_hs_cal")
            if h and p and h["v51_status"] != "ok" and h["status"] == "ok" and p["status"] == "ok":
                a.append(h["iscore_nonnull_mean"]); b.append(p["iscore_nonnull_mean"])
        a, b = np.array(a), np.array(b)
        if not len(a):
            continue
        trim = np.sort(a)[:-3].mean() if len(a) > 3 else float("nan")
        L.append(f"| {T} | {k} | {len(a)} | {a.mean():.2f} / {np.median(a):.2f} / {a.max():.1f} / {(a > 50).sum()} | "
                 f"{b.mean():.2f} / {np.median(b):.2f} / {b.max():.1f} / {(b > 50).sum()} | {trim:.2f} | {(a < b).sum()}/{len(a)} |")
L += ["", "## v5_1-ok runs changed by hs2 (raw not identical), by cell", "",
      "| T | cell | v5_1 ok | changed | mean IS v5_1 / hs2 on changed runs | factor hs2 used (f_red) vs f_v51 |", "|---|---|---|---|---|---|"]
fac = json.loads((RES / "ext_r5hubscreen2_p2" / "factors_used.json").read_text())
for T in (19, 25, 30, 35):
    for k in ("missing", "reversed", "extra"):
        ch, ok = [], 0
        for key, d in idx.items():
            if key[2] != T or key[3] != k:
                continue
            h, v = d.get("tolerant_v5_1_hs2"), d.get("tolerant_v5_1")
            if h["v51_status"] == "ok":
                ok += 1
                if not h["raw_ident_v51"] and v["status"] == "ok" and h["status"] == "ok":
                    ch.append((v["iscore_nonnull_mean"], h["iscore_nonnull_mean"]))
        s = (f"{np.mean([c[0] for c in ch]):.2f} / {np.mean([c[1] for c in ch]):.2f}" if ch else "–")
        L.append(f"| {T} | {k} | {ok} | {len(ch)} | {s} | {fac['red'].get(f'{T}|{k}')} vs {fac['v51'].get(f'{T}|{k}')} |")
(RES / "ext_r5hubscreen2_ruling" / "posthoc.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
