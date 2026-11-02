"""Post-hoc (NOT pre-registered) descriptives of where the module's misses fall, written after
seeing results/ext_metrics_flags/summary.md. Writes results/ext_metrics_flags/posthoc.md."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_pairs import FLAGS, WAuc, load  # noqa: E402


def main():
    d = load()
    mod = d["method"] == d["methods"].index("tolerant_v4")
    lines = ["# Post-hoc descriptives (not pre-registered)", ""]
    for Ts in ((80, 150), (40,)):
        base = mod & np.isin(d["T"], Ts)
        miss = ~d["covered"]
        lines += [f"## T in {Ts}", "", f"AUROC of `1/width` (direction reversed post hoc): "
                  f"{WAuc(-d['width'][base], miss[base], d['topo'][base])(np.ones(20)):.3f}", "",
                  "Miss rate of the module by quintile of interval width:", "", "| quintile | width range | miss rate | median abs C_true |",
                  "|---|---|---|---|"]
        w = d["width"][base]
        q = np.quantile(w, [0.2, 0.4, 0.6, 0.8])
        b = np.digitize(w, q)
        e = [w.min()] + list(q) + [w.max()]
        for k in range(5):
            s = b == k
            lines.append(f"| {k + 1} | {e[k]:.2f}-{e[k + 1]:.2f} | {miss[base][s].mean():.3f} | "
                         f"{np.median(np.abs(d['C_t'][base][s])):.3f} |")
        lines += ["", "Miss rate by |C_true| tercile:", "", "| tercile | abs C range | miss rate |", "|---|---|---|"]
        a = np.abs(d["C_t"][base])
        qa = np.quantile(a, [1 / 3, 2 / 3])
        ba = np.digitize(a, qa)
        ea = [a.min()] + list(qa) + [a.max()]
        for k in range(3):
            s = ba == k
            lines.append(f"| {k + 1} | {ea[k]:.2f}-{ea[k + 1]:.2f} | {miss[base][s].mean():.3f} |")
        lines += ["", "Share of all module misses by damage kind and role:", "", "| kind | role | pairs | misses | miss rate | share of misses |",
                  "|---|---|---|---|---|---|"]
        kinds = np.array([c.split("|")[0] for c in d["cells"]])[d["cell"]]
        tot = miss[base].sum()
        for kd in ("none", "extra", "missing", "reversed"):
            for r, rn in ((2, "damaged"), (1, "downstream"), (0, "untouched")):
                s = base & (kinds == kd) & (d["role"] == r)
                if s.any():
                    lines.append(f"| {kd} | {rn} | {s.sum()} | {miss[s].sum()} | {miss[s].mean():.3f} | {miss[s].sum() / tot:.3f} |")
        lines.append("")
    (FLAGS / "posthoc.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
