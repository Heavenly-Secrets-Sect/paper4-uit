# Lý thuyết coverage: bản nháp và kiểm tra V1

Ngày 2026-11-14. Khám phá (exploratory), không phải xác nhận. Không dùng bank mới.

## Bản nháp lý thuyết
[coverage_theory_draft.md](coverage_theory_draft.md) (tiếng Anh). Do một nhóm agent tranh luận (hai người đề xuất, hai vòng phản biện, một giám khảo); **chưa được kiểm chứng bằng máy hay bởi người ngoài**. Kết luận chính của bản nháp:

- Mệnh đề giữ lại là cận hạng ở mức topology: với đơn vị là một topology và điểm đơn vị S (hệ số nhỏ nhất làm tỉ lệ cặp phi-null bị trượt không quá β), lấy ĉ là điểm lớn nhất trên các đơn vị hiệu chỉnh thì topology mới có xác suất vượt ĉ không quá 1/(N'+1) (1/21 khi N' = 20).
- Cận có điều kiện theo mẫu hiệu chỉnh: với N' = 20, P(độ phủ thực của ĉ ≤ 0,95) có thể tới 0,36; muốn "95% chắc chắn" cần N' ≥ 59.
- Luật đang chạy (phân vị gộp mức cặp) **không** nằm trong mệnh đề; hệ số đóng băng 2,3 đến 2,8 không được bảo đảm.
- Hoán vị giữa bank hiệu chỉnh (D-07H) và các bank kiểm tra không có cơ sở; tham số thiết kế (TAU) đã dò trên D-07H.
- Hệ số 0,5 (`PRESCALE`) không có lý thuyết; chỉ là tham số hóa lại lưới. Nếu cố định và áp giống nhau cho hiệu chỉnh và kiểm tra thì chỉ tích 0,5·c vào khoảng.

## V1: có vô nghĩa (vacuous) không?
Mã: `experiments/ext/coverage_theory/v1_dump.py`, `v1_analyze.py`. Chạy lại pha hiệu chỉnh của `ext_v51_eval` (D-07H development, 20 topology, 1 replicate, lag_max = 2), giữ (dist, half) từng cặp theo đơn vị. Kết quả: [results/ext_coverage_v1/v1_summary.md](../../results/ext_coverage_v1/v1_summary.md); `v1_pairs.json` (0,5 MB) tái tạo được trong khoảng 1 phút.

Kết quả:

1. **Tái lập đúng**: hệ số gộp mức cặp tính lại khớp hệ số đóng băng ở cả 12 ô (T ∈ {40, 80, 150} × 4 loại).
2. **Không vô nghĩa với v5.1**: không có cặp bị mất (lost pair) nào, độ phủ gộp tối đa trên lưới là 1,000, không đơn vị nào có S = vô cực ở β = 0,05 hay 0,10. Dự đoán của nhóm tranh luận về hệ số vô cực không áp dụng cho v5.1.
3. **Hệ số đóng băng xấp xỉ trung vị của điểm đơn vị**: trung vị S(0,05) từ 2,2 đến 2,8, gần hệ số đóng băng 2,3 đến 2,8. Phân vị gộp mức cặp bảo đảm độ phủ trung bình khoảng 0,95, không phải mỗi đơn vị.
4. **Giá của bảo đảm mức topology**: điểm lớn nhất trên 20 đơn vị (luật max, β = 0,05) là từ 3,3 đến 6,5, tức gấp 1,3 đến 2,4 lần hệ số đóng băng (hệ số hiệu dụng sau hệ số co trước hiệu chỉnh 0,5 khoảng 1,65 đến 3,25, so với 1,15 đến 1,40 hiện tại). Ô rộng nhất: T = 80 reversed (6,5), T = 40 reversed (5,6), T = 40 extra (5,2).

Giới hạn: một replicate mỗi topology (20 đơn vị); lag_max = 2 (panel thật dùng lag 1); khoảng 29 cặp phi-null mỗi run nên β = 0,05 tương đương tối đa 1 cặp trượt, thang điểm thô; ĉ của luật max do một đơn vị xấu nhất quyết định nên nhiễu. Chưa chạy V2 đến V12.
