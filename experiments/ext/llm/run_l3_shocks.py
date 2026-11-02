"""L3: text-derived policy shock events and quarterly proxy series (direction "llm").

Chunk selection (105 chunks): policy_shock_flag in {True, "yes"} (75) OR the chunk carries a Paper 1
relation with sign == "policy_shock" OR a policy keyword matches (decree/circular/credit quota/policy
rate/OMO/restructuring...). Each chunk is sent once per prompt variant (A: English instructions,
B: Vietnamese instructions with a different schema order); the LLM returns a list of dated policy
ACTIONS with quarter, stance, the core variable hit, direction on it, magnitude class and a verbatim quote.

Aggregation: events are kept only if the quarter is explicit and the quote is found verbatim in the
chunk (light normalisation); events from both variants are matched per chunk on
(quarter, target, direction). Duplicates across chunks (same quarter, target, direction) are merged into
one event cluster carrying all chunk ids. Series over the 19 panel quarters (2020Q2..2024Q4):
  shock_<VAR>[q] = sum over clusters hitting VAR in q of direction * magnitude (small 1, medium 2, large 3)
plus a monetary-stance index (easing -, tightening +, weighted by magnitude).
"consensus" series use only events found by both variants; "union" series use all verified events.

Outputs: results/ext_llm_shocks/events.json (every event with chunk ids, quotes and variant support),
shocks.csv (consensus series), shocks_union.csv, raw.jsonl, summary.json.
Run: python experiments/ext/llm/run_l3_shocks.py
"""
from __future__ import annotations

import collections
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (NODES, QUARTERS, ROOT, SHORT, FROM_SHORT, ask, calls_used, chunk_text, fmt_chunk,  # noqa: E402
                    load_chunks, load_relations, parse_json, run_parallel)

OUT = ROOT / "results" / "ext_llm_shocks"
KW = re.compile(r"thông tư|nghị định|nghị quyết|quyết định số|lãi suất điều hành|tái cấp vốn|tái chiết khấu|room tín dụng|"
                r"hạn mức (?:tăng trưởng )?tín dụng|chỉ tiêu tăng trưởng tín dụng|cơ cấu lại (?:thời hạn trả )?nợ|giãn nợ|"
                r"gói hỗ trợ|NHNN (?:giảm|tăng|hạ|nâng|điều chỉnh)|cắt giảm lãi suất|tăng lãi suất|giảm lãi suất|\bomo\b|"
                r"tín phiếu|dự trữ bắt buộc", re.I)
VARS = ", ".join(f"{SHORT[n]}" for n in NODES)
MAG = {"small": 1, "medium": 2, "large": 3}


def select(chunks, rels):
    flag = {c["rag_id"] for c in chunks if str(c.get("policy_shock_flag")).lower() in ("true", "yes")}
    ps = {r["chunk_id"] for r in rels if r["relation"]["sign"] == "policy_shock"}
    kw = {c["rag_id"] for c in chunks if KW.search(chunk_text(c))}
    ids = flag | ps | kw
    return [c for c in chunks if c["rag_id"] in ids], {"flag": len(flag), "paper1_policy_shock": len(ps), "keyword": len(kw), "union": len(ids)}


def prompt_a(c):
    return [{"role": "system", "content": "You extract dated economic-policy actions from Vietnamese financial text. "
                                          "You never invent dates. Respond with one JSON object only."},
            {"role": "user", "content": f"""Text chunk:
{fmt_chunk(c)}

List every concrete POLICY ACTION described in this chunk that was taken by an authority (State Bank of Vietnam, Government, Ministry of Finance, SSC, National Assembly): policy rate changes, OMO/bill operations, credit growth quotas ("room"), prudential rules (circulars on capital, LDR, provisioning, debt restructuring/forbearance), decrees on bonds or real estate, fiscal support packages. Ignore market outcomes, forecasts, definitions and plans without a date.

For each action give:
- "quarter": quarter in which the action took effect or was announced, as "YYYYQn"; null if the text does not let you determine it (do not guess from the publication date unless the text says the action happened then)
- "date_text": the date expression in the text
- "policy_type": "policy_rate" | "omo_liquidity" | "credit_quota" | "prudential_rule" | "debt_restructuring" | "bond_market_rule" | "fiscal_support" | "other"
- "stance": "easing" | "tightening" | "neutral"   (for credit/financial conditions)
- "target": the ONE most directly affected variable among [{VARS}] or "OTHER"
- "effect_direction": "+" or "-" (expected direction of the action's effect on that target variable)
- "magnitude": "small" | "medium" | "large"   (policy rate: <=25bp small, 50bp medium, >=100bp or cumulative large; rules/packages by scope)
- "quote": a short VERBATIM quote from the chunk that states the action
- "confidence": number in [0,1]
Return {{"events": [ ... ]}} (empty list if none)."""}]


def prompt_b(c):
    return [{"role": "system", "content": "Bạn trích xuất các hành động chính sách có ngày tháng từ văn bản tài chính tiếng Việt. "
                                          "Không bao giờ bịa ngày. Chỉ trả về một đối tượng JSON."},
            {"role": "user", "content": f"""Đoạn văn bản:
{fmt_chunk(c)}

Hãy liệt kê các hành động chính sách CỤ THỂ do cơ quan có thẩm quyền thực hiện (NHNN, Chính phủ, Bộ Tài chính, UBCKNN, Quốc hội) được nêu trong đoạn: điều chỉnh lãi suất điều hành, nghiệp vụ OMO/tín phiếu, chỉ tiêu/room tăng trưởng tín dụng, quy định an toàn (thông tư về vốn, LDR, trích lập dự phòng, cơ cấu lại nợ), nghị định về trái phiếu hay bất động sản, gói hỗ trợ tài khóa. Bỏ qua diễn biến thị trường, dự báo, định nghĩa, kế hoạch không có thời điểm.

Mỗi hành động là một đối tượng với các khóa theo đúng thứ tự:
- "quote": câu trích NGUYÊN VĂN nêu hành động
- "date_text": cách văn bản ghi thời điểm
- "quarter": quý hành động có hiệu lực hoặc được công bố, dạng "YYYYQn"; null nếu văn bản không cho biết
- "policy_type": "policy_rate" | "omo_liquidity" | "credit_quota" | "prudential_rule" | "debt_restructuring" | "bond_market_rule" | "fiscal_support" | "other"
- "stance": "easing" (nới lỏng) | "tightening" (thắt chặt) | "neutral"
- "target": MỘT biến chịu tác động trực tiếp nhất trong [{VARS}] hoặc "OTHER"
- "effect_direction": "+" hoặc "-" (chiều tác động kỳ vọng lên biến đó)
- "magnitude": "small" | "medium" | "large" (lãi suất: <=25bp nhỏ, 50bp vừa, >=100bp hoặc cộng dồn lớn)
- "confidence": số trong [0,1]
Trả về {{"events": [ ... ]}} (danh sách rỗng nếu không có)."""}]


def _norm(s):
    s = unicodedata.normalize("NFC", str(s or "")).lower()
    return re.sub(r"[\s\.,;:\"'“”…()\-–]+", " ", s).strip()


def verify_quote(q, c):
    if not q:
        return False
    nq, nt = _norm(q), _norm(chunk_text(c))
    if nq and nq in nt:
        return True
    words = nq.split()  # tolerate small edits: 80% of 6-gram windows present
    if len(words) < 6:
        return False
    grams = [" ".join(words[i:i + 6]) for i in range(len(words) - 5)]
    return sum(g in nt for g in grams) / len(grams) >= 0.8


def query(item):
    c, v = item
    msgs = prompt_a(c) if v == "A" else prompt_b(c)
    txt = ask(msgs, tag=f"L3{v}:{c['rag_id']}")
    ans = parse_json(txt)
    if ans is None:
        txt = ask(msgs + [{"role": "user", "content": "Return only valid JSON."}], tag=f"L3{v}-retry:{c['rag_id']}")
        ans = parse_json(txt)
    evs = ans.get("events", []) if isinstance(ans, dict) else (ans if isinstance(ans, list) else [])
    return [e for e in evs if isinstance(e, dict)]


def clean(e, c, v):
    q = e.get("quarter")
    q = q.strip().upper().replace("-", "").replace(" ", "") if isinstance(q, str) else None
    if not (q and re.fullmatch(r"20\d\dQ[1-4]", q)):
        q = None
    tgt = e.get("target") if e.get("target") in FROM_SHORT else "OTHER"
    d = str(e.get("effect_direction") or "").strip()
    d = "+" if d.startswith("+") else "-" if d.startswith("-") else None
    try:
        conf = float(e.get("confidence"))
    except (TypeError, ValueError):
        conf = None
    return {"chunk_id": c["rag_id"], "variant": v, "quarter": q, "date_text": e.get("date_text"),
            "policy_type": e.get("policy_type"), "stance": e.get("stance"), "target": tgt, "direction": d,
            "magnitude": e.get("magnitude") if e.get("magnitude") in MAG else "small", "quote": e.get("quote"),
            "quote_verified": verify_quote(e.get("quote"), c), "confidence": conf}


def series(clusters, key):
    rows = []
    for q in QUARTERS:
        row = {"quarter": q}
        for n in NODES:
            row[f"shock_{SHORT[n]}"] = sum((1 if k["direction"] == "+" else -1) * MAG[k["magnitude"]]
                                           for k in clusters if k["quarter"] == q and k["target"] == SHORT[n] and k[key])
        row["monetary_stance"] = sum({"tightening": 1, "easing": -1}.get(k["stance"], 0) * MAG[k["magnitude"]]
                                     for k in clusters if k["quarter"] == q and k[key] and
                                     k["policy_type"] in ("policy_rate", "omo_liquidity", "credit_quota"))
        row["n_events"] = sum(1 for k in clusters if k["quarter"] == q and k[key])
        rows.append(row)
    return rows


def main():
    chunks, rels = load_chunks(), load_relations()
    sel, counts = select(chunks, rels)
    before = calls_used()
    items = [(c, v) for c in sel for v in ("A", "B")]
    res = run_parallel(query, items, workers=8)
    OUT.mkdir(parents=True, exist_ok=True)
    events = []
    with (OUT / "raw.jsonl").open("w", encoding="utf-8") as f:
        for (c, v), evs in zip(items, res):
            f.write(json.dumps({"chunk_id": c["rag_id"], "variant": v, "events": evs}, ensure_ascii=False) + "\n")
            events += [clean(e, c, v) for e in evs]
    usable = [e for e in events if e["quarter"] and e["direction"] and e["quote_verified"]]
    # match variants within a chunk on (quarter, target, direction)
    keyf = lambda e: (e["chunk_id"], e["quarter"], e["target"], e["direction"])  # noqa: E731
    byv = {v: {keyf(e) for e in usable if e["variant"] == v} for v in ("A", "B")}
    for e in events:
        e["matched_other_variant"] = keyf(e) in byv["B" if e["variant"] == "A" else "A"]
    # cluster across chunks on (quarter, target, direction)
    cl = collections.defaultdict(list)
    for e in usable:
        cl[(e["quarter"], e["target"], e["direction"])].append(e)
    clusters = []
    for (q, t, d), es in sorted(cl.items()):
        mags = collections.Counter(e["magnitude"] for e in es)
        types = collections.Counter(e["policy_type"] for e in es)
        stances = collections.Counter(e["stance"] for e in es)
        clusters.append({"quarter": q, "target": t, "direction": d, "magnitude": max(mags, key=lambda m: (mags[m], MAG[m])),
                         "policy_type": types.most_common(1)[0][0], "stance": stances.most_common(1)[0][0],
                         "chunk_ids": sorted({e["chunk_id"] for e in es}),
                         "variants": sorted({e["variant"] for e in es}),
                         "consensus": {"A", "B"} <= {e["variant"] for e in es},
                         "in_panel_window": q in QUARTERS,
                         "quotes": sorted({e["quote"] for e in es})[:4], "union": True})
    for name, key in (("shocks.csv", "consensus"), ("shocks_union.csv", "union")):
        rows = series(clusters, key)
        with (OUT / name).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    na, nb = len(byv["A"]), len(byv["B"])
    inter = len(byv["A"] & byv["B"])
    summary = {"chunk_selection": counts, "n_chunks": len(sel), "calls_this_run": calls_used() - before,
               "n_events_raw": len(events), "n_events_usable": len(usable),
               "n_without_quarter": sum(1 for e in events if not e["quarter"]),
               "n_quote_not_verified": sum(1 for e in events if not e["quote_verified"]),
               "usable_keys_A": na, "usable_keys_B": nb, "keys_both": inter,
               "jaccard_A_B": inter / (na + nb - inter) if na + nb - inter else None,
               "n_clusters": len(clusters), "n_clusters_consensus": sum(k["consensus"] for k in clusters),
               "n_clusters_in_window": sum(k["in_panel_window"] for k in clusters),
               "n_clusters_consensus_in_window": sum(k["in_panel_window"] and k["consensus"] for k in clusters)}
    (OUT / "events.json").write_text(json.dumps({"summary": summary, "clusters": clusters, "events": events},
                                                ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
