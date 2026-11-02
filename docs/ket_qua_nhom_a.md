# Kết quả nhóm A (bản thăm dò)

**Trạng thái.** Exploratory, chạy trên D-07 development với `tolerant_v4` đã đóng băng: không đổi code, không đổi hệ số width. Các quy tắc được ghi **trước khi chạy** ở [decision_rules.md](decision_rules.md), mục "A-group checks". Kết quả đầy đủ nằm trong `results/a2_baselines/`, `results/a1_latent_noise/` và `results/a3_ges/`.

Mỗi ô trong các bảng dưới ghi **coverage / interval score**. Coverage nên gần 0.95; interval score càng thấp càng tốt.

## A2: so với baseline đã công bố

Hai baseline mới, cả hai đều nằm trong [methods.py](../src/paper4/methods.py):

- **`ida_union`** (IDA, Maathuis và cộng sự 2009).
  - Fit mọi DAG trong Markov equivalence class của skeleton, tối đa 16 DAG.
  - Interval là union của các interval bootstrap.
  - Không đọc mức hỏng khai báo.
- **`bvar_minnesota`** (Bayesian VAR, Minnesota prior).
  - Mọi lag của mọi biến đều được đưa vào. Cặp nằm ngoài skeleton bị prior siết chặt hơn.
  - Hyperparameter chọn bằng marginal likelihood, theo tinh thần Giannone–Lenza–Primiceri 2015.

Bảng sau là kết quả ở T = 150 (trích):

| Hỏng | `plugin` | `lp_allpast` | `ida_union` | `bvar_minnesota` | **`tolerant_v4`** |
|---|---|---|---|---|---|
| Không hỏng | 0.93 / 1.58 | 0.91 / 2.66 | 0.97 / 1.73 | 0.94 / 1.86 | 0.96 / 1.56 |
| Thiếu 20% | 0.66 / 11.47 | 0.90 / 2.74 | 0.72 / 10.71 | 0.77 / 5.90 | **0.97 / 2.06** |
| Thiếu 50% | 0.33 / 29.07 | 0.90 / 2.88 | 0.36 / 28.33 | 0.57 / 10.18 | **0.96 / 2.22** |
| Đảo 20% | 0.86 / 2.96 | 0.88 / 3.51 | 0.93 / 2.25 | 0.87 / 3.03 | **0.97 / 1.89** |
| Đảo 50% | 0.74 / 5.12 | 0.84 / 4.74 | 0.85 / 3.70 | 0.76 / 5.09 | **0.96 / 2.02** |

**Theo quy tắc ghi trước, module đạt 13/18 cell bị hỏng.**

- **Thiếu cạnh: đạt 6/6.** Hai baseline đã công bố đều không khôi phục được cạnh bị thiếu.
  - `ida_union` chỉ xét lại chiều của các cạnh có sẵn, nên coverage chỉ 0.36–0.73.
  - `bvar_minnesota` có đưa mọi lag vào, nhưng prior kéo hệ số của cạnh ngoài skeleton về 0. Đây là đúng lỗi của bản v1 `soft`. Coverage của nó là 0.48–0.77.
- **Đảo cạnh: đạt 4/6.** Hai cell không đạt là đảo 20% ở T = 40 và T = 80. Ở đó module hòa với `ida_union`: chênh lệch âm nhưng CI cắt qua 0. Kết quả này hợp lý, vì IDA được thiết kế chính cho bất định về chiều cạnh.
- **Thừa cạnh: đạt 3/6.** Các cell không đạt đều là hòa. Khi skeleton chỉ thừa cạnh, mọi method đều xấp xỉ `plugin`.

### A2b: baseline thứ ba, chuyển thể Chang–Guo–Malinsky (`pselect_union`)

Cách làm của baseline này:
- Chọn lại adjacency từ dữ liệu, dựa trên Granger test và tương quan riêng phần của phần dư.
- Lặp lại việc chọn 100 lần, mỗi lần cộng nhiễu ngẫu nhiên vào z-score.
- Lấy union interval qua tối đa 16 đồ thị thu được.

Đây là bản chuyển thể sang SVAR, không phải thủ tục gốc.

**Kết quả trên D-07 development: module thắng 16/18 cell.** Hai cell thua đều là **thiếu cạnh ở T = 40**:

| T = 40, thiếu 50% | Coverage | Width | Interval score |
|---|---|---|---|
| `pselect_union` | 0.85 | 3.5 | **6.63** |
| `tolerant_v4` | **0.98** | 6.5 | 7.53 |

Module đạt coverage, còn baseline thì không. Nhưng interval của module rộng gấp đôi, tức là **ở T nhỏ module quá thận trọng với cạnh thiếu**. Từ T = 80 trở lên, module thắng mọi cell.

### Kiểm tra held-out (P4-H1 development, chạy một lần)

| Phần | Tiêu chí ghi trước | Kết quả |
|---|---|---|
| A2 | Thắng mọi baseline đã công bố ở cả 6 cell thiếu cạnh | **Không đạt.** Thắng 4/4 cell ở T ≥ 80. Ở T = 40: thua `pselect_union` ở thiếu 20%, hòa ở thiếu 50% |
| A1 | Coverage ≥ 0.90 ở mọi cell latent1 và ≥ 5/6 cell latent3 | **Đạt:** 6/6 và 5/6. `oracle` còn 0.76 |
| A3 | Coverage ≥ 0.90, và interval score tốt hơn `plugin` ở mọi T | **Đạt:** coverage 0.96 / 0.94 / 0.94 |

Ở held-out, nhiễu đo 10% chỉ đạt 2/6 cell (trên D-07 là 4/6). Nhiễu đo vẫn là limitation.

**Kết luận được phép viết:**

> Module thắng các baseline đã công bố khi T ≥ 80. Ở T = 40, nó là method duy nhất đạt coverage, nhưng interval rộng hơn mức cần thiết.

## A1: biến ẩn và nhiễu đo (plan §9)

Các kịch bản được thử:

- **Biến ẩn:** 1 hoặc 3 biến ẩn AR(1), mỗi biến tác động lên 3 biến quan sát.
- **Nhiễu đo:** phương sai nhiễu bằng 10% hoặc 30% phương sai của chuỗi, tương ứng reliability 0.91 và 0.77.

Truth giữ nguyên ở mọi kịch bản. Calibration chỉ dùng dữ liệu sạch, nên module gặp các sai lệch này mà không được chuẩn bị trước.

Bảng dưới là coverage của `tolerant_v4`. Ô in đậm là ô dưới 0.90.

| Kịch bản | T=80 none | T=80 thiếu 20% | T=80 đảo 20% | T=150 none | T=150 thiếu 20% | T=150 đảo 20% |
|---|---|---|---|---|---|---|
| clean | 0.93 | 0.94 | 0.93 | 0.96 | 0.97 | 0.96 |
| 1 biến ẩn | 0.93 | 0.95 | 0.93 | 0.93 | 0.95 | 0.95 |
| 3 biến ẩn | 0.95 | 0.95 | 0.96 | **0.87** | 0.93 | 0.92 |
| nhiễu 10% | **0.89** | 0.92 | **0.89** | 0.92 | 0.93 | 0.91 |
| nhiễu 30% | **0.81** | **0.89** | **0.79** | **0.77** | **0.83** | **0.78** |

So sánh: ở kịch bản 3 biến ẩn, T = 150, coverage của `oracle` chỉ còn 0.78. Ở nhiễu 30%, `oracle` còn 0.35–0.48.

**Đọc kết quả:**

1. **Module chịu được biến ẩn khá tốt.** Coverage ≥ 0.92 ở 11/12 cell. Ngay cả `oracle` (biết đồ thị quan sát thật) cũng mất coverage. Thiệt hại tăng theo T, vì bias do biến ẩn không giảm khi có thêm dữ liệu.
2. **Đúng như dự đoán, biến ẩn kích hoạt bước repair.** Số cạnh cùng kỳ được "sửa" tăng từ 1.67 (clean) lên 2.82 (3 biến ẩn), ở T = 150, thiếu 20%. Module nhầm confounder thành cạnh thiếu. Nhưng vì mỗi lần nhầm cũng làm rộng interval, coverage vẫn đứng.
3. **Nhiễu đo 30% là giới hạn rõ ràng.** Coverage còn 0.77–0.89. Nhiễu đo làm hệ số bị kéo về 0 (attenuation bias), và không method nào được thiết kế để xử lý việc này. Ở cell đảo cạnh, `inflate` còn làm tốt hơn module. Đây là limitation phải ghi trong bài, và là ứng viên cho một hướng sửa (errors-in-variables).

## A3: skeleton do GES của Paper 2 học

**Thiết lập.**

- GES của Paper 2 được import chỉ đọc từ ACIIDS. Nó chạy đúng như Paper 2: coi các hàng dữ liệu là i.i.d.
- GES học trên một chuỗi **độc lập**, cùng độ dài, để không double dipping (plan §5.2).
- Mức hỏng khai báo là số lỗi trung bình của GES, đo trên bank D-07H.

**GES sai rất nhiều.** Trung bình trên 21 cạnh thật:

| T | Thiếu | Thừa | Đảo |
|---|---|---|---|
| 40 | 14.1 | 12.7 | 3.2 |
| 80 | 12.9 | 12.6 | 2.9 |
| 150 | 11.6 | 13.2 | 3.7 |

Lý do chính: GES bỏ qua thời gian nên sót các cạnh có lag. Số cạnh thiếu dao động 6–19 tùy skeleton, trong khi mức khai báo cố định là 12–13. Nghĩa là **mỗi skeleton nhận một khai báo không chính xác.**

**Kết quả với skeleton GES:**

| T | `plugin` | `inflate` | `lp_allpast` | `ida_union` | `bvar_minnesota` | **`tolerant_v4`** |
|---|---|---|---|---|---|---|
| 40 | 0.38 / 21.8 | 0.86 / 19.8 | không chạy được | 0.39 / 22.0 | 0.41 / 15.6 | **0.98 / 8.3** |
| 80 | 0.35 / 22.5 | 0.83 / 15.2 | 0.82 / 6.7 | 0.35 / 22.6 | 0.49 / 12.5 | **0.95 / 3.7** |
| 150 | 0.32 / 22.2 | 0.80 / 13.1 | 0.86 / 4.4 | 0.32 / 22.2 | 0.59 / 7.8 | **0.94 / 2.6** |

**Claim đạt ở mọi T.** Với skeleton học bằng thuật toán thật và khai báo mức hỏng chỉ là ước lượng:

- Module là method **duy nhất** giữ coverage ≥ 0.94.
- Interval score của module tốt nhất ở mọi T. So với `plugin`, nó thấp hơn 13.5–19.6.

Đây là bằng chứng mạnh nhất hiện có cho câu chuyện "pipeline thật": skeleton từ thuật toán → module → interval đáng tin.

## Tóm tắt cho phần đóng góp

| Câu hỏi reviewer có thể đặt ra | Bằng chứng mới |
|---|---|
| Đã so với phương pháp đã công bố chưa? | Đã so với IDA, BVAR và bản chuyển thể Chang–Guo–Malinsky. Ở T ≥ 80, module thắng ở mọi cell thiếu cạnh, trên cả held-out. Ở T = 40, `pselect_union` có interval score tốt hơn nhưng coverage chỉ 0.85 |
| Có chịu được biến ẩn không? | Có, coverage ≥ 0.92 ở 11/12 cell, trong khi `oracle` tụt còn 0.78 |
| Có chịu được nhiễu đo không? | Chịu được nhiễu 10% ở phần lớn cell. **Không** chịu được nhiễu 30%: đây là limitation |
| Lỗi skeleton có phải do mình tự tạo nên quá dễ? | Với skeleton thật từ GES (sai khoảng 60% cạnh) và mức hỏng khai báo không chính xác, module vẫn đạt coverage 0.94–0.98 |

## Việc nên làm tiếp

1. **Đã làm:** baseline Chang–Guo–Malinsky (A2b) và kiểm tra held-out (xem trên).
2. **Thu hẹp interval ở T nhỏ:** ở T = 40, module rộng gấp đôi `pselect_union`. Có thể mượn bước chọn lại adjacency từ dữ liệu của baseline này.
3. **Nhiễu đo:** thử hiệu chỉnh errors-in-variables. Đây có thể là một mở rộng của nhóm B.
4. **B1 (tự ước lượng mức hỏng):** A3 cho thấy khai báo theo trung bình của thuật toán đã đủ tốt. B1 sẽ bỏ luôn bước khai báo này.
