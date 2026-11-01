# Vùng dùng được của module (sản phẩm P4 của plan, bản thăm dò)

**Câu hỏi.** Module (`tolerant_v4`, đã đóng băng) dùng được ở tổ hợp (mức hỏng, T, lag_max) nào? Ở đâu nên từ chối báo hiệu ứng (abstain)?

**Cấu hình.** Bank D-07 development, 20 topology × 3 lần lặp. Hệ số độ rộng được hiệu chỉnh lại trên D-07H development cho từng T. Ba lưới thực nghiệm:

| lag_max | T | Config |
|---|---|---|
| 1 | 19, 25, 30, 40 | `rq42_region_lag1` |
| 2 | 19, 25, 30, 40, 60 | `rq42_region_lag2` |
| 4 | 40, 60, 80, 150 | `rq42_region_lag4` |

lag_max = 4 nghĩa là các cạnh có lag được rút từ 1..4.

## Bản đồ

Mỗi ô ghi coverage của module, kèm số lượt chạy được trên 60. **Không** = không ước lượng được: số biến hồi quy vượt số quan sát.

| lag_max | T | Không hỏng | Thiếu 20% | Thiếu 50% | Đảo 20% | Đảo 50% |
|---|---|---|---|---|---|---|
| 1 | 19 | 0.95 (60) | **không** | **không** | 0.97 (60) | 0.97 (58) |
| 1 | 25 | 0.97 (60) | 0.96 (60) | 0.96 (60) | 0.98 (60) | 0.97 (60) |
| 1 | 30–40 | 0.97 | 0.96–0.97 | 0.96 | 0.97–0.98 | 0.96–0.97 |
| 2 | 19 | chỉ 9/60 chạy được | không | không | 10/60 | 11/60, khoảng phát nổ |
| 2 | 25–30 | 0.94 (36–54) | **không** | **không** | 0.96 (36–49) | 0.94–0.96 (35–45) |
| 2 | 40 | 0.96 (60) | 0.98 (60) | 0.98 (60) | 0.96 (60) | 0.96 (60) |
| 2 | 60 | 0.96 (60) | 0.96 (60) | 0.96 (60) | 0.97 (60) | 0.97 (60) |
| 4 | 40 | 0.94 (33), IS không ổn định | không | không | 0.95 (33) | 0.94 (33), IS không ổn định |
| 4 | 60 | 0.96 (54) | **không** | **không** | 0.96 (54) | 0.94 (52) |
| 4 | 80 | 0.96 (60) | 0.96 (60) | 0.96 (60) | 0.96 (60) | 0.96 (60) |
| 4 | 150 | 0.97 (60) | 0.95 (60) | 0.95 (60) | 0.96 (60) | 0.95 (60) |

Đối chiếu: ở cùng các ô, `plugin` đạt coverage 0.34–0.69 khi thiếu cạnh, và 0.72–0.85 khi đảo cạnh.

## Quy tắc báo hoặc từ chối (đề xuất)

1. **Nhánh thiếu cạnh** cần mọi lag của mọi biến, tức n × lag_max biến hồi quy (14 × lag_max ở đây). Ràng buộc cứng là T − lag_max ≥ n × lag_max + (số cha cùng kỳ) + 2. Trên lưới T thô đã chạy, nhánh này chạy được và ổn định từ khoảng **T ≈ 1.4–1.8 × n × lag_max** (25/14 ≈ 1.8; 40/28 = 80/56 ≈ 1.4):

   | lag_max | T tối thiểu (quan sát) |
   |---|---|
   | 1 | 25 |
   | 2 | 40 |
   | 4 | 80 |

   Dưới ngưỡng này, module phải **từ chối báo hiệu ứng** nếu khai báo có cạnh thiếu. Báo theo skeleton như `plugin` thì coverage chỉ còn khoảng 0.35.
2. **Nhánh đảo cạnh và trường hợp không hỏng** chỉ cần số tham số của skeleton, nên chạy được ở T nhỏ hơn. Khi số lượt chạy được dưới 100%, hoặc interval score bùng nổ (lag_max = 4, T = 40), nên từ chối.
3. **Với dữ liệu thật (n = 14, T = 19):**
   - Chỉ có lag_max = 1 là khả thi.
   - Ngay cả khi đó, nhánh thiếu cạnh vẫn **không** chạy được. Lý do: 14 lag, cộng các cạnh cùng kỳ, cộng hệ số chặn, vượt 18 quan sát.
   - Nếu prior trích từ văn bản được khai báo là có thiếu cạnh (nên khai báo như vậy, xem `rq42_misstated`), module sẽ từ chối báo hiệu ứng trên panel 14 × 19.
   - Kết quả này khớp với nhận định của plan: T = 19 chỉ để minh họa. Bài 5 cần panel dài hơn, hoặc phải giảm số biến.

## Giới hạn

- Ngưỡng T tối thiểu đo trên generator tuyến tính, nhiễu Gauss, 14 nút, 21 cạnh. Đồ thị dày hơn hoặc cạnh yếu hơn có thể cần T lớn hơn.
- Một hướng có thể mở rộng vùng dùng được ở T nhỏ: co hệ số (shrinkage) cho riêng các hạng ngoài skeleton. Bản v1 (ridge) đã thất bại vì gây lệch, nên chưa đưa vào.
