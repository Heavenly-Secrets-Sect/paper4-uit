# Vòng 2, R2-3: độ bền của `tolerant_auto3`, so sánh công bằng, và `tolerant_auto5` (ID `auto5`)

**Trạng thái.** Exploratory, D-07 development (seed_base 20261102). Calibration và mọi probe thiết kế chỉ trên D-07H development. Không đụng P4-H1, P4-H2 hay bất kỳ split confirmatory nào. Hướng này nối tiếp hướng `gate` của vòng 1 ([gate.md](gate.md)); phần sửa lời của vòng 1 được append vào cuối gate.md.

Mỗi phần dưới đây có quy tắc ghi **trước** khi chạy config đánh giá tương ứng; kết quả được append sau, nguyên văn, kể cả thất bại. Thời điểm (UTC) ghi ở đầu mỗi quy tắc.

Không có lần chạy nào trên D-07 trước khi quy tắc tương ứng được ghi (không có timing run, không có smoke run trên D-07). Mọi smoke/timing đều chạy trên D-07H development.

## 0. Vệ sinh từ vòng 1

**Probe script của gate.md mục 3.1–3.3 đã tìm lại được** trong scratchpad của phiên vòng 1 và được chép nguyên trạng (giữ mtime) vào `experiments/ext/gate_probes/`:
- `gate_core.py` (prototype fit đủ lag, Šidák/Fisher/min-p), `probe.py` + `an1.py`, `an2.py` (mục 3.1, 3.2: tỷ lệ cổng mở, targeted/all), `gate2.py` + `probe2.py` + `an3.py`, `an4.py` (fit hạn chế, bootstrap shock độc lập, mục 3.1), `ext_gate_candidate.py` + `loadcand.py` + `probe3.py` + `an5.py` (mục 3.3: α và xác suất lật);
- output: `probe.pkl`, `probe2.pkl`, `probe_merged.pkl`, `probe3.pkl`.
- Các script dùng đường dẫn tuyệt đối tới scratchpad cũ (`SP=...`); muốn chạy lại thì sửa `SP` thành `experiments/ext/gate_probes`. Chúng đọc `experiments/configs/b1v2_auto.json` và chỉ dùng D-07H development (`seed_base + 500000`). Seed bootstrap của chúng không phụ thuộc runner nên không bị ảnh hưởng bởi sửa lỗi B1.

**Bug mới phát hiện trong file vòng 1 (chưa sửa, chỉ báo).** `src/paper4/ext_narrow.py`, `opened_terms`: khi một cạnh cùng kỳ được repair rơi vào một cặp đã được mở lag, cặp đó trở thành adjacent nên `parent_terms` đã chứa lag block của nó, và `opened_terms` thêm lag block đó **lần nữa**. Cột trùng làm `lstsq` chia đôi hệ số (min-norm), và `fit_equations` chỉ giữ một bản sao, tức **hệ số lag bị giảm một nửa**. Kiểm tra trên SVAR 4 nút, T = 2000: hệ số thật 0.6, fit ra 0.294. Ở T = 40, cột trùng còn có thể làm phương trình underdetermined (một run D-07H T40 missing-0.5 thất bại vì vậy trong smoke của tôi). Ảnh hưởng: mọi row `tolerant_v5`/`tolerant_v5_sel` vòng 1 có repair trên cặp đã mở. `tolerant_auto5` dùng bản khử trùng (`ext_auto5.targeted_terms`). Đã báo cho team lead.

## 1. R2-3a: `tolerant_auto3` dưới biến ẩn và nhiễu đo

*Quy tắc ghi lúc 2026-11-01T19:55Z, trước khi chạy `ext_auto5_a1`.*

**Config.** `experiments/configs/ext_auto5_a1.json`. D-07 development, seed và lưới của `a1_latent_noise` (nên ghép cặp được với các row đó; kiểm tra bằng row `plugin` trùng khớp):
- kịch bản `clean`, `latent1`, `latent3`, `noise0.1` (bỏ `noise0.3` để giữ thời gian chạy; noise0.3 vốn là giới hạn đã biết của mọi method);
- T ∈ {80, 150}; cell none, missing-0.2, reversed-0.2 (lưới a1 chỉ có rate 0.2);
- method: `oracle`, `plugin`, `tolerant_v4` (frozen calibration `experiments/calibration/tolerant_v4_frozen.json`), `tolerant_auto3` (code và width table vòng 1, không đổi; seed bootstrap nay theo tên method);
- 20 topology × 3 replicate, n_boot 199. Khối calibration chép từ `a3_ges` (D-07H development); với v4 nó bị frozen calibration ghi đè.

**Quy tắc (chốt trước, theo synthesis R2-3).** `tolerant_auto3` được coi là **bền với biến ẩn (latent1)** nếu coverage gộp (cột `cov`) ≥ 0.90 ở **cả 4** cell missing-0.2 và reversed-0.2 tại T = 80 và T = 150 dưới `latent1`. Nếu không, latent1 được ghi là giới hạn của auto3.

**Báo cáo kèm, không chấm:**
- latent3 và noise0.1 đọc theo cách của A1: claim độ bền chỉ được phép ở cell có coverage ≥ 0.90; cell none cũng được báo.
- Tỷ lệ cổng mở theo kịch bản và cell (dự đoán trước: biến ẩn làm structural residual tương quan nên mở cổng ở cell none; khi đó auto3 rơi về nhánh mở, tốn IS nhưng giữ coverage).
- IS của auto3 so với v4 và `plugin` (chênh lệch ghép cặp, CI clustered theo topology), và so với `oracle`.
- **Multiplicity:** với mỗi cell, p-value một phía cho H0 "coverage ≤ 0.90" bằng cluster bootstrap theo topology (2000 lần, p = tỷ lệ bootstrap coverage ≤ 0.90). Báo số cell đạt theo điểm (quy tắc) và số cell bác H0 sau Holm ở mức 0.05 trên 4 cell của quy tắc.

## 2. R2-3b: so sánh công bằng với baseline được calibrate theo T

*Quy tắc ghi lúc 2026-11-01T19:55Z, trước khi chạy `fair_baselines.py` trên D-07.*

**Vì sao.** Verifier vòng 1: auto3 được calibrate trên D-07H còn baseline thì không, nên "thắng baseline" chưa công bằng. Baseline không được đọc stated kind (auto3 không đọc), nên hệ số width chỉ theo T, gộp mọi cell calibration, **kể cả cell none**.

**Cách làm.** Script `experiments/ext/auto5/fair_baselines.py`, config `experiments/configs/ext_auto5_fair.json`. Không qua runner vì key `calibrate_methods` của runner là stated kind.
- Baseline: `plugin`, `ida_union`, `bvar_minnesota`, `pselect_union` (built-in, không sửa). Mỗi baseline được fit với **đúng** dòng seed của runner (`rng([unit, 3, T, c_idx, tag])`, tag 1/7/8/9) nên interval thô trùng từng row của `a2_baselines`/`a2b_pselect`. Script kiểm tra điều này (IS thô trùng khớp) trước khi dùng.
- Calibration: đơn vị calibration của runner trên D-07H development (20 topology × 1 replicate, T ∈ {40, 80, 150}, 7 cell: none, extra/missing/reversed × 0.2/0.5). Hệ số cho mỗi (baseline, T) chọn như runner: c nhỏ nhất trên lưới sao cho coverage gộp ≥ min(0.95, max coverage − 0.005). Hai lưới:
  - `_calT` (**chính**): lưới hai phía 0.5..5.0 bước 0.05, tức baseline cũng được làm hẹp nếu over-cover. Đây là bản mạnh nhất của baseline, nên bất lợi cho auto3 (auto3 dùng lưới một phía 1.0..10);
  - `_calT1` (phụ): lưới một phía 1.0..10.0 bước 0.1, giống auto3.
- Đánh giá: D-07 development, 20 × 3, T ∈ {40, 80, 150}, 7 cell. Interval nới/thu quanh điểm giữa; IS và coverage tính đúng như `metrics.evaluate`.
- auto3: row của `results/ext_gate_auto3` (cùng data và skeleton; seed bootstrap vòng 1). Ghép cặp theo (topology, replicate, T, kind, rate).

**Quy tắc (mô tả, chốt trước).** Với mỗi baseline X ∈ {plugin, ida_union, bvar_minnesota, pselect_union} ở bản `_calT`, trong mỗi cell (21 cell = 3 T × 7 cell):
- auto3 **thắng** X nếu coverage auto3 ≥ 0.90 và cận trên 95% CI (clustered theo topology, 2000 lần) của IS(auto3) − IS(X) < 0;
- **thua** nếu cận dưới > 0; còn lại **hòa**.
- Claim "auto3 thắng baseline đã calibrate công bằng ở cell thiếu/đảo cạnh, T ≥ 80" được phép nếu auto3 thắng **mỗi** X ở **cả 8** cell missing/reversed × 0.2/0.5 tại T = 80 và 150. Nếu không, claim thu hẹp về đúng các cell thắng.
- Báo riêng cell none (skeleton đúng) ở mọi T: auto3 so với `ida_union_calT` và `plugin_calT`, theo yêu cầu R2-3b.
- **Multiplicity:** p-value hai phía của mỗi chênh lệch từ cluster bootstrap (2 × min(tỷ lệ ≤ 0, tỷ lệ ≥ 0)); số cell thắng/thua sau Holm ở mức 0.05 trên 21 cell của mỗi baseline, và trên 8 cell của claim.
- Bản `_calT1` và baseline thô (chưa calibrate) chỉ báo cáo.

## Ghi chú tiếp tục sau khi bị ngắt (phiên tiếp theo, 2026-11-02T02:25Z)

Lần thử đầu tiên của vòng 2 bị ngắt vì giới hạn sử dụng lúc khoảng 02:53 giờ địa phương (19:53Z ngày 2026-11-01). Trạng thái lúc ngắt, kiểm tra bằng mtime file:
- Mục 1 và mục 2 ở trên (quy tắc) được lưu lần cuối lúc 2026-11-01T19:50:46Z (mtime của file này). **Dấu thời gian "19:55Z" ghi trong hai quy tắc là sai** (được ghi ước lượng); thời điểm thật là ≤ 19:50:46Z. Lần chạy `ext_auto5_a1` khởi động lúc 19:50:58Z (`experiments/ext/auto5/a1_run.log`), tức 12 giây **sau** khi quy tắc mục 1 được lưu. Thứ tự quy tắc → chạy vẫn đúng.
- `ext_auto5_a1`: pha calibration (D-07H) đã xong (`results/ext_auto5_a1/calibration.json`, 19:52:50Z), pha đánh giá trên D-07 bị ngắt giữa chừng, **không có** `runs.jsonl`/`summary.md`, tức không có kết quả nào được xem. Chạy lại **nguyên config, nguyên quy tắc**, không đổi gì.
- `fair_baselines.py` (mục 2): script được sửa lần cuối lúc 19:51:56Z, sau khi quy tắc mục 2 được lưu (chỉ sửa code, quy tắc không đổi); **chưa từng chạy** (không có `results/ext_auto5_fair`). Config `ext_auto5_fair.json` sửa lần cuối 19:51:47Z.
- Probe thiết kế của auto5 (`probe_auto5.py`, D-07H development) đã khởi động lúc 19:49Z nhưng bị ngắt, không có output (`probe.log` rỗng, không có `probe.pkl`). Chạy lại nguyên trạng. Quy tắc của auto5 (mục 3) **chưa được ghi**; sẽ ghi sau probe và trước khi chạy `ext_auto5_eval`.
- Không có lần chạy nào trên D-07 khác ngoài lần `ext_auto5_a1` bị ngắt nói trên.

## 3. R2-3c: `tolerant_auto5` (B1 bản 5)

### 3.1 Thiết kế

Code: [src/paper4/ext_auto5.py](../../src/paper4/ext_auto5.py) (module mới; không sửa `ext_gate.py` hay `ext_narrow.py`). Method chỉ đọc data và skeleton (pairs, orientation); `skel.damage` bị bỏ ở dòng đầu như auto3.

- **Giữ nguyên của auto3** (import từ `ext_gate`): test cặp trong fit cấu trúc hạn chế, cổng Šidák toàn cục α = 0.10, nhánh đóng (term của skeleton), repair cùng kỳ BH với ngân sách K = max(#BH, Storey, 1), dự phòng đảo chiều (lật mỗi cạnh cùng kỳ |t| > 1.645 với xác suất 0.2 trong mỗi draw).
- **Thay đổi 1, targeted opening có re-selection khi cổng mở** (import `select_open` của v5 nguyên trạng; `opened_terms` được bọc trong `targeted_terms` để **khử term trùng** bằng `list(dict.fromkeys(...))`, tránh bug của ext_narrow ở mục 0). Mở lag block của K' cặp có p screening nhỏ nhất, K' = max(⌈3·k_open⌉, #{p < 0.10}) (hằng số của v5), với **k_open = max(#BH của cổng, 1)** đóng vai số cạnh thiếu khai báo của v5. Selection và repair chạy lại trong **mỗi** bootstrap draw.
  - `tolerant_auto5`: targeted **mỗi khi cổng mở**, ở mọi T (`TAU_ROWS = inf`).
  - `tolerant_auto5_small` (ablation, chỉ báo cáo): targeted chỉ khi rows/(1 + n·lag_max) < 2, tức chỉ T = 40 ở đây; T ≥ 80 dùng nhánh all-lag của auto3. Đây là thiết kế đúng chữ của R2-3c ("targeted ở T nhỏ").
- **Thay đổi 2, two-sided width calibration**: hệ số theo (T, nhánh tự chẩn đoán ∈ closed/open_tgt/open_all) chọn trên lưới 0.5..5.0 bước 0.05, mục tiêu min(0.95, max coverage − 0.005) như runner. Không đi qua `calibrate_methods` (key của runner là stated kind), giống auto3.
- Bảng width ([experiments/ext/auto5/width_table.json](../../experiments/ext/auto5/width_table.json), tạo bởi `make_width_table.py`): closed 1.5 / 1.25 / 1.2; open_tgt 1.2 / 1.2 / 1.2 (T = 40/80/150); open_all (chỉ ablation) 1.2 ở T80, 1.25 ở T150.

### 3.2 Probe thiết kế (D-07H development, in-sample)

Đơn vị calibration của runner: 20 topology × 1 replicate × T ∈ {40, 80, 150} × 7 cell, n_boot 199. Hệ số width tune trên chính các run đó nên số **lạc quan**. Không chạy gì trên D-07 cho phần này.
- Probe 1 (`probe_auto5.py`, 413 s, `results/ext_auto5_probe/probe_summary.md`): luật mở {all, tgt40, tgt80, tgtall} × flip pool {sig, mec} × lưới {one, two}, ngân sách mở = ngân sách repair max(#BH, Storey, 1).
- Probe ngân sách (`probe_budget.py`, `results/ext_auto5_probe/budget.md`, đọc truth chỉ để lập bảng): Storey đếm thừa nặng (T40 missing-0.5: 20.4 so với 11 cạnh thiếu thật; skeleton đúng: 2.6–4.2), nên K' gần như mở toàn bộ 81 cặp (55.8 cặp trung bình). #BH đếm thiếu ở T40 (6.3) nhưng K' = max(3·#BH, #p<0.10) ≈ 22.7.
- Probe 2 (`probe2_auto5.py`, 148 s, `results/ext_auto5_probe/probe2_summary.md`): thêm ngân sách mở k_open = max(#BH, 1) ("sig_bh").

Số in-sample chính (cov / IS, lưới two; nguồn `results/ext_auto5_probe/probe2_summary.md`):

| T | cell | all/sig (≈ auto3) | tgt40/sig_bh (= auto5_small) | **tgtall/sig_bh (= auto5)** |
|---|---|---|---|---|
| 40 | none | 0.968 / 4.42 | 0.971 / 4.32 | 0.971 / 4.32 |
| 40 | missing 0.2 | 0.906 / 7.51 | 0.911 / 5.95 | 0.911 / 5.95 |
| 40 | missing 0.5 | 0.944 / 7.10 | 0.928 / 5.41 | 0.928 / 5.41 |
| 80 | missing 0.2 | 0.950 / 3.32 | 0.950 / 3.32 | 0.944 / 2.87 |
| 80 | missing 0.5 | 0.956 / 3.28 | 0.956 / 3.28 | 0.964 / 2.95 |
| 80 | reversed 0.5 | 0.930 / 2.76 | 0.930 / 2.76 | 0.923 / 2.70 |
| 150 | none | 0.964 / 1.78 | 0.964 / 1.78 | 0.964 / 1.78 |
| 150 | missing 0.5 | 0.956 / 2.22 | 0.956 / 2.22 | 0.971 / 2.12 |
| 150 | reversed 0.5 | 0.915 / 2.27 | 0.915 / 2.27 | 0.913 / 2.11 |

Mean IS trên 21 cell (lưới two): all/sig 3.385, tgt40/sig 3.309, tgt40/sig_bh 3.215, tgt80/sig_bh 3.170, **tgtall/sig_bh 3.140** (thấp nhất). Coverage nhỏ nhất ở cell missing/reversed T ≥ 80: 0.913–0.918 cho mọi biến thể (đều ở reversed 0.5, T150).

**Lựa chọn và lý do (ghi rõ là chọn sau khi xem probe D-07H):** biến thể có mean IS in-sample thấp nhất trong các biến thể giữ coverage ≥ 0.90 ở mọi cell missing/reversed: targeted khi cổng mở ở mọi T, ngân sách mở #BH, flip pool sig (mec làm tệ cell reversed 0.5: T150 2.59 so với 2.27), lưới two. Điều này **trái** với giả thuyết của synthesis X4 ("targeted ở T nhỏ, all-lag ở T lớn"). Một giải thích khả dĩ, chưa kiểm chứng: bằng chứng ở narrow rằng targeted thua ở T150 missing-0.5 đến từ bản có bug term trùng (hệ số lag bị chia đôi). Vì vậy bản đúng chữ của R2-3c được giữ làm ablation `tolerant_auto5_small`.

Ghi chú về over-coverage 0.985 ở T150: trên probe D-07H, hệ số closed|150 tối ưu là 1.2 ở cả hai lưới (bảng width của auto3 có 1.3, do seed bootstrap khác của calibrate_gate). Lưới hai phía không xuống dưới 1.0 ở đâu trừ open_all|40 (0.75, không dùng). Tức là over-coverage của auto3 ở T150 chủ yếu là nhiễu chọn hệ số (1.3 so với 1.2) cộng chênh lệch D-07/D-07H, không phải do sàn 1.0.

### 3.3 Quy tắc ghi trước (viết trước khi chạy `ext_auto5_main`)

**Config.** `experiments/configs/ext_auto5_main.json`. D-07 development, seed của `a2_baselines`/`b1v2_auto`/`ext_gate_auto3` (seed_base 20261102), 20 topology × 3 replicate, n_boot 199, T ∈ {40, 80, 150}, cell none, {extra, missing, reversed} × {0.2, 0.5}, và cell GES. Method: `plugin`, `pselect_union` (built-in, tính lại trong run; phải trùng từng row với `a2b_pselect`), `tolerant_v4` (frozen calibration `experiments/calibration/tolerant_v4_frozen.json`; mức hỏng GES khai báo lấy từ khối calibration của a3_ges trên D-07H), `tolerant_auto5`, `tolerant_auto5_small` (ablation). (`experiments/configs/ext_auto5_eval.json` là bản nháp của lần thử bị ngắt, **không bao giờ chạy**, được thay bằng config này.)

**Quy tắc.** `tolerant_auto5` được **giữ lại** nếu cả bốn điều kiện đều đúng. C1–C3 là ba điều kiện B1 của decision_rules.md, giữ nguyên, cùng cách đọc chặt như auto3 (gate.md mục 4):
1. **C1:** coverage gộp (cột `cov`) ≥ 0.90 ở mọi cell missing và reversed (× 0.2, 0.5) tại T = 80 và 150 (8 cell).
2. **C2:** ở cell none, IS ≤ 1.35 × IS của `tolerant_v4`, tại **cả ba** T = 40, 80, 150.
3. **C3:** ở cell GES tại T = 80 và 150: coverage ≥ 0.90 và IS ≤ 1.10 × IS của `tolerant_v4`.
4. **C4 (mới, theo R2-3):** ở T = 40, cell missing-0.2 và missing-0.5, IS của auto5 **không tệ hơn** `pselect_union`: cận dưới của 95% CI của chênh lệch ghép cặp IS(auto5) − IS(pselect_union) (bootstrap theo topology, 2000 lần, `stats5.paired`) ≤ 0 ở **cả hai** cell. (auto3 và v4 đều trượt điều kiện này ở vòng 1: auto3 +1.60 [+0.79, +2.45] và +2.34 [+1.41, +3.41].)

**Báo cáo kèm, không chấm:** điểm ước lượng của C4 (và biến thể chặt "điểm ước lượng ≤ 0"); coverage ở T150 none (so với 0.985 của auto3); tỷ lệ cổng mở và số cặp mở; chênh lệch ghép cặp với `tolerant_v4`, `plugin`, `pselect_union` ở mọi cell; so với auto3 (row của `results/ext_gate_auto3`, cùng data và skeleton, khác seed bootstrap); ablation `tolerant_auto5_small` chấm theo cùng C1–C4 nhưng **chỉ để báo cáo**. Coverage ở T = 40 ngoài C2/C4 chỉ báo cáo.

**Multiplicity:** C1 và C3-coverage: p một phía cho H0 "coverage ≤ 0.90" (cluster bootstrap theo topology), số cell bác H0 sau Holm (α 0.05) trên 10 cell coverage của C1+C3. C2/C3-IS: tỷ lệ điểm. C4: p một phía cho H0' "auto5 không tệ hơn" bị bác (tức auto5 tệ hơn có ý nghĩa) = tỷ lệ bootstrap của chênh lệch ≤ 0; báo Holm trên 2 cell.

**Rủi ro ghi trước:** (i) coverage reversed-0.5 ở T80/T150 chỉ 0.913–0.923 in-sample; auto3 đã mất ~0.04 từ probe sang D-07 ở T80 reversed-0.5 (0.940 → 0.903), nên C1 có thể trượt; (ii) hệ số closed|80 giảm 1.3 → 1.25 và closed|150 1.3 → 1.2 so với auto3; (iii) T40 missing-0.2 cổng chỉ mở ~62–75% số run, phần cổng đóng vẫn bị lệch.

## 4. Kết quả R2-3a: `ext_auto5_a1` (append sau khi chạy, nguyên văn)

Lần chạy lại (sau lần bị ngắt, config và quy tắc không đổi) khởi động 2026-11-02T02:22:53Z, xong 02:40:29Z: 5760 row trong 1050.8 s với `--workers 3` (khoảng 17.5 phút; máy đang tải khoảng 30 trên 12 core vì các agent khác). Lưới đúng như quy tắc mục 1 (đã thu nhỏ trước: bỏ noise0.3, chỉ T80/T150, rate 0.2). Chấm bằng `python experiments/ext/auto5/check_a1.py`; mọi số dưới đây nằm trong `results/ext_auto5_a1/rule_check.md` và `rule_check.json`.

**Ghép cặp:** row `plugin` và `oracle` trùng từng row với `a1_latent_noise` (1440/1440 mỗi method). Row `tolerant_v4` trùng 968/1440: đúng như dự kiến, vì a1 dùng hệ số v4 tune lại còn ở đây dùng frozen calibration.

**Quy tắc (latent1, coverage auto3 ≥ 0.90 ở missing-0.2 và reversed-0.2 tại T80 và T150): ĐẠT, 4/4 cell.**

| T | latent1 missing-0.2 | latent1 reversed-0.2 |
|---|---|---|
| 80 | 0.956 | 0.937 |
| 150 | 0.977 | 0.970 |

Multiplicity: p một phía cho H0 "coverage ≤ 0.90" (cluster bootstrap 2000 lần theo topology) < 0.0005 ở cả 4 cell (không bootstrap nào ≤ 0.90); sau Holm ở α 0.05: 4/4 cell bác H0.

**Kết luận: `tolerant_auto3` BỀN với một biến ẩn (latent1)** theo quy tắc đã ghi trước.

**Báo cáo kèm (không chấm):**
- Đọc kiểu A1 (coverage ≥ 0.90 theo cell, 6 cell = T80/T150 × none/missing/reversed): clean 6/6 (v4 6/6); latent1 6/6 (v4 6/6); latent3 6/6 (v4 5/6, v4 trượt ở T150 none 0.871); noise0.1 5/6 (v4 5/6). Ô trượt của auto3: noise0.1 T80 reversed-0.2, 0.883 (v4 0.904). Ở noise0.1 T80 missing-0.2 auto3 0.920.
- **Dự đoán trước "biến ẩn mở cổng ở cell none" đúng:** tỷ lệ cổng mở ở cell none tăng từ 0.08 / 0.05 (clean, T80/T150) lên 0.25 / 0.47 (latent1) và 0.55 / 0.82 (latent3). Nhiễu đo 10% gần như không mở cổng (0.10 / 0.15). Khi cổng mở, auto3 rơi về nhánh all-lag và giữ coverage (latent3 T150 none: auto3 0.951 so với v4 0.871).
- IS ghép cặp auto3 − v4 (v4 được biết mức hỏng thật): clean +0.04 đến +0.30; latent1 +0.11 đến +0.33; latent3 −0.09 đến +0.71 (lớn nhất ở T80 none, nơi cổng mở 55% số run); noise0.1 +0.03 đến +0.55. Ở latent3 T150, auto3 hòa hoặc tốt hơn v4 (−0.09 [−0.35, +0.19] ở none, −0.03 ở missing) và còn hòa `oracle` (oracle ở đây không biết biến ẩn và chỉ đạt coverage 0.779).
- auto3 − plugin: thắng lớn ở mọi cell missing/reversed (−0.61 đến −9.17). Ở cell none: hòa ở clean T80 (−0.14 [−0.38, +0.06]) và latent1; **thua** ở clean T150 (+0.29 [+0.17, +0.41]) và latent3 T80 (+0.32 [+0.09, +0.54]); thắng ở latent3 T150 (−0.58) và noise0.1 T80 (−0.57).
- Clean T150 none: coverage auto3 0.983 (seed bootstrap mới), tái hiện over-coverage 0.985 của vòng 1.

## 5. Kết quả R2-3c: `ext_auto5_main` (append sau khi chạy, nguyên văn)

Quy tắc mục 3.3 được ghi xong lúc khoảng 2026-11-02T02:36:39Z; lần chạy khởi động 02:40:46Z, xong 03:04:12Z: 7200 row trong 1405.6 s với `--workers 3` (**23.4 phút, vượt mức ~20 phút** của hard rule 5; lưới không thu nhỏ; máy tải khoảng 20–30 trên 12 core). Chạy một lần. Chấm bằng `python experiments/ext/auto5/check_main.py`; mọi số dưới đây nằm trong `results/ext_auto5_main/rule_check.md` / `rule_check.json` (và `summary.md` của runner).

**Ghép cặp:** `plugin` trùng `a2_baselines` 1260/1260 và trùng `ext_gate_auto3` 1440/1440 (cả cell GES); `pselect_union` trùng `a2b_pselect` 1260/1260.

**Kết luận: `tolerant_auto5` BỊ LOẠI (REJECTED)**, vì C1 trượt đúng một cell, đúng rủi ro (i) đã ghi trước.

| Điều kiện | Kết quả | Đạt? |
|---|---|---|
| C1 coverage ≥ 0.90 (8 cell) | T80: missing 0.944 / 0.944, reversed 0.929 / **0.898**; T150: missing 0.977 / 0.982, reversed 0.960 / 0.942 | **TRƯỢT** (7/8) |
| C2 IS none / v4 ≤ 1.35 | 1.045 / 1.045 / 1.146 (T40/80/150) | đạt |
| C3 GES | T80 cov 0.913, tỷ lệ 0.979; T150 cov 0.949, tỷ lệ 0.945 | đạt |
| C4 T40 missing, IS(auto5) − IS(pselect_union) | missing-0.2 −0.56 [−1.28, +0.18]; missing-0.5 −0.55 [−1.40, +0.53] | đạt (cả cách đọc chặt theo điểm: 2/2) |

Multiplicity: trong 10 cell coverage (C1 + C3), H0 "coverage ≤ 0.90" bị bác sau Holm ở 8/10; hai cell không bác được là T80 reversed-0.5 (0.898, p = 0.60) và T80 GES (0.913, p = 0.095). C4: p một phía cho "auto5 tệ hơn pselect" là 0.93 và 0.87; Holm bác "không tệ hơn" ở 0/2 cell.

Ablation `tolerant_auto5_small` (targeted chỉ ở T40, chỉ báo cáo): trượt cùng cell C1 (T80 reversed-0.5 0.894), đạt C2 (1.020/1.062/1.141), C3 (0.946/0.960; 0.951/0.964) và C4 (−0.42 [−1.08, +0.26]; −0.63 [−1.46, +0.45]); Holm 9/10.

**Báo cáo kèm (không chấm):**
- **auto5 so với auto3** (row vòng 1, cùng data): điểm ước lượng IS thấp hơn ở 23/24 cell, CI < 0 ở 13/24, không cell nào CI > 0; lớn nhất ở T40: missing −2.16 [−2.72, −1.62] và −2.89 [−3.57, −2.23], GES −2.73 [−3.73, −1.80]. Cái giá là coverage ở T40: missing 0.911 → 0.873 và 0.954 → 0.892, GES 0.918 → 0.858 (T40 không được chấm theo C1). Cell duy nhất auto5 không tốt hơn: T80 GES +0.09 [−0.13, +0.38].
- **Over-coverage ở T150 none**: 0.985 (auto3) → 0.975 (auto5), IS 1.87 → 1.79 (−0.08 [−0.12, −0.03]). Vẫn thua `plugin` ở T150 none (+0.21 [+0.12, +0.31]) và extra (+0.14 đến +0.16). Hai phía của lưới không giúp gì thêm vì hệ số tối ưu trên D-07H vẫn ≥ 1.2 (mục 3.2).
- **auto5 so với v4 (v4 được biết mức hỏng thật):** ở T40 missing, auto5 **tốt hơn** v4: −1.36 [−2.11, −0.53] và −1.45 [−2.44, −0.23] (v4 coverage 0.98, auto5 0.87–0.89). Ở T80/T150 missing: hòa (−0.23 đến +0.05, CI chứa 0). Cell none/extra/reversed: −0.09 đến +0.42; CI > 0 ở 11/24 cell (mọi cell none/extra/reversed ở T80 và T150, cộng T40 reversed-0.5).
- **So với `pselect_union`:** auto5 thắng (CI < 0) ở 21/24 cell, hòa ở T40 missing-0.2, missing-0.5 và GES (+0.47 [−0.76, +1.82]), không thua cell nào. Riêng T40 có coverage thấp: auto5 0.873/0.892 so với pselect 0.862/0.853.
- **Targeted ở T lớn (liên quan X4):** `tolerant_auto5_small` − `tolerant_auto5` (all-lag − targeted khi cổng mở) ở T150: missing-0.2 +0.24 [+0.17, +0.30], missing-0.5 +0.08 [+0.01, +0.14], reversed +0.10 / +0.15; ở T80 missing-0.2 +0.41 [+0.29, +0.54]. Tức là trên D-07, **targeted opening có re-selection (khử term trùng) tốt hơn all-lag cả ở T80 và T150**, ngược với kết luận của synthesis X4. Coverage của hai bản tương đương ở các cell này.
- Tỷ lệ cổng mở của auto5 (cùng gate với auto3): none 0.10 / 0.08 / 0.05; missing-0.2 0.62 / 0.98 / 1.00; reversed-0.5 0.13 / 0.23 / 0.55; GES 0.88 / 1.00 / 1.00. Số cặp được mở trung bình khi cổng mở: T40 missing-0.5 22.9, T150 missing-0.5 67.2 (của 81 cặp bị bỏ).

**Đọc kết quả.** Cell trượt (T80 reversed-0.5) là cell mà 77% số run có cổng đóng; coverage ở đó do nhánh đóng và dự phòng lật quyết định, không do phần targeted. Hệ số closed|80 giảm từ 1.3 (auto3, 0.903) xuống 1.25 (auto5, 0.898) là đủ để rơi dưới ngưỡng. Theo quy tắc, không nới ngưỡng và không sửa hệ số sau khi thấy kết quả. Một bản sửa (ví dụ hệ số closed một phía) sẽ là version mới, cần quy tắc mới và đã bị D-07 gợi ý, nên **không** được làm trong vòng này.

## 6. Kết quả R2-3b: so sánh công bằng (append sau khi chạy, nguyên văn)

`fair_baselines.py` chạy một lần, 2026-11-02T03:04:24Z → 03:12:49Z, 504.4 s với `--workers 3` (calibration D-07H 142.3 s), 15120 row. Interval thô của cả 4 baseline trùng từng row với `a2_baselines`/`a2b_pselect` (1260/1260 mỗi baseline, sai khác tối đa 1.4e−14, `results/ext_auto5_fair/pairing_check.json`). Chấm bằng `python experiments/ext/auto5/compare_fair.py`; mọi số dưới đây nằm trong `results/ext_auto5_fair/rule_check.md` / `rule_check.json`, hệ số trong `results/ext_auto5_fair/calibration.json`.

**Hệ số width theo T (gộp mọi cell calibration, kể cả none), bản `_calT` (lưới 0.5..5.0):** plugin 3.9 / 4.1 / 4.1; ida_union 3.45 / 3.8 / 3.7; bvar_minnesota 2.2 / 2.45 / 2.3; pselect_union 1.6 / 1.1 / 1.1 (T40/80/150). Coverage của baseline thô trên bank calibration ở c = 1: plugin 0.76–0.78, ida 0.82–0.85, bvar 0.77–0.80, pselect 0.88–0.94. Không baseline nào được hệ số < 1.

**Quy tắc (auto3 thắng mỗi X_calT ở cả 8 cell missing/reversed × 0.2/0.5 tại T80/T150): KHÔNG ĐẠT.** Claim chỉ đứng ở dạng thu hẹp:

| X (bản `_calT`) | thắng / hòa / thua (21 cell) | Holm thắng / thua (21) | cell claim thắng (8) | Holm thắng trong 8 cell claim |
|---|---|---|---|---|
| plugin | 21 / 0 / 0 | 21 / 0 | 8/8 | 8/8 |
| ida_union | 21 / 0 / 0 | 21 / 0 | 8/8 | 8/8 |
| bvar_minnesota | 16 / 4 / 1 | 16 / 1 | 8/8 | 8/8 |
| pselect_union | 17 / 2 / 2 | 17 / 2 | 6/8 | 6/8 |

Hai cell claim không thắng đều là hòa với `pselect_union_calT`: T80 missing-0.2 −0.24 [−0.48, +0.06] và T150 missing-0.2 −0.02 [−0.17, +0.13]. Hai cell thua `pselect_union_calT` là T40 missing-0.2 (+1.49 [+0.77, +2.34]) và missing-0.5 (+2.39 [+1.47, +3.54]); cell thua `bvar_minnesota_calT` là T40 missing-0.2 (+1.38 [+0.66, +2.13]). Bản `_calT1` (lưới một phía) cho đúng cùng số đếm.

**Skeleton đúng (cell none), theo yêu cầu R2-3b:**

| T | auto3 − ida_union_calT | auto3 − plugin_calT | auto3 − ida_union (thô) | auto3 − plugin (thô) |
|---|---|---|---|---|
| 40 | −6.40 [−7.29, −5.51] | −4.28 [−4.84, −3.64] | **+0.69 [+0.40, +1.01]** | +0.19 [−0.58, +0.77] |
| 80 | −5.03 [−5.59, −4.48] | −3.57 [−3.82, −3.34] | **+0.12 [+0.03, +0.22]** | −0.10 [−0.34, +0.10] |
| 150 | −3.89 [−4.35, −3.45] | −2.77 [−2.98, −2.59] | **+0.14 [+0.07, +0.21]** | **+0.29 [+0.17, +0.42]** |

**Đọc kết quả, nói thẳng.** Calibrate theo T mà không đọc stated kind buộc baseline chọn **một** hệ số cho cả cell none lẫn cell thiếu 50% cạnh. Vì cell thiếu cạnh kéo hệ số lên 3.5–4.1 cho plugin/ida, các bản `_calT` over-cover ở cell none (coverage 1.000) và IS tăng 2.2–3.3 lần so với bản thô. Vì vậy "auto3 thắng plugin_calT/ida_union_calT ở cell none" là hệ quả của việc baseline không có cổng, **không** phải bằng chứng auto3 hẹp hơn trên skeleton đúng. So sánh trung thực trên skeleton đúng là với baseline thô (có coverage 0.86–0.97): auto3 **thua** `ida_union` ở cả ba T và thua `plugin` ở T150. Đây đúng là cái giá của báo động giả (5–10%) cộng dự phòng đảo chiều.

**Câu claim được phép (exploratory, D-07 development):** ở T ≥ 80, trên cell thiếu và đảo cạnh, `tolerant_auto3` (không đọc khai báo) có IS thấp hơn có ý nghĩa so với plugin, ida_union và bvar_minnesota đã được calibrate theo T trên bank calibration (8/8 cell mỗi baseline, cả sau Holm), và so với pselect_union đã calibrate ở 6/8 cell (hòa ở missing-0.2 tại T80 và T150). Ở T40 thiếu cạnh, auto3 thua pselect_union (cả thô lẫn đã calibrate). Trên skeleton đúng, auto3 tốn hơn ida_union thô (+0.12 đến +0.69) và plugin thô ở T150 (+0.29).

## 7. Tổng kết vòng 2 của hướng auto5

| Mục | Quy tắc ghi trước | Kết quả | Holm |
|---|---|---|---|
| R2-3a auto3 dưới latent1 | coverage ≥ 0.90 ở 4 cell missing/reversed-0.2, T80/150 | **ĐẠT** 4/4 (0.937–0.977) | 4/4 |
| R2-3b auto3 vs baseline calibrate theo T | thắng mỗi X_calT ở 8/8 cell missing/reversed T ≥ 80 | **KHÔNG ĐẠT**: 8/8 với plugin, ida, bvar; 6/8 với pselect (2 hòa) | như điểm |
| R2-3c auto5 | B1 C1–C3 + C4 (T40 missing không tệ hơn pselect_union) | **LOẠI**: C1 trượt ở T80 reversed-0.5 (0.898); C2, C3, C4 đạt | 8/10 coverage cell; C4 0/2 "tệ hơn" |

- `tolerant_auto3` vẫn là ứng viên duy nhất của chế độ không khai báo. Nó đạt rule B1 (vòng 1) và rule độ bền latent1 (vòng 2) trên D-07 development.
- `tolerant_auto5` tốt hơn auto3 về IS ở 23/24 cell (CI < 0 ở 13 cell) và là bản đầu tiên không thua `pselect_union` ở T40 thiếu cạnh, nhưng trượt C1 ở một cell 0.898. Theo quy tắc, nó bị loại; không có spec P4-H2 cho auto5.
- Phát hiện phụ: sau khi khử term trùng, targeted opening có re-selection tốt hơn all-lag cả ở T80/T150 (mục 5), ngược với X4. Bug term trùng của ext_narrow có thể là một phần lý do của kết luận X4 ở vòng 1 (chưa kiểm chứng; cần chạy lại v5 với bản khử trùng).
- Vi phạm thời gian: `ext_auto5_main` chạy 23.4 phút (> ~20 phút); `ext_auto5_a1` 17.5 phút.
- Bug trong file có sẵn: không thấy bug mới ngoài bug term trùng của `ext_narrow.opened_terms` (đã ghi ở mục 0 và trong decision_rules.md). Lưu ý cho runner: `fair_baselines.py` phải tự tái tạo pha calibration vì `calibrate_methods` chỉ key theo stated kind; nếu muốn baseline calibrate theo T trong runner, cần một key mới (không sửa trong vòng này).

## Frozen spec for P4-H2

**Ứng viên: `tolerant_auto3` (không phải auto5).** auto3 đạt rule B1 (gate.md mục 4–5) và rule độ bền latent1 (mục 1, 4). auto5 bị loại (mục 5), nên không có spec cho auto5. CHƯA chạy, và tác giả sẽ không chạy.

- **Method:** `tolerant_auto3`, module `src/paper4/ext_gate.py` (nguyên trạng từ vòng 1, sha256 `42cf7285…f6b85a`), bảng width `experiments/ext/gate/width_table.json` (sha256 `392caa46…608603`; closed 1.5/1.3/1.3, open 1.0/1.2/1.3 ở T40/80/150). Tham chiếu: `plugin`, `tolerant_v4` (frozen, `experiments/calibration/tolerant_v4_frozen.json`), và `oracle` trong config latent1. Seed bootstrap của auto3 cố định theo tên (`ext_seed`). Danh sách sha256 đầy đủ: `results/ext_auto5_p4h2_dryrun/frozen_sha256.txt`.
- **Config 1 (B1):** `experiments/configs/ext_auto5_p4h2_auto3.json`: `"bank": "P4-H2"`, `"split": "confirmatory"`, `"frozen_calibration": "experiments/calibration/tolerant_v4_frozen.json"`, T ∈ {40, 80, 150}, cell none + {extra, missing, reversed} × {0.2, 0.5} + GES, 3 replicate, n_boot 199, H 4, seed_base 20261102, calibration block của a3_ges (D-07H development; chỉ dùng để lấy mức hỏng GES khai báo của v4).
- **Config 2 (latent1):** `experiments/configs/ext_auto5_p4h2_auto3_latent1.json`: cùng bank/split/frozen calibration, T ∈ {80, 150}, cell none + {missing, reversed} × 0.2, scenario clean + latent1, method oracle, plugin, tolerant_v4, tolerant_auto3.
- **Lệnh (chạy đúng một lần mỗi config, theo thứ tự):**
  1. `python experiments/run_experiment.py --config experiments/configs/ext_auto5_p4h2_auto3.json --workers 3`
  2. `python experiments/run_experiment.py --config experiments/configs/ext_auto5_p4h2_auto3_latent1.json --workers 3`
  3. `python experiments/ext/auto5/check_p4h2.py` (viết `results/ext_auto5_p4h2_check/check.md`). Script đã được dry-run chỉ trên row D-07 (`--dry-run`, `results/ext_auto5_p4h2_dryrun/check.md`: CONFIRMED trên D-07, Holm 13/14; **đây không phải kết quả xác nhận**).
- **Rule xác nhận (point rule trên coverage gộp, như B1; XÁC NHẬN khi và chỉ khi cả bốn đúng):**
  - **C1:** coverage của auto3 ≥ 0.90 ở mọi cell missing và reversed × {0.2, 0.5} tại T = 80 và 150 (8 cell, config 1).
  - **C2:** ở cell none, IS(auto3) ≤ 1.35 × IS(`tolerant_v4`) tại cả ba T = 40, 80, 150.
  - **C3:** ở cell GES tại T = 80 và 150: coverage ≥ 0.90 và IS(auto3) ≤ 1.10 × IS(`tolerant_v4`).
  - **L1:** scenario latent1 (config 2): coverage ≥ 0.90 ở missing-0.2 và reversed-0.2 tại T = 80 và 150 (4 cell).
  - Báo kèm, không quyết định: p một phía cho H0 "coverage ≤ 0.90" (cluster bootstrap 2000 lần theo topology, seed 0) và số cell bác H0 sau Holm (α 0.05) trên 14 cell coverage (C1 + C3 + L1); chênh lệch IS ghép cặp với v4 và plugin trong `summary.md`.
- **Nếu không xác nhận:** claim "chế độ không khai báo giữ coverage ở T ≥ 80" bị rút về exploratory, và paper chỉ trình bày chế độ có khai báo (v4).
- Thời gian ước tính: config 1 khoảng 10–17 phút, config 2 khoảng 8–12 phút với `--workers 3` (theo `ext_gate_auto3` và `ext_auto5_a1`).

*Ghi chú thời điểm:* tiêu đề "Ghi chú tiếp tục sau khi bị ngắt (… 02:25Z)" ghi ước lượng; ghi chú đó được lưu lúc 2026-11-02T02:22:53Z, cùng giây với lúc khởi động lại `ext_auto5_a1` (`experiments/ext/auto5/a1_rerun.log`), và ngay trước lệnh chạy. Quy tắc mục 3.3 được lưu trước 02:36:39Z (dấu thời gian in ngay sau khi ghi), tức trước khi `ext_auto5_main` khởi động lúc 02:40:46Z. Probe 1 và probe 2 chạy trên D-07H lúc 02:23–02:30Z và 02:31–02:34Z.

## Sửa sau kiểm chứng vòng 2

*Append một lần, 2026-11-02 (vòng 3, ID `auto3fix`, theo synthesis_round2.md R3-6 và mục 1.3). Các mục trên được giữ nguyên văn; khi có mâu thuẫn, mục này thay thế câu tương ứng ở trên. Số lấy từ `results/ext_verify2_auto5/{recompute.json, extra_checks.json}` và `results/ext_auto5_fair/rule_check.md`.*

1. **auto5 so với auto3 (mục 5 và 7).** Câu "IS thấp hơn ở 23/24 cell, CI < 0 ở 13/24" phải kèm **Holm: 10/24**. Không cell nào tệ hơn có ý nghĩa. Một phần lợi ích đến từ width factor đóng thấp hơn (closed 1.25 so với 1.3 ở T80; 1.2 so với 1.3 ở T150), không phải từ targeting. Vì vậy không được gán toàn bộ chênh lệch cho targeted opening.
2. **Phát hiện phụ về X4 (mục 5 "Targeted ở T lớn", mục 7 gạch đầu dòng 3) chỉ là gợi ý, không phải bác bỏ.** Câu "targeted opening có re-selection tốt hơn all-lag cả ở T80 và T150, ngược với X4" được thay bằng:
   - Trên 16 cell T80/T150, `tolerant_auto5_small` − `tolerant_auto5` có CI > 0 ở **6/16** cell (Holm 5/16); 10 cell còn lại hòa.
   - Ở T150, so sánh bị lẫn với width factor tune trong mẫu: open_all|150 = 1.25 so với open_tgt|150 = 1.2, chênh 4.2%.
   - Chỉ T80 missing-0.2 (+0.41) và T150 missing-0.2 (+0.24) rõ ràng lớn hơn phần chênh factor.
   - Câu đúng (theo synthesis X4): "targeted opening có re-selection và de-dup không tệ hơn all-lag ở mọi T đã thử, và tốt hơn rõ ở T40; ở T ≥ 80 lợi thế, nếu có, nhỏ và chưa ổn định."
3. **Mục 6, "IS tăng 2.2–3.3 lần so với bản thô"** sửa thành **1.9–3.3 lần**: plugin 1.94 / 2.25 / 2.94, ida_union 2.67 / 3.01 / 3.33 ở T40 / 80 / 150, cell none.
4. **Target của `_calT` (mục 2, mục 6).** Mô tả "hệ số chọn như runner" là sai. Lưới `_calT` bị chặn ở 5.0, nên target thực tế là coverage lớn nhất trên lưới bị chặn trừ 0.005, thấp hơn 0.95 với plugin và ida. Bản `_calT1` (lưới đến 10) chọn plugin 6.1 / 6.9 / 7.1 và ida 4.8 / 5.6 / 6.3, so với 3.9 / 4.1 / 4.1 và 3.45 / 3.8 / 3.7 của `_calT`. Vậy `_calT` không calibrate theo cùng target với auto3. Verdict R2-3b không đổi dưới `_calT1`: cùng số đếm.
5. **Gộp một factor theo T làm plugin/ida đã calibrate chỉ cover 0.44–0.52 ở missing-0.5.** Vì vậy "auto3 thắng plugin_calT/ida_union_calT" ở các cell đó gần như tự động. Câu "thắng baseline đã calibrate" chỉ có giá trị với `pselect_union` (6/8, Holm 6/8) và phần nào `bvar_minnesota`.
6. **Thua baseline thô ở cell extra T150 (mục 6 chưa nhắc).** Ngoài cell none, auto3 còn thua raw `plugin` ở T150 extra-0.2 (+0.28 [+0.16, +0.40]) và extra-0.5 (+0.23 [+0.14, +0.34]), và thua raw `ida_union` ở cùng hai cell (+0.12 [+0.04, +0.19] và +0.16 [+0.10, +0.23]). Câu claim ở cuối mục 6 phải đọc là: "Trên skeleton đúng và ở cell chỉ có cạnh thừa tại T150, auto3 tốn hơn baseline thô: +0.12 đến +0.69 so với `ida_union` (cell none ở mọi T, extra ở T150) và +0.23 đến +0.29 so với `plugin` (none, extra ở T150)."
7. **Spec P4-H2 ở mục "Frozen spec for P4-H2" đã được thay thế** bởi docs/ext/auto3fix.md mục 6. Spec mới có analyzer `experiments/ext/auto3fix/check_p4h2_v2.py`, run thất bại tính là không cover, báo `n_ok/n_exp`, có preflight và manifest spec, và kèm câu mong manh: 0.903 ở T80 reversed-0.5, Holm 13/14, P(CONFIRMED) ≈ 0.62 trên bootstrap topology của D-07. `check_p4h2.py` và hai config `ext_auto5_p4h2_*` được giữ nguyên nhưng **không** dùng cho P4-H2.
8. Hai điều đã công bố được nhắc lại cho đủ: `ext_auto5_main` mất 23.4 phút, vượt khoảng 20 phút; probe script vòng 1 được chép vào `experiments/ext/gate_probes/`, ngoài thư mục được phép của hướng.
