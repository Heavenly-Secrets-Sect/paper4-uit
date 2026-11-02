# RQ4.1 trên P4-H1: nhân bản held-out đặc trưng sai số theo loại hỏng, mức hỏng và T

**Trạng thái (đọc trước khi đọc số).** Đây là **nhân bản held-out (held-out replication)** trên topology mới so với D-07, **không phải xác nhận niêm phong** như P4-H2. Bank P4-H1 đã được dùng trước đó: split confirmatory dùng cho v4 held-out (`rq42_v4_heldout`, `a2_heldout`-họ), split development dùng cho các kiểm tra nhóm A. Vì vậy kết luận tối đa là "số liệu D-07 có/không lặp lại trên 40 topology khác với seed mới", và các topology này không còn "chưa ai nhìn". Không chạm P4-H2 (mọi split) và D-07H (chỉ đọc file calibration đã đóng băng).

**Ngày ghi:** 2026-11-03. Phần "Đăng ký trước" dưới đây được ghi, hash (xem `results/ext_p4h1_rq41_prereg/hashes.txt`) và lưu snapshot nguyên văn **trước** lượt đánh giá đầy đủ đầu tiên. Phần "Kết quả" append sau, không sửa phần đăng ký.

## File của hướng này (không sửa file nào có sẵn)

| File | Vai trò |
|---|---|
| `experiments/configs/ext_p4h1_rq41_main.json` | Config |
| `experiments/ext/p4h1/rq41/run_pairs_p4h1.py` | Runner pair-level, chuyển thể từ `experiments/ext/metrics/run_pairs.py` (D-07, không sửa) |
| `experiments/ext/p4h1/rq41/analyze_p4h1_rq41.py` | Analyzer: tính các quy tắc và bảng |
| `results/ext_p4h1_rq41_main/` | Pair-level rows (`pairs.npz`), trạng thái từng run, null pair, manifest |
| `results/ext_p4h1_rq41_analysis/` | `rules.json`, `analysis.md` (mọi số trích ở dưới) |
| `results/ext_p4h1_rq41_d07ref/` | Cùng analyzer chạy trên pair-level D-07 đã lưu (`results/ext_metrics_pairs/pairs.npz`), làm mốc tham chiếu |
| `results/ext_p4h1_rq41_prereg/` | Hash và snapshot đăng ký trước |

## Đăng ký trước

### Thiết kế

- Bank P4-H1, **cả hai split** (`load_bank("P4-H1", "development")` và `"confirmatory"`), 20 topology mỗi split, tổng **40 cụm topology**; 3 replicate mỗi topology (120 unit).
- T ∈ {40, 80, 150}; cell: `none` và {extra, missing, reversed} × {0.2, 0.5}. H = 4, lag_max = 2, n_boot = 199, tau_effect = 0.1 (như D-07).
- Methods: `oracle`, `plugin`, `tolerant_v4` (hệ số width đóng băng `experiments/calibration/tolerant_v4_frozen.json`, khoá `mod|T|kind`), `tolerant_v5_1` (`src/paper4/ext_v51.py`, hệ số đóng băng `experiments/ext/v51/frozen_v4_v51.json`, khoá `tolerant_v5_1|T|kind`). **Cả 3 giá trị T (40, 80, 150) đều có trong file đóng băng; không thiếu T nào**, nên không phải hạn chế T.
- **seed_base = 80261102.** Đã kiểm tra: không có `results/*/manifest.json` nào dùng 80261102 hoặc 80261103 trước khi bắt đầu. (Hai hướng song song `p4h1_rq43` và `p4h1_rq44` cũng khai báo seed_base 80261102 trên P4-H1 trong config của chúng; đó là thực nghiệm khác, không có manifest, nên không vi phạm điều kiện; không dùng chung file hay kết quả.) Unit seed = `seed_base + 100000·split_index + 1000·topology_index + replicate`, split_index 0 = development, 1 = confirmatory, để hai split không dùng chung stream.
- Methods chỉ thấy dữ liệu, skeleton công khai (`run_experiment.public()`, không có damage log, không có lag hint) và `skel.damage`. Truth chỉ phần đánh giá đọc (role, C thật, lag thật). **Khác bản D-07:** `run_pairs.py` của D-07 đưa skeleton đầy đủ cho method; bản này đưa `public(skel)` theo luật 2. Method không đọc log, nên số không đổi về nguyên tắc.
- Probe thời gian (4 unit lấy cách đều, `results/ext_p4h1_rq41_main_probe/`, 23.5 s) chạy **trước** khi đăng ký, chỉ để đo thời gian và kiểm tra `status == ok`; analyzer không được chạy trên probe và không số nào của nó được dùng.

### Mốc tham chiếu D-07 (đọc từ file đã lưu, trích nguyên văn)

Nguồn: `docs/ext/metrics.md` và `docs/ext/bang_ban_thao.md` bảng 4a, 4b, M6; số D-07 development, 20 topology × 3, seed 20261102:

- Bảng 4a: plugin trên cặp `damaged`, missing: rel = **1.000** ở mọi (T, rate); mean-lag error 0.92–1.19; coverage plugin trên missing-0.5 (`results/ext_metrics_rq41/cells.json`): **0.353 (T40), 0.337 (T80), 0.328 (T150)**.
- M6: "Khi skeleton thiếu cạnh, cách báo một điểm (plugin) báo hiệu ứng mất đường đi bằng 0: trên damaged pair, sai số tuyệt đối là 1.26–1.34, sai số tương đối là 1.00, và sai số không giảm theo T. Trên cùng các pair, module có sai số tuyệt đối giảm theo T (0.78–0.87 ở T40, 0.45–0.48 ở T80, 0.25–0.27 ở T150)".
- Module (v4) trên damaged missing: rel 0.626 / 0.602 (T40), 0.344 / 0.362 (T80), 0.190 / 0.209 (T150); coverage trên cặp damaged ≥ 0.91 (bảng 4b: 0.912–0.962 theo lag 0; 0.956–0.981 theo lag 1–2).
- Câu "Kết luận được phép viết" của `docs/ext/metrics.md`: lỗi skeleton làm hỏng cường độ và coverage; "Tăng T không sửa được"; lag sai nặng ở cặp damaged (peak hit 0.05–0.15 với plugin).

**Chạy cùng analyzer này trên pair-level D-07** (`results/ext_p4h1_rq41_d07ref/analysis.md`, chạy **trước** khi viết quy tắc, vì đó là D-07, không phải dữ liệu thử): (a) 4/6 cell đúng thứ tự, (b) 3/3, (c) với v4: 6/6 và 4/4 (v5_1 không có trong run D-07), (d) 3/4 ô primary không giảm quá 25%. Tức là **áp nguyên quy tắc dưới đây, D-07 tự nó không đạt (a) và (d)**: ở (a), T40 extra có rel (0.844, 0.862) **cao hơn** reversed (0.735, 0.716); ở (d), missing-0.5 giảm 26.7% (ngay ngoài ngưỡng 25%). Ngưỡng do yêu cầu đặt ra và **không đổi**; mốc này để người đọc hiểu "replicates" khắt khe hơn chính D-07.

### Cách tính (mọi thứ gộp trên cặp, replicate và cả hai split)

- Cặp: mọi cặp có thứ tự non-null (|C_true(H)| > 0.1).
- `role` (truth, chỉ đánh giá): `damaged` = cạnh của chính cặp bị hỏng; `downstream` = có đường đi qua cạnh hỏng; `untouched` = còn lại. Code `roles()` y hệt D-07.
- `rel` = median trên cặp của |Ĉ − C|/|C|; `abs` = median |Ĉ − C|; `mlag` = median |mean lag ước − mean lag thật| (cặp mà cả hai xác định); `peak` = trung bình trên cặp "kept" (Ĉ ≠ 0) của 1[peak lag ước = peak lag thật]; `cov` = tỷ lệ cặp có lo ≤ C thật ≤ hi, cặp bị mất (interval [0, 0]) tính là không phủ.
- CI: bootstrap percentile **theo cụm topology** (resample cả topology, 40 cụm), B = 2000, seed 20261104; cùng ma trận chỉ số resample dùng cho mọi nhóm (ghép cặp giữa method và giữa cell).
- Một cell chỉ được tính (đúng/sai, thắng/thua) khi **mỗi nhóm cặp mà nó so sánh có cặp từ ≥ 8 cụm topology**; ngược lại cell tính là **không thỏa** (bảo thủ; mẫu số không đổi).
- Holm: step-down ở mức 0.05 trên họ kiểm định của từng quy tắc, p một phía bootstrap = (1 + số lần bootstrap ở phía H0)/(B + 1). Holm chỉ dùng để báo "số cell còn lại sau Holm"; **kết luận đạt/không đạt của quy tắc dựa trên ước lượng điểm** (như D-07 phát biểu ngưỡng trên giá trị điểm), số Holm báo cạnh bên mỗi số đếm cell.

### Quy tắc (mirror D-07)

**(a) Thứ tự mức nặng.** Với mỗi (T, rate) trong 6 cell (T ∈ {40, 80, 150} × rate ∈ {0.2, 0.5}): lấy `rel` của **plugin** trên cặp `damaged` cho missing, reversed, extra. Cell **đúng thứ tự** nếu `rel_missing > rel_reversed > rel_extra` (chặt) và cả ba nhóm có ≥ 8 cụm. Quy tắc đạt nếu **≥ 80% cell đúng, tức ≥ 5/6**. Báo kèm: hiệu missing − reversed và reversed − extra với CI cụm, và số cell mà cả hai hiệu có ý nghĩa sau Holm (họ 12 kiểm định, H0: hiệu ≤ 0).

**(b) Coverage của plugin dưới missing-0.5.** Với mỗi T ∈ {40, 80, 150}: `cov` của plugin trên **mọi cặp non-null** của cell missing-0.5 (cùng định nghĩa với run-level D-07 `n_covered_nonnull/n_nonnull`, gộp mọi role). Đạt nếu **ước lượng điểm < 0.60 ở cả 3 T** (và ≥ 8 cụm). Báo CI cụm và số cell có ý nghĩa sau Holm (họ 3, H0: cov ≥ 0.60).

**(c) v4 và v5_1 so với plugin.** Cho mỗi method m ∈ {tolerant_v4, tolerant_v5_1}:
 1. **Giảm sai số.** Trên cặp `damaged` của cell missing, với mỗi (T, rate) (6 cell): `rel_m < rel_plugin` (ước lượng điểm của median; hiệu m − plugin, CI cụm). "Mọi T" được áp dụng chặt: cần **6/6 cell** (cả hai rate ở mỗi T).
 2. **Coverage.** Trên cặp `damaged` của cell missing ở T ∈ {80, 150} × rate ∈ {0.2, 0.5} (4 cell): `cov_m ≥ 0.90` (điểm). Cần **4/4**. Coverage trên mọi cặp non-null của cell cũng báo, mô tả, không vào quy tắc.
 Quy tắc (c) đạt nếu **cả hai** method thỏa cả hai điều kiện. Holm: họ 12 kiểm định cho điều kiện 1 (H0: hiệu ≥ 0), họ 8 cho điều kiện 2 (H0: cov ≤ 0.90).

**(d) Lag của plugin không giảm theo T.** Với cặp `damaged`, `mlag` của plugin: tỷ số `r = mlag(T150) / mlag(T40)`. "Không giảm quá 25%" nghĩa là **r ≥ 0.75**. Các ô tính vào quy tắc: **missing và reversed × {0.2, 0.5} (4 ô)**, đạt nếu 4/4 ô có r ≥ 0.75 (mỗi T ≥ 8 cụm). Cell extra (2 ô) được **báo mô tả, không vào verdict**, vì (i) dự đoán E3/E4 của D-07 về lag của cặp damaged chỉ nói về missing và reversed, và (ii) cặp "damaged" của extra là cạnh thừa mà hiệu ứng thật đến từ đường khác (bảng 4a D-07: mlag của extra giảm 43–45% từ T40 xuống T150, tức D-07 không thỏa nếu tính cả extra). Đây là **một lựa chọn diễn giải của người thực hiện**, ghi rõ ở đây trước khi chạy. Báo CI cụm của r; Holm họ 4 (H0: r ≤ 0.75).

**Verdict.** "**Nhân bản được**" = (a), (b), (c), (d) đều đạt. Báo từng phần riêng (một phần trượt không bị che bởi phần khác). Số cell mô tả và số D-07 tham chiếu ở trên được đặt cạnh nhau trong phần kết quả.

### Dự đoán ghi trước (chỉ để đối chiếu)

- (b) và (c) đạt, vì kết quả D-07 ở đó rất xa ngưỡng (coverage plugin 0.33–0.35 so với 0.60; rel giảm từ 1.00 xuống ≤ 0.63).
- (a) khả năng trượt hoặc sát ngưỡng ở T40 (D-07 trượt 2/6 chính ở đó, vì extra rel cao khi T nhỏ), nên "đạt ≥ 5/6" không chắc.
- (d) sát ngưỡng ở missing-0.5 (D-07: −26.7%).
- v5_1 (chưa có số pair-level nào): kỳ vọng tương tự v4 vì cùng lớp phương pháp, nhưng ở T40 có thể có sai số điểm khác v4.

### Điều kiện hợp lệ của lượt chạy

- Mọi run phải có `status == ok` cho cả 4 method; số run lỗi báo nguyên văn (`manifest.json`, `runs_status.jsonl`). Nếu có run lỗi, các cặp của run đó không có trong bảng, và số run lỗi được nêu cùng mỗi kết luận.
- Không thể đối chiếu từng số với `a2_baselines` (khác bank và seed), nên không có kiểm tra khớp chính xác; thay vào đó phần "Kết quả" nêu sanity: số cặp non-null mỗi unit giống nhau giữa các method, và ở cell `none` oracle tốt hơn plugin.

### Giới hạn đã biết

- Held-out replication, không phải xác nhận. Topology mới nhưng bank P4-H1 đã dùng trước.
- Trong v4/v5_1, module đưa lag từ fit đơn khi có repair; kết quả lag của module không nằm trong quy tắc.
- Median của sai số cặp bị chi phối bởi giá trị trần 1.00 của plugin khi cặp bị mất (rel = 1.000 chính xác); quy tắc (a) so sánh missing với reversed/extra nên hiệu missing − reversed chủ yếu đo "mất hẳn" so với "lệch".
- Cell extra có ít cặp damaged (mỗi cell chỉ một phần nhỏ topology có cặp non-null); điều kiện ≥ 8 cụm áp dụng.
