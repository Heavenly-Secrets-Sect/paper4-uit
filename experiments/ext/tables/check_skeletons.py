"""Check that damaged skeletons of the tlp2 / baselines3 runs equal those of the a2-grid runs (ext_v51_eval).
Writes results/ext_tables_main/checks_skeletons.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def sk(run):
    out = {}
    for line in open(ROOT / "results" / run / "skeletons.jsonl", encoding="utf-8"):
        r = json.loads(line)
        out[(r["topology"], r["replicate"], r["kind"], r["rate"])] = json.dumps(r, sort_keys=True)
    return out


ref = sk("ext_v51_eval")
res = {}
for run in ["ext_tlp2_t40", "ext_tlp2_t80a", "ext_tlp2_t80b", "ext_tlp2_t80c", "ext_tlp2_t150a", "ext_tlp2_t150b",
            "ext_tlp2_t150c", "ext_tlp2_t150d", "ext_baselines3_eval", "a2_baselines", "ext_tlp_eval",
            "ext_redteam_calbase", "ext_baselines2_eval", "ext_v4c_eval", "a2b_pselect"]:
    s = sk(run)
    common = [k for k in s if k in ref]
    res[run] = {"n": len(s), "n_common": len(common), "identical": sum(1 for k in common if s[k] == ref[k])}
json.dump(res, open(ROOT / "results" / "ext_tables_main" / "checks_skeletons.json", "w"), indent=1)
print(json.dumps(res, indent=1))
