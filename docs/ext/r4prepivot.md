# Hướng r4prepivot (vòng 4): hiệu chỉnh width theo từng dataset bằng double bootstrap rút gọn (Beran prepivoting / Loh calibration)

**Trạng thái.** Exploratory, D-07 development (seed_base 20261102 cho phần chính; 20261101 cho phần lag_max = 1). Pre-screen và test chỉ dùng D-07H development. Không chạm P4-H1, P4-H2 (cả hai split) hay split confirmatory nào. Không gọi LLM. Không commit.

**File (chỉ file mới):**
- Code: `src/paper4/ext_r4prepivot.py` (METHODS: `tolerant_v5_1_pp`, `tolerant_v5_1_pp_orig`). Chỉ import `ext_v51`, `methods`, `estimator`, `effects`; không sửa module nào.
- Script: `experiments/ext/r4prepivot/` (`common.py`, `run_eval.py`, `analyze.py`, `prescreen.py`, `test_prepivot.py`, `real_panel.py`).
- Config: `experiments/configs/ext_r4prepivot_{primary,secondary,scen,lag1}.json`.
- Kết quả: `results/ext_r4prepivot_*`.

## 1. Nguồn và ý tưởng

- **Beran (1987), Biometrika 74(3):457–468.** Prepivoting: biến root R thành 1 − α bằng CDF bootstrap của nó, rồi bootstrap lần hai để ước lượng phân phối của root đã prepivot. Interval nhận được có sai số coverage bậc thấp hơn.
- **Loh (1987), JASA 82(397):155–162.** Calibration: chọn nominal level (ở đây là hệ số nhân width) sao cho coverage **ước lượng trong thế giới bootstrap** bằng 1 − α. Thế giới bootstrap có truth đã biết (mô hình đã fit), nên coverage của chính thủ tục có thể được đo trong đó.
- **Martin (1990), JASA 85(412):1105–1118.** Iterated bootstrap: phân tích bậc sai số, và khuyến nghị số draw ở tầng trong.
- **Davidson & MacKinnon (2007), CSDA 51(7):3259–3281.** Fast double bootstrap (một draw tầng trong). Chỉ được đề xuất để screen code path; xem mục 3 về lý do không dùng được với root theo sd.

Áp vào v5.1: bước [6] (hệ số width tune trên bank D-07H theo (T, loại hỏng khai báo)) được thay bằng hệ số f_d tính trên chính dataset. Đây là cách duy nhất để có width rule trên panel thật 14 × 19, nơi không có bank.

## 2. Thiết kế (chốt trước mọi run D-07)

Với một dataset (dữ liệu, skeleton công khai, mức hỏng khai báo):

1. Chạy `tolerant_v5_1` **không đổi**, B = 199 outer draw. Một recorder thay `bootstrap_C` trong namespace của `methods` và `ext_v51` **chỉ trong lúc gọi** (khôi phục trong `finally`). Recorder chép từng dòng `estimator.bootstrap_C`, chỉ thêm việc giữ lại series bootstrap. Vì vậy outer draw **trùng từng bit** với v5.1 (test 6 và pre-screen: 10/10 identical). Gọi `fit` là fit sinh ra outer draw; truth của thế giới outer là C0 = cumulative(irf(fit.B, H)).
2. Giữ B_O = 39 outer series thành công đầu tiên x_b. Với mỗi x_b, chạy **toàn bộ** thủ tục v5.1 với x_b làm dữ liệu: chọn lại cặp mở, repair lại, dựng lại reversal pool, fit sinh của riêng nó, chọn lại trong từng draw. Số draw tầng trong B_I = 19, cho ra C**_{b,1..19}.
3. Root theo (b, cặp có thứ tự): r = |C0 − mean_c C**| / sd_c(C**), với ddof 1. Chỉ lấy cặp có sd > 1e-12·(1 + |mean|), tức bỏ cặp hằng (sd = 0, kể cả sai số làm tròn).
4. c_d = quantile 0.95 của các root gộp; f_d = c_d / z_ref.
5. Interval cuối là percentile interval outer **chưa scale** của v5.1 (không PRESCALE, không bank factor), nới quanh trung điểm theo hệ số f_d. Point estimate, theta, B giữ của v5.1.
6. Nếu ít hơn 20/39 thế giới tầng trong cho ≥ 10 draw hợp lệ, method trả `prepivot_failed`. Seed tầng trong được rút từ rng của method **sau** outer bootstrap, nên không ảnh hưởng outer draw.

### Ba điểm tinh chỉnh so với thiết kế được đề xuất (có lý do, chốt trước khi chạy D-07)

**(R1) Mô hình sinh tầng trong là thủ tục v5.1 chạy trên x_b, không phải fit fb của outer draw.**
- Double bootstrap chuẩn (Beran, Loh, Martin) áp **cả thủ tục** lên mỗi mẫu bootstrap.
- Ở nhánh reversed (v3), mô hình sinh của v5.1 là fit **chưa lật** của skeleton khai báo. Ngược lại, fb là fit đã lật ngẫu nhiên, nên dùng fb sẽ tạo một thế giới tầng trong không tương ứng với thế giới outer.
- Ở nhánh targeted, hai cách gần như cùng phân phối. Khác biệt duy nhất là reversal pool và fallback của tập mở được tính lại trên x_b.
- Chi phí thêm không đáng kể (một lần chọn và một lần fit cho mỗi b).

**(R2) Tập root chính là "nn": cặp ngoài đường chéo có |C0| > 0.1.** Thiết kế gốc dùng mọi cặp, kể cả đường chéo.
- Lý do: thế giới bootstrap **biết** truth của nó (C0, tính từ dữ liệu), nên có thể bắt chước đúng tập được chấm điểm. Coverage được chấm trên cặp non-null ngoài đường chéo, |C_true| > tau_effect = 0.1.
- Không dùng truth thật: ngưỡng 0.1 là định nghĩa "hiệu ứng đáng quan tâm" của chính estimand.
- Bản gốc (mọi cặp, 1.96) vẫn được tính trên cùng draw tầng trong và báo kèm dưới tên `tolerant_v5_1_pp_orig`. Bản này **không** dùng cho verdict.

**(R3) Mẫu số z_ref = t_{0.975, 18} · sqrt(1 + 1/19) = 2.1555, không phải 1.96.**
- Mean và sd tầng trong chỉ có 19 draw. Nếu bootstrap của v5.1 calibrate hoàn hảo và phân phối chuẩn, root là |t_18| · sqrt(20/19). Quantile 0.95 của nó là 2.1555. Interval outer dùng 199 draw, nên ở đó tham chiếu chuẩn 1.96 đúng.
- Chia cho 1.96 làm f_d bị đẩy lên khoảng 10% bất kể dữ liệu. Test 3 (known truth, bootstrap hoàn hảo, 200 lần lặp) cho mean f = 0.9985 với z_ref và 1.098 với 1.96.
- Điều này đã được biết **trước** khi chạy D-07, và nó làm f_d **nhỏ hơn**, tức đi ngược hướng giúp method qua cổng coverage.

### Pre-screen (D-07H development, seed 7 740 000; không dùng cho quyết định nào)

`experiments/ext/r4prepivot/prescreen.py` → `results/ext_r4prepivot_prescreen/prescreen.json` (chạy 12:11Z, 16 s).
- **Exactness:** 10/10 lần recorder cho đúng interval của v5.1, và interval prescale đúng bằng 0.5 × interval chưa scale.
- **Code path:** B_O = 5 đúng như dự kiến cho `prepivot_failed` ở 30/30 dataset (5 < 20).
- **Kích thước đầy đủ (39 × 19), syn_dag_00 missing-0.5:** T40 4.3 s, T80 4.7 s mỗi dataset. v5.1 một mình mất 0.8–0.9 s, tức khoảng 5×.
- **Về B_I = 1 (fast double bootstrap):** không làm được, vì root theo sd cần ít nhất 2 draw tầng trong. Thay bằng chạy rút gọn B_O = 5 cộng 2 dataset kích thước đầy đủ.

**Công bố: các số f đã thấy trước khi viết quy tắc** (đều trên D-07H):
- Pre-screen, syn_dag_00 missing-0.5, root "all"/1.96: f_orig = 0.81 ở T40 và 1.00 ở T80. Bank factor tương ứng là 1.15 và 1.30.
- Test 6, T40 missing-0.5, một dataset khác: f_pp = 0.81.
- Test 8, T80 reversed-0.5: f_pp = 1.08, so với bank 1.35.

Tức là trên vài dataset D-07H, f_d **nhỏ hơn** bank factor khá nhiều. Điều này khớp với giả thuyết: thế giới bootstrap lấy mô hình đã fit (còn thiếu cạnh) làm truth, nên không thấy được bias do damage mà pipeline không phát hiện.

### Test (known truth): 14/14 PASS

`experiments/ext/r4prepivot/test_prepivot.py` → `results/ext_r4prepivot_tests/tests.json`. Các test gồm:
- quantile t khớp bảng;
- root trên ví dụ tính tay;
- bootstrap hoàn hảo cho f ≈ 1;
- bootstrap thiếu phân tán một nửa cho f ≈ 2 (1.93);
- phép nới interval;
- outer draw trùng v5.1;
- không đọc log riêng;
- tính tất định;
- khôi phục `bootstrap_C` kể cả khi có exception;
- nhánh reversed chạy được.

Helper của analyzer (ratio, cổng p, coverage ITT, Holm, Spearman) đã được kiểm trên dữ liệu giả với đáp án biết trước.

## 3. Quy tắc ghi trước (ghi lúc 2026-11-02T12:20Z, trước mọi run D-07 của hướng này)

**Run chính** `experiments/configs/ext_r4prepivot_primary.json`, driver `run_eval.py`, `--workers 3`:
- D-07 development, seed_base 20261102. Dữ liệu và skeleton hỏng sinh bằng chính hàm của runner, theo config `ext_v51_eval`, nên vị trí cell (c_idx) trùng.
- Stream bootstrap outer là stream của `tolerant_v5_1` trong runner: `[unit, 3, T, c_idx, ext_seed("tolerant_v5_1")]`.
- **9 cell:** T ∈ {40, 80} × {missing, reversed} × {0.2, 0.5}, cộng none ở T80.
- **20 topology × 3 replicate (0, 1, 2), tức 60 run mỗi cell.** Đề xuất gốc là 1 replicate vì lo thời gian chạy. Pre-screen cho thấy mỗi dataset chỉ khoảng 5 s, nên dùng cả 3 replicate. Cluster vẫn là 20 topology.
- Comparator là `tolerant_v5_1` với factor đóng băng `experiments/ext/v51/frozen_v4_v51.json` (đủ key T40/T80/T150 × none/extra/missing/reversed), tính lại trong cùng run.

**Kiểm tra ghép cặp (điều kiện hợp lệ).**
- Các dòng `tolerant_v5_1` của run này phải trùng khít với `results/ext_v51_eval/runs.jsonl` ở 540/540 khoá (topology, replicate, T, kind, rate): cùng status, |ΔIS| < 1e-12, cùng `n_covered_nonnull` và `n_nonnull`.
- Nếu không trùng, verdict là KHÔNG GIỮ (invalid).

**Thống kê mỗi cell:**
- Coverage ITT: run thất bại tính mọi cặp non-null là không phủ.
- Tỷ số trung bình R = mean IS_pp / mean IS_v51, trên các run cả hai đều ok.
- Cluster bootstrap theo topology, B = 20000, seed 20261104.
- p một phía cho H0: R ≥ 1.10, tính bằng p = (1 + #{R* ≥ 1.10}) / (B + 1).
- Holm ở mức 0.05 trên 9 kiểm định.
- Cell **non-inferior** nếu H0 bị bác sau Holm. Báo kèm cận trên một phía 95% (phân vị 95 của R*) và CI hai phía 95%.

**`tolerant_v5_1_pp` được GIỮ như một lựa chọn không cần bank (exploratory) nếu đồng thời:**
1. ghép cặp PASS;
2. non-inferior (Holm) ở **≥ 7/9** cell;
3. coverage ITT ≥ 0.90 ở **cả 9** cell;
4. mỗi cell có ≤ 3/60 run `tolerant_v5_1_pp` thất bại.

Nếu không, method chỉ được báo như một sensitivity analysis. Script áp quy tắc: `experiments/ext/r4prepivot/analyze.py primary` → `results/ext_r4prepivot_primary/ruling.md`, `ruling.json`, `analysis.md`, `analysis.json`.

**Báo kèm (mô tả, không đổi verdict):**
- `tolerant_v5_1_pp_orig` (thiết kế đúng như đề xuất), với cùng thống kê.
- Phân phối f_d theo cell (median, IQR, min, max) so với factor hiệu dụng của v5.1 (= factor × 0.5).
- Spearman của f_d với k (số cạnh hỏng khai báo, trong cùng loại, gộp với none) và với T.
- Thời gian mỗi dataset.
- IS trên cặp null.

**Run phụ (mô tả, không có quy tắc; mỗi run dưới 30 phút):**
- `ext_r4prepivot_secondary`: 12 cell còn lại của grid a2 (T40 none; T40/80 extra × 0.2/0.5; T150 cả 7 cell). Ghép cặp với `ext_v51_eval`. Báo cùng thống kê, Holm trên 12 cell.
- `ext_r4prepivot_scen`: kịch bản latent1 và noise0.1 (đúng định nghĩa của runner), T ∈ {80, 150} × {none, missing-0.2, reversed-0.2}. Config gốc là `ext_v51_a1`, nên c_idx và skeleton giống run đó. Ghép cặp với `results/ext_v51_a1`, factor v5.1 lấy từ `results/ext_v51_a1/calibration.json` (bằng factor đóng băng).
- `ext_r4prepivot_lag1`: vùng giống panel thật, lag_max = 1, T ∈ {19, 25} × {none, missing 0.2/0.5, reversed 0.2/0.5}. Config gốc là `ext_region51_lag1` (seed 20261101). Ghép cặp với `results/ext_region51_lag1`, factor v5.1 lấy từ calibration.json của run đó (tune lại theo (lag_max = 1, T) trên D-07H).
- **Panel thật** (`real_panel.py`, chỉ đọc ACIIDS):
  - dữ liệu 14 × 19, chuẩn hoá z-score theo cột;
  - skeleton là prior 21 cạnh;
  - lag_max = 1, H = 4;
  - khai báo none / missing-0.2 / missing-0.5 / reversed-0.2;
  - báo f_d, factor hiệu dụng v5.1 của (lag_max 1, T19), và median width của hai interval.

  Phần này chỉ mô tả.

**Dự đoán, ghi trước:**
- f_d sẽ nhỏ hơn bank factor ở các cell missing, do thế giới bootstrap không thấy damage chưa được phát hiện (pre-screen gợi ý 0.8 so với 1.15 ở T40). Vì vậy cổng coverage ≥ 0.90 nhiều khả năng trượt ở ít nhất một cell missing.
- Ở cell reversed-0.5, coverage có thể thấp hơn v5.1.
- Ở cell none, pp có thể ngang v5.1.
- Nếu dự đoán đúng, verdict sẽ là NOT RETAINED.

Không có thay đổi quy tắc nào sau khi có kết quả. Một thiết kế lại (ví dụ thêm sàn cho f_d) sẽ là một phiên bản mới với quy tắc mới.

---

## 4. Kết quả (append sau khi chạy; quy tắc ở mục 3 không đổi)

**Thời điểm và tính toàn vẹn.**
- File hash ghi trước (`experiments/ext/r4prepivot/prereg_sha256.txt`) có timestamp 2026-11-02T12:18:43Z. Run chính bắt đầu 12:18:48Z.
- Dòng "ghi lúc 12:20Z" ở mục 3 là giờ ước lượng lúc viết; mốc ràng buộc là hash 12:18:43Z. Sau khi chạy, hash của doc phần 1–3 vẫn trùng (28137f48…). Chỉ mục 4 trở đi được append.
- Không file nào trong `prereg_sha256.txt` bị sửa. `extras.py` được viết **sau** verdict; nó chỉ đếm thêm cell "tệ hơn có ý nghĩa", không đổi verdict.

**Thời gian chạy** (`--workers 3`, máy bị chia với các agent khác, load 24–66 trên 12 core):

| Run | Thời gian | Số dataset |
|---|---|---|
| primary | 1256 s | 540 |
| secondary | 1312 s | 720 |
| lag1 | 873 s | 600 |
| scen | 811 s | 720 |

Mọi run đều dưới 30 phút. Log ở `results/ext_r4prepivot_logs/`.

### 4.1 Verdict theo quy tắc (nguyên văn `results/ext_r4prepivot_primary/ruling.md`)

"pairing PASS; non-inferior (Holm 0.05 over 9) 0/9 (raw one-sided 95% bound < 1.10: 1/9); coverage >= 0.90 in 1/9; failure cap (<= 3 failed of 60) PASS -> tolerant_v5_1_pp NOT RETAINED (sensitivity analysis only). Secondary (design as proposed, descriptive): non-inferior Holm 1/9, coverage >= 0.90 in 0/9."

**→ `tolerant_v5_1_pp` KHÔNG ĐƯỢC GIỮ.** Method chỉ được báo như một sensitivity analysis. Vì vậy **không có mục "Frozen spec"** và không có spec manifest.

**Ghép cặp:** dòng `tolerant_v5_1` của run này trùng khít `results/ext_v51_eval/runs.jsonl` ở 540/540 khoá. Mọi so sánh vì thế là ghép cặp thật: cùng dữ liệu, cùng skeleton hỏng, cùng 199 outer draw.

### 4.2 Bảng 9 cell chính

Nguồn: `results/ext_r4prepivot_primary/analysis.md`, `analysis.json`. Mỗi cell có 60 run, 20 cluster.
- R là tỷ số trung bình IS pp / IS v5.1.
- "Tệ hơn" là p một phía cho H0: R ≤ 1, Holm 0.05 trên 9 cell (`results/ext_r4prepivot_extras.json`).

| T | cell | cov v5.1 | cov pp | IS v5.1 | IS pp | R [CI 95% hai phía] | cận trên 1 phía | p(H0: R ≥ 1.10) | non-inf Holm | f_pp median [IQR] | f v5.1 (bank) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 40 | missing-0.2 | 0.922 | **0.828** | 4.84 | 5.79 | 1.196 [1.102, 1.294] | 1.278 | 0.978 | N | 0.822 [0.768, 0.886] | 1.15 |
| 40 | missing-0.5 | 0.939 | **0.816** | 5.09 | 6.28 | 1.234 [1.112, 1.371] | 1.347 | 0.987 | N | 0.751 [0.714, 0.787] | 1.15 |
| 40 | reversed-0.2 | 0.928 | **0.863** | 4.70 | 5.09 | 1.082 [0.993, 1.172] | 1.156 | 0.322 | N | 1.052 [0.982, 1.130] | 1.40 |
| 40 | reversed-0.5 | 0.920 | **0.843** | 4.74 | 5.36 | 1.130 [1.043, 1.226] | 1.210 | 0.711 | N | 1.038 [0.958, 1.110] | 1.40 |
| 80 | missing-0.2 | 0.949 | **0.860** | 2.84 | 3.23 | 1.138 [1.058, 1.215] | 1.203 | 0.820 | N | 0.938 [0.901, 0.969] | 1.30 |
| 80 | missing-0.5 | 0.951 | **0.855** | 3.10 | 3.53 | 1.139 [1.065, 1.214] | 1.202 | 0.845 | N | 0.921 [0.893, 0.944] | 1.30 |
| 80 | reversed-0.2 | 0.941 | **0.876** | 2.79 | 3.07 | 1.098 [1.043, 1.152] | 1.143 | 0.459 | N | 1.034 [0.996, 1.066] | 1.35 |
| 80 | reversed-0.5 | 0.918 | **0.846** | 3.05 | 3.53 | 1.160 [1.105, 1.213] | 1.205 | 0.985 | N | 1.031 [0.986, 1.079] | 1.35 |
| 80 | none | 0.939 | 0.904 | 2.53 | 2.66 | 1.051 [1.006, 1.097] | 1.089 | 0.019 | N (raw Y) | 1.098 [1.063, 1.142] | 1.30 |

**Đọc kết quả:**
- pp **tệ hơn v5.1 có ý nghĩa ở 9/9 cell, cả thô lẫn sau Holm**. Nó không phải "gần ngang". Mọi cell hỏng có R từ 1.08 đến 1.23.
- Coverage chỉ đạt ≥ 0.90 ở **1/9** cell (none, 0.904). Ở cell missing T40, coverage xuống 0.816–0.828.
- Bản đúng như đề xuất (`_orig`: mọi cặp, mẫu số 1.96) cũng không khá hơn: non-inferior 1/9, coverage ≥ 0.90 ở 0/9, coverage 0.834–0.900. Tinh chỉnh (R2) và (R3) không phải nguyên nhân thất bại. Ở cell missing, f_pp nhỏ hơn f_orig khoảng 4–5%, nhưng coverage của hai bản lệch nhau ≤ 0.021.

### 4.3 Hệ số f_d so với bank factor, và tương quan với mức hỏng

- **f_pp (median) bằng 0.65–0.85 lần bank factor hiệu dụng của v5.1** ở cả 9 cell. Thấp nhất ở T40 missing-0.5 (0.751 so với 1.15), cao nhất ở none T80 (1.098 so với 1.30).
- **f_pp tương quan nghịch với mức hỏng khai báo.** Spearman theo run: −0.616 với k (missing + none, n = 300); −0.45 ở T40 và −0.75 ở T80; −0.26 với reversed + none. f_pp tương quan dương với T: +0.31.
- Đây là chiều **ngược** với chiều cần có, vì bank factor của v5.1 không giảm theo damage.
- **Cơ chế** (giải thích, không phải kiểm định):
  - Thế giới bootstrap lấy mô hình đã fit làm truth, tức skeleton khai báo cộng các cặp đã mở và repair trên dữ liệu.
  - Tầng trong chọn lại và repair lại, nên thêm phương sai quanh C0. Khai báo càng nhiều cạnh thiếu thì K = max(3k, …) càng lớn và nhiễu chọn lại càng nhiều. Root vì vậy nhỏ đi và f_d giảm.
  - Bias thật do cạnh thiếu **chưa** được phát hiện thì không tồn tại trong thế giới bootstrap. Double bootstrap không thấy được nó.
  - Ngay cả ở cell none, f_pp (1.10) vẫn thấp hơn bank factor (1.30). Tức là ngay phần sai số mẫu nhỏ của residual bootstrap, double bootstrap rút gọn cũng chỉ bù được khoảng một phần ba.

### 4.4 Run phụ (mô tả, không có quy tắc)

Nguồn: `results/ext_r4prepivot_{secondary,lag1,scen}/analysis.md`; đếm Holm ở `results/ext_r4prepivot_extras.json`. Ghép cặp: secondary 720/720 với `ext_v51_eval`, lag1 600/600 với `ext_region51_lag1`, scen 720/720 với `ext_v51_a1`. Tất cả PASS.

| Run | Số cell | non-inferior (Holm 0.05) | tệ hơn v5.1 (thô / Holm) | coverage pp ≥ 0.90 | Ghi chú |
|---|---|---|---|---|---|
| secondary (T40 none, extra; T150 mọi cell) | 12 | **12/12** | 6 / 2 | 8/12 | Ở T150 mọi cell non-inferior. R = 0.98–1.05, coverage 0.90–0.94 (v5.1: 0.94–0.97). Hụt coverage ở T40 none 0.898, T40 extra 0.879 / 0.879, T80 extra-0.5 0.893 |
| lag1 (lag_max = 1, T19/T25, vùng giống panel thật) | 10 | 5/10 | 2 / 1 | **1/10** | Coverage pp 0.811–0.913. Chỉ T25 none ≥ 0.90. T19 reversed-0.5: 57/60 ok (2 run v5.1 thất bại ngay trên dữ liệu (`bootstrap_failed`, giống run đã lưu), 1 `prepivot_failed`) |
| scen (latent1, noise0.1; T80/150) | 12 | 3/12 | 12 / 12 | 2/12 | Coverage pp 0.804–0.909. Với noise0.1 missing-0.2 ở T80: 0.804, R = 1.28 |

Bản `_orig` ở các run phụ: secondary non-inf 11/12, coverage 9/12; lag1 5/10, 1/10; scen 4/12, 2/12.

**Đọc:**
- pp chỉ "dùng được", theo nghĩa non-inferior **và** coverage ≥ 0.90, ở những cell mà damage vô hại (extra) hoặc T lớn (T150, cả missing). Đó đúng là nơi bank factor ít quan trọng.
- Ở vùng giống panel thật (lag_max = 1, T19/25), pp under-cover ở 9/10 cell. Giả thuyết "đây là width rule duy nhất dùng được trên panel thật" **không được ủng hộ**: rule này có chạy được, nhưng interval của nó không đạt coverage danh nghĩa trong mô phỏng ở chính vùng đó.
- Với biến ẩn và nhiễu đo, pp tệ hơn v5.1 ở 12/12 cell (Holm). Điều này khớp với dự đoán: double bootstrap không thấy lệch mô hình.

### 4.5 Panel thật 14 × 19 (mô tả)

Nguồn: `results/ext_r4prepivot_realpanel/real_panel.md`, `.json`. Cấu hình: lag_max = 1, dữ liệu chuẩn hoá z-score, skeleton prior 21 cạnh.

| Khai báo | k | thế giới trong ok | f_pp | f_orig | f v5.1 (bank lag1, T19) | median width v5.1 | pp | orig |
|---|---|---|---|---|---|---|---|---|
| none | 0 | 39 | 1.216 | 1.173 | 1.50 | 1.97 | 1.60 | 1.54 |
| missing-0.2 | 4 | 39 | 0.716 | 0.732 | 1.05 | 3.25 | 2.22 | 2.27 |
| missing-0.5 | 11 | 38 | 0.617 | 0.667 | 1.05 | 8.03 | 4.72 | 5.10 |
| reversed-0.2 | 4 | 39 | 1.065 | 0.961 | 1.75 | 2.32 | 1.41 | 1.28 |

- Trên panel thật, pp chạy được ở cả 4 khai báo, mỗi lần dưới 5 s.
- f_pp nhỏ hơn bank factor của v5.1 ở cả 4 khai báo, và giảm khi khai báo nhiều cạnh thiếu hơn, đúng mẫu hình mô phỏng.
- Kết hợp với 4.4 (lag1: coverage pp 0.81–0.91): interval pp trên panel thật nhiều khả năng **quá hẹp**. Không nên dùng nó thay cho bank factor của mô phỏng.

### 4.6 Thời gian

- Mỗi dataset tốn khoảng **4.8–5.6 lần** v5.1 một mình (median theo cell).
- Theo nhánh: v3 (none, extra, reversed) mất 2–3.8 s; targeted mất 6.7–17.6 s, dưới máy bị chia.
- Con số 4.7× trong đề xuất là đúng. Ước lượng 3–5 h cho grid 9 cell thì quá bi quan: thực tế 21 phút cho 540 dataset.

### 4.7 Kết luận cho Paper 4

1. Hướng "bỏ bank factor bằng double bootstrap theo dataset" **bị loại** theo quy tắc ghi trước (0/9 non-inferior, coverage 1/9). Bank factor của bước [6] vẫn là thành phần cần thiết. Câu trả lời cho reviewer hỏi "factor có ad hoc không" giờ có bằng chứng: phương án hiệu chỉnh nội tại chuẩn mực nhất (Beran/Loh) chỉ đạt coverage 0.82–0.88 ở mọi cell hỏng có T ≤ 80, thấp hơn v5.1 từ 0.065 đến 0.12, vì nó không thấy damage chưa được phát hiện.
2. Phát hiện phụ dùng được cho paper: **f_d bằng khoảng 0.65–0.9 lần bank factor, và giảm theo mức hỏng khai báo** (Spearman −0.62). Điều này cho thấy phần lớn bank factor đang bù cho **bias cấu trúc** (cạnh thiếu chưa phát hiện, chiều sai), không phải cho sai số mẫu nhỏ. Đây là một lập luận định lượng cho việc vì sao factor phải tune theo (T, loại hỏng khai báo).
3. Nếu muốn làm tiếp, cần một **phiên bản mới với quy tắc mới**, không sửa bản này. Hướng hợp lý là để double bootstrap chỉ tính phần sai số mẫu nhỏ, còn một thành phần riêng cho damage chưa phát hiện. Ví dụ: một bước tạo thêm damage giả trong thế giới bootstrap, tức xoá thêm k cạnh của mô hình đã fit trước khi sinh dữ liệu tầng trong. Chưa thử.

**Bug trong file có sẵn:** không phát hiện bug mới. Lưu ý thiết kế (không phải bug): `tolerant` và `tolerant_sel_dd` tính reversal pool và (ở nhánh v3) repair candidates **một lần trên dữ liệu**, rồi chỉ rút ngẫu nhiên trong từng draw. Vì vậy câu "bước (1)–(4) được làm lại trong mọi draw" chỉ đúng hoàn toàn cho phần opening và repair của nhánh targeted.

**Frozen spec:** không có, vì candidate không đạt.
