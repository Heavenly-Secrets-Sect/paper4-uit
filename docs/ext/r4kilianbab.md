# Vòng 4, ứng viên "kilianbab": bootstrap-after-bootstrap của Kilian (1998) bên trong `tolerant_v5_1`

**Trạng thái.** Exploratory. Đánh giá chỉ trên D-07 development (seed_base 20261102); calibration chỉ trên D-07H development; probe và test chỉ trên D-07H development (seed riêng 777001). Không chạm P4-H2 (cả hai split), P4-H1 hay split confirmatory nào. Không gọi LLM. Không commit.

**File (chỉ file mới).**
- Code: `src/paper4/ext_r4kilianbab.py` (đăng ký `r4kilianbab_bab`, `r4kilianbab_babbc`, `r4kilianbab_babraw`; không đăng ký lại tên có sẵn nào).
- Driver và script: `experiments/ext/r4kilianbab/` (`run_bab.py`, `test_bab.py`, `analyze.py`).
- Config: `experiments/configs/ext_r4kilianbab_eval.json` (grid G), `ext_r4kilianbab_a1.json` (latent1 / noise0.1), `ext_r4kilianbab_smoke.json` (smoke, D-07H).
- Kết quả: `results/ext_r4kilianbab_*`.

---

## 1. Nguồn và ý tưởng

| Nguồn | Dùng gì |
|---|---|
| Kilian L. (1998), *Small-sample confidence intervals for impulse response functions*, REStat 80(2):218–230, doi:10.1162/003465398557465 | Toàn bộ thủ tục: stage 1 ước lượng bias bằng bootstrap; hiệu chỉnh B̂ với stationarity adjustment (không sửa nếu B̂ không dừng; nếu B̂ − Ψ̂ không dừng thì giảm hệ số δ theo bước 0.01); stage 2 bootstrap từ B̃, mỗi draw được sửa bằng **cùng** Ψ̂ của stage 1 với cùng stationarity adjustment; percentile interval |
| Pope A.L. (1990), JTSA 11(3):249–258 | Bias của LS trong VAR là O(1/T) và kéo độ bền (persistence) về 0; dùng để đối chiếu độ lớn bias của stage 1 trong test AR(1) |
| Engsted T., Pedersen T.Q. (2014), Econometrics 2(1):45–71 | So sánh bias correction bằng bootstrap và giải tích trong VAR: sửa bias có thể tăng variance; stationarity adjustment là cần thiết. Đây là lý do có arm K0 và log tần suất shrink |
| Efron B. (1987), JASA 82(397):171–185 | Bias-corrected percentile (BC, a = 0): endpoint Φ(2z0 + z_α), z0 = Φ⁻¹(tỷ lệ draw < θ̂) |
| Kilian L. (1999), REStat 81(4):652–660 | Percentile-t kém ở T nhỏ, nên không dùng |

**Giả thuyết.** Ở T = 40/80, percentile interval của v5.1 được dựng quanh một fit có hệ số lag bị co về 0 (bias LS mẫu nhỏ, Pope 1990). Bootstrap từ fit đó còn co thêm một lần nữa, nên interval lệch về phía 0 và trượt ở một phía. Factor width hai chiều của v5.1 bù bằng cách nới cả hai phía. Re-centre bằng BaB có thể cho factor K1 nhỏ hơn và IS thấp hơn ở cell missing/reversed khi T ≤ 80; ở T = 150 gần như không đổi.

**Khác với probe vòng v3 đã bị loại** (docs/decision_rules.md, mục v3: IS reversed-0.5 T80 từ 3.5 lên 5.4). Probe đó đọc bias từ các draw có rút lại cấu trúc, nên độ biến thiên do lật chiều cũng bị tính thành bias. Ở đây stage 1 refit với **cấu trúc cố định** (`fit.terms`): không chọn lại, không repair BH, không lật chiều.

## 2. Thiết kế (chốt trước khi chạy D-07)

1. **Bước (1)–(4) không đổi.** Hai nhánh của v5.1 (`ext_v51.tolerant_sel_dd` khi khai báo thiếu cạnh và r < TAU; `methods.tolerant(target_reversal=True)` nếu không) được chép từng dòng tới chỗ gọi `bootstrap_C`. Kiểm tra identity: khi ép bias = 0 (B1 = 0, không tiêu random number nào), interval của K1 trùng **từng bit** với `tolerant_v5_1` ở 14/14 cell (T 40/80 × 7 cell, một unit D-07H, n_boot 49): `results/ext_r4kilianbab_tests/tests.json`, khoá `identity`.
2. **Stage 1.** Từ `fit` (fit mà v5.1 đưa vào `simulate_from_fit`), rút B1 = 99 chuỗi residual-bootstrap, refit với `fit.terms` cố định. bias = mean_b(B*_b[1:]) − fit.B[1:], chỉ giữ ở vị trí lag ≥ 1 có trong `fit.terms`. B0 không bao giờ bị sửa; số 0 do chọn cấu trúc không bao giờ bị chạm.
3. **Hiệu chỉnh fit dữ liệu.** Nếu companion_radius(fit.B) ≥ 1: không sửa. Ngược lại B_c[1:] = fit.B[1:] − d·bias, d = 1, giảm 0.01 mỗi bước tới khi radius < 1. (Kilian 1998 viết bước giảm dưới dạng đệ quy trên Ψ; bản tuyến tính ở đây là cách Kilian và Lütkepohl trình bày lại. Hai cách chỉ khác khi shrink xảy ra, và chỉ ở chữ số thập phân thứ hai của d.)
4. **Stage 2.** `fit_c` = `fit` với B thay bằng B_c; intercept, residual gốc và dof giữ nguyên. Mỗi draw mô phỏng từ `fit_c`, chạy lại (1)–(4) đúng như v5.1, rồi trừ d_b·bias tại các vị trí vừa nằm trong lag term của chính draw đó vừa nằm trong support của bias, với cùng stationarity adjustment (không sửa draw có radius ≥ 1), rồi mới tính C(H) = cumulative(irf). Point estimate = mean của các draw đã sửa.
5. **Arm** (một bộ draw cho cả ba arm, nên khác biệt giữa các arm không chứa Monte Carlo noise):
   - **K1** `r4kilianbab_bab`: percentile của draw đã sửa, pre-scale 0.5 như v5.1, factor width hai chiều **tune lại** trên D-07H development bằng `run_experiment.calibrate` (cùng grid 1.0–10, cùng seed calibration như v5.1).
   - **KBC** `r4kilianbab_babbc`: draw của K1, endpoint BC Φ(2z0 + z_a) theo từng cặp, z0 = Φ⁻¹(tỷ lệ draw < Ĉ), **Ĉ = C(H) của `fit_c`** (tâm của thế giới bootstrap, tức ước lượng BaB của Kilian), |z0| cap 0.5; cặp có > 20% draw trùng một giá trị thì dùng percentile thường. Pre-scale 0.5, factor tune riêng.
   - **K0** `r4kilianbab_babraw`: percentile của draw đã sửa, **không** pre-scale, **không** factor.
6. **Log mỗi run:** d của fit dữ liệu, cờ không sửa / shrink, radius trước/sau, tỷ lệ draw bị shrink và tỷ lệ draw không sửa, |bias| trung bình theo lag (tách own-lag và cross), bias có dấu của own-lag; với KBC: tỷ lệ cặp bỏ BC vì tie, tỷ lệ cap, |z0| trung bình.

**Tinh chỉnh so với đề xuất ban đầu (trước khi pre-register, có lý do):**
- (a) Grid G có **21 cell** (3 T × 7 cell: none, extra/missing/reversed × 0.2/0.5), không phải 19. Vậy 8 cell primary và **13** cell còn lại (đề xuất ghi 11). No-harm dùng Holm trên 13.
- (b) Thêm điều kiện **không tệ hơn có ý nghĩa ở cell primary** (Holm trên 8, một phía dIS > 0). Lý do: đề xuất chỉ đếm thắng; một arm thắng 3 và thua 2 cell primary không nên được giữ. Tripwire T80 reversed-0.5 là một trường hợp riêng của điều kiện này và vẫn giữ nguyên hiệu lực "REJECTED bất kể điều gì khác".
- (c) Thêm điều kiện về run thất bại: arm không được có ít run ok hơn v5.1 ở cell nào. Lý do: IS ghép cặp chỉ tính run cả hai đều ok, nên thất bại có thể bị che.
- (d) Driver riêng (`run_bab.py`) thay cho `run_experiment.py --config`: chỉ tune lại factor cho K1/KBC (v5.1 đọc factor frozen), và thêm chẩn đoán phía truth vào mỗi dòng kết quả (centring có dấu, miss về phía 0 hay phía xa, oracle_cal). Method không thấy các đại lượng này. Driver gọi nguyên `run_unit`, `calibrate`, `summarize` của runner.
- (e) Ghép cặp với run cũ: `tolerant_v5_1` chạy lại trong cùng run (cùng seed, cùng thứ tự cell như `ext_v51_eval`, bug E1). Mọi so sánh trong rule dùng dòng v5.1 của **chính run này**. Kiểm tra identity với `results/ext_v51_eval/runs.jsonl` (cùng status, |ΔIS| < 1e-12, cùng số đếm, đủ 1260 khoá) chỉ là kiểm tra reproducibility và được công bố; nếu lệch thì verdict không đổi.
- (f) Nếu cả K1 và KBC đều RETAINED, chọn arm thắng nhiều cell primary hơn; hòa thì chọn IS trung bình thấp hơn trên 8 cell primary; vẫn hòa thì chọn K1 (đơn giản hơn).

## 3. Đánh giá

**Grid G.** D-07 development, 20 topology × 3 replicate, seed_base 20261102, thứ tự cell như `experiments/configs/ext_v51_eval.json`. T ∈ {40, 80, 150} × {none, extra/missing/reversed × 0.2/0.5}; H = 4, lag_max = 2, n_boot = 199, tau_effect = 0.1. Methods: `tolerant_v5_1` (factor frozen `experiments/ext/v51/frozen_v4_v51.json`, đủ 12 khoá `tolerant_v5_1|T|kind` cho T 40/80/150), K1, KBC, K0, `oracle` (tham chiếu; `oracle_cal` = oracle nới 1.4 / 1.3 / 1.2 ở T 40 / 80 / 150). Calibration K1/KBC: D-07H development, 1 replicate, kinds extra/missing/reversed × 0.2/0.5. `--workers 3`. Ước tính ≤ 30 phút (smoke và timing: K-core thêm khoảng 0.2–0.5 s mỗi lần gọi so với v5.1).

**Thứ cấp (mô tả, không quyết định).** Kịch bản latent1 và noise0.1, T ∈ {80, 150}, cell none / missing-0.2 / reversed-0.2 (đúng danh sách cell của `ext_v51_a1`, để dòng v5.1 ghép được với run cũ). Factor K1/KBC lấy từ calibration của run chính, không tune lại.

**Thống kê.** Với mỗi cell và mỗi arm: dIS = mean IS(arm) − mean IS(v5.1), trên các run cả hai cùng ok (IS = mean interval score trên cặp non-null của run). CI 95% bằng cluster bootstrap theo topology (20 cluster, B = 20000, seed 20261104; thống kê = tổng hiệu / tổng số run trong các cluster được rút). p một phía cho dIS < 0: (1 + #{boot ≥ 0}) / (B + 1); cho dIS > 0: (1 + #{boot ≤ 0}) / (B + 1). Coverage = gộp trên cặp non-null của các run ok. Holm step-down ở mức 0.05.

## 4. Quy tắc ghi trước (2026-11-02T12:15Z, trước mọi run trên D-07)

**Cell primary (8):** T ∈ {40, 80} × {missing, reversed} × {0.2, 0.5}. **Cell khác (13):** none ở cả 3 T, extra ở cả 3 T, missing và reversed ở T = 150.

**R1. Thắng.** Một cell primary là WIN của arm nếu Holm (8 cell, một phía dIS < 0, mức 0.05) bác H0 **và** coverage gộp của arm ≥ 0.90 **và** arm có số run ok ≥ v5.1 ở cell đó.

**R2. K1 hoặc KBC được RETAINED (exploratory)** nếu đồng thời:
1. WIN ở ≥ 3/8 cell primary;
2. coverage ≥ 0.90 ở cả 8 cell primary;
3. không cell primary nào tệ hơn có ý nghĩa (Holm 8 cell, một phía dIS > 0, mức 0.05);
4. no-harm trên 13 cell khác: tỷ lệ IS(arm)/IS(v5.1) ≤ 1.05 ở mọi cell; không cell nào tệ hơn có ý nghĩa (Holm 13 cell, một phía dIS > 0, mức 0.05); coverage ≥ 0.90 ở mọi cell mà v5.1 có coverage ≥ 0.90;
5. số run ok ≥ v5.1 ở cả 21 cell.

**R3. Tripwire.** Nếu T80 reversed-0.5 tệ hơn có ý nghĩa sau Holm (họ 8 cell, một phía dIS > 0), arm bị **REJECTED** bất kể các điều kiện khác.

**R4. K0 được RETAINED với nhãn "factor-free"** chỉ nếu coverage ≥ 0.90 ở cả 21 cell **và** non-inferior so với v5.1 ở ≥ 6/8 cell primary, với non-inferior nghĩa là cận trên CI 95% của dIS < 0.05 × IS(v5.1) của cell đó. Dự đoán: K0 **không** đạt (bias correction không xử lý lỗi chọn cấu trúc hay lỗi chiều).

**R5. Chọn giữa K1 và KBC** khi cả hai được giữ: tinh chỉnh (f) ở mục 2.

**R6. Overlay họ.** Holm 0.05 trên 16 test primary (8 của K1 + 8 của KBC), báo cạnh verdict, không đổi verdict. p-value thô của mọi test được ghi vào `results/ext_r4kilianbab_eval/ruling.json` để lead gộp Holm qua các ứng viên vòng 4.

**Dự đoán ghi trước (mô tả, không đổi verdict):**
- P-a. Factor hiệu dụng của K1 ở T40 missing thấp hơn của v5.1 (1.15) ít nhất 0.10.
- P-b. dIS < 0 ở các cell missing/reversed khi T ≤ 80.
- P-c. Ở T = 150, CI của dIS chứa 0 ở mọi cell.
- P-d. Tripwire không kích hoạt (T80 reversed-0.5 không tệ hơn).
- P-e. Với v5.1 ở T 40/80, median sai số có dấu sign(C_true)·(midpoint − C_true) trên cặp non-null âm (interval lệch về phía 0), và đa số miss nằm ở phía 0; BaB kéo đại lượng này về gần 0.

**Báo cáo bắt buộc:** bảng factor K1/KBC so với v5.1; |bias| trung bình theo lag; tần suất shrink (fit dữ liệu và draw); median sai số centring có dấu trên cặp non-null; mọi số trích dẫn được ghi vào `results/ext_r4kilianbab_*`; mỗi số đếm Holm đi kèm số đếm thô.

**Không đổi rule sau khi có kết quả.** Một bản thiết kế lại là phiên bản mới với rule mới.

---

## 5. Kết quả (ghi sau run, 2026-11-02; rule ở mục 4 không đổi)

**Run.** `results/ext_r4kilianbab_eval` (6300 dòng, 1325.7 s gồm calibration 138.8 s, `--workers 3`, máy dùng chung với các agent khác nên load average lên khoảng 60). Bắt đầu 12:15:44Z, kết thúc 12:37:53Z. Hash của doc này, module, driver và config lúc pre-register: `results/ext_r4kilianbab_tests/prereg_hashes.txt`. Không file nào trong số đó bị sửa sau khi run bắt đầu (doc chỉ được append).

**Ghép cặp.** Dòng `tolerant_v5_1` của run này so với `results/ext_v51_eval`: **1260/1260 identical** (status, |ΔIS| < 1e-12, số đếm). Ghép cặp thật.

### 5.1 Verdict, nguyên văn từ `results/ext_r4kilianbab_eval/ruling.md`

- **r4kilianbab_bab**: WIN 0/8 after Holm (raw 0/8); coverage >= 0.90 in all 8 primary: True; primary significantly worse: 3/8 after Holm (raw 5/8); no-harm other 13: False (IS ratio > 1.05: 4/13; worse after Holm: 3/13, raw 7/13; coverage gate fails: 0/13); failures <= v5_1 in all 21: True; tripwire T80 reversed-0.5: False (p> = 0.3082) -> **NOT RETAINED**
- **r4kilianbab_babbc**: WIN 0/8 after Holm (raw 0/8); coverage >= 0.90 in all 8 primary: True; primary significantly worse: 8/8 after Holm (raw 8/8); no-harm other 13: False (IS ratio > 1.05: 5/13; worse after Holm: 4/13, raw 4/13; coverage gate fails: 0/13); failures <= v5_1 in all 21: True; tripwire T80 reversed-0.5: True (p> = 0.0001) -> **REJECTED (tripwire)**
- **r4kilianbab_babraw**: coverage >= 0.90 in all 21: False (fails 4/21); non-inferior 0/8 -> **NOT RETAINED**
- Family overlay (Holm 0.05 over 16 primary tests of K1 + KBC): rejected 0 (K1 0, KBC 0).
- Selected arm (R5): None

**Kết luận: ứng viên kilianbab bị loại ở cả ba arm.** Không có Frozen spec.

### 5.2 Cell primary (coverage / IS; dIS = arm − v5.1 [CI 95%])

| T | cell | v5.1 | K1 | dIS K1 | KBC | dIS KBC |
|---|---|---|---|---|---|---|
| 40 | missing-0.2 | 0.922 / 4.84 | 0.927 / 5.04 | +0.20 [+0.05, +0.35] | 0.942 / 5.75 | +0.91 [+0.59, +1.20] |
| 40 | missing-0.5 | 0.939 / 5.09 | 0.944 / 5.22 | +0.13 [+0.00, +0.26] | 0.949 / 6.44 | +1.35 [+0.99, +1.70] |
| 40 | reversed-0.2 | 0.928 / 4.70 | 0.944 / 5.09 | +0.39 [+0.12, +0.66] | 0.949 / 5.26 | +0.56 [+0.22, +0.86] |
| 40 | reversed-0.5 | 0.920 / 4.74 | 0.940 / 5.10 | +0.36 [+0.26, +0.46] | 0.930 / 5.58 | +0.84 [+0.66, +1.01] |
| 80 | missing-0.2 | 0.949 / 2.84 | 0.942 / 2.93 | +0.09 [+0.01, +0.17] | 0.938 / 3.00 | +0.16 [+0.05, +0.29] |
| 80 | missing-0.5 | 0.951 / 3.10 | 0.955 / 3.17 | +0.07 [−0.02, +0.16] | 0.933 / 3.45 | +0.36 [+0.18, +0.56] |
| 80 | reversed-0.2 | 0.941 / 2.79 | 0.931 / 2.83 | +0.04 [−0.06, +0.14] | 0.957 / 2.92 | +0.13 [−0.02, +0.27] |
| 80 | reversed-0.5 | 0.918 / 3.05 | 0.910 / 3.07 | +0.02 [−0.08, +0.11] | 0.920 / 3.40 | +0.35 [+0.17, +0.54] |

Điểm ước lượng dIS của K1 dương ở cả 8 cell primary; không cell nào có dIS < 0.

### 5.3 Dự đoán ghi trước

| Dự đoán | Kết quả |
|---|---|
| P-a: factor hiệu dụng K1 ở T40 missing thấp hơn v5.1 ≥ 0.10 | **Đúng**: 1.00 so với 1.15 (−0.15). Factor K1 thấp hơn v5.1 ở 12/12 ô (T, kind), từ −0.05 đến −0.20 |
| P-b: dIS < 0 ở missing/reversed khi T ≤ 80 | **Sai**: 0/8 (mọi điểm ước lượng dương) |
| P-c: T150 không đổi (CI chứa 0) | **Sai một phần**: CI của K1 chứa 0 ở 2/7 cell T150; 5/7 tệ hơn nhẹ (+0.03 đến +0.12) |
| P-d: tripwire không kích hoạt | **Đúng cho K1** (T80 reversed-0.5: +0.02 [−0.08, +0.11], p> = 0.31); **sai cho KBC** (+0.35, p> = 0.0001) |
| P-e: v5.1 lệch về phía 0; BaB kéo về gần 0 | **Đúng**: midpoint của v5.1 lệch về 0 ở 8/8 cell primary, và 97–100% số miss của v5.1 ở T 40/80 nằm ở phía 0. K1 giảm độ lệch ở 8/8 cell (ví dụ T40 missing-0.2: −0.36 → −0.17; T80 reversed-0.5: −0.27 → −0.14) và giảm tỷ lệ miss phía 0 xuống 0.77–0.98 |
| K0 không đạt 0.90 ở mọi cell | **Đúng**: 4/21 cell dưới 0.90 (thấp nhất 0.868 ở T80 reversed-0.5); non-inferior 0/8 |

### 5.4 Chẩn đoán Kilian (mean trên run ok; bảng đầy đủ trong `ruling.md`)

- **|bias| trung bình theo lag** (stage 1, cấu trúc cố định): lag 1 khoảng 0.029–0.035 ở T40, 0.017–0.019 ở T80, 0.011–0.012 ở T150; lag 2 khoảng 0.027–0.029 / 0.015 / 0.009. Bias own-lag-1 có dấu âm, khoảng −0.056 đến −0.070 ở T40, −0.030 đến −0.043 ở T80, −0.016 đến −0.025 ở T150: đúng chiều và gần cỡ của Pope/Kendall (test AR(1) ρ = 0.9, T = 40: stage 1 cho −0.089, Monte Carlo −0.109, xấp xỉ −(1+3ρ)/T = −0.093; `results/ext_r4kilianbab_tests/tests.json`).
- **Stationarity shrink.** Ở T40, fit dữ liệu bị shrink trong 10–30% run (không sửa vì B̂ không dừng: 0–6.7%). Ở cấp draw: 31–50% draw bị shrink và 9–45% draw không được sửa (missing-0.5: 45%), d trung bình theo draw chỉ 0.38–0.77. Ở T80 shrink gần như không xảy ra (draw: 1.6–6.4%), ở T150 bằng 0.
- **KBC.** z0 trung bình gần 0 (|mean z0| ≤ 0.014), |z0| trung bình 0.15–0.28; cap 0.5 chạm ở 2–27% số cặp (cao nhất ở reversed-0.5). Hầu như không cặp nào bị bỏ BC vì tie.

### 5.5 Đọc kết quả

1. **Giả thuyết cơ chế đúng, nhưng không thành lợi ích về IS.** Interval của v5.1 thật sự lệch về phía 0. Ở T 40/80, gần như mọi miss nằm ở phía 0 (97–100%), trong khi oracle là 89–95%. BaB sửa được khoảng một nửa độ lệch, và factor tune lại giảm 0.05–0.20 (hiệu dụng). Vậy có thể nói: **một phần nhỏ của factor width hai chiều là bias mẫu nhỏ.** Ở T40, khoảng 0.15–0.20 trên phần vượt 1.0 (0.15–0.40) của factor v5.1.
2. **Vì sao IS vẫn tệ hơn.** Bias correction làm phân phối draw rộng hơn (Engsted và Pedersen 2014 đã cảnh báo variance tăng). Ở T40, width median của K1 lớn hơn v5.1 dù factor nhỏ hơn: missing-0.2 3.45 so với 3.29, reversed-0.5 3.74 so với 3.28. Nguyên nhân là (i) correction đẩy độ bền của mô hình lên gần biên dừng (companion radius trung bình của fit dữ liệu tăng từ 0.879 lên 0.933 ở T40, 0.807 → 0.843 ở T80, 0.781 → 0.802 ở T150; `results/ext_r4kilianbab_eval/radius.txt`), nên C(H) của các draw nhạy hơn, và (ii) stationarity shrink chỉ áp cho một phần draw, nên trộn draw sửa đủ, sửa một phần và không sửa. Kết quả là phân phối draw dàn rộng ra. Sai số tuyệt đối median của point estimate gần như không đổi (0.553 → 0.527 ở T40 missing-0.2; 0.506 → 0.523 ở T40 reversed-0.5).
3. **Ước lượng bias với cấu trúc cố định đúng là tránh được tác hại kiểu probe v3 ở T80 reversed-0.5** (K1 +0.02, không ý nghĩa; probe v3 trên 10 topology từng đẩy IS từ 3.5 lên 5.4). Nhưng ở T40, reversed-0.5 vẫn tệ hơn (+0.36), cùng chiều với bias variance ở trên.
4. **BC còn tệ hơn.** BC dịch endpoint về phía đuôi dài của từng cặp, nhưng z0 không có thông tin về chiều lệch (trung bình gần 0). Kết quả là interval rộng và lệch ngẫu nhiên, thua ở 8/8 cell primary sau Holm.
5. **K0 (không factor) không thay được factor.** Coverage 0.868–0.957, dưới 0.90 ở 4/21 cell. Bias correction không xử lý lỗi chọn cấu trúc hay lỗi chiều, đúng như dự đoán.

**Gợi ý cho paper (exploratory, không phải claim):** có thể ghi trong phần threats/discussion rằng factor width của v5.1 không chủ yếu là bù bias mẫu nhỏ. Re-centre theo Kilian giảm factor 0.05–0.20, nhưng tăng IS 1–8% ở T ≤ 80. Không đề xuất dùng BaB.

### 5.6 Kịch bản thứ cấp (mô tả, không quyết định): `results/ext_r4kilianbab_a1/describe.md`

Run: 3600 dòng, 839.2 s, `--workers 3`, factor K1/KBC lấy từ calibration của run chính. Dòng v5.1 so với `results/ext_v51_a1` (latent1, noise0.1): **720/720 identical**.

| Kịch bản | K1 − v5.1 | KBC − v5.1 |
|---|---|---|
| latent1 (6 cell) | Tệ hơn ở 6/6 cell: +0.23 đến +0.55; coverage giảm 0.013–0.034 (thấp nhất 0.895 ở T80 none) | Tệ hơn ở 6/6 (+0.21 đến +0.56; 5/6 có CI trên 0) |
| noise0.1 (6 cell) | Bằng hoặc tốt hơn nhẹ: −0.14 [−0.26, −0.03] ở T150 missing-0.2; các cell còn lại có CI chứa 0 | Tốt hơn ở T80 none (−0.21) và T150 none (−0.20); còn lại có CI chứa 0 |

Holm trên 12 cell (một phía, tệ hơn): K1 5/12 (thô 6/12), KBC 5/12 (thô 5/12). Tất cả đều ở latent1.

**Đọc.**
- Với biến ẩn, bias correction sửa "bias mẫu nhỏ" của một mô hình vốn sai do confounder. Kết quả là nó đẩy thêm độ bền giả và làm hại.
- Với nhiễu đo 10%, attenuation bias cùng chiều với bias mẫu nhỏ (kéo về 0), nên re-centre giúp một chút. Mức giúp quá nhỏ để thành hướng sửa cho giới hạn nhiễu đo.

## 6. Tổng kết

- **Verdict:** K1 NOT RETAINED; KBC REJECTED (tripwire); K0 NOT RETAINED. Không có arm nào được giữ, nên **không có Frozen spec** và không đề xuất chạy bank held-out.
- **Điều học được:**
  - Interval của v5.1 lệch có hệ thống về phía 0 ở T ≤ 80: 97–100% số miss nằm ở phía 0.
  - BaB sửa được khoảng một nửa độ lệch, và giảm factor width 0.05–0.20.
  - Đổi lại, phân phối draw rộng hơn (bias correction tăng variance và đẩy radius lên gần 1), nên IS tệ hơn 1–8% ở T ≤ 80 và hại rõ khi có biến ẩn.
  - Câu trả lời cho reviewer hỏi "factor có phải chỉ bù bias không?" là **không, chỉ một phần nhỏ**.
- **Bug trong file có sẵn:** không phát hiện.
- **Khác biệt so với đề xuất:** grid G có 21 cell chứ không phải 19 (mục 2, tinh chỉnh a). Ngoài ra không có sai lệch nào khác so với thiết kế đã ghi trước.
- **Toàn bộ số trích dẫn** nằm trong:
  - `results/ext_r4kilianbab_eval/` (`ruling.md`, `ruling.json`, `calibration.json`, `radius.txt`, `summary.md`);
  - `results/ext_r4kilianbab_a1/` (`describe.md`, `describe.json`);
  - `results/ext_r4kilianbab_tests/` (`tests.json`, log, timestamp, hash pre-register).
- **Split đã dùng:** D-07 development (eval và thứ cấp), D-07H development (calibration, test seed 777001, smoke). Không chạm P4-H1, P4-H2 hay split confirmatory nào.
- **Kiểm tra pre-register:**
  - Phần doc trước mục 5 có sha256 `532271fa…bcf`, trùng hash ghi lúc 12:15:44Z (`prereg_hashes.txt`).
  - Module, driver và config chính cũng trùng hash (`shasum -c`: OK).
  - Hash của cả file doc khác đi chỉ vì các mục 5–6 được append.
