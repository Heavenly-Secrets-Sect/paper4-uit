# Vùng dùng được của `tolerant_v5_1` (sản phẩm 4 của plan), bản exploratory

**Mục tiêu.** Đo lại bản đồ vùng dùng được, tức method dùng được hay không theo (lag_max, T, loại và mức hỏng), cho module chính thức mới `tolerant_v5_1`. Bản đồ cũ của v4 nằm ở docs/ket_qua_vung_dung_duoc.md. Mọi kết quả ở đây là exploratory trên D-07 development.

## Thiết kế, ghi trước khi chạy (2026-11-02)

**Lưới.** Giữ nguyên lưới của bản đồ v4 để so sánh trực tiếp. Seed giống bản cũ (seed_base 20261101), nên dữ liệu và skeleton trùng với bản đồ v4.

| lag_max | T | Config |
|---|---|---|
| 1 | 19, 25, 30, 40 | `ext_region51_lag1` |
| 2 | 19, 25, 30, 40, 60 | `ext_region51_lag2` |
| 4 | 40, 60, 80, 150 | `ext_region51_lag4` |

- Cell hỏng: none, missing 0.2 / 0.5, reversed 0.2 / 0.5.
- D-07 development: 20 topology × 3 replicate.
- Method: `oracle`, `plugin`, `tolerant_v4`, `tolerant_v5_1`.

**Calibration.** D-07H development, như bản đồ v4. Hai module được tune lại width ở từng (lag_max, T), vì file frozen chỉ có lag_max = 2 và T = 40/80/150/300. Cụ thể, v4 dùng hệ số `mod|T|kind`, còn v5.1 nằm trong `calibrate_methods`.

**Tham số τ.** Với lưới này, τ không kích hoạt nhánh all-lag. Số dòng trên mỗi biến hồi quy r ≤ 2.6 ở mọi ô, nhỏ hơn τ = 6.61, nên v5.1 luôn đi nhánh targeted.

**Định nghĩa "dùng được", ghi trước.** Một ô (lag_max, T, cell) dùng được với một method nếu thỏa đủ ba điều kiện:
1. Ít nhất 57/60 run trả kết quả (status ok).
2. Coverage gộp ≥ 0.90.
3. IS trung bình ≤ 3 × IS của `oracle` ở cùng (lag_max, T). Điều kiện này bắt trường hợp interval "phát nổ", điều mà bản đồ v4 chỉ ghi định tính.

**T tối thiểu** của một (method, lag_max, loại hỏng) là T nhỏ nhất trên lưới sao cho mọi T từ đó trở lên đều dùng được ở cả hai mức hỏng.

**Báo cáo.**
- Bản đồ v5.1 đặt cạnh bản đồ v4 tính lại trên cùng run.
- Bảng T tối thiểu.
- Câu trả lời cho dữ liệu thật: lag_max = 1, T = 19, n = 14. Ô này có dùng được với v5.1 không?
- Kiểm tra ghép cặp: dòng `plugin` của run mới phải trùng dòng của run `rq42_region_lag*` cũ (cùng seed).

Phần này chỉ mô tả, không có quy tắc giữ hay loại nào. Kết quả không đổi module chính thức.

## Kết quả (sinh bởi `experiments/ext/region51_analyze.py`; bảng đầy đủ ở `results/ext_region51/region_map.md`)

**Kiểm tra ghép cặp.** Dòng `plugin` trùng khít với các run `rq42_region_lag*` cũ: 1200/1200, 1500/1500 và 1200/1200.

**T tối thiểu** (mọi T từ mức này trở lên đều dùng được, ở cả hai mức hỏng):

| lag_max | Loại hỏng | v4 | **v5.1** |
|---|---|---|---|
| 1 | none | 19 | 19 |
| 1 | missing | 25 | **19** |
| 1 | reversed | 19 | 25 |
| 2 | none / missing / reversed | 40 / 40 / 40 | 40 / 40 / 40 |
| 4 | none | 80 | 80 |
| 4 | missing | 150 | **80** |
| 4 | reversed | 80 | 80 |

**Đọc kết quả.**

1. **v5.1 mở rộng vùng dùng được ở nhánh thiếu cạnh.**
   - Với lag_max = 1, T = 19 nay dùng được: coverage 0.93 / 0.96, IS 7.75 / 8.38 ở missing 0.2 / 0.5. Ở cùng ô, v4 không chạy được run nào (0/60).
   - Với lag_max = 4, v5.1 dùng được từ T = 80, trong khi v4 cần T = 150. Ở T = 80 missing-0.5, v4 có IS 4.51, vượt ngưỡng 3 × oracle.
2. **Một ô v5.1 kém hơn v4:** lag_max = 1, T = 19, reversed-0.5. v5.1 có IS 15.69, vượt ngưỡng 3 × oracle; v4 có 12.36 và dùng được. Vì vậy T tối thiểu của v5.1 cho nhánh đảo cạnh ở lag_max = 1 là 25.
3. **Với lag_max = 2, cả hai module đều cần T ≥ 40, và giới hạn không đến từ nhánh thiếu cạnh.**
   - Ở T < 40, ngay cả ô không hỏng cũng chỉ có 9–54/60 run chạy được, với mọi method kể cả `plugin`.
   - Nguyên nhân: phương trình theo skeleton của các nút có nhiều hàng xóm có quá nhiều biến hồi quy. Mỗi cặp kề đưa lag theo cả hai chiều vào phương trình (`parent_terms`).
   - Đây là giới hạn của cách dựng phương trình cơ sở, không phải của module.
4. **Dữ liệu thật (n = 14, T = 19, lag_max = 1):** v5.1 dùng được ở các ô none, missing 0.2 / 0.5 và reversed 0.2. Ô reversed 0.5 thì không. Điều này mở ra khả năng làm case study trên panel thật khi prior được khai báo là thiếu cạnh, điều v4 không làm được. Kết quả là exploratory, và chỉ đúng cho generator mô phỏng của Paper 4.
