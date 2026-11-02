# Vòng 3, R3-3: sửa frozen spec P4-H2 của `tolerant_auto3` (ID `auto3fix`, nối tiếp `auto5`)

**Trạng thái.** Exploratory/spec. Mọi phân tích ở đây chỉ dùng row **đã lưu** trên D-07 development (seed_base 20261102). Không có run mới nào, không có probe mới, không đụng P4-H1, P4-H2 hay split confirmatory. Không chạy bất kỳ config P4-H2 nào. Không sửa file có sẵn nào; `tolerant_auto3` (`src/paper4/ext_gate.py`) và bảng width (`experiments/ext/gate/width_table.json`) giữ nguyên từng byte.

Việc được giao (synthesis_round2.md, mục 3.2 dòng P2 và R3-3): sửa ba điểm của spec P2 bằng **file mới**:
1. run auto3 thất bại hiện bị bỏ âm thầm khi gộp coverage (`experiments/ext/auto5/check_p4h2.py`);
2. báo số run ok theo cell;
3. ghi trước câu về độ mong manh: dry run D-07 chỉ đạt 0.903 ở T80 reversed-0.5 (Holm 13/14).

Thêm: manifest spec (`experiments/ext/auto3fix/p4h2_spec_files.json`), hệ quả của bug E1 (không sửa trước P4-H2, theo quyết định của người dùng), và một so sánh mô tả auto3 với `tolerant_v5_1` trên row a2-grid đã lưu.

---

## 1. Quy tắc ghi trước

*Ghi lúc 2026-11-02T06:02Z, trước khi viết hay chạy bất kỳ script phân tích nào của hướng này (dry run D-07 của analyzer mới, bootstrap độ mong manh, ghép cặp với v5_1).*

### 1.1 Rule xác nhận P4-H2 (spec P2 đã sửa, thay thế `check_p4h2.py`)

Bốn điều kiện C1, C2, C3, L1 **giữ nguyên ngưỡng và cell** của spec cũ (auto5.md, "Frozen spec for P4-H2"; B1 của decision_rules.md). Chỉ cách xử lý run thất bại/thiếu và các kiểm tra toàn vẹn là mới. Analyzer: `experiments/ext/auto3fix/check_p4h2_v2.py`.

**Đơn vị và số run kỳ vọng.** Mỗi cell (scenario, T, kind, rate) có `n_exp` = số topology trong manifest × số replicate của config (20 × 3 = 60 trên P4-H2). Với mỗi method trong mỗi cell, analyzer đếm `n_ok` (status = ok và có `iscore_nonnull_mean`), `n_fail` (có row nhưng status ≠ ok) và `n_absent` (không có row). `n_bad = n_fail + n_absent`.

**Coverage dùng cho quyết định (định nghĩa mới, "failed = uncovered").** Với auto3 trong một cell:
- tử số = tổng `n_covered_nonnull` trên các run ok;
- mẫu số = tổng `n_nonnull` trên **cả `n_exp` đơn vị**. Với một đơn vị thất bại hoặc thiếu row, `n_nonnull` lấy từ bất kỳ row ok nào của cùng (topology, replicate) trong cùng run, vì số pair non-null chỉ phụ thuộc truth SEM, H và tau (không phụ thuộc T, cell, method hay scenario; analyzer kiểm tra tính hằng này và báo lỗi toàn vẹn nếu sai). Tức là run thất bại được tính là **không cover pair nào**.
- Nếu không dựng được mẫu số cho một đơn vị (không có row ok nào của (topology, replicate) đó), cell đó **trượt**.
- Coverage theo định nghĩa cũ (chỉ trên run ok) được báo kèm, không quyết định.

**Trần thất bại.** Một cell của rule (8 cell C1, 3 cell C2, 2 cell C3, 4 cell L1) **trượt** nếu auto3 có `n_bad > 3` (tức > 5% của 60). Cell có 0 run ok thì trượt (coverage = 0, IS không xác định), script không crash.

**Tỉ số IS (C2, C3).** Trung bình `iscore_nonnull_mean` trên các đơn vị mà **cả** auto3 và `tolerant_v4` đều ok (ghép cặp), rồi lấy tỉ số. Khi không có run nào thất bại, định nghĩa này trùng với định nghĩa cũ. Nếu số đơn vị ghép được < `n_exp` − 3, cell trượt.

**Rule (CONFIRMED khi và chỉ khi cả bốn đúng, và mọi kiểm tra toàn vẹn ở dưới đạt):**
- **C1:** coverage (định nghĩa mới) của auto3 ≥ 0.90 ở mọi cell missing và reversed × {0.2, 0.5} tại T = 80 và 150 (8 cell, config 1), mỗi cell đạt trần thất bại.
- **C2:** ở cell none, IS(auto3) ≤ 1.35 × IS(`tolerant_v4`) tại cả ba T = 40, 80, 150 (config 1).
- **C3:** ở cell GES tại T = 80 và 150: coverage (định nghĩa mới) ≥ 0.90 và IS(auto3) ≤ 1.10 × IS(`tolerant_v4`) (config 1).
- **L1:** scenario latent1 (config 2): coverage (định nghĩa mới) ≥ 0.90 ở missing-0.2 và reversed-0.2 tại T = 80 và 150 (4 cell).

**Kiểm tra toàn vẹn (bắt buộc; một kiểm tra trượt thì verdict là NOT CONFIRMED kèm lý do "integrity"):**
- I1: `manifest.json` của mỗi run có `config` **bằng** (so JSON) nội dung file config frozen tương ứng, với `bank` = P4-H2 và `split` = confirmatory.
- I2: manifest liệt kê đúng 20 topology; mọi row thuộc các topology đó; không có (topology, replicate, cell, method) trùng.
- I3: mọi row ok của auto3 có `info_state` ∈ {closed, open, undiagnosable} và `info_c_T` bằng giá trị của bảng width frozen tại (T, state) (undiagnosable dùng closed). Đây là dấu vết hậu kiểm rằng hàm chạy là `ext_gate.tolerant_auto3` với bảng width đã ghim.
- I4: mọi row ok của `tolerant_v4` ở cell không phải GES có `info_c_T` bằng `mod|T|kind` của `tolerant_v4_frozen.json` (cell none dùng `none`); ở cell GES, `info_c_T` thuộc tập giá trị `mod|T|*` của file đó.
- I5: `n_nonnull` hằng trong mỗi (topology, replicate) trên các row ok của run.
- Preflight `experiments/ext/auto3fix/preflight_p4h2.py` (chạy ngay trước run, không đọc topology bank) phải in `PREFLIGHT OK`: `ext_methods()['tolerant_auto3'].__module__ == 'paper4.ext_gate'`; không module ext_* nào khác đăng ký `tolerant_auto3`, `tolerant_v4`, `tolerant_v3`, `plugin` hay `oracle` (runner cho method ext ghi đè built-in cùng tên, bug E4); bảng width và frozen calibration có nội dung như đã ghim; và, nếu lead đưa file hash, sha256 mọi file trong manifest spec khớp.

**Báo kèm, không quyết định:** p một phía cho H0 "coverage ≤ 0.90" bằng cluster bootstrap theo topology (2000 lần, seed 0), với đơn vị thất bại tính vào tử số 0 và mẫu số như trên; số cell bác H0 sau Holm (α 0.05) trên 14 cell coverage (C1 + C3 + L1); `n_ok/n_exp` của mọi method ở mọi cell; coverage theo định nghĩa cũ; tỉ số IS theo định nghĩa cũ (không ghép cặp).

**Nếu NOT CONFIRMED:** claim C-auto ("chế độ không khai báo giữ coverage ở T ≥ 80") chỉ còn là exploratory trên D-07 development; paper trình bày chế độ có khai báo là chính.

### 1.2 Câu về độ mong manh (ghi trước P4-H2, bắt buộc đi kèm mọi lần báo kết quả P2)

> Trên dry run D-07 development, auto3 đạt C1 ở T80 reversed-0.5 với coverage 0.903, ngay trên ngưỡng 0.90, và đây là cell duy nhất trong 14 cell coverage mà Holm không bác được "coverage ≤ 0.90" (13/14). Với 20 topology, CI của coverage một cell rộng khoảng ±0.03. Vì vậy P2 có xác suất đáng kể trượt C1 ở cell này **ngay cả khi** hành vi của auto3 trên P4-H2 giống hệt D-07; một kết quả NOT CONFIRMED do riêng cell này không phải bằng chứng auto3 tệ đi, và một kết quả CONFIRMED không loại được coverage thật dưới 0.90 ở cell này.

Mục 3 bổ sung một con số mô tả cho câu này (xác suất CONFIRMED khi bootstrap topology trên row D-07), tính **sau** khi câu trên đã được ghi. Con số đó không đổi rule.

### 1.3 Phân tích mô tả (không có rule, không quyết định)

- **D1. Dry run của analyzer mới trên row D-07** (`ext_gate_auto3` + `ext_auto5_a1`), chế độ `--dry-run`. Mong đợi: verdict trùng dry run cũ (CONFIRMED, Holm 13/14), vì trên D-07 auto3 không có run thất bại. Kiểm tra I1 bỏ qua ở chế độ dry run (config D-07 khác config P4-H2); I3–I5 vẫn chạy. Kết quả: `results/ext_auto3fix_dryrun/`.
- **D2. Độ mong manh.** Cluster bootstrap theo topology (2000 lần, seed 0) trên row D-07 của dry run: cùng một tập chỉ số topology được rút cho cả hai run (P4-H2 cũng dùng cùng 20 topology cho hai config). Với mỗi bản bootstrap, áp dụng đúng rule 1.1 (coverage gộp, tỉ số IS ghép cặp). Báo tỉ lệ bản bootstrap CONFIRMED, tỉ lệ trượt từng điều kiện và từng cell, và P(coverage ≤ 0.90) ở T80 reversed-0.5. Diễn giải: xác suất CONFIRMED nếu P4-H2 là một mẫu 20 topology "như D-07" và hiệu năng D-07 là thật. Con số này **lạc quan** (D-07 đã dùng để chọn auto3; không tính chênh lệch D-07H/D-07/P4-H2, không tính khác biệt seed bootstrap). Kết quả: `results/ext_auto3fix_fragility/`.
- **D3. auto3 so với `tolerant_v5_1` trên a2 grid đã lưu.** Row auto3 của `results/ext_gate_auto3` và row v5_1 của `results/ext_v51_eval`. Ghép cặp theo (topology, replicate, T, kind, rate), chỉ khi kiểm tra ghép cặp đạt: row `tolerant_v4` của hai run phải trùng `iscore_nonnull_mean` ở mọi key chung (cùng data, cùng skeleton, cùng seed v4). Với 21 cell (T 40/80/150 × none, extra/missing/reversed × 0.2/0.5): coverage hai method, IS, chênh lệch ghép cặp IS(auto3) − IS(v5_1) với 95% CI cluster bootstrap theo topology (2000, seed 0), p hai phía; số cell auto3 tốt hơn/hòa/tệ hơn, thô và sau Holm trên 21 cell. Đây **không** phải so sánh cùng chế độ: v5_1 đọc mức hỏng khai báo, auto3 thì không. Số này chỉ định lượng "cái giá của việc không đọc khai báo" so với ứng viên chế độ khai báo. Kết quả: `results/ext_auto3fix_v51pair/`.
- **D4. Hệ quả E1 trên D-07 (kiểm tra cụ thể).** So row `plugin` (và `tolerant_v4`) clean ở cell none/missing-0.2/reversed-0.2, T80/150, giữa `ext_auto5_a1` (danh sách cell như config 2) và `ext_gate_auto3` (danh sách cell như config 1), để xác nhận rằng hai config cho realisation khác nhau ở cell damaged. Kết quả: `results/ext_auto3fix_e1/`.

---

## 2. Kết quả D1: dry run của analyzer mới trên row D-07 (append sau khi chạy, nguyên văn)

Quy tắc mục 1 được lưu lúc 2026-11-02T06:02:39Z. Analyzer `experiments/ext/auto3fix/check_p4h2_v2.py` được viết sau đó; dry run cuối chạy lúc 06:04:54Z. Mọi số dưới đây nằm trong `results/ext_auto3fix_dryrun/check.md` và `check.json`.

**Sửa một lỗi trong kiểm tra toàn vẹn I4, công bố.** Lần dry run đầu tiên (khoảng 06:04Z) báo I4 FAIL: 20 row `tolerant_v4` ở cell reversed-0.2 có `info_c_T` khác `mod|T|reversed`. Nguyên nhân là định nghĩa I4 trong mục 1.1 viết sai so với runner: runner chọn factor bằng `methods.width_key(stated damage)`, và khi số cạnh đảo khai báo k = 0 (topology ít cạnh cùng kỳ, ví dụ `syn_dag_06`, `syn_dag_15`) key là `none`. I4 được sửa thành "`mod|T|width_key`", tức `none` khi k = 0, ngược lại là kind. Đây là sửa một kiểm tra hậu kiểm cho khớp code đã frozen; ngưỡng, cell và cách tính của C1–C3, L1 không đổi. Việc sửa diễn ra trước mọi lần dùng P4-H2, và chỉ dựa trên row D-07 đã lưu.

**Kết quả dry run (D-07 development, KHÔNG phải xác nhận):** I1 bỏ qua (dry run), I2–I5 OK (2880 row auto3 ok khớp bảng width; 2879 row v4 ok khớp frozen factor). auto3 có **60/60 run ok ở mọi cell** của cả hai run, nên coverage theo định nghĩa mới trùng định nghĩa cũ.

| Điều kiện | D-07 dry run (định nghĩa mới) | Đạt? |
|---|---|---|
| C1 (8 cell) | T80: missing 0.951 / 0.949, reversed 0.932 / **0.903**; T150: missing 0.980 / 0.980, reversed 0.971 / 0.966 | đạt |
| C2 | 1.124 / 1.071 / 1.195 (ghép cặp n = 60 / 60 / 60) | đạt |
| C3 | T80 cov 0.941, ratio 0.955; T150 cov 0.955, ratio 0.968 | đạt |
| L1 | 0.956 / 0.937 / 0.977 / 0.970 | đạt |

Verdict dry run: **CONFIRMED**, trùng dry run cũ. Holm (α 0.05) trên 14 cell coverage: 13/14; cell không bác được là T80 reversed-0.5 (p một phía 0.385). `tolerant_v4` có 59/60 run ok ở T40 GES (một run `underdetermined`), không thuộc cell nào của rule.

**Kiểm tra bằng lỗi tiêm vào** (`experiments/ext/auto3fix/fault_injection.py`, bản sao row D-07 trong scratchpad; output `results/ext_auto3fix_dryrun/fault_injection/`):
- A. 2 run auto3 thất bại ở T80 reversed-0.5: coverage 0.903 → **0.862** (ok-only 0.901), C1 trượt. Tức là chỉ 2 run thất bại trong 60 đã đủ làm trượt cell sát biên này.
- B. Xoá 4 row auto3 ở T150 missing-0.2: bad = 4 > 3, coverage 0.892, cell trượt.
- C. 5 run v4 thất bại ở T80 none: chỉ còn 55 cặp (< 57), C2 trượt (ratio ghép cặp 1.070, không ghép cặp 1.038).
- D. Xoá mọi row auto3 ở latent1 T80 missing-0.2: coverage 0.000, 0/60 run ok, L1 trượt, script không crash.
- Verdict: NOT CONFIRMED, Holm 11/14. Analyzer xử lý đúng cả bốn tình huống.

**Preflight** (`experiments/ext/auto3fix/preflight_p4h2.py`, chạy lúc 06:07Z, chỉ đọc code và config, không đọc topology bank): P1–P5 OK, `PREFLIGHT OK` (`results/ext_auto3fix_dryrun/preflight_dev.json`). Kiểm tra P6 với file hash đúng cho 40/40 khớp; khi đổi một hash, P6 FAIL và exit code 1.

## 3. Kết quả D2: độ mong manh (mô tả; append sau khi chạy, nguyên văn)

`experiments/ext/auto3fix/fragility.py`, 06:07:48Z; `results/ext_auto3fix_fragility/fragility.{md,json}`. Bootstrap 2000 lần theo topology (seed 0) trên row D-07 của dry run, rule đã sửa áp dụng nguyên dạng cho từng bản bootstrap.
- **P(CONFIRMED) = 0.616.**
- P(trượt) theo điều kiện: C1 0.385, C2 0.000, C3 0.000, L1 0.000.
- Cell duy nhất trượt trong ≥ 0.5% số bản bootstrap: T80 reversed-0.5 (0.385). Nó là cell trượt **duy nhất** trong 0.384 số bản.
- Coverage T80 reversed-0.5: 0.903 trên toàn mẫu; bootstrap 2.5/50/97.5% là 0.880 / 0.903 / 0.925; P(cov < 0.90) = 0.385.

Câu mong manh đầy đủ (bổ sung con số vào câu ở mục 1.2, không đổi rule):
> Trên dry run D-07 development, auto3 đạt C1 ở T80 reversed-0.5 với coverage 0.903 (bootstrap theo topology 95%: 0.880–0.925), là cell duy nhất trong 14 mà Holm không bác được "coverage ≤ 0.90" (13/14). Nếu P4-H2 là 20 topology rút giống D-07 và hiệu năng trên D-07 là thật, xác suất spec P2 CONFIRMED chỉ khoảng **0.62**, và gần như toàn bộ rủi ro trượt nằm ở cell này. Con số này còn lạc quan: D-07 đã góp phần chọn auto3, không tính lệch giữa D-07H, D-07 và P4-H2 (auto3 đã mất 0.04 từ probe D-07H sang D-07 ở chính cell này), và trên P4-H2 auto3 dùng seed bootstrap theo tên, khác seed của row D-07. Một kết quả NOT CONFIRMED chỉ do cell này không phải bằng chứng auto3 tệ đi; một kết quả CONFIRMED không loại được coverage thật dưới 0.90 ở cell này.

## 4. Hệ quả của bug E1 cho spec P2 (E1 không sửa trước P4-H2, theo quyết định của người dùng)

Runner seed mọi method bằng `rng([unit, 3, T, c_idx, tag])`, với c_idx là **vị trí** cell trong danh sách cell của config. Damaged skeleton được rút bằng `rng([unit, 1, k_idx])`, với k_idx là vị trí kind trong `["none"] + kinds`. Hệ quả cụ thể cho P2:
1. **Config 1 và spec v5_1 (P1).** Config 1 có thứ tự cell giống `ext_v51_p4h2`/`ext_v51fix_p4h2` ở 7 cell đầu; cell GES đứng cuối nên không làm dịch c_idx. Trên D-07, row v4 của `ext_gate_auto3` và `ext_v51_eval` trùng 1260/1260 (`results/ext_auto3fix_v51pair/pairs.json`). Vì vậy trên P4-H2, row `tolerant_v4` của config 1 phải trùng row v4 của P1 ở 7 cell chung, nếu factor frozen của v4 hai bên giống nhau. Lead nên kiểm tra điều này sau run như một kiểm tra nhất quán mô tả (không thuộc rule). Nếu không trùng, đó là dấu hiệu code hoặc config đã đổi.
2. **Config 2 khác config 1 ở mọi cell damaged.** Config 2 có kinds = [missing, reversed], rates = [0.2], nên k_idx (1, 2 thay vì 2, 3) và c_idx (1, 2 thay vì 3, 5) khác config 1. Trên D-07 (`results/ext_auto3fix_e1/e1.md`): damage log của missing-0.2 trùng **0/60** đơn vị giữa hai lưới, reversed-0.2 trùng 15/60; IS của `plugin` và `tolerant_v4` trùng 60/60 ở cell none và **0/60** ở missing-0.2, reversed-0.2. Hệ quả:
   - Row clean của config 2 **không** phải bản sao của config 1. Đó là một realisation khác của cùng cell, không được dùng cho rule và không được gộp với config 1.
   - L1 (latent1) và C1 không ghép cặp trên cùng skeleton, nên không được diễn giải chênh lệch latent1 − clean giữa hai config như một hiệu ứng ghép cặp. Muốn so latent1 với clean thì dùng row clean của chính config 2 (cùng skeleton, cùng c_idx).
   - Row v4 của config 2 ở cell damaged không trùng row v4 của P1. Bảng v4 của paper lấy từ P1 (synthesis 3.3).
3. **Không có D-07 run nào cho đúng realisation P4-H2 của auto3.** Row auto3 của `ext_gate_auto3` (dry run config 1) dùng seed ext kiểu vòng 1 (theo vị trí trong danh sách ext), còn P4-H2 dùng `ext_seed` theo tên. Ngay cả ở cùng cell, IS của auto3 khác nhau giữa hai run (0/60 trùng, e1.md). Đây thêm một lý do để coi con số mong manh ở mục 3 là lạc quan.
4. **Đổi danh sách cell hay danh sách method của config sẽ đổi realisation.** Đổi danh sách method thì không đổi, vì tag của built-in cố định và tag của ext theo tên. Đổi danh sách cell thì có. Vì vậy hai config P2 phải chạy **nguyên văn**. Preflight P4 kiểm tra điều này, và I1 kiểm tra lại sau run.
5. **E4 và E5 (liên quan).** Runner import mọi `src/paper4/ext_*.py`, và một method ext cùng tên sẽ ghi đè built-in hoặc ghi đè method ext nạp trước. Preflight P1/P2 chặn chuyện này ngay trước run. Kiểm tra I3/I4 xác nhận lại sau run qua dấu vết `info_c_T`/`info_state`. File frozen chỉ có key `mod|*` nên E5 chỉ chạm v4, đúng như ý định.

## 5. Kết quả D3: auto3 so với `tolerant_v5_1` trên row a2-grid đã lưu (mô tả, không rule; append sau khi chạy, nguyên văn)

`experiments/ext/auto3fix/pair_v51.py`, 06:08:13Z; `results/ext_auto3fix_v51pair/pairs.{md,json}`. Kiểm tra ghép cặp đạt: row v4 trùng **1260/1260** giữa `ext_gate_auto3` và `ext_v51_eval`, tức cùng data, cùng skeleton. auto3 và v5_1 đều ok ở 60/60 run mỗi cell.

| Nhóm cell | auto3 tốt hơn / hòa / tệ hơn (CI 95%) | Holm(21) tốt hơn / tệ hơn |
|---|---|---|
| cả 21 cell | 0 / 4 / 17 | 0 / 13 |
| T40 (7) | 0 / 2 / 5 | 0 / 3 |
| T80, T150 (14) | 0 / 2 / 12 | 0 / 10 |
| missing/reversed tại T80, T150 (8) | 0 / 0 / 8 | 0 / 7 |

Số chính (IS(auto3) − IS(v5_1), 95% CI cluster theo topology):
- T40 missing: +3.73 [+2.91, +4.56] và +3.88 [+2.96, +5.00]. IS 8.56/8.97 so với 4.84/5.09.
- T80: missing +0.64 [+0.39, +1.05] / +0.30 [+0.17, +0.44]; reversed +0.08 [+0.00, +0.17] (p 0.050, không qua Holm) / +0.40 [+0.26, +0.56].
- T150: mọi cell damaged +0.22 đến +0.58, đều qua Holm. Cell none +0.30 [+0.21, +0.40], với coverage 0.985 so với 0.963.
- Coverage ở T80 reversed-0.5: auto3 0.903, v5_1 0.918.
- Bốn cell hòa: T40 extra-0.2/0.5, T80 extra-0.2/0.5.

**Đọc kết quả.** Đây không phải so sánh cùng chế độ: v5_1 được biết mức hỏng khai báo đúng, còn auto3 thì không. Số này định lượng cái giá của việc không đọc khai báo so với ứng viên của chế độ khai báo. Ở T ≥ 80 cái giá là 0.08–0.64 IS, có ý nghĩa sau Holm ở 10/14 cell. Ở T40 thiếu cạnh cái giá khoảng 3.7–3.9. auto3 không tốt hơn v5_1 ở cell nào. Câu C-auto của paper không được viết theo kiểu "auto3 gần bằng module khai báo" nếu module khai báo là v5_1. Câu đó chỉ gần đúng so với v4 (C2: 1.07–1.20 ở cell none).

## 6. Frozen spec P4-H2 đã sửa (P2, chế độ không khai báo; thay spec ở auto5.md)

**CHƯA chạy. Tác giả sẽ không chạy.** Mọi file liệt kê trong `experiments/ext/auto3fix/p4h2_spec_files.json`; lead hash tất cả ngay trước run.

- **Method:** `tolerant_auto3` (`src/paper4/ext_gate.py`, sha256 `42cf7285…f6b85a`, giữ nguyên từ vòng 1), bảng width `experiments/ext/gate/width_table.json` (`392caa46…608603`). Tham chiếu: `plugin`, `tolerant_v4` (frozen `experiments/calibration/tolerant_v4_frozen.json`, `9b630cab…19b122`), và `oracle` trong config 2. Ba hash này không đổi so với `results/ext_auto5_p4h2_dryrun/frozen_sha256.txt`.
- **Config mới** (nội dung giống từng key, cùng thứ tự key với config vòng 2; chỉ đổi `name` và `purpose`, để output nằm ở `results/ext_auto3fix_*` và purpose trỏ tới analyzer mới):
  - Config 1: `experiments/configs/ext_auto3fix_p4h2_auto3.json`. P4-H2/confirmatory, T 40/80/150, cell none + {extra, missing, reversed} × {0.2, 0.5} + GES, 3 replicate, n_boot 199, seed_base 20261102, calibration block D-07H development (chỉ dùng để lấy mức hỏng GES khai báo của v4; factor `mod|*` bị file frozen ghi đè).
  - Config 2: `experiments/configs/ext_auto3fix_p4h2_auto3_latent1.json`. T 80/150, cell none + {missing, reversed} × 0.2, scenario clean + latent1, method oracle, plugin, tolerant_v4, tolerant_auto3.
- **Analyzer:** `experiments/ext/auto3fix/check_p4h2_v2.py` (tự chứa, không import `stats5.py` hay `common.py`). **Preflight:** `experiments/ext/auto3fix/preflight_p4h2.py`.
- **Phụ thuộc ngoài repo:** GES của ACIIDS cho cell GES (6 file trong manifest). Các file `src/paper4/ext_*.py` khác cũng được runner import. Mọi `ext_*.py` có mặt lúc chạy (kể cả file mới của vòng 3) phải được hash; preflight liệt kê chúng và chặn trùng tên.
- **Interpreter:** `python` = `/Users/kietnt/miniconda3/bin/python` (Python 3.13.9, numpy 2.5.4), như mọi lần chạy của hướng này. Preflight in ra cả hai, vì manifest của runner không ghi (E6).
- **Lệnh (chạy đúng một lần mỗi lệnh, theo thứ tự; không xem output trước khi chạy xong cả 4):**
  1. `python experiments/ext/auto3fix/preflight_p4h2.py --hashes <file hash của lead> --out results/ext_auto3fix_p4h2_check_preflight.json`. Phải in `PREFLIGHT OK`; nếu không thì **dừng**, không chạy P2.
  2. `python experiments/run_experiment.py --config experiments/configs/ext_auto3fix_p4h2_auto3.json --workers 3`
  3. `python experiments/run_experiment.py --config experiments/configs/ext_auto3fix_p4h2_auto3_latent1.json --workers 3`
  4. `python experiments/ext/auto3fix/check_p4h2_v2.py` → `results/ext_auto3fix_p4h2_check/{check.md, check.json}`
- **Thời gian ước tính với `--workers 3`:**
  - Config 1 khoảng 13–18 phút. Tham chiếu D-07: `ext_gate_auto3`, cùng lưới cộng thêm method `tolerant_auto3_nogate`, mất 1027.6 s khi máy tải khoảng 42 trên 12 core.
  - Config 2 khoảng 7–11 phút. `ext_auto5_a1` với 4 scenario mất 1050.8 s; config 2 chỉ có 2 scenario, cộng pha calibration D-07H.
  - Analyzer dưới 10 s. **Tổng khoảng 20–30 phút.**
- **Rule xác nhận:** nguyên văn mục 1.1 (trích trong manifest, key `confirmatory_rule`). CONFIRMED khi và chỉ khi C1, C2, C3, L1 đều đạt và I1–I5 đạt, với run thất bại tính là không cover và trần 3/60 run thất bại mỗi cell của rule.
- **Bắt buộc khi báo kết quả:** câu mong manh ở mục 3 (P(CONFIRMED) ≈ 0.62 trên bootstrap D-07, cell T80 reversed-0.5), cùng `n_ok/n_exp` theo cell.
- **Multiplicity:** P2 là point rule nên không cần hiệu chỉnh (synthesis 3.3). Holm trên 14 cell coverage chỉ báo kèm.
- **Nếu NOT CONFIRMED:** C-auto chỉ còn exploratory trên D-07 development.
- **File bị thay thế (giữ nguyên, không dùng cho P4-H2):** `experiments/ext/auto5/check_p4h2.py`, `experiments/configs/ext_auto5_p4h2_auto3.json`, `experiments/configs/ext_auto5_p4h2_auto3_latent1.json`. Hai config cũ không được chạy; nếu chạy, chúng sẽ cho đúng cùng realisation (nội dung giống nhau, E1 không đổi), nhưng output sẽ nằm sai thư mục và analyzer cũ bỏ qua run thất bại.

## 7. Tóm tắt của hướng auto3fix

| Việc | Kết quả | Nguồn |
|---|---|---|
| Xử lý run thất bại | Tính là không cover; trần 3/60 mỗi cell của rule; cell 0 run ok thì trượt, không crash; IS ratio ghép cặp | check_p4h2_v2.py; fault_injection/ |
| Báo số run ok | `n_ok/n_exp` mọi method × cell; D-07: auto3 60/60 ở mọi cell | results/ext_auto3fix_dryrun/check.md |
| Câu mong manh | 0.903 [0.880, 0.925]; Holm 13/14; P(CONFIRMED) ≈ 0.616 (lạc quan) | results/ext_auto3fix_fragility/ |
| Toàn vẹn | I1–I5 sau run; preflight P1–P6 trước run (chặn E4, ghim bảng, config, GES, hash) | preflight_p4h2.py |
| Manifest spec | 40 file + bank P4-H2 (lead hash) | experiments/ext/auto3fix/p4h2_spec_files.json |
| auto3 so với v5_1 (mô tả) | tệ hơn 17/21 cell (Holm 13/21), hòa 4, tốt hơn 0; T ≥ 80 missing/reversed tệ hơn 8/8 (Holm 7/8) | results/ext_auto3fix_v51pair/ |
| E1 | Config 1 chung realisation v4 với P1; config 2 là realisation khác ở mọi cell damaged | results/ext_auto3fix_e1/ |

Không có run mới nào. Không sửa file có sẵn nào, ngoài việc append mục "Sửa sau kiểm chứng vòng 2" vào docs/ext/auto5.md.

*Hash lúc viết (để đối chiếu, không thay hash của lead):* `results/ext_auto3fix_dryrun/spec_sha256_at_writing.txt` (40 file trong manifest), gồm `check_p4h2_v2.py` `6cdb6e36…`, `preflight_p4h2.py` `00215df1…`, config 1 `c8fec345…`, config 2 `bf8ff704…`, manifest `2f2c8224…`.
