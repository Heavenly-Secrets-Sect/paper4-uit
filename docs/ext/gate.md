# B1 version 3: module tự chẩn đoán có cổng quyết định (ID `gate`)

**Trạng thái.** Exploratory. Hướng B1: module không cần khai báo mức hỏng. Code: [src/paper4/ext_gate.py](../../src/paper4/ext_gate.py). Hiệu chỉnh width: [experiments/ext/gate/calibrate_gate.py](../../experiments/ext/gate/calibrate_gate.py). Config đánh giá: `experiments/configs/ext_gate_auto3.json`, kết quả ở `results/ext_gate_auto3/`.

## 1. Vì sao cần bản 3

B1 bản 1 và bản 2 đều bị loại ([decision_rules.md](../decision_rules.md), mục B1). Bài học rút ra:

- Mọi báo động giả đều làm module mở toàn bộ lag. Trên skeleton đúng, điều đó làm interval score tăng 1.3–1.6 lần.
- Đếm theo Storey trên khoảng 70 cặp bị lệch lên 3–5 cặp, ngay cả khi p-value dưới null là uniform.
- Test trên VAR reduced-form không phải là test adjacency hợp lệ.

Vì vậy bản 3 **quyết định trước, sửa sau**. Nó không ước lượng số cạnh thiếu rồi đem số đó vào module v4. Thay vào đó, nó test giả thuyết toàn cục "skeleton không thiếu cạnh nào", và chỉ mở lag khi giả thuyết này bị bác. Ý tưởng theo tinh thần Eulig et al. (AAAI 2025): kiểm tra các hệ quả của đồ thị trên dữ liệu trước khi dùng đồ thị đó.

## 2. Thiết kế `tolerant_auto3`

Method chỉ đọc dữ liệu và skeleton. `skel.damage` bị bỏ ngay ở dòng đầu: skeleton được chép lại với damage rỗng.

1. **Test từng cặp trong structural fit của chính skeleton.** Mỗi phương trình được fit bằng các term của skeleton (`parent_terms`: lag của chính nó, lag của các nút kề, cha cùng kỳ). Với mỗi cặp (u, v) mà skeleton bỏ ra, có ba test:
   - F test khi thêm lag 1..lag_max của u vào phương trình của v;
   - F test tương tự cho lag của v trong phương trình của u;
   - Fisher z của tương quan giữa hai structural residual.

   Ba p-value được gộp bằng Šidák. Nếu skeleton đúng, mỗi phương trình được chỉ định đúng và các structural shock độc lập, nên cả ba test đều hợp lệ. Khác với fit đủ lag của `diagnose.py`, fit hạn chế giữ được bậc tự do, nhờ đó test vẫn có power ở T nhỏ.
2. **Cổng toàn cục.** Thống kê là p-value nhỏ nhất trong các cặp bị bỏ ra. p-value toàn cục tính bằng Šidák qua m cặp: `p_gate = 1 − (1 − p_min)^m`. Cổng mở khi `p_gate ≤ 0.10`.
3. **Cổng đóng:** fit skeleton đúng như được đưa vào (term của `plugin`).
4. **Cổng mở:** dùng nhánh thiếu cạnh của module v4.
   - Mọi lag của mọi nút đều vào mọi phương trình.
   - Cạnh cùng kỳ được thêm lại ở các cặp có structural residual của fit đủ lag tương quan với nhau (BH, q = 0.1). Chiều của cạnh được bốc ngẫu nhiên trong mỗi bootstrap draw.
   - **Ngân sách sửa gắn với bằng chứng:** sửa tối đa K = max(số cặp BH phát hiện ở bước 1, số đếm Storey ở bước 1) cặp.
5. **Dự phòng đảo chiều.** Một cạnh cùng kỳ bị đảo nhưng vẫn nằm trong Markov equivalence class thì không để lại dấu vết nào trong dữ liệu Gaussian, nên không chẩn đoán được. Vì vậy, ở cả hai trạng thái, mỗi bootstrap draw lật từng cạnh cùng kỳ có |t| > 1.645 một cách độc lập với xác suất 0.2 (bỏ qua nếu tạo chu trình). Khi đó percentile interval phủ được cả hai chiều của một liên kết cùng kỳ đã được xác nhận.
6. **Width.** Interval được nới quanh điểm giữa bằng một hệ số tune theo (T, trạng thái cổng) trên bank calibration (D-07H development, các cell calibration của v4). Hệ số do `calibrate_gate.py` tính và lưu ở `experiments/ext/gate/width_table.json`.
   - Hệ số được tra theo **chẩn đoán của chính module**, không theo mức hỏng khai báo.
   - Vì vậy method **không** được liệt kê trong `calibrate_methods` của runner. Key của runner là loại hỏng khai báo, và dùng key đó sẽ đưa khai báo trở lại qua đường width.
   - Đây là điểm lệch duy nhất so với quy tắc chung số 4. Thủ tục chọn hệ số thì giữ nguyên như runner: lưới 1.0..10.0, mục tiêu min(0.95, max coverage − 0.005).

**Ablation `tolerant_auto3_nogate`** (chỉ báo cáo, không chấm quy tắc): luôn chạy nhánh mở với cùng dự phòng đảo chiều, width tune theo T trên mọi cell calibration. Nó cho thấy cổng đóng góp bao nhiêu.

## 3. Probe thăm dò trước khi ghi quy tắc (D-07H development)

Mọi lựa chọn thiết kế ở trên được chốt trên các unit calibration của D-07H development: 20 topology × 1 replicate × T ∈ {40, 80, 150} × 7 cell (none, extra/missing/reversed × 0.2/0.5), n_boot = 99. Ở các bảng có "in-sample", hệ số width được tune trên chính các run đó. Probe chỉ dùng D-07H development; **chưa chạy gì trên D-07** trước khi ghi quy tắc.

### 3.1 Tỷ lệ cổng mở ở mức 0.05 (20 run mỗi ô)

| T | Cell | Fit đủ lag (diagnose.py), Šidák | Fit đủ lag, bootstrap gộp hàng | Fit hạn chế, Šidák | Fit hạn chế, bootstrap shock độc lập |
|---|---|---|---|---|---|
| 40 | none | 0.05 | 0.00 | 0.00 | 0.00 |
| 40 | missing 0.2 | 0.10 | 0.05 | **0.70** | 0.65 |
| 40 | missing 0.5 | 0.20 | 0.05 | **0.90** | 0.85 |
| 80 | none | 0.00 | 0.00 | 0.05 | 0.05 |
| 80 | missing 0.2 | 0.70 | 0.30 | **0.95** | 0.95 |
| 80 | missing 0.5 | 1.00 | 0.20 | 1.00 | 1.00 |
| 150 | none | 0.00 | 0.00 | 0.00 | 0.00 |
| 150 | missing 0.2 | 1.00 | 0.40 | 1.00 | 1.00 |
| 150 | reversed 0.5 | 0.35 | 0.15 | 0.55 | 0.50 |

Ba điều rút ra từ bảng:

- **Bootstrap lấy lại nguyên hàng residual (như `simulate_from_fit`) gần như không có power.** Lý do là nó giữ nguyên tương quan giữa các structural residual, tức chính bằng chứng cần test, ngay trong dữ liệu null. Một parametric bootstrap hợp lệ cho null "skeleton đúng" phải lấy lại residual của từng phương trình **độc lập** với nhau.
- **Test trong fit hạn chế mạnh hơn rõ rệt so với fit đủ lag**, nhất là ở T = 40 (0.70 so với 0.10 ở missing 0.2). Báo động giả trên skeleton đúng vẫn ≤ 0.05.
- Šidák giải tích cho kết quả gần như bootstrap shock độc lập (bản sau dùng 99 bootstrap mỗi run). Vì vậy bản 3 dùng Šidák giải tích: rẻ hơn và cho kết quả tất định.

### 3.2 Mở lag có nhắm mục tiêu hay mở toàn bộ, sau khi cổng mở (in-sample, coverage / IS)

Bản probe đầu dùng fit đủ lag với ngưỡng 0.05. Hai cách so sánh:

- **targeted:** chỉ mở lag cho K cặp có p nhỏ nhất, K = max(BH, Storey);
- **all:** mở toàn bộ lag.

| T | Cell | v4 (khai báo đúng) | targeted | all |
|---|---|---|---|---|
| 80 | missing 0.2 | 0.968 / 3.19 | 0.920 / 9.29 | 0.915 / 5.18 |
| 80 | missing 0.5 | 0.959 / 3.28 | 0.926 / 10.85 | 0.950 / 3.30 |
| 150 | missing 0.5 | 0.959 / 2.19 | 0.950 / 3.36 | 0.973 / 2.25 |

Mở có nhắm mục tiêu bỏ sót những cạnh quá yếu để bị gắn cờ, nên các effect đi qua chúng bị lệch. Một khi cổng đã mở (có bằng chứng thật về cạnh thiếu), mở toàn bộ lag lại rẻ. Như vậy, cái đắt trong B1 bản 1–2 là **báo động giả**, không phải bản thân việc mở lag. Bản 3 giữ phần "nhắm mục tiêu" cho việc sửa cạnh cùng kỳ (BH, có ngân sách) và để cổng quyết định có mở lag hay không.

### 3.3 Chọn ngưỡng cổng và xác suất lật (fit hạn chế, in-sample, coverage / IS)

| T | Cell | v4 | α 0.05, lật 0 | α 0.10, lật 0 | α 0.10, lật 0.1 | **α 0.10, lật 0.2** |
|---|---|---|---|---|---|---|
| 40 | none | 0.957 / 4.21 | 0.979 / 4.73 | 0.968 / 4.61 | 0.969 / 4.53 | 0.971 / 4.59 |
| 40 | missing 0.5 | 0.971 / 7.54 | 0.918 / 9.71 | 0.976 / 8.20 | 0.979 / 8.35 | 0.978 / 8.32 |
| 80 | none | 0.954 / 2.22 | 0.971 / 2.41 | 0.971 / 2.41 | 0.971 / 2.42 | 0.968 / 2.36 |
| 80 | reversed 0.5 | 0.944 / 2.60 | 0.897 / 3.31 | 0.901 / 3.27 | 0.928 / 3.00 | 0.940 / 2.82 |
| 80 | ges | 0.956 / 3.38 | 0.944 / 3.23 | 0.944 / 3.23 | 0.944 / 3.40 | 0.950 / 3.36 |
| 150 | none | 0.957 / 1.67 | 0.978 / 1.79 | 0.978 / 1.79 | 0.974 / 1.76 | 0.968 / 1.82 |
| 150 | reversed 0.5 | 0.954 / 1.90 | 0.877 / 3.11 | 0.877 / 3.13 | 0.894 / 2.51 | 0.923 / 2.35 |
| 150 | ges | 0.940 / 2.64 | 0.933 / 2.73 | 0.933 / 2.73 | 0.926 / 2.67 | 0.940 / 2.54 |

- Không có dự phòng đảo chiều thì cell reversed 0.5 ở T = 150 chỉ đạt 0.877.
- Với α = 0.10 và lật 0.2, tỷ lệ IS so với v4 ở cell không hỏng là 1.09 / 1.07 / 1.09 (T = 40 / 80 / 150). Ở cell GES, tỷ lệ này là 1.06 / 0.99 / 0.96.
- Đây là số in-sample trên bank calibration, có lạc quan. Kết luận thật phải chờ D-07.

Tổng cộng đã so sánh bảy biến thể trên probe: hai kiểu test, ba cách calibration cổng, targeted / all, α ∈ {0.05, 0.10, 0.20}, lật ∈ {0, 0.1, 0.2}. Biến thể được chọn là **fit hạn chế, Šidák giải tích, α = 0.10, mở toàn bộ lag khi cổng mở, lật 0.2.**

### 3.4 Bảng width (calibrate_gate.py, D-07H development, n_boot 199, 420 run)

| T | closed | open | nogate (ablation) |
|---|---|---|---|
| 40 | 1.5 | 1.0 | 1.0 |
| 80 | 1.3 | 1.2 | 1.2 |
| 150 | 1.3 | 1.3 | 1.2 |

Tỷ lệ cổng mở trên bank calibration ở cell none là 2/20 (T = 40) và 1/20 (T = 80). Chi tiết ở `experiments/ext/gate/width_table_detail.json`.

## 4. Quy tắc ghi trước (viết trước khi chạy `ext_gate_auto3`)

**Đánh giá.** D-07 development, seed của `a2_baselines` / `b1v2_auto` (seed_base 20261102), nên các row ghép cặp được với các run đó.
- Lưới: T ∈ {40, 80, 150}; các cell none, {extra, missing, reversed} × {0.2, 0.5}, và cell GES (`learned`).
- 20 topology × 3 replicate, n_boot = 199.
- Method: `plugin`, `tolerant_v4` (đọc mức hỏng khai báo), `tolerant_auto3`, `tolerant_auto3_nogate` (ablation).
- `paired_references`: `plugin`, `tolerant_v4`. Calibration của v4 vẫn là khối calibration của `a3_ges` (D-07H development).

**Quy tắc.** Là ba điều kiện của mục B1 trong decision_rules.md, giữ nguyên không đổi. `tolerant_auto3` được **giữ lại** nếu cả ba cùng đúng:
1. Coverage ≥ 0.90 ở mọi cell missing và reversed tại T = 80 và T = 150.
2. Ở cell không hỏng, interval score không quá 1.35 lần của `tolerant_v4`, tại mọi T. Điều kiện này chặn chi phí của báo động giả.
3. Ở cell GES tại T = 80 và 150: coverage ≥ 0.90 và interval score không quá 1.10 lần của `tolerant_v4`. Ở đó `tolerant_v4` đọc trung bình lỗi GES trên bank calibration.

**Cách đọc, chốt trước:**
- Điều kiện 2 áp dụng ở **cả ba** T = 40, 80, 150 (cách đọc chặt của "tại mọi T"). Ngoài ra ghi riêng kết quả nếu chỉ xét T = 80 và 150.
- Các phần khác của T = 40 chỉ báo cáo, không chấm.
- Coverage là coverage gộp (cột `cov` của summary). Interval score là cột `IS`.
- Báo cáo kèm: tỷ lệ cổng mở theo cell, số so với v4 và `plugin` (chênh lệch ghép cặp), và ablation `nogate` (không chấm).

**Rủi ro đã biết, ghi trước:**
- Biến ẩn làm structural residual tương quan nên có thể mở cổng (kịch bản này không thuộc lưới hiện tại).
- Cạnh thiếu quá yếu để phát hiện ở T = 40 sẽ làm lệch các run có cổng đóng. Hệ số closed ở T = 40 (1.5) đã gánh phần này.
- Kết quả phụ thuộc lag_max đúng: lag thật vượt lag_max sẽ làm test lag mở cổng.

## 5. Kết quả

*(Ghi sau khi chạy, bên dưới dòng này.)*

## Kết quả của `ext_gate_auto3` (D-07 development, chạy một lần sau khi ghi quy tắc)

Lần chạy mất 1027.6 s với `--workers 3`, có 5760 row. Thời gian vượt mức khoảng 15 phút vì máy đang chạy cùng lúc vài agent khác (load average khoảng 42 trên 12 core). Lưới **không** bị thu nhỏ. Các row `plugin` trùng khớp từng row với `a2_baselines` (1260/1260), nên ghép cặp được. Muốn chấm lại thì chạy `python experiments/ext/gate/check_gate.py results/ext_gate_auto3`.

**Kết luận: GIỮ LẠI (RETAINED).** Cả ba điều kiện đều đạt, kể cả theo cách đọc chặt (điều kiện 2 xét ở cả T = 40).

**Điều kiện 1 (coverage ≥ 0.90): đạt.**

| T | missing 0.2 | missing 0.5 | reversed 0.2 | reversed 0.5 |
|---|---|---|---|---|
| 80 | 0.951 | 0.949 | 0.932 | **0.903** |
| 150 | 0.980 | 0.980 | 0.971 | 0.966 |

Ô sát ngưỡng nhất là reversed 0.5 ở T = 80 (0.903).

**Điều kiện 2 (IS ở cell không hỏng ≤ 1.35 × v4): đạt ở cả ba T.**

| T | `tolerant_auto3` | `tolerant_v4` | Tỷ lệ | B1 bản 2 (để so) |
|---|---|---|---|---|
| 40 | 4.935 | 4.391 | 1.124 | 1.48 |
| 80 | 2.680 | 2.502 | 1.071 | 1.28 |
| 150 | 1.868 | 1.564 | 1.195 | 1.59 |

**Điều kiện 3 (cell GES): đạt.**

| T | Coverage | IS | Ngưỡng (1.10 × v4) | v4 |
|---|---|---|---|---|
| 80 | 0.941 | 3.545 | 4.082 | 3.711 |
| 150 | 0.955 | 2.534 | 2.880 | 2.619 |

Ở T = 80, module tự chẩn đoán còn **tốt hơn** v4 có khai báo: chênh lệch ghép cặp −0.17 [−0.31, −0.03]. Ở T = 150 thì hòa: −0.08 [−0.29, +0.10].

### Cổng hoạt động thế nào (tỷ lệ cổng mở, 60 run mỗi ô)

| T | none | extra 0.2 / 0.5 | missing 0.2 / 0.5 | reversed 0.2 / 0.5 | GES |
|---|---|---|---|---|---|
| 40 | 0.10 | 0.07 / 0.05 | 0.62 / 0.97 | 0.12 / 0.13 | 0.88 |
| 80 | 0.08 | 0.10 / 0.08 | 0.98 / 1.00 | 0.12 / 0.23 | 1.00 |
| 150 | 0.05 | 0.07 / 0.07 | 1.00 / 1.00 | 0.32 / 0.55 | 1.00 |

- Báo động giả trên skeleton đúng là 5–10%, đúng như ngưỡng α = 0.10 đã chọn.
- Cạnh thiếu được phát hiện gần như chắc chắn từ T = 80.
- Ở T = 40, missing 0.2 chỉ mở cổng 62% số run. Đó là lý do coverage ở ô này còn 0.911 so với 0.983 của v4.

### So với `tolerant_v4` (v4 được biết mức hỏng thật)

`tolerant_auto3` hơi kém v4 ở đa số cell, vì v4 có thông tin khai báo đúng mà auto3 không có. Chênh lệch IS ghép cặp (auto3 − v4):

- T = 80: từ +0.03 (missing 0.5) đến +0.48 (reversed 0.5);
- T = 150: từ +0.18 đến +0.31;
- T = 40: lớn hơn ở missing 0.5 (+1.44) và GES (+1.75).

Như vậy, cái giá của việc **bỏ hẳn bước khai báo** là khoảng 0–20% IS ở T ≥ 80.

### So với baseline đã công bố (cũng không đọc khai báo, nên so sánh công bằng)

Seed giống `a2_baselines` và `a2b_pselect`. Script: `experiments/ext/gate/vs_baselines.py`. Mỗi ô ghi chênh lệch IS (auto3 − baseline), kèm 95% CI theo topology.

| T | Cell | auto3 cov / IS | vs `ida_union` | vs `bvar_minnesota` | vs `pselect_union` |
|---|---|---|---|---|---|
| 40 | missing 0.2 | 0.911 / 8.56 | −1.79 [−2.55, −1.07] | −1.61 [−2.61, −0.64] | **+1.60 [+0.79, +2.45]** |
| 40 | missing 0.5 | 0.954 / 8.97 | −17.95 | −6.01 | **+2.34 [+1.41, +3.41]** |
| 80 | missing 0.2 | 0.951 / 3.48 | −7.14 | −5.13 | −0.26 [−0.49, +0.00] |
| 80 | missing 0.5 | 0.949 / 3.40 | −24.48 | −9.99 | −1.06 [−1.36, −0.78] |
| 80 | reversed 0.2 | 0.932 / 2.87 | −0.05 [−0.37, +0.18] | −1.67 | −0.75 |
| 80 | reversed 0.5 | 0.903 / 3.44 | −0.88 [−1.41, −0.40] | −3.15 | −0.80 |
| 150 | missing 0.2 | 0.980 / 2.34 | −8.38 | −3.57 | +0.03 [−0.15, +0.19] |
| 150 | missing 0.5 | 0.980 / 2.40 | −25.94 | −7.78 | −0.71 [−1.02, −0.40] |
| 150 | reversed 0.2 | 0.971 / 2.11 | −0.14 [−0.73, +0.21] | −0.92 | −0.44 |
| 150 | reversed 0.5 | 0.966 / 2.33 | −1.37 | −2.76 | −1.17 |
| 150 | extra 0.2 / 0.5 | 0.98 / 1.87–1.89 | **+0.12 / +0.16** (thua) | hòa | −0.12 / −0.18 |

- Ở T ≥ 80, auto3 thắng hoặc hòa cả ba baseline trong mọi cell missing và reversed. Có hai ô hòa với `pselect_union` (missing 0.2 ở T = 80 và T = 150) và hai ô hòa với `ida_union` (reversed 0.2).
- Ở T = 40, auto3 vẫn thua `pselect_union` trong các cell thiếu cạnh, giống v4.
- Ở T = 150, auto3 thua `ida_union` chút ít trong các cell extra. Đây là cái giá của phần dự phòng đảo chiều.

### Ablation: bỏ cổng (`tolerant_auto3_nogate`, không chấm)

| T | none: auto3 / nogate | missing 0.5: auto3 / nogate | GES: auto3 / nogate |
|---|---|---|---|
| 40 | 4.93 / 8.30 | 8.97 / 8.23 | 10.22 / 8.55 |
| 80 | 2.68 / 3.29 | 3.40 / 3.41 | 3.55 / 3.56 |
| 150 | 1.87 / 2.18 | 2.40 / 2.30 | 2.53 / 2.56 |

Cổng là thành phần làm nên kết quả: bỏ cổng thì IS ở cell không hỏng tăng 1.17–1.68 lần. Ngược lại, ở T = 40 cổng bỏ sót một phần cạnh thiếu, nên trong cell missing và GES bản không cổng lại tốt hơn.

### Hạn chế, nói thẳng

- Thiết kế (fit hạn chế, α = 0.10, lật 0.2, mở toàn bộ lag) được chọn trên probe D-07H development. D-07 development cũng đã được dùng cho mọi phiên bản trước. Đây **không phải** kiểm định xác nhận: một kiểm định xác nhận cần bank mới, vì mọi split confirmatory đã dùng hết.
- Width được tune bằng script riêng theo trạng thái cổng, không qua `calibrate_methods`. Đây là điểm lệch so với quy tắc chung số 4; lý do ghi ở mục 2.
- T = 40 vẫn yếu: coverage GES 0.918, IS 10.22 so với 8.42 của v4; vẫn thua `pselect_union` trong cell thiếu cạnh.
- Ở T = 150, tỷ lệ IS ở cell không hỏng là 1.195, chủ yếu do phần dự phòng đảo chiều (width 1.654 so với 1.277 của v4).
- Chưa thử với biến ẩn hoặc nhiễu đo. Biến ẩn có thể mở cổng, và khi đó module rơi về nhánh v4 thiếu cạnh: tốn hơn nhưng vẫn giữ được coverage.
- Seed của method ngoài (tag 100 + chỉ số trong danh sách mọi method `ext_*` đã sắp xếp) thay đổi khi agent khác thêm module. Kết quả có thể tái lập, nhưng chỉ với đúng tập file `ext_*` có mặt lúc chạy.

## Sửa sau kiểm chứng vòng 1

*Append trong vòng 2 (hướng `auto5`, docs/ext/auto5.md), theo mục R2-10 của docs/ext/synthesis_round1.md. Phần trên giữ nguyên; các câu dưới đây thay thế câu tương ứng. Số liệu: `results/ext_auto5_gate_corrections/gate_corrections.md` (script `experiments/ext/auto5/gate_corrections.py`, chỉ đọc row đã lưu) và `results/ext_auto5_fair/rule_check.md`.*

1. **"Mọi báo động giả đều làm module mở toàn bộ lag" (mục 1) và hàm ý "B1 bản 1–2 mở all-lag gần như mọi run":** sai về mức độ. Trên skeleton đúng, B1 bản 1 mở all-lag ở 48.3% / 65.0% / 73.3% số run (T = 40/80/150), bản 2 ở 48.3% / 51.7% / 53.3%, tức **48–73%**. Cổng của auto3 hạ tỷ lệ này xuống 10.0% / 8.3% / 5.0%, tức giảm khoảng 5–10 lần, không phải từ ~100%.
2. **"Cổng là thành phần làm nên kết quả" (ablation) chỉ đúng trên skeleton không thiếu cạnh.** Ở cell thiếu cạnh, bản bỏ cổng tốt hơn hoặc ngang: T150 missing-0.2 2.34 so với 2.22 (auto3 − nogate +0.11 [+0.08, +0.14]), missing-0.5 2.40 so với 2.30 (+0.10 [+0.05, +0.13]); T40 missing +0.17 [−0.52, +0.92] và +0.60 [−0.16, +1.62]; T40 GES +1.63 [+0.47, +2.99]. Ở T150, nguyên nhân là hệ số width open|150 = 1.3 so với nogate|150 = 1.2. (Bảng ablation ở trên chỉ in cell missing-0.5; cell missing-0.2 ở T150 chưa được công bố ở vòng 1.)
3. **Claim so với baseline phải thu hẹp.** Tiêu đề "So với baseline đã công bố (cũng không đọc khai báo, nên so sánh công bằng)" là sai: auto3 được calibrate width trên D-07H còn baseline thì không. R2-3b (docs/ext/auto5.md mục 2 và 6) calibrate baseline theo T, gộp mọi cell, không đọc stated kind. Kết quả: quy tắc "thắng mỗi baseline ở cả 8 cell missing/reversed tại T ≥ 80" **không đạt**, vì hòa `pselect_union_calT` ở missing-0.2 tại T80 (−0.24 [−0.48, +0.06]) và T150 (−0.02 [−0.17, +0.13]); thắng 8/8 với plugin/ida_union/bvar_minnesota đã calibrate. Trên skeleton đúng, auto3 **thua** `ida_union` thô ở mọi T (+0.69 [+0.40, +1.01], +0.12 [+0.03, +0.22], +0.14 [+0.07, +0.21]) và thua `plugin` thô ở T150 (+0.29 [+0.17, +0.42]); thắng các bản `_calT` ở cell none chỉ vì một hệ số chung theo T làm baseline over-cover (coverage 1.000). Câu đúng: "Ở T ≥ 80, trên cell thiếu và đảo cạnh, auto3 thắng hoặc hòa mọi baseline, kể cả khi baseline được calibrate theo T; trên skeleton đúng, auto3 tốn hơn ida_union và (ở T150) plugin."
4. **Over-coverage ở T150** (0.985 ở cell none) đến chủ yếu từ hệ số closed|150 = 1.3 của `calibrate_gate.py`; probe vòng 2 trên cùng bank D-07H (seed bootstrap khác) cho 1.2 (docs/ext/auto5.md mục 3.2). Tức là hệ số chọn từ lưới bước 0.1 nhạy với seed bootstrap ở mức ±0.1.
5. **Probe script của mục 3.1–3.3** đã được tìm lại và chép vào `experiments/ext/gate_probes/` (danh sách ở docs/ext/auto5.md mục 0). Chúng dùng đường dẫn tuyệt đối tới scratchpad cũ (`SP=...`).
6. **Độ bền (mới, R2-3a):** auto3 giữ coverage ≥ 0.90 ở cell missing-0.2 và reversed-0.2 tại T80 và T150 dưới một biến ẩn (0.937–0.977, 4/4 cell, cả sau Holm), ở latent3 6/6 cell, ở nhiễu đo 10% 5/6 cell (trượt T80 reversed-0.2, 0.883). Rủi ro "biến ẩn mở cổng" là thật: cổng mở ở cell none 25–47% (latent1) và 55–82% (latent3), nhưng coverage được giữ (docs/ext/auto5.md mục 4).
7. Seed bootstrap của auto3 ở vòng 1 là `rng(100 + vị trí)`; từ vòng 2 runner dùng seed theo tên method, nên row auto3 vòng 1 chỉ tái lập được với đúng tập file `ext_*` lúc chạy. Row clean của `ext_auto5_a1` (seed mới) cho số rất gần: T80 none 0.951 / 2.64 so với 0.947 / 2.68; T150 none 0.983 / 1.87 so với 0.985 / 1.87.
