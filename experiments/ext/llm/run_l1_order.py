"""L1: contemporaneous causal order of the 14 core variables from triplet prompts (direction "llm").

Following Vashishtha et al. (ICLR 2025, arXiv 2310.15117): ask about small subsets (triplets) instead of
single edges, aggregate the answers into pairwise votes, then find the order that minimises the total
weight of violated votes (minimum weighted feedback-arc-set over tournaments; exact by dynamic
programming over subsets, 2^14 states).

Three prompt variants (stability check):
  T1  English, triplet, "which DIRECT contemporaneous effects exist among these three" (graph answer);
      a vote i->j per stated edge.
  T2  Vietnamese, triplet, "recursive (Cholesky-type) order within the quarter" (order answer);
      3 votes per triplet from the stated order. Variables are shown in a different random order than T1.
  P   English, pairwise (91 pairs), "X->Y / Y->X / none within the same quarter".
Votes are normalised per pair by the number of opportunities (12 triplets per pair, 1 pairwise prompt).

Outputs: results/ext_llm_order/order.json (orders per variant + pooled, Kendall tau, bootstrap
P(i before j), per-prior-edge reversal suspicion), raw.jsonl.
Run: python experiments/ext/llm/run_l1_order.py
"""
from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (DESC_EN, DESC_VI, NODES, ROOT, SHORT, FROM_SHORT, ask, calls_used, load_prior21,  # noqa: E402
                    parse_json, run_parallel)

OUT = ROOT / "results" / "ext_llm_order"
N = len(NODES)
IDX = {n: i for i, n in enumerate(NODES)}
CONTEXT_EN = ("Context: quarterly aggregate series for Vietnam, 2020-2024 (banking-sector ratios, macro indicators, "
              "stock-market aggregates), to be modelled with a structural VAR. A contemporaneous effect means a change "
              "in one variable moves another within the SAME quarter.")


def t1_prompt(tri):
    lines = "\n".join(f"- {SHORT[n]}: {DESC_EN[n]}" for n in tri)
    return [{"role": "system", "content": "You are an expert macro-financial economist. Respond with one JSON object only."},
            {"role": "user", "content": f"""{CONTEXT_EN}

Variables:
{lines}

Which DIRECT contemporaneous causal effects exist among these three variables? Only list an effect A->B if A moves B within the same quarter directly (not only through the third variable). Omit pairs with no plausible direct contemporaneous effect. Do not list both A->B and B->A unless you are confident of genuine simultaneity.
Return {{"edges": [{{"from": "<NAME>", "to": "<NAME>"}}, ...], "reason": "<at most 30 words>"}} using the names exactly as given."""}]


def t2_prompt(tri):
    lines = "\n".join(f"- {SHORT[n]}: {DESC_VI[n]}" for n in tri)
    return [{"role": "system", "content": "Bạn là chuyên gia kinh tế vĩ mô và tài chính. Chỉ trả về một đối tượng JSON."},
            {"role": "user", "content": f"""Bối cảnh: các chuỗi tổng hợp theo quý của Việt Nam giai đoạn 2020-2024, dùng trong mô hình SVAR đệ quy.

Các biến:
{lines}

Hãy sắp xếp ba biến theo thứ tự đệ quy trong cùng một quý: biến đứng trước có thể tác động tức thời (trong cùng quý) lên biến đứng sau, còn biến đứng sau KHÔNG tác động tức thời ngược lại lên biến đứng trước. Biến "ngoại sinh" nhất trong quý đứng đầu.
Trả về {{"order": ["<TÊN>", "<TÊN>", "<TÊN>"], "reason": "<tối đa 30 từ>"}} dùng đúng tên biến như trên."""}]


def p_prompt(x, y):
    return [{"role": "system", "content": "You are an expert macro-financial economist. Respond with one JSON object only."},
            {"role": "user", "content": f"""{CONTEXT_EN}

X = {SHORT[x]}: {DESC_EN[x]}
Y = {SHORT[y]}: {DESC_EN[y]}

Within the same quarter, which is more plausible: X directly moves Y, Y directly moves X, or neither has a direct contemporaneous effect on the other?
Return {{"answer": "X->Y" | "Y->X" | "none", "confidence": <number in [0,1]>, "reason": "<at most 30 words>"}}."""}]


def _name(s):
    s = str(s or "").strip().upper()
    return FROM_SHORT.get(s)


def run_t(item):
    variant, tri = item
    msgs = t1_prompt(tri) if variant == "T1" else t2_prompt(tri)
    ans = parse_json(ask(msgs, tag=f"L1{variant}:{'|'.join(SHORT[n] for n in tri)}"))
    votes = []
    if variant == "T1" and isinstance(ans, dict):
        for e in ans.get("edges") or []:
            if isinstance(e, dict):
                a, b = _name(e.get("from")), _name(e.get("to"))
                if a and b and a != b and a in tri and b in tri:
                    votes.append((a, b))
    if variant == "T2" and isinstance(ans, dict):
        o = [_name(v) for v in ans.get("order") or []]
        if len(o) == 3 and set(o) == set(tri):
            votes = [(o[0], o[1]), (o[0], o[2]), (o[1], o[2])]
    return {"variant": variant, "triplet": [SHORT[n] for n in tri], "answer": ans, "votes": [[SHORT[a], SHORT[b]] for a, b in votes]}


def run_p(pair):
    x, y = pair
    ans = parse_json(ask(p_prompt(x, y), tag=f"L1P:{SHORT[x]}|{SHORT[y]}"))
    votes = []
    if isinstance(ans, dict):
        a = str(ans.get("answer") or "").strip()
        if a == "X->Y":
            votes = [(x, y)]
        elif a == "Y->X":
            votes = [(y, x)]
    return {"variant": "P", "pair": [SHORT[x], SHORT[y]], "answer": ans, "votes": [[SHORT[a], SHORT[b]] for a, b in votes]}


def vote_matrix(records, opp):
    W = np.zeros((N, N))
    for r in records:
        for a, b in r["votes"]:
            W[IDX[FROM_SHORT[a]], IDX[FROM_SHORT[b]]] += 1.0
    return W / opp


def best_order(W):
    """Exact minimum of sum_{j placed before i} W[i, j] over all orders (DP over subsets)."""
    full = 1 << N
    f = np.full(full, np.inf)
    f[0] = 0.0
    back = np.zeros(full, dtype=np.int64)
    for S in range(full):
        if not np.isfinite(f[S]):
            continue
        members = [u for u in range(N) if S >> u & 1]
        for v in range(N):
            if S >> v & 1:
                continue
            c = f[S] + sum(W[v, u] for u in members)
            T = S | (1 << v)
            if c < f[T] - 1e-12:
                f[T], back[T] = c, v
    order, S = [], full - 1
    while S:
        v = int(back[S])
        order.append(v)
        S ^= 1 << v
    return order[::-1], float(f[full - 1])


def kendall(o1, o2):
    from scipy.stats import kendalltau
    p1 = [o1.index(i) for i in range(N)]
    p2 = [o2.index(i) for i in range(N)]
    return float(kendalltau(p1, p2).statistic)


def main():
    rnd = random.Random(20261102)
    tris = list(itertools.combinations(NODES, 3))
    t1_items = [("T1", tuple(rnd.sample(t, 3))) for t in tris]
    t2_items = [("T2", tuple(rnd.sample(t, 3))) for t in tris]
    pairs = [tuple(rnd.sample(p, 2)) for p in itertools.combinations(NODES, 2)]
    before = calls_used()
    recs = run_parallel(run_t, t1_items + t2_items, workers=8) + run_parallel(run_p, pairs, workers=8)
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "raw.jsonl").open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    by = {v: [r for r in recs if r["variant"] == v] for v in ("T1", "T2", "P")}
    opp = {"T1": 12.0, "T2": 12.0, "P": 1.0}
    Ws = {v: vote_matrix(by[v], opp[v]) for v in by}
    Wpool = sum(Ws.values()) / len(Ws)
    orders = {}
    for v, W in list(Ws.items()) + [("pooled", Wpool)]:
        o, cost = best_order(W)
        orders[v] = {"order": [SHORT[NODES[i]] for i in o], "violated_weight": cost, "total_weight": float(W.sum()),
                     "_idx": o}
    taus = {f"{a}~{b}": kendall(orders[a]["_idx"], orders[b]["_idx"]) for a, b in itertools.combinations(("T1", "T2", "P"), 2)}
    # bootstrap over prompts within each variant
    rng = np.random.default_rng(7)
    B = 200
    before_cnt = np.zeros((N, N))
    for _ in range(B):
        Wb = []
        for v in ("T1", "T2", "P"):
            rs = by[v]
            sample = [rs[i] for i in rng.integers(0, len(rs), len(rs))]
            Wb.append(vote_matrix(sample, opp[v]))
        o, _ = best_order(sum(Wb) / 3)
        pos = {u: k for k, u in enumerate(o)}
        for i in range(N):
            for j in range(N):
                if pos[i] < pos[j]:
                    before_cnt[i, j] += 1
    P_before = before_cnt / B
    prior = load_prior21()
    pos = {v: {NODES[u]: k for k, u in enumerate(orders[v]["_idx"])} for v in orders}
    edges = []
    for e in prior:
        s, t = e["source"], e["target"]
        i, j = IDX[s], IDX[t]
        per = {}
        for v in ("T1", "T2", "P"):
            fw, bw = Ws[v][i, j], Ws[v][j, i]
            per[v] = {"votes_stated": round(fw * opp[v], 3), "votes_reversed": round(bw * opp[v], 3),
                      "order_reverses": pos[v][t] < pos[v][s]}
        fw, bw = Wpool[i, j], Wpool[j, i]
        edges.append({"source": SHORT[s], "target": SHORT[t], "source_id": s, "target_id": t,
                      "per_variant": per,
                      "vote_share_reversed": float(bw / (fw + bw)) if fw + bw > 0 else None,
                      "vote_support_any_direction": float((fw + bw) / 1.0),
                      "p_order_reversed_bootstrap": float(P_before[j, i]),
                      "pooled_order_reverses": pos["pooled"][t] < pos["pooled"][s],
                      "n_variants_reversing": sum(per[v]["order_reverses"] for v in per),
                      "reversal_suspicion": float(0.5 * P_before[j, i] + 0.5 * (bw / (fw + bw) if fw + bw > 0 else 0.5))})
    edges.sort(key=lambda r: -r["reversal_suspicion"])
    for v in orders:
        orders[v]["n_prior_edges_reversed"] = sum(pos[v][e["target"]] < pos[v][e["source"]] for e in prior)
        orders[v].pop("_idx")
    parse_ok = {v: sum(1 for r in by[v] if r["answer"] is not None) / len(by[v]) for v in by}
    no_vote = {v: sum(1 for r in by[v] if not r["votes"]) / len(by[v]) for v in by}
    out = {"model": "gpt-5-mini-2025-08-07", "nodes": [SHORT[n] for n in NODES], "node_ids": NODES,
           "orders": orders, "kendall_tau": taus, "parse_ok_rate": parse_ok, "share_prompts_without_vote": no_vote,
           "calls_this_run": calls_used() - before, "bootstrap_B": B,
           "P_before": {SHORT[NODES[i]]: {SHORT[NODES[j]]: float(P_before[i, j]) for j in range(N) if j != i} for i in range(N)},
           "vote_matrix_pooled": {SHORT[NODES[i]]: {SHORT[NODES[j]]: float(Wpool[i, j]) for j in range(N) if j != i} for i in range(N)},
           "prior_edges": edges}
    (OUT / "order.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("orders", "kendall_tau", "parse_ok_rate", "share_prompts_without_vote", "calls_this_run")}, indent=1))
    for e in edges[:8]:
        print(e["source"], "->", e["target"], round(e["reversal_suspicion"], 2), e["n_variants_reversing"])


if __name__ == "__main__":
    main()
