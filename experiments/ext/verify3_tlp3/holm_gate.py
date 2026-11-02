"""verify3_tlp3: raw-vs-Holm distinction in decide() on hand-built res. Writes results/ext_verify3_tlp3/holm_gate.json."""
import importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("A", ROOT / "experiments/ext/tlp3/analyze_p4h2.py")
A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
def res_with(pfun):
    cells = {}
    for T in A.TS:
        for i, (k, r) in enumerate(A.DAMAGED):
            comps = {X: {"n_pairs": 60, "complete": True, "d": -0.3, "lo": -0.5, "hi": -0.05, "p": pfun(T, i, X)} for X in A.VERSIONS}
            cells[f"{T}|{k}|{r}"] = {"methods": {m: {"cov": 0.95} for m in [A.REF] + A.VERSIONS}, "comps": comps}
    return {"cells": cells}
out = {}
for name, f in {"all_p_0.02": lambda T, i, X: 0.02,
                "p_0.001_x10_0.03_x2": lambda T, i, X: 0.03 if (T == 150 and i >= 4) else 0.001,
                "p_0.001_x9_0.03_x3": lambda T, i, X: 0.03 if (T == 150 and i >= 3) else 0.001}.items():
    v, per = A.decide(res_with(f))
    out[name] = {"verdict": v, **{X: [per[X]["v4_wins_gate"], per[X]["v4_wins_gate_holm"]] for X in per}}
(ROOT / "results/ext_verify3_tlp3/holm_gate.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=1))
