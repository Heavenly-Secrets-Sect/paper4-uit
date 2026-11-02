"""R3-5 (tlp3), point (5): is the frozen tolerant_v4 realisation identical across configs that use the
same kinds/rates list (hence the same c_idx and k_idx), on D-07 development? Reads existing runs only.
Writes results/ext_tlp3_checks/v4_realisation.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONFIGS = ["ext_v51_eval", "ext_baselines2_eval", "ext_v4c_eval", "ext_tlp_eval", "a2_baselines"]
REF = "ext_v51_eval"


def load(name):
    out = {}
    p = ROOT / f"results/{name}/runs.jsonl"
    if not p.exists():
        return None
    for line in p.open():
        r = json.loads(line)
        if r["method"] == "tolerant_v4" and r.get("scenario", "clean") == "clean":
            out[(r["topology"], r["replicate"], r["T"], r["kind"], float(r["rate"]))] = r
    return out


def main():
    ref = load(REF)
    res = {"reference": REF, "comparisons": {}}
    for c in CONFIGS:
        if c == REF:
            continue
        o = load(c)
        if o is None:
            res["comparisons"][c] = "missing"
            continue
        per_T = {}
        for T in (40, 80, 150):
            same = tot = 0
            for k, r in ref.items():
                if k[2] != T or k not in o:
                    continue
                a, b = r, o[k]
                if a["status"] != "ok" or b["status"] != "ok":
                    continue
                tot += 1
                same += (a["iscore_nonnull_mean"] == b["iscore_nonnull_mean"]
                         and a["n_covered_nonnull"] == b["n_covered_nonnull"])
            per_T[str(T)] = [same, tot]
        res["comparisons"][c] = per_T
    out = ROOT / "results/ext_tlp3_checks"
    out.mkdir(parents=True, exist_ok=True)
    (out / "v4_realisation.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
