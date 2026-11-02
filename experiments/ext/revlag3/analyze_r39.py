"""R3-9 (revlag3): descriptive AUROC of the FROZEN RQ4.4 flag (experiments/ext/revlag/frozen_flag.json,
not refitted) on the pair rows of tolerant_auto3 and tolerant_v5_1, as pre-registered in
docs/ext/revlag3.md. Also the tolerant_v4 rows of the same run (in-sample reference: the flag was
fitted on these very v4 rows of round 1; identical by the validity check).

Scores: p_hat (training encoding of the stated kind), p_hat with the stated dummies set to 0
("p_hat no-stated", the version usable in the auto mode, which reads no stated damage),
comparators rel_width and 1/width. Sets: T80/150 pooled over 7 cells, T40 pooled; per T (mô tả).
Run:  python experiments/ext/revlag3/analyze_r39.py [--run ext_revlag3_flag]
Writes results/<run>/r39_flag.{md,json}.
"""
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from flag3 import HDR, evaluate3, fmt3, load3  # noqa: E402
sys.path.insert(0, str(ROOT / "experiments/ext/revlag"))
from analyze_flag import FROZEN_SHA, holm  # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", default="ext_revlag3_flag"); a = ap.parse_args()
    fpath = ROOT / "experiments/ext/revlag/frozen_flag.json"
    assert hashlib.sha256(fpath.read_bytes()).hexdigest() == FROZEN_SHA
    frozen = json.loads(fpath.read_text())
    out = ROOT / "results" / a.run
    res = {"sets": []}
    L = [f"# R3-9: frozen RQ4.4 flag on auto3 / v5_1 rows ({a.run}; mô tả)", "",
         "Flag không fit lại. CI: topology-cluster bootstrap, 2000 lần, seed 20261103. "
         "p_hat dùng mã hoá stated như lúc train (cell kind).", ""] + HDR
    tests = []
    for method in ("tolerant_auto3", "tolerant_v5_1", "tolerant_v4"):
        rows = load3(a.run, method)
        for lab, sel in (("T80/150", rows["T"] >= 80), ("T40", rows["T"] == 40),
                         ("T80", rows["T"] == 80), ("T150", rows["T"] == 150)):
            for nost in (False, True):
                e = evaluate3(rows, sel, frozen, f"{method} {lab} {'p_hat no-stated' if nost else 'p_hat'}", nostated=nost)
                e.update(method=method, set=lab, nostated=nost)
                res["sets"].append(e)
                L.append(fmt3(e))
                primary = (method == "tolerant_auto3" and nost) or (method == "tolerant_v5_1" and not nost)
                if primary and lab in ("T80/150", "T40"):
                    tests.append(e)
    # pre-registered reading: transfer (AUROC lower CI > 0.5) and adds over 1/width (delta lower CI > 0)
    ph_t = holm([e["p_auc_le_05"] for e in tests]); ph_i = holm([e["p_dinv_le0"] for e in tests])
    L += ["", "## Cách đọc ghi trước (score chính: auto3 = p_hat no-stated; v5_1 = p_hat)", "",
          "| method | tập | AUROC [CI] | chuyển được (CI lo > 0.5) | Holm p (4) | hơn 1/width (CI lo > 0) | Holm p (4) | "
          "F1/F3-ngưỡng 0.65 (mô tả) | F4 (mô tả) |", "|---|---|---|---|---|---|---|---|---|"]
    res["reading"] = []
    for e, pt, pi in zip(tests, ph_t, ph_i):
        f13 = e["auc_p_ci"][0] > 0.65
        f4 = e["share"] <= 0.5 and e["ratio"] >= 2 and e["ratio_ci"][0] > 1
        r = dict(method=e["method"], set=e["set"], transfer=bool(e["auc_p_ci"][0] > 0.5), transfer_holm=bool(pt < 0.05),
                 beats_inv=bool(e["d_inv_ci"][0] > 0), beats_inv_holm=bool(pi < 0.05 and e["d_inv"] > 0), f13=f13, f4=f4)
        res["reading"].append(r)
        L.append(f"| {e['method']} | {e['set']} | {e['auc_p']:.3f} [{e['auc_p_ci'][0]:.3f}, {e['auc_p_ci'][1]:.3f}] | "
                 f"{r['transfer']} | {pt:.4f} | {r['beats_inv']} | {pi:.4f} | {f13} | {f4} |")
    nt, nth = sum(r["transfer"] for r in res["reading"]), sum(r["transfer_holm"] for r in res["reading"])
    ni, nih = sum(r["beats_inv"] for r in res["reading"]), sum(r["beats_inv_holm"] for r in res["reading"])
    L += ["", f"Chuyển được: {nt}/4 (Holm {nth}/4). Hơn 1/width: {ni}/4 (Holm {nih}/4).", ""]
    res.update(n_transfer=nt, n_transfer_holm=nth, n_beats_inv=ni, n_beats_inv_holm=nih)
    # auto3 by gate state (descriptive)
    rows = load3(a.run, "tolerant_auto3")
    if "aux" in rows:
        L += ["## auto3 theo trạng thái gate (mô tả, T80/150)", ""] + HDR
        for code, nm in ((0, "closed"), (1, "open")):
            sel = (rows["T"] >= 80) & (rows["aux"] == code)
            if sel.sum() > 100:
                e = evaluate3(rows, sel, frozen, f"auto3 T80/150 gate {nm} p_hat no-stated", nostated=True)
                res["sets"].append(dict(e, method="tolerant_auto3", set=f"T80/150 gate {nm}", nostated=True))
                L.append(fmt3(e))
    (out / "r39_flag.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "r39_flag.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else o))
    print("\n".join(L))


if __name__ == "__main__":
    main()
