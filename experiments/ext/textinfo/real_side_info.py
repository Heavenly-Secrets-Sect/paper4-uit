"""Real-case side information from Paper 1's stored text evidence, on the 14 core nodes. DESCRIPTIVE ONLY.

Read-only inputs (ACIIDS repository, never modified; no .env, no LLM, no network):
- 01_paper1_foundation/prior_graph/prior_graph_final_278.json        42 prior edges ("source|target")
- 01_paper1_foundation/prior_graph/pipeline_output_raw_278chunk.jsonl 124 extracted relations
- 01_paper1_foundation/rag_kb/rag_kb_full_content.jsonl               278 chunks

Rule-based signals (no learning, no LLM):
- doubt per prior edge on the core nodes: 1 - confidence; a single distinct source; the
  ``conflicted`` flag; verifier-rejected relations on the pair; a relation extracted in the opposite
  direction; accepted instances with opposite signs;
- suspicion per core pair OUTSIDE the prior: chunks whose stored ``candidate_nodes`` list both nodes;
  chunks where a hand-written keyword lexicon matches both nodes; relations extracted on the pair but
  rejected by the verifier (or accepted but not in the final prior); a TF-IDF cosine between the
  bag-of-chunks profiles of the two nodes (which chunks mention each node, weighted by chunk rarity);
- sign hints (positive / negative; ``policy_shock`` is a label, not a sign) and lag hints
  (``immediate`` -> lag 0, ``1_quarter`` -> lag 1, ``unknown`` -> none) from accepted relations.

The composite scores are heuristic; the module only uses their ranks. There is no ground truth on the
real case, so nothing here measures quality or effect.

Run:  python experiments/ext/textinfo/real_side_info.py   (writes results/ext_textinfo_real/)
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P1 = Path("/Users/kietnt/Desktop/Workspace/ACIIDS/01_paper1_foundation")
OUT = ROOT / "results" / "ext_textinfo_real"

# Core 14 nodes: the node list of every D-07 topology (data/topology_bank).
CORE = json.loads((ROOT / "data/topology_bank/D-07/topologies/synthetic_dag_00.json").read_text())["nodes"]

# Keyword lexicon (Vietnamese + English). Acronyms are matched case-sensitively as whole words.
LEXICON = {
    "bank_npl_ratio": ["nợ xấu", r"\bNPL\b"],
    "bank_car_ratio": [r"\bCAR\b", "an toàn vốn", r"\bBasel"],
    "bank_nim_ratio": [r"\bNIM\b", "biên lãi"],
    "bank_roe_ratio": [r"\bROE\b"],
    "bank_ldr_ratio": [r"\bLDR\b", "cho vay/huy động", "cho vay trên huy động"],
    "bank_provision_coverage_proxy_pct": ["bao phủ nợ xấu", r"\bLLR\b", "dự phòng"],
    "bank_z_score": [r"[Zz]-?score"],
    "macro_gdp_yoy_pct": [r"\bGDP\b", "tăng trưởng kinh tế"],
    "macro_cpi_avg_pct": [r"\bCPI\b", "lạm phát"],
    "macro_policy_rate_pct": ["lãi suất điều hành", "lãi suất tái cấp vốn", "tái chiết khấu", "lãi suất chính sách",
                              "hạ lãi suất", "tăng lãi suất", "policy rate"],
    "stock_adj_close_last_vnd": [r"VN-?Index", "giá cổ phiếu"],
    "stock_return_qoq_pct": ["tỷ suất sinh lời", "lợi suất cổ phiếu", r"VN-?Index (?:tăng|giảm)"],
    "stock_avg_daily_volume_cp": ["khối lượng giao dịch", "khối lượng khớp", "thanh khoản"],
    "stock_avg_daily_trade_value_vnd": ["giá trị giao dịch", "giá trị khớp", "thanh khoản"],
}


def _compile(pat: str):
    acronym = pat.startswith(r"\b") or any(c.isupper() for c in pat)
    return re.compile(pat if acronym else re.escape(pat), 0 if acronym else re.IGNORECASE)


def load():
    prior = json.loads((P1 / "prior_graph/prior_graph_final_278.json").read_text(encoding="utf-8"))
    raw = [json.loads(line) for line in (P1 / "prior_graph/pipeline_output_raw_278chunk.jsonl").open(encoding="utf-8")]
    chunks = [json.loads(line) for line in (P1 / "rag_kb/rag_kb_full_content.jsonl").open(encoding="utf-8")]
    return prior, [r for r in raw if r.get("record_type") == "relation"], chunks


def main() -> int:
    prior, rels, chunks = load()
    core = set(CORE)
    edges = {}
    for key, meta in prior.items():
        a, b = key.split("|")
        if a in core and b in core:
            edges[(a, b)] = meta
    edge_pairs = {frozenset(e) for e in edges}

    # relations per unordered core pair
    by_pair = defaultdict(list)
    for r in rels:
        a, b = r["relation"]["source_node"], r["relation"]["target_node"]
        if a in core and b in core and a != b:
            by_pair[frozenset((a, b))].append(r)

    # chunk-level node mentions: stored candidate_nodes, and lexicon matches
    pats = {n: [_compile(p) for p in LEXICON[n]] for n in CORE}
    cand_sets, lex_sets = [], []
    for c in chunks:
        cn = {x.strip() for x in (c.get("candidate_nodes") or "").split(",")} & core
        text = f"{c.get('headline') or ''} {c.get('chunk_content') or ''}"
        lx = {n for n in CORE if any(p.search(text) for p in pats[n])}
        cand_sets.append(cn)
        lex_sets.append(lx)

    # TF-IDF profile of each node over chunks (mentioned by candidate_nodes OR lexicon)
    mentions = [cs | ls for cs, ls in zip(cand_sets, lex_sets)]
    df = [len(m) for m in mentions]
    vec = {n: {i: math.log(1 + len(CORE) / max(df[i], 1)) for i, m in enumerate(mentions) if n in m} for n in CORE}

    def cosine(u, v):
        a, b = vec[u], vec[v]
        num = sum(a[i] * b[i] for i in set(a) & set(b))
        den = math.sqrt(sum(x * x for x in a.values())) * math.sqrt(sum(x * x for x in b.values()))
        return num / den if den else 0.0

    # ---- doubt per prior edge
    doubt_rows = []
    for (a, b), meta in sorted(edges.items()):
        rs = by_pair[frozenset((a, b))]
        n_rej = sum(r["final_status"] == "rejected" for r in rs)
        reverse = sum(r["relation"]["source_node"] == b for r in rs)
        signs = {r["relation"]["sign"] for r in rs if r["final_status"] == "accepted"} & {"positive", "negative"}
        sign_disagree = len(signs) > 1
        single = meta["n_distinct_sources"] <= 1
        score = ((1 - meta["confidence"]) + 0.5 * single + 0.5 * bool(meta["conflicted"]) + 0.25 * min(n_rej, 2)
                 + 0.5 * (reverse > 0) + 0.25 * sign_disagree)
        lag = Counter(r["relation"]["lag_hint"] for r in rs if r["final_status"] == "accepted")
        doubt_rows.append({"edge": f"{a}->{b}", "confidence": meta["confidence"],
                           "n_distinct_sources": meta["n_distinct_sources"], "conflicted": meta["conflicted"],
                           "n_rejected": n_rej, "n_reverse_direction": reverse, "sign_disagree": sign_disagree,
                           "sign_hint": meta["sign"] if meta["sign"] in ("positive", "negative") else None,
                           "lag_hints": dict(lag), "doubt": round(score, 3)})

    # ---- suspicion per non-edge core pair
    sus_rows = []
    for i, u in enumerate(CORE):
        for v in CORE[i + 1:]:
            p = frozenset((u, v))
            if p in edge_pairs:
                continue
            rs = by_pair[p]
            cm_cand = sum(u in s and v in s for s in cand_sets)
            cm_lex = sum(u in s and v in s for s in lex_sets)
            n_rej = sum(r["final_status"] == "rejected" for r in rs)
            n_acc = sum(r["final_status"] == "accepted" for r in rs)  # accepted but not in the final prior
            tfidf = cosine(u, v)
            score = 1.0 * (n_rej > 0) + 1.0 * (n_acc > 0) + math.log1p(cm_cand) + 0.5 * math.log1p(cm_lex) + tfidf
            sus_rows.append({"pair": f"{u}--{v}", "comention_candidate_nodes": cm_cand, "comention_lexicon": cm_lex,
                             "n_rejected_relations": n_rej, "n_accepted_not_in_prior": n_acc,
                             "tfidf_cosine": round(tfidf, 3), "suspicion": round(score, 3)})

    OUT.mkdir(parents=True, exist_ok=True)
    idx = {n: k for k, n in enumerate(CORE)}

    def key_of(a, b):
        x, y = sorted((idx[a], idx[b]))
        return f"{x}-{y}"

    side = {"nodes": CORE,
            "skeleton_oriented": [[idx[a], idx[b]] for a, b in sorted(edges)],
            "doubt": {key_of(*r["edge"].split("->")): r["doubt"] for r in doubt_rows},
            "suspicion": {key_of(*r["pair"].split("--")): r["suspicion"] for r in sus_rows},
            "sign": {key_of(*r["edge"].split("->")): (1 if r["sign_hint"] == "positive" else -1)
                     for r in doubt_rows if r["sign_hint"]},
            "edges_detail": doubt_rows, "pairs_detail": sus_rows,
            "note": "Heuristic, rule-based scores from Paper 1's stored fields; no ground truth; descriptive only."}
    (OUT / "side_info.json").write_text(json.dumps(side, indent=1, ensure_ascii=False), encoding="utf-8")

    # ---- inventory
    n_e, n_o = len(doubt_rows), len(sus_rows)
    lowconf = sum(r["confidence"] < 0.6 for r in doubt_rows)
    single = sum(r["n_distinct_sources"] <= 1 for r in doubt_rows)
    confl = sum(bool(r["conflicted"]) for r in doubt_rows)
    rej = sum(r["n_rejected"] > 0 for r in doubt_rows)
    rev = sum(r["n_reverse_direction"] > 0 for r in doubt_rows)
    sdis = sum(r["sign_disagree"] for r in doubt_rows)
    any_doubt = sum((r["confidence"] < 0.6) or r["n_distinct_sources"] <= 1 or r["conflicted"] or r["n_rejected"] > 0
                    or r["n_reverse_direction"] > 0 or r["sign_disagree"] for r in doubt_rows)
    no_signal = n_e - any_doubt
    signs = sum(r["sign_hint"] is not None for r in doubt_rows)
    lag_imm = sum(r["lag_hints"].get("immediate", 0) > 0 for r in doubt_rows)
    lag_1q = sum(r["lag_hints"].get("1_quarter", 0) > 0 for r in doubt_rows)
    cm_c = sum(r["comention_candidate_nodes"] > 0 for r in sus_rows)
    cm_l = sum(r["comention_lexicon"] > 0 for r in sus_rows)
    cm_any = sum(r["comention_candidate_nodes"] > 0 or r["comention_lexicon"] > 0 for r in sus_rows)
    s_rej = sum(r["n_rejected_relations"] > 0 for r in sus_rows)
    s_acc = sum(r["n_accepted_not_in_prior"] > 0 for r in sus_rows)
    distinct_doubt = len({r["doubt"] for r in doubt_rows})
    distinct_sus = len({r["suspicion"] for r in sus_rows})
    nodes_mentioned = Counter(n for m in mentions for n in m)

    L = ["# ext_textinfo_real: side information the real case would provide (descriptive, no ground truth)", "",
         f"Core nodes: {len(CORE)}. Prior edges with both ends in the core: **{n_e}** (of {len(prior)}). "
         f"Core pairs outside the prior: **{n_o}**. Chunks: {len(chunks)}; relations: {len(rels)} "
         f"({sum(r['final_status'] == 'accepted' for r in rels)} accepted, "
         f"{sum(r['final_status'] == 'rejected' for r in rels)} rejected), "
         f"{sum(len(v) for v in by_pair.values())} of them between two distinct core nodes.", "",
         "## Doubt signals on the prior edges", "",
         "| signal | edges |", "|---|---|",
         f"| confidence < 0.6 | {lowconf} |", f"| single distinct source | {single} |", f"| conflicted | {confl} |",
         f"| >= 1 verifier-rejected relation on the pair | {rej} |",
         f"| relation also extracted in the opposite direction | {rev} |",
         f"| accepted instances with opposite signs | {sdis} |",
         f"| **any doubt signal** | **{any_doubt} / {n_e}** |", f"| no doubt signal | {no_signal} |",
         f"| distinct composite doubt values (ties reduce ranking resolution) | {distinct_doubt} |", "",
         "## Suspicion signals on core pairs outside the prior", "",
         "| signal | pairs |", "|---|---|",
         f"| co-mentioned in >= 1 chunk (stored `candidate_nodes`) | {cm_c} |",
         f"| co-mentioned in >= 1 chunk (keyword lexicon) | {cm_l} |",
         f"| **co-mentioned by either** | **{cm_any} / {n_o}** |",
         f"| >= 1 relation extracted on the pair but rejected | {s_rej} |",
         f"| >= 1 relation accepted on the pair but absent from the final prior | {s_acc} |",
         f"| distinct composite suspicion values | {distinct_sus} |", "",
         "## Sign and lag hints (prior edges)", "",
         f"- Sign hint (positive/negative): {signs} / {n_e} edges; the rest are `policy_shock` (a label, not a sign).",
         f"- Lag hint `immediate` on >= 1 accepted relation: {lag_imm} edges; `1_quarter`: {lag_1q} edges; "
         "everything else `unknown`. Lag hints are therefore almost uninformative.", "",
         "## Mentions per core node (chunks, candidate_nodes or lexicon)", "",
         "| node | chunks |", "|---|---|"] + [f"| {n} | {nodes_mentioned.get(n, 0)} |" for n in CORE] + [
         "", "## Prior edges by doubt (highest first)", "",
         "| edge | conf | sources | conflicted | rejected | reverse | sign | doubt |", "|---|---|---|---|---|---|---|---|"] + [
         f"| {r['edge']} | {r['confidence']} | {r['n_distinct_sources']} | {r['conflicted']} | {r['n_rejected']} | "
         f"{r['n_reverse_direction']} | {r['sign_hint'] or '-'} | {r['doubt']} |"
         for r in sorted(doubt_rows, key=lambda r: -r["doubt"])] + [
         "", "## Top 15 non-prior pairs by suspicion", "",
         "| pair | co-mention (cand) | co-mention (lex) | rejected | accepted-not-in-prior | tf-idf | suspicion |",
         "|---|---|---|---|---|---|---|"] + [
         f"| {r['pair']} | {r['comention_candidate_nodes']} | {r['comention_lexicon']} | {r['n_rejected_relations']} | "
         f"{r['n_accepted_not_in_prior']} | {r['tfidf_cosine']} | {r['suspicion']} |"
         for r in sorted(sus_rows, key=lambda r: -r["suspicion"])[:15]]
    (OUT / "inventory.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:40]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
