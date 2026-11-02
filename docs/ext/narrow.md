# Hướng "narrow": thu hẹp interval của module ở T nhỏ (module v5)

**Trạng thái.** Exploratory, D-07 development. Code: [ext_narrow.py](../../src/paper4/ext_narrow.py). Config: `experiments/configs/ext_narrow_eval.json` (đánh giá có quy tắc), `experiments/configs/ext_narrow_ablation.json` (ablation, mô tả). Probe: `experiments/ext/narrow/probe.py`, kết quả `experiments/ext/narrow/probe{1,2,3}.json`.

## Vấn đề

Ở T = 40, khi khai báo thiếu cạnh, `tolerant_v4` over-cover: coverage 0.98, width khoảng 6.5 so với 3.5 của `pselect_union` (`results/a2b_pselect`). Interval score của v4 vì thế thua `pselect_union` (7.77 vs 6.96 ở missing-0.2; 7.53 vs 6.63 ở missing-0.5), dù `pselect_union` chỉ cover 0.85–0.86.

Hai nguyên nhân, đọc từ code và `results/a2b_pselect/calibration.json`:

1. **Mở mọi lag.** Khi khai báo thiếu cạnh, v3/v4 đưa lag 1..2 của cả 14 nút vào mọi phương trình: 28 regressor lag trên 38 dòng ở T = 40. Không mất số hạng nào, nhưng variance của mọi hệ số tăng vọt.
2. **Calibration chỉ nới, không thu.** Grid của width factor bắt đầu từ 1.0. Ở T = 40, factor của v4 cho missing là `mod|40|missing = 1.0`, tức đã chạm sàn. Interval over-cover mà calibration không thu hẹp được.

## Thiết kế v5

Hai thay đổi, tách riêng được để làm ablation.

**(a) Targeted opening, chọn lại trong mỗi bootstrap draw.** Thay vì mở mọi lag, chỉ mở lag block của những cặp ngoài skeleton có bằng chứng từ dữ liệu.
- **Bằng chứng** cho cặp không kề (u, v) được đo trong **phương trình cấu trúc** của skeleton: lag của chính nút, lag của các cặp kề, và parent cùng kỳ của skeleton. Không dùng reduced form, vì B1 đã chỉ ra Granger test trên reduced form không kiểm được adjacency.
  - F test của lag block của u thêm vào phương trình của v, và ngược lại. Tính theo Frisch–Waugh, quy về F(k, dof) bằng xấp xỉ Paulson.
  - Fisher z của tương quan giữa hai structural residual (dấu vết của cạnh cùng kỳ bị thiếu).
  - Gộp ba p-value bằng Šidák.
- **Số cặp mở:** K = max(⌈3 · k_khai báo⌉, #{p < 0.10}), chặn trên bởi số cặp ngoài skeleton. Mức hỏng khai báo đặt sàn cho số cặp mở; bằng chứng mạnh có thể mở thêm.
- Repair cạnh cùng kỳ giữ như v3: BH trên residual của fit này, tối đa k_khai báo cạnh, chiều bốc ngẫu nhiên mỗi draw.
- **Chọn lại mỗi draw:** mỗi bootstrap draw chạy lại toàn bộ bước chọn trên chuỗi bootstrap. Interval vì thế gộp bất định của bước chọn trên các skeleton khả dĩ quanh skeleton khai báo, đúng ý RQ4.2 của plan ("khoảng hiệu ứng trên các skeleton khả dĩ quanh skeleton đã chọn"). Point estimate là trung bình các draw (bagging).

**(b) Calibration hai chiều.** Interval được trả về đã nhân trước với `PRESCALE` = 0.5 quanh midpoint. Grid 1.0..10 (bước 0.1) của runner vì thế tương đương factor hiệu dụng 0.5..5 (bước 0.05): factor theo (T, loại hỏng khai báo) giờ có thể thu hẹp interval over-cover. Calibration vẫn chạy trên D-07H development, đúng như v4 (`calibrate_methods`).

Không khai báo thiếu cạnh → v5 chính là v3 (đã prescale). Ở cell không hỏng, thừa, đảo, v5 chỉ khác v4 ở grid calibration mịn hơn và ở bootstrap stream.

**Ablation:**
- `tolerant_v5_sel`: (a), nhưng chọn một lần trên dữ liệu, không chọn lại mỗi draw; cộng (b).
- `tolerant_v5_cal2`: chỉ (b), trên v3 (mở mọi lag).

## Probe trên bank calibration (D-07H development), trước khi ghi quy tắc

Probe chỉ dùng D-07H development (bank calibration), seed riêng (7 700 000 + chỉ số topology), 1 replicate, n_boot = 99. D-07 không bị chạm. Với mỗi biến thể, factor c* được chọn trên chính mẫu probe để coverage gộp hai rate missing đạt 0.95 (grid 0.5..5), giống việc calibration sẽ làm; số liệu vì thế lạc quan như nhau cho mọi biến thể. Ô ghi **coverage / IS** tại c*.

T = 40, 20 topology (`probe3.json`):

| Biến thể | c* | missing-0.2 | missing-0.5 | số cặp mở (0.2 / 0.5) |
|---|---|---|---|---|
| v3, mở mọi lag | 0.90 | 0.961 / 7.36 | 0.961 / 7.35 | tất cả |
| top 2k ∪ p<0.05, chọn một lần | 2.40 | 0.961 / 5.87 | 0.942 / 6.29 | 8.5 / 22.0 |
| top 2k ∪ p<0.05, chọn lại | 1.65 | 0.958 / 5.00 | 0.951 / 5.48 | 8.5 / 22.0 |
| **top 3k ∪ p<0.10, chọn lại** | 1.35 | 0.944 / 4.70 | 0.963 / 5.21 | 12.6 / 33.0 |
| top 2k ∪ p<0.20, chọn lại | 1.20 | 0.956 / 4.83 | 0.948 / 5.10 | 17.85 / 26.3 |

T = 80 và 150, 20 topology (`probe2.json`):

| Biến thể | T = 80: miss-0.2 | miss-0.5 | T = 150: miss-0.2 | miss-0.5 |
|---|---|---|---|---|
| v3, mở mọi lag | 0.958 / 3.05 | 0.951 / 3.16 | 0.949 / 2.05 | 0.954 / 2.22 |
| top 2k ∪ p<0.05, chọn lại | 0.963 / 2.91 | 0.949 / 3.18 | 0.971 / 1.85 | 0.944 / 2.25 |
| **top 3k ∪ p<0.10, chọn lại** | 0.954 / 2.87 | 0.949 / 3.13 | 0.963 / 1.86 | 0.944 / 2.19 |
| top 2k ∪ p<0.20, chọn lại | 0.963 / 2.80 | 0.946 / 3.21 | 0.966 / 1.88 | 0.953 / 2.25 |
| top 4k ∪ p<0.05, chọn lại | 0.946 / 2.81 | 0.956 / 3.27 | 0.968 / 1.82 | 0.932 / 2.27 |

Probe đầu tiên (10 topology, mọi T, `probe1.json`) cho cùng thứ tự; biến thể top k ∪ p<0.01 kém hơn (T = 40: 5.30 / 5.33).

**Đọc probe.**
- Ở T = 40, targeted opening giảm IS khoảng 30–35% so với v3 dù v3 đã được calibration hai chiều (c* = 0.90).
- Chọn lại mỗi draw tốt hơn rõ rệt so với chọn một lần (5.00 vs 5.87). Chọn một lần bỏ qua bất định của bước chọn, nên calibration phải nới mạnh (c* = 2.40).
- Ở T = 80 và 150, targeted opening ngang v3: tốt hơn ở missing-0.2, xấp xỉ ở missing-0.5.
- **Chọn top 3k ∪ p < 0.10** (mult = 3, alpha_open = 0.10). Biến thể này ngang top 2k ∪ p<0.20, nhưng gắn số cặp mở trực tiếp nhất với k khai báo. Lựa chọn được làm sau probe, trên bank calibration; kết quả D-07 development không dùng để chọn.

**Cảnh báo chi phí đã biết:** trong bootstrap draw, số cặp được mở lớn hơn trên dữ liệu gốc (ví dụ 19 vs 12 ở một topology, T = 40). DGP của bootstrap chứa các hệ số đã mở (khác 0 do nhiễu), nên bằng chứng cho các cặp này bị phóng đại. Hệ quả là interval bảo thủ hơn; calibration sẽ bù.

## Quy tắc ghi trước (trước khi chạy `ext_narrow_eval`)

**Lần chạy.** `ext_narrow_eval` trên D-07 development, seed_base 20261102 (cùng seed với `a2_baselines` và `a2b_pselect`). Grid: T ∈ {40, 80, 150}; cell none, {extra, missing, reversed} × {0.2, 0.5}; 20 topology × 3 replicate; n_boot = 199. Calibration trên D-07H development (khối calibration của `a3_ges`/`a2b_pselect`), width factor của `tolerant_v5` theo (T, loại hỏng khai báo), gộp các rate.

**Giảm grid để giữ thời gian chạy khoảng 15 phút (CPU dùng chung, 3 worker).** Lần chạy chỉ gồm `lp_allpast`, `tolerant_v4`, `tolerant_v5`. `plugin` và `pselect_union` **không chạy lại**: lấy từ `results/a2b_pselect/runs.jsonl`. Hai lần chạy dùng cùng seed và cùng calibration, nên dữ liệu, skeleton hỏng và các method cũ cho cùng kết quả. Điều kiện để ghép cặp: các dòng `tolerant_v4` của `ext_narrow_eval` phải **trùng khít** với `a2b_pselect`. Nếu không trùng, so sánh với `pselect_union` chỉ được báo là so sánh trung bình không ghép cặp. Phép ghép và CI (bootstrap theo topology, 1000 lần, như `paired_table` của runner) do `experiments/ext/narrow/paired.py` làm.

**`tolerant_v5` được GIỮ nếu cả ba điều kiện đều đúng:**

1. **T = 40, missing (2 cell):** trong mỗi cell missing-0.2 và missing-0.5, coverage của v5 ≥ 0.90, và CI 95% của hiệu IS ghép cặp (v5 − v4) có cận trên < 0.
2. **T = 80 và 150, mọi cell hỏng (12 cell, extra/missing/reversed × 0.2/0.5):** coverage của v5 ≥ 0.90, và IS trung bình của v5 ≤ 1.05 × IS trung bình của v4.
3. **Không thua ở chỗ khác (5 cell):** ở cell none tại mọi T, và ở extra/reversed tại T = 40, IS trung bình của v5 ≤ 1.05 × của v4. Điều kiện này được thêm so với gợi ý ban đầu: v5 thay calibration ở mọi cell, nên cần kiểm rằng grid mịn hơn không làm tệ đi chỗ nào.

Ngược lại, v5 bị **loại**.

**Báo cáo thêm (không ảnh hưởng quyết định):**
- **So với `pselect_union`** (luật A2b, đếm số cell): trong mỗi cell hỏng, v5 coverage ≥ 0.90 và cận trên CI của hiệu IS ghép cặp (v5 − `pselect_union`) < 0. Trọng tâm là hai cell missing ở T = 40, nơi v4 thua.
- Coverage, width, IS của `plugin`, `lp_allpast` từ cùng seed.
- Số cặp mở trung bình (`info_n_open`, `info_n_open_boot_mean`).
- **Ablation** (`ext_narrow_ablation`, cùng seed, mô tả): `tolerant_v5_sel` và `tolerant_v5_cal2` so với v4 và v5 trên các cell missing.

**Giới hạn đã biết trước.**
- Kết quả là development. Mọi split đã dùng một lần, nên một kiểm tra confirmatory của v5 cần bank mới.
- Biến thể v5 được chọn sau probe trên D-07H development. Đây cũng là bank calibration, nên width factor và lựa chọn thiết kế dùng chung một bank. D-07 vẫn chưa được nhìn.
- Stream bootstrap của method ext phụ thuộc vào thứ tự của mọi method ext có mặt trong repo lúc chạy (`rng(100 + e_idx)` trong runner). Vì thế lặp lại lần chạy không cho cùng số liệu từng bit nếu các agent khác thêm hoặc bớt module ext.

## Kết quả `ext_narrow_eval` (D-07 development, chạy một lần, 916 s)

Toàn bộ số liệu: `results/ext_narrow_eval/summary.md` (bảng của runner) và `results/ext_narrow_eval/ruling.md` (sinh bởi `experiments/ext/narrow/paired.py`, ghép với `a2b_pselect`).

**Kiểm tra ghép cặp: đạt.** 1260/1260 dòng `tolerant_v4` của `ext_narrow_eval` trùng khít với `a2b_pselect` (cả IS lẫn số cặp được phủ). So sánh với `plugin` và `pselect_union` vì thế là ghép cặp thật.

**Width factor tune được (D-07H development), đã quy về factor hiệu dụng (× 0.5):**

| T | missing | reversed | none | extra |
|---|---|---|---|---|
| 40 | 1.20 (v4: 1.0, chạm sàn) | 1.40 (v4: 1.4) | 1.40 (1.4) | 1.25 (1.3) |
| 80 | 1.25 (1.3) | 1.35 (1.4) | 1.25 (1.3) | 1.25 (1.3) |
| 150 | 1.25 (1.2) | 1.25 (1.3) | 1.15 (1.2) | 1.15 (1.2) |

### Phán quyết theo quy tắc: **`tolerant_v5` BỊ LOẠI**

- **Điều kiện 1 (T = 40, missing): ĐẠT, 2/2.**

  | Cell | v5 coverage | v5 IS | v4 IS | v5 − v4 (CI 95%) |
  |---|---|---|---|---|
  | missing-0.2 | 0.933 | 4.79 | 7.77 | −2.98 [−3.44, −2.46] |
  | missing-0.5 | 0.944 | 5.12 | 7.53 | −2.41 [−2.76, −2.05] |

- **Điều kiện 2 (T = 80/150, mọi cell hỏng): KHÔNG ĐẠT, 11/12.** Cell trượt là **missing-0.5 ở T = 150**: IS 2.335 so với 2.215 của v4, tỷ lệ **1.054**, vượt ngưỡng 1.05. Coverage 0.960. Hiệu ghép cặp +0.12 [−0.02, +0.27], CI chứa 0, nhưng quy tắc dùng tỷ lệ trung bình nên cell này vẫn trượt. Các cell còn lại có tỷ lệ 0.848–1.019, coverage 0.921–0.973.
- **Điều kiện 3 (không thua ở chỗ khác): ĐẠT, 7/7.** Tỷ lệ IS 0.987–0.998. Ghi chú: phần quy tắc ghi "5 cell" là **đếm sai lúc ghi**. Mô tả của điều kiện (none ở 3 giá trị T, cộng extra/reversed × 2 rate ở T = 40) cho 7 cell, và cả 7 đều được chấm.

Theo quy tắc, v5 bị loại. Không đổi quy tắc sau khi thấy kết quả.

### Những gì kết quả vẫn cho thấy (mô tả, không đổi phán quyết)

- **So với `pselect_union` (luật A2b): v5 đạt 18/18 cell hỏng.** v4 chỉ đạt 16/18, thua ở hai cell missing ở T = 40. Ở T = 40:

  | Cell | `pselect_union` (cov / IS / width) | v4 | **v5** | v5 − `pselect_union` |
  |---|---|---|---|---|
  | missing-0.2 | 0.862 / 6.96 / 3.58 | 0.983 / 7.77 / 6.60 | **0.933 / 4.79 / 3.37** | −2.17 [−2.74, −1.62] |
  | missing-0.5 | 0.853 / 6.63 / 3.50 | 0.978 / 7.53 / 6.45 | **0.944 / 5.12 / 4.08** | −1.51 [−1.93, −1.12] |

  v5 có coverage gần 0.95 với width ngang hoặc hẹp hơn `pselect_union`. Đây là chỗ hổng mà v4 để lại trong claim "beats published baselines on missing edges" (trước đây chỉ đúng với T ≥ 80).
- **T = 80, missing-0.2:** v5 cũng tốt hơn v4 rõ rệt: 2.78 vs 3.28, hiệu −0.50 [−0.66, −0.35].
- **Chi phí ở T = 150:** missing-0.5 nhích lên 5.4% so với v4. Ở T = 150, mở mọi lag đã rẻ (148 dòng cho khoảng 30 regressor), nên targeted opening không còn lợi. Probe trên D-07H trước đó cho thấy hai cách gần như ngang nhau ở cell này (2.19 vs 2.22).
- **Số cặp được mở:** trên dữ liệu gốc trung bình 13.0 (missing-0.2) và 33.2 (missing-0.5) ở T = 40. Trong bootstrap draw con số lớn hơn: 22.6 và 38.7. Tổng số cặp ngoài skeleton là 74 và 81.
- **Cell không thiếu cạnh:** v5 = v3 với grid calibration mịn hơn, và cho kết quả ngang v4 (tỷ lệ IS 0.987–1.019).

## Hai kiểm tra mô tả cho v5 đóng băng, ghi trước khi chạy `ext_narrow_ges` và `ext_narrow_structured`

v5 đã bị loại theo quy tắc. Code và tham số của nó vẫn giữ nguyên (mult = 3, alpha_open = 0.10, PRESCALE = 0.5) để đo hành vi ở hai loại hỏng mà v4 đã được kiểm. Cả hai kiểm tra đều chỉ mô tả, không đổi phán quyết. Calibration trên D-07H development, chỉ dùng các loại hỏng đơn (extra/missing/reversed), giống v4. Hai loại hỏng mới vì thế là out-of-distribution với cả hai module.

### `ext_narrow_ges`: skeleton do GES học (như A3)

- **Thiết lập:** như `a3_ges`: cùng seed, cell `none` và `ges`, T ∈ {40, 80, 150}, 20 topology × 3 replicate, n_boot 199.
- **Mức hỏng khai báo:** trung bình số lỗi GES trên bank calibration.
- **Method:** `plugin`, `pselect_union`, `tolerant_v4`, `tolerant_v5`.
- **Claim được phép**, xét riêng từng T, trong cell `ges`:
  - **"v5 tốt hơn v4 trên skeleton GES"** nếu coverage của v5 ≥ 0.90 và cận trên CI của hiệu IS ghép cặp (v5 − v4) < 0.
  - **"v5 tốt hơn `pselect_union` trên skeleton GES"** nếu coverage của v5 ≥ 0.90 và cận trên CI của hiệu (v5 − `pselect_union`) < 0.
- **Kỳ vọng ghi trước:** lợi thế nằm ở T = 40. Ở held-out của A3, đó là chỗ `pselect_union` có IS thấp hơn v4 (7.61 vs 9.26).

### `ext_narrow_structured`: hỏng có cấu trúc (như `rq42_structured`)

- **Loại hỏng:** shortcut, weak_missing, mixed × {0.2, 0.5}. Module chỉ nhận số đếm khai báo {missing, extra, reversed}.
- **Thiết lập:** T ∈ {40, 80, 150}; bỏ T = 300 để giữ thời gian chạy. 20 topology × 3 replicate, seed_base 20261102. Seed này khác `rq42_structured` (20261101), nên các dòng không ghép được với lần chạy đó; v4 được chạy lại trong cùng lần chạy.
- **Method:** `plugin`, `pselect_union`, `tolerant_v4`, `tolerant_v5`.
- **Báo cáo:** đếm số cell (trên 18) mà v5 có coverage ≥ 0.90 và cận trên CI của (v5 − v4) < 0, và đếm tương tự so với `pselect_union`. Cũng báo số cell mà IS của v5 > 1.05 × IS của v4.

## Kết quả ablation `ext_narrow_ablation` (D-07 development, 771 s, mô tả)

1260/1260 dòng `tolerant_v4` trùng với `ext_narrow_eval`, nên mọi phép so sánh là ghép cặp. Factor hiệu dụng cho missing (× 0.5): `tolerant_v5_sel` 1.80 / 1.55 / 1.45 và `tolerant_v5_cal2` 0.85 / 1.20 / 1.25 ở T = 40 / 80 / 150.

Bảng dưới ghi coverage / IS cho các cell missing, kèm hiệu IS ghép cặp so với v4 (CI 95%).

| T | cell | v4 | `v5_cal2` (chỉ calibration hai chiều) | `v5_sel` (targeted, chọn một lần) | **v5** (targeted, chọn lại mỗi draw) |
|---|---|---|---|---|---|
| 40 | missing-0.2 | 0.983 / 7.77 | 0.962 / 7.01; −0.76 [−0.90, −0.61] | 0.943 / 5.34; −2.43 [−2.88, −1.93] | 0.933 / 4.79; −2.98 [−3.44, −2.46] |
| 40 | missing-0.5 | 0.978 / 7.53 | 0.951 / 6.98; −0.55 [−0.73, −0.35] | 0.952 / 5.60; −1.93 [−2.33, −1.46] | 0.944 / 5.12; −2.41 [−2.76, −2.05] |
| 80 | missing-0.2 | 0.959 / 3.28 | 0.936 / 3.25; −0.02 [−0.09, +0.04] | 0.937 / 3.13; −0.15 [−0.36, +0.05] | 0.942 / 2.78; −0.50 [−0.66, −0.35] |
| 80 | missing-0.5 | 0.957 / 3.37 | 0.939 / 3.34; −0.03 [−0.10, +0.05] | 0.934 / 3.54; +0.17 [−0.02, +0.39] | 0.921 / 3.35; −0.02 [−0.22, +0.19] |
| 150 | missing-0.2 | 0.968 / 2.06 | 0.972 / 2.09; +0.03 [+0.00, +0.06] | 0.978 / 1.89; −0.16 [−0.24, −0.10] | 0.973 / 1.98; −0.08 [−0.21, +0.09] |
| 150 | missing-0.5 | 0.962 / 2.22 | 0.971 / 2.23; +0.01 [−0.02, +0.04] | 0.956 / 2.47; +0.25 [+0.03, +0.49] | 0.960 / 2.34; +0.12 [−0.02, +0.27] |

**Phân rã phần lợi ở T = 40, missing-0.2** (IS từ 7.77 xuống 4.79):
- **Calibration hai chiều:** −0.76. Bỏ sàn 1.0 cho phép factor xuống 0.85.
- **Targeted opening:** khoảng −1.67 nữa (7.01 → 5.34). Đây là phần lớn nhất.
- **Chọn lại mỗi bootstrap draw:** −0.55 nữa (5.34 → 4.79). Chọn một lần bỏ qua bất định của bước chọn, nên calibration phải nới mạnh (factor 1.80 so với 1.20).

**Ở T = 150, missing-0.5, targeted opening là chỗ tốn:** `v5_sel` +0.25 (CI không chứa 0), v5 +0.12. Calibration hai chiều một mình (`v5_cal2`) không tốn gì (+0.01). Kết luận: mở mọi lag là đúng khi T đủ lớn. Lợi thế của targeted opening giảm dần theo T và đổi dấu ở missing-0.5 khi T = 150.

### Quan sát hậu kiểm (post-hoc, KHÔNG phải phiên bản được giữ)

Một module ghép có thể dùng targeted opening khi T nhỏ so với số regressor của fit mở mọi lag, và mở mọi lag (`v5_cal2`) khi T lớn. Ngưỡng nằm đâu đó giữa tỷ lệ dòng/regressor khoảng 2.6 (T = 80) và khoảng 4.9 (T = 150); mọi ngưỡng trong khoảng này cho cùng kết quả trên grid hiện có.

Module ghép đó sẽ qua cả ba điều kiện trên chính các dòng này. Tuy vậy, ngưỡng được chọn **sau khi thấy** kết quả D-07 development, nên đây không phải là một kiểm tra. Muốn thành phiên bản v5.1, nó cần quy tắc mới và một bank chưa dùng (ví dụ một P4-H2 sinh mới). Mọi split hiện có đều đã dùng.

## Kết quả `ext_narrow_ges` (D-07 development, 373 s, mô tả)

Bảng đầy đủ: `results/ext_narrow_ges/describe.md`. Các dòng `tolerant_v4` (359/359) và `plugin` (360/360) trùng khít với `a3_ges`, nên dữ liệu và skeleton GES là cùng một bộ. Mức hỏng khai báo (trung bình trên bank calibration) là missing 13/13/12, extra 12/13/13, reversed 3/3/4 ở T = 40/80/150. v5 mở trung bình 39.0, 39.0 và 36.2 cặp.

Cell `ges`, coverage / IS / width:

| T | `plugin` | `pselect_union` | v4 | **v5** | v5 − v4 | v5 − `pselect_union` |
|---|---|---|---|---|---|---|
| 40 | 0.383 / 21.81 / 1.37 | 0.855 / 6.71 / 3.46 | 0.979 / 8.31 / 6.97 [59/60] | **0.970 / 6.10 / 5.22** [58/60] | −2.24 [−2.60, −1.86] | −0.62 [−1.22, +0.02] |
| 80 | 0.350 / 22.51 / 1.01 | 0.907 / 4.01 / 2.33 | 0.950 / 3.69 / 2.76 | 0.936 / 3.64 / 2.66 | −0.05 [−0.18, +0.12] | −0.36 [−0.58, −0.16] |
| 150 | 0.320 / 22.19 / 0.76 | 0.914 / 3.06 / 1.65 | 0.937 / 2.59 / 1.81 | 0.950 / 2.77 / 2.01 | **+0.18 [+0.03, +0.37]** | −0.29 [−0.68, +0.15] |

**Claim theo quy tắc ghi trước:**
- **"v5 tốt hơn v4 trên skeleton GES": chỉ đúng ở T = 40.** Ở T = 80 hai module hòa. Ở T = 150, v5 **tệ hơn** v4 (CI không chứa 0), giống mẫu missing-0.5 ở T = 150 trong `ext_narrow_eval`.
- **"v5 tốt hơn `pselect_union` trên skeleton GES": chỉ đúng ở T = 80.** Ở T = 40, v5 thu hẹp phần lớn khoảng cách: v4 thua `pselect_union` 8.31 so với 6.71, còn v5 đạt 6.10. Nhưng CI chạm 0 (cận trên +0.02), nên chỉ là hòa. Ở T = 150 cũng hòa.

**Thất bại khi fit:** v5 trả `underdetermined` ở 2/60 lần chạy tại T = 40 (syn_dag_06 rep 0, syn_dag_18 rep 0); v4 có 1/60 (syn_dag_06 rep 2). Skeleton GES có nút với rất nhiều cặp kề, nên phương trình nền của bước screening không còn đủ dòng.

**Ghi chú tái lập:** factor của v5 tune trong lần chạy này hơi khác `ext_narrow_eval`, ví dụ `tolerant_v5|80|missing` là 2.6 so với 2.5. Đây đúng là caveat đã ghi trước: stream bootstrap của method ext phụ thuộc vào số module ext có trong repo lúc chạy. Hiện có 5 module: eiv, gate, narrow, textinfo, tlp.

## Kết quả `ext_narrow_structured` (D-07 development, 983 s, mô tả)

Bảng đầy đủ: `results/ext_narrow_structured/describe.md`. Lần chạy mất khoảng 16 phút, hơi quá mức 15 phút đặt ra. Lúc chạy CPU dùng chung đang tải nặng (load average khoảng 30–40).

**Đếm theo quy tắc ghi trước, trên 18 cell hỏng có cấu trúc:**

| Tiêu chí | Số cell đạt |
|---|---|
| v5 coverage ≥ 0.90 và cận trên CI (v5 − v4) < 0 | **11/18**: 6/6 ở T = 40, 4/6 ở T = 80, 1/6 ở T = 150 |
| v5 coverage ≥ 0.90 và cận trên CI (v5 − `pselect_union`) < 0 | **18/18** |
| IS của v5 > 1.05 × IS của v4 | 1/18: mixed-0.5 ở T = 150, 2.71 so với 2.42, hiệu +0.30 [+0.16, +0.43] |

Một số cell tiêu biểu, ghi **coverage / IS**:

| T | cell | `pselect_union` | v4 | **v5** | v5 − v4 |
|---|---|---|---|---|---|
| 40 | shortcut-0.5 | 0.892 / 6.32 | 0.969 / 9.83 [57/60] | **0.937 / 5.28** | −4.66 [−7.94, −2.69] |
| 40 | mixed-0.5 | 0.839 / 7.33 | 0.987 / 8.80 | **0.965 / 5.96** | −2.84 [−3.22, −2.40] |
| 40 | weak_missing-0.2 | 0.868 / 6.85 | 0.976 / 7.62 | **0.938 / 4.53** | −3.09 [−3.52, −2.59] |
| 80 | weak_missing-0.2 | 0.935 / 3.43 | 0.961 / 3.21 | **0.949 / 2.82** | −0.39 [−0.58, −0.19] |
| 150 | mixed-0.5 | 0.860 / 3.87 | 0.954 / 2.42 | 0.953 / 2.71 | +0.30 [+0.16, +0.43] |

Coverage của v5 nằm trong khoảng 0.930–0.979 ở mọi cell có cấu trúc. Mẫu kết quả giống hai lần chạy trước: lợi lớn ở T = 40, lợi vừa ở T = 80, và ở T = 150 thì hòa hoặc thua khi nhiều cạnh bị thiếu (mixed-0.5).

## Tổng kết hướng "narrow"

- **Phán quyết theo quy tắc:** `tolerant_v5` **BỊ LOẠI**. Điều kiện 2 trượt ở một cell (missing-0.5, T = 150, tỷ lệ IS 1.054 so với ngưỡng 1.05). `tolerant_v4` vẫn là module of record.
- **Đóng góp có thể đưa vào bài, ở mức exploratory:**
  1. **Nguyên nhân over-wide của v4 ở T nhỏ đã được phân rã.** Phần lớn đến từ việc mở mọi lag; một phần đến từ sàn 1.0 của grid calibration.
  2. **Targeted opening theo bằng chứng cấu trúc, chọn lại trong mỗi bootstrap draw**, đóng được lỗ hổng ở T = 40. Trên các skeleton đặt tay:
     - IS giảm 32–38% ở missing (7.77 → 4.79 và 7.53 → 5.12);
     - coverage 0.93–0.94;
     - v5 thắng `pselect_union` ở 18/18 cell hỏng (a2 grid) và 18/18 cell hỏng có cấu trúc, trong khi v4 chỉ đạt 16/18 ở a2 grid.
     - Trên skeleton GES ở T = 40: v5 thắng v4 nhưng chỉ hòa `pselect_union`.
  3. **Bài học thiết kế:** chọn lại bên trong bootstrap tốt hơn chọn một lần (ablation). Lợi thế của targeted opening giảm dần theo T và đổi dấu ở T = 150 khi nhiều cạnh bị thiếu. Mở mọi lag chỉ đáng khi dữ liệu đủ dài.
- **Việc tiếp theo được đề xuất:**
  - Phiên bản v5.1 chuyển giữa targeted opening và mở mọi lag theo tỷ lệ dòng/regressor. Cần quy tắc mới và **một bank mới** để kiểm tra, vì ngưỡng được gợi ý từ chính D-07 development.
  - Tương tự, mọi claim về v5 ở trên chỉ là development, cần bank mới để xác nhận.

## Sửa sau kiểm chứng vòng 1

Phần này được append ở vòng 2 (hướng `v51`, xem `docs/ext/v51.md`), theo mục R2-10 của `docs/ext/synthesis_round1.md`. Không sửa nội dung phía trên; các câu dưới đây thay thế câu tương ứng.

1. **Công bố bổ sung: timing smoke run trên D-07 trước khi ghi quy tắc.** Lúc 18:27:12Z (khoảng 6 phút trước khi ghi quy tắc lúc 18:33:34Z), có một lần chạy thử để đo thời gian trên D-07 development: 1 topology, 1 replicate, có `tolerant_v5`. Output của các cell missing ở T = 40 đã hiện ra trên màn hình. Hyperparameter của v5 (mult = 3, alpha_open = 0.10, PRESCALE = 0.5) đã được chọn từ probe trên D-07H trước lần chạy này, và verifier không thấy dấu hiệu lần chạy đó lái thiết kế hay quy tắc. Tuy vậy, câu "D-07 vẫn chưa được nhìn" trong mục "Giới hạn đã biết trước" là **không đúng**: D-07 đã được nhìn ở 1 topology × 1 replicate trước khi ghi quy tắc.
2. **Structured damage: "11/18" → "10–11/18 (sát biên)".** Verifier chạy lại với seed bootstrap khác: cell T = 80 shortcut-0.5 đổi dấu cận trên CI. Số cell mà v5 thắng v4 trên 18 cell hỏng có cấu trúc vì thế là 10 hoặc 11 tuỳ seed, không phải 11 chắc chắn.
3. **Calibration hai chiều một mình: "khoảng −0.6 đến −0.8" → "−0.55 đến −0.76".** Đây là hai giá trị đo được của `v5_cal2` − v4 ở T = 40 missing-0.5 và missing-0.2 (bảng ablation phía trên). Câu tóm tắt nào dùng "−0.6 đến −0.8" phải đọc theo hai giá trị này.
4. **GES T = 40, v5 so với `pselect_union`:** cận trên CI là +0.02 hay −0.00 tuỳ seed bootstrap. Đây là **hòa sát biên**, đúng như đã viết ("chỉ là hòa"), không được trình bày như thắng.
5. **Đếm điều kiện 3:** đã ghi ở trên rằng "5 cell" là đếm sai lúc ghi quy tắc, đúng là 7 cell. Cả 7 đều được chấm và đều đạt.
6. **Tái lập số của method ext (X9, lỗi B1 của runner).** Mọi số của `tolerant_v5`, `v5_sel`, `v5_cal2` trong doc này chỉ tái lập được từng bit với đúng bộ file `ext_*.py` lúc chạy. Runner nay seed method ext theo tên (`ext_seed`), nên chạy lại sẽ cho số hơi khác (ví dụ factor `tolerant_v5|80|missing` 2.5 hay 2.6). Việc v5 bị loại ở tỷ lệ 1.054 (ngưỡng 1.05, CI của hiệu chứa 0) nằm đúng trong vùng nhạy với nhiễu này. Phán quyết LOẠI vẫn giữ nguyên theo quy tắc.
7. **Phần ghép cặp với baseline đã calibrate (R2-2a)** được làm ở `docs/ext/v51.md`, phần (a): v5 thắng `pselect_cal` và `fullvar_cal` ở 18/18 cell hỏng (Holm 18/18), thắng `targeted_lp_cal` ở 13/18 (Holm 11/18), hòa `targeted_lp_cal` ở T = 40 missing.
8. **Bug trùng term trong `opened_terms` (báo bởi auto5, xem cuối `docs/decision_rules.md`) ảnh hưởng mọi run missing của `tolerant_v5` và `v5_sel` ở doc này.** Đo trong vòng 2 (`results/ext_v51_eval/describe.md`): 100% run missing có term trùng (3–17 term trên fit dữ liệu gốc). Bản de-duplicate (`ext_v51.tolerant_sel_dd`) tốt hơn v5 vòng 1 ở T = 80 missing-0.5 (−0.25 [−0.45, −0.08]) và T = 150 missing (−0.22 và −0.35), và tốt hơn `v5_cal2` ở mọi cell missing kể cả T = 150. Câu "targeted opening là chỗ tốn ở T = 150 missing-0.5" và "mở mọi lag là đúng khi T đủ lớn" trong doc này là kết luận về **bản có bug**; với bản sửa, trên D-07 development targeted opening không tốn ở T = 150. Phán quyết LOẠI của v5 vòng 1 giữ nguyên (đó là phán quyết về module đã đánh giá); module sửa là `tolerant_v5_1` trong `docs/ext/v51.md`.

## Sửa sau kiểm chứng vòng 2

Phần này được append ở vòng 3 (hướng `v51fix`, xem `docs/ext/v51fix.md`), theo mục R3-6 của `docs/ext/synthesis_round2.md`. Không sửa nội dung phía trên. Các câu dưới đây sửa mục 8 của "Sửa sau kiểm chứng vòng 1".

1. **"3–17 term trên fit dữ liệu gốc" và "100% run missing có term trùng".** 3–17 (đúng là 3.1–16.7) là **trung bình theo cell**. Theo từng run, trên fit dữ liệu gốc là 0–44 term, và chỉ 290/360 run missing có term trùng ở fit đó; 360/360 run có term trùng khi tính cả các bootstrap draw (`results/ext_v51fix_shellonly/shell_only.md`). Bug vẫn chạm mọi run missing của `tolerant_v5` và `v5_sel` qua các draw.
2. **Phạm vi của câu "kết luận về bản có bug".** Chỉ các câu dựa trên số của module này ("targeted opening là chỗ tốn ở T150 missing-0.5", "mở mọi lag là đúng khi T đủ lớn", `v5_sel` +0.25 ở T150) bị bug chạm. Bằng chứng của gate trong X4 của synthesis vòng 1 độc lập với bug; kết luận chính của X3 (repair + orientation ở T150) không nói về targeted opening. `v5_sel` chưa được chạy lại sau khi de-dup, nên không có số "đã sửa" cho nó.
3. **"Tốt hơn `v5_cal2` ở mọi cell missing kể cả T150"** là kết quả của bản de-dup với τ = 6.6083. τ này mong manh (11% seed bootstrap của probe cho τ ≈ 2.94). Với τ ≈ 2.94, v5.1 ở T150 sẽ mở mọi lag và mất lợi thế đó (`results/ext_v51fix_t150tau/sens.md`: +0.33 / +0.28 so với v5.1, ngang v4). Lợi thế ở T150 thuộc về targeted opening đã de-dup, không thuộc về "thiết kế lai"; trên T ≤ 150 với 14 nút, `tolerant_v5_1` không bao giờ dùng nhánh all-lag.
4. **Phạm vi hash.** Mọi số của `tolerant_v5`, `v5_sel`, `v5_cal2` trong doc này chỉ tái lập được với đúng bộ file lúc chạy (đã ghi ở mục 6 vòng 1). Spec P4-H2 của module sửa (`tolerant_v5_1`) nay là spec v2 trong `docs/ext/v51fix.md` mục 3, với manifest hash 19 file; `ext_narrow.py` (sha256 9fc15ae7…) nằm trong manifest vì `ext_v51` import nó, và file này không được sửa.
5. **noise0.1 (của module sửa, ghi ở đây vì mục 8 trỏ sang).** `tolerant_v5_1` có coverage dưới 0.90 ở 5/9 cell noise0.1 (v4: 1/9); 0/9 có ý nghĩa sau Holm. Interval hẹp hơn của targeted opening mất coverage sát ngưỡng nhiều hơn dưới nhiễu đo.
