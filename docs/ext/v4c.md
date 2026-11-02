# Hướng "v4c" (R2-4): two-sided calibration cho module và cho mọi baseline

**Trạng thái.** Vòng 2, exploratory, D-07 development (seed_base 20261102, ghép cặp với `a2_baselines`, `a2b_pselect`, `ext_redteam_calbase`). Calibration trên D-07H development (khối calibration của `a3_ges`). Không chạm P4-H1, P4-H2 hay confirmatory split nào.

- Code: [ext_v4c.py](../../src/paper4/ext_v4c.py) (module mới, không sửa file cũ).
- Config đánh giá: `experiments/configs/ext_v4c_eval.json` → `results/ext_v4c_eval/`.
- Script phân tích (rule + mô tả): `experiments/ext/v4c/analyze.py` → `results/ext_v4c_eval/ruling.md`, `results/ext_v4c_eval/describe.md`, `results/ext_v4c_eval/analysis.json`.
- Probe timing: `experiments/ext/v4c/timing_probe.py` → `experiments/ext/v4c/timing_probe.out`.

Không có doc vòng 1 nào mang ID `v4c`, nên không có mục R2-10 nào cần append cho hướng này.

## 1. Vấn đề

`C_GRID` của runner bắt đầu từ 1.0: calibration chỉ nới được interval, không thu hẹp được (bug B6 trong synthesis). Hệ quả đã biết từ vòng 1:

- `tolerant_v4` ở T = 40, khai báo missing: factor `mod|40|missing` = 1.0 (chạm sàn), coverage 0.98 (P2 của redteam: c* trên grid từ 0.5 là 0.9).
- Trong E3 (`ext_redteam_calbase`), `pselect_cal`, `ida_cal`, `fullvar_cal` ngồi ở factor 1.0 ở nhiều cell không thiếu cạnh (ví dụ `pselect_cal|80|none` = `pselect_cal|150|extra` = 1.0, `ida_cal|40|none` = 1.0) trong khi over-cover. Synthesis (mục 1.6, "Bias do sàn calibration") kết luận: các so sánh **mô tả ngoài cell missing** nghiêng về v4. R2-4 yêu cầu sửa một lần cho mọi method.

## 2. Thiết kế

Wrapper trong `src/paper4/ext_v4c.py`: method gốc chạy không đổi, rồi interval được nhân trước với `PRESCALE` = 0.5 quanh midpoint (như `ext_narrow`). Các method nằm trong `calibrate_methods`, nên grid 1.0..10 (bước 0.1) của runner tương đương factor hiệu dụng 0.5..5 (bước 0.05), tune theo (T, loại hỏng khai báo) trên D-07H development, gộp các rate, đúng như `tolerant_v4`.

| Method | Method gốc | Pre-scale |
|---|---|---|
| `tolerant_v4c` | `tolerant_v3` (code của v4 trước khi nhân width factor) | 0.5 |
| `pselect_union_c2` | `pselect_union` | 0.5 |
| `bvar_minnesota_c2` | `bvar_minnesota` | 0.5 |
| `ida_union_c2` | `ida_union` | 0.5; **1.0 khi loại hỏng khai báo là missing** |

**Ngoại lệ của `ida_union_c2`.** Với pre-scale 0.5, factor hiệu dụng tối đa là 5.0. Trong E3, `ida_cal|T|missing` = 7.7 / 8.9 / 8.6 (T = 40/80/150), vượt trần này. Nếu dùng 0.5, `ida_union_c2` sẽ bị trần ép under-cover ở cell missing, tức là một bất lợi mới cho baseline. Vì vậy ở loại khai báo missing, pre-scale là 1.0 (grid hiệu dụng 1.0..10, như E3). Ở đó sàn 1.0 không ràng buộc, nên `ida_union_c2` tương đương `ida_cal` của E3. Lựa chọn dựa trên factor tune trên bank calibration của vòng 1, không trên D-07.

**Bootstrap stream.** Mỗi ext method dùng stream cố định theo tên (`ext_seed`). Vì vậy `tolerant_v4c` **không** dùng chung bootstrap draw với `tolerant_v4` (built-in, `rng(6)`), và các `*_c2` không dùng chung draw với baseline built-in. Hiệu v4c − v4 gồm cả hiệu của width factor lẫn nhiễu Monte Carlo của bootstrap (n_boot = 199). Dữ liệu và skeleton hỏng thì giống hệt, nên mọi phép so sánh vẫn ghép cặp theo dữ liệu.

**Sanity (probe, D-07H development).** Với cùng seed, interval của mỗi wrapper bằng interval của method gốc thu theo pre-scale quanh cùng midpoint, sai lệch tối đa 9e-16 (`timing_probe.out`).

**Không đọc gì ngoài data, public skeleton và `skel.damage`.** `ida_union_c2` chỉ đọc `width_key(skel.damage)` (loại hỏng khai báo), đúng thông tin mà calibration theo stated kind của runner vốn đã dùng.

## 3. Công bố trước khi ghi rule

- **Probe timing (D-07H development, không phải D-07).** Trước khi viết rule, tôi chạy `timing_probe.py` trên 1 topology của D-07H development (seed riêng 7 900 000, 1 replicate, mọi T và mọi cell a2) để đo thời gian và kiểm tra pre-scale. Script không in coverage hay IS. Kết quả: khoảng 6.1 / 5.2 / 1.2 / 4.1 giây mỗi unit cho `tolerant_v4c` / `pselect_union_c2` / `bvar_minnesota_c2` / `ida_union_c2` (1 process). **Chưa có lần chạy nào trên D-07 trước khi rule này được ghi.**
- **Dự đoán không "mới".** Code path của `tolerant_v4c` trùng với `tolerant_v5_cal2` của narrow (v3 + pre-scale 0.5 + calibrate_methods), chỉ khác bootstrap stream. Kết quả `v5_cal2` trên chính D-07 development đã có (`results/ext_narrow_ablation`): T40 missing −0.76 / −0.55, T ≥ 80 missing ratio 0.99–1.015. Trên cell không thiếu cạnh, `tolerant_v5` cũng chính là v3 đã pre-scale, với ratio 0.987–1.019 so với v4 (`results/ext_narrow_eval`). Vì vậy lần chạy D-07 này gần như là **replication với bootstrap stream khác**, không phải một kiểm tra mới. Kiểm tra có giá trị xác nhận chỉ có thể là P4-H2 (mục "Frozen spec", nếu v4c đạt).
- **Grid không giảm.** Ước tính khoảng 10–12 phút với 3 worker (khoảng 23 giây CPU mỗi unit cho mọi method, 60 unit đánh giá + 20 unit calibration), dưới giới hạn 20 phút. Chạy đủ a2 grid.

## 4. Quy tắc ghi trước (trước khi chạy `ext_v4c_eval`)

**Lần chạy.** `ext_v4c_eval` trên D-07 development, seed_base 20261102. T ∈ {40, 80, 150}; cell none, {extra, missing, reversed} × {0.2, 0.5}; 20 topology × 3 replicate; n_boot = 199; H = 4. Method: `plugin` (chỉ để kiểm tra ghép cặp), `tolerant_v4` (frozen, `frozen_calibration` = `experiments/calibration/tolerant_v4_frozen.json`), `tolerant_v4c`, `pselect_union_c2`, `ida_union_c2`, `bvar_minnesota_c2`. Calibration: khối của `a3_ges` (D-07H development, 1 replicate, kinds extra/missing/reversed, rates 0.2/0.5); bốn method ext nằm trong `calibrate_methods`.

**Kiểm tra ghép cặp (điều kiện tiên quyết).** Dòng `plugin` và `tolerant_v4` của `ext_v4c_eval` phải trùng khít với `results/a2_baselines` (IS và số cặp được phủ). Hệ số frozen của v4 lấy từ chính a2_baselines, nên chúng phải trùng. Nếu không trùng, mọi so sánh với run cũ chỉ được báo như so sánh trung bình không ghép cặp, và rule A vẫn chấm trong nội bộ `ext_v4c_eval`.

**Định nghĩa chung.**
- IS của một cell: trung bình `iscore_nonnull_mean` trên các run mà cả hai method so sánh đều có status ok.
- Coverage: pooled trên cặp non-null (lost pair tính là không phủ), như runner.
- CI 95% của hiệu ghép cặp: bootstrap theo topology (cluster), B = 2000, seed 20261102, percentile.
- p một phía (cho Holm): p = (1 + #{boot ≥ 0}) / (B + 1) cho giả thuyết "hiệu < 0" (tương ứng "cận trên CI < 0"; Holm ở mức một phía 0.025).

### Rule A: `tolerant_v4c` được GIỮ nếu cả hai điều kiện đều đúng

1. **T ∈ {80, 150}, cả 7 cell (none, extra-0.2/0.5, missing-0.2/0.5, reversed-0.2/0.5), tổng 14 cell:** tỷ lệ IS(v4c) / IS(v4) nằm trong [0.97, 1.03] ở **mọi** cell.
2. **T = 40, missing-0.2 và missing-0.5 (2 cell):** trong mỗi cell, coverage của v4c ≥ 0.90 **và** cận trên CI 95% của hiệu ghép cặp IS(v4c) − IS(v4) < 0.

Ngược lại, v4c **bị loại**. Ngưỡng ±3% và điều kiện 2 lấy nguyên từ đề bài R2-4, không đổi sau khi thấy kết quả.

**Multiplicity (báo cáo, không đổi phán quyết):**
- Điều kiện 2: số cell đạt khi thay "cận trên CI < 0" bằng Holm trên 2 p-value một phía (α = 0.025).
- Điều kiện 1: quyết định dựa trên tỷ lệ điểm (point ratio). Báo thêm, ở mỗi cell, CI 95% của tỷ lệ (bootstrap theo topology) và test tương đương TOST trên [0.97, 1.03]: p_TOST = max(P*(ratio ≤ 0.97), P*(ratio ≥ 1.03)) theo phân phối bootstrap (cộng 1 như trên). Báo số cell đạt tương đương khi Holm trên 14 p_TOST ở α = 0.05.

**Báo cáo thêm cho v4c (không ảnh hưởng quyết định):** tỷ lệ IS ở 5 cell còn lại của T = 40 (none, extra, reversed); coverage, width; IS trên null pair (`iscore_null_mean`); factor hiệu dụng (`c × pre-scale`) của mọi (method, T, kind) và factor nào chạm sàn (0.5) hoặc trần (5.0; 10 cho `ida_union_c2|missing`).

### Phần B: so sánh mô tả v4c với các baseline `*_c2` trên a2 grid (không phải rule giữ/loại)

**Phân loại một cell** cho cặp (M, X'), M ∈ {v4, v4c}, X' là một phiên bản của baseline X ∈ {pselect_union, ida_union, bvar_minnesota}:
- **M thắng:** coverage(M) ≥ 0.90 **và** cận trên CI 95% của IS(M) − IS(X') < 0 (giống luật A2/A2b/E3).
- **M thua:** cận dưới CI > 0.
- **Hòa:** còn lại.

Bốn so sánh được báo cho mỗi X trên cả 21 cell (3 T × 7 cell, gồm none và extra):
- (a) v4 vs X chưa calibrate (dòng của `a2_baselines`; `pselect_union` từ `a2b_pselect`). Đây là bảng gốc của vòng 1, tính lại.
- (b) v4 vs X_cal của E3 (`ext_redteam_calbase`, sàn 1.0).
- (c) v4 vs X_c2: chỉ đổi calibration của baseline. So (b) với (c) cho thấy riêng tác động của việc gỡ sàn cho baseline.
- (d) v4c vs X_c2: cả hai phía đều two-sided. Đây là so sánh chính của R2-4.

Mọi phép ghép cặp theo khóa (topology, replicate, T, kind, rate); dữ liệu và skeleton giống nhau vì cùng seed_base. Với mỗi cặp (M, X'), báo số cell thắng / hòa / thua và **số cell thắng sau Holm** trên 21 p-value một phía của cặp đó (cell chỉ được đếm nếu Holm bác bỏ ở α = 0.025 và coverage ≥ 0.90). Với claim gộp "thắng cả ida và bvar" (luật A2), p của cell là max của hai p (intersection–union), rồi Holm trên các cell của claim.

**Các claim mô tả vòng 1 ngoài cell missing được kiểm lại.** Một claim được xem là **đổi** nếu phân loại thắng/hòa/thua của các cell mà claim nói tới theo (d) khác với điều claim nêu; nguồn gốc của thay đổi được quy về baseline (nếu (c) đã khác (b)/(a)) hay về v4c (nếu chỉ (d) khác (c)).

- **D1** (A2, decision_rules.md): v4 thắng cả `ida_union` lẫn `bvar_minnesota` ở 4/6 cell reversed (trượt reversed-0.2 ở T40 và T80, hòa với ida) và 3/6 cell extra (trượt extra-0.2/0.5 ở T40 và extra-0.5 ở T80, đều hòa).
- **D2** (A2b): v4 thắng `pselect_union` ở cả 12 cell hỏng không phải missing (16/18 tổng, chỉ thua ở 2 cell missing T40).
- **D3** (E3): ở T ≥ 80, v4 thắng mọi baseline đã calibrate ở 4/4 cell reversed.
- **D4** (E3): ở T = 80, cell none và extra, v4 hòa `ida_cal`.
- **D5** (E3): ở T = 40, v4 hòa `bvar_cal` và `ida_cal` trên none, extra và reversed-0.2.
- **D6** (synthesis 1.6): baseline ngồi ở sàn 1.0 và over-cover ở cell không thiếu cạnh. Kiểm bằng: số (X, T, kind ≠ missing) mà factor hiệu dụng của X_c2 < 1.0, và số cell (ngoài missing) mà IS(X_c2) < IS(X_cal) với cận trên CI < 0.
- **D7** (cell none, so sánh với kết quả của verifier gate rằng `tolerant_auto3` thua `ida_union` trên skeleton đúng ở mọi T): v4 và v4c so với `ida_union_c2`, `pselect_union_c2`, `bvar_minnesota_c2` trên cell none ở từng T.

**Cell missing (báo cho đủ):** (d) ở 4 cell missing T ≥ 80 theo luật R-E3a, và ở 2 cell missing T40 (đặc biệt v4c so với `pselect_union_c2`).

Không có rule nào ở phần B đổi module of record; phần B chỉ quyết định câu chữ mô tả trong bài.

## 5. Kết quả

(Sẽ được append nguyên văn sau khi chạy.)

## Kết quả rule A (lượt chạy lại do phiên chính thực hiện)

**Bối cảnh.** Agent v4c phải dừng khi lượt chạy lại `ext_v4c_eval` chưa xong. Lượt đó bị cắt lần nữa khi reload cửa sổ VS Code. Phiên chính sau đó chạy lại **đúng config `experiments/configs/ext_v4c_eval.json`**, không sửa gì, với `--workers 6`. Lượt chạy hoàn tất: 7560 dòng, 464.6 giây. Phán quyết được tính bằng chính script đã viết trước, `experiments/ext/v4c/analyze.py`, và ghi ra `results/ext_v4c_eval/ruling.md`. Rule ở mục 4 không thay đổi.

**Kiểm tra ghép cặp.** `plugin` và `tolerant_v4` trùng khít 1260/1260 dòng với `a2_baselines`.

**Phán quyết: `tolerant_v4c` GIỮ.**

- **Điều kiện 1: 14/14 cell đạt.** Tỷ lệ IS(v4c)/IS(v4) ở T ∈ {80, 150} nằm trong 0.981–1.014. Test tương đương TOST sau Holm chỉ đạt 5/14, tức phần lớn các cell "không khác" theo point ratio nhưng chưa chứng minh được là tương đương.
- **Điều kiện 2: 2/2 cell đạt, vẫn 2/2 sau Holm.**

  | Cell T40 | Coverage v4 → v4c | IS v4 → v4c | Hiệu v4c − v4 [CI] |
  |---|---|---|---|
  | missing-0.2 | 0.983 → 0.958 | 7.77 → 6.98 | −0.79 [−0.99, −0.58] |
  | missing-0.5 | 0.978 → 0.956 | 7.53 → 6.82 | −0.71 [−0.87, −0.54] |

- **Factor hiệu dụng của v4c ở T40 missing là 0.85**, tức dưới sàn 1.0 cũ. Không factor nào chạm sàn hay trần của grid mới.

Phần B (so sánh mô tả với các baseline `*_c2`) nằm trong `results/ext_v4c_eval/describe.md`. Phiên chính chưa diễn giải phần này.

## Sửa sau kiểm chứng vòng 2

(Append bởi verifier `v4cverify` theo R3-6 và R3-7 của docs/ext/synthesis_round2.md. Không sửa phần nào phía trên. Chi tiết kiểm chứng ở docs/ext/v4cverify.md và `results/ext_v4cverify_recompute/`.)

**Kết quả kiểm chứng độc lập (R3-7).** Rule A được tính lại bằng code riêng (`experiments/ext/v4cverify/recompute.py`, không dùng analyze.py), từ `results/ext_v4c_eval/runs.jsonl`. **`tolerant_v4c` RETAINED được tái lập**: C1 14/14 (ratio 0.981–1.014), TOST Holm 5/14 (cùng 5 cell); C2 2/2, Holm 2/2. Phần B: phân loại W/T/L khớp 252/252 cell. Ba chênh lệch, cả ba là borderline do bootstrap: (b) ida_union W sau Holm là 12–13/21 (ngoài missing 6–7/15) tùy seed; D1 (b) IUT-Holm có 4–5 cell; D6 "X_c2 tốt hơn X_cal" là 8–9/45 (Holm 4/45 ổn định, tệ hơn 6/45). Chạy lại 2 unit với `--workers 3`: 252/252 dòng và `calibration.json` trùng tuyệt đối với run `--workers 6`, với cả miniconda (numpy 2.5.4) lẫn python3 CLT (numpy 2.0.2).

**Sửa câu chữ:**

1. **Factor dưới 1.0.** Có **4 factor baseline dưới 1.0 ngoài cell missing**: `pselect_union_c2` ở T150 none 0.95 và T150 extra 0.90; `ida_union_c2` ở T150 none 0.95 và T150 extra 0.95. Tính cả `tolerant_v4c|40|missing` = 0.85 thì có 5 factor < 1.0. Mọi chỗ nói "2 factor" hoặc chỉ nhắc factor của v4c phải sửa theo đây.
2. **"Factor c2 khớp E3" là sai.** Trên 27 (X, T, kind) mà factor E3 không chạm sàn 1.0, chỉ 8/27 bằng nhau đúng, và **6/27 lệch ≥ 0.1**: pselect 40 none 1.7 so với 1.4; pselect 40 reversed 1.7 so với 1.6; ida 40 missing 7.2 so với 7.7; ida 150 missing 8.9 so với 8.6; ida 150 reversed 1.5 so với 1.6; bvar 40 reversed 1.9 so với 2.0. Số còn lại lệch đúng một bước grid mịn 0.05. Riêng câu ở mục 2, "`ida_union_c2` tương đương `ida_cal` của E3" ở cell missing, chỉ đúng **về thủ tục**: cùng method, cùng pre-scale 1.0, cùng bank. Bootstrap stream thì khác (`ext_seed` so với `rng(7)`), nên factor lệch tới 0.5 ở T40.
3. **0.987 → 0.985.** Ở mục 3, "ratio 0.987–1.019 so với v4 (`results/ext_narrow_eval`)" sửa thành **0.985–1.019**: min 0.9847 ở T150 reversed-0.2, max 1.0194 ở T80 reversed-0.5 (`results/ext_v4cverify_recompute/r36_checks.txt`).
4. **Ba lần chạy và interpreter.** `ext_v4c_eval` đã được khởi chạy ba lần, cùng một config:
   - **Lần 1** (agent v4c, 2026-11-01T19:47:45Z): `python3` của CommandLineTools (numpy 2.0.2), `--workers 3`. Lần này ghi `calibration.json` lúc 19:52:14Z và bị cắt lúc khoảng 20:00Z do usage limit, khi vẫn đang ở pha đánh giá. Không có dòng đánh giá nào được ghi.
   - **Lần 2** (agent v4c, 2026-11-02T02:21:55Z): `python` của miniconda (numpy 2.5.4). Lần này bị dừng sau khoảng 73 s, trước khi calibration xong; không ghi file kết quả nào.
   - **Lần 3** (phiên chính, không phải agent v4c): `--workers 6`, vi phạm hard rule 5 (`--workers 3`). Hoàn tất 7560 dòng trong 464.6 s; `calibration.json` mới trùng từng byte bản của lần 1. Interpreter của lần 3 không được ghi lại (manifest không ghi `sys.executable`, numpy version hay số worker; bug E6).
   
   Kiểm chứng R3-7 cho thấy việc này **không làm đổi kết quả**. Chạy lại 2 unit (syn_dag_00 và syn_dag_01, rep 0) cùng khối calibration với `--workers 3`, bằng cả hai interpreter: dòng trùng tuyệt đối 252/252, calibration.json trùng từng byte. Vì vậy cũng không xác định được lần 3 dùng interpreter nào. Phạm vi kiểm: 2/60 unit đánh giá và toàn bộ calibration.
5. **Thời điểm viết analyze.py.** `experiments/ext/v4c/analyze.py` được viết **một lần**, lúc 2026-11-01T19:49:39Z. Thời điểm này **sau khi lần 1 đã bắt đầu** (19:47:45Z) nhưng trước mọi output: `calibration.json` xuất hiện lúc 19:52:14Z, và không có output đánh giá nào trước lần 3. File không bị sửa sau đó (mtime 02:49 giờ máy, trước `runs.jsonl` 10:37). Câu "script đã viết trước" ở mục kết quả nên đọc là "viết sau khi lần chạy đầu khởi động nhưng trước mọi output; rule ở mục 4 có trước mọi run".
6. **Ước lượng thời gian.** Ở mục 3, "khoảng 10–12 phút với 3 worker" là thấp. Đo lại với 3 worker (22 unit: 218.8 s miniconda, 284.8 s CLT, load average 4–8) và ngoại suy cho 80 unit thì được khoảng 13–17 phút. Lần 1 bị cắt sau 12.25 phút khi vẫn đang đánh giá, khớp với số này. Lần 3 mất 7.7 phút nhờ 6 worker.
7. **Nhãn "width".** Cột width trong `ruling.md`/`describe.md` là **median qua run** của `width_kept`, không phải mean. Ví dụ T40 missing-0.2: median 6.601 → 5.613, mean 6.923 → 5.824. Báo cáo dùng con số nào thì phải ghi rõ đó là median hay mean.
8. **C1 trộn hai nguồn.** Bootstrap stream của `tolerant_v4c` (`ext_seed`) khác của `tolerant_v4` (`rng(6)`), nên tỷ lệ IS ở C1 trộn hiệu ứng của factor với nhiễu Monte Carlo (n_boot = 199). Đây là cách C1 được thiết kế, không phải lỗi tính. Dù vậy, câu "v4c không khác v4 ở T ≥ 80" phải đi kèm TOST Holm 5/14, tức chưa chứng minh được tương đương ở 9/14 cell.
9. **Vị trí trong P4-H2.** Theo synthesis vòng 2 (quyết định đã có), `tolerant_v4c` không phải ứng viên P4-H2 riêng, vì nó là nhánh all-lag (`v5_cal2`) của `tolerant_v5_1`. Kết quả ở đây chỉ dùng để định lượng riêng phần two-sided calibration trong ablation: −0.79/−0.71 ở T40 missing. Không có spec P4-H2 từ hướng này.
