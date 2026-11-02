# r4hubscreen: sàng lọc CSIS cho phương trình hub bị underdetermined (vòng 4, exploratory)

Hướng này thử một kỹ thuật mượn từ tài liệu screening. Khi một phương trình cấu trúc của skeleton có nhiều biến hồi quy hơn số dòng, `tolerant_v5_1` hiện trả `_failed('underdetermined')`. Kỹ thuật này giữ lại một tập term đã rút gọn bằng **conditional sure independence screening (CSIS)** thay vì báo lỗi. Mọi kết quả ở đây là exploratory trên D-07 development. Không chạm P4-H1, P4-H2 hay split confirmatory nào.

## 1. Nguồn và cách đọc nguồn

- **Barut, Fan, Verhasselt (2016), JASA 111(515):1266–1277, arXiv:1206.1024.** CSIS giữ một tập điều kiện X_C đã biết là quan trọng (từ hiểu biết trước). Mỗi biến còn lại được xếp hạng theo độ lớn hệ số hồi quy biên có điều kiện |β̂_{C,j}|: hệ số của X_j khi fit cùng X_C (mục 1–2 của bài). Hai lợi ích nêu trong bài: (i) bắt được "hidden signature variable", biến biên không tương quan với Y nhưng quan trọng khi đã có X_C; (ii) giảm false positive vì tương quan giữa các covariate được giảm khi điều kiện hóa (λ_max(Σ_{D|C}) nhỏ hơn). Bài đề xuất hai cách chọn ngưỡng theo dữ liệu.
- **Fan, Lv (2008), JRSS-B 70(5):849–911.** SIS xếp hạng theo tương quan biên, giữ d biến (gợi ý d = n − 1 hoặc n / log n), rồi mới ước lượng trên tập nhỏ.
- **Kilian (2001), J. Forecasting 20(3):161–179.** Với IRF của VAR, chọn thiếu lag (underfitting) gây bias nặng hơn nhiều so với chọn thừa. Đây là cảnh báo chính với mọi phép rút gọn term.

**Khác biệt so với nguồn, ghi rõ:**
1. Thống kê xếp hạng là |t| của term khi thêm riêng nó vào OLS của y_j trên [1, C_j]. |t| đơn điệu theo |partial correlation|, là dạng chuẩn hóa của |β̂_{C,j}|. Bài gốc dùng |β̂| trên covariate đã chuẩn hóa.
2. Kích thước giữ lại là cố định, d = floor(m / 2.5) − 1 − |C_j|, theo đề xuất của vòng 4, không dùng ngưỡng theo dữ liệu của Barut et al. Với m = 28, cap là 11 cột; n / log n của Fan–Lv cho khoảng 8.
3. Tập điều kiện C_j không đến từ dữ liệu mà từ cấu trúc: own lags và cha cùng kỳ của skeleton. Nếu skeleton sai thì C_j có thể sai, và bài gốc cũng cảnh báo điều kiện hóa trên biến không hoạt động (hình 1c, 2c).

## 2. Thiết kế đã tinh chỉnh, cố định TRƯỚC khi chạy đánh giá

**Probe incidence (D-07H development, chỉ dùng skeleton, không dùng dữ liệu).** Script: `experiments/ext/r4hubscreen/probe_incidence.py`, kết quả ở `results/ext_r4hubscreen_probe/incidence.md`.
- lag_max 1, T ∈ {19, 25, 30, 35, 40}: **không** phương trình cơ sở nào fail check của `fit_equations`. Check của `screen_pairs` chỉ fail ở T19 reversed (0.15), nhưng nhánh reversed không gọi screening.
- lag_max 2: tỷ lệ unit có ít nhất một phương trình fail (screen / fit) là:
  - T19: 0.92–1.00 / 0.57–0.93;
  - T25: 0.27–0.72 / 0.18–0.38;
  - T30: 0.10–0.25 / 0.02–0.18;
  - T35: 0–0.10 / 0;
  - T40: 0 / 0.
- Bản đồ region51 (`docs/ext/region51.md`) đã cho thấy v5_1 chạy 60/60 ở lag_max 1, T = 19/25/30, trừ reversed-0.5 T19 (58/60).

**Hệ quả cho giả thuyết đề xuất.** Câu "điều này chặn phân tích lag_max 1 trên panel thật 14 × 19" **không đúng** với dữ liệu hiện có: ở lag_max 1, v5_1 đã chạy được. Chỗ bị chặn thật là **lag_max 2 ở T ≤ 30**, và với panel thật là lag_max 2. Vì vậy:

1. **Lưới chính đổi** từ lag 2 T{30, 35, 40} + lag 1 T{19, 25, 30} sang **lag_max 2, T ∈ {19, 25, 30, 35}**, cell {missing-0.2, reversed-0.2, extra-0.2}. Đây là **12 cell chính**, khớp với con số "12 damaged cells" trong rule đề xuất. Lý do: lưới cũ chỉ có rút gọn ở T30, nên gần như chỉ kiểm tra identity.
2. **Lưới phụ** (để kiểm tra identity và mô tả): lag 2 ô none ở T19–35, lag 2 T40 (4 ô), lag 1 T{19, 25, 30} (12 ô).
3. **Xếp hạng chung một pool.** Trong phương trình fail, các lag term của skeleton và các lag term của khối mở ở bước (2) được xếp hạng **chung**. Đề xuất gốc rút term skeleton trước rồi giới hạn khối mở vào phần còn trống. Nhưng term skeleton một mình đã lấp đầy cap, nên thứ tự đó sẽ đóng mọi khối mở của phương trình fail, mà mở khối chính là việc của bước (2).
4. **Hai hệ số width** để giữ đúng "where v5_1 already runs, the candidate is identical". Run không có rút gọn ở bất kỳ đâu (fit dữ liệu, screening, mọi bootstrap draw) dùng **đúng hệ số của v5_1** f_v51(T, kind). Run có rút gọn dùng f_red(T, kind), tune trên các run rút gọn của D-07H development.
   - Fallback được ghi trước: nếu có dưới 3 run rút gọn cho (T, kind), gộp qua kind ở cùng T; nếu vẫn dưới 3, gộp mọi T; nếu không có run nào, dùng f_v51.
   - Nếu f_v51 thiếu (v5_1 không hoàn tất run calibration nào), run không rút gọn dùng chuỗi f_red.
   - Biến thể một hệ số `tolerant_v5_1_hs1` được báo cáo phụ.
5. **Cùng luồng bootstrap.** Candidate dùng stream `rng([unit, 3, T, c_idx, ext_seed("tolerant_v5_1")])`, giống v5_1. Check underdetermination chỉ phụ thuộc số term, không phụ thuộc dữ liệu, nên run không rút gọn cho output **giống hệt** v5_1.
6. **Hiệu chỉnh.** Làm trên D-07H development, 20 topology × 3 replicate, chỉ rate 0.2 (như lưới đánh giá). Lag 2 T40 dùng hệ số v5_1 frozen từ `experiments/ext/v51/frozen_v4_v51.json`. Các T khác không có trong file frozen nên v5_1 được tune trong chính lượt chạy. Plugin_cal dùng hệ số một chiều theo (T, kind, rate), như `inflate` của runner.
7. **Mốc so sánh luôn chạy được.** `plugin` **không** luôn chạy được ở lag 2 T < 40 (region51: 9–56/60), trái với giả định của đề xuất. So sánh với `plugin_cal` vì vậy chỉ làm trên các run cả hai cùng hoàn tất. Bổ sung `plugin_hs_cal` (plugin cộng cùng phép rút gọn CSIS, hiệu chỉnh riêng) làm mốc phụ luôn chạy được.

**Code:**
- Method: `src/paper4/ext_r4hubscreen.py` (`tolerant_v5_1_hs`, `plugin_hs`). Module mới, chỉ import từ module cũ.
- Driver: `experiments/ext/r4hubscreen/run_r4.py`. Nó import hàm của runner; cần driver riêng vì runner chỉ có một hệ số cho mỗi (method, T, kind).
- Config: `experiments/configs/ext_r4hubscreen_lag2.json` và `_lag1.json`. D-07 development, 20 × 3, seed_base 20261102, n_boot 199, H 4. Layout cell là [extra, missing, reversed] × [0.2, 0.5], nên c_idx và skeleton trùng với `ext_v51_eval` và `a2_baselines`; chỉ các cell rate 0.2 và none được fit.

**Kiểm tra trước khi đánh giá (D-07H, đã chạy):** `experiments/ext/r4hubscreen/check_identity.py`, kết quả ở `results/ext_r4hubscreen_identity/identity.md`.
- Unit test CSIS: PASS.
- 128 run, trong đó 112 run không rút gọn: cả 112 giống hệt v5_1 → **PASS**.
- 16 run có rút gọn; 3 trong số đó v5_1 fail.

## 3. Quy tắc ghi trước (2026-11-02, trước lượt chạy đánh giá trên D-07)

**Cell chính P (12):** lag_max 2 × T ∈ {19, 25, 30, 35} × {missing-0.2, reversed-0.2, extra-0.2}. Mỗi cell có 60 run (20 topology × 3).

**Validity.**
- **V1:** script identity trên D-07H PASS (đã đạt ở trên).
- **V2:** trên MỌI cell của cả hai lưới, mọi run có hs_reduced = 0 và v5_1 ok đều cho dòng candidate trùng dòng v5_1 (|ΔIS| < 1e-12, cùng n_covered). V2 fail thì verdict là **INVALID**.
- **V3:** dòng v5_1 ở lag 2 T40 trùng `ext_v51_eval`, và dòng plugin trùng `a2_baselines`. Lệch được công bố, không đổi verdict.

**RETAINED (exploratory)** khi và chỉ khi V2 PASS và cả bốn tiêu chí sau đều đạt:
- **C1:** candidate hoàn tất ≥ 59/60 run (≥ 0.98) ở cả 12 cell P.
- **C2:** ITT coverage của candidate ≥ 0.90 ở ≥ 10/12 cell P, và không cell nào < 0.85. ITT nghĩa là run fail tính mọi cặp non-null là trượt. Kèm theo (mô tả): số cell Holm bác H0 "ITT ≤ 0.90" (cluster bootstrap theo topology, B = 20000, α = 0.05, Holm trên 12).
- **C3, no-harm:** trên các run v5_1 hoàn tất (ghép cặp), ở mỗi cell P có run ghép cặp: tỷ số IS trung bình candidate / v5_1 ≤ 1.05, **và** không cell nào tệ hơn có ý nghĩa sau Holm. Kiểm định một phía cho hiệu > 0, cluster bootstrap theo topology, B = 20000, Holm trên các cell có run ghép cặp, α = 0.05. Cell không có run ghép cặp nào thì tính là đạt (vacuous) và được báo cáo.
- **C4:** IS trung bình ghép cặp của candidate ≤ của `plugin_cal` ở ≥ 6/12 cell P, chỉ trên các run cả hai hoàn tất. Cell `plugin_cal` không có run nào tính là không thắng. Số thắng và số thua có ý nghĩa sau Holm (một phía, B = 20000, Holm trên 12, α = 0.05) được báo cáo kèm.

Nếu không đạt thì **REJECTED**, kèm danh sách tiêu chí trượt.

**Báo cáo mô tả, không quyết định:**
- tỷ lệ hoàn tất của v5_1 và plugin;
- coverage và IS trên các run "được cứu" (v5_1 fail, candidate ok);
- `tolerant_v5_1_hs1`; so sánh với `plugin_hs_cal`;
- số run rút gọn mỗi cell; lưới phụ;
- panel thật.

**Panel thật (chỉ mô tả).** Script `experiments/ext/r4hubscreen/real_panel.py`.
- Dữ liệu: panel 14 × 19, cửa sổ "defensible", chuẩn hóa z-score từng cột. Prior 21 cạnh: subgraph cảm sinh từ `prior_graph_final_278.json`.
- lag_max 1 và 2; khai báo none, missing k = 4, extra k = 4, reversed k = 2.
- Hệ số width: hệ số T19 của lượt chạy tương ứng.
- Báo cáo: method có chạy được không, phương trình nào bị rút gọn, width trung vị trên 182 cặp, và tỷ lệ interval không chứa 0.

**Ngân sách thời gian.** Ước lượng khoảng 25 phút ở `--workers 3` cho cả hai lag, gồm calibration. Không thu nhỏ lưới.

## 4. Kết quả


Lượt chạy ngày 2026-11-02, `--workers 3`. Máy dùng chung với nhiều agent khác (load khoảng 50 trên 12 core), nên chạy chậm hơn ước lượng:
- lag 2: 2043.9 s, trong đó calibration 968.6 s;
- lag 1: 1167.4 s, trong đó calibration 514.0 s.

Lưới không bị thu nhỏ. Bảng đầy đủ:
- `results/ext_r4hubscreen_ruling/ruling.md` (và `ruling.json`);
- `results/ext_r4hubscreen_ruling/describe.md`;
- `results/ext_r4hubscreen_real/real.md`.

### 4.1 Validity (nguyên văn)

- V1 identity script (D-07H): PASS (112 non-reduced runs)
- V2 candidate == v5_1 on runs with no reduction and v5_1 ok (all cells): 1458/1458 -> **PASS**
- V3 pairing lag 2 T40: v5_1 vs ext_v51_eval 240/240 identical (of 240 rows); plugin vs a2_baselines 240/240 (of 240)

### 4.2 Verdict (nguyên văn, `rule_eval.py`)

- C1 completion >= 59/60: 12/12 cells -> PASS
- C2 ITT coverage >= 0.90 in >= 10/12 (got 12/12), min >= 0.85 (got 0.924) -> PASS; Holm (alpha 0.05, over 12) rejections of H0 'ITT <= 0.90': 12/12
- C3 no-harm vs v5_1 on runs where v5_1 completes: ratio <= 1.05 in 12/12, Holm-significant worse 0/11 (cells with paired runs) -> PASS
- C4 IS <= plugin_cal (paired, both completed) in 8/12 (need >= 6); Holm-significant wins 4/12, Holm-significant worse 1/12 -> PASS
- Secondary vs plugin_hs_cal: IS <= in 5/12, Holm wins 3/12, Holm worse 0/12
- Validity V2: PASS

**Verdict: RETAINED (exploratory)**

### 4.3 Đọc kết quả (các số lấy từ ruling.md và describe.md)

1. **Candidate chạy được ở mọi run của lưới chính** (60/60 ở cả 12 cell), trong khi `tolerant_v5_1` chỉ hoàn tất:
   - T19: 0 / 8 / 3 run trên 60 (missing / reversed / extra);
   - T25: 26 / 36 / 33;
   - T30: 52 / 48 / 51;
   - T35: 60 / 60 / 60.

   ITT coverage của candidate là 0.924–0.976. Của v5_1 là 0.000–0.670 ở T ≤ 25 và 0.827–0.864 ở T30.
2. **Coverage trên các run "được cứu"** (v5_1 fail, candidate ok) là 0.931–1.000 ở các cell chính. Như vậy phần underfitting do bỏ term **không** phá coverage sau hiệu chỉnh, trái với lo ngại từ Kilian (2001).
3. **Cái giá là interval rộng và đuôi IS rất nặng ở T nhỏ.**
   - Ở T19 missing, IS trung bình là 152.63 nhưng trung vị chỉ 25.17. Có 10/60 run có IS > 50, lớn nhất 4206.6.
   - So trên 25 run mà `plugin_cal` cũng chạy được, candidate **tệ hơn có ý nghĩa sau Holm**: hiệu +299.46. Đây là "Holm worse 1/12" trong C4.
   - Nguyên nhân: fit dữ liệu hoặc bootstrap gần explosive. Hiện tượng này cũng có ở chính v5_1: lag 1 T19 reversed, IS trung bình 362.19 trên 60/60 run, không do rút gọn.
   - Ở T25 missing, IS trên run được cứu là 39.96, so với 13.95 trên run v5_1 tự chạy được.
4. **Nơi có lợi thật:** T30 và T35 missing. Ở đó v5_1 và candidate gần như trùng nhau, và thắng `plugin_cal` có ý nghĩa sau Holm: hiệu −11.66 và −13.83. Candidate gần như không thêm gì so với v5_1 ở đây, chỉ cứu 8/60 run ở T30 missing. Thắng có ý nghĩa còn lại là T19 reversed (−5.94, chỉ trên 8 run ghép cặp) và T35 reversed (−0.61).
5. **Với mốc luôn chạy được `plugin_hs_cal`** (cùng phép rút gọn, không có phần tolerant), candidate có IS ≤ ở 5/12 cell, thắng sau Holm 3/12, thua sau Holm 0/12. Ở T19 và T25, khi skeleton thiếu cạnh, `plugin_hs_cal` chỉ đạt coverage nhờ hệ số rất lớn (7.3–7.7) và có IS tương đương hoặc tốt hơn về trung bình. Ví dụ T19 missing: 45.92 so với 152.63 trung bình, nhưng 40.09 so với 25.17 trung vị.
6. **Lưới phụ.**
   - lag 2 T40: 0 run rút gọn, candidate trùng v5_1.
   - lag 1: rút gọn chỉ xảy ra ở T19 missing (10 run) và T19 reversed (3 run), qua screening hoặc qua draw. Ở T25 và T30 không có run nào.
   - Không có run nào ở lag 1 mà v5_1 fail.
7. **Giả thuyết "chặn phân tích lag_max 1 của panel thật" bị bác.** Trên panel thật (z-score), ở lag_max 1, v5_1 chạy ở cả 4 khai báo mà không cần rút gọn: width trung vị 2.15–4.68. Ở **lag_max 2**, v5_1 fail ("underdetermined") ở cả 4 khai báo. Candidate chạy được, chỉ rút gọn phương trình của `macro_policy_rate_pct` (bậc 9 trong prior), cộng thêm 5 nút khác khi khai báo missing. Width trung vị 2.12–7.30, và gần như không interval nào loại được 0 (tỷ lệ 0.00–0.01). Kết quả chỉ mang tính mô tả.
8. **Độ nhạy của hệ số width.** Ở lag 2 T40, hệ số frozen của v5_1 (2.3–2.8) cho coverage 0.914–0.928. Tune lại trên D-07H (chỉ rate 0.2, 3 replicate) cho 2.7–3.3, và biến thể `hs1` dùng hệ số này đạt 0.948–0.955. Đây là cùng một điểm yếu đã biết: hệ số phụ thuộc vào bank và lưới calibration.

### 4.4 Phát hiện về file hiện có (báo cáo, không sửa)

- `ext_narrow.screen_pairs` (check `|X| + lag_max + 2 > m`) chặt hơn check của `estimator.fit_equations` (`|terms| + 2 > m`). Ở lag 2 T25–35 khi khai báo missing, nhánh targeted của v5_1 fail ở **screening** dù các phương trình vẫn fit được.
- `estimator.fit_equations` cho qua phương trình có dof = 1–2. Khi đó `simulate_from_fit` phóng phần dư theo sqrt(m / dof), nên IS bùng nổ, như ở lag 1 T19 reversed với v5_1. Đây không phải bug, nhưng là nguồn chính của đuôi IS. Candidate theo đúng thiết kế không chạm vào các phương trình này. Một bản v2 có thể rút gọn theo ngưỡng dof thay vì chỉ khi check fail; đó sẽ là quy tắc mới.

## 5. Frozen spec (chỉ dùng cho exploratory; chưa chạy held-out nào)

- **Method:** `tolerant_v5_1_hs`, module `src/paper4/ext_r4hubscreen.py`, dựng trên `ext_v51`, `ext_narrow`, `methods` và `estimator` mà không sửa các module đó.
- **Bootstrap stream:** `rng([unit, 3, T, c_idx, ext_seed("tolerant_v5_1")])`, giống v5_1.
- **Width:** chạy qua driver `experiments/ext/r4hubscreen/run_r4.py`.
  - Run không có rút gọn ở đâu cả (dữ liệu, screening, mọi draw): f_v51(T, kind). Lấy từ file frozen nếu có key, nếu không thì tune trên bank calibration.
  - Run có rút gọn: f_red(T, kind), tune trên các run rút gọn, với fallback (≥ 3 run; gộp theo T; gộp toàn bộ; rồi f_v51) như mục 2.
  - Hệ số đã tune trên D-07H dev: `results/ext_r4hubscreen_lag2/calibration.json` và `results/ext_r4hubscreen_lag1/calibration.json`.
- **Config template:** `experiments/configs/ext_r4hubscreen_TEMPLATE.json`. Bank, split, seed_base và bank calibration để là PLACEHOLDER.
- **Rule:** giữ nguyên mục 3 (V2, C1–C4 trên 12 cell lag 2 × T{19, 25, 30, 35} × {missing, reversed, extra}-0.2). Đề nghị thêm cho một lượt held-out: báo cáo IS trung vị bên cạnh IS trung bình, vì đuôi nặng ở T19. Đề nghị này phải được ghi thành quy tắc **trước** lượt đó nếu muốn dùng để ra quyết định.
- **Spec manifest:** `experiments/ext/r4hubscreen/spec_files.json`, gồm sha256 của 22 file phụ thuộc.

**Mức chắc chắn.** RETAINED chỉ là exploratory trên D-07 development. D-07 đã bị dùng nhiều lần, và mọi split confirmatory hiện có đều đã dùng. Một claim xác nhận cần bank niêm phong mới.
