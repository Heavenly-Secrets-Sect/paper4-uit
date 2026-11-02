"""R3-4 last part (revlag3): 1/width as a comparator row in the RQ4.4 tables, on the round-2 FRESH
D-07 development runs (seed_base 30261102; results/ext_revlag_fresh{,_ges,_a1}), tolerant_v4 rows,
frozen flag not refitted. Also the rule F1-F4 recomputed with the TRAINING encoding of the stated
kind (descriptive: the round-2 verdict stands as recorded). Descriptive, pre-registered in
docs/ext/revlag3.md. No new data.
Run:  python experiments/ext/revlag3/flag_extra.py
Writes results/ext_revlag3_flagextra/{flag_extra.md, flag_extra.json}.
"""
import hashlib, json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from flag3 import HDR, evaluate3, fmt3, load3  # noqa: E402
sys.path.insert(0, str(ROOT / "experiments/ext/revlag"))
from analyze_flag import FROZEN_SHA  # noqa: E402


def main():
    fpath = ROOT / "experiments/ext/revlag/frozen_flag.json"
    assert hashlib.sha256(fpath.read_bytes()).hexdigest() == FROZEN_SHA
    frozen = json.loads(fpath.read_text())
    out = ROOT / "results/ext_revlag3_flagextra"; out.mkdir(parents=True, exist_ok=True)
    res = {}
    L = ["# RQ4.4 tables with 1/width as comparator (fresh D-07 development, seed_base 30261102; tolerant_v4)", ""]
    for enc in ("round2", "train"):
        clean = load3("ext_revlag_fresh", encoding=enc)
        ges = load3("ext_revlag_fresh_ges", encoding=enc)
        a1 = load3("ext_revlag_fresh_a1", encoding=enc)
        sets = [evaluate3(clean, clean["T"] >= 80, frozen, "clean T80/150"),
                evaluate3(clean, clean["T"] == 40, frozen, "clean T40"),
                evaluate3(ges, np.ones(len(ges["T"]), bool), frozen, "GES all T")]
        sets += [evaluate3(ges, ges["T"] == T, frozen, f"GES T{T}") for T in (40, 80, 150)]
        sets += [evaluate3(a1, a1["scen"] == s, frozen, f"{nm} T80/150") for s, nm in enumerate(a1["scen_names"])]
        sets += [evaluate3(clean, (clean["T"] >= 80) & (clean["cell"] == c), frozen, f"clean T80/150 {cn}")
                 for c, cn in enumerate(clean["cells"])]
        res[enc] = sets
        e1, e3 = sets[0], sets[1]
        F = {"F1": e1["auc_p_ci"][0] > 0.65, "F2": e1["d_auc_ci"][0] > 0, "F3": e3["auc_p_ci"][0] > 0.65,
             "F4_T80_150": e1["share"] <= 0.5 and e1["ratio"] >= 2 and e1["ratio_ci"][0] > 1,
             "F4_T40": e3["share"] <= 0.5 and e3["ratio"] >= 2 and e3["ratio_ci"][0] > 1}
        res[enc + "_rule"] = F
        n_diff = int((load3("ext_revlag_fresh", encoding="train")["stated"] != load3("ext_revlag_fresh", encoding="round2")["stated"]).sum())
        L += [f"## Mã hoá stated: {'round 2 (width_key)' if enc == 'round2' else 'như lúc train (cell kind)'}", ""] + HDR + \
             [fmt3(e) for e in sets] + ["", f"F1–F4 (mô tả): {F}; số hàng clean khác mã hoá giữa hai cách: {n_diff}", ""]
    (out / "flag_extra.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "flag_extra.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else o))
    print("\n".join(L))


if __name__ == "__main__":
    main()
