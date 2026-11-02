# r5hubscreen2: `hubscreen` v2, thành phần B của `tolerant_v5_2` (vòng 5, exploratory)

**Trạng thái.** Exploratory. Evaluation chỉ trên D-07 development với **seed_base mới 70261102**. Calibration (chỉ f_red) trên D-07H development, 3 replicate. Không đụng P4-H1, P4-H2 (cả hai split) hay split confirmatory nào. Không LLM call, không git commit. Module of record vẫn là `tolerant_v5_1`. Hướng này chỉ thêm file mới có tiền tố `r5`; mọi module cũ chỉ được import.

## 1. Vì sao có v2

Vòng 4 (`docs/ext/r4hubscreen.md`, `docs/ext/synthesis_round4.md` mục 2.8) giữ `hubscreen` v1 (RETAINED, exploratory), nhưng verifier tìm ra ba điểm yếu:

1. Khi tập điều kiện C_j (own lag + cha cùng kỳ) tự nó đã vượt cap, v1 giữ own lag 1 và chỉ các cha cùng kỳ có |t| cao nhất. Vì vậy v1 **bỏ ít nhất một cha cùng kỳ khai báo** ở 55% (T19 reversed) và 38% (T19 extra) số lần rút gọn rơi vào nhánh này. Đó là truncation xoá cạnh skeleton, không phải CSIS.
2. "Trùng hệt v5_1 ở mọi chỗ v5_1 chạy được" sai: 98 run v5_1-ok bị đổi vì rút gọn ở mức draw hoặc screening.
3. Trên các run "được cứu" ở T ≤ 25, `plugin_hs_cal` có mean IS thấp hơn ở 6/6 cell.

v2 sửa điểm 1 theo đúng mục 4.1 (B) của synthesis, báo trung thực điểm 2, và đưa điểm 3 thành tiêu chí P2c.

## 2. Thiết kế

### 2.1 Method `tolerant_v5_1_hs2` (`src/paper4/ext_r5hubscreen2.py`)

Giống hệt `ext_r4hubscreen.tolerant_v5_1_hs` (và do đó giống `tolerant_v5_1`), chỉ đổi hàm rút gọn. Với phương trình j fail check đang áp dụng (`fit_equations`: len(terms) + 2 > m; `screen_pairs`: 1 + len(terms) + lag_max + 2 > m):

- C_j = own lag 1..lag_max và **mọi term lag 0** mà danh sách mang; pool = các lag term còn lại; cap = floor(m / 2.5) cột kể cả intercept (như v1).
- Nếu |C_j| ≤ cap − 1: **đúng v1** (giữ C_j và top d = cap − 1 − |C_j| term của pool theo |t| có điều kiện).
- Nếu |C_j| > cap − 1: bỏ own lag 2..lag_max. C'_j = own lag 1 + mọi term lag 0. Giữ C'_j, cộng top d' = cap − 1 − |C'_j| term của pool nếu d' > 0 (ở lag_max 2 thì không bao giờ xảy ra). **Không bao giờ bỏ term lag 0.** Nếu C'_j vẫn vượt cap thì giữ nguyên C'_j, vì cap là ngân sách screening, không phải check khả thi.
- Nếu danh sách đã rút gọn vẫn fail check của `fit_equations`, fit là "underdetermined":
  - ở mức dữ liệu, run fail và được tính vào ITT;
  - trong một bootstrap draw, draw fail và `bootstrap_C` xử lý như với v5_1 (run chỉ fail qua `_too_few`).
- Nếu phương trình cơ sở của bước screening vẫn fail check screening sau rút gọn, `ValueError` được raise như `ext_narrow.screen_pairs`:
  - mức dữ liệu: run fail "underdetermined";
  - mức draw: giữ tập mở của dữ liệu, như v5_1.

**Những điểm mình phải chốt khi diễn giải 4.1 (B), ghi rõ:**
1. "Cha cùng kỳ khai báo" được hiểu rộng thành **mọi term lag 0**. Trong draw, danh sách còn mang cạnh repair và cạnh bị lật; những term này cũng không bị bỏ.
2. Phần "bỏ own lag 2..lag_max trước" được hiểu là: own lag ≥ 2 bị bỏ hẳn, không đưa vào pool.
3. Ý "run fail" của 4.1 (B) áp dụng cho fit ở mức dữ liệu. Ở mức draw, mình giữ cách xử lý draw hỏng của v5_1.
4. Dựng sẵn từ số học: ở lag_max 2, m = 17 (T19), cap = 6, một phương trình chỉ còn fail check fit nếu có ≥ 15 cha cùng kỳ, và chỉ còn fail check screening nếu có ≥ 12. Với n = 14 thì gần như không xảy ra. Vì vậy C1 (completion) của v2 gần như chắc chắn giống v1; phần khác biệt nằm ở IS và coverage.

**Output info:** `hs_reduced`, `hs_eq_data`, `hs_eq_total`, `hs_trunc_eq_data`, `hs_trunc_eq_total`, `hs_contemp_dropped` (bằng 0 theo cấu tạo, đếm để kiểm), `hs_fit_fail`, `hs_screen_fail`, `hs_draws_reduced`.

**Bootstrap stream:** `rng([unit, 3, T, c_idx, ext_seed("tolerant_v5_1")])`, giống v5_1 và v1. Check rút gọn chỉ phụ thuộc số term, nên run không có rút gọn ở đâu (dữ liệu, screening, mọi draw) cho output trùng v5_1 từng bit.

### 2.2 Width factor (không re-tune gì ngoài f_red)

| Factor | Nguồn | Ghi chú |
|---|---|---|
| f_v51(T, kind), T 40/80/150 | `experiments/ext/v51/frozen_v4_v51.json` | frozen của v5_1 |
| f_v51(T, kind), T 19/25/30/35 | `results/ext_r4hubscreen_lag2/calibration.json` khóa `v51` | file frozen không có T < 40. Đây là factor v5_1 vòng 4 tune trên D-07H dev (seed 20261102, 3 replicate); vòng 5 **dùng nguyên**, không tune lại. Không có khóa `19|missing` vì vòng 4 v5_1 không hoàn tất run calibration nào ở đó |
| f_red(T, kind) | **tune ở vòng 5** trên run rút gọn của hs2, D-07H development, 3 replicate | xem dưới |
| `plugin_hs_cal` | `results/ext_r4hubscreen_lag2/calibration.json` khóa `plugin_hs` | "as defined in round 4": method `ext_r4hubscreen.plugin_hs` và factor vòng 4, không tune lại |
| v1 (`tolerant_v5_1_hs`, chỉ mô tả) | f_v51 / khóa `red` của calibration vòng 4 | đúng luật hai factor của vòng 4 |

**Luật áp factor cho hs2:** run không có rút gọn ở đâu và f_v51(T, kind) tồn tại thì dùng f_v51; ngược lại dùng f_red.

**Calibration f_red.**
- Dữ liệu: D-07H development, 20 topology × 3 replicate. Unit = 70261102 + 500 000 + 1000·topology + replicate, theo quy ước calibration của runner; chưa dùng bao giờ.
- Lưới: lag_max 2, T 19/25/30/35, cell extra/missing/reversed-0.2.
- Chỉ fit `tolerant_v5_1_hs2`.
- Factor theo luật của runner: c nhỏ nhất trên lưới 1.0..10 bước 0.1 sao cho coverage gộp của cặp non-null ≥ min(0.95, max − 0.005), tính trên các run có rút gọn.
- Fallback ghi trước, như vòng 4, với MIN_RED = 3:
  1. ≥ 3 run rút gọn ở (T, kind) thì dùng khóa đó;
  2. nếu không, gộp qua kind ở T;
  3. nếu không, gộp mọi T và kind của calibration;
  4. nếu vẫn không có, dùng f_v51.
- Với T 40/80/150 của lưới G, calibration không có T đó nên rơi xuống bước 3. Mình dự báo ở G không có run rút gọn nào (vòng 4: lag 2 T40 có 0 run rút gọn), nên factor này gần như chắc không được dùng. Nếu có run dùng nó thì số run được báo.

### 2.3 Driver, config, dữ liệu

- Driver: `experiments/ext/r5hubscreen2/run_r5.py`, gồm `calibrate` và `main`.
  - Unit, data, skeleton và c_idx theo đúng runner, với layout [extra, missing, reversed] × [0.2, 0.5].
  - Guard: từ chối bank chứa "P4-H1" hoặc "P4-H2", và từ chối split khác development.
  - Factor thật sự đã dùng được ghi vào `results/<name>/factors_used.json`, kèm sha256 của các file nguồn.
- Config:
  - `experiments/configs/ext_r5hubscreen2_cal.json`;
  - `experiments/configs/ext_r5hubscreen2_p2.json`: method v5_1, hs2, v1, `plugin_hs_cal`;
  - `experiments/configs/ext_r5hubscreen2_g.json`: method v5_1, hs2.
- Tham số chung: H 4, n_boot 199, tau_effect 0.1, generator lag_max 2 như mọi lưới D-07.
- **Seed guard:** trước run đầu tiên, `grep` không thấy `70261102` hay `70761102` trong `results/*/manifest.json` hay `results/*/*.json`. Chuỗi này chỉ xuất hiện trong `docs/ext/synthesis_round4.md`, nơi nó được đề xuất. Agent vòng 5 khác (thành phần A) có thể dùng cùng seed_base cho kịch bản của họ; điều đó được phép theo đề bài.

## 3. Rule ghi trước (2026-11-02, trước lượt calibration và evaluation đầu tiên)

Rule chuyển từ mục 4.2 của `synthesis_round4.md`. Chỉ đổi những chỗ thành phần B cần số chính xác, và mọi chỗ đổi đều được đánh dấu **[điều chỉnh]**. Analyzer: `experiments/ext/r5hubscreen2/analyze.py`. Sha256 của file này và của analyzer nằm ở `results/ext_r5hubscreen2_prereg/hashes.txt`, ghi trước run đầu tiên.

**V0 (unit test, trước mọi bank run).** Chạy `experiments/ext/r5hubscreen2/tests.py`, mặc định 8 topology, n_boot 99. Đạt khi cả bốn test đạt:
- **T1:** nhánh CSIS (|C_j| ≤ cap − 1) trùng `ext_r4hubscreen.csis_reduce` trên mọi ca ngẫu nhiên (cần > 500 ca).
- **T2:** ở nhánh truncation, ca tất định giữ đúng own lag 1 và mọi cha cùng kỳ. Stress 4000 ca với lag_max 1..3: 0 vi phạm (term lag 0 bị bỏ hoặc mất own lag 1), 0 own lag ≥ 2 còn lại, và > 100 ca truncation.
- **T3:** phương trình vẫn fail check sau rút gọn làm `fit_reduced2` trả "underdetermined", và method trả status "underdetermined".
- **T4 (probe D-07H dev, replicate 7, ngoài replicate calibration):** hs2 trùng v5_1 từng bit trên mọi run không rút gọn; hs2 trùng v1 từng bit trên mọi run không có phương trình truncation; tổng số term lag 0 bị bỏ = 0.

V0 thất bại thì verdict là **INVALID**.

**V1 (identity) [điều chỉnh].** Trên mọi run của P2 và G có hs_reduced = 0, hs2 phải có cùng status với v5_1 và C/lo/hi raw trùng từng bit. Tổng số term lag 0 bị bỏ trên mọi run phải bằng 0. V1 fail thì verdict là **INVALID**.
- Báo kèm số run v5_1-ok bị hs2 đổi: rút gọn ở mức dữ liệu, chỉ trong draw, và số run mà hs2 fail.
- Phần "ở mọi cell none/extra trùng v5_1" của 4.2 viết cho NG-A. Thành phần B có thể rút gọn ở cell none/extra khi T nhỏ, nên chỉ phần "run không rút gọn" áp dụng.

**P2 (region grid Gaussian).** lag_max 2 × T {19, 25, 30, 35} × {missing, reversed, extra}-0.2: 12 cell, mỗi cell 60 run (20 topology × 3), D-07 development, seed_base 70261102.
- **P2a:** hs2 hoàn tất ≥ 59/60 ở cả 12 cell. Run fail theo luật mới của (B) cũng tính là fail.
- **P2b:** ITT coverage của hs2 ≥ 0.90 ở ≥ 10/12 cell, và không cell nào < 0.85. ITT nghĩa là run fail tính mọi cặp non-null là trượt.
- **P2c [điều chỉnh: thêm Holm và số cluster].** Xét 6 cell T ∈ {19, 25}. Run "được cứu" là run có v5_1 raw status ≠ ok và hs2 ok. Ghép cặp với `plugin_hs_cal` trên các run được cứu mà `plugin_hs_cal` cũng ok.
  - Đại lượng: R = mean IS(hs2) / mean IS(`plugin_hs_cal`).
  - Cluster bootstrap theo topology, B = 20000, seed 20261106 + chỉ số cell.
  - p_i = (1 + #{R* ≥ 1.10}) / (B + 1), cho H0: R ≥ 1.10.
  - Cell đạt khi Holm trên 6 cell bác H0 ở α = 0.05 **và** run ghép cặp đến từ ≥ 8 topology cluster.
  - Cần ≥ 4/6 cell đạt.
  - Báo kèm: cận trên một phía 95% không hiệu chỉnh (đúng câu chữ của 4.2: "< 1.10"), số cell đạt khi không hiệu chỉnh, và median IS của cả hai.
  - Lý do của điều chỉnh: đề bài yêu cầu "Holm with every cell count" và "≥ 8 topology clusters". Holm chỉ làm tiêu chí chặt hơn câu chữ của 4.2.

**No-harm (a), chỉ cho thành phần B.** Lưới G = lag_max 2 × T {40, 80, 150} × (none + {extra, missing, reversed} × {0.2, 0.5}): 21 cell Gaussian, D-07 development, seed_base 70261102. So sánh hs2 với v5_1, ghép cặp trên run cả hai ok:
- tỉ số mean IS ≤ 1.03 ở cả 21 cell;
- không cell nào tệ hơn có ý nghĩa sau Holm trên 21. Kiểm định một phía cho hiệu > 0, cluster bootstrap theo topology, B = 20000, seed 20261108 + chỉ số cell. Một cell chỉ được tính là tệ hơn có ý nghĩa khi có ≥ 8 cluster;
- coverage (trên run hoàn tất) của hs2 ≥ 0.90 ở mọi cell mà v5_1 đạt ≥ 0.90;
- **[điều chỉnh]** cả 21 cell đủ 60 dòng hs2; thiếu dòng thì no-harm (a) FAIL.

No-harm (b) (ng_mix) và (c) (latent/noise) của 4.2 viết cho bản ghép. Đề bài vòng 5 chỉ yêu cầu (a) cho thành phần B đứng riêng.

**Verdict cho thành phần B.**
- **RETAINED (component B, exploratory)** khi V0, V1, P2a, P2b, P2c và no-harm (a) đều đạt.
- **INVALID** khi V0 hoặc V1 fail.
- **REJECTED** trong các trường hợp còn lại, kèm danh sách tiêu chí trượt.

**Báo cáo mô tả, không quyết định:**
- bảng từng cell (ok, coverage, ITT, mean IS, median IS) của hs2, v5_1, v1, `plugin_hs_cal`;
- số run rút gọn, số run có truncation, số fit-fail và screen-fail;
- hs2 so với v5_1 trên run cả hai ok trong P2 (tỉ số, p worse, Holm 12, ≥ 8 cluster);
- hs2 so với v1 trên run cả hai ok;
- coverage trên run được cứu.

**Không đổi rule sau khi có kết quả.** Kết quả được dán nguyên văn vào mục 5.

**Ngân sách thời gian.** Với `--workers 3` trên máy dùng chung, ước lượng: calibration khoảng 5–10 phút; P2 với 4 method khoảng 15–20 phút; G với 2 method ở T150 khoảng 20–30 phút. Không thu nhỏ lưới.

## 4. Những gì đã chạy TRƯỚC khi ghi rule

1. **T1–T3 nhanh** (không có dữ liệu bank): cả ba PASS (T1 2700/2700; T2 1747 ca truncation, 0 vi phạm; T3 PASS).
2. **Smoke pipeline trên D-07H development** (không phải dữ liệu đánh giá):
   - Config `experiments/configs/ext_r5hubscreen2_smoke_{cal,p2,g}.json`: 2 topology × 1 replicate, seed_base 70261102 + 700 000, n_boot 19, G chỉ T40/80.
   - Kết quả ở `results/ext_r5hubscreen2_smoke_*`. Analyzer đã chạy trên smoke để gỡ lỗi định dạng.
   - **Đã thấy:** bảng smoke gồm IS và coverage của 2 topology D-07H ở n_boot 19 (ví dụ `plugin_hs_cal` có đuôi IS 729 ở T19 missing), và V1 47/47 trùng.
   - Sau smoke, mình chỉ sửa một chỗ trong analyzer: no-harm (a) thêm điều kiện đủ 60 dòng mỗi cell, để cell trống không đạt một cách vacuous. Không có thay đổi nào khác về rule hay method.

## 5. Kết quả

**Thứ tự chạy.** Rule và hash được ghi lúc 14:44:52Z (`results/ext_r5hubscreen2_prereg/hashes.txt`). Sau đó chạy liên tiếp, log ở `results/ext_r5hubscreen2_run.log`:
- V0: 14:44:59–14:45:58Z;
- calibration: 98.8 s;
- P2: 316.0 s, 2880 dòng;
- G: 420.7 s, 2520 dòng; xong lúc 14:59:53Z.

Cả lượt chạy dùng `--workers 3`. Sau lượt chạy, `shasum -c` trên cả 12 file đã hash đều OK, nên rule, analyzer, method, driver và config không đổi. Bảng đầy đủ ở `results/ext_r5hubscreen2_ruling/ruling.md` (và `ruling.json`). V0 ở `results/ext_r5hubscreen2_tests/tests.md`. f_red ở `results/ext_r5hubscreen2_cal/calibration.json`. Factor thật sự đã dùng ở `results/ext_r5hubscreen2_p2/factors_used.json`.

### 5.1 Validity (nguyên văn)

- V0 unit tests + D-07H identity probe: PASS
- V1 hs2 == v5_1 (status, raw C/lo/hi bit-identical) on every run with hs_reduced = 0 (P2 + G): 1618/1618; lag-0 terms dropped in total: 0 -> **PASS**
- Honest identity: v5_1-ok runs 1707, changed by hs2 89 (reduction at data level 0, in draws only 89; hs2 failed on 0 of them)

### 5.2 Verdict (nguyên văn, `analyze.py`)

- V0: PASS; V1: PASS
- P2a completion >= 59/60: 12/12 cells -> PASS
- P2b ITT >= 0.90 in >= 10/12 (got 12/12), min >= 0.85 (got 0.943) -> PASS
- P2c rescued runs vs plugin_hs_cal, ratio < 1.10 by Holm(6) with >= 8 clusters: 1/6 (need >= 4; unadjusted upper 95% < 1.10: 1/6) -> FAIL
- No-harm (a) on G: ratio <= 1.03 in 21/21, Holm(21) worse with >= 8 clusters 0/21, coverage kept >= 0.90 where v5_1 >= 0.90 in 21/21, all 21 cells with 60 rows: True -> PASS

**Verdict: REJECTED** (failed: P2c)

### 5.3 Đọc kết quả

Các số dưới đây lấy từ `ruling.md`. Số đánh dấu *post hoc* lấy từ `results/ext_r5hubscreen2_ruling/posthoc.md` (`experiments/ext/r5hubscreen2/posthoc.py`, viết sau ruling, chỉ để mô tả).

1. **Phần sửa của v2 hoạt động đúng thiết kế.** Tổng số term lag 0 bị bỏ là 0 trên mọi run. Không có fit-fail hay screen-fail nào. Completion là 60/60 ở cả 12 cell. ITT coverage là 0.943–0.968.
   - Nhánh truncation vẫn xảy ra nhiều ở T19: 60, 29 và 38 run có ít nhất một phương trình truncation (missing / reversed / extra). Nhưng giờ chỉ own lag 2 bị bỏ.
2. **v2 gần như không khác v1 về IS.** Trên run cả hai cùng ok, tỉ số mean IS v2 / v1 là 0.915–1.095; 7/12 cell nằm trong ±0.5%.
   - Bỏ hay giữ cha cùng kỳ ở nhánh truncation không phải nguồn chính của đuôi IS.
3. **P2c thất bại: 1/6** (cần ≥ 4). Chỉ T25 missing đạt: tỉ số 0.629, cận trên 0.807. Theo cell:
   - **T19 missing:** mean IS 288.00 so với 56.81 (tỉ số 5.07). Median thì ngược lại: 30.40 so với 40.38. *Post hoc:* một run có IS 14361.7; bỏ 3 run lớn nhất thì mean của hs2 còn 37.31; hs2 có IS thấp hơn ở 41/60 run. Đây là đuôi nặng đã thấy ở vòng 4 (fit gần explosive khi m = 17), không phải lỗi của phép rút gọn mới.
   - **T19 reversed:** tỉ số 1.691, chỉ 16 cluster.
   - **T19 extra:** tỉ số 1.100, cận trên 1.156.
   - **T25 reversed:** tỉ số 0.967, nhưng cận trên 1.102 (p 0.053), chỉ 9 cluster.
   - **T25 extra:** tỉ số 1.044, cận trên 1.209.

   Kết luận của verifier vòng 4 vẫn đứng ở T19: trên run được cứu, mốc đơn giản `plugin_hs_cal` không thua hs2 về mean IS. Phép so median nghiêng về hs2 ở T19 missing và T25, nhưng rule đã ghi trước dùng mean.
4. **Identity trung thực.** Có 89/1707 run v5_1-ok bị hs2 đổi, đều do rút gọn **chỉ trong draw** (0 run ở mức dữ liệu). Trên các run này hs2 không fail lần nào. *Post hoc*, theo cell:
   - T25 missing: đổi 26/26 run. f_red bằng f_v51 (1.6), mà IS vẫn tăng từ 12.11 lên 15.77, nên phần tăng đến từ draw được rút gọn thay vì bị bỏ.
   - T30 missing: đổi 49/52 run, IS giảm từ 16.47 xuống 12.87.
   - T30 reversed: đổi 7 run, IS giảm từ 25.55 xuống 16.14.

   Mô tả (không quyết định): ở T25 missing, hs2 tệ hơn v5_1 có ý nghĩa sau Holm 12 trên 26 run ghép cặp (13 cluster): tỉ số 1.302, hiệu +3.663. Như vậy hs2 **không** là "chế độ dự phòng chỉ chạm vào run v5_1 fail". Ở T25 missing, nó làm tệ đi chính các run v5_1 chạy được.
5. **No-harm (a) đạt hoàn toàn và tầm thường.** G có 0 run rút gọn trong 1260 run hs2. hs2 trùng v5_1 từng bit ở cả 21 cell, nên tỉ số đúng bằng 1.0000. Factor fallback của f_red cho T 40/80/150 không được dùng ở run nào.
6. **Calibration f_red (D-07H dev, 3 replicate):**
   - T19: extra 4.2, missing 1.8, reversed 2.5;
   - T25: 3.4 / 1.6 / 3.0;
   - T30: 3.1 / 2.0 / 3.0;
   - T35: 1.8 (chỉ 3 run rút gọn ở T35; mọi kind dùng chung khóa gộp theo T).

   So với f_red vòng 4 (T19 extra 3.7, T35 2.6), factor dịch tới ±0.5–0.8 khi đổi mẫu calibration. Đây vẫn là điểm yếu đã biết: factor nhạy với mẫu calibration.

### 5.4 Verdict cho thành phần B

**REJECTED** (chỉ trượt P2c, 1/6). V0, V1, P2a, P2b và no-harm (a) đều đạt. Theo mục 4.2 của synthesis, thành phần B không vào `tolerant_v5_2`. Nếu thành phần A đạt P1, bản ghép chỉ gồm A.

**Những điều đứng được để dùng sau:**
- v2 chạy được ở mọi run của lưới lag_max 2, T ≤ 35, với ITT ≥ 0.94 và không bỏ cạnh cùng kỳ nào.
- Nhưng v2 không tốt hơn mốc đơn giản `plugin_hs_cal` về mean IS trên run được cứu.
- v2 thay đổi 89 run v5_1-ok qua rút gọn trong draw.

Nếu muốn cứu hướng này, hướng hợp lý là xử lý đuôi gần explosive (ví dụ một ngưỡng dof hay một check stationarity của fit), vì đó là nguồn chính của mean IS lớn. Đây sẽ là một quy tắc mới, phải ghi trước và chạy trên dữ liệu mới, không phải sửa v2 sau khi xem kết quả.

**Không có bug mới trong file hiện có.** Các điểm đã biết từ vòng 4 (`screen_pairs` chặt hơn `fit_equations`; `simulate_from_fit` phóng residual theo sqrt(m / dof) khi dof nhỏ) vẫn đúng và vẫn là nguồn của đuôi IS.
