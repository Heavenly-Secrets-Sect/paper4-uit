# Hướng `metrics`: đặc trưng sai số RQ4.1 và cờ tin cậy RQ4.4 cho module (bản thăm dò)

**Trạng thái.** Exploratory, chỉ dùng D-07 development (đánh giá) và hệ số width đã hiệu chỉnh trên D-07H development. Không có phương pháp ước lượng mới. Module là `tolerant_v4` đã đóng băng.

**File của hướng này** (không sửa file nào có sẵn):

| File | Vai trò |
|---|---|
| `experiments/configs/ext_metrics_pairs.json` | Config của thực nghiệm pair-level |
| `experiments/ext/metrics/run_pairs.py` | Chạy lại đúng seed của `a2_baselines` / `a2b_pselect`, lưu từng cặp |
| `experiments/ext/metrics/aggregate_rq41.py` | Gộp các kết quả đã có (run-level) thành bảng RQ4.1 |
| `experiments/ext/metrics/analyze_pairs.py` | Bảng RQ4.1 theo lag thật và vai trò cặp; phân tích cờ RQ4.4 |
| `results/ext_metrics_pairs/`, `results/ext_metrics_rq41/`, `results/ext_metrics_flags/` | Kết quả |

## Đăng ký trước (viết TRƯỚC khi chạy `ext_metrics_pairs`)

### Vì sao cần thực nghiệm mới

`run_experiment.py` chỉ lưu một hàng mỗi run, với median trên các cặp. Breakdown theo **lag thật của cặp** và theo **vai trò của cặp so với cạnh hỏng** không dựng được từ các hàng đó. `run_pairs.py` chạy lại **đúng** seed của `a2_baselines` (unit seed, skeleton hỏng, dữ liệu, rng của từng method đều trùng), nên mọi số gộp phải khớp với kết quả đã lưu.

Probe thời gian (3 unit, lưu ở `results/ext_metrics_pairs_probe/`, không dùng để kết luận): 420/420 số đếm `n_covered_nonnull` và `n_nonnull` khớp đúng với `a2_baselines` / `a2b_pselect`. **Điều kiện hợp lệ:** ở lượt chạy đầy đủ, mọi số đếm này phải khớp 100%; nếu không, lượt chạy bị coi là hỏng và báo lại như vậy.

### Thiết kế

- Bank D-07 development, 20 topology × 3 replicate, seed_base 20261102 (ghép cặp với `a2_baselines`).
- T ∈ {40, 80, 150}; ô hỏng: none, extra / missing / reversed × {0.2, 0.5}. H = 4, lag_max = 2, n_boot = 199, tau = 0.1.
- Methods: `oracle` (tham chiếu), `plugin`, `lp_allpast`, `ida_union`, `bvar_minnesota`, `pselect_union`, `tolerant_v4`.
- Hệ số width của module đọc từ `results/a2_baselines/calibration.json` (hiệu chỉnh trên D-07H development bởi runner với cùng config), nên trùng với hệ số đã dùng trong `a2_baselines`.
- Ô GES (`a3_ges`) và các kịch bản biến ẩn / nhiễu đo **không** chạy lại ở mức cặp; chúng chỉ có trong bảng run-level.

**Nhãn phía truth (chỉ phần đánh giá đọc):**

- `direct_lag` của cặp i → j: lag của cạnh trực tiếp i → j trong đồ thị thật (0, 1, 2), hoặc "không có cạnh trực tiếp" (hiệu ứng chỉ đi qua nút khác).
- `role`:
  - `damaged`: chính cạnh của cặp bị hỏng (bị xóa, bị đảo, hoặc là cạnh thừa được thêm);
  - `downstream`: có đường đi i ⇝ a → b ⇝ j qua một cạnh hỏng a → b (với extra: theo chiều của cạnh thừa trong skeleton hỏng);
  - `untouched`: còn lại.

### RQ4.1: sẽ báo cáo gì (mô tả, không có quy tắc đạt / không đạt)

1. **Bảng run-level từ kết quả đã có** (`aggregate_rq41.py`): `a2_baselines`, `a2b_pselect`, `rq42_v4` (thêm T = 300), `rq42_v4_heldout`, `a1_latent_noise`, `a3_ges`. Theo (T × loại hỏng × mức hỏng × method): sai số tuyệt đối và tương đối của C(H), tỷ lệ sai dấu, tỷ lệ mất hiệu ứng, sai số mean lag, peak-lag hit, coverage, width, interval score. Các số này là median của median theo run, giống `summary.md`.
2. **Bảng pair-level** (`analyze_pairs.py`): cùng các metric, gộp trực tiếp trên cặp, chia theo `role` và theo `direct_lag`, cho `plugin`, `tolerant_v4` và các baseline đã công bố.
3. **Null pairs:** tỷ lệ cặp null (|C| ≤ 0.1) có interval không chứa 0 ("tín hiệu giả").

**Dự đoán ghi trước** (để đối chiếu, không phải quy tắc):

- E1. Với missing, sai số của `plugin` dồn vào cặp `damaged` (hiệu ứng bị mất, báo [0, 0]); coverage của cặp `downstream` cũng giảm nhưng ít hơn.
- E2. Với missing, ở T ≥ 80, coverage của `tolerant_v4` trên cặp `damaged` có cạnh lag 0 thấp hơn cặp có cạnh lag 1–2. Lý do: cạnh có lag được khôi phục chắc chắn nhờ "mọi lag", còn cạnh cùng kỳ phụ thuộc bước repair theo tương quan phần dư.
- E3. Với reversed, cặp `damaged` đều có lag 0 (theo cách tạo hỏng). Sai dấu và lệch của `plugin` dồn vào các cặp `damaged` và `downstream`.
- E4. Sai số mean lag của `plugin` khi missing lớn hơn ở cặp có đường đi qua cạnh hỏng.

### RQ4.4: quy tắc ghi trước

**Biến cần dự báo (chính):** `miss` = interval của `tolerant_v4` không chứa C thật (cặp non-null).
**Biến phụ:** `large_err` = |Ĉ − C| > 0.5 |C| (để nối với `results/rq44_flags`).

**Tín hiệu (không cần truth), chiều giả định: giá trị lớn hơn thì rủi ro cao hơn.**

| Tín hiệu | Mức | Định nghĩa |
|---|---|---|
| `rel_width` | cặp | width / \|Ĉ\| |
| `width` | cặp | width |
| `zero_in` | cặp | 1 nếu interval chứa 0 |
| `struct_sens` | cặp | \|Ĉ_module − Ĉ_plugin\| / width |
| `resid_lb` | cặp | max Ljung-Box Q(4) của phần dư cấu trúc ở hai phương trình đầu mút (base fit của module) |
| `rx_pair` | cặp | \|corr\| phần dư cấu trúc của hai đầu mút |
| `rx_end` | cặp | max \|corr\| giữa phần dư của một đầu mút và phần dư của nút mà skeleton coi là không kề |
| `coef_stab` | cặp | \|Ĉ_A − Ĉ_B\| / width; A, B là 60% đầu và 60% cuối chuỗi (plan: độ ổn định hệ số) |
| `lag_stab` | cặp | \|mean lag_A − mean lag_B\| (plan: độ ổn định lag) |
| `n_repair` | fit | `info_n_repair`: số cạnh cùng kỳ được thêm lại |
| `n_pool` | fit | kích thước reversal pool (0 khi không khai báo đảo) |
| `n_resid_bh` | fit | số cặp không kề có tương quan phần dư ý nghĩa (BH, q = 0.1), không giới hạn (chẩn đoán phần dư) |

**Tập đánh giá chính:** T ∈ {80, 150}, gộp 7 ô hỏng. T = 40 báo riêng. Tín hiệu không xác định ở một cặp (ví dụ `coef_stab` khi cửa sổ không fit được) thì cặp đó bị bỏ khỏi AUROC của tín hiệu đó; tỷ lệ xác định được báo kèm.

**Thống kê:**

- AUROC gộp (Mann–Whitney, rank trung bình cho ties).
- AUROC phân tầng: trung bình có trọng số (theo số cặp) của AUROC trong từng (T, ô hỏng), chỉ trên các tầng mà tín hiệu có ít nhất 2 giá trị khác nhau. Phân tầng loại bỏ phần AUROC đến từ chênh lệch tỷ lệ miss giữa các ô.
- CI 95%: bootstrap theo cụm topology (20 cụm, 1000 lần lấy lại, percentile).
- Tín hiệu kết hợp: logistic (Newton, ridge 1e-3) trên log1p của các tín hiệu liên tục không âm, `rx_pair`, `rx_end`, `zero_in`, ba tín hiệu mức fit, chỉ báo thiếu giá trị của `coef_stab` / `lag_stab` (điền median của fold train), log T và loại hỏng khai báo (đều quan sát được). Đánh giá bằng 5-fold cross-validation **theo nhóm topology** (fold = chỉ số topology mod 5); AUROC tính trên điểm out-of-fold. CI bootstrap theo cụm trên điểm out-of-fold, không fit lại.

**Quy tắc:**

- **R1 (từng tín hiệu).** Một tín hiệu **dự báo được** miss của module nếu cận dưới CI 95% của **cả** AUROC gộp **và** AUROC phân tầng đều > 0.5. Nó **hữu ích** nếu thêm điều kiện AUROC gộp ≥ 0.65. Nếu cận trên CI < 0.5, báo là **quan hệ ngược chiều**.
- **R2 (kết hợp).** Tín hiệu kết hợp **thêm thông tin ngoài `rel_width`** nếu CI 95% của ΔAUROC = AUROC(kết hợp, out-of-fold) − AUROC(`rel_width`) có cận dưới > 0 (bootstrap cặp theo cụm).
- **R3 (ngưỡng cố định, ghi trước).** Cờ `rel_width > 2` (ngưỡng ví dụ ở `docs/ket_qua_rq44.md`). Báo: tỷ lệ cặp bị cờ, tỷ lệ miss trong nhóm có cờ và không cờ, tỷ số hai tỷ lệ (CI theo cụm), coverage của nhóm không cờ. Cờ **dùng được** nếu tỷ số ≥ 2 và cận dưới CI > 1.
- Các tiêu chí trên áp dụng y hệt cho `large_err` và báo cạnh nhau, nhưng kết luận chính dựa trên `miss`.
- Mô tả thêm (không có quy tắc): coverage của module theo ngũ phân vị của `rel_width` (conditional coverage).

**Dự đoán ghi trước:** `rel_width` dự báo `large_err` tốt (như `rq44_flags`, AUROC khoảng 0.8), nhưng dự báo `miss` kém hơn nhiều, có thể gần 0.5 hoặc ngược chiều. Lý do: interval đã hiệu chỉnh tự nới rộng ở các cặp khó, nên miss không dồn vào chỗ interval rộng tương đối.

## Kết quả (thêm vào sau khi chạy; phần đăng ký ở trên giữ nguyên)

**Ghi chú minh bạch.** Sau khi viết phần đăng ký và trước lượt chạy đầy đủ, code phân tích (`analyze_pairs.py`) được chạy thử trên dữ liệu probe (1 topology × 3 replicate) để bắt lỗi. Quy tắc không đổi sau bước này. `posthoc.py` được viết **sau khi** xem kết quả; mọi số của nó được ghi là post-hoc.

**Lượt chạy.** `ext_metrics_pairs`: 60 unit, 259 560 hàng cặp, 796 s với `--workers 3` (dưới 15 phút, không cần thu nhỏ lưới). **Điều kiện hợp lệ đạt:** 8 400 run được so với `a2_baselines` / `a2b_pselect`, **0 lệch** (`results/ext_metrics_pairs/check.txt`). Mọi số pair-level dưới đây vì thế là cùng dữ liệu, cùng skeleton và cùng interval với các bảng A2 đã công bố trong repo.

### RQ4.1-a. Bảng run-level từ kết quả đã có

Bảng đầy đủ (mọi T, mọi ô, mọi method, cả held-out, GES, biến ẩn và nhiễu đo): `results/ext_metrics_rq41/tables.md`. Trích D-07 development, T = 150 (`a2_baselines` + `a2b_pselect`). Các cột: abs / rel = sai số tuyệt đối / tương đối của C(H); sign = tỷ lệ sai dấu; lost = tỷ lệ hiệu ứng bị báo bằng 0; mean-lag = sai số mean lag; peak = peak-lag hit; cov; width; IS.

| Hỏng | Method | abs | rel | sign | lost | mean-lag | peak | cov | width | IS |
|---|---|---|---|---|---|---|---|---|---|---|
| none | `plugin` | 0.19 | 0.16 | 0.01 | 0.00 | 0.17 | 0.82 | 0.93 | 1.07 | 1.58 |
| none | `pselect_union` | 0.22 | 0.18 | 0.03 | 0.00 | 0.19 | 0.76 | 0.98 | 1.70 | 2.03 |
| none | **`tolerant_v4`** | 0.19 | 0.16 | 0.01 | 0.00 | 0.17 | 0.82 | 0.96 | 1.28 | 1.56 |
| missing 0.5 | `plugin` | 0.73 | 1.00 | 0.15 | 0.40 | 0.22 | 0.56 | 0.33 | 1.00 | 29.07 |
| missing 0.5 | `ida_union` | 0.75 | 1.00 | 0.14 | 0.40 | – | – | 0.36 | 1.30 | 28.33 |
| missing 0.5 | `bvar_minnesota` | 0.51 | 0.49 | 0.05 | 0.00 | 0.25 | 0.66 | 0.57 | 1.13 | 10.18 |
| missing 0.5 | `pselect_union` | 0.27 | 0.24 | 0.06 | 0.00 | 0.20 | 0.66 | 0.91 | 1.65 | 3.11 |
| missing 0.5 | **`tolerant_v4`** | 0.26 | 0.24 | 0.03 | 0.00 | 0.21 | 0.70 | 0.96 | 1.76 | 2.22 |
| reversed 0.5 | `plugin` | 0.26 | 0.25 | 0.04 | 0.00 | 0.21 | 0.68 | 0.74 | 1.07 | 5.12 |
| reversed 0.5 | `ida_union` | 0.25 | 0.23 | 0.03 | 0.00 | – | – | 0.85 | 1.32 | 3.70 |
| reversed 0.5 | `pselect_union` | 0.30 | 0.26 | 0.06 | 0.00 | 0.22 | 0.64 | 0.89 | 1.73 | 3.50 |
| reversed 0.5 | **`tolerant_v4`** | 0.25 | 0.23 | 0.02 | 0.00 | 0.21 | 0.68 | 0.96 | 1.58 | 2.02 |

Các điểm khác từ bảng đầy đủ:

- **T = 300** (`rq42_v4`, mẫu khác seed): missing 0.5, `plugin` vẫn rel 1.00, lost 0.41, coverage 0.30; module rel 0.17, coverage 0.95. **Tăng T không sửa được sai số do skeleton thiếu cạnh**, chỉ sửa phần sai số lấy mẫu.
- **Sai số lag chịu tác động ít hơn sai số cường độ.** Với `plugin` ở T = 80, mean-lag error là 0.24 khi không hỏng và 0.25–0.27 ở các ô missing; peak-lag hit giảm từ 0.73 xuống 0.51. Cường độ thì sụp (rel 0.24 → 1.00). Ở mức run, phần lớn thiệt hại nằm ở **cường độ và coverage**, không ở lag. Mục RQ4.1-b cho thấy kết luận này đổi khi nhìn riêng các cặp bị hỏng.
- **T = 40, missing:** sai số điểm của module **lớn hơn** `plugin` (abs 0.82 so với 0.59 ở missing 0.2), peak hit thấp hơn (0.37 so với 0.56). Đây là cái giá của việc đưa mọi lag vào khi T nhỏ. Module đổi lại bằng coverage (0.98 so với 0.65).
- **`pselect_union` ở T = 40 báo 0 cho 27.5% hiệu ứng non-null, ngay cả khi skeleton đúng** (lost 0.275, rel 1.00). Ước lượng điểm của nó lấy từ đồ thị chọn lại chưa nhiễu, và ở T nhỏ bước chọn bỏ sót cạnh. Interval union của nó vẫn phủ 0.85–0.89. Tức là baseline này có interval dùng được nhưng **ước lượng điểm không dùng được ở T = 40**.
- **GES** (`a3_ges`, T = 150): `plugin` abs 0.73, mean-lag 0.33, peak 0.40; module abs 0.30, mean-lag 0.21, peak 0.64. Ở đây module cải thiện cả lag, không chỉ coverage.
- **Held-out P4-H1 confirmatory** (`rq42_v4_heldout`, chỉ đọc lại số đã lưu), T = 150, missing 0.5: `plugin` abs 0.75 / cov 0.34; module abs 0.28 / cov 0.96. Cùng mẫu hình với development.

### RQ4.1-b. Pair-level: theo vai trò của cặp (`results/ext_metrics_pairs/rq41_pairs.md`, bảng A)

Trích T = 150. Ô ghi: rel / mean-lag / peak / cov / IS.

| Hỏng | Vai trò (n) | `plugin` | `bvar_minnesota` | `pselect_union` | **`tolerant_v4`** |
|---|---|---|---|---|---|
| missing 0.5 | damaged (655) | 1.00 / 0.87 / 0.15 / 0.01 / 54.0 | 0.65 / 0.24 / 0.56 / 0.15 / 19.9 | 0.24 / 0.21 / 0.58 / 0.83 / 4.35 | **0.21 / 0.18 / 0.70 / 0.96 / 2.30** |
| missing 0.5 | downstream (665) | 1.00 / 0.27 / 0.54 / 0.22 / 24.9 | 0.51 / 0.30 / 0.61 / 0.70 / 5.53 | 0.29 / 0.20 / 0.66 / 0.93 / 2.59 | **0.30 / 0.26 / 0.63 / 0.97 / 2.25** |
| missing 0.5 | untouched (534) | 0.19 / 0.16 / 0.74 / 0.86 / 2.87 | 0.21 / 0.23 / 0.85 / 0.92 / 2.06 | 0.18 / 0.18 / 0.79 / 0.97 / 1.92 | 0.20 / 0.21 / 0.79 / 0.96 / 2.02 |
| reversed 0.5 | damaged (193) | 0.61 / 0.86 / 0.05 / 0.26 / 15.9 | 0.65 / 0.76 / 0.07 / 0.24 / 16.7 | 0.64 / 0.84 / 0.05 / 0.45 / 10.9 | **0.33 / 0.86 / 0.05 / 0.93 / 3.00** |
| reversed 0.5 | downstream (389) | 0.58 / 0.33 / 0.54 / 0.46 / 11.1 | 0.58 / 0.32 / 0.55 / 0.52 / 9.83 | 0.51 / 0.27 / 0.54 / 0.83 / 4.71 | **0.39 / 0.33 / 0.54 / 0.90 / 2.59** |
| reversed 0.5 | untouched (1272) | 0.18 / 0.16 / 0.81 / 0.90 / 1.83 | 0.23 / 0.25 / 0.83 / 0.91 / 1.99 | 0.20 / 0.18 / 0.76 / 0.97 / 1.97 | 0.19 / 0.16 / 0.81 / 0.98 / 1.63 |

`ida_union` ở reversed 0.5 damaged: rel 0.50, cov 0.54, IS 10.6.

**Đối chiếu với dự đoán ghi trước:**

- **E1 đúng.** Với missing, `plugin` gần như không phủ cặp `damaged`: coverage 0.012–0.050 ở T = 80 và 150, lost 0.24 (missing 0.2) đến 0.65 (missing 0.5). Cặp `downstream` cũng sụp, coverage 0.22–0.42. Mức sụp ít hơn cặp `damaged` nhưng vẫn rất nặng. Như vậy lỗi một cạnh lan sang mọi hiệu ứng đi qua cạnh đó: ở missing 0.5 có 665 cặp `downstream` so với 655 cặp `damaged`.
- **E3 đúng, và kèm một phát hiện về module.** Ở reversed, các cặp `damaged` đều có lag 0. Với `plugin`, mean-lag error là 0.86 và peak hit 0.05: hiệu ứng cùng kỳ bị báo thành hiệu ứng trễ (`oracle`: peak hit 0.92). **Module có đúng các con số lag này (0.86 / 0.05)**, dù cường độ đã được sửa (rel 0.33, cov 0.93). Lý do nằm ở code: `tolerant()` trả `theta` của fit trên skeleton nhận được khi không có cạnh repair, nên **output lag của module khi khai báo đảo chính là của `plugin`**. Đây không phải bug theo nghĩa code chạy sai, mà là một lỗ hổng thiết kế, cần ghi trong bài. Hướng sửa (chưa làm, vì hướng này không đề xuất method mới): báo lag từ các draw cấu trúc giống như C(H).
- **E4 đúng.** Với missing 0.5, mean-lag error của `plugin` là 0.87–1.04 ở cặp `damaged`, 0.27–0.34 ở `downstream` và 0.16–0.21 ở `untouched` (T = 80 và 150). Kết luận "lag ít bị ảnh hưởng" ở mức run chỉ đúng **trung bình**. Trên các cặp chịu hỏng trực tiếp, lag sai nặng.
- **Cái giá của module trên cặp không bị chạm:** ở missing 0.2, T = 80, cặp `untouched` có abs err 0.40 với module so với 0.29 với `plugin`, width 2.58 so với 1.39. Nguyên nhân là module mở mọi lag cho mọi phương trình. Coverage của nó trên các cặp này là 0.95, của `plugin` là 0.86.

### RQ4.1-c. Theo lag thật của cạnh bị xóa (E2; bảng C, CI theo cụm topology)

Coverage trên cặp có cạnh trực tiếp bị xóa, chia theo cạnh đó là cùng kỳ (lag 0) hay có lag (1–2):

| T | Hỏng | `tolerant_v4` lag 0 / lag 1–2 (hiệu [CI]) | `pselect_union` lag 0 / lag 1–2 (hiệu [CI]) |
|---|---|---|---|
| 40 | missing 0.5 | 0.943 / 0.978 (−0.035 [−0.070, −0.000]) | 0.622 / 0.872 (−0.251 [−0.313, −0.180]) |
| 80 | missing 0.2 | 0.924 / 0.969 (−0.045 [−0.137, +0.024]) | 0.582 / 0.925 (−0.343 [−0.456, −0.224]) |
| 80 | missing 0.5 | 0.912 / 0.961 (−0.049 [−0.098, −0.009]) | 0.549 / 0.918 (−0.369 [−0.433, −0.298]) |
| 150 | missing 0.2 | 0.949 / 0.956 (−0.007 [−0.054, +0.036]) | 0.570 / 0.963 (−0.393 [−0.484, −0.304]) |
| 150 | missing 0.5 | 0.938 / 0.970 (−0.032 [−0.058, −0.008]) | 0.497 / 0.972 (−0.474 [−0.543, −0.404]) |

- **E2 đúng về chiều, nhưng nhỏ với module.** Hiệu −0.01 đến −0.05; CI loại trừ 0 ở các ô missing 0.5. Coverage của module trên cạnh cùng kỳ bị xóa vẫn ở mức 0.91–0.95.
- **Đây là phát hiện có giá trị nhất của mục này cho bài: cơ chế làm baseline mạnh nhất thua.** `pselect_union` chọn lại được adjacency, nhưng cặp mới chọn không có chiều, nên chỉ có hạng có lag. Kết quả là nó **mất hẳn hiệu ứng cùng kỳ** của cạnh bị xóa: coverage 0.50–0.62 trên cạnh lag 0, so với 0.87–0.97 trên cạnh có lag. Bước repair theo tương quan phần dư cấu trúc của module khôi phục được đúng phần này. Ở T = 150, missing 0.5, cạnh lag 0: module có IS 3.30 và coverage 0.94; `pselect_union` có IS 10.03 và coverage 0.50 (bảng B).

### RQ4.1-d. Cặp null: tín hiệu giả (bảng D)

Tỷ lệ cặp null có interval không chứa 0:

| T | Hỏng | `plugin` | `ida_union` | `bvar_minnesota` | `pselect_union` | **`tolerant_v4`** |
|---|---|---|---|---|---|---|
| 80 | none | 0.036 | 0.010 | 0.008 | 0.001 | 0.005 |
| 150 | missing 0.5 | 0.022 | 0.010 | 0.019 | 0.004 | 0.020 |
| 150 | reversed 0.5 | 0.130 | 0.069 | 0.072 | 0.029 | **0.004** |

Ở mọi ô, module báo tín hiệu giả ở mức 0.2–2.0%. Mức này thấp hơn `plugin` ở mọi ô, và đặc biệt thấp khi skeleton bị đảo (`plugin` lên tới 13%). `pselect_union` thấp nhất ở hầu hết ô, vì interval union rộng.

### RQ4.4. Cờ tin cậy cho module (`results/ext_metrics_flags/summary.md`)

**T ∈ {80, 150}, outcome chính `miss`** (25 956 cặp, base rate 0.045):

| Tín hiệu | AUROC gộp [CI] | AUROC phân tầng [CI] | R1 |
|---|---|---|---|
| `rel_width` | 0.660 [0.619, 0.702] | 0.656 [0.616, 0.695] | **hữu ích** (vừa qua ngưỡng 0.65) |
| `zero_in` | 0.623 [0.592, 0.655] | 0.608 [0.580, 0.638] | dự báo được |
| `width` | 0.368 [0.326, 0.417] | 0.333 [0.289, 0.379] | **ngược chiều** |
| `resid_lb` | 0.453 [0.421, 0.485] | 0.452 [0.421, 0.483] | ngược chiều (yếu) |
| `struct_sens` | 0.496 [0.467, 0.528] | 0.538 [0.504, 0.571] | không |
| `rx_pair`, `rx_end` | 0.514, 0.507 | 0.497, 0.486 | không |
| `coef_stab` | 0.491 [0.464, 0.517] | 0.493 | không |
| `lag_stab` (xác định ở 47% cặp) | 0.549 [0.493, 0.592] | 0.552 [0.506, 0.588] | không |
| `n_repair`, `n_pool`, `n_resid_bh` | 0.479, 0.511, 0.486 | 0.467, 0.508, 0.496 | không |
| Kết hợp (CV 5-fold theo topology) | **0.741 [0.702, 0.776]** | 0.728 | **R2: ΔAUROC = +0.081 [+0.044, +0.119], thêm thông tin** |

- **R3:** cờ `rel_width > 2` gắn cho 42.9% cặp. Tỷ lệ miss là 0.069 ở nhóm có cờ, 0.026 ở nhóm không cờ; tỷ số 2.60 [2.05, 3.38], tức là **dùng được**. Coverage của nhóm không cờ là 0.974.
- **Outcome phụ `large_err`** (base rate 0.217): `rel_width` 0.858 [0.844, 0.871]; kết hợp 0.860, ΔAUROC +0.002 [−0.001, +0.004], tức là không thêm gì. R3: tỷ số 6.76 [6.05, 7.59].
- **T = 40, `miss`** (12 978 cặp, base rate 0.062): `rel_width` 0.595 [0.569, 0.628], dự báo được nhưng không hữu ích; `width` 0.181, ngược chiều mạnh; kết hợp 0.847 [0.815, 0.878], ΔAUROC +0.252 [+0.200, +0.296]. R3 **không dùng được**: 85.5% cặp bị cờ, tỷ số 1.64 [1.19, 2.45].

**Coverage có điều kiện theo ngũ phân vị của `rel_width`, T ∈ {80, 150}:** 0.975 / 0.975 / 0.969 / 0.953 / **0.904**. Ở T = 40: 0.962 / 0.956 / 0.941 / 0.919 / 0.914. Coverage gộp đúng danh nghĩa che đi việc module **phủ thiếu ở nhóm cặp có hiệu ứng nhỏ so với độ rộng**.

**Đối chiếu dự đoán ghi trước:** đúng một nửa. `rel_width` dự báo `miss` kém hơn `large_err` nhiều (0.66 so với 0.86), đúng như dự đoán, nhưng **không** về gần 0.5.

**Đọc kết quả:**

1. **Các chẩn đoán mà plan liệt kê (độ ổn định hệ số, phần dư, độ ổn định lag) không dự báo được miss của module.** Mọi AUROC đều nằm trong khoảng 0.45–0.55. Đây là **kết quả âm**, cần báo đúng như vậy. Cùng với `struct_sens` ≈ 0.5 (giống `rq44_flags`), nó cho thấy phần bất định về cấu trúc mà các chẩn đoán này đo được đã nằm sẵn trong độ rộng interval của module.
2. **Thông tin còn lại nằm ở độ hẹp tuyệt đối của interval.** `width` ngược chiều với giả định: interval **hẹp** mới hay trượt. Mô hình kết hợp học được chiều này qua cross-validation (trọng số chuẩn hóa của log1p width là −0.75 ở T 80/150, −1.84 ở T 40). Đây là lý do nó thắng `rel_width`.
3. **Hệ quả cho cờ tin cậy ở Bài 5:** dùng `rel_width > 2` ở T ≥ 80 (đơn giản, dùng được). Ở T = 40, ngưỡng cố định không dùng được; cần cờ hai phía (interval rất hẹp **hoặc** rộng tương đối), hay mô hình kết hợp. Mô hình kết hợp mới chỉ được kiểm tra bằng CV trên D-07 development, chưa có held-out.

**Post-hoc, không đăng ký trước** (`results/ext_metrics_flags/posthoc.md`):

- Tỷ lệ miss theo ngũ phân vị width, từ hẹp đến rộng: ở T = 80/150 là 0.070 / 0.060 / 0.045 / 0.033 / 0.015; ở T = 40 là 0.190 / 0.072 / 0.025 / 0.015 / 0.007. AUROC của 1/width là 0.632 (T 80/150) và 0.819 (T 40).
- Miss tăng theo |C thật|: 0.030 / 0.049 / 0.055 theo tam phân vị ở T 80/150. Giả thuyết (chưa kiểm): bias mẫu nhỏ trên hiệu ứng mạnh, mà percentile bootstrap không sửa được.
- **Module phủ thiếu trên cặp chịu đảo chiều.** Miss rate ở reversed `damaged` là 0.120 và `downstream` là 0.108 (T 80/150); ở T = 40, `damaged` là 0.211. Cặp `untouched` của cùng ô chỉ 0.030. Coverage gộp của ô reversed (0.93–0.96) che đi lỗ hổng này. Đây là limitation thứ hai, sau output lag, của nhánh xử lý đảo chiều.

### Kết luận được phép viết

> RQ4.1: Lỗi skeleton làm hỏng chủ yếu **cường độ và coverage** của các cặp có cạnh hỏng **và của mọi cặp nằm sau cạnh đó**. Ở các cặp này, lag cũng sai nặng: peak-lag hit 0.05–0.15 với `plugin`. Tăng T không sửa được. Module khôi phục cường độ và coverage ở cả cặp hỏng lẫn cặp phía sau. Nó khôi phục được cả hiệu ứng cùng kỳ của cạnh bị xóa, phần mà baseline chọn lại adjacency (`pselect_union`) mất. Khi skeleton bị đảo, module **không** sửa được lag, và phủ thiếu trên các cặp đi qua cạnh bị đảo (khoảng 0.88–0.90).

> RQ4.4: Ở T ≥ 80, độ rộng tương đối là cờ đơn giản dùng được: AUROC 0.66 cho miss và 0.86 cho lệch lớn. Ngưỡng 2 tách miss rate 2.6 lần. Các chẩn đoán phần dư và độ ổn định theo cửa sổ không mang thêm thông tin.

### Giới hạn

- Chỉ dùng D-07 development. Mô hình logistic kết hợp mới được đánh giá bằng CV theo topology, chưa có held-out (mọi split đã dùng một lần).
- Ô GES, biến ẩn và nhiễu đo chỉ có ở bảng run-level, không có pair-level.
- Lag của module khi khai báo thiếu cạnh lấy từ fit với **một** lần rút chiều ngẫu nhiên cho cạnh repair (`fit` trong `tolerant()`), nên sai số lag của module ở các ô này có thêm nhiễu.
- `coef_stab` và `lag_stab` dùng base terms của module, không có cạnh repair; ở T = 40 cửa sổ thường không fit được (`coef_stab` chỉ xác định ở 43% cặp).
- Các số run-level là median của median, giống mọi `summary.md`.

## Sửa sau kiểm chứng vòng 1

(Append ở vòng 2 bởi hướng `revlag`, theo R2-10 trong `docs/ext/synthesis_round1.md`. Phần trên giữ nguyên; các câu dưới đây thay cho câu tương ứng ở trên.)

1. **Thời điểm smoke-test.** Câu "Sau khi viết phần đăng ký và trước lượt chạy đầy đủ, code phân tích (`analyze_pairs.py`) được chạy thử trên dữ liệu probe" (mục "Ghi chú minh bạch") **sai về thời điểm**. Verifier đối chiếu timestamp: `analyze_pairs.py` được sửa lần cuối lúc 01:27:16, **sau khi** lượt chạy đầy đủ `ext_metrics_pairs` đã bắt đầu (khoảng 01:25). Câu đúng: code phân tích được chạy thử trên dữ liệu probe và sửa lỗi **trong khi** lượt chạy đầy đủ đang chạy, trước khi có kết quả của nó. Không có thay đổi rule nào sau khi có kết quả (01:38:26).
2. **`resid_lb` là quan hệ ngược chiều, không phải "không mang thông tin".** Câu "Mọi AUROC đều nằm trong khoảng 0.45–0.55" và câu kết luận RQ4.4 "Các chẩn đoán phần dư và độ ổn định theo cửa sổ không mang thêm thông tin" phải sửa: `resid_lb` có AUROC 0.453 [0.421, 0.485], cận trên CI < 0.5, tức là **ngược chiều** (đúng như bảng đã ghi, nhưng phần "Đọc kết quả" nói sai). Với outcome `large_err`, `lag_stab` có dự báo (0.588). Câu đúng: **không chẩn đoán nào của plan dự báo miss theo chiều plan nêu**; `resid_lb` dự báo ngược chiều (yếu).
3. **"Hữu ích" của `rel_width` là sát biên.** AUROC 0.660 đạt ngưỡng 0.65 của R1 **chỉ ở điểm ước lượng**; CI [0.619, 0.702] chạm xa dưới 0.65. Câu "hữu ích (vừa qua ngưỡng 0.65)" và "độ rộng tương đối là cờ đơn giản dùng được: AUROC 0.66" phải đọc là: dự báo được (CI > 0.5), **hữu ích sát biên** (chỉ điểm ước lượng ≥ 0.65). Cờ R3 `rel_width > 2` ở T ≥ 80 vẫn đạt (2.60 [2.05, 3.38]).
4. **Cơ chế lag-0 của `pselect_union` thuộc bản chuyển thể trong repo.** Câu "Đây là phát hiện có giá trị nhất của mục này cho bài: cơ chế làm baseline mạnh nhất thua" phải thu hẹp: việc cặp được chọn lại chỉ có hạng có lag (mất hiệu ứng cùng kỳ) đến từ `src/paper4/methods.py` (`pselect_union.to_skel` đưa cặp được chọn vào mà không có hướng và không vào `s.undetermined`), tức là **thuộc tính của bản chuyển thể trong repo**, không phải điểm yếu của phương pháp Chang–Guo–Malinsky gốc. Không được trình bày như điểm yếu của baseline đã công bố.
5. **Chiều ngược của width và mô hình kết hợp là post hoc theo chiều** và chỉ có CV support; không được trình bày như cờ đã validate. Vòng 2 đã freeze một mô hình kết hợp trên các hàng D-07 vòng 1 và đánh giá một lần trên lượt chạy D-07 development mới (seed_base 30261102): xem `docs/ext/revlag.md` mục (c).
6. **"Module phủ thiếu trên cặp chịu đảo chiều" (post-hoc ở trên) và kết luận RQ4.1 "phủ thiếu trên các cặp đi qua cạnh bị đảo".** Verifier vòng 1 cho thấy oracle thô (skeleton đúng) miss các cặp theo định nghĩa role gần như ngang module (T80 0.162 so với 0.158), nên quy kết cho module bị bác ở vòng 1. Vòng 2 đo lại theo định nghĩa red team (|ΔC| ≥ θ) với rule ghi trước: xem `docs/ext/revlag.md` mục (a); kết luận ở đó thay cho câu quy kết ở đây.
7. **Lag dưới reversal.** Câu "Khi skeleton bị đảo, module **không** sửa được lag" vẫn đúng cho `tolerant_v4`. Version báo lag từ structural draw (`tolerant_v4L`) được đánh giá ở `docs/ext/revlag.md` mục (b).
