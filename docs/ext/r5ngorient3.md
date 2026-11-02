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

**5.1 V0** (`v0_unit_test.py`, chạy 14:49:34Z, 233.3 s; `results/ext_r5ngorient3_v0/v0.md`, `v0.json`). Chép nguyên văn:
- "C1 sai chiều có điều kiện, hỗn hợp ng_mix, m 148, b 0.6 = 0.0580 (≤ 0.10) -> ĐẠT"
- "C2 cặp non-Gaussian tệ nhất ở m 400, b 0.6: skewexp- → uniform = 0.0980 (≤ 0.30); số cặp vượt: 0/25 -> ĐẠT"
- "C3 hỗn hợp m 400 = 0.0181 ≤ m 148 = 0.0580 -> ĐẠT"
- "C4 gauss → gauss: b 0.3 m 78: gate 0.080, mean p 0.504; b 0.3 m 148: gate 0.088, mean p 0.501; b 0.3 m 400: gate 0.092, mean p 0.497; b 0.6 m 78: gate 0.082, mean p 0.503; b 0.6 m 148: gate 0.094, mean p 0.500; b 0.6 m 400: gate 0.090, mean p 0.498 -> ĐẠT"
- "C5 max |Δp| thang dương = 9.33e-15, gate lệch 0 -> ĐẠT"
- "Báo thêm: max |Δp| thang âm = 9.33e-15; max |p(y,x) − (1 − p(x,y))| = 5.22e-15"
- "**V0: PASS**"

So sánh mô tả với v2 trên cùng mẫu (tỷ lệ sai khi gate mở, hỗn hợp ng_mix):

| b | m | v3 | v2 |
|---|---|---|---|
| 0.6 | 78 | 0.114 | 0.184 |
| 0.6 | 148 | 0.058 | 0.164 |
| 0.6 | 400 | 0.018 | 0.150 |
| 0.3 | 78 | 0.177 | 0.254 |
| 0.3 | 148 | 0.088 | 0.217 |
| 0.3 | 400 | 0.023 | 0.179 |

- Ở v3 tỷ lệ sai giảm theo m; ở v2 thì không (tái lập phát hiện của verifier).
- t5 → uniform ở m 400, b 0.6: v3 0.036, v2 0.462.
- Cặp tệ nhất của v3:
  - ở m 148, b 0.6: uniform → skewexp− 0.188, uniform → skewexp+ 0.160 (v2: 0.430 / 0.442);
  - ở m 400: skewexp− → uniform 0.098.
- Ở m 78, b 0.3, tỷ lệ sai hỗn hợp có điều kiện là 0.177. Đây là ô không nằm trong tiêu chí.

V0 đạt, nên theo rule chuyển sang bank run.

**5.2 Evaluation D-07** (`results/ext_r5ngorient3_runlog.txt`), chạy tuần tự với `--workers 3`:
- `ext_r5ngorient3_ngmix`: 14:53:50Z–15:07:39Z, 828.5 s, 5040 hàng.
- `ext_r5ngorient3_gauss`: 15:07:39Z–15:20:07Z, 747.9 s, 5040 hàng.
- Exit 0 cả hai; mọi method ok 60/60 ở mọi cell (failure 0/0 ở mọi cell được chấm).

**5.3 Kiểm hash trước khi chạy analyzer:** mọi file trong `hashes.txt` (trừ chính doc này, vốn được nối thêm nhật ký) khớp sha256. Bản doc lúc đăng ký `r5ngorient3_prereg.md` cũng khớp.

**5.4 Kết quả theo rule** (`analyze.py`, `results/ext_r5ngorient3_analysis/ruling.md`, `ruling.json`). Chép nguyên văn:
- "V1: Cell none/extra (2 shock × 3 T × 3 cell): 1080/1080 run trùng v5_1 từng bit"; "Run missing/reversed không có gate nào mở (mức dữ liệu và mọi draw): 6/6 trùng v5_1"; "Width factor của NG-A v3 bằng factor frozen của v5_1 ở 2520/2520 run ghép cặp"; "**V1: PASS**"
- "Endpoint gộp = trung bình qua 8 cell của dIS/IS_v51 = -0.0090 [95% CI -0.0142, -0.0035]; cận trên 95% một phía = -0.0044; p một phía (H0 ≥ 0) = 0.0003 -> ĐẠT"
- "Coverage NG-A v3 ≥ 0.90 ở cả 8 cell: ĐẠT; failure arm ≤ v5_1 + 1 ở cả 8 cell: ĐẠT"; "**P1: PASS**"
- "Win Holm 8: 1/8."
- "**No-harm (a): ĐẠT**"; "**No-harm (b): ĐẠT**"
- "V0 ĐẠT; V1 ĐẠT; P1 ĐẠT; no-harm (a) ĐẠT; no-harm (b) ĐẠT -> **RETAINED (thành phần A, exploratory)**."

## 6. Số chi tiết (mọi số ở `results/ext_r5ngorient3_analysis/ruling.md`)

### 6.1 P1, NG-A v3 − v5_1, 8 cell primary ng_mix

| T | cell | cov v3 / v5_1 | IS v3 / v5_1 | dIS [CI] | dIS/IS | p Holm (8) |
|---|---|---|---|---|---|---|
| 80 | missing-0.2 | 0.963 / 0.961 | 2.968 / 2.978 | −0.009 [−0.023, +0.005] | −0.32% | 0.448 |
| 80 | missing-0.5 | 0.959 / 0.960 | 3.274 / 3.279 | −0.005 [−0.060, +0.052] | −0.15% | 1.000 |
| 80 | reversed-0.2 | 0.950 / 0.950 | 2.881 / 2.881 | −0.000 [−0.032, +0.032] | −0.01% | 1.000 |
| 80 | reversed-0.5 | 0.938 / 0.937 | 2.988 / 2.984 | +0.003 [−0.064, +0.072] | +0.12% | 1.000 |
| 150 | missing-0.2 | 0.970 / 0.970 | 1.789 / 1.801 | −0.012 [−0.031, +0.006] | −0.66% | 0.448 |
| 150 | missing-0.5 | 0.961 / 0.962 | 2.064 / 2.088 | −0.024 [−0.042, −0.004] | −1.14% | 0.062 |
| 150 | **reversed-0.2** | 0.965 / 0.961 | 1.804 / 1.856 | **−0.052 [−0.085, −0.020]** | −2.82% | **0.0032 (WIN)** |
| 150 | reversed-0.5 | 0.947 / 0.946 | 2.009 / 2.054 | −0.045 [−0.088, −0.004] | −2.19% | 0.092 |

Mọi cell có 20 cluster. Endpoint gộp −0.90% IS.

### 6.2 No-harm

- **(a) Gaussian, 21 cell:**
  - IS ratio 0.993–1.020; không cell nào tệ hơn sau Holm 21 (p Holm nhỏ nhất 0.83);
  - coverage v3 bằng hoặc gần bằng v5_1 (T40 reversed-0.5: 0.918 so với 0.928, vẫn ≥ 0.90);
  - 9 cell none/extra trùng từng bit;
  - cell xa nhất là T150 reversed-0.5: ratio 1.020, +0.043 [−0.008, +0.104].
- **(b) 13 cell ng_mix không primary:**
  - đạt theo rule (ratio ≤ 1.05);
  - **nhưng T40 reversed-0.5 có ratio 1.030, dIS +0.130 [+0.048, +0.223]**, CI không chứa 0, coverage 0.945 so với 0.950;
  - T40 reversed-0.2: +0.050 [−0.011, +0.118].
  - Rule (b) không dùng kiểm định nên cell này không làm hỏng verdict. Đây là dấu hiệu hại thật ở T40 reversed dưới ng_mix và phải báo cùng verdict.

### 6.3 Phụ: coverage trên cặp affected (dC ≥ 0.05), 4 cell reversed ng_mix, Holm 4

| T | cell | cov v5_1 → v3 | Δ [CI] | p Holm (4) | closed share |
|---|---|---|---|---|---|
| 80 | reversed-0.2 | 0.873 → 0.886 | +0.012 [+0.000, +0.028] | 0.175 | 0.13 |
| 150 | reversed-0.2 | 0.904 → 0.944 | **+0.040 [+0.022, +0.066]** | **0.0002** | 0.54 |
| 80 | reversed-0.5 | 0.888 → 0.896 | +0.008 [−0.002, +0.018] | 0.175 | 0.10 |
| 150 | reversed-0.5 | 0.902 → 0.909 | +0.008 [−0.010, +0.023] | 0.225 | 0.12 |

- 1/4 có ý nghĩa (v2 trên dữ liệu vòng 4: 4/4).
- Width trung vị của các cặp này gần như không đổi (ví dụ T150 rev-0.2: 1.695 → 1.721).
- Dưới Gaussian, cùng các cell: −0.028 đến +0.006.

### 6.4 Mô tả: v3 so với v2 trên cùng dữ liệu (không quyết định)

- **v2 − v5_1, endpoint gộp: −0.69% [−1.21%, −0.18%], cận trên một phía −0.27%.** Nghĩa là trên dữ liệu vòng 5, v2 cũng đạt endpoint gộp.
- **v3 − v2, endpoint gộp: −0.21% [−0.48%, +0.05%], cận trên +0.01%:** không có ý nghĩa.
  - Theo cell: v3 tốt hơn v2 ở T150 (−0.007 đến −0.019);
  - v3 tệ hơn v2 ở T80 reversed-0.2: +0.018 [+0.002, +0.039].
- **Chất lượng evidence thì khác rõ:**
  - AUROC cho cạnh pool bị đảo thật (ng_mix), v3 so với v2: T40 0.629 / 0.607, T80 0.747 / 0.715, **T150 0.858 / 0.773**.
  - Cạnh cùng kỳ thật bị xoá, p đúng chiều ở mức dữ liệu (T150): 0.742 so với 0.672; draw đúng chiều 0.695 so với 0.680.
  - Gaussian: AUROC 0.489–0.505 cho cả hai (đúng như kỳ vọng khi gate gần như đóng).
- Gate mở theo draw:
  - giống v2 vì gate không đổi: Gaussian 0.078 / 0.119 / 0.160 ở T40/80/150 (gộp 0.123);
  - ng_mix 0.140 / 0.439 / 0.752.
- Runtime (tổng trong method): ng_mix v5_1 626 s, v2 894 s, v3 925 s (+48%); Gaussian 627 / 785 / 789 s.

## 7. Kết luận

1. **Verdict theo rule ghi trước: thành phần A (v5_1 + NG-A v3) RETAINED (exploratory).** V0, V1, P1, no-harm (a) và (b) đều đạt. Thành phần A được giữ cho `tolerant_v5_2`.
2. **Lỗi cấu tạo đã sửa được ở mức unit test.**
   - Tỷ lệ sai chiều khi gate mở trên hỗn hợp ng_mix (b 0.6) giảm theo m: 0.114 / 0.058 / 0.018, so với 0.184 / 0.164 / 0.150 của v2.
   - t5 → uniform ở m 400: 0.036 so với 0.462.
   - Trên bank, AUROC của evidence cho cạnh bị đảo ở T150 tăng từ 0.77 lên 0.86.
3. **Nhưng lợi ích IS nhỏ và không riêng của bản sửa.**
   - Endpoint gộp là −0.9% IS; chỉ 1/8 cell qua Holm.
   - v2 cũng đạt endpoint gộp trên cùng dữ liệu (−0.7%).
   - v3 so với v2 không khác có ý nghĩa (−0.2%, CI chứa 0).
   - Câu đúng là: "orientation theo non-Gaussianity (v2 hay v3) giảm IS khoảng 1% dưới shock non-Gaussian tổng hợp ở T ≥ 80, không hại dưới Gaussian; bản sửa luật dấu cải thiện evidence rõ nhưng chưa chuyển thành IS khác biệt đo được". Không nên viết "sửa luật dấu làm IS tốt hơn".
4. **Cảnh báo phải đi kèm verdict:**
   - ng_mix T40 reversed-0.5 tệ hơn với CI không chứa 0 (+0.130, ratio 1.030), vẫn trong ngưỡng 1.05 của rule;
   - Gaussian T150 reversed-0.5 ratio 1.020;
   - gate mở dưới Gaussian ở T150 là 0.16, trên mức danh nghĩa 0.10 (giống v2).
5. **Giới hạn:**
   - Dữ liệu là 20 topology của D-07 đã dùng nhiều lần; seed mới chỉ làm mới truth, skeleton hỏng và dữ liệu.
   - Endpoint gộp được chọn sau khi thấy v2.
   - V1 (ii) chỉ có 6 run không mở gate nào, nên kiểm tra đó yếu; phần identity chính là 1080/1080 run none/extra.
   - Kết quả chỉ là exploratory. Kiểm tra trên topology mới (P4-H2 development) là quyết định của người dùng, theo mục 4.3 của synthesis, và nên xét cùng kết quả của thành phần B.

## 8. Bug và quan sát về file có sẵn (không sửa)

- Không thấy bug mới trong `ext_r4ngorient.py`, `run_ng.py`, `laws.py`, `ext_v51.py`.
  - Nhánh copy với evidence v2 trùng `tolerant_ngA` 28/28.
  - Driver ghi đúng factor frozen (2520/2520).
- `numpy` trên máy này (Accelerate, macOS) phát RuntimeWarning "divide by zero/overflow encountered in matmul" giả trong `estimator.py`, `ext_narrow.py`, `methods.py` khi chạy ngoài driver (driver tắt RuntimeWarning). Kết quả không bị ảnh hưởng (copy check trùng từng bit).

## 9. Split đã dùng

- D-07H development: code check (seed_base 70261102 + 700 000, 2 unit, ng_mix), không tính IS hay coverage.
- D-07 development: seed_base 70261102 (ng_mix, gauss).
- V0: dữ liệu mô phỏng 2 biến (seed 70261104). Design check: seed 999.
- Không đụng P4-H1, P4-H2 (cả hai split) hay confirmatory split nào. Không có calibration nào.
