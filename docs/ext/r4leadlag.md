# Hướng "r4leadlag" (vòng 4): cổng lead-lag trên residual trước bước contemporaneous repair

**Trạng thái.** Exploratory. Đánh giá chỉ trên D-07 development (seed_base 20261102). Calibration và mọi design probe chỉ trên D-07H development. Không chạm P4-H2 (cả hai split), P4-H1 hay confirmatory split nào. Không gọi LLM. Không commit.

**File của hướng này (đều là file mới):**
- Method: `src/paper4/ext_r4leadlag.py`. Module đăng ký `tolerant_v5_1_leadlag` (variant A) và `tolerant_v5_1_leadlag_skel` (variant D). Nó import `ext_v51`, `ext_narrow`, `methods` và không sửa module nào.
- Driver và script: `experiments/ext/r4leadlag/`. Gồm `worker.py`, `drive.py`, `probe.py`, `probe_draws.py`, `analyze.py`, `test_r4leadlag.py`, `test_analyze.py`.
- Config: `experiments/configs/ext_r4leadlag_eval_{clean,latent,noise}.json`.
- Kết quả: `results/ext_r4leadlag_*`.

---

## 1. Nguồn và cơ chế

**Nguồn đã đọc (theo nội dung đã biết của các bài):**
- Haugh (1976, JASA 71:378–385). Hai chuỗi được prewhiten bằng mô hình univariate riêng. Cross-correlation r_uv(k) của hai residual khi đó xấp xỉ độc lập, mỗi cái ~ N(0, 1/m) dưới H0 "hai chuỗi độc lập". Statistic là S = m Σ_{|k|≤M} r_uv(k)², ~ χ²(2M+1). Bản small-sample dùng trọng số m/(m−|k|).
- Hong (1996, Biometrika 83:615–625). Tổng quát Haugh bằng kernel weighting k(j/M) và chuẩn hoá về N(0,1). Haugh tương ứng với truncated uniform kernel. Hong chứng minh kernel không đều (ví dụ Daniell) có power cao hơn khi cross-correlation giảm dần theo lag.
- Lipsitch, Tchetgen Tchetgen và Cohen (2010, Epidemiology 21:383–388). Đây là logic negative control: một "exposure" không thể gây ra outcome (ở đây là **lead** của chuỗi kia: tương lai không gây ra hiện tại). Nếu nó vẫn liên quan tới outcome, liên hệ đó phải đến từ confounding hoặc bias.

**Áp dụng vào v5_1.** Chỉ đổi step (3) (contemporaneous repair):
- v5_1 dùng BH (q = 0.1) trên correlation lag 0 của residual cấu trúc của fit f0 (skeleton + các lag block đã mở). Nó lấy tối đa k_miss cặp mạnh nhất.
- Một hidden common cause cũng để lại đúng dấu vết lag 0 như vậy. Vì thế v5_1 có thể thêm một cạnh contemporaneous giả giữa hai co-child.
- Giả thuyết: trong generator, latent là AR(1) với persistence 0.5–0.8, nên nó để lại cross-correlation ở lag khác 0. Một cạnh contemporaneous bị thiếu thì chỉ để lại dấu vết ở lag 0.
- Cổng (gate): Q = m Σ_{0<|l|≤M} (m/(m−|l|)) ρ_uv(l)², tham chiếu χ²(2M). M = 4 khi T ≤ 80, M = 6 khi T > 80. Đuôi χ² với df chẵn được tính đúng (tổng Poisson).
- Cặp BH-significant có p_Q < 0.05 bị gắn nhãn "confounded" và không được repair. Cặp BH-significant kế tiếp lấy chỗ, cho đến khi đủ k_miss hoặc hết danh sách.
- Cổng chạy trên dữ liệu và chạy lại trong mỗi bootstrap draw.
- Mọi thứ khác giữ nguyên: opening, reversal, prescale 0.5. Width factor được calibrate lại trên D-07H development sạch.

**Mức trung thành với nguồn:**
- Statistic là của Haugh, bản có trọng số small-sample, với lag 0 bị loại.
- Haugh gốc tham chiếu χ²(2M+1) vì có lag 0. Ở đây lag 0 bị loại nên dùng χ²(2M).
- Residual dùng là residual cấu trúc của fit nhiều biến, không phải residual univariate. Lựa chọn này là bắt buộc: residual univariate để lại cross-correlation ở lag khác 0 cho cả một cạnh contemporaneous thật, vì động học của hai chuỗi khác nhau.
- Không dùng kernel của Hong. Hong chỉ được trích như bản tổng quát hoá.

**Blind spot đã biết (phải nêu trong paper).** Dưới Gaussianity, một confounder white-noise (không persistent) tác động lên hai co-child ở cùng lag không phân biệt được với một cạnh contemporaneous.

---

## 2. Design probe trên D-07H development và tinh chỉnh trước khi ghi rule

Hai probe dưới đây đều chạy trên D-07H development, dùng unit seed của stream calibration (seed_base + 500000 + 1000·t_idx + rep). Cả hai chạy trước khi rule được ghi và trước mọi run D-07.

### 2.1 Probe 1: dữ liệu, không bootstrap (`probe.py` → `results/ext_r4leadlag_probe/probe.{md,json}`)

Thiết lập: 20 topology × 3 replicate; scenario clean / latent1 / latent3 / noise0.1; T 40 / 80 / 150; stated missing-0.2/0.5. Probe tính step (3) của v5_1 trên dữ liệu và áp cổng lên mọi cặp BH-significant.

Class theo truth:
- E0: cạnh contemporaneous thật bị xoá.
- EL: cạnh lag thật bị xoá.
- C: co-child, không phải cạnh.
- N: không thuộc loại nào.

Variant:
- **A**: thiết kế được giao.
- **B**: A sau khi prewhiten AR(2) từng residual.
- **C**: A với M = 2.
- **D**: A trên residual của fit chỉ gồm term của skeleton (không mở lag block), như `screen_pairs`.
- **E**: A chỉ trên các lag |l| > lag_max.

Kết quả chính (flag rate = tỉ lệ cặp BH-significant bị gắn nhãn):

| scen | T | flag C: A / D | flag E0: A / D | AUROC C vs E0: A / D | C được repair/run: v5_1 → A → D | E0 được repair/run: v5_1 → A → D |
|---|---|---|---|---|---|---|
| clean | 150 | – | 0.02 / 0.12 | – | 0 | 1.91 → 1.88 → 1.69 |
| latent1 | 80 | 0.04 / 0.17 | 0.00 / 0.06 | 0.41 / 0.61 | 0.19 → 0.18 → 0.16 | 1.42 → 1.42 → 1.32 |
| latent1 | 150 | 0.00 / 0.36 | 0.01 / 0.11 | 0.55 / 0.64 | 0.44 → 0.44 → 0.29 | 1.82 → 1.80 → 1.62 |
| latent3 | 80 | 0.00 / 0.12 | 0.00 / 0.05 | 0.48 / 0.62 | 0.76 → 0.76 → 0.67 | 1.24 → 1.24 → 1.18 |
| latent3 | 150 | 0.02 / 0.19 | 0.01 / 0.11 | 0.59 / 0.65 | 1.27 → 1.24 → 1.03 | 1.63 → 1.62 → 1.47 |

B, C và E không tốt hơn A: flag C ≤ 0.05 ở T ≥ 80, AUROC 0.36–0.63. Bảng đầy đủ nằm trong `results/ext_r4leadlag_probe/probe.md`.

**Đọc probe.**
- (i) Vấn đề có thật. v5_1 dùng 0.44 (latent1) và 1.27 (latent3) slot repair mỗi run cho cặp co-child ở T150.
- (ii) Variant A gần như không bao giờ gắn nhãn co-child (0–4%). Lý do cơ học: f0 đã mở lag block của cặp (cặp co-child có residual correlation nên được mở). Hơn nữa, residual của một VAR là prediction error: phần persistent của latent bị lag của chính các co-child hấp thụ, phần còn lại gần với innovation của latent, tức white noise. Đó chính là blind spot đã nêu.
- (iii) D giữ được một phần dấu vết (AUROC 0.61–0.65), nhưng gắn nhãn sai 11–12% cạnh E0 thật ở T150. Trên dữ liệu sạch, D làm mất 0.22 cạnh E0 được repair mỗi run.

### 2.2 Probe 2: nhãn theo bootstrap draw (`probe_draws.py` → `results/ext_r4leadlag_probe/probe_draws.{md,json}`)

Thiết lập: 10 topology D-07H × replicate 0, clean/latent1/latent3, T 80/150, missing-0.5, n_boot 49, chạy qua vòng unit của runner.

| scen | T | A: nhãn trên data / mỗi draw / draw có nhãn | D: nhãn trên data / mỗi draw / draw có nhãn | repair mỗi draw A / D |
|---|---|---|---|---|
| clean | 80 | 0.00 / 0.08 / 0.08 | 0.20 / 1.73 / 0.78 | 7.38 / 6.13 |
| clean | 150 | 0.00 / 0.08 / 0.07 | 0.70 / 2.20 / 0.84 | 7.88 / 6.16 |
| latent1 | 150 | 0.00 / 0.11 / 0.10 | 0.30 / 2.52 / 0.90 | 8.08 / 6.10 |
| latent3 | 150 | 0.10 / 0.13 / 0.12 | 0.70 / 2.81 / 0.90 | 8.85 / 7.20 |

**Đọc probe 2.** Bootstrap series sinh từ mô hình đã fit, không có latent. Mọi nhãn trong draw vì vậy là nhãn sai theo định nghĩa. Với D, residual chỉ gồm term của skeleton của bootstrap series bị rò phần lag của các block đã mở. Kết quả là D gắn nhãn khoảng 2 cặp mỗi draw, kể cả trên dữ liệu sạch, và giảm số repair mỗi draw khoảng 1.3–2.0.

### 2.3 Quyết định trước khi ghi rule

- **Variant A** (`tolerant_v5_1_leadlag`) là ứng viên được giao, ghi rule nguyên như đề xuất. Không đổi M, ngưỡng hay residual. Probe dự báo A gần như trơ.
- **Variant D** (`tolerant_v5_1_leadlag_skel`) là variant duy nhất có khả năng phân biệt trên probe. Nó được ghi rule **riêng**, với cùng các ngưỡng, như variant phụ. Lý do: để kiểm xem một cổng có chút thông tin có biến thành thay đổi IS hay không. Probe dự báo D gây hại trên clean.
- B, C, E bị loại ở mức probe và không chạy trên D-07. Toàn bộ năm variant đã thử được công bố ở đây.
- Không có tinh chỉnh nào khác.

---

## 3. Rule ghi trước (verbatim; ghi trước mọi run D-07 của hướng này)

**Comparator.** `tolerant_v5_1` với width factor frozen (`experiments/ext/v51/frozen_v4_v51.json`, có đủ các key `tolerant_v5_1|{40,80,150}|{none,extra,missing,reversed}`). File này được chép nguyên vào `experiments/ext/r4leadlag/frozen_r4leadlag.json`, cùng factor của A và D được tune trên D-07H development sạch (`drive.py calibrate`, kinds extra/missing/reversed × rates 0.2/0.5, 1 replicate, như `ext_v51_eval`). Oracle chỉ là tham chiếu mô tả.

**Run.**
- D-07 development, 20 topology × 3 replicate, seed_base 20261102, H = 4, n_boot 199, lag_max 2.
- Chạy qua `experiments/ext/r4leadlag/drive.py run`, dùng các hàm của runner. Có hai patch phía worker, runner không bị sửa:
  - (a) A và D dùng stream tag bootstrap của `tolerant_v5_1`, nên ở cell không có stated missing chúng trùng v5_1 từng bit, và ở cell missing ghép cặp theo cùng random number.
  - (b) evaluate thêm coverage cho co-child pair, và class theo truth cho các log của cổng. Truth chỉ được đọc sau khi method đã trả kết quả.
- Config:
  - `ext_r4leadlag_eval_clean`: grid G = T {40, 80, 150} × {none, extra, missing, reversed} × {0.2, 0.5}, giữ kinds để c_idx và stream damage trùng `ext_v51_eval`.
  - `ext_r4leadlag_eval_latent`: latent1, latent3 (3 children) × {none, missing-0.2, missing-0.5} × T {40, 80, 150}, kèm oracle. kinds [missing] giữ k_idx = 1 và c_idx = 1 cho missing-0.2, như `ext_v51_a1`/`a1t40`.
  - `ext_r4leadlag_eval_noise`: noise0.1 × {none, missing-0.2} × T {80, 150}, mô tả.
- `--workers 3`.

**Thống kê.**
- dIS = IS(variant) − IS(v5_1), theo run, trên các cặp run đều ok.
- Ước lượng là trung bình gộp. CI 95% percentile từ cluster bootstrap theo topology, B = 20000, seed 20261104.
- p hai phía = min(1, 2·min(p_less, p_greater)), với p_less = (1 + #{boot ≥ 0})/(B + 1) và p_greater tương tự.
- Holm step-down ở mức 0.05.
- Coverage là pooled non-null coverage theo ITT: run thất bại tính mọi cặp non-null là không cover.

**Validity.**
- **V1:** mọi row của variant ở cell không có stated missing (G: none/extra/reversed; latent và noise: none) trùng row v5_1 của cùng run (status, |ΔIS| < 1e-12, cùng số cover, cùng số non-null). V1 trượt thì variant đó NOT RETAINED (integrity).
- **Kiểm ghép cặp** (báo, không đổi verdict): row v5_1 của run này so với row đã lưu của `ext_v51_eval` (clean), `ext_v51_a1` (T80/150) và `ext_v51_a1t40` (T40) trên các khoá chung.

**Áp riêng cho từng variant (A, D):**
- **Primary cells (8):** {latent1, latent3} × {missing-0.2, missing-0.5} × T {80, 150}. Một cell là **WIN** nếu Holm (0.05, hai phía, trên 8 cell) bác H0, dIS < 0, và coverage (ITT) ≥ 0.90.
- **RETAINED (exploratory)** khi đạt đủ:
  - (i) WIN ≥ 2/8;
  - (ii) coverage ≥ 0.90 ở cả 8 primary cell;
  - (iii) no-harm trên 10 cell (6 cell clean missing T {40, 80, 150} × {0.2, 0.5} và 4 cell latent T40 {latent1, latent3} × {0.2, 0.5}): tỉ số IS ≤ 1.05, không có cell tệ hơn có ý nghĩa sau Holm (0.05, hai phía, trên 10), và coverage ≥ 0.90 ở mọi cell mà v5_1 có coverage ≥ 0.90;
  - (iv) V1 đạt.
- **Tính thông tin của nhãn.**
  - AUROC của score −p_Q, co-child C (positive) so với cạnh bị thiếu thật E0 ∪ EL (negative).
  - Tính trên các cặp được cổng xét trên dữ liệu, gộp latent1 + latent3 và missing-0.2/0.5, ở T = 150.
  - CI 95% bằng cluster bootstrap theo topology, B = 2000, seed 20261104.
  - Nếu cận dưới ≤ 0.5, hoặc không ước lượng được (< 10 cặp ở một class), thì báo **"gate not informative"**, bất kể kết quả IS.
- **Overlay đa variant:** số WIN khi Holm trên 16 cell (8 của A + 8 của D). Một claim RETAINED nào trích ra ngoài phải kèm số này.
- **Báo kèm (mô tả, không đổi verdict):**
  - noise0.1 × missing-0.2 ở T80/150;
  - coverage và IS trên co-child pair (oracle, v5_1, A, D);
  - bảng confusion nhãn × class trên dữ liệu (latent T80/150, latent T40, clean, noise);
  - số nhãn trung bình mỗi draw;
  - AUROC ở T80, AUROC chỉ so với E0, và AUROC trên mọi cặp không kề;
  - các cell T40 latent nằm trong no-harm.

**Không đổi rule sau khi có kết quả.** Thiết kế lại phải là version mới, có rule mới. Analyzer `experiments/ext/r4leadlag/analyze.py` được viết và test known-truth (`test_analyze.py`, 6/6) trước run. Hash của nó nằm trong `results/ext_r4leadlag_prereg/prereg_sha256.txt`.

---

## 4. Dự đoán (ghi trước, từ probe)

- **A:** trơ. Nhãn trên dữ liệu ≤ 0.1 mỗi run, và khoảng 0.1 mỗi draw. dIS gần 0 ở mọi cell, nên dự đoán **NOT RETAINED** (0–1 WIN) và **"gate not informative"** (AUROC T150 khoảng 0.55, CI chứa 0.5).
- **D:** gắn khoảng 2 nhãn sai mỗi draw, kể cả trên dữ liệu sạch. Dự đoán interval của D ở cell missing hẹp hơn hoặc lệch, và có thể giảm coverage trên cạnh E0 bị xoá. Rủi ro trượt no-harm ở clean T150. AUROC T150 khoảng 0.6–0.65: có thể đạt "informative" theo cận dưới. Dự đoán **NOT RETAINED**.
- Cả hai: noise0.1 không gây thêm nhãn đáng kể (probe: flag E0 ≤ 0.09).

---

## 5. Lệnh

```
PY=/Users/kietnt/miniconda3/bin/python
$PY experiments/ext/r4leadlag/drive.py calibrate --workers 3
$PY experiments/ext/r4leadlag/drive.py run --config experiments/configs/ext_r4leadlag_eval_latent.json --workers 3
$PY experiments/ext/r4leadlag/drive.py run --config experiments/configs/ext_r4leadlag_eval_clean.json --workers 3
$PY experiments/ext/r4leadlag/drive.py run --config experiments/configs/ext_r4leadlag_eval_noise.json --workers 3
$PY experiments/ext/r4leadlag/analyze.py
```

---

## 6. Kết quả (append sau run)

**Timeline (UTC, `experiments/ext/r4leadlag/logs/`):**
- Rule hashed: 12:22:51Z.
- Calibrate: 12:22:54–12:33:33Z (638 s).
- Latent run: 12:33:38–13:15:15Z (2497 s, 4320 row).
- Clean run: 13:15:15–13:27:58Z.
- Noise run: 13:27:58–13:31:14Z.
- Analyzer: chạy một lần sau run noise. Hash của `analyze.py` và của doc lúc chạy trùng `prereg_sha256.txt` (2e622ca7…, a4b4126e…).

**Thời gian chạy vượt mục tiêu 30 phút.** Run latent mất 41.6 phút vì máy bị chia sẻ (load average 45–62 trên 12 core, do các agent vòng 4 khác chạy cùng lúc). Grid không bị cắt.

**Calibration** (`results/ext_r4leadlag_cal/calibration.json`):
- Factor `tolerant_v5_1` được tune lại trùng frozen ở 12/12 key.
- Factor của A và D trùng v5_1 ở mọi key none/extra/reversed.
- Ở key missing, factor khác v5_1:

| Key | v5_1 | A | D |
|---|---|---|---|
| T40 missing | 2.3 | 2.3 | 2.3 |
| T80 missing | 2.6 | 2.5 | 2.5 |
| T150 missing | 2.3 | 2.4 | 2.5 |

### 6.1 Verdict theo rule (verbatim từ `results/ext_r4leadlag_rule/ruling.md`)

- V1 A (tolerant_v5_1_leadlag): rows identical to tolerant_v5_1 in cells without stated missing edges: 1380/1380 -> PASS
- V1 D (tolerant_v5_1_leadlag_skel): rows identical to tolerant_v5_1 in cells without stated missing edges: 1380/1380 -> PASS
- Pairing: tolerant_v5_1 rows identical to stored ext_v51_eval: 1260/1260 shared keys
- Pairing: tolerant_v5_1 rows identical to stored ext_v51_a1: 720/720 shared keys
- Pairing: tolerant_v5_1 rows identical to stored ext_v51_a1t40: 240/240 shared keys

Variant A:
- Wins (Holm 0.05 over 8, est < 0, coverage >= 0.90): 2/8 ['latent3|80|0.2', 'latent3|150|0.2']; Holm rejections over 8 (any sign): 2
- Coverage >= 0.90 in all 8 primary cells: True
- No-harm (10 cells; Holm over 10 rejections any sign: 2): clean T150 m0.2: Holm-significant worsening; clean T150 m0.5: Holm-significant worsening
- **Verdict A: NOT RETAINED**
- AUROC of the label score (-p_Q), co-child C vs true missing edge (E0/EL), pairs examined by the gate on the data, latent1+latent3, missing-0.2/0.5: T150 0.592 [0.532, 0.648] (C 191, edges 475); T80 0.477 [0.370, 0.595] (C 92, edges 386); T150 vs E0 only 0.589 [0.527, 0.649] (C 191, edges 454); T150 all non-adjacent pairs 0.617 [0.590, 0.643] (C 1036, edges 1660)
- **Gate informative (T150 lower bound > 0.5): yes**
- Labels on the data (latent T80/150; labelled/examined by truth class): C 8/283, CE 1/121, E0 8/821, EL 0/40, N 3/418; per draw: labelled 0.07, draws with a label 0.07, repaired 6.09
- Labels on the data (clean all T; labelled/examined by truth class): E0 4/530, EL 0/26, N 1/299; per draw: labelled 0.09, draws with a label 0.08, repaired 5.06

Variant D:
- Wins (Holm 0.05 over 8, est < 0, coverage >= 0.90): 1/8 ['latent3|150|0.2']; Holm rejections over 8 (any sign): 2
- Coverage >= 0.90 in all 8 primary cells: True
- No-harm (10 cells; Holm over 10 rejections any sign: 2): clean T150 m0.2: Holm-significant worsening; clean T150 m0.5: Holm-significant worsening
- **Verdict D: NOT RETAINED**
- AUROC ...: T150 0.593 [0.546, 0.636] (C 200, edges 477); T80 0.548 [0.477, 0.619] (C 93, edges 386); T150 vs E0 only 0.617 [0.569, 0.658] (C 200, edges 455); T150 all non-adjacent pairs 0.294 [0.268, 0.321] (C 1036, edges 1660)
- **Gate informative (T150 lower bound > 0.5): yes**
- Labels on the data (latent T80/150; labelled/examined by truth class): C 62/293, CE 54/122, E0 106/822, EL 29/41, N 63/445; per draw: labelled 1.73, draws with a label 0.66, repaired 5.20
- Labels on the data (clean all T; labelled/examined by truth class): E0 47/530, EL 16/26, N 31/303; per draw: labelled 1.09, draws with a label 0.51, repaired 4.42

- Overlay: wins over both variants' 16 primary cells with Holm over 16: 3

### 6.2 Số chính (từ `ruling.md`; dIS = variant − v5_1, CI cluster bootstrap B = 20000)

| cell | v5_1 cov / IS | A: cov, dIS [CI] | D: cov, dIS [CI] |
|---|---|---|---|
| latent1 T80 m0.2 | 0.953 / 3.155 | 0.946, −0.023 [−0.060, +0.018] | 0.942, +0.026 [−0.023, +0.080] |
| latent1 T150 m0.2 | 0.956 / 2.154 | 0.961, +0.020 [+0.002, +0.036] | 0.965, +0.043 [+0.007, +0.079] |
| latent1 T80 m0.5 | 0.958 / 3.466 | 0.949, +0.010 [−0.053, +0.084] | 0.946, +0.097 [−0.034, +0.250] |
| latent1 T150 m0.5 | 0.957 / 2.384 | 0.961, +0.028 [−0.004, +0.058] | 0.965, +0.068 [+0.028, +0.112] (Holm, tệ hơn) |
| latent3 T80 m0.2 | 0.961 / 3.207 | 0.955, **−0.045 [−0.072, −0.018]** (Holm) | 0.953, −0.046 [−0.112, +0.031] |
| latent3 T150 m0.2 | 0.916 / 2.864 | 0.927, **−0.044 [−0.069, −0.020]** (Holm) | 0.936, **−0.078 [−0.127, −0.028]** (Holm) |
| latent3 T80 m0.5 | 0.968 / 3.594 | 0.962, −0.053 [−0.099, −0.002] | 0.955, −0.099 [−0.205, −0.002] |
| latent3 T150 m0.5 | 0.935 / 2.867 | 0.942, +0.004 [−0.043, +0.045] | 0.945, −0.041 [−0.107, +0.022] |
| clean T150 m0.2 (no-harm) | 0.966 / 1.759 | 0.972, +0.033 [+0.015, +0.049] (Holm, tệ hơn) | 0.978, +0.069 [+0.041, +0.096] (Holm, tệ hơn) |
| clean T150 m0.5 (no-harm) | 0.968 / 1.986 | 0.974, +0.043 [+0.023, +0.063] (Holm, tệ hơn) | 0.975, +0.090 [+0.040, +0.145] (Holm, tệ hơn) |
| noise0.1 T80 m0.2 (mô tả) | 0.916 / 3.261 | 0.903, +0.052 [−0.000, +0.110] | 0.906, +0.024 [−0.058, +0.119] |
| noise0.1 T150 m0.2 (mô tả) | 0.916 / 2.242 | 0.927, −0.046 [−0.069, −0.024] | 0.935, −0.044 [−0.098, +0.010] |

**Các điểm khác:**
- Mọi tỉ số IS no-harm đều ≤ 1.05: A ≤ 1.022, D ≤ 1.045.
- Không cell no-harm nào rơi dưới 0.90 coverage.
- 0 run thất bại ở mọi cell, cho cả ba method.
- Bảng co-child pair và oracle nằm ở cuối `ruling.md`. Ở T150, coverage của v5_1 trên mọi co-child pair là 0.828–0.853. A đạt 0.851–0.873, D đạt 0.861–0.880. Oracle ở latent3 T150 chỉ cover 0.779 (non-null): oracle cũng bị confounder làm lệch.

### 6.3 So với dự đoán ở mục 4

- **A trơ: đúng.**
  - Trên dữ liệu, cổng chỉ gắn nhãn 8/283 cặp co-child và 8/821 cạnh E0 ở latent T80/150. Mỗi draw có khoảng 0.07 nhãn.
  - Dự đoán "gate not informative" **sai theo tiêu chí đã ghi**: AUROC T150 = 0.592 [0.532, 0.648]. Thứ hạng p_Q có chút thông tin, nhưng ngưỡng p < 0.05 gần như không bao giờ đạt, nên cổng hầu như không hành động.
- **D: đúng một phần.**
  - D gắn khoảng 1.7 nhãn mỗi draw ở latent và 1.1 ở clean.
  - AUROC 0.593 [0.546, 0.636] đạt "informative" như dự đoán là có thể.
  - D trượt no-harm ở clean T150 như dự đoán. Nhưng mục 7 cho thấy phần trượt này đến từ width factor, không phải từ cổng.
- **noise0.1:** cổng A gắn 1/88 nhãn trên cạnh E0; D gắn 8/88. Không có tác động đáng kể.

---

## 7. Phân rã post hoc (MÔ TẢ, không thuộc rule; quyết định sau khi xem summary của run latent)

**Lý do làm.**
- Factor được tune lại cho A/D khác factor của v5_1 ở T80 missing (2.5 so với 2.6) và T150 missing (2.4–2.5 so với 2.3).
- Trong khi đó, A gần như không bao giờ gắn nhãn.
- Vậy hiệu dIS của rule có thể là hiệu của calibration chứ không phải của cổng.

**Thiết kế phân rã.**
- Chạy lại A và D với **đúng factor frozen của v5_1** (`experiments/ext/r4leadlag/frozen_r4leadlag_v51factors.json`). Seed và cell giữ nguyên.
- Config:
  - `ext_r4leadlag_decomp_latent`: latent1/3 × T80/150, 454 s.
  - `ext_r4leadlag_decomp_clean`: clean T150, 159 s.
- Kiểm tra: row ở cell không missing trùng v5_1 1080/1080.
- Phần cổng = (variant với factor v5_1) − v5_1. Phần factor = (variant với factor riêng) − (variant với factor v5_1).
- Script: `experiments/ext/r4leadlag/decomp.py`. Kết quả: `results/ext_r4leadlag_rule/decomp.{md,json}`.

| cell | A: phần cổng | A: phần factor | D: phần cổng | D: phần factor |
|---|---|---|---|---|
| latent3 T80 m0.2 | −0.015 [−0.046, +0.010] | −0.030 [−0.052, −0.008] | −0.023 [−0.090, +0.043] | −0.023 [−0.050, +0.007] |
| latent3 T150 m0.2 | +0.008 [−0.013, +0.030] | −0.051 [−0.075, −0.027] | −0.007 [−0.044, +0.032] | −0.071 [−0.112, −0.028] |
| latent1 T150 m0.5 | +0.009 [−0.022, +0.042] | +0.019 [+0.002, +0.035] | +0.027 [−0.020, +0.080] | +0.041 [+0.007, +0.072] |
| clean T150 m0.2 | +0.002 [−0.012, +0.017] | +0.030 [+0.018, +0.042] | −0.001 [−0.028, +0.029] | +0.070 [+0.055, +0.083] |
| clean T150 m0.5 | +0.006 [−0.017, +0.030] | +0.037 [+0.022, +0.051] | +0.031 [−0.018, +0.087] | +0.059 [+0.025, +0.089] |

**Kết quả trên 10 cell (8 primary + clean T150 × 2):**
- Phần cổng: Holm 0.05 cho tốt hơn 0/10 và tệ hơn 0/10, với cả A lẫn D.
- Coverage của bản chỉ có cổng: 0.915–0.969, gần như trùng v5_1 (|Δ| ≤ 0.007).
- Mọi WIN theo rule (A: latent3 T80/T150 m0.2; D: latent3 T150 m0.2) và mọi vi phạm no-harm (clean T150) đều đến từ phần factor.
- Cơ chế: factor lớn hơn làm interval rộng hơn. Rộng hơn có lợi ở cell under-cover (latent3 T150, coverage 0.916) và có hại ở cell over-cover (clean T150, coverage 0.966). Factor nhỏ hơn ở T80 có lợi ở latent3 T80 (coverage 0.96).

**Bài học phương pháp (cho các ứng viên vòng 4 khác).**
- Tune lại width factor trên D-07H cho một method **gần như trùng** v5_1 đã tự nó đổi IS khoảng ±0.03–0.07.
- Mức đó đủ để tạo WIN hoặc "harm" có ý nghĩa sau Holm ở T80/150.
- Hệ quả: rule nào so một variant đã re-calibrate với v5_1 frozen nên kèm phân rã cổng/factor như trên, hoặc so ở cùng factor. Nếu không, verdict có thể chỉ đo nhiễu calibration (grid 0.05 ở factor hiệu dụng, 20 topology D-07H × 1 replicate).

---

## 8. Kết luận

- **Verdict theo rule:** A NOT RETAINED (2/8 WIN, trượt no-harm ở clean T150). D NOT RETAINED (1/8 WIN, trượt no-harm ở clean T150). Overlay Holm trên 16: 3 WIN. Không có "Frozen spec": không variant nào đạt.
- **Diễn giải (dựa trên phân rã post hoc):** cổng lead-lag không đổi interval score hay coverage ở bất kỳ cell nào. Mọi khác biệt có ý nghĩa đến từ calibration.

**Vì sao cổng không làm được việc của nó.**
- Residual cấu trúc là prediction error của một VAR. Lag của chính các co-child, và lag block được mở cho cặp, đã hấp thụ phần persistent của latent AR(1).
- Phần còn lại trong residual gần với innovation của latent: white noise, tác động cùng lúc lên hai co-child. Đó đúng là blind spot "white-noise confounder" của giả thuyết.
- Kết quả: confounder persistent trong generator này **xuất hiện như** một confounder white noise sau khi residualize.
- Trên residual chỉ gồm term của skeleton (D) thì còn dấu vết. Nhưng cạnh bị thiếu thật cũng để lại cross-correlation ở lag khác 0 (lag của cạnh, lag của chính nút). Vì thế AUROC trên mọi cặp không kề của D chỉ là 0.294: cạnh thật trông "confounded" hơn cả co-child.
- Trong bootstrap draw (thế giới không có latent), D gắn khoảng 1–2 nhãn sai mỗi draw.

**Điều đứng vững và đáng ghi vào paper (limitations, M về latent).**
- Ở T150, `tolerant_v5_1` dùng khoảng 0.4 (latent1) và 1.3 (latent3) slot repair mỗi run cho cặp co-child. Đây là số của probe D-07H; trên D-07, A xét 283 cặp C trong 821 + 40 cạnh bị thiếu.
- Coverage của v5_1 trên co-child pair ở T150 chỉ là 0.83–0.85.
- Một kiểm định lead-lag kiểu Haugh trên residual cấu trúc **không** tách được confounder persistent khỏi cạnh contemporaneous bị thiếu ở T ≤ 150: AUROC ≤ 0.62, flag rate trên co-child ≤ 3% ở ngưỡng 0.05.

**Câu đề xuất cho paper:**

> "A lead-lag portmanteau gate (Haugh 1976) on the structural residuals does not separate hidden persistent confounders from missing contemporaneous edges at T ≤ 150 (AUROC 0.59 [0.53, 0.65] at T = 150, labels on 3% of co-child pairs), because the VAR residuals retain only the confounder's innovation; it leaves interval score and coverage unchanged (0/10 cells after Holm, at equal width factors)."

**Bug và bẫy trong file có sẵn (báo, không sửa):**
- (a) `run_experiment.py` chỉ áp width factor cho method có trong `calibrate_methods`. Một config liệt kê `tolerant_v5_1` trong `methods` mà quên `calibrate_methods` sẽ chạy v5_1 **không calibrate** (prescale 0.5) mà không báo gì. Smoke test của hướng này gặp đúng lỗi đó trước khi sửa config. Đây là bẫy, chưa hẳn là bug, nhưng nên có cảnh báo.
- (b) Stream tag của ext method theo tên (`ext_seed`). Hai method cùng code nhưng khác tên vì thế không ghép cặp theo random number. Hướng này dùng patch phía worker (`worker.py`) thay vì sửa runner.

**File kết quả:**
- `results/ext_r4leadlag_probe/` (probe D-07H)
- `results/ext_r4leadlag_tests/` (unit test, test analyzer)
- `results/ext_r4leadlag_prereg/prereg_sha256.txt`
- `results/ext_r4leadlag_cal/`
- `results/ext_r4leadlag_eval_{latent,clean,noise}/`
- `results/ext_r4leadlag_decomp_{latent,clean}/`
- `results/ext_r4leadlag_rule/{ruling,decomp}.{md,json}`
