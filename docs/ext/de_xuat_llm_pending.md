# Đề xuất dùng LLM cho module chịu lỗi (PENDING, chờ duyệt)

**Trạng thái.** Chưa làm. Theo yêu cầu, mọi việc cần gọi LLM phải được đề xuất và duyệt trước. Phần không cần LLM (dùng lại output Paper 1 đã có sẵn) đang được làm ở hướng `textinfo` (docs/ext/textinfo.md).

**Nguồn dữ liệu văn bản đã có** (chỉ đọc, không sửa):

- `ACIIDS/01_paper1_foundation/rag_kb/rag_kb_full_content.jsonl`: 278 chunk tin tức/báo cáo. Mỗi chunk có `event_time`, `headline`, `chunk_content`, `source`.
- `ACIIDS/01_paper1_foundation/prior_graph/pipeline_output_raw_278chunk.jsonl`: 124 quan hệ đã trích, trong đó 82 accepted và 42 rejected.
  - `sign`: 41 quan hệ là `policy_shock`.
  - `lag_hint`: 90 `immediate`, 30 `unknown`, chỉ 4 `1_quarter`.
  - `event_date`: 26 quan hệ có ngày sự kiện.
- `ACIIDS/01_paper1_foundation/prior_graph/prior_graph_final_278.json`: 42 cạnh prior. Mỗi cạnh có `confidence`, `n_instances`, `n_distinct_sources`, `conflicted`.

## Các đề xuất

| # | Ý tưởng | LLM làm gì | Thứ module nhận thêm | Đánh giá thế nào | Ghi chú |
|---|---|---|---|---|---|
| L1 | **Causal order thay cho cạnh** (Vashishtha và cộng sự, ICLR 2025) | Hỏi theo bộ ba biến (triplet prompts) để suy ra thứ tự nhân quả cùng kỳ của 14 biến | Thứ tự cùng kỳ. Trong SVAR đệ quy, thứ tự này quyết định identification, nên nó cho biết cạnh nào có khả năng bị đảo | Mô phỏng: thay LLM bằng một thứ tự có lỗi ở mức kiểm soát. Dữ liệu thật: chỉ mô tả | Khoảng 364 bộ ba; chi phí thấp |
| L2 | **Chấm lại độ tin của từng cạnh và lag** | Đọc lại các chunk liên quan, cho lag (`lag_hint` hiện gần như toàn `immediate`/`unknown`), cho độ tin, và đo độ đồng thuận giữa các prompt/model (Kumar và cộng sự 2026: confidence lấy từ logit không đáng tin) | Bản đồ nghi ngờ theo từng cạnh tốt hơn, cùng lag hint | Hướng `textinfo` đã đo được lợi ích theo chất lượng tín hiệu (AUROC). L2 chỉ cần cho thấy tín hiệu thật đạt mức chất lượng nào | Ranh giới plan: edge score thuộc Bài 3 |
| L3 | **Chuỗi cú sốc từ văn bản làm proxy** (theo Aruoba–Drechsel 2024) | Gán ngày và độ lớn cho các cú sốc chính sách (41 quan hệ `policy_shock`, 26 ngày sự kiện), tạo chuỗi proxy theo quý | Một external instrument cho cú sốc chính sách. Nó định chiều các cạnh cùng kỳ của biến chính sách: đúng phần mà dữ liệu không nhận diện được | Mô phỏng: proxy = cú sốc + nhiễu. Dữ liệu thật: T = 19 quá ngắn, chỉ minh họa | Khảo sát chưa thấy bài nào dùng proxy sinh bởi LLM trong proxy-SVAR có suy luận chính thức, nên đây là khoảng trống. Có thể thuộc Bài 5 |
| L4 | **"Data đề xuất, text phân xử"** | Khi module tìm được cặp nghi thiếu cạnh (bước repair) hoặc nghi đảo, truy xuất các chunk liên quan và hỏi LLM chiều hoặc có-không | Chiều cho các cạnh được thêm lại (hiện đang rút ngẫu nhiên) và cho các cạnh trong reversal pool | Mô phỏng: LLM được thay bằng một "oracle có lỗi". Dữ liệu thật: case study định tính | Nối Paper 1 với Paper 4. Cần một luồng human-in-the-loop |
| L5 | **LLM ước lượng mức hỏng của prior** | Cho LLM đánh giá độ đầy đủ của prior theo từng lĩnh vực | `damage_estimate` | Yếu: LLM hay dự đoán thừa cạnh và tự tin không đúng mức (Kumar 2026) | Ưu tiên thấp. Hướng B1 (ước lượng từ dữ liệu) hợp lý hơn |

## Thứ tự đề xuất nếu được duyệt

1. **L3 và L4 có tiềm năng đóng góp lớn nhất.** L3 lấp đúng điểm yếu cố hữu của module: chiều của cạnh cùng kỳ không học được từ dữ liệu. L4 biến pipeline Paper 1 → Paper 4 thành một vòng lặp có kiểm chứng.
2. **L1 rẻ và có tài liệu ủng hộ.** Có thể làm trước để thử nghiệm.
3. **Trước khi làm, cần thầy quyết định:**
   - text và LLM thuộc Bài 4 hay Bài 5, vì plan §9 xếp phần lớn các hướng mở rộng vào Bài 5;
   - có được dùng điểm theo cạnh từ Paper 1 hay không, vì plan §8 nói edge score thuộc Bài 3.
