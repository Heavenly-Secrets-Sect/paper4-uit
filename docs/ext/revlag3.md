# Hướng `revlag3` (vòng 3, tiếp nối `revlag`): comparator khả thi cho reversal, RQ4.4 cho auto3/v5_1, sửa spec P3/P4

**Trạng thái.** Exploratory. Evaluation chỉ trên D-07 development (seed_base 20261102). Calibration và design probe chỉ trên D-07H development. Không đụng P4-H1, P4-H2 hay confirmatory split nào; không chạy config P4-H2 nào. Module of record vẫn là `tolerant_v4` (frozen). Không có LLM call, không git commit.

Bốn việc (synthesis_round2.md, R3-4, R3-9, sửa spec P3/P4, R3-6 cho revlag.md):

- **(A) R3-4.** Pre-register version mới xử lý reversal bằng orientation draw có trọng số theo evidence (module mới `src/paper4/ext_revlag3.py`), so với `tolerant_v4` trên cặp affected (định nghĩa red team, |ΔC| ≥ 0.05), để trả lời: gap 0.06–0.08 so với `oracle_cal` có giảm được bằng một method khả thi hay không. Nhánh "nhiều orientation draw hơn" được trả lời bằng phân tích Monte Carlo trên dữ liệu vòng 2 (không cần run mới, lý do ở (A4)). Thêm 1/width làm comparator row trong bảng RQ4.4.
- **(B) R3-9.** AUROC (mô tả) của flag RQ4.4 frozen trên hàng `tolerant_auto3` và `tolerant_v5_1`.
- **(C) Sửa spec P3/P4** (đường dẫn frozen calibration bị hard-code; lệch mã hoá feature "stated") bằng file mới, kèm spec manifest.
- **(D) R3-6** cho revlag.md (append một lần, heading "Sửa sau kiểm chứng vòng 2").

## File của hướng này (chỉ file mới)

| File | Vai trò |
|---|---|
| `src/paper4/ext_revlag3.py` | `tolerant_v4R` (evidence-weighted orientation draws), `tolerant_v4Rmap` (hard MAP orientation, ablation), và ba variant chỉ dùng cho probe D-07H (`tolerant_v4R_t05`, `tolerant_v4R_mix`, `tolerant_v4R_bag`) |
| `experiments/ext/revlag3/run_pairs3.py` | Runner pair-level mới: đọc frozen calibration **chỉ** từ key `frozen_calibration` và kiểm sha256 với `frozen_calibration_sha256`; hỗ trợ mọi ext method trên stream `ext_seed` như runner chính; lưu cả hai mã hoá stated; đếm run thất bại; ghi module định nghĩa từng method |
| `experiments/ext/revlag3/calibrate3.py`, `probe_variants.py` | Calibration width trên D-07H development bằng `run_experiment.calibrate` |
| `experiments/ext/revlag3/frozen_revlag3.json`, `frozen_revlag3_eval.json` | Width factor frozen (mod\|* = tolerant_v4_frozen.json nguyên văn; tolerant_v5_1\|* = frozen_v4_v51.json nguyên văn; tolerant_v4R* từ D-07H) |
| `experiments/ext/revlag3/probe_evidence.py` | Probe D-07H: evidence có phân biệt được cặp bị đảo không |
| `experiments/ext/revlag3/analyze_rev.py` | Rule R1/R2 của (A) |
| `experiments/ext/revlag3/mc_draws.py` | Phân tích Monte Carlo cho nhánh "nhiều draw hơn" |
| `experiments/ext/revlag3/flag3.py`, `flag_extra.py`, `analyze_r39.py` | Flag frozen: mã hoá như lúc train, 1/width, R3-9 |
| `experiments/ext/revlag3/check3.py` | Kiểm tra hợp lệ (trùng hàng với vòng 2 / runner) |
| `experiments/ext/revlag3/analyze_flag_p4h2_v2.py`, `analyze_lag_p4h2_v2.py`, `p4h2_spec_files.json` | Spec P3/P4 đã sửa (FROZEN, NOT RUN) |
| `experiments/configs/ext_revlag3_{cal,probe,probe2}.json` | D-07H (calibration, probe) |
| `experiments/configs/ext_revlag3_{rev,flag}.json` | D-07 development (evaluation) |
| `experiments/configs/ext_revlag3_p4h2.json` | P4-H2 (FROZEN, NOT RUN) |
| `results/ext_revlag3_*` | Kết quả |

## Những gì đã chạy TRƯỚC khi ghi rule (công bố đầy đủ, chỉ D-07H development)

Không có run nào trên D-07 trước khi ghi phần đăng ký này. Đã chạy:

1. **Probe evidence** (`probe_evidence.py`, D-07H development, 20 topology × 1 replicate, T 40/80/150, reversed-0.2/0.5; 0.5 s; `results/ext_revlag3_probe/evidence.md`). Với mỗi cặp trong pool của v3 (cặp contemporaneous có |t| > 1.645), Δℓ = log-likelihood Gaussian của hệ cấu trúc khi lật riêng cặp đó trừ khi giữ nguyên. Kết quả: ở T80/150, AUROC của Δℓ để nhận ra cặp bị đảo trong pool là 0.83–0.88 (mean Δℓ cặp bị đảo +3.1 đến +7.0, cặp không bị đảo −1.5 đến −3.8); ở T40 không có thông tin (0.50–0.55). Cặp bị đảo nằm trong pool: 21/26 và 63/72 ở T80; 26/26 và 69/72 ở T150. Nghĩa là evidence có thật ở T ≥ 80 (lag set của hai phương trình khác nhau nên hai hướng không tương đương), nhưng 10–20% cặp bị đảo ở T80 nằm ngoài pool và không method nào dựa trên pool cứu được.
2. **Calibration** (`calibrate3.py`, 60.2 s, `--workers 3`): `run_experiment.calibrate` trên D-07H development (unit seed_base + 500 000), kind reversed + none. Factor (đã gồm pre-scale 0.5): `tolerant_v4R` reversed 3.0/2.7/2.5 (hiệu dụng 1.5/1.35/1.25), `tolerant_v4Rmap` 3.2/2.8/2.7 (1.6/1.4/1.35); v4 frozen là 1.4/1.4/1.3. Factor plugin ở cell none ra 1.4/1.3/1.2, trùng a2_baselines (kiểm tra seed).
3. **Probe 1** (`ext_revlag3_probe`, D-07H development, 20 topology × 1 replicate, cell reversed; 48 s): oracle, v4, v4R, v4Rmap (`results/ext_revlag3_probe/rev_analysis.md`). **Đã xem số.** Coverage trên cặp affected **không tăng**: v4R − v4 từ −0.069 đến −0.011, v4Rmap từ −0.103 đến 0.000 ở T80/150; R1 0/4 cho cả hai. Point error trên cặp affected giảm ở T150 (median 0.498 → 0.358 ở rev-0.2; 0.415 → 0.337 ở rev-0.5) nhưng interval hẹp hơn (median width 1.62 → 1.38), nên coverage không tăng. v4Rmap có IS tệ hơn v4 ở 6/6 cell theo point (ratio 1.06–1.20).
4. **Probe 2** (`probe_variants.py` + `ext_revlag3_probe2`, D-07H development; calibration 66.5 s, probe 67.4 s; `results/ext_revlag3_probe2/rev_analysis.md`): ba variant gợi ý từ probe 1 — evidence tempered ×0.5 (`_t05`), mixture 50% draw đều như v3 + 50% draw theo evidence (`_mix`), parametric bootstrap của quyết định orientation (`_bag`). **Đã xem số.** Không variant nào tăng coverage trên cặp affected có ý nghĩa (delta từ −0.046 đến +0.023; R1 0/4 cho cả ba). `_mix` có IS tốt hơn hoặc ngang v4 ở 6/6 cell reversed (ratio 0.928–0.998; T150 rev-0.2 −0.141 [−0.194, −0.088]); `_bag` tệ hơn ở T40 (ratio 1.07–1.08).
5. Các script phân tích (`analyze_rev.py`, `mc_draws.py`, `flag3.py`, `flag_extra.py`, `analyze_r39.py`, `check3.py`) được viết trước mọi run D-07 và chỉ được chạy thử trên các run D-07H ở trên. `mc_draws.py` và `flag_extra.py` đọc dữ liệu D-07 **đã có từ vòng 2** (ext_revlag_lag, ext_revlag_fresh*); chưa chạy trước khi ghi rule.

Vì probe đã xem số, việc chọn `tolerant_v4R_mix` làm comparator thứ hai là **lựa chọn sau probe D-07H** (được phép, đã công bố). `tolerant_v4R` là thiết kế chính đã định trước probe; `tolerant_v4Rmap` là ablation đã định trước probe. `_t05` và `_bag` không vào evaluation D-07.

## Đăng ký trước

### Chung

- CI: bootstrap theo cụm topology (20 cụm), 2000 lần, percentile, seed 20261103 (dùng lại `Boot`/`Clus` của revlag, không đổi). p một phía = tỷ lệ replicate ở phía H0 (sàn 1/2000). Holm như ghi ở từng rule. Mọi số trích dẫn nằm trong `results/ext_revlag3_*`.
- Interpreter: `/usr/bin/python3` (CLT, numpy 2.0.2), `--workers 3`, như run vòng 2 của revlag (để kiểm tra trùng hàng tuyệt đối).

### (A) R3-4: comparator khả thi cho reversal

**Methods** (đều chỉ đọc data, public skeleton và `skel.damage`; ở cell không có stated reversal, cả ba trả về `tolerant_v3` pre-scale 0.5):
- `tolerant_v4R` (chính): Δℓ_e cho mỗi cặp e của pool v3 tính một lần trên data; prior π = k_rev/|pool|; log posterior odds a_e = logit(π) + Δℓ_e. Mỗi bootstrap draw sắp pool theo a_e + Gumbel (Plackett–Luce, tức lấy mẫu không hoàn lại với trọng số exp(a_e)) và lật k_rev cặp đầu tiên không tạo chu trình. Phần còn lại giống hệt v3 (fit0 làm DGP, refit mỗi draw, point estimate = mean của draw). Thay đổi duy nhất so với v3: thứ tự lật có trọng số thay vì đều.
- `tolerant_v4R_mix` (phụ, chọn sau probe D-07H): mỗi draw, với xác suất 0.5 dùng thứ tự đều như v3, còn lại dùng thứ tự theo evidence.
- `tolerant_v4Rmap` (ablation): lật cố định k_rev cặp có a_e lớn nhất, bootstrap với term cố định.
- Width: factor theo (T, stated kind) tune trên D-07H development bằng `run_experiment.calibrate` (grid hai phía 0.5–5 nhờ pre-scale 0.5), frozen trong `experiments/ext/revlag3/frozen_revlag3_eval.json` (sha256 `c57218af10124073fa73ec9688bc7c419b56771fd5a29dcd717d4f7029a47cdc`). v4 dùng factor frozen của nó (mod\|*).

**Run** `ext_revlag3_rev`: D-07 development, seed_base 20261102, 20 topology × 3 replicate, T 40/80/150, chỉ cell reversed-0.2 và reversed-0.5 (vị trí cell c_idx giữ như grid đầy đủ, nên stream giống `ext_revlag_lag`/`a2_baselines`), H 4, lag_max 2, n_boot 199, τ 0.1. Methods: `oracle`, `tolerant_v4`, `tolerant_v4R`, `tolerant_v4R_mix`, `tolerant_v4Rmap`.

**Điều kiện hợp lệ:** hàng `oracle` và `tolerant_v4` phải trùng tuyệt đối (C_e, lo, hi, C_t) với `results/ext_revlag_lag/pairs.npz` trên cùng khoá. Nếu không, run bị coi là hỏng và báo như vậy.

**Đơn vị:** cặp non-null; ghép cặp giữa các method trên cùng (unit, T, cell, cặp); chỉ giữ cặp mà mọi method đều ok (số run thất bại được báo). Affected = dC ≥ 0.05 (θ chính), sensitivity θ = 0.02 / 0.10. `oracle_cal` = oracle nới quanh trung điểm bằng c_T của plugin ở cell none (1.4/1.3/1.2), như vòng 2.

**Rule (mỗi method mới M, so với v4):**
- **R1 (chính, "gap giảm").** Ở 4 cell chính (reversed-0.2/0.5 × T 80/150), trên cặp affected: Δ = cov(M) − cov(v4). Cell **đạt** nếu cận dưới CI 95% của Δ > 0 **và** p Holm (một phía, H0: Δ ≤ 0, Holm qua 4 cell của M) < 0.05. Báo thêm Holm qua toàn họ (3 method × 4 cell = 12 test).
- **R2a (không làm tệ IS).** Ở cả 6 cell reversed (T 40/80/150), trên mọi cặp non-null: IS trung bình của M ≤ 1.05 × IS của v4 (point rule).
- **R2b (coverage).** Ở 4 cell chính, coverage của M trên mọi cặp non-null ≥ 0.90.
- **Câu trả lời cho câu hỏi R3-4, theo từng M:** R1 ≥ 3/4 và R2a, R2b đạt → **"GIẢM ĐƯỢC"** (gap giảm bằng method khả thi); R1 1–2/4 và R2 đạt → **"GIẢM MỘT PHẦN"**; R1 0/4 → **"KHÔNG GIẢM"**; còn lại → "KHÔNG KẾT LUẬN". Version **GIỮ** chỉ khi R1 4/4 và R2a, R2b đạt; ngược lại **LOẠI**.
- **Kết luận chung cho R3-4:** "gap giảm được bằng một method khả thi" nếu `tolerant_v4R` hoặc `tolerant_v4R_mix` là "GIẢM ĐƯỢC" **và** vẫn đạt R1 ≥ 3/4 khi dùng Holm qua toàn họ 12 test. Nếu cả ba là "KHÔNG GIẢM" thì câu cho paper là: "với các comparator khả thi đã thử (orientation draw theo likelihood evidence, mixture, MAP), gap không giảm; nó là cái giá của việc không biết hướng đúng, trong phạm vi các method đã thử" — không được viết "không thể giảm".
- **Báo kèm, không quyết định verdict:** closed share = Δ / (cov(oracle_cal) − cov(v4)) kèm CI; gap còn lại cov(M) − cov(oracle_cal); median |C − C_true| và median width trên cặp affected (centring); coverage trên cặp unaffected; T = 40; sensitivity θ; IS delta có CI và số cell IS tệ hơn có ý nghĩa sau Holm (6 cell).
- **Có điều kiện, ghi trước:** chỉ khi một M có verdict GIỮ, owner viết một spec P4-H2 phụ cho M (file mới, kèm manifest); ngược lại không có spec P4-H2 nào cho reversal comparator.

**Dự đoán ghi trước:** theo probe D-07H, R1 0/4 cho cả ba method, tức "KHÔNG GIẢM"; point error trên cặp affected giảm ở T150; `tolerant_v4R_mix` không tệ IS (R2a đạt), `tolerant_v4Rmap` hỏng R2a.

**(A4) Nhánh "nhiều orientation draw hơn" (mô tả, không có run mới).** Lý do không chạy: centre của v4 là trung bình của 199 draw; tăng số draw chỉ giảm sai số Monte Carlo của centre và của quantile, không đổi kỳ vọng của centre. `mc_draws.py` đo điều này trên `ext_revlag_lag` (D-07 development, vòng 2): v4 và v4L dùng cùng thuật toán trên hai stream độc lập (identity check vòng 2), nên |C_v4 − C_v4L|/√2 ước lượng sd Monte Carlo của centre với 199 draw. Cách đọc ghi trước: nếu median sd Monte Carlo < 0.2 × median |C_v4 − C_true| trên cặp affected ở mọi cell T ≥ 80, thì "nhiều draw hơn không thể đóng gap" là câu được phép viết. Báo kèm coverage của interval trung bình hai stream (proxy cho 398 draw) so với v4.

**(A5) 1/width trong bảng RQ4.4 (mô tả, không có run mới).** `flag_extra.py` trên các run fresh vòng 2 (seed_base 30261102, hàng `tolerant_v4`): thêm cột AUROC(1/width) [CI] và p̂ − 1/width [CI] cho clean T80/150, clean T40, GES (gộp và theo T), latent1, latent3, noise0.1, noise0.3 và 7 cell clean T80/150; làm hai lần, với mã hoá stated của vòng 2 và với mã hoá lúc train. Verdict F1–F4 vòng 2 giữ nguyên như đã ghi; bản tính lại với mã hoá lúc train chỉ là mô tả.

### (B) R3-9: flag RQ4.4 frozen trên auto3 và v5_1 (mô tả)

**Run** `ext_revlag3_flag`: D-07 development, seed_base 20261102, 20 topology × 3 replicate, T 40/80/150, 7 cell (none + extra/missing/reversed × 0.2/0.5), methods `tolerant_v4`, `tolerant_auto3` (stream `ext_seed`, width table của ext_gate), `tolerant_v5_1` (stream `ext_seed`, factor `tolerant_v5_1|T|kind` của frozen_v4_v51.json).

**Điều kiện hợp lệ:** hàng `tolerant_v4` trùng tuyệt đối với `ext_revlag_lag`; mỗi run của auto3 có (số cặp cover, số cặp non-null) trùng `results/ext_gate_auto3/runs.jsonl`, của v5_1 trùng `results/ext_v51_eval/runs.jsonl`. Nếu lệch, kết quả (B) vẫn được báo nhưng ghi rõ là không tái lập runner.

**Lưu ý ghi trước (in-sample).** Flag được fit trên hàng v4 của chính các dataset này (seed_base 20261102, vòng 1). Với auto3/v5_1 thì interval khác, nhưng miss của các method trên cùng data có tương quan, nên AUROC ở đây có thể lạc quan so với dữ liệu mới. Hard rule 3 của vòng 3 đặt evaluation ở seed_base 20261102, nên không dùng seed mới. Hàng v4 của run này được báo như reference in-sample.

**Score và cách đọc (ghi trước):**
- auto3: score chính là p̂ với stated dummy = 0 ("p̂ no-stated"), vì chế độ auto không đọc stated damage; p̂ đầy đủ báo kèm.
- v5_1: score chính là p̂ đầy đủ (chế độ khai báo); p̂ no-stated báo kèm.
- Comparator: rel_width và 1/width của chính method đó.
- Tập chính: T80/150 gộp 7 cell; T40 gộp 7 cell. Theo T (80, 150) và theo trạng thái gate của auto3: mô tả.
- "Chuyển được" ở (method, tập) nếu cận dưới CI của AUROC(score chính) > 0.5; "hơn 1/width" nếu cận dưới CI của AUROC(score chính) − AUROC(1/width) > 0. Báo số đạt trên 4 (2 method × 2 tập), chưa hiệu chỉnh và sau Holm (4). Ngưỡng F1/F3 (0.65) và F4 được áp máy móc như mô tả, không phải verdict.

**Dự đoán ghi trước:** chuyển được 4/4; "hơn 1/width" ở T80/150 cho v5_1, có thể không cho auto3 (gate state làm width của auto3 mang thông tin khác).

### (C) Spec P3/P4 đã sửa (FROZEN, NOT RUN)

Xem mục "Frozen spec P4-H2 (sửa P3/P4)" bên dưới. Không có kết quả nào trong hướng này dựa trên P4-H2.

## Kết quả

(Thêm sau khi chạy; phần đăng ký ở trên giữ nguyên.)
