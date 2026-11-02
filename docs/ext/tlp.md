# Baseline Targeted Local Projections (`targeted_lp`), ID `tlp`

**Trạng thái.** Baseline đã công bố, mô tả (descriptive). Code: [src/paper4/ext_tlp.py](../../src/paper4/ext_tlp.py). Config đánh giá: [experiments/configs/ext_tlp_eval.json](../../experiments/configs/ext_tlp_eval.json). Probe thăm dò: [experiments/configs/ext_tlp_probe_db.json](../../experiments/configs/ext_tlp_probe_db.json). Không sửa file nào có sẵn; `tolerant_v4` vẫn đóng băng.

## 1. Phương pháp gốc (Nemtyrev & Boldea, arXiv 2603.00248, v2 tháng 6/2026)

Đọc từ bản HTML v2 trên arXiv.

- **LP:** β^LP_h là hệ số của y_{j,t} khi hồi quy y_{i,t+h} lên shock variable y_{j,t} và p lag của mọi biến (eq. 3; simulation dùng p = 10).
- **Target:** β^VAR_h = J_i' Â^h Γ̂ J_j, impulse response của một VAR với q < p lag, cùng recursive identification (simulation dùng q ∈ {1, 8}; bài nhấn mạnh "phải đủ lag trong target VAR").
- **TLP:** ridge co LP về target, `β^TLP_h = v_h β^LP_h + (1 − v_h) β^VAR_h`. Weight tối ưu MSE (Theorem 4, eq. 20):

  `v_h = max[1 − (Σ^LP_h − Σ^COV_h) / (T (β^LP_h − β^VAR_h)²), 0]`, một số vô hướng cho mỗi horizon.
- **Suy luận: mean symmetric double bootstrap (MSDB).**
  - Tầng 1: moving-block residual bootstrap của reduced-form VAR, block dài T^{1/3}.
  - Tầng 2: lặp lại thủ tục trên từng mẫu tầng 1 (simulation: B1 = 200, B2 = 100).
  - Σ^LP, Σ^COV là moment của tầng 2, lấy trung bình qua b1 (eqs. 23–24). Phần bias của weight được ước lượng lại trong mỗi mẫu tầng 1.
  - Interval: `β̂^TLP ± q_{1−α}(|t_b|) √Σ̂^TLP`, với `t_b = (β̂_b − mean β̂_b) / √Σ̂_b` (eqs. 27–28). Bài nhắm coverage 90%.
- Bài không công bố code (không tìm thấy repository trong bản HTML).

## 2. Chuyển thể sang Paper 4

- **Target = plug-in SVAR trên skeleton được cung cấp** (`parent_terms`, lag 1..lag_max, B0 theo skeleton), tức là đúng `plugin`. Khi skeleton hỏng, các ràng buộc 0 của nó chính là "local misspecification" mà TLP được thiết kế để chống.
- **Shock và identification theo skeleton, giống `lp_allpast`:** LP cho shock vào i kiểm soát các cha cùng kỳ của i trong skeleton. Cả hai estimator cho response với **unit structural shock** (Γ có đường chéo bằng 1), nên khi skeleton đúng chúng ước lượng cùng một đại lượng.
- **Estimand:** C(H) = Σ_{h=0..H} β^TLP_h. Weight tính riêng theo từng (h, cặp có thứ tự) như trong bài, rồi cộng lại. `theta` trả về là β^TLP_h, nên có cả lag error.
- Không đọc mức hỏng khai báo; không dùng edge score của Paper 3; không thấy truth.

### Các chỗ lệch so với bài gốc (ghi chính xác)

| # | Bài gốc | Ở đây | Lý do |
|---|---|---|---|
| D1 | Double bootstrap B1 = 200, B2 = 100 | `targeted_lp`: **single-level bootstrap**, B = n_boot = 199. Σ^LP, Σ^COV là moment của chính các mẫu tầng 1. Phần bias của weight vẫn được ước lượng lại trong mỗi mẫu (variance giữ cố định, đúng như bài làm với variance trung bình). Interval là `Ĉ ± q_{0.95}(|C_b − mean C_b|)`: đây là MSDB khi Σ̂_b được thay bằng một hằng số, lúc đó việc studentize triệt tiêu | Double bootstrap tốn khoảng 15 s/lần gọi ở T = 80 (B2 = 49), gấp khoảng 50 lần. Cả grid cần khoảng 5 giờ CPU. Bản double (`targeted_lp_db`, B1 = 199, B2 = 49) chỉ chạy trong probe ở mục 4 |
| D2 | Coverage danh nghĩa 90% | 95% (α = 0.05), như mọi method của Paper 4 | So sánh cùng chuẩn |
| D3 | p = 10, q = 8 hoặc 4 (q < p) | q = lag_max = 2 (target là SVAR của skeleton). p = lag_max + 1 = 3 (lag augmentation, như `lp_allpast`), hạ xuống tới khi mọi shock còn ≥ 5 residual dof. **Ở T = 40, n = 14, điều này cho p = 1 < q**, trái với điều kiện q ≤ p của bài | Với p = 2 ở T = 40, LP chỉ còn 1–4 dof; trong sanity check trên D-07H (2 topology), width trung vị lên 8–11 so với khoảng 3 khi p = 1. Chọn biến thể khả thi mạnh nhất cho baseline |
| D4 | Bootstrap DGP: "reduced-form VAR", số lag không ghi rõ | VAR(lag_max) **không ràng buộc** (target bỏ các zero restriction của skeleton). Residual được rescale theo √(rows / dof). Nếu companion radius ≥ 0.98, lag k được nhân với s^k để radius = 0.98 (intercept giữ mean gốc) | Nếu bootstrap từ SVAR của skeleton thì bootstrap tin rằng target không bias. VAR nhiều tham số ở T = 40 đôi khi không dừng |
| D5 | v_h chỉ chặn dưới ở 0 | Chặn thêm trên ở 1; v_h = 0 khi β^LP = β^VAR. Variance trong eq. 20 dùng variance mẫu hữu hạn của bootstrap, nên số hạng bias là (β^LP − β^VAR)² không nhân T. Hai cách tương đương: T·Var ≈ Σ | Bài không xử lý tử số âm |
| D6 | Mẫu LP theo từng horizon: không ghi rõ | Mẫu chung t = p..T−H−1 cho mọi h (như `lp_allpast`) | Đơn giản, nhanh (Frisch–Waugh) |
| D7 | Bản double: Σ^TLP_b1 là variance tầng 2 của TLP | Trong tầng 2, weight của TLP dùng moment của chính mẫu b1 đó (moment trung bình qua b1 chưa có khi đang ở trong vòng lặp) | Tránh lưu toàn bộ mẫu tầng 2 |

Ngoài ra có **`targeted_lp_cal`**: cùng estimator, được nới width theo (T, loại hỏng khai báo) trên bank calibration, đúng cách `tolerant_v4` được nới (`calibrate_methods`). Biến thể này **không phải** phương pháp đã công bố. Nó chỉ trả lời câu hỏi: nếu baseline được hiệu chỉnh width giống module thì sao. Nó dùng chung kết quả tính của `targeted_lp` trên cùng (data, skeleton), qua cache.

### Sanity check đã chạy trước khi ghi quy tắc (D-07H development, không phải bank đánh giá)

Script: [experiments/ext/tlp/sanity.py](../../experiments/ext/tlp/sanity.py), 2 topology D-07H.

- T = 2000, skeleton đúng: max |LP − truth| = 0.150 và 0.119; max |SVAR − truth| = 0.077 và 0.079. Cả hai estimator đều hội tụ về truth.
- T = 2000, thiếu 50%: LP lệch tới 0.41–0.43, SVAR lệch tới 0.75–0.79. LP cũng bị lệch khi thiếu cha cùng kỳ, vì shock bị nhận dạng sai.
- Thời gian: 0.2–0.4 s mỗi lần gọi (n_boot 199).
- Weight trung bình lên LP (h ≥ 1): 0.11–0.16 khi skeleton đúng, 0.15–0.22 khi thiếu 50%.

## 3. Quy tắc ghi trước (trước khi chạy `ext_tlp_eval`)

Ghi ngày 2026-11-02, trước khi chạy config đánh giá. Đây là quy tắc mô tả, không quyết định giữ hay loại method nào.

**Dữ liệu:** `results/ext_tlp_eval/` (D-07 development, seed_base 20261102, 20 topology × 3 replicate, T ∈ {40, 80, 150}; none, extra/missing/reversed × 0.2/0.5; n_boot 199). Calibration của `tolerant_v4` và `targeted_lp_cal` trên D-07H development.

**Quy tắc chính (R1).** Trong mỗi cell bị hỏng (18 cell = 3 T × 3 loại × 2 tỷ lệ), `tolerant_v4` **thắng `targeted_lp`** nếu đồng thời:
1. coverage gộp (pooled) của `tolerant_v4` trên các cặp non-null ≥ 0.90;
2. cận trên của CI 95% (bootstrap theo topology, như `paired_table`) cho hiệu interval score trung bình (`tolerant_v4` − `targeted_lp`) < 0.

Báo cáo: số cell thắng trên 18, tách theo loại hỏng và theo T.

**Báo cáo kèm, cùng định nghĩa:**
- R1-rev: số cell `targeted_lp` thắng `tolerant_v4` (coverage của `targeted_lp` ≥ 0.90 và cận dưới của CI cho hiệu v4 − TLP > 0). Các cell còn lại là hòa.
- R2: như R1 nhưng so với `targeted_lp_cal`.
- R3: cell không hỏng (3 cell, T = 40/80/150): coverage và interval score của cả hai, không có ngưỡng.
- Mô tả: TLP có tốt hơn hai thành phần của nó không? Interval score so với `plugin` (paired table) và với `lp_allpast` (T ≥ 80, tính bằng [experiments/ext/tlp/score.py](../../experiments/ext/tlp/score.py)). Weight trung bình v lên LP theo cell (`info_v_mean`).

**Dự đoán ghi trước (không phải quy tắc).** `tolerant_v4` thắng phần lớn cell thiếu cạnh ở T ≥ 80, vì target của TLP thiếu lag và LP thừa hưởng shock bị nhận dạng sai khi thiếu cha cùng kỳ. Ở cell thừa cạnh, các method gần hòa. Ở T = 40, TLP có thể có interval score thấp hơn module, vì module rộng ở cell thiếu cạnh.

## 4. Probe double bootstrap (thăm dò, D-07H development)

Config `ext_tlp_probe_db`: 6 topology D-07H, 1 replicate, T ∈ {80, 150}, các cell none / missing 0.5 / reversed 0.5, `targeted_lp` so với `targeted_lp_db`. Mục đích: xem simplification D1 có làm thay đổi coverage và width không. Không có quy tắc; chỉ báo cáo số.

## 5. Kết quả (ghi sau khi chạy, quy tắc ở mục 3 không đổi)

**Lần chạy.**
- `results/ext_tlp_eval/` có 7560 dòng, chạy mất 990.2 s với `--workers 3`. Thời gian vượt mốc 15 phút một chút, vì máy đang chịu load 28–38 do các agent khác. Grid giữ nguyên, không cắt.
- Kết quả của quy tắc: `results/ext_tlp_eval/tlp_rules.md`, sinh bởi `experiments/ext/tlp/score.py`.
- **Kiểm tra tái lập:**
  - Hệ số calibration `mod|*` của `tolerant_v4` trùng hoàn toàn với `results/a2_baselines/calibration.json`.
  - Interval score từng run của `plugin`, `pselect_union` và `tolerant_v4` trùng 1260/1260 với `results/a2b_pselect/runs.jsonl`.
  - Vậy các dòng được ghép cặp đúng với a2.

### R1 (quy tắc chính): `tolerant_v4` thắng `targeted_lp` ở **13/18** cell bị hỏng; `targeted_lp` thắng **0**; hòa 5

Theo loại hỏng: extra 4/6, missing 4/6, reversed 5/6. Theo T: T = 40 được 1/6, T = 80 được 6/6, T = 150 được 6/6.

Mỗi ô ghi coverage / interval score; cột cuối là hiệu IS (v4 − TLP) với CI 95%.

| T | Hỏng | `tolerant_v4` | `targeted_lp` | v4 − TLP [CI 95%] | Kết luận |
|---|---|---|---|---|---|
| 40 | none | 0.935 / 4.39 | 0.889 / 4.72 | −0.33 [−0.73, +0.07] | (R3) |
| 40 | extra 0.2 | 0.912 / 4.72 | 0.886 / 4.84 | −0.11 [−0.61, +0.39] | hòa |
| 40 | extra 0.5 | 0.919 / 4.86 | 0.883 / 4.92 | −0.06 [−0.49, +0.35] | hòa |
| 40 | missing 0.2 | 0.983 / 7.77 | 0.864 / 5.15 | +2.61 [+1.91, +3.27] | hòa (TLP coverage < 0.90) |
| 40 | missing 0.5 | 0.978 / 7.53 | 0.826 / 5.88 | +1.65 [+0.97, +2.31] | hòa (TLP coverage < 0.90) |
| 40 | reversed 0.2 | 0.921 / 4.78 | 0.877 / 5.16 | −0.38 [−0.92, +0.22] | hòa |
| 40 | reversed 0.5 | 0.921 / 4.78 | 0.868 / 5.80 | −1.02 [−1.52, −0.41] | v4 thắng |
| 80 | none | 0.933 / 2.50 | 0.957 / 3.09 | −0.59 [−0.88, −0.28] | (R3) |
| 80 | extra 0.2 | 0.946 / 2.53 | 0.957 / 3.14 | −0.61 [−0.91, −0.31] | v4 thắng |
| 80 | extra 0.5 | 0.948 / 2.65 | 0.958 / 3.13 | −0.48 [−0.74, −0.23] | v4 thắng |
| 80 | missing 0.2 | 0.959 / 3.28 | 0.930 / 3.48 | −0.20 [−0.37, −0.01] | v4 thắng |
| 80 | missing 0.5 | 0.957 / 3.37 | 0.901 / 4.16 | −0.79 [−1.02, −0.54] | v4 thắng |
| 80 | reversed 0.2 | 0.948 / 2.79 | 0.948 / 3.43 | −0.64 [−0.84, −0.40] | v4 thắng |
| 80 | reversed 0.5 | 0.929 / 2.97 | 0.937 / 3.85 | −0.88 [−1.15, −0.60] | v4 thắng |
| 150 | none | 0.964 / 1.56 | 0.959 / 1.86 | −0.30 [−0.44, −0.16] | (R3) |
| 150 | extra 0.2 | 0.965 / 1.58 | 0.955 / 1.90 | −0.32 [−0.46, −0.18] | v4 thắng |
| 150 | extra 0.5 | 0.967 / 1.66 | 0.954 / 1.95 | −0.29 [−0.40, −0.18] | v4 thắng |
| 150 | missing 0.2 | 0.968 / 2.06 | 0.930 / 2.28 | −0.22 [−0.38, −0.06] | v4 thắng |
| 150 | missing 0.5 | 0.962 / 2.22 | 0.905 / 2.66 | −0.44 [−0.64, −0.25] | v4 thắng |
| 150 | reversed 0.2 | 0.970 / 1.89 | 0.926 / 2.68 | −0.79 [−1.17, −0.50] | v4 thắng |
| 150 | reversed 0.5 | 0.959 / 2.02 | 0.866 / 3.77 | −1.75 [−2.29, −1.29] | v4 thắng |

**Dự đoán ghi trước so với kết quả:**
- Dự đoán "v4 thắng phần lớn cell thiếu cạnh ở T ≥ 80": **đúng**, 4/4.
- Dự đoán "cell thừa cạnh gần hòa": **sai** ở T ≥ 80. Ở đó v4 thắng 4/4 với khoảng cách −0.29 đến −0.61, vì interval của TLP (bootstrap từ VAR không ràng buộc) rộng hơn cần thiết khi skeleton chỉ thừa cạnh.
- Dự đoán "ở T = 40, TLP có IS thấp hơn ở cell thiếu cạnh": **đúng về IS**, nhưng coverage của TLP chỉ 0.83–0.86, nên theo R1-rev không tính là thắng.

### R2: so với `targeted_lp_cal` (TLP được nới width giống module): v4 thắng **13/18**, `targeted_lp_cal` thắng **2/18**

Hai cell `targeted_lp_cal` thắng đều là **thiếu cạnh ở T = 40**:

| T = 40 | `tolerant_v4` | `targeted_lp_cal` | v4 − TLP_cal [CI 95%] |
|---|---|---|---|
| missing 0.2 | 0.983 / 7.77 (width 6.60) | 0.953 / 4.75 (width 3.77) | +3.01 [+2.61, +3.43] |
| missing 0.5 | 0.978 / 7.53 (width 6.45) | 0.935 / 5.02 (width 3.71) | +2.51 [+2.13, +2.89] |

Hệ số nới của `targeted_lp_cal`, lấy từ `calibration.json`:

| T | none | extra | missing | reversed |
|---|---|---|---|---|
| 40 | 1.2 | 1.2 | 1.4 | 1.4 |
| 80 | 1.0 | 1.0 | 1.1 | 1.0 |
| 150 | 1.0 | 1.1 | 1.3 | 1.4 |

**Đây là phát hiện quan trọng nhất của hướng này.** Ở T = 40, khi thiếu cạnh, một baseline đã công bố, chỉ cần được hiệu chỉnh width như module, đã đạt coverage ≥ 0.90 với interval hẹp hơn v4 khoảng 40%. Nó cũng tốt hơn `pselect_union` ở cùng cell: 0.862 / 6.96 và 0.853 / 6.63. Nói cách khác, chỗ yếu đã biết của v4 (quá rộng ở T nhỏ khi thiếu cạnh) có một lời giải cụ thể: co về target theo MSE thay vì mở mọi lag. Lưu ý: `targeted_lp_cal` là chuyển thể của nhóm, không phải phương pháp đã công bố.

### R3: cell không hỏng

| T | `tolerant_v4` | `targeted_lp` | `targeted_lp_cal` |
|---|---|---|---|
| 40 | 0.935 / 4.39 | 0.889 / 4.72 | 0.939 / 4.50 |
| 80 | 0.933 / 2.50 | 0.957 / 3.09 | 0.957 / 3.09 |
| 150 | 0.964 / 1.56 | 0.959 / 1.86 | 0.959 / 1.86 |

### Mô tả: TLP so với hai thành phần của nó

| T | Hỏng | TLP − `plugin` | TLP − `lp_allpast` | v trung bình (h ≥ 1) |
|---|---|---|---|---|
| 80 | none | +0.31 [−0.11, +0.70] | −2.61 [−2.94, −2.23] | 0.102 |
| 80 | missing 0.5 | −24.62 [−26.03, −23.30] | −1.56 [−1.86, −1.29] | 0.126 |
| 150 | none | +0.28 [+0.10, +0.46] | −0.80 [−0.98, −0.63] | 0.127 |
| 150 | missing 0.5 | −26.42 [−27.89, −24.92] | −0.23 [−0.35, −0.10] | 0.188 |
| 150 | reversed 0.5 | −1.36 [−1.82, −0.90] | −0.97 [−1.26, −0.69] | 0.137 |

(Bảng đủ có trong `tlp_rules.md`.)

- TLP thắng `lp_allpast` ở mọi cell có T ≥ 80; `lp_allpast` không chạy được ở T = 40.
- TLP thắng `plugin` rất xa ở mọi cell thiếu cạnh.
- Ở cell không hỏng hoặc thừa cạnh, TLP tệ hơn `plugin` một chút: +0.24 đến +0.41 (có ý nghĩa ở T = 150).
- Weight lên LP nhỏ: v trung bình 0.10–0.19. Weight tăng theo mức thiếu cạnh và theo T, đúng như cơ chế của bài.
- **Cơ chế thất bại của TLP:**
  - Khi skeleton xóa mất một đường truyền, target cho đúng 0. Nếu variance của LP lớn hơn (LP − target)², weight MSE đặt v = 0 và TLP bằng 0 luôn. Số cặp non-null bị "lost" là 54/1854 ở T = 40 và 65/1854 ở T = 80 (thiếu 50%).
  - Ở cell đảo 50%, T = 150, coverage chỉ 0.866. LP kiểm soát sai cha cùng kỳ nên cũng bị lệch, tức là cả hai thành phần cùng sai.
- Ở T = 40, VAR không ràng buộc dùng làm bootstrap DGP phải bị co về radius 0.98 trong 231/420 run. Ở T ≥ 80 thì 0/840.

### Probe double bootstrap (D-07H development, 6 topology, thăm dò)

`results/ext_tlp_probe_db/`: 72 dòng, chạy 350.5 s. Mỗi ô ghi coverage / width / IS.

| T | Hỏng | `targeted_lp` (single, D1) | `targeted_lp_db` (MSDB, B2 = 49) | db − single [CI 95%] |
|---|---|---|---|---|
| 80 | none | 0.935 / 2.57 / 4.54 | 0.896 / 2.17 / 3.95 | −0.59 [−1.14, −0.18] |
| 80 | missing 0.5 | 0.886 / 2.82 / 5.80 | 0.791 / 2.28 / 6.91 | +1.11 [−0.69, +3.14] |
| 80 | reversed 0.5 | 0.891 / 2.79 / 6.09 | 0.851 / 2.14 / 6.75 | +0.66 [−0.05, +1.75] |
| 150 | none | 0.965 / 1.57 / 1.90 | 0.960 / 1.54 / 1.89 | −0.01 [−0.11, +0.06] |
| 150 | missing 0.5 | 0.910 / 1.65 / 2.57 | 0.876 / 1.52 / 2.82 | +0.25 [−0.02, +0.59] |
| 150 | reversed 0.5 | 0.856 / 1.69 / 4.43 | 0.811 / 1.60 / 4.69 | +0.25 [+0.04, +0.43] |

**Đọc kết quả:**
- Bản double bootstrap đúng theo bài cho interval **hẹp hơn** và coverage **thấp hơn** ở các cell bị hỏng: 0.79–0.88 so với 0.86–0.91. IS của nó tệ hơn hoặc ngang bản single.
- Vậy simplification D1 **không làm baseline yếu đi** ở cell hỏng. Nếu có ảnh hưởng thì bản single còn có lợi hơn.
- Ở cell không hỏng, T = 80, bản double tốt hơn: −0.59.
- Chỉ có 6 topology, nên đây là thăm dò, không phải bằng chứng.

### Kết luận được phép viết

> So với Targeted Local Projections (Nemtyrev & Boldea 2026), dùng plug-in SVAR trên skeleton làm target: module thắng 13/18 cell bị hỏng, gồm 12/12 cell ở T ≥ 80, và không thua cell nào. Ở T = 40, TLP gốc chỉ đạt coverage 0.83–0.89. Khi TLP được hiệu chỉnh width như module, nó thắng module ở hai cell thiếu cạnh, T = 40.

**Hệ quả cho Paper 4:** kết quả R2 là ứng viên trực tiếp cho hướng "thu hẹp interval ở T nhỏ" ([ket_qua_nhom_a.md](../ket_qua_nhom_a.md), việc nên làm số 2). Ví dụ: một module dùng TLP-style MSE shrinkage của bản mở mọi lag về `plugin` khi được khai báo thiếu cạnh. Nếu thử hướng này, phải là một version mới với quy tắc mới, ghi trước khi chạy.

## Sửa sau kiểm chứng vòng 1

Append theo R2-10 của [synthesis_round1.md](synthesis_round1.md). Nội dung các mục trên giữ nguyên; các câu dưới đây thay thế câu tương ứng khi trích dẫn.

1. **"TLP không thắng cell nào / module không thua cell nào" chỉ đúng nhờ cổng coverage ≥ 0.90.** Xét riêng interval score (proper scoring rule), `targeted_lp` có IS **thấp hơn** v4 có ý nghĩa ở T40 missing 0.2 (+2.61 [+1.91, +3.27]) và missing 0.5 (+1.65 [+0.97, +2.31]), với coverage chỉ 0.864 và 0.826. Câu kết luận ở mục 5 phải đọc là: "module thắng 13/18 cell bị hỏng, gồm 12/12 cell ở T ≥ 80; không thua cell nào **theo rule có cổng coverage**; theo IS thuần, TLP tốt hơn module ở hai cell thiếu cạnh T = 40 nhưng under-cover."
2. **Probe double bootstrap ở mục 4 không faithful.** Nó dùng B2 = 49 (bài: 100), p = 3 với mẫu LP chung (bài: p > q, ví dụ (10, 8) hoặc (8, 4), mẫu theo horizon) và mức 95% (bài: 90%). Câu "simplification D1 không làm baseline yếu đi" chưa được chứng minh: ở T80 none, bản double tốt hơn có ý nghĩa (−0.59 [−1.14, −0.18]), cỡ bằng biên thắng của v4 ở T80 none/extra. Câu đúng: "probe 6 topology không cho thấy bản double tốt hơn ở cell hỏng, nhưng ở T80 none bản double tốt hơn; câu hỏi baseline bị làm yếu được xử lý ở vòng 2 ([tlp2.md](tlp2.md))."
3. **`targeted_lp_cal` phụ thuộc cache module-level và thứ tự gọi.** Kết quả vòng 1 đúng vì runner gọi `targeted_lp` ngay trước `targeted_lp_cal` trên cùng (data, skeleton). Bản vòng 2 `tlp2_lp_cal` ([src/paper4/ext_tlp2.py](../../src/paper4/ext_tlp2.py)) tự tính mỗi lần gọi với seed theo nội dung input.
4. **"MSE shrinkage của all-lags fit về plugin là cách chữa"** (mục "Hệ quả cho Paper 4") mới là giả thuyết, chưa có thí nghiệm.
5. **Tái lập:** số của `targeted_lp` vòng 1 chỉ tái lập được với đúng bộ file ext_*.py lúc chạy (seed của ext method khi đó là vị trí trong danh sách; nay cố định theo tên).
