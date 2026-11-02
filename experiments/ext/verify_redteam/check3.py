"""F6 re-framing: share of v4's IS gain that fullvar_cal already reaches, against plugin and against pselect_cal."""
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
rows = [json.loads(l) for l in open(ROOT / "results/ext_redteam_calbase/runs.jsonl")]
g = defaultdict(list)
for r in rows:
    if r["status"] == "ok": g[(r["T"], r["kind"], r["rate"], r["method"])].append(r["iscore_nonnull_mean"])
cal = json.loads((ROOT / "results/ext_redteam_calbase/calibration.json").read_text())
for T in (80, 150):
    for rate in (0.2, 0.5):
        m = {k: np.mean(g[(T, "missing", rate, k)]) for k in ("plugin", "tolerant_v4", "fullvar_cal", "pselect_cal")}
        sp = (m["plugin"] - m["fullvar_cal"]) / (m["plugin"] - m["tolerant_v4"])
        sb = (m["pselect_cal"] - m["fullvar_cal"]) / (m["pselect_cal"] - m["tolerant_v4"])
        print(f"T={T} missing-{rate}: IS plugin {m['plugin']:.2f} pselect_cal {m['pselect_cal']:.2f} fullvar_cal {m['fullvar_cal']:.2f} v4 {m['tolerant_v4']:.2f} | share vs plugin {sp:.3f} | share of v4 margin over pselect_cal {sb:.3f}")
print("factors at floor 1.0 (T>=80):", sorted(k for k, v in cal.items() if v == 1.0 and "|40|" not in k and "|" in k))
