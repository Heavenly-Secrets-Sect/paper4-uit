# Vòng 4, ứng viên `levboot`: residual hiệu chỉnh leverage (HC2/HC3) trong residual bootstrap của `tolerant_v5_1`

**Trạng thái:** exploratory, chỉ trên D-07 development (seed_base 20261102 cho grid G, 20261101 cho grid lag_max 1/4 như `ext_region51_lag*`). Calibration và probe chỉ trên D-07H development. Không chạm P4-H1, P4-H2 (cả hai split) hay bất kỳ split confirmatory nào. Không gọi LLM. Không commit.

**File của hướng này (tất cả là file mới):**
- Module: `src/paper4/ext_r4levboot.py` (METHODS: `r4levboot_L2`, `r4levboot_L3`, `r4levboot_W3`; `r4levboot_U` chỉ để kiểm tra identity).
- Driver: `experiments/ext/r4levboot/run.py` (gọi runner không sửa, thêm log raw coverage và failure rate).
- Probe / test: `experiments/ext/r4levboot/probe_identity.py`, `experiments/ext/r4levboot/test_analyze.py`.
- Analyzer: `experiments/ext/r4levboot/analyze.py`.
- Config: `experiments/configs/ext_r4levboot_{g,gw,lag1,lag4,smoke_d07h}.json`.
- Kết quả: `results/ext_r4levboot_*`.

---

## 1. Kỹ thuật và mức trung thành với nguồn

**Nguồn:**
- Wu, C.F.J. (1986). *Jackknife, bootstrap and other resampling methods in regression analysis.* Ann. Statist. 14(4):1261–1295. Wu chỉ ra residual bootstrap thường cho variance estimator bị lệch khi có leverage hoặc heteroskedasticity, và đề xuất weighted (wild-type) bootstrap với residual chia cho sqrt(1 − h_t).
- MacKinnon, J.G., White, H. (1985). J. Econometrics 29(3):305–325. Các biến thể HC2 (r_t² / (1 − h_t)) và HC3 (r_t² / (1 − h_t)²) của heteroskedasticity-consistent covariance.
- Davidson, R., Flachaire, E. (2008). *The wild bootstrap, tamed at last.* J. Econometrics 146(1):162–169. Wild bootstrap với trọng số Rademacher, residual được biến đổi theo leverage (dạng HC3: r_t / (1 − h_t)); Rademacher cho ERP nhỏ nhất ở mẫu nhỏ.

Lưu ý về việc đọc nguồn: trong vòng này mình chỉ đọc được abstract/trang tóm tắt (STICERD cho Davidson–Flachaire; Project Euclid và bản PDF không tải được). Công thức HC2/HC3 và dạng transform theo leverage là kiến thức chuẩn, nhưng **không được đối chiếu với full text trong vòng này**.

**Design (thay đổi duy nhất: `estimator.simulate_from_fit`).** Với mỗi phương trình j, dựng lại design X_j = [1, data[rows − lag, i] cho (i, lag) ∈ fit.terms[j]] của **fit dữ liệu mà v5_1 truyền vào bootstrap**: fit có các lag block đã mở theo targeted opening, cùng các cạnh cùng kỳ đã repair hoặc lật. Leverage h_tj = rowsum(Q²) từ reduced QR của X_j; nếu X_j rank deficient thì dùng SVD có rank tolerance. FLOOR = 0.05.

| Arm | Residual pool | Resampling |
|---|---|---|
| `tolerant_v5_1` (tham chiếu) | (r − mean) · sqrt(m / dof_j) | cả dòng, `rng.integers(0, m, T − p)` |
| `r4levboot_L2` | r_tj / sqrt(max(1 − h_tj, 0.05)), centre theo cột, không rescale dof | như v5_1 |
| `r4levboot_L3` | r_tj / max(1 − h_tj, 0.05), centre theo cột, không rescale dof | như v5_1 |
| `r4levboot_W3` (bổ sung) | r_tj / max(1 − h_tj, 0.05), không centre | **wild, recursive design**: u*_t = e_t · η_t, η_t Rademacher, một η_t cho cả dòng (giữ phụ thuộc giữa các phương trình), dòng giữ đúng thời điểm t |

Phần còn lại của v5_1 giữ nguyên từng dòng: screening, targeted opening (re-select mỗi draw), repair, reversal, percentile 199 draw, PRESCALE 0.5 và width factor của runner theo (T, stated kind). Factor của các arm được **re-tune trên D-07H development**. `tolerant_v5_1` dùng factor frozen trong `experiments/ext/v51/frozen_v4_v51.json`; file này có đủ key `tolerant_v5_1|{40,80,150}|{none,extra,missing,reversed}` cho grid G (lag_max 2).

**Cách thay hàm mà không sửa `estimator.py`.** Trong lúc gọi, method gán tạm `estimator.simulate_from_fit` bằng hàm mới. `estimator.bootstrap_C` tra tên này lúc gọi, nên dùng đúng hàm mới. Khối `finally` trả hàm gốc về. `estimator.cumulative` cũng được bọc tạm để đếm số draw thành công. Không file nào bị sửa.

**Common random numbers (CRN), bổ sung.** Khi generator đến từ runner (`default_rng([unit, 3, T, cell, tag])`), arm re-seed bằng stream tag của `tolerant_v5_1`. L2/L3 vì vậy rút **đúng các dòng, đúng chiều repair và đúng các lần lật** như v5_1, nên hiệu IS chỉ còn phản ánh residual pool. W3 rút dấu Rademacher thay cho chỉ số dòng, nên các số ngẫu nhiên phía sau lệch đi. Việc này không dùng thông tin gì về truth.

**Điểm lệch so với nguồn (cần nói rõ trong paper nếu dùng):**
1. Trong Wu (1986) và Davidson–Flachaire (2008), transform theo leverage dùng cho **wild bootstrap fixed-design**: residual ở lại với dòng của nó, nên dòng có leverage cao vẫn nằm đúng chỗ ảnh hưởng tới phương sai hệ số. L2/L3 lại **resample dòng iid**, nên residual bị đưa sang thời điểm ngẫu nhiên. Phép biến đổi khi đó chỉ đổi phương sai và hình dạng của pool, không gắn lại với dòng leverage cao. Đây là dạng "modified residuals" quen thuộc của residual bootstrap (mình nhớ là Davison & Hinkley 1997, mục 6.2, nhưng không kiểm tra lại trong vòng này). W3 là dạng trung thành với nguồn nhất mà vẫn chạy được trong SVAR đệ quy.
2. Bootstrap ở đây là **recursive design**: chuỗi giả sinh lại toàn bộ regressor. Vì vậy ngay cả W3 cũng không giữ được leverage của từng dòng; với VAR có thể xem Gonçalves & Kilian (2004, J. Econometrics), mình trích từ trí nhớ.

**Phân tích tiên nghiệm (ghi trước khi chạy).** Dưới homoskedasticity, E[r_t²] = σ²(1 − h_t) và Σ_t (1 − h_t) = dof, nên:
- **L2:** E[(1/m) Σ r_t²/(1 − h_t)] = σ². Phương sai pool bằng pool đều sqrt(m/dof) **trong kỳ vọng**. Dự đoán: L2 ≈ v5_1 ở mọi cell, factor gần như không đổi.
- **L3:** E[(1/m) Σ r_t²/(1 − h_t)²] = σ² · mean(1/(1 − h_t)) ≥ σ² m/dof. L3 bơm phương sai pool lên, nhiều nhất ở phương trình leverage cao (hub, phương trình có lag block mở). Dự đoán: raw interval rộng hơn; factor re-tune giảm. IS chỉ đổi nếu cách phân bổ độ rộng theo phương trình tốt hơn một factor đều theo cell.
- Cơ chế trong brief ("trả lại trọng lượng cho dòng leverage cao") **không hoạt động** với resample iid, vì lý do ở mục 1 bên trên.

## 2. Probe và kiểm tra trên D-07H development (trước khi chạy D-07)

Script `experiments/ext/r4levboot/probe_identity.py`, seed riêng 77 000 000, 6 topology đầu của D-07H development, lag_max 1/2/4, T 40/80/150, các cell none / missing-0.2 / missing-0.5 / reversed-0.2, 199 draw. Kết quả nằm ở `results/ext_r4levboot_probe/` (`probe.json`, `probe.log`); lượt smoke 1 topology đã ghi probe.json trước, lượt đầy đủ ghi đè khi xong.

**Kiểm tra (lượt smoke 1 topology, T40, 49 draw; lượt đầy đủ ghi trong probe.json khi xong):**
- I1: `r4levboot_U` (pool đều qua plumbing của module, có CRN) cho ra **đúng y hệt** `tolerant_v5_1`, max |diff| của lo, hi và C = 0 (4/4 lần gọi).
- I2: wrapper profile-only của driver không đổi v5_1 (max diff 0).
- I3: `estimator.simulate_from_fit` và `estimator.cumulative` được trả về sau mỗi lần gọi, kể cả khi có exception.
- I4: Σ_t h_tj = số cột của X_j (max sai lệch 5e−15).
- Smoke driver và analyzer: `results/ext_r4levboot_smoke_d07h` (D-07H, 2 topology, T40). 56 row, bootstrap 199/199 ở mọi row.
- Analyzer known-truth: `test_analyze.py` qua 5/5 test (Holm, CI khi hiệu hằng, raw coverage diff, ITT coverage khi có 1 run hỏng, p của nhiễu đối xứng). Log ở `results/ext_r4levboot_probe/test_analyze.log`.

**Profile leverage (probe, lag_max 1 và 2, trung bình theo topology):**

| lag_max | T | cell | mean h | tỉ lệ h > 0.9 | var pool L2 / (RSS/dof) | var pool L3 / (RSS/dof) | raw width L2 / v5_1 | L3 / v5_1 | W3 / v5_1 |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 40 | none / reversed-0.2 | 0.276 | 0 | 1.01 | 1.46 | 1.009 / 1.010 | 1.033 / 1.049 | 0.968 / 1.005 |
| 2 | 40 | missing (0.2 + 0.5) | 0.387 | 0.0002 | 1.00 | 1.76 | 0.998 | 1.069 | 0.915 |
| 2 | 80 | missing | 0.191 | 0 | 1.00 | 1.25 | 0.994 | 1.007 | 0.857 |
| 2 | 150 | missing | 0.105 | 0 | 1.00 | 1.12 | 1.009 | 1.017 | 0.857 |
| 1 | 40 | missing | 0.212 | 0 | 1.00 | 1.29 | 0.994 | 1.004 | 0.844 |
| 4 | 40 | none | 0.514 | 0.005 | 1.00 | 2.45 | 0.962 | 1.113 | 1.055 |
| 4 | 80 | missing | 0.363 | 0 | 1.00 | 1.63 | 0.992 | 1.054 | 0.914 |

(Lag_max 4 lấy từ phần probe đã chạy xong lúc ghi; T40 missing ở lag 4 thì v5_1 thường hỏng. Số đầy đủ ở `probe.log`.)

**Hệ quả cho giả thuyết của brief, ghi trước khi chạy D-07:**
- Tiền đề "mean h ≈ 0.5–0.8 ở T = 40, lag_max 2" **sai**: đo được 0.28–0.39, gần như không có dòng nào có h > 0.9. Mức 0.5–0.6 chỉ xuất hiện ở lag_max 4, T = 40.
- L2 trùng v5_1 về phương sai pool (1.00) và độ rộng raw (±1%), đúng như phân tích tiên nghiệm. Dự đoán L2 không thắng cell nào.
- L3 bơm phương sai pool 1.46–1.76× ở T40, nhưng raw width chỉ tăng 3–7%. Phần lớn độ rộng của v5_1 ở T40 đến từ structural draws và re-selection, không đến từ nhiễu residual.
- W3 hẹp hơn 5–15% ở cell missing.

## 3. Quy tắc ghi trước (pre-registration)

Quy tắc được ghi **trước** run D-07 đầu tiên của hướng này. Thời điểm ghi là mtime của file này, trước `results/ext_r4levboot_g/manifest.json`.

**Run:**
- `python experiments/ext/r4levboot/run.py --config experiments/configs/ext_r4levboot_g.json --workers 3`, gồm v5_1, L2 và L3.
- `python experiments/ext/r4levboot/run.py --config experiments/configs/ext_r4levboot_gw.json --workers 3`, gồm W3, cùng seed dữ liệu.
- Hai run grid lag_max 1 và 4, chỉ để mô tả.
- Áp rule: `python experiments/ext/r4levboot/analyze.py` → `results/ext_r4levboot_g/ruling.md`.

**Grid G:** T ∈ {40, 80, 150} × {none, extra/missing/reversed × 0.2/0.5}, tổng 21 cell. Mỗi cell có 20 topology × 3 replicate = 60 run.

**Tính hợp lệ (điều kiện trước khi đọc kết quả):**
- Row `tolerant_v5_1` của `ext_r4levboot_g` phải trùng 1260/1260 với row đã lưu trong `results/ext_v51_eval`, so cả IS lẫn số cặp được cover.
- Nếu không trùng, kết quả là INVALID, không có verdict.

**Primary:** 8 cell, gồm 6 cell hỏng ở T = 40 cộng missing-0.2 và missing-0.5 ở T = 80. Với 3 arm, primary family có **24 test**.
- dIS = IS(arm) − IS(v5_1), ghép cặp theo unit.
- CI 95% bằng cluster bootstrap theo topology, B = 20000, seed 20261104.
- p hai phía = 2·min(P*(≤0), P*(≥0)), có hiệu chỉnh +1.
- **Holm ở mức 0.05 trên cả 24 test.**

**Cell WIN:**
- Holm bác, với dIS < 0.
- Coverage ITT của arm ≥ 0.90. Run hỏng tính mọi cặp non-null là không cover.
- Số run hỏng của arm ≤ số run hỏng của v5_1 + 1.

**Arm RETAINED (exploratory) khi đủ cả ba:**
- WIN ở ≥ 2/8 cell primary.
- Coverage ITT ≥ 0.90 và điều kiện failure đạt ở cả 8 cell primary.
- No-harm ở **13 cell còn lại** của G (brief ghi "11", nhưng 21 − 8 = 13). Ở mỗi cell:
  - tỉ số IS ≤ 1.05;
  - không có worsening qua Holm 0.05 trên 13 test của arm (Holm bác với dIS > 0);
  - coverage ≥ 0.90 ở mọi cell mà v5_1 có ≥ 0.90;
  - số run hỏng ≤ v5_1 + 1.

**Ứng viên `levboot` RETAINED** nếu có ít nhất một arm RETAINED. Khi có nhiều arm, chọn arm nhiều WIN nhất; nếu hòa, chọn arm có IS trung bình thấp hơn trên 8 cell primary.

**Claim phụ (mô tả, kèm CI):** "leverage giải thích một phần factor" chỉ được nêu khi raw coverage (bỏ PRESCALE và factor) của arm − raw coverage của v5_1 ≥ +0.02 ở ≥ 4/6 cell hỏng T = 40. CI lấy từ cluster bootstrap theo topology, B = 20000.

**Dự đoán của brief (mô tả, không thuộc verdict):**
- (a) effective factor ở T40 missing và T40 reversed giảm ≥ 0.10 so với v5_1 (1.15 và 1.40);
- (b) IS ở T40 thấp hơn hoặc bằng;
- (c) ở T150 không có gì đổi.

**Báo cáo thêm:**
- bảng factor;
- profile h_t (mean, tỉ lệ h > 0.9, tỉ lệ bị floor);
- failure rate (tries − succ)/tries;
- coverage raw của v5_1 và từng arm.

Grid lag_max 1 và lag_max 4 (T 40/80, none / missing-0.2 / reversed-0.2) **chỉ để mô tả**. Ở hai grid này v5_1 được calibrate lại trong chính run trên D-07H, vì `frozen_v4_v51.json` chỉ có factor cho lag_max 2. Các cell calibration giống `ext_region51_lag*`, nên factor T40 của v5_1 phải trùng `results/ext_region51_lag*/calibration.json`, và row v5_1 ở none / missing-0.2 tại T40 phải trùng row đã lưu.

**Những điểm đã tinh chỉnh so với brief, kèm lý do:**
1. Thêm W3, dạng gần nguồn nhất (mục 1).
2. Holm gộp trên 24 test thay cho 3 family 8 test, để kiểm soát FWER khi có nhiều arm.
3. Sửa số cell no-harm từ 11 thành 13.
4. Dùng coverage ITT và trần failure, theo quy ước của P1.
5. Dùng CRN để giảm nhiễu Monte Carlo khi ghép cặp.
6. Tách W3 sang run riêng để mỗi run dưới khoảng 30 phút. Dữ liệu vẫn ghép cặp theo seed.

Không đổi rule sau khi có kết quả. Một thiết kế lại sẽ là phiên bản mới với rule mới.

## 4. Kết quả (append sau khi chạy; rule ở mục 3 không đổi)

**Thời điểm và hash.**
- Rule ghi lúc 2026-11-02T12:28:35Z (`results/ext_r4levboot_prereg/prereg_sha256.txt`).
- Các run D-07 bắt đầu lúc 12:28:40Z.
- Sau khi chạy, hash của `analyze.py`, `ext_r4levboot.py` và `run.py` vẫn trùng file prereg.

| Run | Thời gian | Số row | Ghi chú |
|---|---|---|---|
| `ext_r4levboot_g` (v5_1, L2, L3) | 2265 s (37.8 phút) | 3780 | **Vượt mục tiêu 30 phút**: máy có load average 40–54 vì nhiều agent khác chạy song song |
| `ext_r4levboot_gw` (W3) | 849 s | 1260 | |
| `ext_r4levboot_lag1` | 692 s | 1440 | |
| `ext_r4levboot_lag4` | 1233 s | 1440 | |

**Tính hợp lệ.** Row `tolerant_v5_1` của `ext_r4levboot_g` trùng `results/ext_v51_eval`: "1260/1260 identical (1260 vs 1260 rows) -> **True**". Không có run nào hỏng, ở cả 4 method và 21 cell của G.

**Probe đầy đủ trên D-07H** (`results/ext_r4levboot_probe/probe.json`): I1 max diff 0.0 trên 204 lần gọi; I2 0.0; I3 true; I4 7.1e−15.

### 4.1 Verdict, nguyên văn từ `results/ext_r4levboot_g/ruling.md`

- "**r4levboot_L2: wins 0/8 (Holm over 24), coverage >= 0.90 in all primary: True, harm: True -> NOT RETAINED**"
- "**r4levboot_L3: wins 0/8 (Holm over 24), coverage >= 0.90 in all primary: True, harm: True -> NOT RETAINED**"
- "**r4levboot_W3: wins 0/8 (Holm over 24), coverage >= 0.90 in all primary: True, harm: True -> NOT RETAINED**"
- Claim phụ, cả ba arm: "raw coverage − v5_1 raw coverage >= 0.02 in 0/6 T40 damaged cells -> claim 'leverage explains part of the factor' NOT MADE"
- "**Candidate levboot: NOT RETAINED**"

**Đếm Holm.**
- Primary (24 test): Holm bác 15/24, **cả 15 đều theo chiều arm tệ hơn**. Theo arm: L2 1/8 (T40 missing-0.5, +0.141 [+0.051, +0.227]), L3 7/8, W3 7/8.
- No-harm (13 cell mỗi arm): Holm bác L2 3/13, L3 11/13, W3 4/13, mọi lần bác đều là tệ hơn.

### 4.2 Số chính (D-07 development, exploratory)

**L2, HC2-type.** Đúng như phân tích tiên nghiệm, L2 gần như là v5_1.
- Ở T40, dIS nằm trong khoảng −0.036 đến +0.141.
- Ở T150 missing nó tệ hơn một chút nhưng có ý nghĩa: +0.040 [+0.023, +0.057] và +0.060 [+0.039, +0.081]. Factor T150 missing tăng từ 1.15 lên 1.20 (một bước grid). Tỉ số IS chỉ 1.02–1.03, nhưng Holm vẫn bác.

**L3, HC3-type.**
- Pool variance gấp 1.48–1.92 lần ở T40, nhưng raw coverage chỉ đổi từ −0.004 đến +0.016 so với v5_1.
- Sau re-tune, IS tệ hơn +0.30 đến +0.51 ở mọi cell T40.

**W3, wild Rademacher.**
- Raw interval hẹp hơn; raw coverage thấp hơn v5_1 từ 0.004 đến 0.049 ở mọi cell.
- Factor phải **tăng** (T40 missing 1.35 so với 1.15; reversed 1.55 so với 1.40).
- IS tệ hơn +0.23 đến +0.40 ở T40.

**Effective factor** (runner × 0.5; v5_1 dùng giá trị frozen):

| T | kind | v5_1 | L2 | L3 | W3 |
|---|---|---|---|---|---|
| 40 | none | 1.30 | 1.35 | 1.50 | 1.55 |
| 40 | extra | 1.30 | 1.30 | 1.35 | 1.50 |
| 40 | missing | 1.15 | 1.20 | 1.20 | 1.35 |
| 40 | reversed | 1.40 | 1.40 | 1.40 | 1.55 |
| 80 | missing | 1.30 | 1.30 | 1.30 | 1.50 |
| 150 | missing | 1.15 | 1.20 | 1.25 | 1.35 |

Bảng đầy đủ 12 dòng nằm trong ruling.md.

**Dự đoán của brief:**
- (a) factor T40 missing/reversed giảm ≥ 0.10: **sai ở mọi arm**. Thay đổi là −0.05/0.00 (L2), −0.05/0.00 (L3), −0.20/−0.15 (W3); dấu âm nghĩa là factor tăng.
- (b) IS ở T40 thấp hơn hoặc bằng: **sai** với L3 và W3; L2 hòa ở 5/6 cell và tệ hơn ở 1.
- (c) T150 không đổi: **sai**. Cả ba arm tệ hơn có ý nghĩa ở T150 missing.

**Profile leverage của fit dữ liệu (grid G, lag_max 2):**
- T40: mean h 0.276–0.430, tỉ lệ h > 0.9 là 0.0002–0.0021, tỉ lệ bị floor ≤ 0.0003, mean h lớn nhất theo phương trình 0.56–0.63.
- T80: mean h 0.135–0.210. T150: 0.071–0.115.
- Failure rate của bootstrap (tries − succ)/tries = 0 ở mọi cell và mọi method.

### 4.3 Grid lag_max 1 và 4 (mô tả; `results/ext_r4levboot_lag{1,4}/describe.md`)

**Kiểm tra.** Row v5_1 ở T40 none + missing-0.2 trùng 120/120 với `ext_region51_lag1` và `ext_region51_lag4`. Factor v5_1 ở T40 re-tune trong run trùng factor đã lưu: lag1 3.7 / 3.1 / 3.8; lag4 3.3 / – / 3.2.

**lag_max 1.**
- Mean h chỉ 0.08–0.20.
- Holm bác 9/18 test mô tả, tất cả theo chiều arm tệ hơn: L3 4, W3 5, L2 0.
- Điểm L2 tốt hơn duy nhất ở mức thô là T80 missing-0.2: −0.049 [−0.082, −0.013], p 0.0105, không qua Holm.

**lag_max 4.**
- T40 nằm ngoài vùng dùng được: v5_1 hỏng 27/60 run ở none và reversed-0.2, 60/60 ở missing-0.2. IS ở các run còn lại cũng bùng nổ (161–197).
- Đây là nơi duy nhất leverage thật sự cao: mean h 0.514, tỉ lệ h > 0.9 khoảng 0.03, tỉ lệ bị floor 0.013.
- Ở đây raw coverage của L3 cao hơn v5_1: +0.052 [+0.038, +0.068] và +0.042 [+0.034, +0.051]. Đổi lại IS tệ hơn, có lần rất xa: reversed-0.2 +241 [+0.6, +722]. Residual chia cho 1 − h gần floor (tối đa ×20) sinh ra chuỗi bootstrap gần như explosive.
- Ở T80: L3 và W3 tệ hơn ở 3/3 cell (Holm). Holm bác tổng cộng 10/15.

## 5. Diễn giải

1. **Width factor của v5_1 không phải là một hiệu chỉnh leverage.**
   - Ở T = 40, lag_max 2, leverage vừa phải (mean 0.28–0.43), gần như không có dòng nào h > 0.9. Tiền đề 0.5–0.8 của brief không đúng ở grid của paper.
   - Bơm phương sai residual theo leverage (L3: ×1.5–1.9) gần như không đổi raw coverage (≤ +0.016).
   - Vậy phần thiếu coverage của raw percentile interval (0.84–0.91 ở T40) **không** đến từ việc pool residual bị co. Nhiều khả năng nó đến từ bias của C(H) (bias của OLS ở mẫu nhỏ, structural draws và re-selection), thứ mà nới phương sai không sửa được. Điều này khớp với việc bias-correction (Kilian) là hướng đáng thử hơn. Đây là suy luận, chưa kiểm.
2. **L2 trùng v5_1** cả về lý thuyết lẫn thực nghiệm. Chuyển sang HC2 không giúp đổi factor thành "một bước chuẩn có thể trích dẫn": factor không giảm.
3. **W3**, dạng trung thành với Wu và Davidson–Flachaire nhất, cho interval hẹp hơn và coverage thấp hơn, nên factor phải tăng. Một lý do khả dĩ: trong recursive design, wild bootstrap giữ hình dạng thời gian của residual. Pool iid resample lại trộn đều, nên nó tạo thêm biến thiên của regressor trong các draw. Mình chưa kiểm cơ chế này.
4. **Câu dùng được cho paper**, mục threats hoặc ablation: "Thay residual bootstrap đều bằng residual hiệu chỉnh leverage (HC2/HC3, hoặc wild Rademacher) không làm giảm hệ số hiệu chỉnh độ rộng, và làm interval score tệ hơn ở T = 40 (D-07 development, exploratory). Phần thiếu coverage của percentile interval vì vậy không do leverage."

## 6. Ghi chú, bug và giới hạn

- **Không có Frozen spec**, vì ứng viên NOT RETAINED. Không chạy bank held-out nào.
- **Runtime.** Run G mất 37.8 phút, vượt mục tiêu 30 phút do máy bị chia với các job khác. Grid không bị cắt.
- **Calibration của v5_1 bị tính thừa.** Muốn runner áp factor frozen cho `tolerant_v5_1` thì method phải nằm trong `calibrate_methods`. Runner re-tune nó trên D-07H, rồi `frozen_calibration` ghi đè **trước khi** ghi `calibration.json`. Vì vậy factor re-tune của method frozen không được lưu (không so được với frozen) và tốn khoảng 1/4 thời gian calibration. Đây là nhận xét về `experiments/run_experiment.py`; mình **không sửa**. Ở grid lag thì factor re-tune của v5_1 trùng factor đã lưu của `ext_region51_lag*`.
- **Thay hàm lúc chạy.** Method gán tạm `estimator.simulate_from_fit` và `estimator.cumulative`, rồi trả lại trong `finally` (đã kiểm I3). Cách này an toàn với runner hiện tại vì mỗi process gọi method tuần tự. Nó **không an toàn** nếu sau này method được gọi đa luồng trong cùng một process.
- **CRN** dựa vào quy ước seed của runner (`default_rng([unit, 3, T, cell, tag])`). Ngoài runner thì method dùng generator như được truyền vào.
- **Nguồn.** Full text của ba bài nguồn không được đọc trong vòng này (mục 1). Davison & Hinkley (1997) và Gonçalves & Kilian (2004) được trích từ trí nhớ.
