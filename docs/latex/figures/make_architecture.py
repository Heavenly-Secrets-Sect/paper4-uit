"""Architecture figure of the method (feedback point 7). Writes architecture_srci.png and .pdf next to this file.
Names in the figure follow the paper vocabulary; code names are in docs/ext/naming.md.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent
GREY, DARK, LIGHT = "#444444", "#111111", "#F2F2F2"

fig, ax = plt.subplots(figsize=(13, 6.4))
ax.set_xlim(0, 13.2)
ax.set_ylim(0, 6.4)
ax.axis("off")


def box(x, y, w, h, title, body="", fill="white", bold=True, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fill, ec=DARK, lw=1.2, ls=ls))
    ax.text(x + w / 2, y + h - 0.2, title, ha="center", va="top", fontsize=10.5, fontweight="bold" if bold else "normal", color=DARK)
    if body:
        ax.text(x + w / 2, y + h - 0.3 - 0.27 * (title.count("\n") + 1) - 0.12, body, ha="center", va="top", fontsize=8.6, color=GREY, linespacing=1.35)


def arrow(p, q, label="", rad=0.0, dy=0.12):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=13, color=DARK, lw=1.2, connectionstyle=f"arc3,rad={rad}"))
    if label:
        ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + dy, label, ha="center", fontsize=8.2, color=GREY)


# input
box(0.1, 3.7, 1.9, 2.3, "Input", "data X (T × n)\nstated skeleton S\nstated damage\n(missing, extra,\nreversed counts)", fill=LIGHT)
# step boxes
box(2.45, 3.7, 2.1, 2.3, "1. Evidence\nscoring", "for each unlinked pair:\nF-tests (two lag\nblocks) + Fisher z\non residuals;\nSidak-combined p")
box(4.85, 3.7, 2.1, 2.3, "2. Targeted Lag\nExpansion (TLE)", "open lag blocks for the\nK strongest pairs, with\nK = min(|N|,\nmax(3 k_miss, #{p<0.10}))")
box(7.25, 3.7, 2.1, 2.3, "3. Edge Repair\n(FCER)", "add contemporaneous\nedges by Benjamini-\nHochberg (q = 0.10) on\nresidual correlations;\ndraw direction")
box(9.65, 3.7, 1.7, 2.3, "4. Targeted\nreversal", "flip k_rev edges\namong significant\ncontemporaneous\nedges (acyclic)")
# bootstrap band
box(2.45, 0.35, 8.9, 2.55, "5. Residual bootstrap with structure re-selection  (B draws)", "", fill="white", ls="--")
ax.text(6.9, 2.0, "for each draw b:   X*(b) from fitted model + resampled residuals   →   repeat steps 1-4 on X*(b)\n"
                  "→   refit   →   cumulative effect  C*(b)(H)    (structure uncertainty is propagated into the interval)",
        ha="center", va="center", fontsize=9, color=DARK, linespacing=1.6)
ax.text(6.9, 1.1, "Switch rule (RBS): if rows / regressors of the all-lag fit < τ  →  targeted opening (steps 1-4)\n"
                  "otherwise  →  all-lag branch (no re-selection needed)",
        ha="center", va="center", fontsize=8.6, color=GREY, style="italic", linespacing=1.5)
# step 6
box(11.6, 0.35, 1.5, 2.55, "6. Width\ncalibration\n(FWC)", "percentile interval,\nshrink, then\n× c(T, kind)", fill=LIGHT)
# output
box(11.6, 3.7, 1.5, 2.3, "Output", "interval for\nC(H) per pair\n+ reliability\nflag", fill=LIGHT)

arrow((2.0, 4.85), (2.45, 4.85))
arrow((4.55, 4.85), (4.85, 4.85))
arrow((6.95, 4.85), (7.25, 4.85))
arrow((9.35, 4.85), (9.65, 4.85))
arrow((10.5, 3.7), (10.5, 2.9), "")
arrow((11.35, 1.6), (11.6, 1.6))
arrow((12.35, 2.9), (12.35, 3.7))
ax.text(6.9, 0.12, "c(T, kind): order statistic of per-topology scores on a separate calibration bank (finite-sample, topology level)",
        ha="center", fontsize=8.4, color=GREY)

fig.savefig(HERE / "architecture_srci.png", dpi=200, bbox_inches="tight", facecolor="white")
fig.savefig(HERE / "architecture_srci.pdf", bbox_inches="tight", facecolor="white")
print("written")
