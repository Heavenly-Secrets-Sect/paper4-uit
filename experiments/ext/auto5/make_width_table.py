"""Width table of tolerant_auto5 and of the ablation tolerant_auto5_small from the in-sample probe
factors (results/ext_auto5_probe/probe2_summary.json, D-07H development, two-sided grid 0.5..5.0).
tolerant_auto5 = variant tgtall/sig_bh/two (closed|T, open_tgt|T); tolerant_auto5_small = variant
tgt40/sig_bh/two (adds open_all|80, open_all|150; its closed|T and open_tgt|40 are the same records,
checked below). Run: python experiments/ext/auto5/make_width_table.py"""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
S = json.loads((HERE.parents[2] / "results/ext_auto5_probe/probe2_summary.json").read_text())
main, small = S["tgtall/sig_bh/two"]["factors"], S["tgt40/sig_bh/two"]["factors"]
for k in set(main) & set(small):
    assert main[k] == small[k], k
table = dict(sorted({**main, **small}.items()))
(HERE / "width_table.json").write_text(json.dumps(table, indent=2), encoding="utf-8")
print(table)
