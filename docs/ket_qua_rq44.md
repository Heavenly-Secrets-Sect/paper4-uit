# Kết quả RQ4.4: cờ tin cậy không cần đáp án (bản thăm dò)

**Câu hỏi (plan, RQ4.4).** Có đại lượng nào quan sát được, không cần biết đáp án, mà dự báo được hiệu ứng nào đáng tin không?

**Cách làm** (`experiments/run_flags.py`, kết quả ở `results/rq44_flags/`):

- **Dữ liệu:** bank D-07, mỗi topology 2 lần lặp, T ∈ {80, 150}.
- **Ô hỏng:** không hỏng; thiếu 20% / 50%; đảo 20% / 50%.
- **Module:** `tolerant_v3_cal`.
- **Biến cần dự báo:** một cặp gọi là *không đáng tin* khi ước lượng lệch quá 50% so với |C_thật|, **hoặc** khoảng tin cậy không chứa giá trị thật. Tỷ lệ chung là 23%.
- **Cách đánh giá:** AUROC trên các topology confirmatory. Mô hình logistic kết hợp các tín hiệu được fit trên các topology development, nên phép đánh giá tách theo topology.

## Các tín hiệu

| Tín hiệu | Định nghĩa |
|---|---|
| `rel_width` | Độ rộng khoảng / \|Ĉ\| của module |
| `struct_sens` | \|Ĉ_module − Ĉ_plugin\| / độ rộng khoảng: kết quả xê dịch bao nhiêu khi nới lỏng skeleton |
| `method_sens` | \|Ĉ_plugin − Ĉ_lp\| / độ rộng khoảng của LP: SVAR và local projection bất đồng bao nhiêu |
| `zero_in` | Khoảng tin cậy có chứa 0 hay không |

## Kết quả (AUROC trên topology confirmatory)

| T | Hỏng | Tỷ lệ không đáng tin | `rel_width` | `struct_sens` | `method_sens` | `zero_in` | Kết hợp |
|---|---|---|---|---|---|---|---|
| tất cả | tất cả | 0.231 | **0.834** | 0.548 | 0.504 | 0.712 | 0.834 |
| 80 | không hỏng | 0.203 | 0.744 | 0.500 | 0.511 | 0.649 | 0.743 |
| 80 | thiếu 50% | 0.326 | 0.820 | 0.368 | 0.426 | 0.586 | 0.824 |
| 150 | thiếu 20% | 0.203 | 0.846 | 0.509 | 0.502 | 0.753 | 0.853 |
| 150 | đảo 50% | 0.202 | 0.862 | 0.599 | 0.540 | 0.759 | 0.862 |

## Đọc kết quả

1. **Độ rộng tương đối là cờ tốt nhất** (AUROC 0.74–0.87). Ghép thêm các tín hiệu khác không cải thiện gì.
2. **Hai tín hiệu "độ nhạy" gần như không có thông tin** (AUROC khoảng 0.5). Lý do: module đã đưa phần bất định về cấu trúc vào trong chính khoảng tin cậy, nên phần xê dịch còn lại không mang thêm thông tin. Đây là kết quả âm, cần báo cáo đúng như vậy.
3. **Hệ quả thực hành cho Bài 5:** cờ tin cậy chỉ cần một ngưỡng trên độ rộng tương đối. Ví dụ: đánh dấu "không đáng tin" khi độ rộng vượt 2 lần |Ĉ|. Ngưỡng cụ thể nên chọn theo mức báo động giả chấp nhận được.

## Giới hạn

- Biến cần dự báo gộp hai loại thất bại: lệch lớn và khoảng không chứa giá trị thật. Độ rộng tương đối tự nhiên bắt được loại lệch lớn ở những cặp có hiệu ứng nhỏ so với nhiễu.
- Chưa thử các tín hiệu khác mà plan liệt kê: độ ổn định hệ số qua cửa sổ thời gian, chẩn đoán phần dư, độ ổn định lag.
- Chỉ dùng một kiểu generator.
