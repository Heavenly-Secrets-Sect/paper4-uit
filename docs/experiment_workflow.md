# Workflow thực nghiệm Paper 4

Bám theo `Plan_Paper3_Paper4_Paper5.docx`, mục 5.2. Đây là trạng thái code hiện tại, chưa phải protocol đã duyệt. Những lựa chọn plan chưa quy định được ghi ở [open_questions.md](open_questions.md).

```
          ┌─────────────────────────────── đồ thị THẬT (truth) ───────────────────────────────┐
          │  topology 14 nút lấy từ generator bank + gán lag + gán hệ số                      │
          └───────────┬───────────────────────────────────────────────┬───────────────────────┘
                      │ (B1) sinh dữ liệu                              │ bỏ chiều, bỏ lag
                      ▼                                                ▼
              dữ liệu T × 14                                    true skeleton
                      │                                                │ (B3) làm hỏng có kiểm soát:
                      │                                                │      thêm / xóa / đảo, tỷ lệ định trước
                      │                                                ▼
                      │                                         skeleton HỎNG  +  mức hỏng
                      │                                                │
                      └──────────────►  (B4) module Dynamic SEM  ◄─────┘
                                                 │
                                                 ▼
                                  hiệu ứng + khoảng + cờ tin cậy
                                                 │
                                                 ▼
                              so với truth → sai số, coverage (RQ4.1–4.4)
```

**Điểm mấu chốt:** dữ liệu được sinh từ **đồ thị thật**. Module chỉ nhận **skeleton hỏng**, không bao giờ thấy đồ thị thật. Nếu sinh dữ liệu từ chính skeleton đưa vào module thì sẽ không có lỗi nào để nghiên cứu.

## Ánh xạ sang code

| Bước | Module | Hàm chính | Output |
|---|---|---|---|
| Topology | `data/topology_bank/` + `src/paper4/topology.py` | `load_bank("D-07", "development")` | DAG tĩnh 14 nút, 21 cạnh (bản chép từ Paper 2), đã kiểm SHA-256 với manifest |
| Gán lag + hệ số | `src/paper4/generator.py` | `build_dynamic_sem` | `DynamicSEM`: ma trận B (lag_max+1 × 14 × 14), phương sai nhiễu, lag của từng cạnh |
| (B1) Sinh dữ liệu | `src/paper4/generator.py` | `DynamicSEM.simulate(T, rng)` | Mảng T × 14 |
| Truth của hiệu ứng | `src/paper4/effects.py`, `metrics.truth_effects` | `irf`, `cumulative`, `mean_lag`, `peak_lag` | IRF θ(h), C(H), mean lag, peak lag |
| True skeleton | `src/paper4/skeleton.py` | `true_skeleton(sem)` | Skeleton: các cặp kề, có chiều, không có lag |
| (B3) Làm hỏng | `src/paper4/skeleton.py` | `damage(skel, kind, rate, rng)` | Skeleton hỏng kèm `damage_estimate`. `to_interface()` xuất theo giao diện ở plan mục 7 |
| (B4) Fit và bootstrap dùng chung | `src/paper4/estimator.py` | `fit_equations`, `bootstrap_C` | B̂ (OLS hoặc ridge), C(H) bootstrap |
| (B4) Baseline b0–b5 | `src/paper4/methods.py` | `oracle`, `plugin`, `inflate`, `lp_allpast`, `bagging` | C(H) kèm khoảng 95% |
| (B4) Module chịu lỗi | `src/paper4/methods.py` | `tolerant_v3` + `calibrate_width` = **`tolerant_v4`** (module chính thức) | Mọi lag khi khai báo thiếu cạnh, thêm lại cạnh cùng kỳ theo tương quan phần dư, rút chiều có nhắm mục tiêu khi khai báo đảo, nới rộng theo (T, loại hỏng). Các bản v1 `soft`, v2 `tolerant` bị loại, giữ lại để đối chiếu |
| So với truth | `src/paper4/metrics.py` | `evaluate(sem, est, H)` | Sai số cường độ (theo cạnh và theo C(H)), sai số lag, coverage và độ rộng khoảng |
| Runner | `experiments/run_experiment.py` | `--config experiments/configs/*.json` | `results/<name>/`: runs, skeletons (log hỏng riêng), calibration, summary |
| Chấm quy tắc | `experiments/check_rules.py` | `results/<name> --module tolerant_v4` | Kết luận giữ / loại theo [decision_rules.md](decision_rules.md) |
| RQ4.3 | `experiments/run_edge_cost.py` | — | `results/rq43_edge_cost/` |
| RQ4.4 | `experiments/run_flags.py` | — | `results/rq44_flags/` |

## Kết quả

- RQ4.1 và RQ4.2: [ket_qua_rq42.md](ket_qua_rq42.md)
- RQ4.3: [ket_qua_rq43.md](ket_qua_rq43.md)
- RQ4.4: [ket_qua_rq44.md](ket_qua_rq44.md)
- Vùng dùng được (sản phẩm P4): [ket_qua_vung_dung_duoc.md](ket_qua_vung_dung_duoc.md)
- Nhật ký các vòng cải tiến và quy tắc ghi trước: [decision_rules.md](decision_rules.md)

## Bước chưa làm

- **B2, mở rộng T bằng hàm lạm phát:** chờ thầy định nghĩa (câu hỏi 3 ở [open_questions.md](open_questions.md)). Hiện tại generator sinh chuỗi dài bao nhiêu cũng được từ cùng một cấu trúc; đây là hướng thứ nhất mà plan mục 5.5 nêu.
- **Biến ẩn và nhiễu đo** (plan mục 9 giao cho Bài 4).
- **Lỗi do chính thuật toán học skeleton tạo ra** (skeleton học bằng GES hay SP-GES của Bài 2).
