# Vòng 4, ID "mondrian": split-conformal (Mondrian) cho hệ số width ở bước (6) của `tolerant_v5_1`

**Trạng thái.** Exploratory. Đánh giá chỉ trên D-07 development (seed_base 20261102). Calibration và mọi probe thiết kế chỉ dùng D-07H development. Không chạm P4-H1, P4-H2 (cả hai split) hay bất kỳ confirmatory split nào. Không gọi LLM. Không commit git.

**File của hướng này** (đều là file mới):
- `src/paper4/ext_r4mondrian.py`: module, gồm instrumentation và hai method `tolerant_v5_1_m0`, `tolerant_v5_1_m2`.
- `experiments/ext/r4mondrian/run_pairs.py`: driver ở mức pair. Nó mô phỏng y hệt runner cho v5_1.
- `experiments/ext/r4mondrian/calibrate.py`: tính bảng q và chạy kiểm tra V2.
- `experiments/ext/r4mondrian/analyze.py`: analyzer theo rule đã ghi trước.
- `experiments/ext/r4mondrian/q_table.json` (chính) và `q_table_rep3.json` (sensitivity).
- `experiments/configs/ext_r4mondrian_{cal,eval,a1}.json`.
- `results/ext_r4mondrian_*`.

---

## 1. Nguồn và cách áp dụng

| Nguồn | Lấy gì |
|---|---|
| Lei, G'Sell, Rinaldo, Tibshirani, Wasserman (2018), JASA 113:1094–1111, arXiv:1604.04173 | **Split conformal.** Score được tính trên một tập calibration tách riêng. Ngưỡng là score nhỏ thứ ⌈(N+1)(1−α)⌉. Khi score exchangeable, ta có 1−α ≤ P(cover) ≤ 1−α + 1/(N+1) (cận trên cần thêm điều kiện không có ties). Bài cũng có biến thể **locally weighted**: residual chia cho một thang đo cục bộ. Score ở đây đi theo dạng đó: \|C_true − mid\| / h, trong đó h là half-width của percentile bootstrap |
| Romano, Patterson, Candès (2019), NeurIPS, arXiv:1905.03222 (CQR) | **Conformalize một interval có sẵn** của mô hình gốc thay vì dựng interval mới. Ở đây mô hình gốc là percentile interval của v5_1. Khác CQR ở chỗ: score là độ lệch đối xứng đã chuẩn hoá theo h, tức nhân hệ số quanh midpoint, chứ không phải max(lo − y, y − hi) cộng/trừ một hằng số. Lý do: giữ đúng dạng của bước (6) hiện tại, vốn nhân half-width |
| Vovk, Gammerman, Shafer (2005), *Algorithmic Learning in a Random World* (Mondrian CP) | **Mondrian taxonomy.** Chia đối tượng thành lớp theo một hàm của input, rồi tính quantile riêng trong từng lớp. Validity khi đó giữ **trong từng lớp**. Ở đây lớp được xác định từ structural draws của chính method (R/S), không dùng truth |
| Cabezas, Soares, Ramos, Stern, Izbicki (2024/25), arXiv:2411.19368 (TRUST) | Calibrate confidence set chỉ bằng **dữ liệu mô phỏng từ mô hình**, khi n nhỏ. Bài có local coverage hữu hạn mẫu và conditional coverage tiệm cận. Ở Paper 4, "mô phỏng" là generator trên bank D-07H. Vì thế guarantee chỉ có nghĩa **tương đối với generator** |

**Giới hạn trung thực (ghi trước).**
1. Guarantee là marginal trên generator, tức trên phân phối của (topology, truth, dữ liệu, skeleton hỏng).
2. Các pair trong cùng một dataset phụ thuộc nhau, nên các score không exchangeable từng pair một. Phát biểu hữu hạn mẫu vì vậy chỉ xấp xỉ. Cluster theo topology mới là đơn vị exchangeable.
3. D-07H và D-07 là hai bank sinh bằng cùng script, nhưng mỗi bank chỉ có 20 topology, nên chuyển giao giữa hai bank không hoàn hảo.
4. Không có gì chuyển sang panel thật 14 × 19.

---

## 2. Thiết kế, và các chỗ chỉnh so với đề xuất (đều làm TRƯỚC khi đăng ký)

**Không đổi gì ở bước (1)–(5).** `v51_with_structure` gọi đúng `ext_v51.tolerant_v5_1`, trên đúng stream `rng(ext_seed("tolerant_v5_1"))` của runner. Cấu trúc của từng draw được ghi lại bằng cách bọc `bootstrap_C` trong hai namespace `paper4.ext_v51` và `paper4.methods`, chỉ trong thời gian một lần gọi. Wrapper truyền vào một `refit` tương đương và không gọi thêm số ngẫu nhiên nào. Kiểm tra: trên 28 trường hợp D-07H (2 topology × T 40/150 × 7 cell), lo, hi và C giống `ext_v51.tolerant_v5_1` từng bit. V1 dưới đây kiểm lại trên toàn bộ grid.

**Lớp của pair.** Mỗi draw refit một cấu trúc, gồm các term của mọi phương trình: own lags, lag của các cặp kề, khối lag được mở, và parent cùng kỳ (kể cả cạnh repaired và cạnh bị lật). Từ cấu trúc đó, mỗi term (i, lag) trong phương trình j cho một cạnh i → j có trọng số = lag. Lag luôn hướng về phía trước theo thời gian; lag 0 là cạnh cùng kỳ.

Arrival time d_ij là trọng số đường đi ngắn nhất từ i tới j, chặn ở H + 1. Vì own lag luôn có mặt, C_ji(H) khác 0 về mặt cấu trúc khi và chỉ khi d_ij ≤ H. Từ đó định nghĩa:
- diff_ij = tỷ lệ draw có arrival i → j khác arrival của skeleton khai báo (các term của chính skeleton);
- **R** nếu diff_ij ≥ 0.05, **S** nếu ngược lại;
- f_ij = tỷ lệ draw có d_ij ≤ H (chỉ để mô tả).

**Chỉnh (a): arrival time thay cho reachability.** Trong `estimator.py`, mọi cặp kề đều có lag theo cả hai chiều. Vì vậy reachability tính cả lag chỉ còn là chỉ báo "cùng thành phần liên thông" của skeleton, và gần như không đổi giữa các draw, nên lớp R gần như rỗng. Arrival time giữ đúng ý đồ ("cấu trúc được rút có đổi cách i tới j không?") và mịn hơn: hễ reachability trong H đổi thì arrival time cũng đổi. f_ij vẫn được ghi để mô tả.

**Score và factor.** Trên mỗi case calibration, với mỗi pair non-null (\|C_true\| > 0.1, cùng tập estimand với phần đánh giá), score là s = \|C_true − mid\| / h. Ở đây mid và h là midpoint và half-width **chưa scale** của percentile interval. Quy ước biên: h = 0 mà trượt thì s = +inf; h = 0 mà trúng thì s = 0.

Với mỗi ô (T, stated kind, lớp) có N score, q là score nhỏ thứ ⌈(N+1)·0.95⌉. Lớp có N < 50 được gộp với lớp kia trong cùng ô, và khi đó cả hai dùng q gộp, tức q của M0. Interval cuối là mid ± q·h. Có hai arm:
- **M0:** không chia lớp. Đây là arm sanity.
- **M2:** hai lớp R/S. Đây là arm chính.

Calibration dùng D-07H development, replicate 0, với seed của phase calibration. Đây đúng là các case đã cho ra factor frozen của v5_1. **Sensitivity** (chỉ mô tả) dùng 3 replicate.

**Chỉnh (b): validity.** Đề xuất gốc yêu cầu \|IS_M0/IS_v51 − 1\| ≤ 0.02 và \|Δcov\| ≤ 0.01 ở mọi cell. Probe in-sample trên D-07H (mục 4) cho thấy riêng việc làm tròn grid đã làm coverage lệch tới −0.014: ở T80 none và T80 missing-0.5, q_M0 thấp hơn factor frozen 0.034–0.042, gần một bước grid 0.05. Ngưỡng 0.01 vì thế sẽ báo "lỗi implementation" cho một khác biệt vốn không phải lỗi. Rule mới tách kiểm tra implementation trực tiếp khỏi kiểm tra độ gần:
- **V1:** row v5_1 của driver phải trùng khít row đã lưu của `ext_v51_eval` ở 1260/1260 run: cùng status, IS lệch < 1e-12, cùng số pair được cover và cùng số non-null.
- **V2:** áp rule grid của runner lên score đã ghi của replicate 0 phải tái lập đúng 12/12 factor `tolerant_v5_1|T|kind` của `frozen_v4_v51.json`. **Đã đạt trước khi đăng ký** (mục 4).
- **V3:** max \|q_M0 − 0.5 × factor frozen\| ≤ 0.05 (một bước grid) trên 12 key.
- **V4:** \|IS_M0/IS_v51 − 1\| ≤ 0.02 và \|cov_M0 − cov_v51\| ≤ **0.02** ở mọi cell trong 21 cell.

**Chỉnh (c): WIN phải đến từ việc chia lớp.** Probe D-07H cho thấy M0 − v5_1 đôi khi có ý nghĩa thống kê. Ví dụ T80 none: −0.015 [−0.024, −0.005], p 0.005. Lý do là M0 hẹp hơn grid một chút. Như vậy một "WIN" so với v5_1 có thể chỉ do làm tròn. Rule mới yêu cầu một cell WIN phải có cải thiện M2 − v5_1 có ý nghĩa (Holm 18), **và** cải thiện M2 − M0 có ý nghĩa (Holm 18). Đây là kiểm định intersection–union, chặt hơn đề xuất gốc.

**Chỉnh (d): số cell.** Grid G có 3 T × (none + 6 cell hỏng) = **21 cell**: 18 cell hỏng và 3 cell none. Đề xuất ghi "19 cell", đó là lỗi đếm. Rule dưới đây dùng 21 và 18.

**Chỉnh (e): lost pair.** Trên D-07H có 0 pair với h = 0, tức không có score vô hạn. Ở D-07, v5_1 có 0 lost pair (row đã lưu). Nếu q = inf xuất hiện, method trả status "uncalibrated" và run đó tính là thất bại.

**Hệ quả có thể đoán trước.** Với stated none hoặc extra, v5_1 không rút cấu trúc. Lớp R khi đó rỗng, bị gộp, và **M2 = M0**. Chỉ 12 cell missing/reversed có thể WIN.

---

## 3. Đăng ký trước (rule), ghi trước run D-07

**Dữ liệu.**
- Run đánh giá: `results/ext_r4mondrian_eval`. Config `experiments/configs/ext_r4mondrian_eval.json`: D-07 development, 20 topology × 3 replicate, T ∈ {40, 80, 150}, none + {extra, missing, reversed} × {0.2, 0.5}, lag_max 2, H 4, n_boot 199, seed_base 20261102.
- Bảng q: `experiments/ext/r4mondrian/q_table.json` (D-07H replicate 0).
- So sánh: v5_1 với factor frozen `experiments/ext/v51/frozen_v4_v51.json` (đủ 12 key cần dùng).

**Thống kê.**
- Mỗi run: IS là trung bình interval score trên các pair non-null. Coverage được gộp theo pair.
- Mỗi cell: IS là trung bình qua các run.
- Hiệu ghép cặp: cluster bootstrap theo topology (ratio of sums), B = 20000, seed 20261104, CI percentile 95%.
- p một phía: p_less = (1 + #{b ≥ 0})/(B + 1), p_greater = (1 + #{b ≤ 0})/(B + 1). p hai phía = min(1, 2·min).
- Holm step-down ở mức 0.05.
- Run thất bại dùng chung cho cả ba arm (cùng draw) và bị loại. Cell có > 3/60 run thất bại xem như trượt cổng coverage.

**Validity.** V1, V2, V3 và V4 phải cùng đạt (mục 2). Nếu không, ghi "lỗi implementation", M2 không được đánh giá, verdict là NOT RETAINED (invalid).

**Primary.** Trên 18 cell hỏng, xét hai họ kiểm định:
- Holm 0.05 trên 18 p hai phía của M2 − v5_1;
- Holm 0.05 trên 18 p hai phía của M2 − M0.

Một cell là **WIN** khi cả hai họ đều bác H0, cả hai ước lượng đều < 0, và coverage của M2 ≥ 0.90.

**RETAINED (exploratory)** khi đạt tất cả các điều kiện sau:
1. validity đạt;
2. WIN ≥ 4/18;
3. coverage của M2 ≥ 0.90 ở cả 18 cell hỏng;
4. coverage của M2 ≥ 0.90 ở 3 cell none;
5. **no-harm:** không có cell nào trong 21 cell mà M2 tệ hơn v5_1 có ý nghĩa sau Holm 0.05 trên 21 p hai phía, và IS_M2 ≤ 1.05 × IS_v51 ở cả 21 cell.

Nếu không đạt thì NOT RETAINED.

**Secondary (không quyết định verdict).** Xét các pair bị ảnh hưởng bởi cạnh đảo, ở 6 cell reversed. Định nghĩa affected và oracle_cal theo revlag3: non-null, dC = \|C_true − C_true khi các cạnh thật bị đảo được đặt bằng 0\| ≥ 0.05; oracle_cal là interval của oracle nới theo hệ số 1.4 / 1.3 / 1.2 cho T 40 / 80 / 150. Oracle được fit một lần mỗi T bằng rng(2) ở c_idx 0. Báo coverage của v5_1, M0, M2 và oracle_cal; hiệu M2 − v5_1 với p một phía (M2 cao hơn), Holm trên 6; khoảng cách tới oracle_cal.

**Mô tả (không quyết định verdict).**
- Bảng q, kích thước lớp, coverage theo lớp.
- Sensitivity: bảng q 3 replicate (`q_table_rep3.json`), áp lên cùng run D-07.
- No-harm theo kịch bản: grid của `ext_v51_a1` (T 80/150; none, missing-0.2, reversed-0.2), với latent1 và noise0.1 (`results/ext_r4mondrian_a1`), kèm V1 so với row đã lưu của `ext_v51_a1`.

**Không đổi rule sau khi có kết quả.** Nếu thiết kế lại, đó là version mới với rule mới.

**Thời gian dự kiến** với `--workers 3`: run D-07H 194 s (đã chạy). Run D-07 khoảng 4–6 phút, run kịch bản khoảng 3–5 phút. Không cần thu nhỏ grid.

---

## 4. Những gì đã thấy trên D-07H trước khi đăng ký (công bố)

Run `results/ext_r4mondrian_cal`: D-07H development, seed của phase calibration, 3 replicate. Kết quả: 1260 run, 36834 pair non-null, 0 run thất bại, 0 pair với h = 0. Thời gian 193.9 s.

**V2 đạt 12/12.** Rule grid của runner, áp lên score replicate 0 đã ghi, cho lại đúng factor frozen ở cả 12 key (`results/ext_r4mondrian_cal/calibration.md`).

**Bảng q (replicate 0, factor hiệu dụng trên h).**

| T | kind | q M0 | 0.5 × frozen | N R / N S | q R | q S |
|---|---|---|---|---|---|---|
| 40 | none | 1.298 | 1.30 | 0 / 585 (gộp) | – | – |
| 40 | extra | 1.294 | 1.30 | 0 / 1170 (gộp) | – | – |
| 40 | missing | 1.140 | 1.15 | 419 / 751 | 1.323 | 1.105 |
| 40 | reversed | 1.401 | 1.40 | 327 / 843 | 1.177 | 1.456 |
| 80 | none | 1.266 | 1.30 | 0 / 585 (gộp) | – | – |
| 80 | extra | 1.210 | 1.20 | 0 / 1170 (gộp) | – | – |
| 80 | missing | 1.259 | 1.30 | 421 / 749 | 1.342 | 1.128 |
| 80 | reversed | 1.342 | 1.35 | 363 / 807 | 1.476 | 1.234 |
| 150 | none | 1.165 | 1.20 | 0 / 585 (gộp) | – | – |
| 150 | extra | 1.181 | 1.20 | 0 / 1170 (gộp) | – | – |
| 150 | missing | 1.150 | 1.15 | 421 / 749 | 1.243 | 1.072 |
| 150 | reversed | 1.198 | 1.20 | 372 / 798 | 1.304 | 1.191 |

Nhận xét:
- Đúng như giả thuyết, M0 tái lập factor hiện tại lệch trong khoảng một bước grid (max 0.0415).
- Ở T80/150, lớp R cần factor lớn hơn lớp S.
- Ở T40 reversed thì **ngược lại**: q_R = 1.18 < q_S = 1.46.

**Sensitivity 3 replicate (đã thấy).** Ở T40, q tăng mạnh: none 1.30 → 1.64, extra 1.29 → 1.54, reversed 1.40 → 1.64. Như vậy factor ở T40 tính từ một replicate D-07H không ổn định. Ở T80/150 độ lệch nằm trong khoảng −0.13 đến +0.02.

**Probe in-sample (smoke test analyzer trên chính D-07H, gộp 3 replicate; `results/ext_r4mondrian_cal/smoke_insample.md`).** Probe này đã được xem trước khi viết rule. Nó không phải bằng chứng, vì q được ước lượng trên replicate 0 của chính các case này.
- M0 so với v5_1: \|Δcov\| tới 0.014, tỷ lệ IS trong khoảng 0.991–1.002. Đây là lý do của chỉnh (b).
- M2 − v5_1 trên IS nằm trong khoảng −0.11 đến +0.10. Có cell M2 tệ hơn (T40 missing-0.5 +0.10, T150 missing-0.5 +0.03), tức ngay cả in-sample lợi ích cũng nhỏ và không đều.
- Coverage của lớp R dưới v5_1 thấp hơn lớp S ở T80/150 (ví dụ T150 reversed-0.2: 0.913 so với 0.965). M2 cân bằng lại hai lớp.

Rule ở mục 3 không dùng thêm thông tin nào từ D-07.

---

## 5. Kết quả (append sau run; rule ở mục 3 giữ nguyên)

**Thứ tự thời gian.**
- Rule và mọi code/config được hash lúc 2026-11-02T12:21:17Z, ghi trong `results/ext_r4mondrian_prereg_sha256.txt`.
- Run D-07 bắt đầu 12:21:17Z và mất 472.5 s, cho 1260 run và 38934 pair, 0 run thất bại.
- Run kịch bản bắt đầu 12:29:16Z và mất 412.9 s, cho 720 run.
- Doc này lúc append vẫn có cùng sha256 với lúc hash (6c3a43f4…).

Analyzer: `experiments/ext/r4mondrian/analyze.py`. Số nguyên văn ở `results/ext_r4mondrian_eval/ruling.{md,json}`.

### 5.1 Validity, nguyên văn
- "V1 (driver v5_1 rows = stored `ext_v51_eval` rows): 1260/1260 identical (1260 vs 1260 rows, failed runs 0) -> **PASS**"
- "V3 (max |q_M0 − 0.5 × frozen factor| over 12 keys ≤ 0.05): 0.0415 -> **PASS**"
- "V4 (M0 vs v5_1: |IS ratio − 1| ≤ 0.02 and |Δcov| ≤ 0.02, every cell): 21/21 -> **PASS**"
- V2 12/12 PASS (mục 4).

Như vậy ghép cặp với run đã lưu là thật: row v5_1 trùng khít, nên M0 và M2 dùng đúng draw của v5_1.

### 5.2 Primary, nguyên văn

"WIN 0/18 (Holm 18 vs v5_1, better: 1/18; Holm 18 vs M0, better: 0/18); coverage ≥ 0.90 in all 18 damaged cells: True; in the 3 none cells: True; IS ratio M2/v5_1 ≤ 1.05 in all 21 cells: True; Holm-21 significant worsening vs v5_1: 0/21; validity: True."

**Verdict: NOT RETAINED.**

Đọc kết quả:
- **Cell duy nhất mà M2 tốt hơn v5_1 sau Holm 18 là T150 extra-0.5** (−0.006 [−0.010, −0.002], p 0.0026). Ở cell này M2 = M0, nên lợi thế chỉ đến từ việc làm tròn grid. Đây đúng là trường hợp mà chỉnh (c) được đặt ra để loại.
- **Không cell nào có M2 − M0 có ý nghĩa sau Holm 18.** Hiệu M2 − M0 trên IS nằm trong khoảng −0.064 (T40 missing-0.2) đến +0.104 (T40 reversed-0.5).
- **Ở T40 reversed-0.5, M2 tệ hơn v5_1:** +0.104 [+0.035, +0.175], p 0.0025. Cell này bị Holm 18 bác trong họ "vs v5_1", nhưng theo hướng tệ hơn. Ở Holm 21 (no-harm) nó vừa không bị bác, vì 0.0025 > 0.05/21 = 0.00238. Coverage của M2 ở đây là 0.910, so với 0.920 của v5_1. Tóm lại, no-harm chỉ đạt sát biên ở cell này.
- **Cơ chế.** Chia lớp chủ yếu dịch coverage từ lớp S sang lớp R, còn lợi ròng trên IS gần 0:
  - T150 reversed-0.5: lớp R tăng 0.901 → 0.919, lớp S gần như giữ nguyên (0.968 → 0.967).
  - T80 missing-0.2: lớp R tăng 0.931 → 0.937, lớp S giảm 0.953 → 0.927.
- **Ở T40 reversed, thứ tự lớp ước lượng trên D-07H (q_R < q_S) không chuyển sang D-07.** Trên D-07 lớp R vốn đã under-cover (0.916 / 0.895), và M2 còn hạ nó xuống 0.883 / 0.836. Nguyên nhân là factor theo lớp ước lượng từ 20 topology D-07H, quá ít để ổn định.

### 5.3 Secondary: cặp chịu ảnh hưởng của cạnh đảo (nguyên văn, Holm 6)

| T | cell | n aff | cov v5_1 | cov M2 | cov oracle_cal | M2 − v5_1 [CI] | Holm 6 | M2 − oracle_cal [CI] |
|---|---|---|---|---|---|---|---|---|
| 40 | reversed-0.2 | 232 | 0.841 | 0.823 | 0.961 | −0.017 [−0.039, +0.006] | - | −0.138 [−0.196, −0.086] |
| 40 | reversed-0.5 | 564 | 0.860 | 0.832 | 0.931 | −0.028 [−0.050, −0.011] | - | −0.099 [−0.140, −0.062] |
| 80 | reversed-0.2 | 232 | 0.849 | 0.841 | 0.944 | −0.009 [−0.033, +0.014] | - | −0.103 [−0.145, −0.060] |
| 80 | reversed-0.5 | 564 | 0.858 | 0.865 | 0.945 | +0.007 [−0.004, +0.016] | - | −0.080 [−0.105, −0.057] |
| 150 | reversed-0.2 | 232 | 0.884 | 0.914 | 0.978 | +0.030 [+0.011, +0.054] | rej | −0.065 [−0.118, −0.027] |
| 150 | reversed-0.5 | 564 | 0.883 | 0.897 | 0.970 | +0.014 [+0.007, +0.021] | rej | −0.073 [−0.099, −0.047] |

"Secondary count: M2 raises affected-pair coverage after Holm(6) in 2/6 cells."
- Ở T150, M2 thu hẹp khoảng cách tới oracle_cal 16–32% (−0.095 → −0.065; −0.087 → −0.073).
- Ở T40, M2 làm khoảng cách rộng thêm.
- Ở mọi cell, khoảng cách tới oracle_cal vẫn còn từ −0.065 đến −0.138.
- Lớp R chỉ chứa 50–77% cặp affected, nên bộ phân lớp R/S chỉ bắt được một phần cặp chịu ảnh hưởng của cạnh đảo.

### 5.4 Mô tả: M0, tức bản conformal của factor hiện tại

`results/ext_r4mondrian_eval/m0_guarantee.md` (post hoc, chỉ mô tả).

- **M0 thay grid factor gần như không tốn gì.** Trên 21 cell, max \|IS ratio − 1\| = 0.0047 và max \|cov_M0 − cov_v51\| = 0.0070. Như vậy giả thuyết "factor hiện tại, sai khác tới mức làm tròn, chính là quantile 0.95 thực nghiệm của s gộp" đúng.
- **Nhưng phát biểu "finite-sample guarantee" ở mức pair không đứng vững trên D-07.** Lấy coverage của M0 với bảng replicate 0 và tính CI cluster theo topology: CI loại 0.95 ở **11/21** cell. Cụ thể T40 0.912–0.937 (6/7 cell), và T150 missing over-cover 0.966/0.968. Với bảng 3 replicate còn **5/21** cell.
- Lý do: các pair trong cùng dataset và cùng topology phụ thuộc nhau. Cỡ mẫu hiệu dụng của calibration vì thế gần với 20 topology, không phải N ≈ 1170 pair. Cận 1/(N+1) của Lei et al. không áp dụng được. Vì vậy, dùng M0 để trả lời phê bình "ad hoc" thì chỉ có thể nói: "factor là quantile conformal của score chuẩn hoá trên bank calibration". **Không** được viết "đảm bảo coverage hữu hạn mẫu ≥ 0.95".
- Muốn có một guarantee thật, phải dùng conformal ở mức cluster: mỗi topology cho một score, ví dụ quantile trong cluster. Khi đó N = 20 và q sẽ thô (rank ⌈21 · 0.95⌉ = 20, tức gần như lấy max). Hướng này chưa thử.

### 5.5 Mô tả: sensitivity với bảng q 3 replicate

`results/ext_r4mondrian_eval/sens_rep3.md`. Phần validity trong file đó báo FAIL là đương nhiên, vì bảng khác factor frozen; không áp dụng ở đây.
- Ở T40, bảng 3 replicate nâng coverage của M0 lên 0.942–0.958 (từ 0.912–0.937). Cái giá là IS tăng +0.01 đến +0.19 so với v5_1; các hiệu có ý nghĩa ở mức thô là T40 missing-0.5 +0.102, reversed-0.2 +0.189 và reversed-0.5 +0.169.
- Ở T150 missing, M0 3-rep tốt hơn v5_1: −0.022 [−0.036, −0.006] và −0.036 [−0.052, −0.016].
- M2 − M0 với bảng 3 replicate: chỉ có ý nghĩa thô ở T40 missing-0.2 (−0.072, p 0.010) và T40 reversed (+0.013 / +0.015, tệ hơn). Kết luận về việc chia lớp không đổi.
- Hệ quả cho module of record, chỉ là quan sát: factor T40 của v5_1 được tune trên **1** replicate D-07H và rất nhạy với mẫu calibration (q_M0 T40 none 1.30 → 1.64). Đây là một nguồn của coverage 0.91–0.94 ở T40 trên D-07.

### 5.6 Mô tả: no-harm theo kịch bản (latent1, noise0.1; T 80/150)

`results/ext_r4mondrian_a1/noharm.md`. V1 so với row đã lưu của `ext_v51_a1`: 720/720 identical.
- **latent1:** M2 − v5_1 trong khoảng −0.040 đến +0.034, coverage của M2 0.919–0.947. Có một hiệu thô tệ hơn: T150 missing-0.2 +0.027 [+0.002, +0.052].
- **noise0.1:** ở T80 missing-0.2, M2 tệ hơn rõ: +0.118 [+0.034, +0.202], p 0.0057, coverage 0.883 so với 0.916 của v5_1. Ngược lại, ở T150 reversed-0.2 M2 tốt hơn: −0.066 [−0.105, −0.030], coverage 0.902 so với 0.888.
- Như vậy dưới nhiễu đo, lớp S (factor nhỏ hơn) bị hở. Đây thêm một lý do để không giữ M2.

### 5.7 Kết luận cho Paper 4
1. **M2 (Mondrian R/S): NOT RETAINED.** Không có frozen spec.
2. **M0 có thể dùng làm cách *mô tả* bước (6)**: "hệ số width là quantile split-conformal ⌈(N+1)·0.95⌉ của score \|C_true − mid\|/h trên bank calibration". Mô tả này tương đương factor hiện tại, với chênh IS ≤ 0.5% và chênh coverage ≤ 0.007. Paper phải nói rõ:
   - đơn vị exchangeable là topology, không phải pair;
   - trên D-07, coverage lệch 0.95 có ý nghĩa ở 11/21 cell;
   - vì vậy không có guarantee hữu hạn mẫu ở mức pair.
3. **Nên làm tiếp (đề xuất, chưa làm):**
   - (i) calibration T40 trên nhiều replicate hơn. Bằng chứng: ở T40 coverage của M0 3-rep là 0.942–0.958 so với 0.912–0.937, nhưng IS tăng;
   - (ii) conformal ở mức cluster cho một guarantee trung thực;
   - (iii) bộ phân lớp R/S chưa bắt được cặp chịu ảnh hưởng của cạnh đảo (chỉ 50–77%). Một bộ phân lớp tốt hơn cần thông tin về hướng của cạnh cùng kỳ, mà dữ liệu Gaussian không cung cấp.

### 5.8 Bug / lưu ý trong file có sẵn
- Không tìm thấy bug mới trong `ext_v51.py`, `ext_narrow.py`, `methods.py`, `estimator.py`. Instrumentation tái lập v5_1 đúng từng bit, và V1 đạt 1260/1260 cùng 720/720.
- Lưu ý: `frozen_v4_v51.json` ghi factor T40 của v5_1 được tune trên 1 replicate D-07H. Mục 5.5 cho thấy factor này nhạy với mẫu. Đây không phải bug, nhưng là một threat nên nhắc trong paper.
