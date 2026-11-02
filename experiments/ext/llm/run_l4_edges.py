"""L4-lite: per-pair edge adjudication grounded in Paper 1 chunks (direction "llm").

Pairs: the 21 prior edges induced on the 14 core nodes + up to 40 candidate missing pairs (co-mentioned
in >= 2 chunks by the lexical matcher in common.py, absent from the 21-edge prior, ranked by number of
co-mentioning chunks). For each pair: retrieve chunks (co-mention first, plus Paper 1's evidence chunks
for that pair, plus single-node context if fewer than 3 co-mentions), then ask the LLM with two prompt
variants that differ in language, format and variable ORDER (variant A: X = alphabetically first node;
variant B: X and Y swapped), so a position bias cannot masquerade as agreement.

Output: results/ext_llm_edges/edges.json (+ raw.jsonl with every prompt/answer pair id).
Run: python experiments/ext/llm/run_l4_edges.py
"""
from __future__ import annotations

import collections
import itertools
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (DESC_EN, DESC_VI, NODES, ROOT, SHORT, ask, calls_used, fmt_chunk, load_chunks,  # noqa: E402
                    load_prior21, load_relations, node_hits, parse_json, run_parallel)

OUT = ROOT / "results" / "ext_llm_edges"
MAX_CHUNKS = 8
N_MISSING = 40


def build_pairs(chunks, prior, rels):
    hits = {c["rag_id"]: node_hits(c) for c in chunks}
    co = collections.defaultdict(list)
    for cid, h in hits.items():
        for a, b in itertools.combinations(sorted(h), 2):
            co[(a, b)].append(cid)
    p1ev = collections.defaultdict(list)
    for r in rels:
        s, t = r["relation"]["source_node"], r["relation"]["target_node"]
        if s in NODES and t in NODES and s != t:
            p1ev[tuple(sorted((s, t)))].append(r["chunk_id"])
    prior_keys = {tuple(sorted((e["source"], e["target"]))): e for e in prior}
    miss = sorted(((k, len(v)) for k, v in co.items() if k not in prior_keys and len(v) >= 2),
                  key=lambda kv: (-kv[1], kv[0]))[:N_MISSING]
    pairs = []
    for k, e in prior_keys.items():
        pairs.append({"pair": list(k), "kind": "prior", "prior_source": e["source"], "prior_target": e["target"],
                      "prior_sign": e["sign"], "prior_confidence": e["confidence"], "co_mentions": len(co.get(k, []))})
    for k, n in miss:
        pairs.append({"pair": list(k), "kind": "missing_candidate", "co_mentions": n})
    by_id = {c["rag_id"]: c for c in chunks}
    for p in pairs:
        a, b = p["pair"]
        k = (a, b)
        cm = sorted(co.get(k, []), key=lambda cid: -(hits[cid].get(a, 0) + hits[cid].get(b, 0)))
        ids = list(dict.fromkeys(p1ev.get(k, []) + cm))[:MAX_CHUNKS]
        if len(cm) < 3:
            for n in (a, b):
                single = sorted((cid for cid, h in hits.items() if n in h and cid not in ids), key=lambda cid: -hits[cid][n])
                ids += single[:2]
        p["chunk_ids"] = ids
        p["paper1_evidence_chunks"] = sorted(set(p1ev.get(k, [])))
        p["chunks"] = [by_id[i] for i in ids]
    return pairs


SYS_A = ("You are an expert in Vietnamese macro-finance and banking. You judge causal claims about aggregate "
         "quarterly series strictly from the provided Vietnamese text excerpts, using economic knowledge only to "
         "interpret them, and you say so when the text is insufficient. Respond with a single JSON object only.")


def prompt_a(x, y, chunks):
    ex = "\n\n".join(fmt_chunk(c) for c in chunks)
    return [{"role": "system", "content": SYS_A}, {"role": "user", "content": f"""Two quarterly aggregate variables for Vietnam (2020-2024), used as nodes of a dynamic structural model:
X = {SHORT[x]}: {DESC_EN[x]}
Y = {SHORT[y]}: {DESC_EN[y]}

Text excerpts (Vietnamese):
{ex}

Decide whether these excerpts support a DIRECT causal edge between X and Y (not mere co-movement, not only through another variable).
Return JSON with keys:
- "text_support": "supports_edge" | "contradicts_edge" | "insufficient"
- "direction": "X->Y" | "Y->X" | "both" | "unclear"   (as stated or clearly implied by the text)
- "sign": "+" | "-" | "mixed" | "unclear"   (sign of the effect in the stated direction)
- "lag": "same_quarter" | "later_quarters" | "both" | "unclear"
- "mediated": true if the text describes the link as running through another variable, else false
- "edge_confidence": number in [0,1], probability that a direct X-Y edge exists given the text
- "knowledge_direction": "X->Y" | "Y->X" | "both" | "none"   (your view from economics alone, ignoring the text)
- "evidence_ids": list of chunk ids you relied on (may be empty)
- "evidence_quote": a short verbatim quote, or ""
- "rationale": at most 40 words"""}]


SYS_B = ("Bạn là chuyên gia kinh tế vĩ mô, tài chính và ngân hàng Việt Nam. Bạn đánh giá quan hệ nhân quả giữa các "
         "chuỗi số liệu tổng hợp theo quý, chỉ dựa trên các đoạn văn bản được cung cấp. Chỉ trả về một đối tượng JSON.")


def prompt_b(x, y, chunks):
    ex = "\n\n".join(fmt_chunk(c) for c in chunks)
    return [{"role": "system", "content": SYS_B}, {"role": "user", "content": f"""Hai biến tổng hợp theo quý của Việt Nam (2020-2024):
X = {SHORT[x]}: {DESC_VI[x]}
Y = {SHORT[y]}: {DESC_VI[y]}

Các đoạn văn bản:
{ex}

Bước 1: trích nguyên văn tối đa 2 câu liên quan nhất đến quan hệ giữa X và Y (nếu không có thì để rỗng).
Bước 2: dựa trên các câu đó, phân bố xác suất cho 4 khả năng loại trừ nhau: X tác động trực tiếp lên Y; Y tác động trực tiếp lên X; tác động hai chiều; không có quan hệ trực tiếp (chỉ đồng biến, qua biến trung gian, hoặc văn bản không nói).
Bước 3: độ trễ của tác động nếu có.
Trả về JSON với các khóa:
- "quotes": danh sách câu trích, mỗi câu kèm id chunk dạng {{"id": "...", "text": "..."}}
- "p_x_to_y", "p_y_to_x", "p_both", "p_none": các số trong [0,1], tổng bằng 1
- "sign": "+" | "-" | "mixed" | "unclear"
- "lag": "same_quarter" | "later_quarters" | "both" | "unclear"
- "mediator": tên biến trung gian nếu văn bản nói tác động đi qua biến khác, nếu không thì ""
- "rationale": tối đa 40 từ"""}]


def norm_a(ans, x, y):
    """Variant A -> common schema in terms of the canonical pair (a, b) = sorted."""
    if not isinstance(ans, dict):
        return None
    conf = ans.get("edge_confidence")
    try:
        conf = float(conf)
    except (TypeError, ValueError):
        conf = None
    if conf is None:
        conf = {"supports_edge": 0.75, "contradicts_edge": 0.1}.get(ans.get("text_support"), 0.3)
    d = ans.get("direction")
    pdir = {"X->Y": (1.0, 0.0), "Y->X": (0.0, 1.0), "both": (0.5, 0.5)}.get(d, (0.5, 0.5))
    p_xy, p_yx = pdir
    return {"p_edge": conf, "p_xy_given_edge": p_xy, "p_yx_given_edge": p_yx,
            "dir_stated": d in ("X->Y", "Y->X", "both"), "both": d == "both",
            "support": ans.get("text_support"), "lag": ans.get("lag"), "sign": ans.get("sign"),
            "knowledge_direction": ans.get("knowledge_direction"), "mediated": bool(ans.get("mediated")),
            "evidence_ids": ans.get("evidence_ids") or []}


def norm_b(ans, x, y):
    if not isinstance(ans, dict):
        return None
    try:
        v = [max(0.0, float(ans.get(k) or 0)) for k in ("p_x_to_y", "p_y_to_x", "p_both", "p_none")]
    except (TypeError, ValueError):
        return None
    s = sum(v) or 1.0
    pxy, pyx, pb, pn = (t / s for t in v)
    pe = pxy + pyx + pb
    return {"p_edge": pe, "p_xy_given_edge": (pxy + 0.5 * pb) / pe if pe > 0 else 0.5,
            "p_yx_given_edge": (pyx + 0.5 * pb) / pe if pe > 0 else 0.5,
            "dir_stated": pe >= 0.5 and max(pxy, pyx, pb) >= 0.3, "both": pb > max(pxy, pyx),
            "support": "supports_edge" if pe >= 0.5 else "insufficient", "lag": ans.get("lag"), "sign": ans.get("sign"),
            "mediated": bool(ans.get("mediator")), "evidence_ids": [q.get("id") for q in ans.get("quotes") or [] if isinstance(q, dict)]}


def to_ab(n, x, y, a, b):
    """Re-express a normalised answer about (x, y) in terms of (a, b)."""
    if n is None:
        return None
    m = dict(n)
    if (x, y) == (a, b):
        m["p_ab"], m["p_ba"] = n["p_xy_given_edge"], n["p_yx_given_edge"]
    else:
        m["p_ab"], m["p_ba"] = n["p_yx_given_edge"], n["p_xy_given_edge"]
    if "knowledge_direction" in n and (x, y) != (a, b):
        m["knowledge_direction"] = {"X->Y": "Y->X", "Y->X": "X->Y"}.get(n["knowledge_direction"], n["knowledge_direction"])
    return m


def query(item):
    p, variant = item
    a, b = p["pair"]
    if variant == "A":
        x, y = a, b
        msgs = prompt_a(x, y, p["chunks"])
        txt = ask(msgs, tag=f"L4A:{a}|{b}", reasoning_effort="medium")
        ans = parse_json(txt)
        if ans is None:  # one retry with an explicit reminder (different prompt => different cache key)
            txt = ask(msgs + [{"role": "user", "content": "Return only valid JSON."}], tag=f"L4A-retry:{a}|{b}", reasoning_effort="medium")
            ans = parse_json(txt)
        return {"variant": "A", "x": x, "y": y, "raw": ans, "norm": to_ab(norm_a(ans, x, y), x, y, a, b)}
    x, y = b, a
    msgs = prompt_b(x, y, p["chunks"])
    txt = ask(msgs, tag=f"L4B:{a}|{b}", reasoning_effort="medium")
    ans = parse_json(txt)
    if ans is None:
        txt = ask(msgs + [{"role": "user", "content": "Chỉ trả về JSON hợp lệ."}], tag=f"L4B-retry:{a}|{b}", reasoning_effort="medium")
        ans = parse_json(txt)
    return {"variant": "B", "x": x, "y": y, "raw": ans, "norm": to_ab(norm_b(ans, x, y), x, y, a, b)}


def majority(vals):
    vals = [v for v in vals if v and v != "unclear"]
    if not vals:
        return "unclear"
    c = collections.Counter(vals).most_common()
    return c[0][0] if len(c) == 1 or c[0][1] > c[1][1] else "disagree"


def main():
    chunks, prior, rels = load_chunks(), load_prior21(), load_relations()
    pairs = build_pairs(chunks, prior, rels)
    before = calls_used()
    items = [(p, v) for p in pairs for v in ("A", "B")]
    res = run_parallel(query, items, workers=8)
    OUT.mkdir(parents=True, exist_ok=True)
    out_pairs = []
    with (OUT / "raw.jsonl").open("w", encoding="utf-8") as f:
        for (p, v), r in zip(items, res):
            f.write(json.dumps({"pair": p["pair"], "variant": v, "x": r["x"], "y": r["y"], "answer": r["raw"]}, ensure_ascii=False) + "\n")
    by_pair = collections.defaultdict(dict)
    for (p, v), r in zip(items, res):
        by_pair[tuple(p["pair"])][v] = r["norm"]
    for p in pairs:
        a, b = p["pair"]
        ns = {v: n for v, n in by_pair[(a, b)].items() if n is not None}
        pe = [n["p_edge"] for n in ns.values()]
        pab = [n["p_edge"] * n["p_ab"] for n in ns.values()]
        pba = [n["p_edge"] * n["p_ba"] for n in ns.values()]
        dirs = []
        for n in ns.values():
            if not n["dir_stated"]:
                dirs.append("unclear")
            elif n["both"]:
                dirs.append("both")
            else:
                dirs.append(f"{SHORT[a]}->{SHORT[b]}" if n["p_ab"] > n["p_ba"] else f"{SHORT[b]}->{SHORT[a]}")
        sup = ["yes" if n["p_edge"] >= 0.5 else "no" for n in ns.values()]
        rec = {k: v for k, v in p.items() if k != "chunks"}
        rec.update({
            "pair_short": [SHORT[a], SHORT[b]],
            "per_variant": {v: {k: n[k] for k in ("p_edge", "p_ab", "p_ba", "support", "lag", "sign", "mediated",
                                                  "evidence_ids", "knowledge_direction") if k in n} | {"direction": d}
                            for (v, n), d in zip(ns.items(), dirs)},
            "support_mean": statistics.mean(pe) if pe else None,
            "p_ab_mean": statistics.mean(pab) if pab else None,
            "p_ba_mean": statistics.mean(pba) if pba else None,
            "support_agree": len(set(sup)) == 1 if len(sup) == 2 else None,
            "direction_majority": majority(dirs),
            "direction_agree": (len(set(dirs)) == 1 and dirs[0] != "unclear") if len(dirs) == 2 else None,
            "lag_majority": majority([n["lag"] for n in ns.values()]),
            "lag_agree": len({n["lag"] for n in ns.values()}) == 1 if len(ns) == 2 else None,
        })
        if p["kind"] == "prior":
            s, t = p["prior_source"], p["prior_target"]
            p_stated = rec["p_ab_mean"] if (s, t) == (a, b) else rec["p_ba_mean"]
            p_rev = rec["p_ba_mean"] if (s, t) == (a, b) else rec["p_ab_mean"]
            rec.update({"p_stated_direction": p_stated, "p_reversed_direction": p_rev,
                        "doubt": 1.0 - p_stated if p_stated is not None else None,
                        "reversal_score": (p_rev / (p_rev + p_stated)) if p_stated is not None and (p_rev + p_stated) > 0 else 0.5})
        else:
            rec["suspicion"] = rec["support_mean"]
        out_pairs.append(rec)
    summary = {
        "n_pairs": len(out_pairs), "n_prior": sum(r["kind"] == "prior" for r in out_pairs),
        "n_missing_candidates": sum(r["kind"] != "prior" for r in out_pairs),
        "support_agreement": statistics.mean(r["support_agree"] for r in out_pairs if r["support_agree"] is not None),
        "direction_agreement_when_both_state": None, "lag_agreement": statistics.mean(r["lag_agree"] for r in out_pairs if r["lag_agree"] is not None),
        "calls_this_run": calls_used() - before,
    }
    both = [r for r in out_pairs if all(v["direction"] != "unclear" for v in r["per_variant"].values()) and len(r["per_variant"]) == 2]
    if both:
        summary["direction_agreement_when_both_state"] = statistics.mean(r["direction_agree"] for r in both)
        summary["n_pairs_both_state_direction"] = len(both)
    pe_a = [r["per_variant"]["A"]["p_edge"] for r in out_pairs if set(r["per_variant"]) == {"A", "B"}]
    pe_b = [r["per_variant"]["B"]["p_edge"] for r in out_pairs if set(r["per_variant"]) == {"A", "B"}]
    from scipy.stats import spearmanr
    summary["support_spearman_A_vs_B"] = float(spearmanr(pe_a, pe_b).statistic)
    (OUT / "edges.json").write_text(json.dumps({"model": "gpt-5-mini-2025-08-07", "summary": summary, "pairs": out_pairs},
                                               ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
