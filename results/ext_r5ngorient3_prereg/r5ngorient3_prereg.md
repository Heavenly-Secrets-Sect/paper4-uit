# Hướng `r5ngorient3` (vòng 5): NG-A v3, thành phần (A) của `tolerant_v5_2`

**Trạng thái.** Exploratory. Evaluation chỉ trên D-07 development với **seed_base mới 70261102**. Không có calibration nào (thành phần A thừa kế factor frozen của `tolerant_v5_1`). Code check chỉ chạy trên D-07H development. Không đụng P4-H1, P4-H2 (cả hai split) hay confirmatory split nào. Không LLM call, không git commit. Module of record vẫn là `tolerant_v5_1`. Hướng này chỉ thêm file mới (tiền tố `r5ngorient3`).

**Nhiệm vụ.** Xây NG-A v3 đúng như mục 4.1 (A) của `docs/ext/synthesis_round4.md`, chạy V0 (unit test, mục 4.2) trước mọi bank run. V0 hỏng thì dừng và bỏ thành phần A. V0 đạt thì chạy P1 (8 cell primary ng_mix, endpoint gộp) cho riêng thành phần A (v5_1 + A) so với `tolerant_v5_1`, cùng no-harm trên lưới Gaussian G (21 cell) và 13 cell ng_mix không primary, rồi ra verdict cho riêng thành phần A.

## 1. Câu hỏi và lỗi cần sửa

NG-A v2 (`ext_r4ngorient.tolerant_ngA`) thay hai đồng xu của v5_1 (chiều cạnh repair ở bước 3, cạnh bị lật ở bước 4) bằng evidence non-Gaussian theo cặp của Hyvärinen & Smith (2013, JMLR 14:111–152), đặt sau gate Jarque–Bera. Verifier vòng 4 tìm ra một **lỗi cấu tạo**: ở dạng tanh, dấu hiệu chỉnh super-/sub-Gaussian lấy từ **trung bình** excess kurtosis của cặp. Với cặp khác law, luật này không consistent:
- tỷ lệ sai chiều theo hỗn hợp law của ng_mix là 0.132 / 0.162 / 0.148 ở m 78 / 148 / 400, không giảm theo m;
- cặp có uniform gần như tung đồng xu (t5 → uniform sai 52% ở m 400).

HS 2013 mục 2.6 dùng dấu kurtosis của **một biến** và nói rằng thường hai dấu giống nhau. Uniform (exkurt −1.2) trộn với law super-Gaussian phá giả định đó.

## 2. File của hướng này (chỉ file mới)

| File | Vai trò |
|---|---|
| `src/paper4/ext_r5ngorient3.py` | `tolerant_ngA3` (NG-A v3); hàm evidence `ng_evidence3`; nhánh copy từ `ext_r4ngorient` với evidence là tham số |
| `experiments/ext/r5ngorient3/v0_unit_test.py` | V0 (đăng ký trước, mục 4.1) |
| `experiments/ext/r5ngorient3/analyze.py` | Rule V1, P1, no-harm, verdict, phần phụ và diagnostic (mục 4.3–4.5) |
| `experiments/ext/r5ngorient3/check_copy.py` | Code check trước khi đăng ký: copy fidelity và identity (mục 3.3) |
| `experiments/ext/r5ngorient3/design_popcheck.py` | Kiểm dấu kỳ vọng của thống kê ở m = 10⁶ (mục 3.3) |
| `experiments/ext/r5ngorient3/make_frozen.py` | Ghép factor frozen |
| `experiments/ext/r5ngorient3/frozen_r5ngorient3.json` | `frozen_v4_v51.json` nguyên văn + `tolerant_ngA3|*` = `tolerant_ngA|*` = `tolerant_v5_1|*` |
| `experiments/configs/ext_r5ngorient3_{ngmix,gauss}.json` | Config evaluation (chạy bằng driver có sẵn `experiments/ext/r4ngorient/run_ng.py`, không sửa) |
| `results/ext_r5ngorient3_*` | Kết quả |

## 3. Thiết kế NG-A v3

### 3.1 Hàm evidence `ng_evidence3(x, y)` (R > 0 nghĩa là x → y)

Giữ nguyên từ v2:
- x, y là phần dư cấu trúc như v2 (BH candidate: phần dư base fit; cạnh pool u → v: phần dư của u và phương trình của v fit lại bỏ u_t), chuẩn hoá trên m dòng;
- **gate JB** như v2: JB_i = m(skew_i²/6 + exkurt_i²/24), p_i = exp(−JB_i/2), mở khi 1 − (1 − min(p_x, p_y))² < 0.10;
- **bộ chọn dạng** như v2: S = m(skew_x² + skew_y²)/6, K = m(exkurt_x² + exkurt_y²)/24;
- **S ≥ K: dạng skew** của v2 (HS 2013 eq. 13): lật dấu từng biến cho skewness dương, R = ρ·mean(x²y − xy²);
- **jackknife se** như v2 (10 block dòng liên tiếp; dạng và họ cố định từ toàn mẫu; chuẩn hoá và ρ làm lại trong từng subsample); p = Φ(R/se), cắt [0.05, 0.95]; gate đóng thì p = 0.5 đúng.

Thay đổi duy nhất là **S < K: dạng "lik"**, hiệu log-likelihood xấp xỉ của hai chiều (HS 2013 mục 2):

R = mean[ G_x(x) − G_x(r_xy) + G_y(r_yx) − G_y(y) ],

với ρ = mean(xy), r_yx = (y − ρx)/√(1 − ρ²) (phần dư của y theo x), r_xy = (x − ρy)/√(1 − ρ²).

- **G_x chọn từ dấu excess kurtosis của chính x**, G_y từ dấu của chính y:
  - exkurt ≥ 0 (super-Gaussian): họ log cosh, G(u) = −log cosh(πu/2), log-density của luật hyperbolic secant phương sai 1;
  - exkurt < 0 (sub-Gaussian): generalized Gaussian shape 4, G(u) = −(u/a)⁴ với a² = Γ(1/4)/Γ(3/4), phương sai 1.
- **Mỗi phần dư dùng họ của biến mà nó thay thế trong chiều của nó:** trong mô hình x → y, r_yx đứng ở vị trí của y; trong mô hình y → x, r_xy đứng ở vị trí của x. Log-likelihood của x → y là G_x(x) + G_y(r_yx), của y → x là G_y(y) + G_x(r_xy); Jacobian hai chiều bằng nhau nên triệt tiêu.
- Vì mỗi hiệu dùng cùng một họ, hằng số chuẩn hoá triệt tiêu. Khi hai họ trùng nhau, R đúng là likelihood ratio một-G của HS. Khi ρ nhỏ, khai triển bậc một cho R ≈ ρ·mean(y g_x(x) − x g_y(y)), tức dạng tanh của HS cho từng biến.

### 3.2 Lý do chọn như vậy (ghi trước khi chạy V0)

- Theo lý thuyết ổn định của ICA: dưới x → y, (r_xy, y) là phép quay góc θ của hai nguồn độc lập (x, e), với sin θ = ρ. R kỳ vọng là J(0) − J(θ) của contrast G_x(u₁) + G_y(u₂). Đạo hàm bậc một bằng 0 do độc lập. Bậc hai cho
  E R ≈ (θ²/2)·{E[x g_x(x) − g_x′(x)] + E[e g_y(e) − g_y′(e)]},
  dương khi mỗi họ khớp loại super/sub của nguồn tương ứng. Luật dấu trung bình của v2 dùng **một** họ cho cả hai nguồn, nên sai khi hai nguồn khác loại (ví dụ t5 và uniform).
- Họ của y được dùng cho r_yx ≈ e. Với các law của ng_mix và b ≤ 0.6, dấu kurtosis của y = b·x + e trùng dấu của e (ví dụ t5 → uniform, b 0.6: exkurt y ≈ −0.23). Ở mẫu hữu hạn, dấu này có thể bị đoán sai khi |exkurt y| nhỏ. Đây là rủi ro đã biết; V0 đo nó.
- Không chọn họ cho phần dư từ kurtosis của chính phần dư: khi đó mỗi hiệu có thể trộn hai họ khác nhau. Hằng số chuẩn hoá không triệt tiêu, và một hiệu KL không mang thông tin chiều xuất hiện ngay ở bậc 0.
- Họ sub-Gaussian: generalized Gaussian shape 4 trơn, có chuẩn hoá đóng, và cho E[s g(s) − g′(s)] = −4c·exkurt(s) > 0 với mọi nguồn sub-Gaussian. Đây là lựa chọn của nhóm; HS 2013 không chỉ định họ sub-Gaussian.
- Dạng skew khi skew trội giữ như v2 (theo 4.1 A). Giới hạn đã biết: nguyên nhân đối xứng mà chỉ nhiễu lệch thì dạng skew không có thông tin. Ở population, các law của ng_mix luôn rơi vào dạng lik (mục 3.3).
- Mọi phần khác của NG-A giữ nguyên v2 từng dòng: tính lại evidence trong mỗi draw; bước 3 `rng.random() < p_uv`; bước 4 Plackett–Luce bằng key Efraimidis–Spirakis với w_e = 1 − p(chiều khai báo); `methods._flip_from` khi mọi trọng số bằng 0.5; common random numbers với v5_1; switch TAU, targeted opening, BH, pool, 199 draw, percentile, PRESCALE 0.5.
- **Factor:** thừa kế factor frozen của v5_1 (`frozen_v4_v51.json`), không re-tune.

### 3.3 Những gì đã chạy TRƯỚC khi ghi phần đăng ký (không chạm D-07)

1. **Kiểm dấu ở population** (`design_popcheck.py`, `results/ext_r5ngorient3_check/design_popcheck.txt`):
   - m = 10⁶, một mẫu cho mỗi cặp, không gate, không jackknife, dạng lik bị ép;
   - 25 cặp law non-Gaussian có thứ tự × b ∈ {0.3, 0.6};
   - **R > 0 ở cả 50/50.** Bộ chọn dạng ở population chọn lik ở cả 50.
   - Mục đích là bắt lỗi dấu hoặc lỗi suy dẫn; nó không nói gì về tỷ lệ ở mẫu hữu hạn. Mình công bố việc đã xem cái này.
2. **Code check của hàm evidence** (scratch, 300 mẫu ngẫu nhiên, không phải lưới V0):
   - phản đối xứng |p(y,x) − (1 − p(x,y))| ≤ 2.9e−15;
   - bất biến thang dương và âm ≤ 9.5e−15; gate lệch 0.
   - Không xem tỷ lệ đúng chiều.
3. **Copy fidelity và identity** (`check_copy.py`, `results/ext_r5ngorient3_check/check_copy.json`):
   - D-07H development, seed_base 70261102 + 700 000, ng_mix, 2 unit, T 80/150, đủ 7 cell;
   - nhánh copy với evidence v2 trùng `tolerant_ngA` từng bit (status, lo, hi, C) ở **28/28** run;
   - `tolerant_ngA3` trùng `tolerant_v5_1` ở **12/12** run none/extra;
   - thời gian: v5_1 13.5 s, NG-A v2 20.7 s, NG-A v3 22.0 s (+63% so với v5_1).
   - Không tính truth, IS hay coverage.
4. **Chạy thử analyzer** trên dữ liệu vòng 4 đã thấy (`ext_r4ngorient_v2_*`, NG-B đứng thay cho arm), trong scratch, để chắc analyzer chạy hết các nhánh. Analyzer tái lập số NG-B v2 trong `docs/ext/r4ngorient.md` mục 9 (3 WIN: −0.082, −0.046, −0.062). Ở bước này mình cũng thấy endpoint gộp của NG-A v2 trên dữ liệu vòng 4 là −0.0194 [−0.0268, −0.0123]. Đó là dữ liệu cũ đã thấy, không phải dữ liệu vòng 5.
5. **Guard seed:** không `results/*/manifest.json` nào có seed_base 70261102 (đã kiểm trước mọi run).

## 4. Đăng ký trước (ghi 2026-11-02 14:48Z, trước mọi run V0 và D-07)

### 4.1 V0: unit test NG-A v3 (`v0_unit_test.py`)

- **Mô hình:** LiNGAM 2 biến x → y, x = e₁, y = b·x + e₂, e₁ và e₂ độc lập, phương sai 1.
- **Law:** mọi **cặp có thứ tự** của 6 lựa chọn {laplace, t5, skewexp+, skewexp−, uniform, gauss}, tức 36 cặp. skewexp± có dấu cố định.
- **Lưới:** b ∈ {0.3, 0.6}, m ∈ {78, 148, 400}, 500 rep mỗi ô, seed 70261104.
- Gọi `ng_evidence3(x, y)` với x là nguyên nhân.
- **Đúng** = p > 0.5, **sai** = p < 0.5. Gate đóng cho p = 0.5 đúng, nên không tính là đúng hay sai.
- **Tỷ lệ sai khi gate mở** của một cặp = n_sai / n_gate_mở (bằng 0 nếu gate không bao giờ mở).
- **Hỗn hợp ng_mix:** trọng số law laplace 1/4, t5 1/4, skewexp+ 1/8, skewexp− 1/8, uniform 1/4, nhân theo (cause, noise) trên 25 cặp non-Gaussian. Tỷ lệ sai hỗn hợp = Σ w·n_sai / Σ w·n_mở, tức P(sai | gate mở) dưới hỗn hợp law của ng_mix.

**Tiêu chí (cả năm đều quyết định):**
- **C1:** tỷ lệ sai hỗn hợp (khi gate mở) ở m 148, b 0.6 ≤ 0.10.
- **C2:** cả 25 cặp law non-Gaussian có thứ tự: tỷ lệ sai khi gate mở ở m 400, b 0.6 ≤ 0.30.
- **C3 (consistency):** tỷ lệ sai hỗn hợp ở m 400, b 0.6 ≤ ở m 148, b 0.6.
- **C4:** gauss → gauss, ở **mỗi** ô (b, m) trong 6 ô: gate mở ≤ 0.12 và mean p ∈ [0.48, 0.52].
- **C5:** |p(a·x, c·y) − p(x, y)| ≤ 1e−9 và gate trùng, với a, c = exp(U(−3, 3)), trên mọi rep của mọi ô.

**V0 PASS khi C1–C5 cùng đạt. V0 FAIL thì dừng:** không bank run nào, thành phần A bị bỏ khỏi vòng 5.

Chỉ báo, không quyết định: tỷ lệ không điều kiện, mọi b và m, cặp có Gaussian, thang âm, phản đối xứng, tỷ lệ dạng/họ, và `ng_evidence` của v2 trên cùng mẫu.

### 4.2 Evaluation runs (chỉ khi V0 PASS)

D-07 development, **seed_base 70261102**, 20 topology × 3 replicate, T 40/80/150, đủ 7 cell (none + {extra, missing, reversed} × {0.2, 0.5}), H 4, lag_max 2, n_boot 199, τ 0.1, `--workers 3`, driver `experiments/ext/r4ngorient/run_ng.py` (không sửa).

| Run | Shock | Method |
|---|---|---|
| `ext_r5ngorient3_ngmix` | ng_mix | oracle, tolerant_v5_1, tolerant_ngA3, tolerant_ngA |
| `ext_r5ngorient3_gauss` | gauss | như trên |

- `tolerant_ngA3` và `tolerant_ngA` dùng stream của v5_1 (`stream_of`), nên có common random numbers.
- Mọi arm dùng factor frozen của v5_1 (`frozen_r5ngorient3.json`, sha256 `29b1fe2f416996cee1c98e335a6e5976be171b1091ed847380d1c8b2dd246d85`; config kiểm hash này).
- `tolerant_ngA` (v2) chỉ để mô tả, không vào rule.
- Hai run chạy **tuần tự** vì máy dùng chung.

### 4.3 Thống kê

Như vòng 4:
- IS của run = mean IS trên cặp non-null.
- Ghép cặp trên các run mà cả hai method ok.
- dIS = arm − v5_1. CI 95% bằng cluster bootstrap theo topology (20 cluster), B = 20000, seed 20261104, percentile.
- p một phía = tỷ lệ resample ở phía H0, sàn 1/B.
- IS ratio = mean IS arm / mean IS v5_1 trên run ghép cặp.
- Coverage = n_covered_nonnull / n_nonnull gộp trên run ok.
- **Một cell chỉ được tính là win hay thua có ý nghĩa khi có ≥ 8 topology cluster** trong các run ghép cặp.
- Helper (`holm`, `Boot`, `ci`, `p_side`, `load_runs`, `auroc`) import nguyên từ `experiments/ext/r4ngorient/analyze.py` (không sửa, có trong hash).

### 4.4 Rule cho thành phần A

**V1 (identity):**
- (i) Ở mọi run của 9 cell none/extra × 2 shock, `tolerant_ngA3` trùng v5_1 từng bit: status, IS, n_covered, lo/hi/C của mọi cặp non-null trong `pairs.npz`.
- (ii) Ở mọi run missing/reversed mà không gate nào mở (mức dữ liệu và mọi draw, theo `diag.jsonl`), arm trùng v5_1.
- (iii) Width factor của arm bằng factor của v5_1 ở mọi run ghép cặp.

**P1 (ng_mix, 8 cell primary T{80, 150} × {missing, reversed} × {0.2, 0.5}):**
- **Endpoint gộp** E = (1/8) Σ_c dIS_c / IS_v51,c. Mỗi tỷ số cell là Σ dIS / Σ IS_v51 trên run ghép cặp.
- Bootstrap dùng cùng resample topology cho mọi cell; cận trên 95% một phía là quantile 0.95 của E qua các resample.
- **P1 đạt khi đủ ba điều kiện:**
  - cận trên 95% một phía của E < 0;
  - coverage của arm ≥ 0.90 ở cả 8 cell primary;
  - ở mỗi cell, số run thất bại của arm ≤ số của v5_1 + 1.
- Phụ (báo, không quyết định):
  - WIN theo Holm 8 từng cell (Holm bác dIS ≥ 0, coverage ≥ 0.90, failure guard, ≥ 8 cluster);
  - coverage trên cặp affected (dC ≥ 0.05) ở 4 cell reversed, Δ = cov(arm) − cov(v5_1), Holm 4, H0 Δ ≤ 0.

**No-harm:**
- **(a) Lưới Gaussian G, 21 cell** (3 T × 7 cell). Mọi cell phải đủ ba điều kiện:
  - IS ratio ≤ 1.03;
  - không tệ hơn có ý nghĩa (Holm 21, H0 dIS ≤ 0, cell cần ≥ 8 cluster);
  - coverage của arm ≥ 0.90 ở mọi cell mà v5_1 ≥ 0.90.
- **(b) 13 cell ng_mix không primary** (7 cell T40; none, extra-0.2, extra-0.5 ở T80 và T150). Mọi cell phải đủ hai điều kiện:
  - IS ratio ≤ 1.05;
  - coverage của arm ≥ 0.90 ở mọi cell mà v5_1 ≥ 0.90.

**Verdict thành phần A:**
- **RETAINED (thành phần A, exploratory)** khi V0, V1, P1, no-harm (a) và (b) cùng đạt.
- Ngược lại là **NOT RETAINED**: bỏ thành phần A khỏi `tolerant_v5_2`.

### 4.5 Điều chỉnh so với bản nháp mục 4.2 của synthesis (chỉ chỗ cần số cụ thể), ghi trước khi chạy

1. **"Tỷ lệ sai hướng (khi gate mở)"** đọc theo nghĩa đen: P(sai | gate mở). Cách này chặt hơn tỷ lệ không điều kiện mà verifier dùng (0.132 / 0.162 / 0.148). Tỷ lệ không điều kiện được báo kèm.
2. **Trọng số hỗn hợp** theo `laws.node_laws("ng_mix")`: 4 law đồng xác suất, dấu skewexp đồng xác suất, cause và noise độc lập. Đây đúng là trọng số verifier dùng.
3. skewexp± là hai lựa chọn law riêng có dấu cố định, nên có 36 cặp có thứ tự. "Cặp law non-Gaussian" ở C2 là 25 cặp không có gauss.
4. C3 đo ở b 0.6, cùng b với C1 và C2. b 0.3 được báo kèm.
5. C4 áp cho cặp gauss → gauss ở từng ô (b, m). C5 áp cho mọi rep của mọi ô.
6. P1 giữ hai guard của rule v1/v2 (coverage ≥ 0.90 ở 8 cell, failure guard), dù bản nháp 4.2 không nhắc lại. Hai guard này chỉ làm rule chặt hơn.
7. V1 cho riêng thành phần A: không có hubscreen nên không có "run bị rút gọn". Thêm kiểm tra factor bằng nhau.
8. No-harm (c) (latent1, noise0.1; chỉ mô tả cho bản ghép) **không chạy** cho riêng thành phần A. Task chỉ định G và 13 cell ng_mix, và driver ng_mix không có sẵn kịch bản latent/noise.
9. Như bản nháp đã ghi: việc đổi từ "≥ 3/8 win" sang endpoint gộp được quyết định **sau** khi thấy v2 (8/8 dIS âm nhưng nhỏ). Seed mới giảm nhưng không xóa vấn đề này, và vẫn là 20 topology của D-07, nên mọi kết quả là exploratory.

### 4.6 Dự đoán ghi trước

- **V0:** dấu ở population đúng cả 50/50, nên C2, C3 có khả năng đạt. C1 (≤ 0.10 ở m 148) là chỗ rủi ro nhất: ở m 148, dấu kurtosis của biến gần Gaussian (như y trong t5 → uniform, exkurt ≈ −0.23, se ≈ 0.4) bị đoán sai khá thường xuyên. Mình đoán tỷ lệ sai hỗn hợp có điều kiện khoảng 0.06–0.12; xác suất V0 PASS khoảng 60%.
- **P1:** NG-A v2 đạt endpoint gộp trên dữ liệu vòng 4 (mục 3.3.4). v3 chỉ đổi evidence ở chỗ v2 sai, nên mình đoán E khoảng −0.015 đến −0.03, xác suất P1 đạt khoảng 60%.
- **No-harm (a):** gate không đổi, nên dưới Gaussian gate vẫn mở 7–18% (cao nhất ở T150). Có rủi ro nhỏ ở Gaussian T150; mình đoán đạt.
- **No-harm (b):** đạt.

## 5. Nhật ký chạy (ghi theo thứ tự, sau phần đăng ký)

Mọi mục dưới đây được ghi sau khi phần 1–4 đã được hash (`results/ext_r5ngorient3_prereg/hashes.txt`). Bản doc lúc hash được lưu ở `results/ext_r5ngorient3_prereg/r5ngorient3_prereg.md`.
