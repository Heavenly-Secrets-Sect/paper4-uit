"""D4 (docs/ext/auto3fix.md 1.3): consequence of bug E1 for the two P2 configs, on stored D-07 rows.
Config 2's cell list (none, missing-0.2, reversed-0.2) is that of ext_auto5_a1; config 1's (none,
extra/missing/reversed x 0.2/0.5, GES) is that of ext_gate_auto3. Compare clean rows of both runs at
T80/150: identical IS for plugin / tolerant_v4 / tolerant_auto3, and identical stated k (same damaged
skeleton). Output: results/ext_auto3fix_e1/e1.json, e1.md.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_p4h2_v2 as C  # noqa: E402

ROOT = C.ROOT


def idx(run):
    d = {}
    for r in C.load_rows(ROOT / "results" / run / "runs.jsonl"):
        if r.get("scenario", "clean") == "clean":
            d[(r["method"], r["topology"], r["replicate"], r["T"], r["kind"], float(r["rate"]))] = r
    return d


def main():
    a, g = idx("ext_auto5_a1"), idx("ext_gate_auto3")
    out = defaultdict(dict)
    for (m, t, rep, T, k, r), ra in a.items():
        if m not in ("plugin", "tolerant_v4", "tolerant_auto3"):
            continue
        rg = g.get((m, t, rep, T, k, r))
        if rg is None:
            continue
        cell = f"{T}|{k}|{r}"
        o = out[cell].setdefault(m, {"n": 0, "same_IS": 0, "same_k": 0})
        o["n"] += 1
        o["same_IS"] += ra.get("iscore_nonnull_mean") == rg.get("iscore_nonnull_mean")
        o["same_k"] += ra.get("k") == rg.get("k")
    def sk(run):
        res = {}
        for line in open(ROOT / "results" / run / "skeletons.jsonl", encoding="utf-8"):
            x = json.loads(line)
            if "kind" in x and "T" not in x and "scenario" not in x:
                res[(x["topology"], x["replicate"], x["kind"], x["rate"])] = json.dumps(x["log"], sort_keys=True)
        return res
    sa, sg = sk("ext_auto5_a1"), sk("ext_gate_auto3")
    skel = {}
    for kind in ("missing", "reversed"):
        ks = [k for k in sa if k[2] == kind and k[3] == 0.2 and k in sg]
        skel[f"{kind}|0.2"] = {"units": len(ks), "identical_damage_log": sum(sa[k] == sg[k] for k in ks)}
    out["damaged_skeletons"] = skel
    d = ROOT / "results" / "ext_auto3fix_e1"
    d.mkdir(parents=True, exist_ok=True)
    (d / "e1.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = ["# D4: E1 on the two P2 grids (stored D-07 rows: ext_auto5_a1 vs ext_gate_auto3, clean scenario)", "",
         "| cell | method | rows | identical IS | identical stated k |", "|---|---|---|---|---|"]
    for cell in sorted((c for c in out if c != "damaged_skeletons"), key=lambda c: (int(c.split('|')[0]), c)):
        for m, o in sorted(out[cell].items()):
            L.append(f"| {cell} | {m} | {o['n']} | {o['same_IS']} | {o['same_k']} |")
    L += ["", "Damaged skeletons (damage log per topology x replicate): " + "; ".join(f"{k} identical {v['identical_damage_log']}/{v['units']}" for k, v in skel.items())]
    L += ["", "tolerant_auto3 of ext_gate_auto3 used round-1 (position-based) ext seeds and ext_auto5_a1 name-based ones, so its IS differs even where the cell is the same."]
    (d / "e1.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
