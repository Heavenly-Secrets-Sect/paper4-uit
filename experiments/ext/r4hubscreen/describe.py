"""Descriptive tables cited in docs/ext/r4hubscreen.md (no decision): IS mean/median/max and count of
runs with IS > 50 (heavy tails from explosive bootstrap fits), reduction statistics, and the v5_1 width
factors tuned in-run vs frozen at lag 2 T40.

Run: python experiments/ext/r4hubscreen/describe.py -> results/ext_r4hubscreen_ruling/describe.md
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "results"
M = ["tolerant_v5_1_hs", "tolerant_v5_1", "plugin_cal", "plugin_hs_cal"]


def main():
    out = ["# r4hubscreen: descriptive tables (experiments/ext/r4hubscreen/describe.py)", ""]
    for lag, Ts in ((2, (19, 25, 30, 35, 40)), (1, (19, 25, 30))):
        rows = [json.loads(l) for l in open(RES / f"ext_r4hubscreen_lag{lag}" / "runs.jsonl")]
        out += [f"## lag_max {lag}: IS on completed runs (n ok · mean · median · max · #IS>50)", "",
                "| T | cell | " + " | ".join(M) + " |", "|---|---|" + "---|" * len(M)]
        for T in Ts:
            for k in ("none", "missing", "reversed", "extra"):
                cs = []
                for m in M:
                    v = np.array([r["iscore_nonnull_mean"] for r in rows if r["T"] == T and r["kind"] == k
                                  and r["method"] == m and r["status"] == "ok"])
                    cs.append("–" if not len(v) else f"{len(v)} · {v.mean():.2f} · {np.median(v):.2f} · {v.max():.1f} · {(v > 50).sum()}")
                out.append(f"| {T} | {k} | " + " | ".join(cs) + " |")
        out += ["", f"## lag_max {lag}: reductions of the candidate per run (means over 60 runs)", "",
                "| T | cell | runs reduced | eq reduced in data-level fits/screens | draws with reduction (of 199) | terms dropped (all calls) |",
                "|---|---|---|---|---|---|"]
        for T in Ts:
            for k in ("none", "missing", "reversed", "extra"):
                g = [r for r in rows if r["T"] == T and r["kind"] == k and r["method"] == "tolerant_v5_1_hs"]
                out.append(f"| {T} | {k} | {sum(r['hs_reduced'] for r in g)} | {np.mean([r.get('info_hs_eq_data', 0) for r in g]):.2f} | "
                           f"{np.mean([r.get('info_hs_draws_reduced', 0) for r in g]):.1f} | {np.mean([r.get('info_hs_terms_dropped', 0) for r in g]):.0f} |")
        cc = json.loads((RES / f"ext_r4hubscreen_lag{lag}" / "cal_counts.json").read_text())
        cal = json.loads((RES / f"ext_r4hubscreen_lag{lag}" / "calibration.json").read_text())
        out += ["", f"## lag_max {lag}: width factors (runner scale; effective = x 0.5 for v5_1 / candidate)", "",
                "| key | f_v51 used | f_v51 tuned in run | f_red | f_red source | hs1 (single) | plugin_hs_cal |", "|---|---|---|---|---|---|---|"]
        for T in Ts:
            for k in ("none", "extra", "missing", "reversed"):
                key = f"{T}|{k}"
                out.append(f"| {key} | {cal['v51'].get(key, '–')} | {cc['v51_tuned_in_run'].get(key, '–')} | {cal['red'].get(key, '–')} | "
                           f"{cc['red_source'].get(key, '–')} | {cal['hs_all'].get(key, '–')} | {cal['plugin_hs'].get(key, '–')} |")
        out.append("")
    (RES / "ext_r4hubscreen_ruling" / "describe.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
