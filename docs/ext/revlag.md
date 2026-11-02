# Hướng `revlag` (vòng 2, tiếp nối `metrics`): coverage trên cặp chịu đảo chiều, lag output, freeze cờ RQ4.4

**Trạng thái.** Exploratory. Đánh giá chỉ trên D-07 development. Design probe chỉ trên D-07H development. Không đụng P4-H1, P4-H2 hay bất kỳ confirmatory split nào. Module of record vẫn là `tolerant_v4` (frozen); hướng này thêm một version chỉ đổi **phần báo lag** (`tolerant_v4L`) và một cờ tin cậy đã freeze.

Ba việc (synthesis_round1.md, R2-6 và R2-7):

- **(a) R2-6a.** Coverage của oracle trên cặp "affected" theo định nghĩa red team (|ΔC| ≥ 0.05, sensitivity 0.02/0.05/0.10). Mục tiêu: chốt câu "khó nội tại" hay "lỗi module" (xung đột X1).
- **(b) R2-6b.** Module mới `tolerant_v4L` (src/paper4/ext_revlag.py): interval giống hệt v4 frozen, nhưng mean/peak lag lấy từ các structural draw (như C(H)) thay vì từ fit0.
- **(c) R2-7.** Freeze một cờ kết hợp (logistic trên đại lượng quan sát được) chỉ dùng hàng D-07 của vòng 1, rồi đánh giá **một lần** trên một lượt chạy D-07 development mới với seed_base khác (30261102). Báo AUROC với CI clustered theo topology, kể cả cho hàng GES/latent/noise.

## File của hướng này (chỉ file mới)

| File | Vai trò |
|---|---|
| `src/paper4/ext_revlag.py` | `tolerant_v4L`; `tolerant_v4L_draws` trả thêm IRF của từng draw |
| `experiments/ext/revlag/run_pairs.py` | Runner pair-level, mirror đúng seed/stream của `run_experiment.py` (oracle rng(2), v4 rng(6), v4L `ext_seed`) |
| `experiments/ext/revlag/check_identity.py` | Kiểm tra v4L với cùng stream rng(6) cho C/lo/hi trùng bit với v4 (D-07H) |
| `experiments/ext/revlag/probe_summary.py` | Bảng mô tả lag theo cell/role |
| `experiments/ext/revlag/flaglib.py`, `flag_design.py`, `frozen_flag.json` | Thiết kế và freeze cờ RQ4.4 trên hàng D-07 vòng 1 |
| `experiments/configs/ext_revlag_*.json` | Config probe (D-07H) và config đánh giá (D-07) |
| `results/ext_revlag_*` | Kết quả |

## Những gì đã chạy TRƯỚC khi ghi rule (công bố đầy đủ)

Không có lượt chạy nào trên D-07 trước khi ghi phần đăng ký này. Đã chạy:

1. `check_identity.py` trên D-07H development (2 topology, T 40/80, 7 cell): 28/28 run cho C, lo, hi của `tolerant_v4L` trùng bit với `tolerant_v4` khi dùng cùng stream rng(6); với cell có structural draw, cumulative(theta_v4L) = C; với cell không có, theta trùng v4 (`results/ext_revlag_identity/check.txt`).
2. Design probe `ext_revlag_probe` trên D-07H development (6 topology × 1 replicate, T 40/80/150, 7 cell; oracle, v4, v4L), 34 s. Bảng: `results/ext_revlag_probe/summary.md`. Điều thấy được (6 topology, nhiễu lớn): peak hit trên cặp damaged của cell reversed tăng từ 0.00–0.13 (v4) lên 0.13–0.50 (v4L); mean-lag error trên các cặp đó giảm (ví dụ T150 reversed-0.5: 0.88 → 0.33). Ở vài cell missing, mean-lag error trên mọi cặp **tăng** nhẹ (T40 missing-0.2: 0.676 → 0.741; T150 missing-0.5: 0.272 → 0.292), và tỷ lệ cặp có mean lag xác định giảm tới 0.045. Probe này là căn cứ đặt margin 0.05 và yêu cầu "vừa vượt margin vừa có ý nghĩa" ở điều kiện L2 dưới đây.
3. Timing probe GES và latent/noise trên D-07H development, 3 topology (`ext_revlag_probe_ges`, `ext_revlag_probe_a1`): 3.4 s và 12 s. Không xem số.
4. Thiết kế cờ RQ4.4 (`flag_design.py`) **chỉ trên hàng D-07 vòng 1** (`results/ext_metrics_pairs/pairs.npz`, không sinh dữ liệu mới). Kết quả và trọng số đã freeze ở mục (c).

## Đăng ký trước

### Chung

- **Lượt đánh giá chính** `ext_revlag_lag`: D-07 development, seed_base 20261102 (ghép cặp với `a2_baselines` và `ext_metrics_pairs`), 20 topology × 3 replicate, T ∈ {40, 80, 150}, cell none + {extra, missing, reversed} × {0.2, 0.5}, H = 4, lag_max = 2, n_boot = 199, tau = 0.1. Methods: `oracle`, `tolerant_v4` (rng(6), hệ số width frozen), `tolerant_v4L` (stream `ext_seed("tolerant_v4L")` như runner).
- **Điều kiện hợp lệ:** hàng `oracle` và `tolerant_v4` của lượt này phải trùng **tuyệt đối** (C_e, lo, hi của mọi cặp non-null) với hàng tương ứng trong `results/ext_metrics_pairs/pairs.npz` của vòng 1. Nếu không, lượt chạy bị coi là hỏng và được báo như vậy.
- CI: bootstrap theo cụm topology (20 cụm), 2000 lần lấy lại, percentile, seed 20261103. p-value một phía từ bootstrap = tỷ lệ replicate nằm ở phía H0 (sàn 1/2000). Holm áp trong từng họ test của một rule.
- Mọi số được trích sẽ nằm trong `results/ext_revlag_*`.

### (a) R2-6a: oracle trên cặp affected (phân tích trên `ext_revlag_lag`)

- **Affected (định nghĩa red team, `experiments/ext/redteam/pair_probe.py`):** cặp non-null có ΔC = |C_true − C0| ≥ θ, với C0 là C_true khi mọi cạnh thật bị hỏng (ở đây: cạnh bị đảo) được đặt hệ số 0 trong SEM thật. θ chính = 0.05; sensitivity θ = 0.02 và 0.10. Unaffected = non-null còn lại.
- **Tham chiếu chính:** `oracle_cal` = oracle (skeleton thật, lag thật) có interval nới quanh trung điểm bằng hệ số c_T của `plugin` trên cell none ("T|none|0.0" trong `results/a2_baselines/calibration.json`: 1.4 / 1.3 / 1.2, tune trên D-07H development). Lý do: v4 được calibrate width còn oracle thì không, nên so v4 với oracle thô lẫn hiệu ứng calibration vào. **Tham chiếu phụ:** oracle thô (như X1), báo cạnh nhau.
- **Gap** g = cov(v4) − cov(ref) trên cùng các cặp affected (ghép cặp), CI clustered.
- **Phân loại từng cell** (4 cell chính: reversed-0.2, reversed-0.5 × T ∈ {80, 150}; θ = 0.05; ref = `oracle_cal`):
  - **M (lỗi module):** cận trên CI của g < −0.03.
  - **I (khó nội tại):** cov(ref) < 0.90 và cận dưới CI của g > −0.03.
  - **N (không có lỗi module đáng kể, cặp không khó):** cov(ref) ≥ 0.90 và cận dưới CI của g > −0.03.
  - **U:** còn lại (không kết luận).
- **Verdict tổng:** #M ≥ 3 → "lỗi module"; nếu không, #I ≥ 3 → "chủ yếu khó nội tại"; nếu không, #M = 0 và #(I ∪ N) ≥ 3 → "không có lỗi module vượt 0.03"; còn lại → "hỗn hợp / không kết luận".
- **Holm:** họ M (H0: g ≥ −0.03, p = tỷ lệ replicate ≥ −0.03) và họ non-inferiority (H0: g ≤ −0.03), mỗi họ 4 cell. Báo số cell M và số cell có non-inferiority sau Holm.
- **Sensitivity:** bảng y hệt ở θ = 0.02 và 0.10 và với oracle thô. Verdict được gọi là **bền** nếu verdict tổng giống nhau ở cả θ = 0.02 và θ = 0.10 (ref `oracle_cal`). T = 40 báo, không phân loại vào verdict.
- **Mô tả thêm:** difference-in-differences (miss_affected − miss_unaffected) của v4 trừ cùng đại lượng của `oracle_cal`; coverage của cặp affected với cell missing (cùng định nghĩa) để đối chiếu.

### (b) R2-6b: `tolerant_v4L` (đánh giá trên `ext_revlag_lag`)

**Method.** `tolerant_v4L` = `tolerant_v4` frozen, trừ một điểm: khi có structural draw (repair hoặc reversal), theta = trung bình IRF qua các draw, nên cumulative(theta) = C (C(H) của v4 vốn đã là trung bình draw). Khi không có structural draw, output trùng v4. Interval: cùng thủ tục, cùng hệ số width frozen; trong lượt chạy, v4L dùng stream riêng (`ext_seed`) nên interval chỉ khác v4 ở nhiễu bootstrap.

**Đơn vị so sánh:** cặp non-null, ghép cặp v4L − v4 trên cùng (unit, T, cell, cặp).

- **L1 (chính).** Trên cặp **damaged** (role = 2, round-1 definition: chính cạnh của cặp bị đảo) của cell reversed-0.2 và reversed-0.5, ở T ∈ {80, 150} (4 cell), xét cặp kept (C_e ≠ 0 ở cả hai method): Δ peak-lag hit = hit(v4L) − hit(v4). **Đạt** ở một cell nếu cận dưới CI 95% clustered > 0 **và** p Holm (một phía, H0: Δ ≤ 0, Holm qua 4 cell) < 0.05. L1 đạt nếu 4/4 cell đạt.
- **L2 (không làm tệ).** Ở mỗi cell trong 21 cell (T ∈ {40, 80, 150} × 7 cell), trên mọi cặp non-null:
  - (i) Δ mean-lag abs error (trung bình |ml_e − ml_t| trên cặp có mean lag xác định ở cả truth, v4 và v4L): **tệ hơn** nếu điểm ước lượng > +0.05 **và** cận dưới CI > 0;
  - (ii) Δ peak-lag hit (cặp kept ở cả hai): **tệ hơn** nếu điểm ước lượng < −0.05 **và** cận trên CI < 0;
  - (iii) Δ tỷ lệ cặp có mean lag ước lượng xác định: **tệ hơn** nếu điểm ước lượng < −0.05 **và** cận trên CI < 0.
  L2 đạt nếu **0** cell tệ hơn ở cả (i), (ii), (iii). Rule dùng CI chưa hiệu chỉnh (chặt hơn cho mục đích "không gây hại"); số cell tệ hơn sau Holm (21 cell mỗi metric) cũng được báo.
- **Verdict:** `tolerant_v4L` **GIỮ** nếu L1 và L2 cùng đạt; ngược lại **LOẠI**.
- **Báo kèm, không quyết định verdict:** coverage và IS của v4L so với v4 theo cell (kỳ vọng chênh ≤ 0.015 coverage, chỉ do nhiễu bootstrap); mean-lag error trên cặp reversed damaged; T = 40; percentile interval của mean lag từ các draw (coverage của lag interval, mô tả); bản lặp lại L1/L2 trên lượt chạy fresh `ext_revlag_fresh` (seed 30261102), mô tả.

**Dự đoán ghi trước:** L1 đạt (probe D-07H cho mức tăng 0.1–0.45). Rủi ro chính là L2(i) ở cell missing T40, nơi trung bình IRF qua các draw có thể đẩy mean lag ra xa.

### (c) R2-7: cờ RQ4.4 đã freeze, đánh giá một lần trên lượt chạy D-07 fresh

**Thiết kế (đã làm, chỉ trên hàng D-07 vòng 1, `results/ext_revlag_flagdesign/design.md`).**
- Outcome: `miss` = interval của `tolerant_v4` không chứa C_true (cặp non-null).
- Hai bộ feature quan sát được: S1 = log1p(rel_width), log1p(width), zero_in, log T, dummy loại hỏng khai báo (missing / reversed / extra theo `width_key`); S2 = S1 + tương tác của log1p(width) và log1p(rel_width) với (log T − log 80). Chọn bằng grouped 5-fold CV theo topology; S2 chỉ được chọn nếu hơn S1 ≥ 0.005 AUROC out-of-fold ở T 80/150. Kết quả: S1 0.7375, S2 0.7343 (T 80/150); S1 0.838 ở T 40. **Chọn S1.**
- Fit lại S1 trên toàn bộ 38 934 hàng vòng 1 (gộp T), lưu trong `experiments/ext/revlag/frozen_flag.json` (sha256 `7da8843fab352e798bec6471497192cfba201c0fa64ea333d2a4510938c37df3`). Trọng số chuẩn hóa: intercept −3.466, log1p rel_width +0.251, log1p width −1.407, zero_in +0.420, log T −0.635, stated_missing +0.137, stated_reversed +0.020, stated_extra +0.066.
- Cờ nhị phân: p̂ > 0.10 (xác suất miss dự báo gấp đôi mức danh nghĩa 0.05). Ngưỡng cố định trước, không tune. Kiểm tra in-sample trên hàng huấn luyện (không phải đánh giá): T 80/150 gắn cờ 8.8% cặp, miss 0.142 so với 0.035; T 40 gắn cờ 18.9%, miss 0.216 so với 0.026.

**Lượt chạy đánh giá (một lần, sau khi ghi rule này):** D-07 development, **seed_base 30261102** (unit 30261102 + 1000·t + rep; không trùng unit nào của 20261102 hay của calibration +500000). Cùng 20 topology với dữ liệu huấn luyện, chỉ khác seed: đây là kiểm tra trên dữ liệu mới, **không** phải trên topology mới.
- `ext_revlag_fresh`: T ∈ {40, 80, 150}, 7 cell, methods `tolerant_v4`, `tolerant_v4L`.
- `ext_revlag_fresh_ges`: cell GES (stated damage = trung bình lỗi GES trên D-07H development, `results/a3_ges/calibration.json`), T ∈ {40, 80, 150}, `tolerant_v4`.
- `ext_revlag_fresh_a1`: kịch bản latent1, latent3, noise0.1, noise0.3; T ∈ {80, 150}; cell none, missing-0.2, reversed-0.2; `tolerant_v4`.

**Rule (score = p̂ của mô hình frozen, không fit lại; mọi CI clustered theo 20 topology):**
- **F1.** Clean, T ∈ {80, 150}, gộp 7 cell: cận dưới CI của AUROC(p̂) > 0.65.
- **F2.** Clean, T ∈ {80, 150}: cận dưới CI của ΔAUROC = AUROC(p̂) − AUROC(rel_width) > 0.
- **F3.** Clean, T = 40: cận dưới CI của AUROC(p̂) > 0.65.
- **F4.** Cờ p̂ > 0.10, riêng ở T ∈ {80, 150} và ở T = 40: tỷ lệ cặp bị cờ ≤ 0.50, tỷ số miss rate (cờ / không cờ) ≥ 2 và cận dưới CI > 1.
- **Verdict:** cờ **ĐẠT (validated trên D-07 fresh)** nếu F1, F2, F3, F4 (cả hai tập T) cùng đạt; ngược lại **KHÔNG ĐẠT**, báo điều kiện nào hỏng. Vì verdict đòi mọi điều kiện cùng đạt (intersection-union), không cần hiệu chỉnh; vẫn báo số điều kiện đạt sau Holm qua 5 test (p một phía từ bootstrap).
- **Phụ (mô tả, có cách đọc ghi trước):** AUROC(p̂), AUROC(rel_width) và cờ p̂ > 0.10 trên GES (gộp T và từng T), latent1, latent3, noise0.1, noise0.3 (mỗi kịch bản gộp T 80/150 và 3 cell). Cờ "chuyển được" sang kịch bản đó nếu cận dưới CI của AUROC(p̂) > 0.5. Báo số kịch bản chuyển được, chưa hiệu chỉnh và sau Holm (5 kịch bản). AUROC cho auto3/v5 không thuộc phạm vi hướng này.

**Dự đoán ghi trước:** F1 sát biên (OOF vòng 1 là 0.74, CI vòng 1 rộng khoảng ±0.04); F3 đạt; F4 đạt ở cả hai tập T. Ở noise0.3, miss do attenuation bias không liên quan độ rộng, nên AUROC có thể gần 0.5.

## Kết quả

(Thêm sau khi chạy; phần đăng ký ở trên giữ nguyên.)

### Quy trình, gián đoạn và công bố

- **Thời điểm.** Phần đăng ký ở trên được băm lúc 2026-11-01T19:52:37Z (`results/ext_revlag_identity/rule_hash_before_runs.txt`, sha256 `f610adaa…543a`); băm lại trước các lượt chạy fresh vẫn trùng, tức phần đăng ký không đổi. Lượt `ext_revlag_lag` khởi chạy ngay sau đó trong **lần thử thứ nhất** của vòng 2 và ghi xong `pairs.npz` + `manifest.json` lúc khoảng 19:58Z (356.6 s, `--workers 3`). Lần thử thứ nhất bị dừng vì usage limit quanh thời điểm đó, nhưng lượt này **đã hoàn tất** (manifest là file ghi sau cùng), nên được dùng nguyên, **không chạy lại**. Ba lượt fresh chưa từng chạy ở lần thử thứ nhất; chúng được chạy ở lần thử thứ hai, bắt đầu 2026-11-02T02:24:29Z (`results/ext_revlag_identity/fresh_runs_started_utc.txt`, log `fresh_runs.log`): `ext_revlag_fresh` 576.7 s, `ext_revlag_fresh_ges` 84.4 s, `ext_revlag_fresh_a1` 332.7 s, đều `--workers 3`, đều dưới 20 phút, không thu nhỏ lưới.
- **Script phân tích** (`check_validity.py`, `analyze_lag.py`, `analyze_flag.py`, `oracle_peak.py`) viết ở lần thử thứ hai, sau phần đăng ký. `analyze_lag.py` và `analyze_flag.py` được viết xong trước khi xem bất kỳ số nào của (a), (b), (c). Bản đầu của `check_validity.py` chạy quá chậm (đọc npz từng phần tử) và bị dừng trước khi in gì; bản vector hoá thay thế. Sau khi có kết quả, chỉ sửa định dạng in (Holm in ra `np.float64(...)`) trong `analyze_flag.py`; không có thay đổi logic.
- **Không có lượt chạy nào khác trên D-07** ngoài `ext_revlag_lag` và ba lượt fresh. Không đụng D-07 confirmatory, P4-H1, P4-H2.
- **Cảnh báo kỹ thuật.** numpy (BLAS Accelerate trên macOS) in `RuntimeWarning: divide by zero/overflow encountered in matmul` khi tính score; đã kiểm tra: không có giá trị không hữu hạn trong feature hay trong p̂ ở cả bốn tập (fresh, GES, a1, vòng 1).
- **Điều kiện hợp lệ của `ext_revlag_lag`: ĐẠT.** `oracle` và `tolerant_v4`: mỗi method 38 934 hàng, cùng khóa, **0 hàng lệch** C_e/lo/hi/C_t so với `results/ext_metrics_pairs/pairs.npz` (`results/ext_revlag_lag/validity.txt`).

### (a) R2-6a: kết quả (`results/ext_revlag_lag/analysis_a.md`, `analysis.json`)

Ref chính `oracle_cal`, θ = 0.05 (cặp affected: 232 ở reversed-0.2, 564 ở reversed-0.5, mỗi T):

| cell | T | cov v4 | cov oracle_cal | g [CI 95%] | Holm p (H0 g ≥ −0.03) | DiD miss [CI] | lớp |
|---|---|---|---|---|---|---|---|
| reversed-0.2 | 80 | 0.862 | 0.944 | −0.082 [−0.108, −0.056] | 0.002 | +0.086 [+0.057, +0.115] | M |
| reversed-0.2 | 150 | 0.909 | 0.978 | −0.069 [−0.106, −0.037] | 0.007 | +0.073 [+0.037, +0.112] | M |
| reversed-0.5 | 80 | 0.863 | 0.945 | −0.082 [−0.117, −0.050] | 0.002 | +0.080 [+0.048, +0.113] | M |
| reversed-0.5 | 150 | 0.906 | 0.970 | −0.064 [−0.092, −0.038] | 0.007 | +0.068 [+0.041, +0.098] | M |
| reversed-0.2 | 40 (báo) | 0.819 | 0.961 | −0.142 [−0.219, −0.080] | – | +0.127 | – |
| reversed-0.5 | 40 (báo) | 0.867 | 0.931 | −0.064 [−0.099, −0.026] | – | +0.048 | – |

- **#M = 4/4 (sau Holm qua 4 cell: 4/4); #I = 0, #N = 0. Verdict tổng theo rule: "lỗi module".**
- **Sensitivity:** θ = 0.02 → "lỗi module" (4 M); θ = 0.10 → "lỗi module" (4 M). Tập affected gần như không đổi theo θ (233 / 232 / 227 ở reversed-0.2), vì ΔC hoặc bằng 0 hoặc lớn. **Verdict bền: có.**
- **Với oracle thô** (tham chiếu phụ, θ = 0.05): cov oracle 0.879 / 0.957 / 0.878 / 0.947 (theo thứ tự bảng), g = −0.017 [−0.066, +0.035], −0.047 [−0.089, −0.008], −0.014 [−0.055, +0.029], −0.041 [−0.066, −0.018]; cả 4 cell là U, verdict "hỗn hợp / không kết luận" (0 M và 0 non-inferior sau Holm). Giống θ = 0.02 và 0.10.
- **DiD** (miss affected − miss unaffected của v4, trừ cùng đại lượng của ref) dương và CI loại 0 ở **mọi** cell T ≥ 80, với cả hai ref (oracle thô: +0.064 đến +0.084): miss của v4 dồn vào cặp affected nhiều hơn của oracle.
- **Đối chiếu cell missing** (cùng định nghĩa, θ = 0.05): g so với oracle_cal từ −0.012 đến +0.021, không cell nào dưới −0.03. Khoảng trống chỉ có ở reversal.

**Đọc kết quả (chốt X1).** Câu hỏi "khó nội tại hay lỗi module" có hai phần, và cả hai đều có thật:
1. **Có phần khó nội tại cho bootstrap thô ở T = 80:** oracle với skeleton đúng nhưng không nới width chỉ phủ 0.88 trên các cặp này (0.95 ở T = 150). Đây là phần verifier vòng 1 thấy.
2. **Nhưng có lỗi module vượt 0.03 khi so cùng mức calibration.** Nới oracle bằng hệ số none của plugin (1.4/1.3/1.2) đưa nó lên 0.94–0.98, còn v4, dù được nới **nhiều hơn** (hệ số frozen cho stated reversed là 1.4/1.4/1.3), chỉ đạt 0.86–0.91. Khoảng cách 0.06–0.08 không phải do width; DiD dương cho thấy v4 lệch tâm trên đúng các cặp chịu đảo chiều.
3. Câu cho bài: *dưới reversal, module phủ thiếu các cặp chịu ảnh hưởng của cạnh bị đảo (0.86 ở T80, 0.91 ở T150); oracle cùng mức calibration phủ 0.94–0.98, nên khoảng 0.06–0.08 là do nhánh xử lý đảo chiều của module; so với oracle không calibrate, khoảng cách chỉ 0.01–0.05 và không kết luận được.* Câu vòng 1 "chủ yếu là độ khó nội tại" (X1) phải thu hẹp lại như vậy. R-P1a của red team vẫn là FLAG như đã ghi.

### (b) R2-6b: kết quả (`results/ext_revlag_lag/analysis_b.md`, `oracle_peak.md`)

**L1 (peak hit, cặp damaged của cell reversed, kept ở cả hai):**

| cell | T | n | hit v4 | hit v4L | Δ [CI 95%] | p Holm (4 cell) | đạt |
|---|---|---|---|---|---|---|---|
| reversed-0.2 | 80 | 73 | 0.027 | 0.110 | +0.082 [+0.026, +0.154] | 0.002 | có |
| reversed-0.2 | 150 | 73 | 0.014 | 0.123 | +0.110 [+0.041, +0.188] | 0.002 | có |
| reversed-0.5 | 80 | 193 | 0.047 | 0.347 | +0.301 [+0.231, +0.373] | 0.002 | có |
| reversed-0.5 | 150 | 193 | 0.052 | 0.321 | +0.269 [+0.205, +0.345] | 0.002 | có |

L1: **4/4 (sau Holm 4/4) → ĐẠT.** T = 40 (báo): +0.123 và +0.244, CI loại 0.

**L2 (21 cell):** số cell tệ hơn theo rule: (i) 0, (ii) 0, (iii) 0; sau Holm (21 cell/metric): 0, 0, 0. Δ mean-lag error lớn nhất là T40 missing-0.2 +0.025 [+0.002, +0.047], dưới margin 0.05. Tỷ lệ cặp có mean lag xác định giảm nhiều nhất −0.045 (T40 reversed-0.2), cũng dưới margin. Ở cell none/extra, output trùng v4 tuyệt đối (Δ = 0), đúng thiết kế. **L2 ĐẠT.**

**Verdict: `tolerant_v4L` GIỮ** (L1 và L2 cùng đạt). Đúng dự đoán ghi trước; rủi ro ở missing T40 có xuất hiện nhưng nhỏ hơn margin.

**Báo kèm:**
- Mean-lag error trên cặp damaged reversed (T ≥ 80, cặp có mean lag xác định ở truth, v4 và v4L; `analysis_b.md`): v4 0.86–0.91 → v4L 0.37–0.60. Ở mức cell (mọi cặp non-null), reversed-0.5: 0.366 → 0.317 (T80), 0.317 → 0.241 (T150).
- **Vẫn xa oracle:** peak hit của oracle trên cùng các cặp là 0.90–0.93, mean-lag error 0.16–0.22. v4L chỉ thu hẹp một phần (0.11–0.35). Cơ chế (giả thuyết, chưa kiểm): mỗi draw chỉ lật k_rev cạnh lấy từ pool, nên nhiều draw vẫn giữ chiều sai, và trung bình IRF vẫn đặt đỉnh ở lag 1.
- Coverage/IS của v4L so với v4: chênh coverage tối đa 0.007, IS chênh tối đa 0.08 về trị tuyệt đối (T40 reversed-0.5: 4.551 → 4.471), đúng kỳ vọng "chỉ khác nhiễu bootstrap".
- Percentile interval của mean lag từ các draw phủ mean lag thật chỉ 0.66–0.76: **không** dùng được như lag interval trung thực. Không đề xuất báo lag interval kiểu này.
- **Lặp lại mô tả trên lượt fresh** (`results/ext_revlag_fresh/analysis_b.md`, seed_base 30261102; dòng "Verdict … LOẠI" trong file đó là kết quả áp máy móc rule lên dữ liệu lặp, chỉ mang tính mô tả, không thay verdict ở trên): L1 3/4. Cell không đạt là reversed-0.2 T80: +0.026 [+0.000, +0.066], p Holm 0.128 (hit 0.026 → 0.053, n = 76). Ba cell còn lại: +0.079, +0.258, +0.278, CI loại 0. L2: 0 cell tệ hơn ở cả ba metric. Tức là cải thiện ở reversed-0.5 lặp lại rõ, còn ở reversed-0.2 (ít cặp, khoảng 75) thì nhỏ và không ổn định ở T80.

### (c) R2-7: kết quả (`results/ext_revlag_fresh/flag_eval.md`, `flag_eval.json`)

Mô hình frozen (sha256 `7da8843f…7df3`, kiểm tra lại trong script), không fit lại. Hàng `tolerant_v4`, cặp non-null, D-07 development seed_base 30261102.

| tập | n | miss rate | AUROC(p̂) [CI] | AUROC(rel_width) [CI] | ΔAUROC [CI] | bị cờ | miss cờ / không cờ | tỷ số [CI] |
|---|---|---|---|---|---|---|---|---|
| clean T80/150 | 26 082 | 0.047 | 0.730 [0.694, 0.763] | 0.657 [0.615, 0.693] | +0.073 [+0.040, +0.110] | 0.082 | 0.161 / 0.037 | 4.32 [3.42, 5.50] |
| clean T40 | 13 041 | 0.072 | 0.824 [0.782, 0.862] | 0.590 [0.558, 0.621] | +0.234 [+0.197, +0.275] | 0.193 | 0.246 / 0.031 | 7.95 [5.84, 10.89] |

- F1 đạt (0.694 > 0.65); F2 đạt (+0.040 > 0); F3 đạt (0.782 > 0.65); F4 T80/150 đạt (8.2% bị cờ, tỷ số 4.32, cận dưới 3.42); F4 T40 đạt (19.3%, 7.95, cận dưới 5.84). Sau Holm qua 5 test: 5/5 (mọi p Holm = 0.0025).
- **Verdict cờ RQ4.4: ĐẠT (validated trên D-07 fresh).**
- Theo cell (T80/150, mô tả): AUROC(p̂) 0.70–0.79 ở cả 7 cell; ΔAUROC so với rel_width dương ở cả 7, CI loại 0 ở 5/7 (không loại 0 ở missing-0.5 và reversed-0.2).

**Phụ (GES, latent, noise):**

| kịch bản | n | miss rate | AUROC(p̂) [CI] | AUROC(rel_width) | tỷ số cờ [CI] |
|---|---|---|---|---|---|
| GES, gộp T | 5 589 | 0.049 | 0.738 [0.710, 0.766] | 0.559 | 5.01 [3.70, 6.47] |
| latent1 | 11 178 | 0.052 | 0.657 [0.614, 0.705] | 0.545 | 3.12 [2.30, 4.23] |
| latent3 | 11 178 | 0.071 | 0.596 [0.548, 0.649] | 0.491 | 2.85 [2.05, 3.90] |
| noise0.1 | 11 178 | 0.085 | 0.717 [0.683, 0.752] | 0.612 | 3.45 [2.82, 4.21] |
| noise0.3 | 11 178 | 0.186 | 0.687 [0.664, 0.711] | 0.562 | 2.28 [1.97, 2.64] |

- Cờ chuyển được ở **5/5** kịch bản, chưa hiệu chỉnh và sau Holm (5 kịch bản).
- GES theo T: 0.715 [0.600, 0.816] (T40), 0.740 (T80), 0.708 (T150). Ở GES T150, rel_width tốt hơn một chút: ΔAUROC −0.027 [−0.096, +0.033].
- latent3 chỉ yếu (0.596). Ở noise0.3, cờ vẫn xếp hạng được, nhưng nhóm không cờ vẫn miss 0.159: cờ không cứu được coverage khi bias do nhiễu đo chiếm ưu thế.

**Đối chiếu dự đoán ghi trước:** F1 được dự đoán sát biên, thực tế đạt rõ (cận dưới 0.694). F3 và F4 đạt như dự đoán. Dự đoán "noise0.3 gần 0.5" **sai**: 0.687.

**Giới hạn của (c).** Lượt fresh dùng **cùng 20 topology** với dữ liệu huấn luyện, chỉ khác seed: đây là dữ liệu mới, chưa phải topology mới. Feature chỉ là interval, ước lượng điểm, T và loại hỏng khai báo, nên cờ là cờ **của chính `tolerant_v4`** (đổi width factor là phải fit lại). P4-H2 là phép thử thật.

### Tổng hợp multiplicity (quy tắc 7)

| rule | số cell/test | đạt (theo rule) | đạt sau Holm |
|---|---|---|---|
| (a) họ M, 4 cell, θ 0.05, oracle_cal | 4 | 4 M | 4 |
| (a) họ non-inferiority | 4 | 0 | 0 |
| (b) L1 | 4 | 4 | 4 |
| (b) L2 tệ hơn (i)/(ii)/(iii) | 21 mỗi metric | 0/0/0 | 0/0/0 |
| (c) F1–F4 | 5 | 5 | 5 |
| (c) kịch bản phụ chuyển được | 5 | 5 | 5 |

## Frozen spec for P4-H2

Hai spec ứng viên. Không chạy. Không đụng P4-H2 trong hướng này.

**Chung.**
- Module file: `src/paper4/ext_revlag.py` (sha256 `81e9988b…7e00e`), method `tolerant_v4L`. `tolerant_v4` = `methods.tolerant_v3` trên stream rng(6), nới bằng hệ số frozen; runner pair-level `experiments/ext/revlag/run_pairs.py` tính đúng như runner chính (kiểm tra: 0 hàng lệch với vòng 1).
- Config: `experiments/configs/ext_revlag_p4h2.json`: `"bank": "P4-H2"`, `"split": "confirmatory"`, `"frozen_calibration": "experiments/calibration/tolerant_v4_frozen.json"` (run_pairs đọc cùng file đó qua `frozen_factor`), seed_base 20261102, 3 replicate, T ∈ {40, 80, 150}, cell none + {extra, missing, reversed} × {0.2, 0.5}, H 4, lag_max 2, n_boot 199, τ 0.1, methods `tolerant_v4`, `tolerant_v4L`. Không có bước calibration.
- Lệnh, chạy đúng một lần:
  1. `python experiments/ext/revlag/run_pairs.py --config experiments/configs/ext_revlag_p4h2.json --workers 3`
  2. `python experiments/ext/revlag/analyze_lag.py --run ext_revlag_p4h2` (rule L1/L2)
  3. `python experiments/ext/revlag/analyze_flag_p4h2.py --run ext_revlag_p4h2` (rule F1–F4)
- sha256 của mọi file liên quan: `results/ext_revlag_identity/p4h2_spec_sha256.txt`. Mọi file trong đó phải không đổi khi chạy.
- CI: bootstrap theo cụm topology của P4-H2 (mọi topology của split), 2000 lần, percentile, seed 20261103; p một phía = tỷ lệ replicate ở phía H0 (sàn 1/2000).

**Spec 1: `tolerant_v4L` (lag từ structural draw).** Rule y hệt rule (b) đã ghi trước ở trên:
- L1: trên cặp damaged (role 2) của reversed-0.2 và reversed-0.5, T ∈ {80, 150}, cặp kept ở cả hai: Δ peak-lag hit (v4L − v4) có cận dưới CI > 0 **và** p Holm (một phía, 4 cell) < 0.05 ở **cả 4/4** cell.
- L2: ở 21 cell, 0 cell tệ hơn theo (i) Δ mean-lag abs error > +0.05 và cận dưới CI > 0; (ii) Δ peak hit < −0.05 và cận trên CI < 0; (iii) Δ tỷ lệ mean lag xác định < −0.05 và cận trên CI < 0.
- Xác nhận nếu L1 và L2 cùng đạt; ngược lại không xác nhận. Báo nguyên văn.
- *Rủi ro ghi trước:* trên lượt D-07 fresh, cell reversed-0.2 T80 không đạt (+0.026 [0.000, 0.066]). Rule không được nới vì điều này. Nếu P4-H2 chỉ đạt 3/4, câu đúng là "cải thiện lag ở reversal mức 0.5, không xác nhận được ở mức 0.2".

**Spec 2: cờ RQ4.4 frozen** (`experiments/ext/revlag/frozen_flag.json`, sha256 `7da8843fab352e798bec6471497192cfba201c0fa64ea333d2a4510938c37df3`, score = p̂, cờ = p̂ > 0.10, không fit lại). Rule y hệt (c) trên hàng `tolerant_v4`, cặp non-null:
- F1: T ∈ {80, 150}, gộp 7 cell, cận dưới CI của AUROC(p̂) > 0.65.
- F2: T ∈ {80, 150}, cận dưới CI của AUROC(p̂) − AUROC(rel_width) > 0.
- F3: T = 40, cận dưới CI của AUROC(p̂) > 0.65.
- F4: ở T ∈ {80, 150} và riêng ở T = 40: tỷ lệ bị cờ ≤ 0.50, tỷ số miss rate (cờ / không cờ) ≥ 2, cận dưới CI của tỷ số > 1.
- Xác nhận nếu cả 5 điều kiện cùng đạt (intersection-union); báo kèm số điều kiện đạt sau Holm qua 5 test.

**Không đưa vào P4-H2:** kết luận (a). Đó là phân tích dùng truth, không phải method. Nếu team muốn lặp lại (a) trên P4-H2, phải thêm `oracle` vào config và ghi rule riêng trước khi chạy.

### File thêm ở lần thử thứ hai

`experiments/ext/revlag/check_validity.py`, `analyze_lag.py`, `analyze_flag.py`, `analyze_flag_p4h2.py` (chưa chạy trên P4-H2; đã chạy thử trên `ext_revlag_fresh`, output vào scratchpad, ra đúng số của `flag_eval.md`), `oracle_peak.py`; `experiments/configs/ext_revlag_p4h2.json` (FROZEN, NOT RUN); kết quả `results/ext_revlag_lag/{validity.txt, analysis_a.md, analysis_b.md, analysis.json, oracle_peak.md}`, `results/ext_revlag_fresh/{analysis_b.md, analysis.json, flag_eval.md, flag_eval.json}`, `results/ext_revlag_fresh_ges/`, `results/ext_revlag_fresh_a1/`, `results/ext_revlag_identity/{fresh_runs_started_utc.txt, fresh_runs.log, p4h2_spec_sha256.txt}`. Sửa vòng 1 của hướng `metrics` đã được append vào `docs/ext/metrics.md` (mục "Sửa sau kiểm chứng vòng 1").

## Sửa sau kiểm chứng vòng 2

(Append một lần theo R3-6 của docs/ext/synthesis_round2.md. Hướng `tables` (R3-8, docs/ext/bang_ban_thao.md) append thay owner, vì hướng `revlag3` dừng trước khi append; bản nháp của nó được dùng làm cơ sở và đã sửa cho khớp với file hiện có. Phần trên giữ nguyên; các câu dưới đây thay thế câu tương ứng.)

1. **Câu X1 thay thế.** Bỏ câu đọc kết quả (a) ở mục "(a) R2-6a: kết quả", điểm 3 ("khoảng 0.06–0.08 là do nhánh xử lý đảo chiều của module"). Câu đúng là câu X1 mới của synthesis_round2.md mục 1.6:
   > Trên các pair bị ảnh hưởng bởi cạnh đảo (|ΔC| ≥ 0.05), `tolerant_v4` cover 0.86 (T80) và 0.91 (T150), so với 0.94–0.98 của một oracle biết hướng đúng được widen về cùng mức width. Interval của v4 rộng hơn nhưng lệch tâm. Chưa test xong xem gap này có giảm được bằng cách xử lý reversal tốt hơn hay không.

   Verdict "lỗi module" theo rule (a) vẫn là verdict đã ghi. Nhưng nó chỉ nói v4 kém một reference **biết hướng thật**; nó không chứng minh nhánh reversal có lỗi sửa được. R3-4 (docs/ext/revlag3.md) chưa có kết quả hợp lệ trên D-07: run `ext_revlag3_rev` hỏng điều kiện validity của oracle, còn run sửa `ext_revlag3_rev2` chưa chạy. Vì vậy câu cuối của X1 vẫn là "chưa test xong".
2. **"Khó nội tại ở T80" bị nói quá.** Ở T80, raw oracle under-cover trên mọi nhóm pair: 0.899 ở cell none, và 0.902 / 0.909 trên pair unaffected của reversed-0.2 / 0.5 (`results/ext_verify2_revlag/recheck_a.md`; cũng ở bảng 3b của docs/ext/bang_ban_thao.md). Trên pair affected nó cover 0.879 / 0.878, nên phần khó riêng của pair affected nhiều nhất khoảng 0.03 ở T80. Ở T150 (0.957 / 0.947) phần này bằng 0. Câu "có phần khó nội tại cho bootstrap thô ở T = 80" phải đọc là "bootstrap thô under-cover ở T80 trên mọi pair; phần riêng của pair affected nhiều nhất khoảng 0.03".
3. **"Verdict bền theo θ" gần như hiển nhiên.** Tập affected gần như trùng nhau qua θ = 0.02 / 0.05 / 0.10: 233 / 232 / 227 pair ở reversed-0.2 và 569 / 564 / 558 ở reversed-0.5 (`results/ext_revlag_lag/analysis_a.md`). Lý do là ΔC hoặc bằng 0 hoặc lớn. Sensitivity theo θ không phải bằng chứng độc lập.
4. **Thời điểm viết `analyze_flag.py`.** Câu ở mục "Quy trình, gián đoạn và công bố" ("`analyze_lag.py` và `analyze_flag.py` được viết xong trước khi xem bất kỳ số nào của (a), (b), (c)") sai với `analyze_flag.py`. Script này được viết **sau** khi đã xem số (a) và (b), nhưng **trước** khi có số (c). Rule (c) đã được ghi từ trước, nên verdict (c) không đổi.
5. **1/width là comparator phải báo.** Comparator đã đăng ký (rel_width) là comparator yếu. So với 1/width (`results/ext_revlag3_flagextra/flag_extra.md`):
   - clean T80/150: p̂ 0.730, 1/width 0.658, chênh +0.072 [+0.037, +0.107];
   - clean T40: 0.824 so với 0.808, chênh chỉ +0.015 [+0.005, +0.025].

   Trên 9 tập, CI loại 0 ở 7/9: 5 tập nghiêng về p̂, 2 tập nghiêng về 1/width (GES T40 −0.048 [−0.070, −0.026]; noise0.3 −0.023 [−0.040, −0.003]). Sau Holm(9) (`results/ext_verify3_revlag3/holm_inv_width.json`), p̂ tốt hơn ở 5/9 và 1/width tốt hơn ở 1/9 (GES T40; p Holm của noise0.3 là 0.116). Câu C-RQ4.4 phải kèm: "ở T40 gần như toàn bộ khả năng phân biệt đến từ width".
6. **L1 ở reversed-0.2 mong manh.** Cell T80 chỉ dựa trên 6 pair bất đồng trong 73 pair. Nó **không tái lập** trên run fresh: +0.026 [0.000, 0.066], Holm p 0.128, nên L1 trên fresh chỉ đạt 3/4 (`results/ext_revlag_fresh/analysis_b.md`). Câu lag cho paper chỉ được nói chắc ở reversed-0.5.
7. **Lag interval.** Percentile interval của mean lag chỉ cover 0.66–0.76. Không được báo nó như interval trung thực.
8. **Phạm vi generalisation của flag.** Flag được train và test trên cùng 20 topology D-07, chỉ khác seed. Đây là generalisation sang dữ liệu mới, không sang topology mới.
9. **Spec P3/P4.** `run_pairs.py` không đọc key `frozen_calibration`; factor lấy từ đường dẫn hard-code `ext_revlag._FROZEN`. Feature `stated` lúc đánh giá được mã hoá bằng width_key, khác cách mã hoá lúc train flag (cell kind): lệch ở 219/39123 hàng clean fresh (0.56%). Tính lại F1–F4 với mã hoá lúc train cho cùng verdict (ratio 4.32 → 4.33). Bản spec sửa bằng file mới của R3-4 **chưa hoàn tất**, theo docs/ext/revlag3.md và verifier vòng 3:
   - đã có config `experiments/configs/ext_revlag3_p4h2.json`, `experiments/ext/revlag3/run_pairs3.py`, `analyze_flag_p4h2_v2.py`, `analyze_lag_p4h2_v2.py`;
   - chưa có manifest `experiments/ext/revlag3/p4h2_spec_files.json`, và chưa có mục spec/rule xác nhận trong revlag3.md.

   Lead quyết định spec nào được khoá trước P4-H2.
