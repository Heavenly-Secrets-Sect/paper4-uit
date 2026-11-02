"""Sensitivity of the tlp2 rule to a driver defect found after the runs (docs/ext/tlp2.md, section 7).

Defect: experiments/ext/tlp2/run_cells.py drops cells from the skeleton dict, and the runner seeds the
bootstrap of built-in methods and of runner-seeded ext methods with rng([unit, 3, T, c_idx, tag]) where
c_idx is the POSITION of the cell in that dict. Dropping earlier cells shifts c_idx, so tolerant_v4 and
targeted_lp in cells that are not first in the full order get fresh bootstrap draws (same data, same
skeleton, same frozen width factors). The tlp2_* methods are content-seeded and unaffected.

This script re-scores the SAME pre-registered rule (experiments/ext/tlp2/score.py, unchanged) after
replacing every tolerant_v4 row by the round-1 row of results/ext_tlp_eval/runs.jsonl for the same
(topology, replicate, T, kind, rate): frozen v4 with the round-1 c_idx, i.e. bit-identical to a2/ext_tlp_eval.
It also writes the run-level difference between the two v4 draws.

Output: results/ext_tlp2_rules_v4r1/rules.md, rules.json, v4_seed_noise.json
Usage: python experiments/ext/tlp2/score_v4r1.py
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import score as S  # noqa: E402

ROOT = S.ROOT
OUT = "results/ext_tlp2_rules_v4r1"


def main():
    r1 = {S.key(r): r for r in map(json.loads, (ROOT / "results/ext_tlp_eval/runs.jsonl").open())
          if r["method"] == S.REF}
    orig_load = S.load
    noise = defaultdict(list)

    def load_sub():
        rows, missing = orig_load()
        out, n_sub = [], 0
        for r in rows:
            if r["method"] == S.REF:
                o = r1[S.key(r)]
                d = r["iscore_nonnull_mean"] - o["iscore_nonnull_mean"]
                noise[f"{r['T']}|{r['kind']}|{float(r['rate'])}"].append(d)
                n_sub += 1
                r = o
            out.append(r)
        print(f"substituted {n_sub} tolerant_v4 rows by round-1 rows")
        return out, missing

    S.load = load_sub
    sys.argv = [sys.argv[0], "--out", OUT]
    S.main()
    summ = {c: {"n": len(v), "mean_diff_new_minus_r1": float(np.mean(v)), "mean_abs_diff": float(np.mean(np.abs(v))),
                "n_identical": int(np.sum(np.abs(v) < 1e-9))} for c, v in sorted(noise.items())}
    (ROOT / OUT / "v4_seed_noise.json").write_text(json.dumps(summ, indent=2))
    print(json.dumps(summ, indent=2))


if __name__ == "__main__":
    main()
