"""FROZEN, NOT RUN on P4-H2. Confirmatory check of the frozen RQ4.4 flag (docs/ext/revlag.md,
"Frozen spec for P4-H2"): rules F1-F4 exactly as in analyze_flag.py, on the tolerant_v4 rows of
results/<run>/pairs.npz (default ext_revlag_p4h2). Same frozen model (sha256 checked), same
bootstrap (topology clusters of that run, 2000 resamples, seed 20261103).

Run:  python experiments/ext/revlag/analyze_flag_p4h2.py [--run ext_revlag_p4h2] [--out DIR]
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from analyze_flag import FROZEN_SHA, evaluate, fmt, holm, load  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="ext_revlag_p4h2")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    fpath = HERE / "frozen_flag.json"
    assert hashlib.sha256(fpath.read_bytes()).hexdigest() == FROZEN_SHA
    frozen = json.loads(fpath.read_text())
    rows = load(a.run)
    e1 = evaluate(rows, rows["T"] >= 80, frozen, "T80/150 (7 cell)")
    e3 = evaluate(rows, rows["T"] == 40, frozen, "T40 (7 cell)")
    F = {"F1": e1["auc_p_ci"][0] > 0.65, "F2": e1["d_auc_ci"][0] > 0, "F3": e3["auc_p_ci"][0] > 0.65,
         "F4_T80_150": e1["share"] <= 0.5 and e1["ratio"] >= 2 and e1["ratio_ci"][0] > 1,
         "F4_T40": e3["share"] <= 0.5 and e3["ratio"] >= 2 and e3["ratio_ci"][0] > 1}
    ps = [e1["p_auc_le_065"], e1["p_d_le0"], e3["p_auc_le_065"], e1["p_ratio_le1"], e3["p_ratio_le1"]]
    ph = [float(x) for x in holm(ps)]
    verdict = "ĐẠT" if all(F.values()) else "KHÔNG ĐẠT"
    hdr = ["| tập | n | miss rate | AUROC(p_hat) [CI] | AUROC(rel_width) [CI] | delta AUROC [CI] | flagged share | "
           "miss flagged / unflagged | ratio [CI] |", "|---|---|---|---|---|---|---|---|---|"]
    L = [f"# Frozen RQ4.4 flag, confirmatory check on {a.run}", ""] + hdr + [fmt(e1), fmt(e3), ""] + \
        [f"- {k}: {v}" for k, v in F.items()] + \
        [f"- one-sided p {[round(p, 4) for p in ps]}; Holm {[round(p, 4) for p in ph]}", "", f"**Verdict: {verdict}**"]
    out = Path(a.out) if a.out else ROOT / "results" / a.run
    out.mkdir(parents=True, exist_ok=True)
    (out / "flag_confirm.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "flag_confirm.json").write_text(json.dumps({"rule": F, "p": ps, "p_holm": ph, "verdict": verdict,
                                                       "T80_150": e1, "T40": e3}, indent=1, default=float))
    print("\n".join(L))


if __name__ == "__main__":
    main()
