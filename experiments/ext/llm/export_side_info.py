"""Export the LLM signals in the format of the text-informed module (src/paper4/ext_textinfo.py); no LLM call.

ext_textinfo reads, per unordered node-index pair "u-v" (u < v):
  doubt      on skeleton pairs (higher = more likely extra or reversed),
  suspicion  on non-adjacent pairs (higher = more likely missing),
  sign       optional +1 / -1 on skeleton pairs.
Node indices follow the order of NODES (core14_provenance.json). Only ranks matter in ext_textinfo.

doubt     = 0.5 * L4 doubt (1 - P(edge in the stated direction), mean of 2 prompt variants)
          + 0.5 * L1 reversal suspicion (bootstrap P(order reverses) and vote share, 3 variants)
suspicion = L4 support (mean P(direct edge)) for the 40 candidate pairs; pairs never co-mentioned are
            left out (ext_textinfo treats a missing key as a tie at the bottom of the ranking only if the
            caller fills it; we fill 0.0 explicitly for every other non-adjacent pair).
sign      = majority of the two L4 sign answers in the prior direction, only when both agree.

Output: results/ext_llm_edges/textinfo_side_info.json, plus sign/lag statistics printed.
"""
from __future__ import annotations

import collections
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import NODES, ROOT, SHORT, load_prior21  # noqa: E402


def key(a, b):
    i, j = NODES.index(a), NODES.index(b)
    return f"{min(i, j)}-{max(i, j)}"


def main():
    edges = json.loads((ROOT / "results/ext_llm_edges/edges.json").read_text(encoding="utf-8"))["pairs"]
    order = json.loads((ROOT / "results/ext_llm_order/order.json").read_text(encoding="utf-8"))
    l1 = {(e["source_id"], e["target_id"]): e for e in order["prior_edges"]}
    prior = load_prior21()
    adj = {key(e["source"], e["target"]) for e in prior}
    doubt, suspicion, sign, table = {}, {}, {}, []
    sign_cmp = collections.Counter()
    lag_c = collections.Counter()
    for r in edges:
        a, b = r["pair"]
        k = key(a, b)
        if r["kind"] == "prior":
            s, t = r["prior_source"], r["prior_target"]
            e1 = l1[(s, t)]
            d = 0.5 * r["doubt"] + 0.5 * e1["reversal_suspicion"]
            doubt[k] = round(d, 4)
            sg = [v.get("sign") for v in r["per_variant"].values()]
            # the sign is stated for the direction each variant chose; use it only if both point the stated way
            dirs_ok = all(v["direction"] == f"{SHORT[s]}->{SHORT[t]}" for v in r["per_variant"].values())
            if dirs_ok and len(set(sg)) == 1 and sg[0] in ("+", "-"):
                sign[k] = 1 if sg[0] == "+" else -1
                ps = {"positive": "+", "negative": "-"}.get(prior_sign := next(e["sign"] for e in prior if (e["source"], e["target"]) == (s, t)))
                if ps:
                    sign_cmp["agree" if ps == sg[0] else "disagree"] += 1
                else:
                    sign_cmp[f"prior_{prior_sign}"] += 1
            lag_c[r["lag_majority"]] += 1
            table.append({"edge": f"{SHORT[s]}->{SHORT[t]}", "doubt": round(d, 3), "L4_doubt": round(r["doubt"], 3),
                          "L4_support": round(r["support_mean"], 3), "L4_direction": r["direction_majority"],
                          "L4_lag": r["lag_majority"], "L1_reversal_suspicion": round(e1["reversal_suspicion"], 3),
                          "L1_variants_reversing": e1["n_variants_reversing"], "sign_hint": sign.get(k)})
        else:
            suspicion[k] = round(r["suspicion"], 4)
    for a, b in itertools.combinations(NODES, 2):
        k = key(a, b)
        if k not in adj and k not in suspicion:
            suspicion[k] = 0.0
    table.sort(key=lambda x: -x["doubt"])
    out = {"node_order": NODES, "pair_key": "u-v with u < v, indices into node_order",
           "doubt": doubt, "suspicion": suspicion, "sign": sign, "prior_edge_table": table,
           "provenance": "experiments/ext/llm/export_side_info.py from results/ext_llm_edges/edges.json and results/ext_llm_order/order.json"}
    (ROOT / "results/ext_llm_edges/textinfo_side_info.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for x in table:
        print(x)
    print("sign hints:", len(sign), dict(sign_cmp), "| lag of prior edges (L4 majority):", dict(lag_c))
    top = sorted(((v, k) for k, v in suspicion.items() if v > 0), reverse=True)[:8]
    print("top suspicion:", [(SHORT[NODES[int(k.split('-')[0])]], SHORT[NODES[int(k.split('-')[1])]], v) for v, k in top])


if __name__ == "__main__":
    main()
