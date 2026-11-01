# Kết quả RQ4.3: bản đồ chi phí theo cạnh (bản thăm dò)

**Câu hỏi (plan, RQ4.3).** Cạnh nào của skeleton, khi sai, làm hiệu ứng lệch nhiều nhất? Bản đồ này có ổn định qua các topology không?

**Cách làm** (`experiments/run_edge_cost.py`, kết quả ở `results/rq43_edge_cost/`):

- **Dữ liệu:** toàn bộ 40 topology của D-07 (development và confirmatory), mỗi topology 2 lần lặp.
- **Làm hỏng:** mỗi lần chỉ làm hỏng **một** cạnh thật. Xóa cạnh đó; nếu là cạnh cùng kỳ thì làm thêm một lần đảo chiều.
- **Ước lượng:** dùng ước lượng điểm (`plugin`) trên chuỗi T = 2000. Chuỗi dài để độ lệch đo được là lệch do cạnh sai, không phải do nhiễu.
- **Chi phí với một cặp mục tiêu (i → j):** |Ĉ(skeleton hỏng) − Ĉ(skeleton đúng)| / |C_thật|.
- **Phân loại cạnh:** theo **vai trò** so với cặp mục tiêu, không theo tên cạnh, để bản đồ chuyển được sang topology khác. Có 4 vai trò: nằm trên đường đi i ⇝ j; đi vào biến gây sốc i; đi vào biến chịu tác động j; khác.

## Kết quả

Mỗi ô ghi: trung vị chi phí tương đối / tỷ lệ cặp bị lệch quá 20%.

| Hỏng | Lag của cạnh | Trên đường đi | Đi vào nguồn i | Đi vào đích j | Khác |
|---|---|---|---|---|---|
| Thiếu | cùng kỳ | **0.93 / 0.81** | 0.10 / 0.19 | 0.03 / 0.12 | 0.00 / 0.00 |
| Thiếu | có lag | **0.81 / 0.73** | 0.07 / 0.16 | 0.06 / 0.23 | 0.00 / 0.01 |
| Đảo | cùng kỳ | **0.53 / 0.77** | 0.14 / 0.40 | 0.05 / 0.09 | 0.00 / 0.03 |

**Độ ổn định:**

- Tương quan Spearman giữa trung vị chi phí trên các topology development và confirmatory: **0.99**, tính trên 12 ô.
- Giữa topology Erdős–Rényi và scale-free hub: **0.97**.

## Đọc kết quả

1. **Gần như toàn bộ chi phí đến từ cạnh nằm trên đường truyền dẫn.** Mất một cạnh như vậy thì hiệu ứng lệch khoảng 80–93%, tức mất gần hết. Đảo chiều một cạnh cùng kỳ trên đường đi làm hiệu ứng lệch khoảng một nửa.
2. **Cạnh đi vào biến gây sốc gây hại nhỏ** (trung vị 7–14%), vì IRF chỉ dùng các phương trình nằm sau biến gây sốc. Riêng trường hợp đảo cạnh đi vào nguồn trên topology scale-free hub thì đáng kể hơn: trung vị 0.27, và 59% số cặp lệch quá 20%.
3. **Cạnh không liên quan tới cặp mục tiêu hầu như không gây hại.** Những cạnh này chiếm đa số, nên tỷ lệ hỏng chung không phải là thước đo tốt cho mức độ nguy hiểm.
4. **Bản đồ theo vai trò ổn định qua các topology** (ρ = 0.97–0.99). Điều này trả lời vế thứ hai của RQ4.3: bản đồ dùng được cho topology mới.

## Ý nghĩa cho Bài 5 và Bài 3 (plan mục 8)

- **Bài 5:** để biết một hiệu ứng có đáng tin không, chỉ cần kiểm tra các cạnh nằm trên đường đi của nó, không cần kiểm tra cả skeleton.
- **Bài 3 (phần tùy chọn):** trọng số chi phí cho quyết định admit / abstain nên đặt nặng vào các cạnh có khả năng nằm trên nhiều đường truyền dẫn.

## Giới hạn

- Chi phí đo trên ước lượng điểm (`plugin`), chưa đo trên module. Module v3 được thiết kế chính để giảm loại chi phí "trên đường đi". Bảng tương ứng cho module là việc tiếp theo.
- Mỗi lần chỉ hỏng một cạnh, nên tương tác giữa nhiều cạnh hỏng cùng lúc chưa được đo.
- Generator chỉ có một kiểu: tuyến tính, nhiễu Gauss, lag_max = 2.
