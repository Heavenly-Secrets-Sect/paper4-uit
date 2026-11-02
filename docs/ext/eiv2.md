# Mở rộng `eiv2` (vòng 2, R2-5): `tolerant_eiv2`, bỏ admissibility cap toàn cục

**Trạng thái.** Exploratory extension trên D-07 development (seed_base 20261102, ghép cặp với `a2_baselines` và `ext_eiv_a1noise`). Calibration trên D-07H development (block của `a3_ges`). Không chạm P4-H1, P4-H2 hay confirmatory split nào. Không sửa file có sẵn nào.

- Code: [`src/paper4/ext_eiv2.py`](../../src/paper4/ext_eiv2.py) (module mới; `ext_eiv.py` của vòng 1 giữ nguyên).
- Config: [`experiments/configs/ext_eiv2_eval.json`](../../experiments/configs/ext_eiv2_eval.json) (run chấm rule), [`experiments/configs/ext_eiv2_hetero.json`](../../experiments/configs/ext_eiv2_hetero.json) (nhiễu không đồng nhất, mô tả).
- Script: `experiments/ext/eiv2/` (probe, driver nhiễu không đồng nhất `run_hetero.py`, `hetero.py`, script chấm rule).
- Kết quả: `results/ext_eiv2_probes/`, `results/ext_eiv2_eval/`, `results/ext_eiv2_hetero/`, `results/ext_eiv2_r1fix/`.
- Sửa doc vòng 1 (R2-10): đã append vào [eiv.md](eiv.md), mục "Sửa sau kiểm chứng vòng 1".

## Công bố quy trình: lần thử bị ngắt

Lần thử đầu của vòng 2 bị ngắt do usage limit khoảng 02:50 (giờ máy) ngày 2026-11-02. Lúc đó đã có: `src/paper4/ext_eiv2.py`, bốn script probe trong `experiments/ext/eiv2/`, và bốn file log probe trong `results/ext_eiv2_probes/`. **Chưa có** doc, config, rule hay run nào trên D-07. Lần thử này (lần 2) kiểm tra lại các file đó, giữ nguyên code của module (không đổi dòng nào), và tiếp tục từ chỗ dừng. Ở lần 2 có thêm một smoke test của driver `run_hetero.py` trên **D-07H development** (1 topology, n_boot 19, `results/ext_eiv2_smoke_d07h/`), không phải D-07.

## Vấn đề (từ kiểm chứng vòng 1)

`ext_eiv.estimate_noise_share` đặt `crit[grid > lam] = inf` bên trong vòng lặp qua phương trình. Như vậy r̂ bị chặn bởi min_j λ_j trên **cả 14 phương trình**, với λ_j là nghiệm nhỏ nhất của det(X_j'X_j − λ·m·D_j) = 0. Ở T nhỏ, chỉ một phương trình gần collinear là đủ kéo r̂ xuống: share thật 0.231, r̂ 0.121 (T80) và 0.175 (T150), r̂ chạm cap ở 5/12 và 3/12 run (`results/ext_eiv2_r1fix/cap_vs_probe.txt`). Đây là nguyên nhân chính khiến `tolerant_eiv` hụt coverage ở noise 30% (synthesis X8).

## Phương pháp `tolerant_eiv2`

**Thay đổi duy nhất so với `tolerant_eiv`** nằm ở estimator của r (D = r·diag(var(y))), `estimate_noise_share_v2`, mode `"pereq"`:

- **Cap theo từng phương trình.** Trong tiêu chí GMM, phương trình j được chỉnh với r_j = min(r, 0.7·λ_j). Đây chính là Fuller-type guard mà fit đã dùng (`ext_eiv.fit_corrected`, GUARD = 0.7). Một phương trình ill-conditioned chỉ đóng góp moment đã chỉnh một phần, chứ không còn phủ quyết cả grid.
- **Kiểm tra positive definite.** Mọi corrected Gram matrix X_j'X_j − m·r_j·D_j dùng trong tiêu chí được kiểm tra bằng Cholesky. Nếu hỏng, r_j của phương trình đó bị chia đôi cho đến khi đạt. Vì r_j ≤ 0.7·λ_j < λ_j nên về lý thuyết điều này không bao giờ xảy ra; nó là lưới an toàn. Probe 1 đếm được 0 lần sửa.
- Tiêu chí giữ nguyên vòng 1: tổng bình phương tương quan instrument–residual (instrument là lag p+1, p+2 của các nút trong phương trình), grid r ∈ [0, 0.6] bước 0.01.

Mọi phần khác giữ nguyên `tolerant_eiv`: corrected LS với guard 0.7λ, back-off khi không stationary, bootstrap toàn bộ thủ tục với r ước lượng lại trong từng draw, chỉ chỉnh các term của skeleton khi mở mọi lag, repair theo residual thô, rút chiều có nhắm mục tiêu khi khai báo đảo. Width hiệu chỉnh theo (T, loại hỏng khai báo) trên dữ liệu **sạch** của D-07H development (`calibrate_methods`). Method chỉ thấy data, public skeleton và `skel.damage`.

**Ablation `plugin_eiv2`:** corrected LS (cùng estimator của r) trên skeleton như được cho, cùng bootstrap, không có tolerance machinery, không hiệu chỉnh width. Đây là bản tương ứng của `plugin_eiv` vòng 1 với estimator mới.

Module **không** kiểm tra trùng term theo kiểu bug của `ext_narrow.opened_terms`, vì nó không dựng trên v5: `parent_terms` duyệt mỗi cặp một lần, `soft_terms` gồm lag 1..p của mọi nút cộng các term cùng kỳ (lag 0), nên không có term trùng.

## Probe thiết kế (D-07H development, trước khi ghi rule; width CHƯA hiệu chỉnh)

Mọi probe dùng bank calibration D-07H development, seed riêng (4242, 5151), không chạm D-07. Nhiễu không đồng nhất `het r`: tỷ lệ nhiễu của từng chuỗi là lưới đều trên [0, 2r] (trung bình r), hoán vị ngẫu nhiên qua các chuỗi (`experiments/ext/eiv2/hetero.py`). Share thật trung bình ở het0.3 là 0.214 (thấp hơn 0.231 vì share = r/(1+r) lõm).

### Probe 1: r̂ theo admissibility mode (`probe_rhat.py`, 20 topology, `results/ext_eiv2_probes/rhat.txt`)

Trung bình (sd) của r̂ trên skeleton đúng:

| T | Kịch bản | Share thật | global (vòng 1) | **pereq (v2)** | free (không cap) |
|---|---|---|---|---|---|
| 80 | hom0 | 0 | 0.033 (0.024) | 0.052 (0.059) | 0.044 (0.035) |
| 80 | hom0.1 | 0.091 | 0.069 (0.042) | 0.091 (0.071) | 0.123 (0.138) |
| 80 | hom0.3 | 0.231 | 0.122 (0.054) | 0.187 (0.113) | 0.251 (0.151) |
| 80 | het0.3 | 0.214 | 0.099 (0.061) | 0.126 (0.113) | 0.184 (0.127) |
| 150 | hom0 | 0 | 0.033 (0.028) | 0.035 (0.030) | 0.044 (0.049) |
| 150 | hom0.1 | 0.091 | 0.082 (0.046) | 0.093 (0.073) | 0.087 (0.056) |
| 150 | hom0.3 | 0.231 | 0.150 (0.062) | 0.219 (0.149) | 0.188 (0.112) |
| 150 | het0.3 | 0.214 | 0.104 (0.059) | 0.129 (0.081) | 0.144 (0.100) |

- Bỏ cap toàn cục loại phần lớn bias trung bình ở noise 30% đồng nhất (0.122 → 0.187 ở T80, 0.150 → 0.219 ở T150), robust với skeleton thiếu/đảo 20% (bảng đầy đủ trong file).
- Cái giá là **sd tăng gần gấp đôi** (0.05–0.06 → 0.11–0.15). RMSE so với share thật không tốt hơn (probe 1b, skeleton đúng): bằng nhau ở T80 hom0.3 (0.121), tệ hơn ở T150 hom0.3 (0.102 → 0.149) và ở hom0.1 (0.047 → 0.071 ở cả hai T).
- Ở nhiễu không đồng nhất het0.3, r̂ vẫn thấp (0.126/0.129 so với 0.214): mô hình một tham số bị sai.

### Probe 1b: LIML-type criterion (`probe_rhat2.py`, `results/ext_eiv2_probes/rhat2.txt`)

Thay tiêu chí tương quan bằng tổng u'P_Z u / u'u (dạng LIML / Anderson–Rubin) không cải thiện: pereq/liml cho r̂ 0.162 (T80) và 0.202 (T150) ở hom0.3, RMSE 0.151/0.153, so với pereq/corr 0.121/0.149. Theo synthesis, LIML/Fuller-k chỉ xét **sau** khi sửa cap; đã xét và **không dùng**.

### Probe 2: coverage / IS chưa hiệu chỉnh (`probe_cov.py`, 12 topology, n_boot 99, `cov_main.txt`, `cov_diag.txt`)

Coverage / IS / median |C| null pair ở noise 30% đồng nhất:

| T | Cell | v3 | eiv (vòng 1) | **eiv2 (cap 0.7)** | eiv2 cap 0.99 | eiv2 với share thật (chẩn đoán) |
|---|---|---|---|---|---|---|
| 80 | none | 0.707 / 5.09 / 0.030 | 0.842 / 3.94 / 0.048 | 0.850 / 3.97 / 0.047 | 0.852 / 3.56 / 0.048 | 0.919 / 3.79 / 0.069 |
| 80 | missing | 0.786 / 5.46 / 0.185 | 0.941 / 4.57 / 0.223 | 0.944 / 4.43 / 0.204 | 0.921 / 4.57 / 0.195 | 0.949 / 4.68 / 0.208 |
| 80 | reversed | 0.684 / 6.46 / 0.028 | 0.776 / 5.40 / 0.045 | 0.822 / 5.46 / 0.040 | 0.830 / 4.93 / 0.044 | 0.903 / 4.55 / 0.057 |
| 150 | none | 0.649 / 4.56 / 0.015 | 0.840 / 2.65 / 0.029 | 0.863 / 2.59 / 0.032 | 0.888 / 2.50 / 0.031 | 0.926 / 2.46 / 0.040 |
| 150 | missing | 0.743 / 4.37 / 0.127 | 0.896 / 3.21 / 0.127 | 0.878 / 3.41 / 0.127 | 0.898 / 3.18 / 0.130 | 0.921 / 3.27 / 0.142 |
| 150 | reversed | 0.603 / 5.52 / 0.017 | 0.832 / 3.16 / 0.027 | 0.832 / 3.24 / 0.027 | 0.860 / 3.18 / 0.023 | 0.908 / 2.90 / 0.043 |

(Cột "share thật" đọc share thật nên **chỉ là chẩn đoán**, không bao giờ là candidate. Cột eiv2 lấy từ `cov_main.txt`; `cov_diag.txt` chạy lại eiv2 với stream rng khác do vị trí variant, số lệch ≤ 0.01.)

Đọc probe 2:
- Chưa hiệu chỉnh, eiv2 hơn eiv vòng 1 ít và không đều: coverage +0.003 đến +0.046 ở 4/6 cell, bằng ở T150 reversed, −0.018 ở T150 missing. Phương sai lớn hơn của r̂ ăn mất phần lớn lợi ích từ bias nhỏ hơn.
- Với share thật, coverage chưa hiệu chỉnh là 0.903–0.949. Vậy phần hụt còn lại chủ yếu do sai số của r̂, không phải do phần còn lại của thủ tục.
- Cap 0.99 có coverage cao hơn cap 0.7 ở 5/6 cell hom0.3, nhưng tệ hơn ở het0.3 T80 (`cov_main.txt`). Khác biệt nằm trong mức nhiễu của 12 topology. **Giữ cap 0.7**: nó trùng guard của chính fit, nên là lựa chọn nhất quán, không phải lựa chọn tối ưu theo probe. Cap 0.99 không được đánh giá trên D-07.
- Fit guard 0.9 thay cho 0.7 (`eiv2g9`, `cov_diag.txt`) làm IS tăng rõ (ví dụ T80 missing hom0.3: 5.77 so với 4.54) mà coverage không tăng đều. Không dùng.
- Nhiễu không đồng nhất het0.3: mọi variant đều hụt 0.90 ở ít nhất 3/6 cell (eiv2 0.79–0.94), kể cả khi biết share trung bình thật (0.85–0.95, hụt ở 4/6 cell). Mô hình một tham số là giới hạn thật.

**Dự đoán (ghi trước để đối chiếu, không dùng để chấm):** sau calibration (hệ số ≥ 1.0 trên dữ liệu sạch), coverage của eiv2 ở noise 30% có thể vẫn hụt 0.90 ở 1–4 cell, đặc biệt các cell reversed. Rule có thể không đạt.

## Quy tắc ghi trước (viết TRƯỚC khi chạy `ext_eiv2_eval` và `ext_eiv2_hetero`)

Không có run nào trên D-07 trước khi đoạn này được ghi.

### Thiết lập run chấm rule: `ext_eiv2_eval`

- D-07 development, seed_base 20261102, 20 topology × 3 replicate, T ∈ {80, 150}.
- Cell: none, missing-0.2, reversed-0.2. Kịch bản: clean, noise0.1, noise0.3 (nhiễu đồng nhất của runner).
- Method: `oracle`, `plugin`, `tolerant_v4` (hệ số frozen, `frozen_calibration`), `tolerant_eiv2`, `plugin_eiv2`. n_boot 199.
- Calibration: D-07H development, block của `a3_ges`; `calibrate_methods` = [`tolerant_eiv2`].
- Runner chuẩn, `--workers 3`.
- So với vòng 1: bỏ `inflate` và `lp_allpast` để giữ run dưới khoảng 20 phút. v4 dùng hệ số frozen, nên số của v4 có thể lệch nhẹ so với bảng vòng 1 (khi đó hệ số v4 được tune lại theo block `a3_ges`). Seed bootstrap của ext method giờ cố định theo tên (`ext_seed`).

### Rule (giữ nguyên rule vòng 1 để so được)

`tolerant_eiv2` được **giữ** nếu cả hai điều kiện đều đúng:

1. **Coverage ≥ 0.90 ở cả 12 cell noise0.1 và noise0.3** (2 mức nhiễu × 2 T × 3 cell). Coverage là tỷ lệ gộp non-null pair qua các run, pair bị mất tính là không phủ (như runner).
2. **Trên dữ liệu sạch, ở cả 6 cell**, interval score trung bình của `tolerant_eiv2` ≤ 1.15 × của `tolerant_v4`.

Nếu một điều kiện không đạt: **loại**, kèm số cell đạt của từng điều kiện.

### Báo cáo multiplicity (không đổi verdict)

Bootstrap theo cụm topology, B = 2000, `default_rng(0)`, Holm ở α = 0.05:
- Điều kiện 1, qua 12 cell: số cell có coverage **lớn hơn 0.90 có ý nghĩa** (H0: cov ≤ 0.90, p một phía = tỷ lệ bootstrap cov* ≤ 0.90), và số cell **nhỏ hơn 0.90 có ý nghĩa** (p = tỷ lệ cov* ≥ 0.90).
- Điều kiện 2, qua 6 cell: số cell có tỷ lệ IS **nhỏ hơn 1.15 có ý nghĩa** (H0: ratio ≥ 1.15) và **lớn hơn 1.15 có ý nghĩa**.
- Chênh lệch IS ghép cặp `tolerant_eiv2` − `tolerant_v4` ở noise0.1 (6 cell) và noise0.3 (6 cell): p hai phía = 2·min(tỷ lệ d* ≤ 0, tỷ lệ d* ≥ 0); đếm số cell tốt hơn / tệ hơn có ý nghĩa, không chỉnh và có Holm trong từng nhóm 6 cell.

### Báo cáo thêm (không dùng để chấm)

- **IS ở noise0.1 so với v4** (yêu cầu của R2-5): bảng chênh lệch ghép cặp và CI.
- **Null pair:** median và mean của `C_abs_spurious` (|C| ước lượng trên null pair), và mean của `iscore_null_mean`, cho `tolerant_v4`, `tolerant_eiv2`, `plugin_eiv2`, ở cả 18 cell; số cell eiv2 có |C| null cao hơn v4.
- **Ablation:** `plugin_eiv2` so với `plugin` (tác dụng của riêng corrected LS) và so với `tolerant_eiv2` (tác dụng của tolerance machinery dưới nhiễu).
- r̂ trung bình (sd) theo kịch bản và T so với share 0 / 0.091 / 0.231; số phương trình bị cap tại r̂ (`info_n_eq_capped`).

### Run mô tả: `ext_eiv2_hetero` (không có verdict)

- Cùng D-07 development, seed, topology, T, cell, n_boot, calibration như trên. Chạy bằng `experiments/ext/eiv2/run_hetero.py` (runner chuẩn, chỉ thay hàm thêm nhiễu: `meas_noise` âm = nhiễu không đồng nhất với tỷ lệ trung bình |giá trị|).
- Kịch bản: noise0.3 (đồng nhất), het0.1, het0.3. Method: `plugin`, `tolerant_v4` (frozen), `tolerant_eiv` (vòng 1), `tolerant_eiv2`. `calibrate_methods` = [`tolerant_eiv`, `tolerant_eiv2`].
- Kiểm tra tái lập: các dòng `tolerant_eiv2`, `tolerant_v4`, `plugin` ở noise0.3 phải **trùng bit-for-bit** với `ext_eiv2_eval` (cùng seed, cùng hệ số calibration).
- Báo cáo:
  - coverage / IS của eiv2, eiv, v4 ở het0.1 và het0.3; số cell (trên 12) eiv2 đạt ≥ 0.90;
  - **tác dụng của việc sửa cap:** chênh lệch IS ghép cặp và chênh lệch coverage `tolerant_eiv2` − `tolerant_eiv` ở noise0.3 (6 cell), có Holm;
  - r̂ ở het0.1/het0.3 so với share trung bình thật.

### Sửa grid của run mô tả TRƯỚC khi chạy nó (ghi lúc rule run đã xong, run mô tả chưa chạy)

Run chấm rule `ext_eiv2_eval` mất 1635 s (khoảng 27 phút, load average 17–34 do các agent khác), vượt mức khoảng 20 phút. Để `ext_eiv2_hetero` không vượt nhiều hơn, **bỏ kịch bản het0.1**; chỉ còn noise0.3 và het0.3. Mọi thứ khác giữ nguyên. Thay đổi này chỉ giảm grid, không đổi phần báo cáo nào đã ghi cho noise0.3 và het0.3. Câu "số cell (trên 12) eiv2 đạt ≥ 0.90" ở het0.1+het0.3 đổi thành "trên 6" (chỉ het0.3). Lúc sửa đã thấy kết quả của `ext_eiv2_eval` (nhiễu đồng nhất) nhưng chưa có dòng nào của run mô tả.

### Ứng viên cho P4-H2

`tolerant_eiv2` chỉ là ứng viên cho run xác nhận P4-H2 nếu **rule của `ext_eiv2_eval` đạt**. Run mô tả không thay đổi điều này. Nếu rule không đạt thì không có spec P4-H2 từ hướng này.

## Kết quả `ext_eiv2_eval` (D-07 development, chạy một lần)

**Nguồn:** `results/ext_eiv2_eval/summary.md`, `results/ext_eiv2_eval/rule_check.txt` (sinh bởi `experiments/ext/eiv2/check_rule.py`), `results/ext_eiv2_eval/calibration.json`. Rule ghi lúc 09:27:25 (giờ máy), run bắt đầu 09:27:32 và kết thúc 09:54:48 (`experiments/ext/eiv2/eval_start.log`). 5400 dòng, 1635.3 s, cả 5 method ok 1080/1080. Thời gian vượt mức khoảng 20 phút vì load average 17–34; grid không bị giảm giữa chừng.

Hệ số width của `tolerant_eiv2` (D-07H development, dữ liệu sạch): 80: none 1.2, missing 1.0, reversed 1.2; 150: none 1.2, missing 1.1, reversed 1.2.

### Kết luận theo quy tắc: **LOẠI (REJECTED)**

- **Điều kiện 1: 11/12 cell.** Cell hụt duy nhất: noise0.3 T80 reversed, coverage **0.897** (thiếu 0.003).
  - Multiplicity (Holm qua 12 cell, bootstrap theo cụm topology): 7/12 cell lớn hơn 0.90 có ý nghĩa; **0/12 cell nhỏ hơn 0.90 có ý nghĩa**. Cell hụt có p(cov ≥ 0.90) = 0.41, tức là việc hụt nằm ở mức nhiễu. Không có Holm: 9/12 lớn hơn có ý nghĩa, 0/12 nhỏ hơn.
- **Điều kiện 2: 6/6 cell.** Tỷ lệ IS so với v4 trên dữ liệu sạch 1.051–1.118. Holm qua 6 cell: 6/6 nhỏ hơn 1.15 có ý nghĩa.

Theo rule, verdict là loại, và **không có spec P4-H2** từ hướng này (rule không được nới sau khi thấy kết quả).

### Bảng chính: coverage / IS

| Kịch bản | T | Cell | `plugin` | `tolerant_v4` | **`tolerant_eiv2`** | `plugin_eiv2` | `tolerant_eiv` vòng 1 (tham khảo, seed cũ) |
|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.869 / 2.78 | 0.933 / 2.50 | 0.943 / 2.71 | 0.905 / 2.75 | 0.939 / 2.60 |
| clean | 80 | missing | 0.665 / 11.06 | 0.961 / 3.27 | 0.958 / 3.66 | 0.696 / 10.50 | 0.953 / 3.59 |
| clean | 80 | reversed | 0.814 / 3.70 | 0.941 / 2.81 | 0.945 / 2.95 | 0.858 / 3.72 | 0.949 / 2.96 |
| clean | 150 | none | 0.930 / 1.58 | 0.964 / 1.56 | 0.970 / 1.67 | 0.935 / 1.65 | 0.953 / 1.60 |
| clean | 150 | missing | 0.684 / 10.55 | 0.969 / 2.04 | 0.969 / 2.27 | 0.698 / 10.35 | 0.964 / 2.26 |
| clean | 150 | reversed | 0.841 / 3.09 | 0.964 / 1.96 | 0.959 / 2.08 | 0.858 / 3.16 | 0.957 / 2.03 |
| noise0.1 | 80 | none | 0.813 / 3.55 | 0.893 / 2.95 | 0.934 / 3.11 | 0.896 / 3.12 | 0.927 / 3.00 |
| noise0.1 | 80 | missing | 0.626 / 11.61 | 0.942 / 3.47 | 0.948 / 4.35 | 0.703 / 10.40 | 0.945 / 4.20 |
| noise0.1 | 80 | reversed | 0.760 / 4.48 | 0.904 / 3.18 | 0.924 / 3.46 | 0.859 / 3.94 | 0.937 / 3.34 |
| noise0.1 | 150 | none | 0.863 / 2.12 | 0.921 / 1.89 | 0.970 / 1.91 | 0.935 / 1.84 | 0.950 / 1.81 |
| noise0.1 | 150 | missing | 0.639 / 11.15 | 0.925 / 2.44 | 0.957 / 2.52 | 0.705 / 10.34 | 0.959 / 2.47 |
| noise0.1 | 150 | reversed | 0.782 / 3.83 | 0.914 / 2.27 | 0.949 / 2.22 | 0.857 / 3.12 | 0.947 / 2.20 |
| noise0.3 | 80 | none | 0.702 / 5.44 | 0.815 / 4.10 | 0.905 / 3.84 | 0.851 / 4.14 | 0.874 / 3.85 |
| noise0.3 | 80 | missing | 0.543 / 13.08 | 0.917 / 3.90 | 0.936 / 4.35 | 0.688 / 10.85 | 0.938 / 4.33 |
| noise0.3 | 80 | reversed | 0.661 / 6.34 | 0.826 / 4.23 | **0.897** / 4.01 | 0.821 / 4.67 | 0.885 / 3.97 |
| noise0.3 | 150 | none | 0.669 / 4.28 | 0.774 / 3.37 | 0.933 / 2.42 | 0.891 / 2.52 | 0.895 / 2.47 |
| noise0.3 | 150 | missing | 0.515 / 13.10 | 0.830 / 3.52 | 0.919 / 3.09 | 0.677 / 10.74 | 0.923 / 2.96 |
| noise0.3 | 150 | reversed | 0.625 / 5.89 | 0.784 / 3.66 | 0.909 / 2.80 | 0.828 / 3.70 | 0.893 / 2.87 |

Cột vòng 1 lấy từ `results/ext_eiv_a1noise/rule_check.txt`. Cùng dữ liệu và skeleton, nhưng seed bootstrap và hệ số width khác, nên **không ghép cặp**. So sánh ghép cặp eiv2 với eiv vòng 1 nằm ở run mô tả bên dưới. `oracle`, `plugin` và `tolerant_v4` trùng số vòng 1 ở 18/18 cell (`results/ext_eiv2_eval/match_round1.txt`): hệ số frozen của v4 trùng hệ số đã dùng ở vòng 1 tại T80/150.

### Chênh lệch IS ghép cặp `tolerant_eiv2` − `tolerant_v4` (CI 95% clustered theo topology)

| Kịch bản | T80 none | T80 missing | T80 reversed | T150 none | T150 missing | T150 reversed |
|---|---|---|---|---|---|---|
| clean | +0.21 [+0.11, +0.32] | +0.39 [+0.30, +0.48] | +0.14 [+0.08, +0.22] | +0.10 [+0.04, +0.16] | +0.23 [+0.17, +0.28] | +0.12 [+0.05, +0.19] |
| noise0.1 | +0.15 [−0.00, +0.30] | **+0.88 [+0.58, +1.27]** | +0.28 [+0.11, +0.44] | +0.03 [−0.10, +0.13] | +0.08 [−0.03, +0.19] | −0.04 [−0.15, +0.06] |
| noise0.3 | −0.26 [−0.64, +0.08] | +0.45 [+0.27, +0.62] | −0.22 [−0.54, +0.09] | **−0.94 [−1.20, −0.69]** | **−0.43 [−0.69, −0.18]** | **−0.86 [−1.13, −0.59]** |

- **IS ở noise0.1 so với v4 (yêu cầu R2-5):** eiv2 không tốt hơn v4 ở cell nào (0/6), tệ hơn có ý nghĩa ở 2/6 (T80 missing +0.88, T80 reversed +0.28); cả hai vẫn có ý nghĩa sau Holm. Ở noise0.1 v4 đã đạt ≥ 0.90 ở 5/6 cell (0.893 ở T80 none).
- noise0.3: tốt hơn có ý nghĩa ở 3/6 (cả ba cell T150; Holm 3/6), tệ hơn ở 1/6 (T80 missing; Holm 1/6).
- Clean: tệ hơn ở 6/6 (Holm 6/6), +0.10 đến +0.39, trong ngưỡng 15%.

### Null pair (`C_abs_spurious` và `iscore_null_mean`)

Median |C| trên null pair của eiv2 **cao hơn v4 ở 18/18 cell**. Ví dụ noise0.3 T80 none 0.039 → 0.080, noise0.3 T150 none 0.032 → 0.057, clean T80 missing 0.225 → 0.254. IS trên null pair cũng tăng ở mọi cell (ví dụ noise0.3 T80 none 0.663 → 1.128). Phần lớn tăng đến từ chính corrected LS: `plugin_eiv2` có |C| null bằng đúng eiv2 ở cell none (cùng điểm ước lượng). Đây là cái giá của việc bỏ attenuation: hệ số giả cũng được khuếch đại.

### Ablation `plugin_eiv2`

- So với `plugin`: tốt hơn có ý nghĩa ở 6/6 cell noise0.1 và 6/6 cell noise0.3 (Holm), từ −0.27 đến −2.36. Trên dữ liệu sạch: tốt hơn ở 2 cell missing, tệ hơn nhẹ ở T150 none (+0.07). Corrected LS một mình đã sửa phần lớn attenuation ở cell none: coverage noise0.3 T150 none 0.669 → 0.891.
- So với `tolerant_eiv2`: tolerance machinery vẫn cần cho skeleton hỏng (missing −6.05 đến −8.08, reversed −0.48 đến −1.08, mọi kịch bản). Ở cell none, hai method gần như trùng điểm ước lượng; khác biệt chỉ do width calibration.

### r̂ của `tolerant_eiv2`

| Kịch bản | Share thật | T80: r̂ mean (sd) | T150: r̂ mean (sd) | Số phương trình bị cap tại r̂ (T80 / T150) |
|---|---|---|---|---|
| clean | 0 | 0.034 (0.046) | 0.025 (0.026) | 1.05 / 0.27 |
| noise0.1 | 0.091 | 0.099 (0.082) | 0.094 (0.054) | 2.83 / 1.64 |
| noise0.3 | 0.231 | 0.193 (0.140) | 0.206 (0.100) | 5.36 / 4.85 |

Vòng 1 cho 0.115 (T80) và 0.159 (T150) ở noise0.3. Bỏ cap toàn cục đã loại phần lớn bias trung bình, như probe 1 dự đoán. Không có lần sửa PD nào (0 trên mọi run).

### Đọc kết quả

1. **Sửa cap có tác dụng đúng hướng.** So với vòng 1 (không ghép cặp), coverage ở noise0.3 tăng ở 4/6 cell: T80 none 0.874 → 0.905, T150 none 0.895 → 0.933, T150 reversed 0.893 → 0.909, T80 reversed 0.885 → 0.897; giảm nhẹ ở hai cell missing (0.938 → 0.936, 0.923 → 0.919). Ba trong bốn cell vòng 1 hụt giờ đạt.
2. **Rule vẫn không đạt, nhưng chỉ ở mức nhiễu.** Cell T80 reversed hụt 0.003, và Holm không xác nhận cell nào dưới 0.90. Đây là trường hợp giống v5 ở vòng 1: verdict máy móc là loại, bằng chứng không cho thấy hỏng thật. Rule đã ghi trước, nên verdict giữ là **loại**.
3. **Chi phí không đổi so với vòng 1:** IS tệ hơn v4 ở T80 missing ở mọi mức nhiễu (+0.39 clean, +0.88 noise0.1, +0.45 noise0.3), và |C| trên null pair tăng ở mọi cell.
4. **Lợi ích chỉ rõ ở noise 30% và T = 150.** Ở noise 10%, eiv2 không có lợi thế về IS so với v4, chỉ tăng coverage (v4 hụt nhẹ ở T80 none, 0.893).

## Kết quả run mô tả `ext_eiv2_hetero` (D-07 development, không có verdict)

**Nguồn:** `results/ext_eiv2_hetero/summary.md`, `results/ext_eiv2_hetero/describe.txt` (sinh bởi `experiments/ext/eiv2/describe_hetero.py`), `results/ext_eiv2_hetero/calibration.json`. Chạy 09:55:41–10:13:06 (`experiments/ext/eiv2/hetero_start.log`), 2880 dòng, 1040 s, mọi method ok 720/720. Grid đã giảm trước khi chạy (bỏ het0.1, xem trên).

**Tái lập:** cả 1080 dòng noise0.3 dùng chung với `ext_eiv2_eval` (plugin, v4, eiv2) **trùng hoàn toàn**. Hệ số calibration của eiv2 cũng trùng. Driver `run_hetero.py` không làm đổi gì ở nhiễu đồng nhất.

### Coverage / IS

| Kịch bản | T | Cell | `plugin` | `tolerant_v4` | `tolerant_eiv` (vòng 1, seed mới) | **`tolerant_eiv2`** |
|---|---|---|---|---|---|---|
| noise0.3 | 80 | none | 0.702 / 5.44 | 0.815 / 4.10 | 0.875 / 3.85 | 0.905 / 3.84 |
| noise0.3 | 80 | missing | 0.543 / 13.08 | 0.917 / 3.90 | 0.939 / 4.39 | 0.936 / 4.35 |
| noise0.3 | 80 | reversed | 0.661 / 6.34 | 0.826 / 4.23 | 0.889 / 3.96 | 0.897 / 4.01 |
| noise0.3 | 150 | none | 0.669 / 4.28 | 0.774 / 3.37 | 0.898 / 2.48 | 0.933 / 2.42 |
| noise0.3 | 150 | missing | 0.515 / 13.10 | 0.830 / 3.52 | 0.931 / 2.94 | 0.919 / 3.09 |
| noise0.3 | 150 | reversed | 0.625 / 5.89 | 0.784 / 3.66 | 0.897 / 2.84 | 0.909 / 2.80 |
| het0.3 | 80 | none | 0.694 / 5.40 | 0.810 / 4.04 | 0.866 / 3.95 | 0.889 / 3.84 |
| het0.3 | 80 | missing | 0.540 / 13.20 | 0.887 / 4.16 | 0.919 / 4.38 | 0.926 / 4.47 |
| het0.3 | 80 | reversed | 0.654 / 6.48 | 0.830 / 4.17 | 0.882 / 4.02 | 0.882 / 4.04 |
| het0.3 | 150 | none | 0.669 / 4.40 | 0.766 / 3.55 | 0.839 / 3.01 | 0.881 / 2.84 |
| het0.3 | 150 | missing | 0.507 / 13.11 | 0.823 / 3.54 | 0.897 / 3.13 | 0.900 / 3.17 |
| het0.3 | 150 | reversed | 0.607 / 6.11 | 0.770 / 3.81 | 0.859 / 3.19 | 0.878 / 3.25 |

### Tác dụng của việc sửa cap (ghép cặp eiv2 − eiv vòng 1, cùng run)

- **Coverage ở noise0.3:** tăng có ý nghĩa ở 2/6 cell (Holm 2/6): T80 none +0.030 [+0.014, +0.047], T150 none +0.036 [+0.020, +0.055]. Hai cell reversed +0.008 và +0.012 (CI chứa 0). Hai cell missing −0.002 và −0.013 (CI chứa 0).
- **IS ở noise0.3:** không khác có ý nghĩa ở cell nào (0/6, cả không chỉnh lẫn Holm), từ −0.06 đến +0.15.
- **IS ở het0.3:** tốt hơn có ý nghĩa ở 1/6 (T150 none −0.17 [−0.25, −0.09], Holm 1/6), còn lại CI chứa 0.
- Với seed mới, `tolerant_eiv` vòng 1 vẫn hụt 0.90 ở 4/6 cell noise0.3 (0.875, 0.889, 0.898, 0.897), giống vòng 1. eiv2 chỉ hụt 1/6.
- r̂ ở noise0.3: eiv 0.115 / 0.159 so với eiv2 0.193 / 0.206 (T80 / T150), share thật 0.231.

### Nhiễu không đồng nhất het0.3 (share trung bình thật 0.214)

- Coverage ≥ 0.90: **eiv2 2/6**, eiv 1/6, v4 0/6. eiv2 đạt 0.878–0.926. Hụt ở cả hai cell none và hai cell reversed.
- So với v4, eiv2 vẫn tốt hơn có ý nghĩa về IS ở cả ba cell T150 (−0.71, −0.37, −0.56; Holm 3/6) và tệ hơn ở T80 missing (+0.30; Holm 1/6). Giống mẫu hình ở nhiễu đồng nhất.
- r̂ chỉ đạt 0.150 (T80) và 0.134 (T150): mô hình một tham số D = r·var(y) gom các chuỗi nhiễu nhiều và nhiễu ít lại, nên chuỗi nhiễu nhiều bị chỉnh thiếu.
- Null pair: median |C| của eiv2 cao hơn v4 ở cả 6 cell het0.3 (ví dụ T80 none 0.035 → 0.067).

## Kết luận vòng 2 cho hướng eiv

1. **Verdict theo rule ghi trước: LOẠI** (điều kiện 1 đạt 11/12, điều kiện 2 đạt 6/6). Cell hụt là noise0.3 T80 reversed, 0.897. Holm không xác nhận cell nào dưới 0.90 có ý nghĩa, nên đây là thất bại ở mức nhiễu. Rule vẫn giữ nguyên, không nới.
2. **Chẩn đoán của verifier được xác nhận:** bỏ cap toàn cục đưa r̂ ở noise 30% từ 0.115/0.159 lên 0.193/0.206 (share thật 0.231), và số cell noise0.3 hụt giảm từ 4 xuống 1 (cùng run, cùng seed mới). Lợi ích ghép cặp chỉ có ý nghĩa ở coverage của hai cell none. IS không đổi có ý nghĩa.
3. **Giới hạn còn lại:**
   - sd của r̂ gần gấp đôi so với vòng 1;
   - IS tệ hơn v4 ở T80 missing ở mọi mức nhiễu;
   - |C| trên null pair cao hơn v4 ở mọi cell (18/18 nhiễu đồng nhất, 6/6 het0.3);
   - ở noise 10%, eiv2 không có lợi thế IS nào so với v4 (0/6 tốt hơn, 2/6 tệ hơn);
   - với nhiễu không đồng nhất, mô hình một tham số chỉ đạt 2/6 cell.
4. **Câu được phép viết (exploratory, D-07 development):**

> Một hiệu chỉnh errors-in-variables, với mức nhiễu ước lượng từ dữ liệu bằng GMM có cap theo từng phương trình, giữ coverage ≥ 0.90 ở 11/12 cell nhiễu đo 10% và 30% (min 0.897; không cell nào dưới 0.90 có ý nghĩa sau Holm). Chi phí trên dữ liệu sạch là 5–12% interval score so với `tolerant_v4`. Ở nhiễu 30% và T = 150, interval score tốt hơn `tolerant_v4` có ý nghĩa ở cả ba cell. Ở T = 80, method tệ hơn ở cell thiếu cạnh, và nó làm tăng |C| ước lượng trên null pair. Khi tỷ lệ nhiễu khác nhau giữa các chuỗi (trung bình 30%), coverage còn 0.878–0.926. Rule ghi trước (12/12) không đạt, nên đây chưa phải module of record.

5. **Không có spec P4-H2.** Theo mục "Ứng viên cho P4-H2" ghi trước, `tolerant_eiv2` không phải ứng viên vì rule không đạt. Nếu nhóm muốn thử lại, đó phải là một version mới với rule mới. Ví dụ: per-series noise share (mô hình nhiều tham số có shrinkage về r chung) cho nhiễu không đồng nhất, hoặc width calibration trên dữ liệu calibration có nhiễu. Việc thứ hai cần người giữ runner hỗ trợ. Không version nào trong số đó đã được chạy.

## Ghi chú cho người giữ repo

- Không phát hiện bug mới trong file có sẵn. Lưu ý: `src/paper4/ext_eiv2.py` import các hàm từ `ext_eiv.py` (GUARD, fit_stationary, ...). Nếu ai sửa `ext_eiv.py`, số của eiv2 sẽ đổi theo; hai file nên được coi là đã đóng băng cùng nhau.
- `experiments/ext/eiv2/run_hetero.py` thay `add_measurement_noise` bên trong module runner lúc import (kể cả trong worker spawn). Đây là cách duy nhất để thêm kịch bản mà không sửa runner. Nếu runner sau này hỗ trợ nhiễu theo từng chuỗi, nên chuyển sang key config chính thức.
- `results/ext_eiv2_smoke_d07h/` là smoke test của driver trên D-07H (1 topology, n_boot 19), không phải kết quả.

## Sửa sau kiểm chứng vòng 2

(Append bởi verifier `v4cverify` theo R3-6 của docs/ext/synthesis_round2.md. Không sửa phần nào phía trên; các mục dưới đây thay thế câu chữ tương ứng. Số kiểm lại nằm ở `results/ext_v4cverify_recompute/r36_checks.txt` và `results/ext_verify2_eiv2/`.)

1. **Câu "11/12" phải luôn kèm con số Holm.** Điều kiện 1 đạt 11/12 theo point estimate, nhưng chỉ **7/12 cell có coverage lớn hơn 0.90 có ý nghĩa sau Holm** (α = 0.05, bootstrap theo topology), và ở noise0.3 chỉ **2/6** (T80 missing, T150 none). Tôi tính lại bằng code riêng: 7/12 ở seed 0 (seed đã ghi trước), 1, 3, 4 và 8/12 ở seed 2; 0/12 cell nhỏ hơn 0.90 có ý nghĩa ở mọi seed. Với 20 cluster, CI 95% của cell hụt (noise0.3 T80 reversed) là [0.871, 0.924]. "Không bác được" **không** có nghĩa là đạt. Các cụm "hụt ở mức nhiễu" và "không có thất bại thật" ở mục "Đọc kết quả" và "Kết luận vòng 2" phải đọc theo nghĩa này. Câu được phép viết (mục 4 của "Kết luận vòng 2") sửa thành: "... giữ coverage ≥ 0.90 ở 11/12 cell nhiễu đo 10% và 30% theo point estimate (min 0.897); chỉ 7/12 cell (2/6 ở nhiễu 30%) lớn hơn 0.90 có ý nghĩa sau Holm, và không cell nào nhỏ hơn 0.90 có ý nghĩa ...".
2. **"Tác dụng của việc sửa cap" bị lẫn với width.** So sánh eiv2 với eiv (cùng run `ext_eiv2_hetero`) khác nhau ở ba thứ: estimator của r, bootstrap stream (`ext_seed` theo tên), và width factor ở 2/6 cell noise0.3 (T80 reversed: eiv 1.3, eiv2 1.2; T150 none: eiv 1.1, eiv2 1.2). Ở hai cell có coverage tăng có ý nghĩa (T80 none, T150 none), interval của eiv2 rộng hơn 15.6% và 18.4% (`results/ext_verify2_eiv2/confound.txt`). Ở T150 none, riêng tỷ lệ factor 1.2/1.1 = 1.091 đã giải thích khoảng 9.1 trong 18.4 điểm phần trăm rộng thêm (width/factor ratio còn 1.085). IS khác biệt ở 0/6 cell. Câu đúng: lợi ích coverage của việc sửa cap chủ yếu được mua bằng width, chưa phải bằng chứng rằng bản thân estimator mới tốt hơn.
3. **Spread do rng của probe 2.** Câu "số lệch ≤ 0.01" (giữa `cov_main.txt` và `cov_diag.txt`) sai. Coverage lệch tới **0.023** (T150 het0.3 none), lệch > 0.01 ở 10/24 cell, IS lệch tới 0.29 (`results/ext_verify2_eiv2/probe_rng_diff.txt`).
4. **RMSE của probe 1b.** Câu "hom0.1 (0.047 → 0.071 ở cả hai T)" sửa thành: hom0.1 skeleton đúng, T80 0.047 → 0.071, **T150 0.047 → 0.073** (`results/ext_eiv2_probes/rhat2.txt`).
5. **Một timing run chưa công bố trên D-07H.** Ngoài smoke test `results/ext_eiv2_smoke_d07h/`, transcript của lần 2 còn có một timing run (script `timing.py` trong scratchpad, khoảng 09:23 giờ máy): 1 topology D-07H development, noise 0.3, n_boot 199, so sánh v3/eiv/eiv2. Run này nằm trên bank được phép và trước khi ghi rule, không có số nào của nó được trích trong doc. Công bố ở đây cho đủ.
