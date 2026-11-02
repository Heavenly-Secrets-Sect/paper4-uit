"""Verifier: is K1's lower width factor explained by re-centring or by wider raw draws?
raw width (pre-prescale, pre-factor) per run: v5_1 = width_kept/(0.5*c_T); K1 = width_kept/(0.5*c_T); K0 = width_kept.
K1 raw should equal K0 raw (same draws). Report median paired ratio K0raw / v5_1raw per cell."""
import json
import numpy as np
ROOT = "/Users/kietnt/Desktop/Workspace/Paper4_UIT"
rows = [json.loads(l) for l in open(f"{ROOT}/results/ext_r4kilianbab_eval/runs.jsonl")]
idx = {(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"], r["method"]): r for r in rows if r["status"] == "ok"}
CELLS = [("none", 0.0)] + [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]
cal = json.load(open(f"{ROOT}/results/ext_r4kilianbab_eval/calibration.json"))
out = {}
for T in (40, 80, 150):
    for k, rt in CELLS:
        rat, rat1, chk = [], [], []
        for key, r in idx.items():
            if key[5] != "tolerant_v5_1" or key[2:5] != (T, k, rt):
                continue
            b = key[:5]
            k0, k1 = idx.get(b + ("r4kilianbab_babraw",)), idx.get(b + ("r4kilianbab_bab",))
            if not k0 or not k1 or r["width_kept"] is None:
                continue
            v_raw = r["width_kept"] / (0.5 * r["info_c_T"])
            k1_raw = k1["width_kept"] / (0.5 * k1["info_c_T"])
            rat.append(k0["width_kept"] / v_raw)
            chk.append(abs(k1_raw - k0["width_kept"]) / k0["width_kept"])
        kind = k
        fv = 0.5 * cal[f"tolerant_v5_1|{T}|{kind}"]; fk = 0.5 * cal[f"r4kilianbab_bab|{T}|{kind}"]
        out[f"{T}|{k}|{rt}"] = {"median_rawwidth_ratio_K0_over_v51": round(float(np.median(rat)), 3),
                                "mean_rawwidth_ratio": round(float(np.mean(rat)), 3),
                                "factor_ratio_K1_over_v51": round(fk / fv, 3),
                                "final_width_ratio_pred": round(float(np.median(rat)) * fk / fv, 3),
                                "max_rel_diff_K1raw_vs_K0": float(max(chk))}
json.dump(out, open(f"{ROOT}/results/ext_verify4_kilianbab/rawwidth.json", "w"), indent=1)
for k, v in out.items(): print(k, v)
