# Hướng `llm`: tín hiệu từ LLM cho module chịu lỗi (L1, L4-lite, L3)

**Trạng thái.** Đã chạy xong, theo đề xuất đã duyệt (docs/ext/de_xuat_llm_pending.md). Phần này chỉ **đo tín hiệu thật trên văn bản Paper 1** và quy về thang AUROC mà hướng `textinfo` dùng. Phần đánh giá module trong mô phỏng thuộc `textinfo` (docs/ext/textinfo.md), không làm lại ở đây.

**Ngân sách.** Tổng cộng **1152 chat call / 1500** (1 smoke, L4: 122, L3: 210, L1: 819). Không có retry nào xảy ra. Mọi call đi qua `paper4.llm.chat` (`store=False`, kiểm tra egress SG, egress = SG trong suốt quá trình), model `gpt-5-mini-2025-08-07`. Chạy lại mọi script là miễn phí nhờ cache `results/llm_cache` (1152 file). Log từng call: `results/ext_llm_meta/call_log.jsonl`.

## 1. Dữ liệu và quy ước đã dùng

| Thứ | Nguồn (chỉ đọc) |
|---|---|
| 14 biến lõi | `ACIIDS/02_observational_data/processed/core14_provenance.json` → `nodes` (`tier1_core14`) |
| 19 quý | cùng file, window `defensible`: 2020Q2..2024Q4 |
| Prior 21 cạnh | induced subgraph của `prior_graph_final_278.json` (42 cạnh) trên 14 nút, như `ACIIDS/03_causal_discovery/scripts/prior_extraction.py::extract_induced_subdag`. Khớp con số 21/42 trong `node_set_selection.md`. |
| Văn bản | `rag_kb_full_content.jsonl` (278 chunk), `pipeline_output_raw_278chunk.jsonl` (124 quan hệ, 82 accepted) |
| Nhãn người | `evaluation_benchmark/ground_truth_v1.2_draft.jsonl`: 16 quan hệ giữa các nút lõi (11 cặp), `annotator_type = human` |
| Panel | `candidate_quarterly_matrix_raw.csv`, 14 × 19 |

Tên ngắn dùng trong prompt: NPL, CAR, NIM, ROE, LDR, PROV_COVERAGE, Z_SCORE, GDP_GROWTH, CPI_INFLATION, POLICY_RATE, STOCK_PRICE, STOCK_RETURN, TRADE_VOLUME, TRADE_VALUE. Mô tả tiếng Anh/Việt và từ đồng nghĩa dùng cho lexical retrieval nằm trong `experiments/ext/llm/common.py` (`DESC_EN`, `DESC_VI`, `SYN`).

Script (`experiments/ext/llm/`): `common.py` (wrapper đếm call, cap 1500, parse JSON), `run_l4_edges.py`, `run_l3_shocks.py`, `run_l1_order.py`, `signal_quality.py`, `export_side_info.py`. Ba script cuối không gọi LLM.

## 2. L1: causal order cùng kỳ

**Cách làm.** Theo Vashishtha và cộng sự (ICLR 2025): hỏi theo bộ ba thay vì từng cạnh. Có ba biến thể prompt:
- **T1** (tiếng Anh): "trong cùng quý, có những tác động trực tiếp nào giữa ba biến?". Trả về đồ thị; mỗi cạnh là một phiếu.
- **T2** (tiếng Việt): "xếp ba biến theo thứ tự đệ quy trong quý, kiểu SVAR Cholesky". Trả về thứ tự đầy đủ, được 3 phiếu cho mỗi bộ ba. Thứ tự trình bày biến được xáo khác với T1.
- **P** (tiếng Anh, pairwise, 91 cặp): "X->Y / Y->X / none trong cùng quý".

Mỗi biến thể hỏi đủ C(14,3) = 364 bộ ba (P hỏi đủ 91 cặp). Phiếu được chuẩn hóa theo số cơ hội: 12 bộ ba mỗi cặp, 1 prompt pairwise. Thứ tự được tìm bằng **minimum weighted feedback-arc-set chính xác**, dùng DP trên 2^14 tập con. Pooled là trung bình ba ma trận phiếu. Bootstrap (B = 200) lấy lại prompt trong từng biến thể để cho P(i đứng trước j).

**Kết quả** (`results/ext_llm_order/order.json`):

- Pooled order: GDP_GROWTH → CPI_INFLATION → POLICY_RATE → NPL → LDR → NIM → PROV_COVERAGE → CAR → ROE → STOCK_PRICE → STOCK_RETURN → Z_SCORE → TRADE_VOLUME → TRADE_VALUE.
- Kendall tau giữa các thứ tự:

| | toàn bộ 91 cặp | trong cùng khối (Bank/Macro/Stock) | chiều của 21 cặp prior |
|---|---|---|---|
| T1 ~ P | **0.89** | 0.87 | 95% |
| T1 ~ T2 | 0.16 | 0.33 | 86% |
| T2 ~ P | 0.23 | 0.47 | 81% |

Tau toàn cục giữa T2 và hai biến thể còn lại thấp vì T2 buộc phải xếp cả những cặp không liên quan. T2 đặt khối chứng khoán trước khối ngân hàng, T1/P làm ngược lại; đó là quy ước tùy ý, không phải tín hiệu. Khi chỉ xét chiều của 21 cạnh prior, ba biến thể đồng ý 81–95%.
- Số cạnh prior bị đảo: T1 4, T2 1, P 5, pooled 4.
- Reversal suspicion theo cạnh (`prior_edges[*].reversal_suspicion` = ½ bootstrap P(đảo) + ½ tỷ lệ phiếu đảo):

| Cạnh prior | suspicion | số biến thể đảo |
|---|---|---|
| LDR → POLICY_RATE | 1.00 | 3/3 |
| NIM → NPL | 0.89 | 2/3 |
| POLICY_RATE → CPI_INFLATION | 0.86 | 2/3 (T2 không đảo) |
| POLICY_RATE → GDP_GROWTH | 0.85 | 2/3 (T2 không đảo) |
| ROE → Z_SCORE | 0.25 | 0/3 |
| 16 cạnh còn lại | ≤ 0.08 | 0/3 |

**Diễn giải.** Hai cạnh POLICY_RATE → {CPI, GDP} bị đảo đúng theo quy ước SVAR tiền tệ kiểu Christiano–Eichenbaum–Evans: output và giá đứng trước lãi suất, vì chính sách chỉ tác động lên chúng với độ trễ. T2 theo quy ước ngược lại (policy đi trước). Vì vậy tín hiệu ở đây là **"cạnh này nhiều khả năng là cạnh có lag, không phải cạnh cùng kỳ"**, chứ không phải "cạnh sai chiều". L4 khớp với cách đọc này: lag của POLICY→CPI là `both`, của POLICY→GDP là `unclear`.

## 3. L4-lite: phân xử từng cặp dựa trên chunk

**Cặp được hỏi.**
- 21 cạnh prior.
- 40 cặp ứng viên thiếu cạnh: cặp được nhắc chung trong ít nhất 2 chunk theo lexical matcher và không có trong prior, xếp theo số chunk nhắc chung (đủ 40 cặp).

**Truy xuất.** Lấy tối đa 8 chunk cho mỗi cặp (trung bình 6.5): chunk evidence của Paper 1 cho cặp đó, rồi các chunk nhắc cả hai biến. Nếu cặp có dưới 3 chunk nhắc chung, thêm 2 chunk ngữ cảnh cho mỗi biến.

**Hai biến thể prompt** (khác cả ngôn ngữ, định dạng lẫn **thứ tự X/Y**, để position bias không trông như đồng thuận):
- **A** (tiếng Anh): phân loại `supports/contradicts/insufficient`, kèm direction, sign, lag, `edge_confidence` và `knowledge_direction`.
- **B** (tiếng Việt): trích câu trước, rồi cho phân bố xác suất {X→Y, Y→X, hai chiều, không có cạnh trực tiếp}, sign, lag và biến trung gian.

`reasoning_effort = medium`.

**Kết quả** (`results/ext_llm_edges/edges.json`; mỗi cặp có `support_mean`, `p_ab_mean`/`p_ba_mean`, `direction_majority`, `lag_majority`, độ đồng thuận và chunk ids):

| Self-consistency A vs B | Giá trị |
|---|---|
| Đồng ý có/không cạnh (ngưỡng 0.5) | 70% (43/61) |
| Spearman / Pearson của P(edge) | 0.79 / 0.63 |
| Đồng ý chiều, khi cả hai nêu chiều (26 cặp) | **96%** |
| Đồng ý lag | 67% |
| P(edge) trung bình | A 0.26, B 0.53 |

P(edge) trung bình chênh gấp đôi chỉ vì định dạng prompt. Phần lớn bất đồng có/không là do A nghiêm hơn về chữ "trực tiếp". Điều này khớp với Kumar và cộng sự 2026: mức tự tin tuyệt đối của LLM không dùng được, chỉ **thứ hạng** dùng được. Với `ext_textinfo` thì vậy là đủ, vì module chỉ dùng rank.

- **Cạnh prior bị nghi** (doubt = 1 − P(cạnh đúng chiều đã nêu)):
  - LDR → POLICY_RATE: doubt 0.94, văn bản không ủng hộ ở chiều nào.
  - NIM → NPL: doubt 0.94, chiều đọc từ văn bản là NPL → NIM.
  - POLICY_RATE → CPI: doubt 0.49, văn bản nói hai chiều.
- **Cặp nghi thiếu cạnh** (suspicion = P(edge) trung bình):

| Cặp | suspicion | chiều | lag |
|---|---|---|---|
| NIM – PROV_COVERAGE | 0.88 | hai chiều | cùng quý |
| LDR → NPL | 0.73 | LDR→NPL | quý sau |
| STOCK_PRICE – TRADE_VALUE | 0.65 | không đồng ý | cùng quý |
| LDR → TRADE_VALUE | 0.55 | | |
| STOCK_PRICE – TRADE_VOLUME | 0.55 | | |
| ROE ← POLICY_RATE | 0.48 | | |

  Cặp gần định nghĩa (TRADE_VALUE–TRADE_VOLUME, STOCK_PRICE–STOCK_RETURN) bị LLM chấm thấp (≤ 0.2), đúng với yêu cầu "cạnh nhân quả trực tiếp".
- **Lag của 21 cạnh prior** (đa số của hai biến thể): `same_quarter` 9, `later_quarters` 5, hai biến thể bất đồng 4, `unclear` 2, `both` 1. So với `lag_hint` của Paper 1 (gần như toàn `immediate`), L4 cho thêm thông tin lag cho khoảng một phần ba số cạnh.
- **Sign:** có 15 cạnh mà cả hai biến thể cùng nêu sign và cùng chiều prior. Trong 12 cạnh có sign prior ±, 11 trùng và 1 khác; 3 cạnh còn lại có sign prior là `policy_shock`.

## 4. L3: chuỗi cú sốc chính sách từ văn bản

**Cách làm.**
- **Chọn chunk:** `policy_shock_flag` ∈ {True, yes} (75 chunk), hoặc chunk có quan hệ `policy_shock` của Paper 1 (38), hoặc khớp từ khóa chính sách (42); hợp lại được 105 chunk.
- **Trích sự kiện:** mỗi chunk được hỏi 2 lần (A tiếng Anh, B tiếng Việt với thứ tự khóa khác). LLM trích các hành động chính sách có quý, `policy_type`, stance, biến bị tác động (1 trong 14 biến, hoặc OTHER), chiều, magnitude class và câu trích nguyên văn.
- **Lọc:** chỉ giữ sự kiện có quý rõ, có chiều, và có câu trích **tìm thấy nguyên văn** trong chunk.
- **Gộp:** các sự kiện cùng (quý, biến, chiều) ở nhiều chunk thành một cluster mang đủ chunk ids. Cluster "consensus" là cluster mà cả hai biến thể cùng tìm thấy.
- **Chuỗi theo quý:** `shock_<VAR>[q] = Σ chiều × magnitude` (small 1, medium 2, large 3); thêm `monetary_stance` cho các loại `policy_rate`/`omo_liquidity`/`credit_quota`.

**Kết quả** (`results/ext_llm_shocks/`: `shocks.csv` là bản consensus, `shocks_union.csv`, `events.json` có từng sự kiện kèm chunk id, quote và biến thể; `raw.jsonl`):

- 104 sự kiện thô, nhưng **55 sự kiện không xác định được quý** từ văn bản; 2 quote không khớp nguyên văn.
- Còn 47 sự kiện dùng được, gộp thành 28 cluster; 10 cluster consensus.
- **Chỉ 14 cluster nằm trong 19 quý của panel, trong đó 8 consensus.** Nhiều chunk có `event_time` 2025–2026, nằm ngoài window.
- Biến thể A dè dặt hơn hẳn: 14 key dùng được, so với 31 của B. Jaccard A/B = 0.36. Trong 19 key chỉ có ở B, 12 key thuộc 2025–2026; B đã gán quý dựa vào ngữ cảnh.

8 cluster consensus trong window. Ngày tháng được kiểm thủ công với chunk:

| Quý | Sự kiện (chunk) | Biến / chiều | Kiểm tra |
|---|---|---|---|
| 2022Q3 | NHNN tăng lãi suất điều hành tháng 9/2022 (RAGKB_040, 046) | POLICY_RATE + large | đúng |
| 2022Q4 | tăng tiếp tháng 10/2022, mỗi đợt 1 điểm % (RAGKB_032, 046) | POLICY_RATE + large | đúng |
| 2022Q3 | Nghị định 65/2022, ngày 16/9/2022 (RAGKB_060) | OTHER −; TRADE_VOLUME − | ngày đúng; target TRADE_VOLUME là gượng |
| 2022Q4 | TT22/2019: tỷ lệ vốn ngắn hạn cho vay trung-dài hạn về 30% từ 1/10/2022 (RAGKB_059) | LDR − | đúng |
| 2023Q4 | TT22/2023 sửa TT41, ngày 29/12/2023 (RAGKB_061) | CAR + small | đúng |
| 2024Q3 | ba luật đất đai/nhà ở/KDBĐS có hiệu lực 1/8/2024 (RAGKB_050, R020, R049) | OTHER + | đúng |
| 2024Q3 | "NHNN bán hơn 6 tỷ USD ... duy trì lãi suất điều hành thấp" (RAGKB_R049) | POLICY_RATE −, easing, large | **sai stance**: lãi suất không đổi, bán USD là hút thanh khoản VND |

**So với chuỗi lãi suất thật trong panel** (`macro_policy_rate_pct`). Panel chỉ đổi 2 lần: +2.0 điểm ở **2022Q1** và −1.5 điểm ở **2023Q1**. Văn bản thì đặt hai đợt tăng ở **2022Q3 và 2022Q4** (tháng 9 và tháng 10/2022, QĐ 1606/QĐ-NHNN). Vì vậy chuỗi proxy và Δpolicy_rate **không trùng quý nào** (Pearson ≈ 0). Chunk RAGKB_008 chỉ ghi theo năm ("tăng lên 6,0% năm 2022", "giảm về 4,5% từ 2023"). Theo các quyết định NHNN công khai, lãi suất tái cấp vốn còn giảm nhiều đợt trong 2020 (tháng 3, 5, 10/2020) và 2023 (tháng 3, 5, 6/2023); panel không thấy các đợt đó vì để 4,0% ngay từ 2020Q1. Có vẻ cột lãi suất của panel được điền theo bậc năm. **Cần người kiểm tra lại cột này trước khi dùng nó làm biến chính sách hay làm chuẩn cho L3.** Corpus cũng không có sự kiện nào có ngày cho các đợt giảm 2020 và 2023 ("NHNN 4 lần giảm lãi suất điều hành năm 2023" không có quý), nên L3 không khôi phục được chúng.

## 5. Chất lượng tín hiệu (`results/ext_llm_quality/quality.json`)

Không có ground truth trên dữ liệu thật; dưới đây chỉ là các proxy.

1. **Self-consistency.**
   - L1: tau 0.89 (T1~P); 0.16–0.23 khi so với T2 trên toàn bộ cặp; đồng ý 81–95% về chiều của các cặp prior.
   - L4: đồng ý chiều 96%, đồng ý có/không 70%, Spearman 0.79.
   - L3: Jaccard 0.36.
2. **Đồng thuận chéo giữa hai phương pháp gần độc lập.** L1 không đọc văn bản, L4 đọc chunk. Spearman giữa reversal score của hai bên trên 21 cạnh = **0.52**. Cả hai cùng nghi đúng hai cạnh **LDR → POLICY_RATE** và **NIM → NPL**.
3. **Đồng ý với Paper 1.**
   - So với quan hệ accepted: trong 23 quan hệ có hướng giữa nút lõi, L4 cho support ≥ 0.5 ở 19. Trong 19 cặp L4 nêu được chiều, 18 trùng chiều. Thứ tự L1 trùng 18/23. Cách đo này **không độc lập**, vì L4 đọc lại chính evidence chunk của Paper 1.
   - So với nhãn người (11 cặp: 6 valid, 5 invalid): AUROC của L4 support là **0.60, CI95 bootstrap [0.20, 0.97]**. Chiều L4 trên các cặp valid đúng 4/4; L1 đúng 5/6. Hai cặp invalid bị L4 chấm cao là POLICY–CPI và POLICY–GDP, nhưng hai nhãn này là `policy_statement`/`correlation_only`: chúng chấm việc câu văn đó có khẳng định nhân quả không, chứ không chấm việc cạnh đó có thật không. Vì vậy AUROC 0.60 là ước lượng thấp và rất nhiễu của chất lượng cạnh.
4. **Theo dữ liệu.** Granger hai biến, lag 1, trên panel; sai phân 8 cột không dừng, còn 17 quan sát dùng được.
   - 122 test, 11.5% có p < 0.10, gần mức 10% kỳ vọng nếu không có quan hệ nào. Nói cách khác, **dữ liệu gần như không nói gì**.
   - Ở 5 cặp có Granger một chiều và L4 có nêu chiều, cả 5 trùng chiều L4. Nhưng 4 trong 5 cặp có biến ngân hàng simulated_calibrated, và p chưa hiệu chỉnh đa kiểm định.
   - Pairwise LiNGAM trên residual AR(1) trùng chiều L4 22/30; riêng các cặp toàn biến thật trùng 8/0. Tuy nhiên đó gần như toàn cặp có POLICY_RATE, mà cột này là chuỗi bậc thang chỉ đổi 2 lần, và bootstrap share không ổn định. **Không nên coi đây là bằng chứng.**
5. **L3 so với lãi suất thật.** Không trùng quý nào; xem mục 4: lỗi có vẻ nằm ở ngày tháng của panel, không phải ở văn bản.

## 6. Quy về thang AUROC của `textinfo`

`textinfo` dùng mô hình binormal: score = nhiễu + δ·1[hỏng], AUROC = Φ(δ/√2). Ước lượng cho tín hiệu thật:

- **Chặn trên từ reliability.** Reliability của trung bình hai biến thể L4 (Spearman–Brown, Pearson 0.63) là 0.77. Vậy corr với bất kỳ đại lượng tiềm ẩn nào ≤ 0.88.
- **Từ đồng thuận chéo.** L1 ~ L4 = 0.52, nên mỗi phương pháp tương quan cỡ √0.52 ≈ 0.72 với phần tín hiệu chung. Phần chung đó có thể chính là "niềm tin của LLM", không phải sự thật, nên đây vẫn là cận trên.
- **Đổi corr ρ với nhãn hỏng (tỷ lệ hỏng π) sang AUROC:** δ = ρ / √(π(1−π)(1−ρ²)).

| ρ (corr với nhãn hỏng thật) | AUROC, π = 0.1 | AUROC, π = 0.2 | AUROC, π = 0.3 |
|---|---|---|---|
| 0.2 | 0.69 | 0.64 | 0.62 |
| 0.3 | 0.77 | 0.71 | 0.69 |
| 0.4 | 0.85 | 0.78 | 0.75 |
| 0.72 (cận trên, nếu phần chung = sự thật) | 0.99 | 0.97 | 0.95 |

- **Ước lượng trực tiếp duy nhất** là AUROC 0.60 [0.20, 0.97] trên 11 cặp có nhãn người, và bị kéo thấp vì lý do đã nêu ở mục 5.

**Kết luận về thang.**
- Với doubt (thừa/đảo) và suspicion (thiếu), mức thực tế hợp lý là **AUROC ≈ 0.65–0.8, trung tâm ≈ 0.7**.
- Mức 0.9 là lạc quan; nó chỉ đạt được ở những cạnh mà L1 và L4 cùng nghi (LDR→POLICY_RATE, NIM→NPL).
- Mức 0.5 **chưa loại trừ được** về mặt thống kê với cỡ mẫu hiện có.

Khuyến nghị cho `textinfo`: lấy a = 0.7 làm "LLM thực tế", a = 0.9 làm cận lạc quan, và báo kết quả trên cả dải 0.5–0.9. Với sign hint: so với sign prior, tỷ lệ khác là 1/12 ≈ 0.08. Prior không phải sự thật, nên nên mô phỏng `sign_error` cỡ 0.1–0.2.

## 7. Phát hiện đáng chú ý

1. **LDR → POLICY_RATE nhiều khả năng là cạnh sai.** Cả ba biến thể L1 đều đảo nó. L4 không thấy văn bản ủng hộ ở chiều nào (support 0.14). Cạnh có confidence 0.42 và chỉ dựa trên 1 nguồn. Nhãn người cho cặp này là valid theo chiều ngược lại, POLICY → LDR qua cơ chế gián tiếp.
2. **NIM → NPL nhiều khả năng bị đảo** (NPL → NIM), cả L1 và L4 đều chỉ ra. Quan hệ gốc của Paper 1 dựa trên câu "NIM bị thu hẹp trong khi tỷ lệ nợ xấu ... có thể tăng", tức là chỉ đồng biến. Nếu đảo cạnh này thì có thể thêm PROV_COVERAGE → NIM mà không tạo chu trình. PROV_COVERAGE → NIM đã được Paper 1 accepted nhưng không có trong prior cuối; nhiều khả năng nó bị loại vì chu trình NIM → NPL → PROV_COVERAGE → NIM (giả thuyết, chưa kiểm). L4 lại xếp NIM–PROV_COVERAGE là cặp nghi thiếu số 1 (0.88). Ba tín hiệu này ghép thành một câu chuyện nhất quán.
3. **POLICY_RATE → CPI và POLICY_RATE → GDP nên coi là cạnh có lag, không phải cạnh cùng kỳ.** L1 đảo chúng theo quy ước SVAR kiểu CEE, còn biến thể kia giữ chiều. Đây là câu hỏi identification (đặt policy trước hay sau trong thứ tự Cholesky), không phải lỗi skeleton thông thường. Mọi kết quả trên dữ liệu thật dùng thứ tự đệ quy nên báo cả hai thứ tự.
4. **Cạnh thiếu đáng xét nhất:** NIM–PROV_COVERAGE, LDR → NPL (quý sau), STOCK_PRICE–TRADE_VALUE.
5. **Ngày cú sốc:** văn bản đặt các đợt tăng lãi suất ở 2022Q3–Q4 và một chuỗi quy định siết chặt cũng trong 2022Q3–Q4 (NĐ 65/2022, TT22/2019 bước 30%). Cột lãi suất của panel đặt đợt tăng ở 2022Q1 và đợt giảm ở 2023Q1. Đây có thể là lỗi ngày tháng trong dữ liệu quan sát, và cần người kiểm.

## 8. Cảnh báo

- Hai nhóm proxy đều có vấn đề. Self-consistency và đồng thuận với Paper 1 là **cận trên** của chất lượng: LLM có thể nhất quán mà vẫn sai, và L4 đọc lại chính evidence của Paper 1. Bộ nhãn người chỉ có 11 cặp, và chấm loại khẳng định trong câu chứ không chấm sự thật của cạnh.
- Bảy biến ngân hàng là simulated_calibrated hoặc derived. Mọi "chiều theo dữ liệu" trên các cặp ngân hàng là thuộc tính của bộ mô phỏng, không phải của Việt Nam. Với T = 19, Granger và LiNGAM gần như không có power.
- Mức tự tin tuyệt đối của LLM phụ thuộc mạnh vào prompt: P(edge) trung bình 0.26 ở A và 0.53 ở B. Chỉ dùng thứ hạng.
- Lexical retrieval còn thô: Z_SCORE chỉ có 4 chunk, GDP–POLICY không có chunk nhắc chung nào (phải dựa vào evidence chunk của Paper 1).
- L3 thưa: chỉ 8 cluster consensus trong 19 quý. Mapping "biến bị tác động" dễ gượng (NĐ 65 → TRADE_VOLUME), và có 1 stance sai (R049). Chuỗi proxy chưa dùng được làm external instrument trên dữ liệu thật; chỉ đủ để minh họa và để định ngày cho kịch bản mô phỏng.
- Plan §8: điểm theo cạnh thuộc Bài 3. Ở đây điểm theo cạnh chỉ được tạo ra và đo chất lượng. Có dùng chúng trong module Bài 4 trên dữ liệu thật hay không là việc thầy quyết định; nếu không thì chuyển sang Bài 5.
- Kết quả trên dữ liệu thật chỉ được đọc là phụ thuộc hàm có điều kiện, không phải hiệu ứng nhân quả.

## 9. Cách đưa vào module text-informed

- **File sẵn dùng:** `results/ext_llm_edges/textinfo_side_info.json`. Khóa cặp là `"u-v"` theo chỉ số trong `node_order`, đúng format của `src/paper4/ext_textinfo.py`.
  - `doubt` (21 cặp prior) = ½ L4 doubt + ½ L1 reversal suspicion.
  - `suspicion` cho mọi cặp không kề: L4 support cho 40 ứng viên, 0 cho các cặp còn lại.
  - `sign` (15 cặp): chỉ lấy khi hai biến thể đồng ý cả chiều lẫn sign.
  - Module chỉ dùng rank nên không cần hiệu chỉnh thang.
- **Trong mô phỏng:** không dùng trực tiếp được vì topology mô phỏng không có văn bản. Kết quả ở đây chỉ dùng để **chọn mức a**: chạy `textinfo` với a ∈ {0.5, 0.7, 0.9}, coi 0.7 là kịch bản LLM thực tế, và `sign_error` ≈ 0.1–0.2.
- **Thứ tự L1:** dùng làm nguồn tách riêng cho reversal pool (cạnh cùng kỳ nào có khả năng đảo), hoặc làm thứ tự Cholesky thay thế trong phân tích độ nhạy. Hai thứ tự T1/P và T2 khác nhau đúng ở vị trí của POLICY_RATE, nên đó là trục độ nhạy tự nhiên.
- **Lag từ L4:** cạnh có `lag_majority = later_quarters` (POLICY→STOCK_PRICE, NPL→ROE, CPI→NPL, POLICY→NPL, NIM→CAR) nên được ưu tiên mở lag thay vì giữ ở lag 0, khi module mở lag có mục tiêu.
- **Chuỗi L3:** chưa nên dùng làm instrument trên dữ liệu thật. Có thể dùng các quý 2022Q3–Q4 làm "sự kiện thời gian" trong generator mở rộng T (plan §5.5), và dùng `events.json` làm danh sách để người kiểm duyệt (human-in-the-loop, L4 trong đề xuất).
