# Enhanced v2: Báo cáo kiểm định thực nghiệm trên ngân hàng D-07 (40 DAGs)

- **Issue:** #91 (audit claim PR #89, sửa cơ chế fail-closed, gate nghiệm thu trước claim)
- **Protocol:** `docs/enhanced_v2_protocol_claim_map.md` — D-01 .. D-08 và sửa đổi A-91 (mục 7)
- **Tập dữ liệu:** bank D-07, `d07_manifest.json`, canonical SHA-256 `23fdaee452b1f952d9274b95795c6e4e207af29e66edb02982a82017fe5b24df`
- **Simulator:** linear-Gaussian SEM, 14 node / 21 cạnh, $T = 150$, `noise_scale = 1.0`, `penalty_discount = 1.0`
- **So sánh ghép cặp:** Enhanced v2 so với Standard v2 (comparator chính); Plain GES là baseline phụ
- **Quy ước dấu:** benefit convention — $\Delta_{\text{F1}} = \text{F1}_{\text{Enh}} - \text{F1}_{\text{Std}}$, $\Delta_{\text{SHD}} = \text{SHD}_{\text{Std}} - \text{SHD}_{\text{Enh}}$; $\Delta > 0$ có lợi cho Enhanced. F1 là arrowhead F1.

---

## 1. Tóm tắt

| Hạng mục | Kết quả |
|---|---|
| Claim superiority của PR #89 | **Thu hồi.** Median paired $\Delta$ của PR #89 bằng 0 trên cả F1 và SHD (CI [0, 0]); cải thiện mean đến từ 12/40 DAG. |
| Phạm trù claim hiện hành | Cải thiện orientation và SHD tổng thể có điều kiện trên skeleton chung với Standard v2, stratum Benign ($\rho_{\text{directed}} \le 0.20$), trong simulator ở trên (claim map 7.2). Không có claim skeleton. |
| Sửa cơ chế (AC-03, AC-04) | Soft score margin cho data arrow bị prior phản đối; tách local abstention khỏi global fallback; mẫu số conflict rate là mọi adjacency có hướng prior. |
| Gate nghiệm thu pre-registered (confirmatory, seed mới, $R = 5$) | **`CLAIM_UNLOCKED`** — superiority đạt ở cả $\rho \in \{0.0, 0.1, 0.2\}$; non-inferiority đạt ở cả $\rho \in \{0.5, 0.7, 1.0\}$; fallback tại $\rho = 0$ là 15/100 cell. |
| Giới hạn chính | Topology confirmatory đã bị lộ trước gate (PR #89 và audit #91). Seed mới chỉ chống leakage ở mức dữ liệu. Xem mục 6. |

---

## 2. Audit claim PR #89

Số liệu tái hiện bằng code PR #89 (HEAD `97c5d24`), toàn bank 40 DAG, $\rho = 0$, seed gốc:

| Chỉ số | Giá trị đo | Claim PR #89 | Đánh giá |
|---|---|---|---|
| Median paired $\Delta_{\text{F1}}$ (95% CI) | 0.0000 [0.0000, 0.0000] | "vượt trội cấu trúc" | Không đạt D-06 |
| Median paired $\Delta_{\text{SHD}}$ (95% CI) | 0.0 [0.0, 0.0] | "vượt trội cấu trúc" | Không đạt D-06 |
| Win / Tie / Loss | 12 / 28 / 0 | "tỷ lệ thua 0% tuyệt đối" | 0 loss chủ yếu do 28/40 DAG fallback về Standard v2 (output trùng comparator) |
| Fallback | 28/40 (ER 14/20, Hub 14/20) | không báo ở bảng $\rho = 0$ | Mechanism fail-closed kích hoạt trên 70% bank dù prior đúng 100% |
| Confirmatory: cận CI được báo | cận **trên** $\Delta_{\text{F1}}$ = +0.1086 | trình bày như bằng chứng | Cận trên không mang thông tin cho superiority; cận dưới là 0.0 |
| $\rho = 0.7$: 40/40 fallback, 0 loss | — | "miễn nhiễm rủi ro, an toàn tuyệt đối" | Output trùng Standard v2 ở mọi cell: tính chất của cầu dao ngắt, không phải khả năng phân biệt thích ứng |

Các mục khác của báo cáo PR #89 không còn áp dụng cho code sau #91 và đã bị loại khỏi báo cáo này: bảng Meek cascade kèm diễn giải "giải thích tại sao" (chỉ là tương quan mô tả trên 20 DAG mỗi profile, không phải bằng chứng cơ chế), và bảng runtime (chưa đo lại cho code #91).

---

## 3. Root cause đã xác minh

Diagnostic per-DAG trên code PR #89, $\rho = 0$, toàn bank:

1. **Nguồn conflict.** Có 188 data arrow của Standard v2 bị prior phản đối; **188/188 ngược với generator truth**. Ở $\rho = 0$ prior trùng truth, nên toàn bộ "prior conflict" thực chất là lỗi định hướng của data (GES ở $T = 150$), bị quy kết thành mâu thuẫn của prior do quy tắc ưu tiên tuyệt đối data arrow (`enhanced_prior_ges_v2.py`, vòng kiểm tra data arrow trước PR này).
2. **Mẫu số conflict rate.** Mẫu số cũ là `n_oriented + n_conflicts`. Nhiều graph chỉ còn 1–3 line để orient, nên vài data arrow sai đủ đẩy rate vượt 0.40.
3. **Không đặc thù cho Hub.** Fallback bằng nhau giữa hai profile (ER 14/20, Hub 14/20). Mô tả "v-structure giả trên cấu trúc Hub" trong Issue #91 mục 2.2 không được dữ liệu hỗ trợ như một cơ chế riêng của Hub; hiện tượng xảy ra trên cả hai profile.

Phân phối local BIC margin của data arrow (chỉ đo trên **development split**, dùng parent set của consistent extension): arrow ngược truth có median margin 6.46, arrow đúng truth có median 25.75. Với ngưỡng margin 0.64 ($= 0.8 \times 0.8$, từ `orientation_weight` và confidence prior sẵn có), 32% arrow ngược truth và 14% arrow đúng truth rơi dưới ngưỡng. Margin phân biệt được một phần, không tách biệt hoàn toàn; do đó override có thể gây hại khi prior sai, và được kiểm soát bởi global fallback cùng gate non-inferiority.

---

## 4. Thay đổi và kết quả

### 4.1. Thay đổi cơ chế (`enhanced_prior_ges_v2.py`)

| AC | Trước | Sau |
|---|---|---|
| AC-03 | Data arrow bị prior phản đối luôn thắng và luôn tính 1 conflict. | Tính local BIC margin giữ arrow so với đảo arrow. Nếu margin $\ge$ `orientation_weight` × chênh lệch confidence prior: giữ data, tính 1 conflict (local). Nếu nhỏ hơn: nhận hướng prior khi graph vẫn acyclic, có consistent extension và không phát sinh unshielded collider mới; ngược lại giữ data và tính conflict. Đếm ở `n_data_arrows_overridden`. |
| AC-04 | Fallback khi `conflicts / (oriented + conflicts) > max_conflict_rate` và `oriented + conflicts >= 2`. | Conflict xử lý per edge. Global fallback chỉ khi `n_conflicts >= n_min_conflicts` (mặc định 3) **và** `n_conflicts / n_prior_evaluable > max_conflict_rate`; `n_prior_evaluable` là số adjacency của Standard v2 có hướng prior. |

Không có tham số nào được tune trong #91: `orientation_weight = 0.8`, `score_margin_gate = 0.05`, `max_conflict_rate = 0.40` kế thừa harness PR #89; `n_min_conflicts = 3` lấy từ Issue #91 AC-04.

### 4.2. Before / After — toàn bank, seed gốc, $R = 1$ (exploratory, mô tả)

Bảng này dùng dữ liệu đã được xem trước, chỉ để đối chiếu với PR #89; không dùng để claim.

| $\rho = 0$ | Mean F1 Std / Enh | Mean SHD Std / Enh | Median $\Delta_{\text{F1}}$ [95% CI] | Median $\Delta_{\text{SHD}}$ [95% CI] | W / T / L | Fallback |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Trước (PR #89) | 0.5551 / 0.6083 | 15.93 / 14.22 | 0.0000 [0.0000, 0.0000] | 0.0 [0.0, 0.0] | 12 / 28 / 0 | 28/40 |
| Sau (#91) | 0.5551 / 0.6432 | 15.93 / 13.10 | 0.0768 [0.0308, 0.0909] | 2.0 [1.0, 3.0] | 30 / 10 / 0 | 6/40 |

Phần lớn mức giảm fallback đến từ AC-04 (mẫu số và điều kiện tối thiểu); AC-03 override 9 data arrow trên 40 DAG ở $\rho = 0$.

Ở $\rho = 0.7$ (corruption đếm đúng số cạnh, khác cách Bernoulli của PR #89 nên không so trực tiếp): fallback 28/40, W / T / L = 7 / 32 / 1, median $\Delta$ = 0 trên cả hai metric, 7 data arrow bị override bởi prior sai.

### 4.3. Gate nghiệm thu pre-registered — confirmatory, seed base mới

Cấu hình: split `confirmatory` (20 topology), $R = 5$ replicate mỗi topology (100 cell mỗi mức $\rho$), data seed base `20271000` (chưa từng dùng), cluster bootstrap theo topology 1000 resample. Quy tắc gate khóa tại claim map 7.3 trước khi chạy.

Danh tính code tại thời điểm chạy gate (base HEAD `97c5d24` + working tree #91):

- `enhanced_prior_ges_v2.py`: SHA-256 `022cc5c192962fbce874ade6809576edcd7554e42d0dcb4ff18ff0f2655a91ad`
- `evaluate_d07_bank.py`: SHA-256 `eafdf4fb3ff7e960867bb5015d904bc7a0d209357084d96d4f16f5055bbff3b4` (bản CRLF lúc chạy); `36b6027d48d6b50d76a1b675ea929b24d128cc3bbf79975170fd6e42da2a7eca` sau khi chuẩn hóa line ending về LF theo `.gitattributes`. Nội dung ngoài line ending không đổi.

**Stratum Benign — superiority (D-06 theo A-91):**

| $\rho$ nominal (achieved) | Median $\Delta_{\text{SHD}}$ [95% CI] | Median $\Delta_{\text{F1}}$ [95% CI] | W / T / L (cell) | Fallback | Verdict |
|---|:---:|:---:|:---:|:---:|:---:|
| 0.00 (0.000) | 1.9 [1.3, 2.2] | 0.0582 [0.0389, 0.0719] | 73 / 27 / 0 | 15/100 | SUPERIORITY_PASS |
| 0.10 (0.095) | 1.6 [1.2, 1.9] | 0.0430 [0.0346, 0.0542] | 71 / 29 / 0 | 19/100 | SUPERIORITY_PASS |
| 0.20 (0.190) | 1.2 [0.8, 1.8] | 0.0316 [0.0248, 0.0497] | 58 / 42 / 0 | 26/100 | SUPERIORITY_PASS |

**Stratum Severe — non-inferiority (D-02: cận dưới SHD > −1.0, F1 > −0.05):**

| $\rho$ nominal (achieved) | Cận dưới 95% CI $\Delta_{\text{SHD}}$ | Cận dưới 95% CI $\Delta_{\text{F1}}$ | W / T / L (cell) | Fallback | Verdict |
|---|:---:|:---:|:---:|:---:|:---:|
| 0.50 (0.524) | 0.1 | 0.0000 | 20 / 80 / 0 | 74/100 | NI_PASS |
| 0.70 (0.714) | 0.0 | 0.0000 | 7 / 93 / 0 | 90/100 | NI_PASS |
| 1.00 (1.000) | 0.0 | 0.0000 | 2 / 97 / 1 | 94/100 | NI_PASS |

**Verdict gate: `CLAIM_UNLOCKED`** (superiority ở mọi mức Benign, NI ở mọi mức Severe, fallback tại $\rho = 0$ là 15% < 20%). Artifact: `results/issue91_acceptance_gate_confirmatory.json`.

Diễn giải được phép (claim map 7.2):

- Trong simulator và bank đã khai báo, với directional prior có hư hại thực nhận $\le 0.19$, Enhanced v2 giảm SHD tổng thể (median theo topology 1.2–1.9 cạnh) và tăng arrowhead F1 (median 0.032–0.058) so với Standard v2, cận dưới 95% CI dương ở cả ba mức.
- Ở $\rho \ge 0.52$, Enhanced v2 không kém Standard v2 theo margin D-02. Non-inferiority chủ yếu đạt qua global fallback (74–94% cell); không được diễn giải là khả năng thích ứng với prior sai. Có 1 loss ở $\rho = 1.0$.
- Skeleton trùng Standard v2 ở mọi cell (`max_abs_delta_f1_skeleton = 0.0`); không có claim skeleton.

### 4.4. Development split, $R = 5$, seed gốc (exploratory, để minh bạch)

Chạy trước gate confirmatory, không dùng để chỉnh tham số.

| $\rho$ | Median $\Delta_{\text{SHD}}$ [95% CI] | Median $\Delta_{\text{F1}}$ [95% CI] | W / T / L | Fallback |
|---|:---:|:---:|:---:|:---:|
| 0.00 | 1.8 [1.1, 2.8] | 0.0496 [0.0337, 0.0819] | 65 / 35 / 0 | 21/100 |
| 0.10 | 1.8 [1.3, 2.4] | 0.0470 [0.0361, 0.0641] | 63 / 37 / 0 | 21/100 |
| 0.20 | 1.8 [1.3, 2.0] | 0.0445 [0.0346, 0.0525] | 57 / 43 / 0 | 30/100 |
| 0.50 | cận dưới 0.0 | cận dưới −0.0007 | 22 / 77 / 1 | 61/100 |
| 0.70 | cận dưới 0.0 | cận dưới 0.0000 | 13 / 86 / 1 | 79/100 |
| 1.00 | cận dưới 0.0 | cận dưới 0.0000 | 6 / 94 / 0 | 88/100 |

Development cho fallback tại $\rho = 0$ là 21%, cao hơn ngưỡng 20% của AC-05; điều kiện fallback của gate chỉ đạt trên confirmatory. Chênh lệch này nằm trong biến thiên giữa các tập 20 topology và cần được nêu cùng claim.

---

## 5. Hiện trạng Acceptance Criteria Issue #91

| AC | Trạng thái | Bằng chứng |
|---|---|---|
| AC-01 Loại ngôn từ hype | Đã làm | Báo cáo này viết lại toàn bộ; danh sách từ cấm ở claim map 7.2. |
| AC-02 Khóa claim boundary | Đã làm | Claim map mục 7 (A-91), `CONTRACT_TRACEABILITY.md` DEC-05/DEC-06. |
| AC-03 Soft score-margin | Đã làm | Mục 4.1; test 14, 15, 18. |
| AC-04 Mẫu số & local/global | Đã làm | Mục 4.1; test 15, 16, 17. |
| AC-05 Superiority 40 DAG | Đã làm với phạm vi chặt hơn issue | Gate chạy trên confirmatory với seed mới thay vì toàn 40 DAG (development đã được dùng khi thiết kế). Issue ghi "Median $\Delta_{\text{SHD}} < 0$ với cận dưới CI > 0" là mâu thuẫn dấu; gate dùng benefit convention thống nhất. |

---

## 6. Giới hạn

1. **Topology confirmatory đã bị lộ.** 20 topology confirmatory đã có kết quả công bố ở PR #89, và diagnostic audit #91 đã in thống kê fallback per-DAG của cả 40 DAG trước khi thiết kế cơ chế. Thiết kế dựa trên margin của development split và không tune tham số, nhưng không loại trừ được ảnh hưởng gián tiếp. Claim confirmatory sạch hoàn toàn cần bank topology held-out mới (quyền quyết định của Human).
2. **Prior synthetic.** Prior định hướng sinh từ generator truth với confidence cố định 0.8 và đảo ngẫu nhiên đều; không suy rộng sang prior chuyên gia thật, nơi lỗi có thể tương quan với cấu trúc.
3. **Nhãn `mpdag`.** Meek closure chỉ cài R1–R3; khi có background knowledge cần R4 để đạt maximal orientation.
4. **CRIT-05.** Stability gate bootstrap/subsampling bên trong estimator chưa được cài; cluster bootstrap hiện có chỉ là suy luận ở mức benchmark.
5. **Runtime và Meek cascade.** Chưa đo lại cho code #91.

---

## 7. Tái hiện

```bash
# Gate nghiệm thu pre-registered (confirmatory, seed base mới)
python 03_causal_discovery/proposed_framework/enhanced_v2/scripts/evaluate_d07_bank.py --acceptance-gate --split confirmatory --replicates 5 --seed-base 20271000

# Development, exploratory
python 03_causal_discovery/proposed_framework/enhanced_v2/scripts/evaluate_d07_bank.py --acceptance-gate --split development --replicates 5

# Before/After toàn bank, seed gốc
python 03_causal_discovery/proposed_framework/enhanced_v2/scripts/evaluate_d07_bank.py --corruption 0.0
```
