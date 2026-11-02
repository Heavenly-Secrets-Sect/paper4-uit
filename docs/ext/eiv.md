# Mở rộng `eiv`: module chịu nhiễu đo (errors-in-variables)

**Trạng thái.** Exploratory extension trên D-07 development. Code: [`src/paper4/ext_eiv.py`](../../src/paper4/ext_eiv.py). Config đánh giá: [`experiments/configs/ext_eiv_a1noise.json`](../../experiments/configs/ext_eiv_a1noise.json). Script probe: `experiments/ext/eiv/`. Log probe: `results/ext_eiv_probes/`. Không sửa file nào có sẵn.

## Vấn đề

A1 ([ket_qua_nhom_a.md](../ket_qua_nhom_a.md)) cho thấy `tolerant_v4` mất coverage khi có nhiễu đo:

- nhiễu 30% (reliability 0.77): coverage 0.77–0.89;
- nhiễu 10%: 4/6 cell đạt trên D-07, 2/6 trên held-out.

Nguyên nhân là **attenuation bias** (regression dilution). OLS trên chuỗi quan sát y = x + v kéo mọi hệ số về 0, nên C(H) bị co lại. Bootstrap resample chính fit đã bị co, nên không thấy được bias này.

## Phương pháp `tolerant_eiv`

**1. Corrected least squares** (Fuller 1987, method-of-moments errors-in-variables). Với mỗi phương trình j:

    β_j = (X_j'X_j − m·D_{X_j})⁻¹ X_j'y_j

trong đó D_{X_j} là phương sai nhiễu của từng regressor.

- Regressor có lag mang nhiễu ở thời điểm khác target, nên không cần chỉnh hiệp phương sai target–regressor.
- **Fuller-type guard:** gọi λ là nghiệm nhỏ nhất của det(X'X − λ·m·D_X) = 0. Mức correction được giới hạn ở min(1, 0.7λ), nên không hướng nào trong không gian regressor bị khuếch đại quá 1/(1 − 0.7) ≈ 3.3 lần.
- Nếu fit sau correction không stationary (companion radius ≥ 0.99), correction được giảm dần theo hệ số 0.8.

**2. Ước lượng mức nhiễu từ dữ liệu.** Method **không bao giờ đọc noise ratio thật**.

- Mô hình: D = r·diag(var(y)). Chỉ có một tham số r, là tỷ lệ phương sai quan sát do white noise gây ra (giả định *homogeneous reliability*).
- r ước lượng bằng **GMM trên các phương trình của skeleton được cho** (`parent_terms`). Nhiễu đo không tương quan chuỗi, nên với D đúng thì residual đã chỉnh của mọi phương trình trực giao với các lag sâu p+1, p+2 của các nút trong phương trình đó (instrument kiểu Durbin / Hansen–Sargent).
- Tiêu chí: tổng bình phương tương quan instrument–residual qua mọi phương trình. r là điểm cực tiểu trên lưới [0, 0.6], bước 0.01.

**3. Bootstrap toàn bộ thủ tục.**

- Shock cấu trúc lấy từ residual đã chỉnh, được biến đổi về covariance Σ_e = Cov(resid) − N(D), với N = (I − B0) D (I − B0)' + Σ_k B_k D B_k' là phần nhiễu nằm trong residual.
- Mô phỏng x* từ fit đã chỉnh, cộng white noise N(0, D) để được y*.
- **Ước lượng lại r trên y***, rồi fit lại có correction.

**4. Giữ nguyên machinery của `tolerant_v3`.**

- Khai báo thiếu cạnh: mở mọi lag. Chỉ các term của chính skeleton (kể cả cạnh cùng kỳ được repair) được chỉnh. Khối lag thêm vào được đưa vào như control, không chỉnh (xem probe 6).
- Repair cạnh cùng kỳ: dùng tương quan residual **thô**, giống v3 (xem probe 4).
- Rút chiều có nhắm mục tiêu khi khai báo đảo.
- `tolerant_eiv` nằm trong `calibrate_methods`, nên width được hiệu chỉnh theo (T, loại hỏng khai báo) trên dữ liệu **sạch** của bank D-07H development, giống hệt `tolerant_v4`.

**Ablation (có trong code, không chạy trong đánh giá vì lý do thời gian):** `plugin_eiv` là corrected LS trên skeleton như được cho, không có tolerance machinery.

## Các probe thăm dò (D-07H development, trước khi đánh giá)

Mọi probe dùng bank calibration D-07H development, seed riêng (777 / 888), không chạm vào D-07. Coverage trong các probe là **chưa hiệu chỉnh** width.

### Probe 1: extended Yule–Walker không ràng buộc (bị bỏ)

D ước lượng từ VAR(2) đầy đủ, bằng misfit của autocovariance ở lag 3–4 (`results/ext_eiv_probes/yw_common.txt`). Kết quả gần như vô dụng:

| T | Share thật 0.231 (ratio 0.3), ước lượng trung bình |
|---|---|
| 80 | 0.016 |
| 150 | 0.047 |

Lý do: VAR có 392 tham số, và nhiễu đóng vai một ridge ngầm. Bỏ D đi làm tăng variance, nên tiêu chí luôn chọn D ≈ 0.

### Probe 2: GMM trên phương trình của skeleton (được chọn)

12 topology, `results/ext_eiv_probes/gmm_*.txt`. Bảng ghi trung bình (sd) của r̂:

| Skeleton | T | share 0 | share 0.091 | share 0.231 |
|---|---|---|---|---|
| đúng | 80 | 0.035 (0.044) | 0.095 (0.058) | 0.193 (0.076) |
| đúng | 150 | 0.033 (0.028) | 0.107 (0.037) | 0.220 (0.056) |
| thiếu 20% | 80 | 0.038 | 0.100 | 0.193 |
| thiếu 20% | 150 | 0.033 | 0.097 | 0.210 |
| đảo 20% | 150 | 0.039 | 0.112 | 0.207 |
| thừa 20% | 150 | 0.032 | 0.108 | 0.192 |

- Gần không bias, và robust với skeleton hỏng.
- Nếu ước lượng trên phương trình mọi lag (`full`) thì không ổn định: ở T = 150, share 0.231, kết quả là 0.335 (sd 0.180). Vì vậy r luôn được ước lượng trên `parent_terms` của skeleton.

### Probe 3–6: thiết kế bootstrap / guard

6–8 topology, n_boot 99, chưa hiệu chỉnh.

- **Probe 3 (`p_*`, `q_*`):** chỉnh cả khối mọi lag trong cell thiếu cạnh khiến width tăng gấp đôi ngay cả trên dữ liệu sạch. Ở T = 80, width 4.68 so với 2.08 của v3.
  - Đã đổi sang chỉnh **chỉ các term của skeleton**.
- **Bias correction của r** bằng pilot bootstrap (49 draw): r gần sự thật hơn (0.217–0.223 so với 0.231 ở T = 150), nhưng IS tăng.
  - Ví dụ none, T = 150, nhiễu 0.3: IS 2.60 so với 2.00 khi không có bias correction.
  - Đã **tắt** (`v_*`).
- **Probe 4 (`diag_missing.py`):** repair dựa trên covariance shock đã chỉnh làm phồng tương quan, nên số cạnh repair tăng từ 1–2 lên 4. Với r cố định bằng 0, width bằng v3. Đã đổi về repair theo **residual thô**.
- **Probe 6, guard** (`g_*`, `h_*`). Bảng ghi coverage / IS, chưa hiệu chỉnh, 8 topology:

| Cell | v3 | guard 0.9λ | **guard 0.7λ** | guard 0.5λ | guard λ−1 |
|---|---|---|---|---|---|
| none T80 sạch | 0.908 / 1.96 | 0.926 / 2.17 | 0.930 / 2.18 | 0.923 / 2.08 | 0.919 / 2.04 |
| none T80 nhiễu 0.3 | 0.790 / 3.60 | 0.893 / 3.54 | 0.908 / 3.15 | 0.875 / 3.06 | 0.827 / 3.21 |
| none T150 nhiễu 0.3 | 0.738 / 2.99 | 0.923 / 2.00 | 0.915 / 1.92 | 0.882 / 2.03 | 0.830 / 2.43 |
| missing T80 sạch | 0.934 / 2.80 | 0.978 / 4.13 | 0.970 / 3.50 | 0.959 / 2.94 | 0.948 / 2.71 |
| missing T80 nhiễu 0.3 | 0.841 / 4.13 | 0.959 / 5.61 | 0.948 / 4.03 | 0.911 / 3.40 | 0.834 / 4.05 |
| missing T150 nhiễu 0.3 | 0.760 / 3.85 | 0.945 / 2.99 | 0.904 / 2.52 | 0.849 / 2.75 | 0.738 / 3.87 |
| reversed T80 nhiễu 0.3 | 0.760 / 4.13 | 0.856 / 3.99 | 0.871 / 3.71 | 0.841 / 3.39 | 0.827 / 3.54 |
| reversed T150 nhiễu 0.3 | 0.731 / 3.69 | 0.900 / 2.60 | 0.889 / 2.46 | 0.852 / 2.71 | 0.793 / 3.05 |

Guard 0.7λ được chọn làm thỏa hiệp. Guard 0.9λ quá đắt ở cell thiếu cạnh, còn 0.5λ và λ−1 chỉnh quá yếu khi nhiễu 0.3. Đây là hyperparameter **được chọn trên bank calibration**, không phải trên D-07.

Cũng đã thử giữ r̂ cố định trong bootstrap (không ước lượng lại). Cách này cho width lớn hơn, nên bị bỏ.

## Quy tắc ghi trước (viết TRƯỚC khi chạy `ext_eiv_a1noise`)

**Thiết lập.**

- D-07 development, seed_base 20261102: dữ liệu và skeleton trùng với `a1_latent_noise` và `a2_baselines`.
- 20 topology × 3 replicate.
- T ∈ {80, 150}.
- Cell: none, missing-0.2, reversed-0.2.
- Kịch bản: clean, noise0.1, noise0.3.
- Method: `oracle` (tham chiếu), `plugin`, `inflate`, `lp_allpast`, `tolerant_v4`, `tolerant_eiv`. n_boot 199.
- Calibration: D-07H development, block của `a3_ges` (kinds extra / missing / reversed, rates 0.2 / 0.5). `tolerant_eiv` nằm trong `calibrate_methods`.

**Quy tắc.** `tolerant_eiv` được **giữ** nếu cả hai điều kiện đều đúng:

1. **Coverage ≥ 0.90 ở mọi cell noise0.1 và noise0.3.** Tổng cộng 12 cell: 2 mức nhiễu × 2 T × 3 cell hỏng.
2. **Trên dữ liệu sạch, ở mọi cell** (6 cell: 2 T × 3 cell hỏng), interval score của `tolerant_eiv` ≤ 1.15 × interval score của `tolerant_v4`.

Nếu một điều kiện không đạt, kết luận là **loại**, kèm số cell đạt của từng điều kiện.

**Báo cáo nhưng không dùng để chấm:**

- chênh lệch interval score có ghép cặp so với `tolerant_v4` và `plugin`, kèm CI 95% clustered theo topology;
- coverage và IS của `inflate` và `lp_allpast` ở các cell nhiễu;
- sai số tuyệt đối của C(H);
- r̂ trung bình theo kịch bản, so với share thật 0, 0.091, 0.231.

**Ghi chú tái lập.** Runner cấp rng cho method extension theo thứ tự tên của *mọi* method trong `src/paper4/ext_*.py` (`rng(100 + e_idx)`). Lúc ghi quy tắc, `tolerant_eiv` có e_idx = 8 trong 12 method extension. Nếu agent khác thêm method, seed bootstrap của `tolerant_eiv` sẽ đổi khi chạy lại. Cần báo cho người giữ runner.

## Kết quả của `ext_eiv_a1noise` (D-07 development, chạy một lần)

**Nguồn số liệu:**

- `results/ext_eiv_a1noise/summary.md`
- `results/ext_eiv_a1noise/rule_check.txt`, sinh bởi `experiments/ext/eiv/check_rule.py`

6480 hàng, chạy hết 1017.7 s, khoảng 17 phút. Lâu hơn ước tính 15 phút vì máy đang chịu load average khoảng 55 từ các agent khác. Grid giữ nguyên, không giảm.

### Kết luận theo quy tắc: **LOẠI (REJECTED)**

**Điều kiện 1 không đạt: 8/12 cell.** Cả 6 cell noise0.1 đều đạt. Ở noise0.3, 4 cell hụt 0.90:

| Cell noise0.3 | Coverage `tolerant_eiv` | Coverage `tolerant_v4` |
|---|---|---|
| T80 none | **0.874** | 0.815 |
| T80 missing | 0.938 | 0.917 |
| T80 reversed | **0.885** | 0.826 |
| T150 none | **0.895** | 0.774 |
| T150 missing | 0.923 | 0.830 |
| T150 reversed | **0.893** | 0.784 |

**Điều kiện 2 đạt: 6/6 cell.** Tỷ lệ IS so với `tolerant_v4` trên dữ liệu sạch:

| T | none | missing | reversed |
|---|---|---|---|
| 80 | 1.038 | 1.098 | 1.055 |
| 150 | 1.026 | 1.106 | 1.035 |

### Bảng chính: coverage / IS

Ô in đậm là ô dưới 0.90.

| Kịch bản | T | Cell | `plugin` | `inflate` | `lp_allpast` | `tolerant_v4` | **`tolerant_eiv`** |
|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.869 / 2.78 | 0.936 / 2.50 | 0.839 / 5.70 | 0.933 / 2.50 | 0.939 / 2.60 |
| clean | 80 | missing | 0.665 / 11.06 | 0.892 / 15.47 | 0.840 / 5.78 | 0.961 / 3.27 | 0.953 / 3.59 |
| clean | 80 | reversed | 0.814 / 3.70 | 0.941 / 3.02 | 0.820 / 6.39 | 0.941 / 2.81 | 0.949 / 2.96 |
| clean | 150 | none | 0.930 / 1.58 | 0.963 / 1.57 | 0.908 / 2.66 | 0.964 / 1.56 | 0.953 / 1.60 |
| clean | 150 | missing | 0.684 / 10.55 | 0.862 / 12.95 | 0.905 / 2.73 | 0.969 / 2.04 | 0.964 / 2.26 |
| clean | 150 | reversed | 0.841 / 3.09 | 0.954 / 2.64 | 0.873 / 3.50 | 0.964 / 1.96 | 0.957 / 2.03 |
| noise0.1 | 80 | none | 0.813 / 3.55 | 0.894 / 2.97 | 0.826 / 5.87 | **0.893** / 2.95 | 0.927 / 3.00 |
| noise0.1 | 80 | missing | 0.626 / 11.61 | 0.886 / 15.45 | 0.827 / 5.87 | 0.942 / 3.47 | 0.945 / 4.20 |
| noise0.1 | 80 | reversed | 0.760 / 4.48 | 0.911 / 3.32 | 0.812 / 6.35 | 0.904 / 3.18 | 0.937 / 3.34 |
| noise0.1 | 150 | none | 0.863 / 2.12 | 0.921 / 1.90 | 0.874 / 3.10 | 0.921 / 1.89 | 0.950 / 1.81 |
| noise0.1 | 150 | missing | 0.639 / 11.15 | 0.854 / 12.98 | 0.869 / 3.17 | 0.925 / 2.44 | 0.959 / 2.47 |
| noise0.1 | 150 | reversed | 0.782 / 3.83 | 0.942 / 2.73 | 0.839 / 4.09 | 0.914 / 2.27 | 0.947 / 2.20 |
| noise0.3 | 80 | none | 0.702 / 5.44 | 0.813 / 4.17 | 0.804 / 6.61 | **0.815** / 4.10 | **0.874** / 3.85 |
| noise0.3 | 80 | missing | 0.543 / 13.08 | 0.878 / 15.38 | 0.804 / 6.62 | 0.917 / 3.90 | 0.938 / 4.33 |
| noise0.3 | 80 | reversed | 0.661 / 6.34 | 0.854 / 4.03 | 0.793 / 6.88 | **0.826** / 4.23 | **0.885** / 3.97 |
| noise0.3 | 150 | none | 0.669 / 4.28 | 0.771 / 3.40 | 0.773 / 4.41 | **0.774** / 3.37 | **0.895** / 2.47 |
| noise0.3 | 150 | missing | 0.515 / 13.10 | 0.848 / 13.09 | 0.775 / 4.41 | **0.830** / 3.52 | 0.923 / 2.96 |
| noise0.3 | 150 | reversed | 0.625 / 5.89 | 0.893 / 3.21 | 0.743 / 5.43 | **0.784** / 3.66 | **0.893** / 2.87 |

**Kiểm tra tính nhất quán với `a1_latent_noise` (cùng seed, cùng dữ liệu).**

- `plugin` và `lp_allpast` cho đúng các số cũ. Ví dụ clean T80 missing: `plugin` 0.665 / 11.06.
- `tolerant_v4` trùng ở cell none, ví dụ noise0.3 T150 none: 0.774 / 3.37.
- Ở cell missing và reversed, `tolerant_v4` và `inflate` khác nhẹ. Lý do: calibration block của `a3_ges` (bắt buộc theo hard rule) gộp rates 0.2 và 0.5 khi tune width.
  - `tolerant_v4`, clean T80 missing: 0.961 / 3.27 ở đây, 0.944 / 3.22 trong a1.
  - `inflate`, clean T80 missing: 15.47 ở đây, 16.20 trong a1.
- So sánh trong tài liệu này luôn dùng số của chính run này.

### Chênh lệch IS có ghép cặp so với `tolerant_v4`

`tolerant_eiv` trừ v4, CI 95% clustered theo topology.

| Kịch bản | T80 none | T80 missing | T80 reversed | T150 none | T150 missing | T150 reversed |
|---|---|---|---|---|---|---|
| clean | +0.10 [+0.01, +0.18] | +0.32 [+0.20, +0.45] | +0.16 [+0.09, +0.23] | +0.04 [−0.01, +0.10] | +0.22 [+0.15, +0.30] | +0.07 [+0.03, +0.12] |
| noise0.1 | +0.05 [−0.10, +0.20] | +0.73 [+0.43, +1.09] | +0.16 [+0.04, +0.28] | −0.08 [−0.17, +0.01] | +0.03 [−0.08, +0.13] | −0.07 [−0.19, +0.05] |
| noise0.3 | −0.26 [−0.51, −0.01] | +0.42 [+0.27, +0.57] | −0.25 [−0.55, +0.02] | **−0.90 [−1.12, −0.68]** | **−0.56 [−0.77, −0.36]** | **−0.79 [−1.02, −0.54]** |

So với `plugin`, `tolerant_eiv` tốt hơn ở cả 12 cell nhiễu: từ −0.30 [−0.46, −0.15] (noise0.1 T150 none) đến −10.14 [−10.94, −9.30] (noise0.3 T150 missing).

### Mức nhiễu ước lượng

r̂ trung bình (sd), gộp mọi cell. Share thật là 0 / 0.091 / 0.231.

| T | clean | noise0.1 | noise0.3 |
|---|---|---|---|
| 80 | 0.028 (0.027) | 0.072 (0.043) | **0.115** (0.057) |
| 150 | 0.023 (0.021) | 0.084 (0.037) | **0.159** (0.051) |

### Đọc kết quả

1. **Nhiễu 10% được giải quyết.** Coverage 0.927–0.959 ở cả 6 cell. v4 chỉ có 0.893–0.942, với 1 cell < 0.90 trên run này. Chi phí IS nhỏ hoặc không có ý nghĩa thống kê, trừ T80 missing (+0.73).
2. **Nhiễu 30% được cải thiện rõ nhưng chưa đủ.**
   - Coverage tăng 0.02–0.12 so với v4: 0.874–0.938 so với 0.774–0.917.
   - Ở T = 150, IS tốt hơn v4 có ý nghĩa ở cả 3 cell. Ví dụ none: 2.47 so với 3.37.
   - 4/6 cell vẫn hụt 0.90, thiếu 0.005–0.026.
   - Ở T = 150, `tolerant_eiv` là method duy nhất đạt ≥ 0.89 ở mọi cell, ngoài `inflate` ở reversed (0.893). Đáng chú ý, `oracle` chỉ còn 0.355.
3. **Nguyên nhân chính của phần hụt: r̂ bị kéo về 0 ở nhiễu lớn.** Ở noise0.3, r̂ chỉ đạt 0.115 (T80) và 0.159 (T150) so với share thật 0.231, tức correction chỉ được khoảng một nửa đến hai phần ba. Đây là bias kiểu weak-instrument: instrument là lag p+1, p+2 nên tương quan với regressor yếu, và estimator nghiêng về OLS (r = 0). Probe 2 trên D-07H (seed 777) cho r̂ cao hơn (0.193 / 0.220). Probe 3 (seed 888) đã cho 0.137–0.177. Vậy phần lạc quan của probe 2 là do biến thiên giữa các tập topology.
4. **Chi phí trên dữ liệu sạch nhỏ: IS tăng 2.6–10.6%,** cao nhất ở cell missing (+0.22 đến +0.32). Đạt ngưỡng 15% đã ghi trước. Width hiệu chỉnh trên dữ liệu sạch của `tolerant_eiv` thấp hơn của v4 (1.0–1.3 so với 1.2–1.4), vì bootstrap ước lượng lại r̂ đã tự thêm biến thiên.
5. **Giới hạn của thiết kế.** Mô hình nhiễu giả định reliability đồng nhất (D = r·var(y)). Generator A1 đúng là sinh nhiễu như vậy, nên kết quả trên là trường hợp thuận lợi về mặt cấu trúc nhiễu. Robustness với nhiễu không đồng nhất **chưa được kiểm tra**.

### Câu được phép viết

> Một hiệu chỉnh errors-in-variables với mức nhiễu ước lượng từ dữ liệu, không biết noise ratio, đưa coverage của module lên ≥ 0.93 ở nhiễu đo 10%. Ở nhiễu 30%, coverage tăng từ 0.77–0.92 lên 0.87–0.94, và interval score tốt hơn `tolerant_v4` có ý nghĩa ở T = 150. Chi phí trên dữ liệu sạch là ≤ 11% interval score. Nhưng ở nhiễu 30%, coverage danh nghĩa vẫn chưa đạt ở 4/6 cell. Nhiễu đo lớn vẫn là limitation, đã được thu hẹp nhưng chưa được loại bỏ.

### Hướng cho version sau (chưa chạy; cần quy tắc mới)

- **Sửa bias của r̂.** Bias correction bằng bootstrap (đã có trong code, `bias_correct=True`) chỉ tăng coverage khoảng 0.01 trong probe 5, nên khó bù được khoảng hụt 0.026. Ứng viên tốt hơn:
  - instrument được chọn theo độ mạnh, hoặc LIML / Fuller-k thay cho tiêu chí GMM có trọng số đơn vị;
  - Kalman-filter MLE của mô hình state-space y = x + v, với x là SVAR ràng buộc theo skeleton.
- **Calibrate width trên dữ liệu calibration có nhiễu,** ví dụ trộn reliability 1.0 / 0.9 / 0.77. Runner hiện chỉ calibrate trên dữ liệu sạch, nên việc này cần người giữ runner hỗ trợ. Không được sửa runner.
- **Kiểm tra nhiễu không đồng nhất giữa các chuỗi,** và tương tác với biến ẩn: confounder có tự tương quan có thể làm GMM nhầm thành nhiễu, hoặc ngược lại.

## Sửa sau kiểm chứng vòng 1

*Append ở vòng 2 (2026-11-02) theo mục R2-10 của [synthesis_round1.md](synthesis_round1.md). Nội dung phía trên giữ nguyên để lưu vết; các câu dưới đây thay thế những câu tương ứng ở trên. Số liệu: `results/ext_eiv2_r1fix/corrections.txt` (tính lại từ `results/ext_eiv_a1noise/runs.jsonl` bằng `experiments/ext/eiv2/r1_corrections.py`) và `results/ext_eiv2_r1fix/cap_vs_probe.txt` (chạy lại script của verifier `experiments/ext/verify_eiv/cap_vs_probe.py`, D-07H development, seed 777).*

1. **Probe 2 đã được gán sai.** Bảng "Probe 2: GMM trên phương trình của skeleton" ở trên được tính bằng `experiments/ext/eiv/noise_est.gmm_common`, một hàm **không có** admissibility cap. Estimator thực sự được đánh giá, `ext_eiv.estimate_noise_share`, đặt `crit[grid > lam] = inf` bên trong vòng lặp qua phương trình, nên r̂ bị chặn trên bởi min_j λ_j của **cả 14 phương trình**. Trên đúng dữ liệu probe 2 (share thật 0.231): estimator được đánh giá cho 0.121 (T80) và 0.175 (T150), còn `gmm_common` cho 0.193 và 0.220; r̂ nằm đúng ở cap trong 5/12 run (T80) và 3/12 run (T150). Ở share 0.091: 0.077 so với 0.095 (T80), 0.088 so với 0.107 (T150). Vì vậy câu "Gần không bias, và robust với skeleton hỏng" chỉ đúng cho `gmm_common`, không đúng cho method được đánh giá.
   - **Docstring của `src/paper4/ext_eiv.py`** có cùng lỗi: câu "A probe on the calibration bank (docs/ext/eiv.md) showed this to be close to unbiased at noise ratios 0, 0.1, 0.3 ..." mô tả `gmm_common`, không phải `estimate_noise_share` của module. File này đã được đánh giá nên **không sửa**; ghi chú ở đây thay cho việc sửa docstring.
2. **Chẩn đoán ở mục "Đọc kết quả", ý 3, bị bác.** Nguyên nhân chính khiến r̂ bị kéo về 0 ở noise 30% là cap toàn cục nói trên (0.193 → 0.121 ở T80), không phải weak instruments. Weak instruments chỉ giải thích phần còn lại (0.231 → 0.193). Câu "phần lạc quan của probe 2 là do biến thiên giữa các tập topology" cũng sai: probe 2 lạc quan vì nó chạy một estimator khác. Bản sửa cap là `tolerant_eiv2` (docs/ext/eiv2.md).
3. **"Nhiễu 10% được giải quyết (coverage ≥ 0.93)" là nói quá.** Sửa thành: coverage ≥ **0.927** (min 0.9272 ở T80 none). `tolerant_v4` vốn đã đạt ≥ 0.90 ở 5/6 cell noise0.1. `tolerant_eiv` không tốt hơn v4 có ý nghĩa ở cell noise0.1 nào, và **tệ hơn** có ý nghĩa ở T80 missing (+0.73 [+0.44, +1.10]) và T80 reversed (+0.16 [+0.03, +0.28]) (paired IS, CI clustered theo topology, B = 2000).
4. **Chi phí chưa báo cáo trên null pair.** `tolerant_eiv` làm tăng |C| ước lượng trên null pair (median `C_abs_spurious`) ở **cả 18 cell**, ví dụ noise0.3 T80 none 0.039 → 0.076 (mean 0.052 → 0.087), clean T80 missing 0.225 → 0.261.
5. **Câu được phép viết (thay câu ở trên):**

> Một hiệu chỉnh errors-in-variables với mức nhiễu ước lượng từ dữ liệu giữ coverage ≥ 0.927 ở nhiễu đo 10% (v4 đã đạt ≥ 0.90 ở 5/6 cell, nên lợi ích ở mức này nhỏ, và IS tệ hơn ở T80 missing/reversed). Ở nhiễu 30%, coverage tăng từ 0.77–0.92 lên 0.87–0.94 và interval score tốt hơn `tolerant_v4` có ý nghĩa ở cả 3 cell T = 150, nhưng tệ hơn ở T80 missing. Coverage danh nghĩa chưa đạt ở 4/6 cell noise 30%, phần lớn do một admissibility cap toàn cục trong estimator của mức nhiễu. Method cũng làm tăng |C| trên null pair ở mọi cell. Mô hình nhiễu D = r·var(y) trùng đúng generator, nên đây là trường hợp thuận lợi nhất cho method.
