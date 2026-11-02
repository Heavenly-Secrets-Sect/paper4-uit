# TLP vòng 3: sửa frozen spec P5 cho P4-H2 (ID `tlp3`, mục R3-5)

**Trạng thái.** Tiếp nối `tlp2` ([tlp2.md](tlp2.md)). Đây là việc **spec**, không có rule giữ/loại phương pháp nào trên D-07. Không đụng P4-H2, P4-H1 hay confirmatory split; không chạy config P4-H2 nào; không gọi LLM. Chỉ có ba việc có chạy: preflight (chỉ import code), một smoke test trên **D-07H development** (plumbing và đo thời gian), và chấm lại các `runs.jsonl` **đã có** của D-07 development bằng analyzer mới (kiểm tra analyzer). Không có run mới nào trên D-07.

Ghi phần 0–5 lúc 2026-11-02T06:05Z, **trước** khi chạy smoke test và trước khi chấm lại bằng analyzer mới. Kết quả được append ở mục 6 trở đi.

**File mới (không sửa file cũ nào):**
- [experiments/configs/ext_tlp3_p4h2.json](../../experiments/configs/ext_tlp3_p4h2.json): config P4-H2 của P5. Thay `ext_tlp2_p4h2.json`; file cũ **không được chạy**.
- [experiments/ext/tlp3/analyze_p4h2.py](../../experiments/ext/tlp3/analyze_p4h2.py): analyzer mới. Thay `experiments/ext/tlp2/score.py` cho P4-H2; `score.py` **không được dùng** cho P4-H2.
- [experiments/ext/tlp3/preflight.py](../../experiments/ext/tlp3/preflight.py): kiểm tra registry method (E4) và ghi hash, chạy ngay trước run.
- [experiments/ext/tlp3/p4h2_spec_files.json](../../experiments/ext/tlp3/p4h2_spec_files.json): spec manifest (mọi file mà spec phụ thuộc, lệnh, thời gian, chính sách chạy lại).
- [experiments/ext/tlp3/check_v4_realisation.py](../../experiments/ext/tlp3/check_v4_realisation.py) → `results/ext_tlp3_checks/v4_realisation.json`: kiểm tra trên các run D-07 đã có (mục 1, điểm 5).
- [experiments/configs/ext_tlp3_smoke.json](../../experiments/configs/ext_tlp3_smoke.json): smoke test trên D-07H development.

## 0. Phối hợp với `baselines3` (R3-1)

Lúc viết (06:03Z), `docs/ext/baselines3.md` **chưa tồn tại**. `src/paper4/ext_baselines3.py` đã có nhưng chỉ đăng ký `pselect_union_v3(_cal)`, `pselect_cal`, `fullvar_cal`; không có method TLP nào. Synthesis vòng 2 (R3-1) dự kiến envelope của P7 gồm `targeted_lp_cal` và `tlp2_db_p3`, chỉ ở **T80/150 × missing**. Vì vậy, theo đúng chỉ dẫn của task, spec P5 đã sửa được viết đầy đủ ở đây. Quy tắc rút P5 nằm ở mục 5.

## 1. Năm điểm verifier nêu (synthesis vòng 2, bảng 3.2, dòng P5) và cách sửa

| # | Điểm | Cách sửa |
|---|---|---|
| (1) | Doc (tlp2.md mục 8) nói A' "đếm cả số qua Holm", còn `score.py` chỉ đếm số thắng thô (không bắt buộc Holm) | **Quyết định ngay bây giờ: A' BẮT BUỘC Holm** (mục 2). Analyzer mới cài đúng định nghĩa này, và doc này dùng cùng câu chữ |
| (2) | Chưa ghim hash `ext_tlp.py`, `ext_tlp2.py`, `score.py`, `run_experiment.py` | Spec manifest liệt kê mọi file (module, analyzer, config, preflight, file frozen, runner, `src/paper4/{__init__,methods,estimator,metrics,generator,skeleton,effects,topology}.py`, doc này). Vì runner import **mọi** `ext_*.py` (E4), manifest liệt kê thêm chúng như "registry dependents". `preflight.py` fail nếu tên method trùng hoặc resolve sai module, và ghi sha256 của mọi module paper4 được nạp. Lead hash toàn bộ ngay trước run |
| (3) | `score.py` sẽ in claim B "incomplete" và pairing 0/0 trên P4-H2 | Analyzer mới **không có** claim B, **không** kiểm tra pairing với vòng 1, **không** có khối db90. Nó không đọc file nào của D-07. Ngoài ra (lỗ hổng tôi tìm thêm): `score.py` dựng truth cho db90 từ config D-07 `ext_tlp2_t80a.json`, và bỏ qua âm thầm các run fail. Analyzer mới có rule rõ ràng cho run fail (mục 3) |
| (4) | Budget khoảng 80 phút | Đo lại bằng smoke test trên D-07H và đối chiếu với tổng thời gian các run D-07 của tlp2 (mục 4). P5 cần người dùng duyệt ngoại lệ budget; nếu không được duyệt thì rút (mục 5) |
| (5) | Phải ghi rằng realisation duy nhất theo `c_idx` là bản confirmatory | Ghi ở mục 3.4. Thêm một bằng chứng: realisation v4 của config này **trùng** realisation v4 của P1 (`ext_v51_p4h2`) ở T80/150, vì hai config có cùng danh sách kinds/rates (cùng `c_idx`, cùng `k_idx`) |

**Bằng chứng cho (5), đã chạy trên D-07 development** (`results/ext_tlp3_checks/v4_realisation.json`; chỉ đọc runs có sẵn): dòng `tolerant_v4` của `ext_v51_eval` trùng bit-for-bit (IS và số cặp phủ) với `ext_baselines2_eval`, `ext_v4c_eval`, `ext_tlp_eval`, `a2_baselines` ở **420/420** run cho mỗi T ∈ {40, 80, 150}. Cả năm config có kinds [extra, missing, reversed] × rates [0.2, 0.5]. Bản v4c chạy với `--workers 6` và numpy khác mà vẫn trùng. Danh sách T không ảnh hưởng đến seed: seed của data là `[unit, 2, T]` và của method là `[unit, 3, T, c_idx, tag]`. tlp2.md mục 7.1 đã kiểm chứng điều này: các run chỉ có T = 80 vẫn trùng `ext_tlp_eval` ở mọi cell đứng đầu thứ tự.

**Driver.** P5 chạy bằng runner gốc, không cần driver mới; lỗi `c_idx` của `run_cells.py` vì vậy không còn liên quan. Không sửa `run_cells.py` (các run D-07 đã dùng nó).

## 2. Quyết định về A' (ghi trước P4-H2, không đổi sau đó)

- Một **lần thắng của v4** ở một cell được tính cho A/A' khi và chỉ khi nó thắng theo **gate view** (cov(v4) ≥ 0.90 và cận trên CI 95% của v4 − X < 0) **và** Holm-adjusted p < 0.05. Holm tính trong 12 cell hỏng (T ∈ {80, 150}), riêng cho từng phiên bản X.
- Một **lần thua** (X thắng) được đếm **thô, không Holm**, theo cả gate view và pure-IS view. Như vậy điều kiện "không thua" chặt hơn.
- Lý do: P5 là câu confirmatory về 12 cell. Nếu đếm số thắng mà không hiệu chỉnh, 12 test ở mức 0.05 sẽ cho số thắng bị thổi lên. Còn số thua được đếm thô vì một lần thua dù chỉ ở mức danh nghĩa cũng phải chặn claim.
- Trên D-07, quyết định này không đổi verdict nào của tlp2 (bản chính: mọi lần thắng đều qua Holm; sensitivity v4r1: `targeted_lp` 11/12, cả 11 qua Holm). Điều này được kiểm lại bằng analyzer mới ở mục 6.
- Câu A' trong synthesis vòng 2, mục 1.7 ("ở 11–12/12 cell ... Mọi lần thắng đều qua Holm") khớp với định nghĩa này.

## 3. Frozen spec P5 cho P4-H2 (rule confirmatory, nguyên văn)

### 3.1 Cái gì chạy

- **Config:** `experiments/configs/ext_tlp3_p4h2.json`. Method: `tolerant_v4` (frozen, `experiments/calibration/tolerant_v4_frozen.json`), `targeted_lp` (`src/paper4/ext_tlp.py`), `tlp2_db`, `tlp2_db_p3` (`src/paper4/ext_tlp2.py`). Bank P4-H2 / confirmatory, T = [80, 150], kinds [extra, missing, reversed] × rates [0.2, 0.5] (cộng cell none, do runner luôn chạy), 3 replicate, H = 4, n_boot = 199, seed_base 20261102. Khối calibration là D-07H development: runner bắt buộc calibrate khi có `tolerant_v4`, sau đó file frozen ghi đè `mod|T|kind`. Ngoài các key `name` và `purpose`, config này giống từng key với `ext_tlp2_p4h2.json`. Các key về grid và seed giống `ext_v51_p4h2.json`.
- **Lệnh (đúng thứ tự):**
  1. `python3 experiments/ext/tlp3/preflight.py --out results/ext_tlp3_preflight/preflight.json`. Phải in `"ok": true`, nếu không thì không chạy.
  2. `python3 experiments/run_experiment.py --config experiments/configs/ext_tlp3_p4h2.json --workers 3`
  3. `python3 experiments/ext/tlp3/analyze_p4h2.py --run ext_tlp3_p4h2 --out results/ext_tlp3_p4h2_verdict`
- Chạy **một lần**. Nếu bị ngắt trước khi có `results/ext_tlp3_p4h2/runs.jsonl`, chạy lại một lần với config không đổi và công bố. Không bao giờ chạy qua driver lọc cell. Nên chạy sau P1 (`ext_v51_p4h2`) để kiểm tra mô tả ở 3.4 có dữ liệu so sánh; verdict không phụ thuộc kiểm tra đó.

### 3.2 Thống kê

Với mỗi X ∈ {`targeted_lp`, `tlp2_db`, `tlp2_db_p3`} và mỗi cell c trong 12 cell hỏng (T ∈ {80, 150} × kind ∈ {extra, missing, reversed} × rate ∈ {0.2, 0.5}):
- d = trung bình qua các run ghép cặp (cả v4 và X đều status ok) của IS(v4) − IS(X), với IS = interval score trung bình trên cặp non-null.
- CI 95% percentile và p hai phía, từ bootstrap resample topology (10000 lần), seed `[0, T, chỉ số cell, chỉ số X]` (chỉ số cell: 0 = none, 1..6 theo thứ tự extra 0.2, extra 0.5, missing 0.2, missing 0.5, reversed 0.2, reversed 0.5; chỉ số X theo thứ tự trên). p = 2·min(P*(d* ≤ 0), P*(d* ≥ 0)), sàn 1/10000.
- Coverage cov(M) của method M ở cell c = tổng số cặp non-null được phủ (run ok) chia cho tổng số cặp non-null trên **mọi** run dự kiến (topology trong manifest × 3 replicate). Run fail của M tính là không phủ cặp nào. Cặp lost (estimate đúng 0) tính là không phủ.
- **Đủ dữ liệu:** cell c đủ cho X nếu số run ghép cặp ok ≥ ⌈0.90 × số run dự kiến⌉ (54 nếu P4-H2 có 20 topology).
- **Gate view:** v4 thắng nếu cov(v4) ≥ 0.90 và cận trên CI < 0; X thắng nếu cov(X) ≥ 0.90 và cận dưới CI > 0; còn lại hòa. **Pure-IS view:** như gate view, bỏ hai điều kiện coverage.
- **Holm:** áp dụng cho 12 p-value của mỗi X (step-down, đơn điệu). Một lần thắng "qua Holm" khi hướng đúng theo view đó và p_Holm < 0.05.

### 3.3 Verdict (intersection-union qua ba phiên bản; không hiệu chỉnh thêm giữa các X)

- **INVALID** nếu `results/ext_tlp3_p4h2/manifest.json` mang config khác `experiments/configs/ext_tlp3_p4h2.json`.
- **NOT CONFIRMED (incomplete)** nếu có bất kỳ cặp (X, cell) nào không đủ dữ liệu.
- **CONFIRMED-A (xác nhận mạnh):** với **mỗi** X: v4 thắng theo gate view **và qua Holm** ở 12/12 cell, và X thắng 0 cell theo gate view và 0 cell theo pure-IS view (đếm thô).
- **CONFIRMED-A' (xác nhận):** không đạt A, nhưng với **mỗi** X: số cell v4 thắng theo gate view **và qua Holm** ≥ 10, và X thắng 0 cell theo cả hai view (đếm thô).
- **NOT CONFIRMED:** các trường hợp còn lại. Khi đó paper chỉ báo số đếm.
- Báo kèm, không vào verdict: mọi số đếm theo cả hai view, thô và qua Holm; verdict của cell none; số run fail theo method; thời gian chạy.
- P5 là **secondary** (synthesis 3.3), nên không có overlay Bonferroni giữa các spec. Mọi kết quả đều được báo, kể cả NOT CONFIRMED.

**Câu paper tương ứng:**
- **A:** "Trên bank niêm phong P4-H2, ở T ≥ 80 `tolerant_v4` có interval score thấp hơn cả ba phiên bản Targeted Local Projections ở 12/12 cell hỏng (mọi lần thắng qua Holm trong 12 cell); TLP không tốt hơn ở cell nào."
- **A':** như trên, thay "12/12" bằng "ít nhất k/12" (k = min qua ba phiên bản của số thắng qua Holm).

### 3.4 Realisation duy nhất (bug E1, không sửa trước P4-H2)

- Runner seed bootstrap của `tolerant_v3`→`tolerant_v4` (tag 6) và của `targeted_lp` (tag `ext_seed`) theo **vị trí** cell (`c_idx`). Realisation của v4 và `targeted_lp` trong `ext_tlp3_p4h2` vì vậy là **realisation confirmatory duy nhất** của P5. Mọi test ghép cặp của P5 chỉ dùng dòng trong chính run này.
- `tlp2_db` và `tlp2_db_p3` seed theo nội dung input (data, skeleton, lag_max, H, tag), nên không phụ thuộc `c_idx`.
- Config này có cùng danh sách kinds/rates và cùng seed_base với `ext_v51_p4h2` (P1). Data (seed `[unit, 2, T]`), skeleton (seed `[unit, 1, k_idx]`), `c_idx`, hệ số frozen `mod|*` và seed của `tolerant_v3` đều giống nhau, nên **dòng v4 ở T80/150 phải trùng bit-for-bit với P1**. Trên D-07 điều này đúng ở 420/420 run mỗi T (mục 1). Analyzer báo kiểm tra này một cách mô tả, khi `results/ext_v51_p4h2/runs.jsonl` có. Nếu không trùng, báo lỗi tái lập; verdict của P5 không đổi.
- Hệ quả của E1, ghi trước: (a) một config P4-H2 có danh sách kinds khác (ví dụ chỉ [missing]) sẽ có skeleton khác (do `k_idx`), không chỉ draw khác. Spec nào muốn cùng realisation với P1/P5 phải giữ đúng danh sách [extra, missing, reversed] × [0.2, 0.5]. (b) Không được tách P5 theo cell; tách theo T thì an toàn về seed, nhưng spec này không tách.

## 4. Budget: cách ước lượng (ghi trước khi đo)

- Số liệu D-07 hiện có: tổng thời gian các run T80/150 của tlp2 (t80a, t80b, t80c, t150a–d) theo manifest là 1326 + 737 + 550 + 364 + 979 + 634 + 675 = 5265 s (khoảng 88 phút). Con số này gồm 7 lần calibration phase, mỗi lần có calibrate `targeted_lp` cho `tlp2_lp_cal`, cùng `tlp2_lp_cal` ở main phase. P5 không có hai phần đó, nên 88 phút là **cận trên**.
- Smoke `ext_tlp3_smoke` (D-07H development, 3 topology × 1 replicate, calibration 3 topology, `--workers 3`): ba unit chạy song song, nên thời gian main của smoke ≈ thời gian một unit (t_unit). Ước lượng P5 = 20 × t_unit (60 unit / 3 worker) + calibration (20 unit × 1 replicate, chỉ có plugin và tolerant_v3; ước lượng bằng tỷ lệ từ smoke). Ghi vào `results/ext_tlp3_checks/runtime_estimate.json`.
- Smoke chỉ để đo thời gian và chạy thử analyzer (dev mode). Không rule nào đọc số IS/coverage của smoke.

## 5. Khi nào rút P5 (ghi trước)

P5 bị **rút** (không chạy trên P4-H2) nếu một trong các điều sau đúng lúc lead khoá danh sách spec:
- (W1) Người dùng không duyệt ngoại lệ budget cho P5 (khoảng 75–90 phút với `--workers 3`).
- (W2) Spec P7 (R3-1, `baselines3`) đã khoá có chứa **cả** `tlp2_db_p3` **và** một bản TLP calibrate (`targeted_lp_cal` hoặc tương đương) ở **mọi 12 cell hỏng T80/150**, với Holm trên toàn family. Khi đó P5 trùng lặp và chỉ tốn budget. Nếu P7 chỉ phủ cell missing (như dự kiến ở R3-1), P5 **không** trùng: nó là spec duy nhất đặt câu về bản double bootstrap đúng bài (`tlp2_db`) và về các cell extra/reversed.

Khuyến nghị của tôi: khi không đúng W1–W2, giữ P5 làm secondary và chạy **cuối cùng** (sau P1 → P2 → P3/P4 → P7), đúng thứ tự synthesis 3.3. Nếu budget chặt, P5 là spec đầu tiên nên bỏ. Lý do: claim chính của paper là P7, không phải P5. Trên D-07, biên của v4 trước TLP ở T ≥ 80 lớn (12/12 qua Holm), nên giá trị thông tin của P5 thấp hơn chi phí 75–90 phút CPU.

## 6. Kiểm tra sẽ chạy ngay sau khi ghi các mục trên (đều không phải evaluation)

- (K1) `preflight.py` trên code hiện tại: kỳ vọng `ok: true`, registry resolve đúng module, không có tên trùng.
- (K2) Smoke `ext_tlp3_smoke` trên D-07H development bằng runner gốc, rồi `analyze_p4h2.py --dev`: kỳ vọng 0 run fail, analyzer chạy hết. Ghi thời gian.
- (K3) Chấm lại bằng `analyze_p4h2.py --dev` các run D-07 development đã có của tlp2 (các dòng T80/150 của t80a, t80b, t80c, t150a–d). Kỳ vọng: số thắng của v4 theo gate view và qua Holm là 12/12 cho cả ba X. Đây là con số mà `results/ext_tlp2_rules/rules.json` báo cho họ T ≥ 80. CI có thể lệch nhẹ vì seed bootstrap giờ theo từng so sánh.
- (K4) Như K3, nhưng thay dòng v4 bằng dòng v4 của `ext_tlp_eval` (sensitivity v4r1 của tlp2): kỳ vọng `targeted_lp` 11/12 qua Holm, còn `tlp2_db` và `tlp2_db_p3` 12/12. Verdict dev là A'.
- Nếu K3/K4 lệch kỳ vọng thì đó là lỗi cài đặt của analyzer (rule ở mục 3 là chuẩn). Lỗi đó sẽ được sửa **trong chính file analyzer mới** (chưa frozen, chưa dùng cho P4-H2) và ghi lại ở đây.

## 7. Kết quả các kiểm tra (append sau khi chạy; mục 0–6 không đổi)

**K1 preflight** (06:05:01Z; `results/ext_tlp3_preflight/preflight_spec_time.json`): lần chạy đầu lúc doc này chưa tồn tại fail đúng một điểm ("spec file missing: docs/ext/tlp3.md"). Sau khi ghi doc: `ok: true`. Registry resolve đúng `targeted_lp → paper4.ext_tlp`, `tlp2_db`/`tlp2_db_p3 → paper4.ext_tlp2`; không tên method nào bị nhiều module `ext_*` định nghĩa, kể cả `ext_baselines3.py` và `ext_revlag3.py` mới của vòng 3.

**K2 smoke** (`ext_tlp3_smoke`, D-07H development, 3 topology × 1 replicate, `--workers 3`; log `experiments/ext/tlp3/logs/smoke.log`): 168 dòng, **0 fail**, 233.2 s. Calibration xong lúc 06:05:13Z (khoảng 11 s), main khoảng 222 s. `analyze_p4h2.py --dev` chạy hết (`results/ext_tlp3_smoke_dev_analyze/`). Không đọc số IS/coverage của smoke cho mục đích nào.

**Ước lượng budget** (`results/ext_tlp3_checks/runtime_estimate.json`): 20 × 222 s main + khoảng 77 s calibration ≈ **75 phút** với `--workers 3`. Cận trên theo D-07 là 87.8 phút. Khoảng ghi cho người dùng duyệt: **70–90 phút**. Smoke chỉ có 3 unit, và tải máy (các agent khác chạy song song) có thể kéo dài thời gian.

**K3** (dev rescore các dòng T80/150 đã có của tlp2, `results/ext_tlp3_checks/k3_dev_rescore/`): v4 thắng theo gate view và qua Holm ở 12/12 cho cả ba X, X thắng 0 cell theo cả hai view; nhãn dev "CONFIRMED-A", đúng kỳ vọng. So với `results/ext_tlp2_rules/rules.json` (`results/ext_tlp3_checks/k3_k4_crosscheck.json`): d và coverage **trùng hoàn toàn** (sai khác tối đa 0); cận CI lệch tối đa 0.027 do seed bootstrap giờ riêng theo từng so sánh.

**K4** (như K3, dòng v4 lấy từ `ext_tlp_eval`, `results/ext_tlp3_checks/k4_dev_rescore_v4r1/`): `targeted_lp` 11/12 (11 qua Holm), `tlp2_db` và `tlp2_db_p3` 12/12; nhãn dev "CONFIRMED-A'", đúng kỳ vọng. Cell hòa là T80 missing 0.2: −0.18 [−0.38, +0.02], p = 0.079.

**Kiểm tra thêm (không ghi trước ở mục 6, công bố ở đây):**
- K5, tiêm lỗi (`results/ext_tlp3_checks/k5_failure_injection/`): 7 run `tlp2_db` fail ở T80 missing 0.5 cho 53/60 cặp ok < 54, và verdict thành "NOT CONFIRMED (incomplete: tlp2_db@80|missing|0.5)". 3 run v4 fail ở T150 extra 0.2 hạ cov(v4) từ 0.962 xuống 0.898, vì run fail tính là không phủ.
- K6, chế độ confirmatory trên run smoke (`results/ext_tlp3_checks/k6_confirmatory_mode_on_smoke/`): config check báo MISMATCH, verdict "INVALID", đúng thiết kế. Kiểm tra realisation P1 báo "not available".
- Thời điểm gián đoạn lần 1 của tlp2: `results/ext_tlp2_checks/check_impl.json` có mtime 19:50:36Z và `results/ext_tlp2_probe/summary.md` có mtime 19:54:01Z ngày 2026-11-01 (02:50–02:54 giờ +07:00 ngày 2026-11-02). Điều này khớp với correction 3 đã append vào tlp2.md.

**Không có thay đổi nào cho analyzer sau K3–K6.** Spec ở mục 3 là bản cuối.

## 8. Kết luận R3-5

- **P5 đã sửa đủ (1)–(5)** bằng file mới: config `experiments/configs/ext_tlp3_p4h2.json`, analyzer `experiments/ext/tlp3/analyze_p4h2.py`, preflight `experiments/ext/tlp3/preflight.py`, manifest `experiments/ext/tlp3/p4h2_spec_files.json`. File cũ `ext_tlp2_p4h2.json` và `tlp2/score.py` không được dùng cho P4-H2.
- **A' bắt buộc Holm**, nhất quán giữa doc (mục 2–3) và analyzer (`decide`).
- **Rút hay giữ:** lúc 06:09Z `docs/ext/baselines3.md` vẫn chưa có, nên chưa thể áp W2. Khuyến nghị: giữ P5 làm secondary, chạy cuối cùng, nếu người dùng duyệt 70–90 phút. Rút P5 nếu W1 hoặc W2 (mục 5) đúng lúc lead khoá danh sách spec. Nếu budget chặt, P5 là spec nên bỏ đầu tiên. Khi rút, câu TLP của paper giữ ở mức exploratory: câu A' đã sửa ở synthesis vòng 2, mục 1.7, cộng correction 1 trong tlp2.md.
- **Lưu ý cho `baselines3`/lead:** P7 muốn dùng chung realisation v4 với P1/P5 thì phải giữ kinds [extra, missing, reversed] × rates [0.2, 0.5]. Nếu chỉ chạy [missing], skeleton cũng khác (seed `[unit, 1, k_idx]`), không chỉ bootstrap draw. `tlp2_db_p3` seed theo nội dung, nên trên cùng data và skeleton nó cho cùng dòng ở mọi config.
