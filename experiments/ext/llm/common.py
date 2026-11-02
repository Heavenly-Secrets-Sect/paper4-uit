"""Shared helpers for direction "llm" (docs/ext/llm.md).

Every LLM request goes through ``paper4.llm.chat`` (store=False, Singapore egress check, disk cache).
This module only adds: a budget counter (cache hits are free and not counted), a hard cap, robust
JSON parsing, the 14 core nodes with descriptions/synonyms, and lexical chunk retrieval.

Text sources (read-only): ACIIDS/01_paper1_foundation (rag_kb, prior_graph, evaluation_benchmark).
Node set: ACIIDS/02_observational_data/processed/core14_provenance.json ("nodes"), window "defensible"
(2020Q2..2024Q4, 19 quarters). Prior: the induced subgraph of prior_graph_final_278.json on these 14
nodes (21 of 42 edges), as in ACIIDS/03_causal_discovery/scripts/prior_extraction.py.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4 import llm as _llm  # noqa: E402  (the ONLY way to reach the LLM)

ACIIDS = Path("/Users/kietnt/Desktop/Workspace/ACIIDS")
P1 = ACIIDS / "01_paper1_foundation"
CHUNKS_PATH = P1 / "rag_kb" / "rag_kb_full_content.jsonl"
RELS_PATH = P1 / "prior_graph" / "pipeline_output_raw_278chunk.jsonl"
PRIOR_PATH = P1 / "prior_graph" / "prior_graph_final_278.json"
GOLD_PATH = P1 / "evaluation_benchmark" / "ground_truth_v1.2_draft.jsonl"
PROV_PATH = ACIIDS / "02_observational_data" / "processed" / "core14_provenance.json"
MATRIX_PATH = ACIIDS / "02_observational_data" / "processed" / "candidate_quarterly_matrix_raw.csv"

MODEL = "gpt-5-mini-2025-08-07"
BUDGET = 1500
META = ROOT / "results" / "ext_llm_meta"
CALL_LOG = META / "call_log.jsonl"
_LOCK = threading.Lock()

# --- nodes -------------------------------------------------------------------------------------
NODES = json.loads(PROV_PATH.read_text(encoding="utf-8"))["nodes"]
QUARTERS = json.loads(PROV_PATH.read_text(encoding="utf-8"))["windows"]["defensible"]["quarters"]
assert len(NODES) == 14 and len(QUARTERS) == 19

DESC_EN = {
    "bank_npl_ratio": "Banking-sector non-performing loan (NPL) ratio, %",
    "bank_car_ratio": "Banking-sector capital adequacy ratio (CAR), %",
    "bank_nim_ratio": "Banking-sector net interest margin (NIM), %",
    "bank_roe_ratio": "Banking-sector return on equity (ROE), %",
    "bank_ldr_ratio": "Banking-sector loan-to-deposit ratio (LDR), %",
    "bank_provision_coverage_proxy_pct": "Banking-sector loan-loss provision coverage of NPLs, %",
    "bank_z_score": "Banking-sector Z-score (distance to insolvency, bank stability)",
    "macro_gdp_yoy_pct": "Vietnam real GDP growth, year-on-year %",
    "macro_cpi_avg_pct": "Vietnam CPI inflation (quarterly average), %",
    "macro_policy_rate_pct": "State Bank of Vietnam policy (refinancing) rate, %",
    "stock_adj_close_last_vnd": "Stock price level (adjusted close of listed stocks, quarter end)",
    "stock_return_qoq_pct": "Stock return, quarter-on-quarter %",
    "stock_avg_daily_volume_cp": "Stock market average daily trading volume (shares)",
    "stock_avg_daily_trade_value_vnd": "Stock market average daily trading value (VND)",
}
DESC_VI = {
    "bank_npl_ratio": "Tỷ lệ nợ xấu (NPL) toàn ngành ngân hàng, %",
    "bank_car_ratio": "Hệ số an toàn vốn (CAR) của ngân hàng, %",
    "bank_nim_ratio": "Biên lãi ròng (NIM) của ngân hàng, %",
    "bank_roe_ratio": "Tỷ suất lợi nhuận trên vốn chủ sở hữu (ROE) của ngân hàng, %",
    "bank_ldr_ratio": "Tỷ lệ dư nợ cho vay trên vốn huy động (LDR), %",
    "bank_provision_coverage_proxy_pct": "Tỷ lệ bao phủ nợ xấu bằng dự phòng, %",
    "bank_z_score": "Z-score ổn định ngân hàng (khoảng cách tới mất khả năng thanh toán)",
    "macro_gdp_yoy_pct": "Tăng trưởng GDP thực của Việt Nam so với cùng kỳ, %",
    "macro_cpi_avg_pct": "Lạm phát CPI bình quân quý, %",
    "macro_policy_rate_pct": "Lãi suất điều hành (tái cấp vốn) của NHNN, %",
    "stock_adj_close_last_vnd": "Mức giá cổ phiếu (giá đóng cửa điều chỉnh cuối quý)",
    "stock_return_qoq_pct": "Suất sinh lời cổ phiếu theo quý, %",
    "stock_avg_daily_volume_cp": "Khối lượng giao dịch cổ phiếu bình quân mỗi ngày",
    "stock_avg_daily_trade_value_vnd": "Giá trị giao dịch cổ phiếu bình quân mỗi ngày (VND)",
}
SHORT = {
    "bank_npl_ratio": "NPL", "bank_car_ratio": "CAR", "bank_nim_ratio": "NIM", "bank_roe_ratio": "ROE",
    "bank_ldr_ratio": "LDR", "bank_provision_coverage_proxy_pct": "PROV_COVERAGE", "bank_z_score": "Z_SCORE",
    "macro_gdp_yoy_pct": "GDP_GROWTH", "macro_cpi_avg_pct": "CPI_INFLATION", "macro_policy_rate_pct": "POLICY_RATE",
    "stock_adj_close_last_vnd": "STOCK_PRICE", "stock_return_qoq_pct": "STOCK_RETURN",
    "stock_avg_daily_volume_cp": "TRADE_VOLUME", "stock_avg_daily_trade_value_vnd": "TRADE_VALUE",
}
FROM_SHORT = {v: k for k, v in SHORT.items()}

# Lexical synonyms for retrieval (lower-cased regex fragments, matched on headline + chunk_content).
SYN = {
    "bank_npl_ratio": [r"nợ xấu", r"\bnpl\b", r"nợ nhóm 3", r"nợ có khả năng mất vốn", r"nợ tiềm ẩn"],
    "bank_car_ratio": [r"\bcar\b", r"an toàn vốn", r"basel", r"vốn tự có", r"tăng vốn điều lệ"],
    "bank_nim_ratio": [r"\bnim\b", r"biên lãi", r"thu nhập lãi thuần", r"chênh lệch lãi suất"],
    "bank_roe_ratio": [r"\broe\b", r"lợi nhuận (?:trước thuế|sau thuế|ngân hàng|ngành ngân hàng)",
                       r"khả năng sinh lời", r"tỷ suất sinh lời"],
    "bank_ldr_ratio": [r"\bldr\b", r"cho vay (?:trên|/) ?huy động", r"dư nợ (?:trên|/) ?huy động",
                       r"tín dụng (?:trên|/) ?huy động", r"tỷ lệ cấp tín dụng so với", r"huy động vốn",
                       r"tăng trưởng tín dụng", r"room tín dụng", r"hạn mức tín dụng"],
    "bank_provision_coverage_proxy_pct": [r"bao phủ nợ xấu", r"\bllr\b", r"dự phòng", r"trích lập"],
    "bank_z_score": [r"z-score", r"z score", r"ổn định (?:hệ thống )?ngân hàng", r"an toàn hệ thống",
                     r"đổ vỡ", r"rút tiền hàng loạt", r"kiểm soát đặc biệt"],
    "macro_gdp_yoy_pct": [r"\bgdp\b", r"tăng trưởng kinh tế", r"tổng sản phẩm"],
    "macro_cpi_avg_pct": [r"\bcpi\b", r"lạm phát", r"chỉ số giá tiêu dùng"],
    "macro_policy_rate_pct": [r"lãi suất điều hành", r"tái cấp vốn", r"tái chiết khấu", r"\bomo\b",
                              r"lãi suất chính sách", r"(?:tăng|giảm|hạ|nâng) (?:các mức )?lãi suất"],
    "stock_adj_close_last_vnd": [r"vn-?index", r"giá cổ phiếu", r"thị giá", r"vốn hóa", r"chỉ số chứng khoán",
                                 r"\bđiểm\b"],
    "stock_return_qoq_pct": [r"suất sinh lời", r"lợi suất cổ phiếu", r"tăng điểm", r"giảm điểm",
                             r"hiệu suất (?:đầu tư|cổ phiếu)", r"giảm \d+(?:[.,]\d+)?% ?(?:trong|so)",
                             r"tăng \d+(?:[.,]\d+)?% ?(?:trong|so)"],
    "stock_avg_daily_volume_cp": [r"khối lượng giao dịch", r"thanh khoản", r"khớp lệnh", r"cổ phiếu giao dịch"],
    "stock_avg_daily_trade_value_vnd": [r"giá trị giao dịch", r"thanh khoản", r"gtgd", r"nghìn tỷ đồng/phiên",
                                        r"tỷ đồng/phiên", r"dòng tiền"],
}
_SYN_RE = {n: [re.compile(p, re.I) for p in pats] for n, pats in SYN.items()}


def load_chunks() -> list[dict]:
    return [json.loads(l) for l in CHUNKS_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]


def load_relations() -> list[dict]:
    out = []
    for l in RELS_PATH.read_text(encoding="utf-8").splitlines():
        if l.strip():
            r = json.loads(l)
            if r.get("record_type") == "relation":
                out.append(r)
    return out


def load_prior21() -> list[dict]:
    g = json.loads(PRIOR_PATH.read_text(encoding="utf-8"))
    out = []
    for k, v in g.items():
        s, t = k.split("|")
        if s in NODES and t in NODES:
            out.append({"source": s, "target": t, **v})
    assert len(out) == 21, len(out)
    return out


def load_gold() -> list[dict]:
    return [json.loads(l) for l in GOLD_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]


def load_panel():
    """14 x 19 panel (rows = QUARTERS, cols = NODES) as a numpy array."""
    import csv
    import numpy as np
    rows = {r["quarter"]: r for r in csv.DictReader(MATRIX_PATH.open(encoding="utf-8"))}
    return np.array([[float(rows[q][n]) for n in NODES] for q in QUARTERS])


def chunk_text(c: dict) -> str:
    return f"{c.get('headline') or ''}\n{c.get('chunk_content') or ''}"


def node_hits(c: dict) -> dict[str, int]:
    txt = chunk_text(c)
    out = {}
    for n, regs in _SYN_RE.items():
        k = sum(len(r.findall(txt)) for r in regs)
        if k:
            out[n] = k
    return out


def fmt_chunk(c: dict) -> str:
    return (f"[{c['rag_id']}] (domain={c.get('domain')}, event_time={c.get('event_time')})\n"
            f"Headline: {c.get('headline')}\nText: {c.get('chunk_content')}\nSource: {(c.get('source') or '')[:120]}")


# --- guarded, counted LLM call -----------------------------------------------------------------
def _cache_key(model: str, messages: list[dict], params: dict) -> Path:
    # Same key as paper4.llm.chat, used only to tell a cache hit (free) from a paid call.
    key = hashlib.sha256(json.dumps([model, messages, params], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return _llm.CACHE / f"{key}.json"


def calls_used() -> int:
    if not CALL_LOG.exists():
        return 0
    return sum(1 for l in CALL_LOG.read_text(encoding="utf-8").splitlines() if l.strip())


_USED = {"n": None}


def ask(messages: list[dict], tag: str, **params) -> str:
    """One request through paper4.llm.chat. Counts paid calls; refuses past BUDGET.

    If chat raises because the egress country is not SG, the error propagates: callers must stop.
    """
    params = {"response_format": {"type": "json_object"}, "reasoning_effort": "low", **params}
    path = _cache_key(MODEL, messages, params)
    if path.exists():
        return _llm.chat(messages, model=MODEL, **params)
    for attempt in range(3):
        try:
            return _paid(messages, tag if attempt == 0 else f"{tag}#retry{attempt}", path, params)
        except RuntimeError as e:  # egress not SG or budget exhausted: stop, never work around
            raise
        except Exception:  # noqa: BLE001 - transient API error (rate limit, timeout): back off and retry
            if attempt == 2:
                raise
            time.sleep(10 * (attempt + 1))


def _paid(messages, tag, path, params):
    with _LOCK:
        if _USED["n"] is None:
            _USED["n"] = calls_used()
        if _USED["n"] >= BUDGET:
            raise RuntimeError(f"LLM budget of {BUDGET} calls exhausted")
        _USED["n"] += 1
        META.mkdir(parents=True, exist_ok=True)
        with CALL_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "tag": tag, "key": path.stem}) + "\n")
    return _llm.chat(messages, model=MODEL, **params)


def parse_json(text: str):
    """Robust JSON parse: strip code fences, take the outermost {...} or [...]."""
    if text is None:
        return None
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    try:
        return json.loads(t)
    except Exception:  # noqa: BLE001
        pass
    for o, cl in (("{", "}"), ("[", "]")):
        i, j = t.find(o), t.rfind(cl)
        if i != -1 and j > i:
            try:
                return json.loads(t[i:j + 1])
            except Exception:  # noqa: BLE001
                continue
    return None


def run_parallel(fn, items, workers: int = 8):
    """Map fn over items with threads; the first item runs alone so the client and geo check init once."""
    from concurrent.futures import ThreadPoolExecutor
    items = list(items)
    if not items:
        return []
    first = [fn(items[0])]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        rest = list(ex.map(fn, items[1:]))
    return first + rest


def quarter_of(text: str | None) -> str | None:
    """Normalise '2022-Q3', '2022Q3', 'Q3/2022', '2022-09-30' to '2022Q3'."""
    if not text:
        return None
    s = str(text)
    m = re.search(r"(20\d\d)\s*-?\s*Q([1-4])", s, re.I) or None
    if m:
        return f"{m.group(1)}Q{m.group(2)}"
    m = re.search(r"Q([1-4])\s*[/-]\s*(20\d\d)", s, re.I)
    if m:
        return f"{m.group(2)}Q{m.group(1)}"
    m = re.search(r"(20\d\d)-(\d\d)(?:-\d\d)?", s)
    if m:
        return f"{m.group(1)}Q{(int(m.group(2)) - 1) // 3 + 1}"
    return None
