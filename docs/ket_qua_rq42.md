# Kết quả RQ4.2: module chịu lỗi skeleton (bản thăm dò)

**Trạng thái.** Toàn bộ là kết quả *thăm dò* (exploratory), chưa phải kết quả xác nhận. Quy tắc giữ hay loại được ghi trước từng lượt chạy ở [decision_rules.md](decision_rules.md) và chấm tự động bằng `experiments/check_rules.py`. Cấu hình thực nghiệm:

- **Generator:** SVAR có 14 nút, 21 cạnh, lag_max = 2, khoảng 30% cạnh cùng kỳ.
- **Đại lượng cần ước lượng:** C(4) của mọi cặp có |C| > 0.1.
- **Mẫu:** 20 topology × 3 lần lặp mỗi ô.
- **Bootstrap:** 199 lần.

## Câu hỏi

Khi skeleton đưa vào bị thiếu cạnh, thừa cạnh hoặc đảo chiều, liệu có cách ước lượng nào (a) cho khoảng tin cậy phủ được giá trị thật ở mức gần 95%, và (b) có interval score tốt hơn các cách báo một điểm? Đây là RQ4.2 trong plan.

## Các phương pháp so sánh

| Tên | Vai trò | Cách làm |
|---|---|---|
| `oracle` | b0, mốc tham chiếu | Đồ thị thật với lag thật (ngoài thực tế không có) |
| `plugin` | b1 | Dynamic SEM trên đúng skeleton nhận được, bootstrap phần dư |
| `inflate` | b3 | Khoảng của b1 nới rộng theo hằng số c, hiệu chỉnh riêng từng ô hỏng trên bank D-07H development |
| `lp_allpast` | b4 | Local projection dùng toàn bộ quá khứ; skeleton chỉ cho tập cha cùng kỳ |
| `bagging` | b5 | b1 fit lại trên các skeleton bị xáo trộn theo mức hỏng khai báo |
| `tolerant_v3_cal` | **module** | Xem mục "Module v3 làm gì" bên dưới |

## Module v3 làm gì

Module nhận skeleton cùng mức hỏng khai báo (loại hỏng và số cặp hỏng), rồi xử lý theo loại hỏng:

1. **Khai báo có cạnh thiếu:**
   - Mọi lag của mọi biến đều được đưa vào mọi phương trình, nên không hạng có lag nào bị mất.
   - Những cặp có **phần dư cấu trúc tương quan** được thêm lại cạnh cùng kỳ. Kiểm định dùng Benjamini–Hochberg; số cạnh thêm tối đa bằng số cặp thiếu khai báo.
   - Lý do: mô hình giả định các cú sốc cấu trúc độc lập với nhau, nên một cạnh cùng kỳ bị mất để lại đúng dấu vết là tương quan giữa phần dư.
   - Chiều của cạnh thêm vào không nhận diện được, nên mỗi lần bootstrap rút chiều ngẫu nhiên.
2. **Khai báo có cạnh đảo:** mỗi lần bootstrap đảo số cặp bằng số khai báo. Chỉ đảo trong các cặp có hệ số cùng kỳ ý nghĩa thống kê (|t| > 1.645), vì độ lớn của liên kết cùng kỳ nhận diện được, chỉ chiều là không.
3. **Không khai báo hỏng:** dùng đúng skeleton, khi đó module trùng với `plugin`.
4. **Hiệu chỉnh mẫu nhỏ:** khoảng được nới rộng bởi hệ số c_T. Hệ số này chỉ phụ thuộc T: 1.5 / 1.3 / 1.2 ở T = 80 / 150 / 300. Nó được hiệu chỉnh trên các ô **không hỏng** của D-07H development, nên không mang thông tin gì về hỏng.

## Các vòng cải tiến

| Phiên bản | Ý tưởng | Kết quả theo quy tắc | Bài học |
|---|---|---|---|
| v1 `soft` | Skeleton thành prior ridge mềm cho các hạng có lag | **Loại** | Phạt ridge làm hệ số bị kéo lệch về 0, và bootstrap không thấy phần lệch đó, nên coverage còn thấp hơn `plugin` |
| v2 `tolerant` | Mọi lag khi khai báo thiếu cạnh; thêm lại cạnh cùng kỳ theo tương quan phần dư; bagging chiều | **Loại**, chỉ do coverage ô đảo 20% (0.86–0.89) | Đã thắng `lp_allpast` 6/6 ô hỏng. Phần hụt còn lại phần lớn do bootstrap ở mẫu nhỏ: chính `oracle` cũng chỉ đạt 0.895 ở T = 80 |
| v3 `tolerant_v3_cal` | Đảo có nhắm mục tiêu, cộng hiệu chỉnh mẫu nhỏ theo T | **Giữ** trên development **và** held-out | Ở các ô hỏng, coverage vượt mức danh nghĩa (0.94–0.99) |

v3 được kiểm tra đúng một lần trên **D-07 confirmatory**. Paper 4 chưa từng dùng split này cho phát triển hay hiệu chỉnh.

## Bảng chính: held-out (D-07 confirmatory), T = 150

Mỗi ô ghi: coverage / interval score (thấp hơn là tốt hơn).

| Hỏng | `oracle` | `plugin` | `inflate` | `lp_allpast` | `bagging` | **`tolerant_v3_cal`** |
|---|---|---|---|---|---|---|
| Không hỏng | 0.93 / 1.06 | 0.92 / 1.58 | 0.97 / 1.60 | 0.89 / 2.72 | 0.91 / 1.59 | **0.97 / 1.61** |
| Thừa 50% | 0.93 / 1.06 | 0.92 / 1.71 | 0.97 / 1.71 | 0.89 / 2.75 | 0.95 / 2.49 | **0.97 / 1.70** |
| Thiếu 20% | 0.93 / 1.06 | 0.66 / 11.29 | 0.88 / 14.35 | 0.89 / 2.73 | 0.67 / 10.15 | **0.98 / 2.12** |
| Thiếu 50% | 0.93 / 1.06 | 0.34 / 29.17 | 0.49 / 28.37 | 0.88 / 2.91 | 0.40 / 22.15 | **0.98 / 2.23** |
| Đảo 20% | 0.93 / 1.06 | 0.83 / 3.16 | 0.95 / 2.62 | 0.88 / 3.27 | 0.87 / 2.26 | **0.97 / 1.95** |
| Đảo 50% | 0.93 / 1.06 | 0.70 / 5.89 | 0.93 / 3.71 | 0.85 / 4.30 | 0.84 / 2.81 | **0.96 / 2.11** |

## v4: hiệu chỉnh riêng cho module, kiểm tra trên bank mới P4-H1

**v4 (`tolerant_v4`) là module chính thức hiện tại.** Nó giống v3, chỉ khác ở hệ số nới rộng: hệ số được hiệu chỉnh cho **chính module**, theo từng (T, loại hỏng khai báo), trên D-07H development. v4 được **giữ** trên D-07 development và trên **P4-H1 confirmatory**, một bank sinh mới cho Paper 4. Bank này được sinh sau khi v3 đã đóng băng và chỉ chạy một lần.

Kết quả trên P4-H1 ở **T = 40**, mức mà `lp_allpast` không ước lượng được. Mỗi ô ghi coverage / interval score:

| Hỏng | `oracle` | `plugin` | `inflate` | `bagging` | **`tolerant_v4`** |
|---|---|---|---|---|---|
| Không hỏng | 0.87 / 2.78 | 0.82 / 5.14 | 0.94 / 4.49 | 0.83 / 5.15 | **0.95 / 4.57** |
| Thiếu 20% | 0.87 / 2.78 | 0.66 / 12.20 | 0.91 / 19.31 | 0.69 / 10.14 | **0.98 / 7.82** |
| Thiếu 50% | 0.87 / 2.78 | 0.34 / 29.77 | 0.54 / 32.59 | 0.50 / 16.98 | **0.97 / 7.75** |
| Đảo 20% | 0.87 / 2.78 | 0.79 / 6.46 | 0.93 / 5.23 | 0.81 / 6.01 | **0.95 / 5.11** |
| Đảo 50% | 0.87 / 2.78 | 0.74 / 8.01 | 0.92 / 5.84 | 0.79 / 6.70 | **0.95 / 5.29** |

So với v3 trên P4-H1, coverage ở các ô thiếu cạnh tiến gần 0.95 hơn: 0.975 so với 0.988 ở T = 80, và 0.967 so với 0.976 ở T = 150.

## Lỗi có cấu trúc (ngoài phân phối)

`rq42_structured`, D-07 development. Module v4 đã đóng băng; nó chỉ nhận số cạnh thiếu / thừa / đảo khai báo, và hệ số độ rộng giữ nguyên như khi hiệu chỉnh cho hỏng một loại. Còn `inflate` được hiệu chỉnh riêng trên chính các ô này, nên có lợi thế. Các kiểu hỏng:

- **shortcut:** chuỗi A→B→C bị ghi tắt thành A→C, đồng thời bỏ một cạnh của chuỗi.
- **weak_missing:** bỏ các cạnh yếu nhất.
- **mixed:** thiếu, thừa và đảo cùng lúc.

Kết quả ở T = 150, mỗi ô ghi coverage / interval score:

| Hỏng | `plugin` | `inflate` | `lp_allpast` | **`tolerant_v4`** |
|---|---|---|---|---|
| shortcut 20% | 0.70 / 8.06 | 0.94 / 10.99 | 0.89 / 2.79 | **0.96 / 2.04** |
| shortcut 50% | 0.58 / 11.98 | 0.90 / 11.49 | 0.89 / 2.81 | **0.96 / 2.09** |
| weak_missing 20% | 0.69 / 7.38 | 0.89 / 10.68 | 0.89 / 2.74 | **0.96 / 2.07** |
| weak_missing 50% | 0.34 / 22.78 | 0.51 / 22.67 | 0.89 / 2.90 | **0.96 / 2.18** |
| mixed 20% | 0.61 / 11.46 | 0.91 / 12.08 | 0.87 / 3.32 | **0.96 / 2.34** |
| mixed 50% | 0.36 / 23.58 | 0.78 / 15.51 | 0.84 / 4.32 | **0.94 / 2.54** |

**Kết luận:** module tổng quát hóa được sang các kiểu lỗi giống lỗi trích xuất văn bản mà nó chưa từng gặp khi hiệu chỉnh. Ở T = 80 kết quả cùng xu hướng: coverage 0.96–0.97, IS 3.1–3.4, trong khi `lp_allpast` là 5.3–6.2.

## Đọc kết quả

- **Cách báo một điểm (`plugin`) sụp khi skeleton thiếu cạnh.** Coverage chỉ còn 0.34–0.66, và tăng T không cứu được. Nguyên nhân là những hiệu ứng mất đường đi bị báo bằng 0 với khoảng [0, 0].
- **Nới rộng khoảng (`inflate`) không cứu được hiệu ứng đã mất,** vì nới rộng khoảng [0, 0] theo bất kỳ hệ số nào cũng vẫn là [0, 0].
- **Bỏ skeleton cho phần có lag (`lp_allpast`) chịu được thiếu cạnh,** nhưng tốn phương sai, không chạy được ở T = 40, và yếu khi đảo cạnh.
- **Module v3** đạt coverage ≥ 0.95 ở mọi ô. Interval score của nó tốt nhất ở mọi ô hỏng, và ngang `plugin`/`inflate` khi skeleton đúng.

## Giới hạn, tự phản biện

1. **Coverage vẫn hơi vượt mức danh nghĩa (0.95–0.98):** đã giảm bớt ở v4 nhờ hiệu chỉnh riêng cho module. Phần còn lại là do hệ số được chọn trên lưới bước 0.1, và do mỗi loại hỏng chỉ có một hệ số chung cho mọi mức hỏng.
2. **Khai báo sai mức hỏng** (`rq42_misstated`, D-07 development, T = 150). Mỗi ô ghi coverage / IS của `tolerant_v3_cal`:

   | Hỏng thật | Khai báo đúng | Khai báo ×0.5 | Khai báo ×2 | Không khai báo (×0) |
   |---|---|---|---|---|
   | Thiếu 20% | 0.975 / 2.11 | 0.975 / 2.12 | 0.976 / 2.12 | 0.724 / 10.53 |
   | Thiếu 50% | 0.969 / 2.30 | 0.966 / 2.32 | 0.971 / 2.30 | 0.367 / 28.25 |
   | Đảo 20% | 0.953 / 2.12 | 0.951 / 2.13 | 0.961 / 2.09 | 0.887 / 2.69 |
   | Đảo 50% | 0.939 / 2.17 | 0.922 / 2.40 | 0.906 / 2.63 | 0.790 / 4.38 |

   **Báo động giả trên skeleton đúng:** IS là 1.61 khi khai báo đúng (không hỏng). Khai báo thiếu 4 cặp cho IS 2.03, đảo 1 cặp cho 1.82, đảo 3 cặp cho 2.13. Coverage luôn ≥ 0.95.

   **Kết luận:** module chỉ cần biết *có* hỏng hay không, gần như không cần biết chính xác bao nhiêu. Chi phí bất đối xứng: khai báo thừa tốn nhiều nhất khoảng 30% interval score, còn bỏ sót thì tốn gấp 5–13 lần. Khuyến nghị cho Bài 5: luôn khai báo một mức thiếu cạnh tối thiểu khi dùng prior trích từ văn bản.
3. **Hỏng hỗn hợp và lỗi có cấu trúc** đã thử (mục trên). Chưa thử lỗi do chính thuật toán học skeleton tạo ra, chẳng hạn skeleton học bằng GES hay SP-GES của Bài 2.
4. **T = 40:** module chạy được và đạt coverage khoảng 0.95 (xem bảng P4-H1 ở trên). T = 19 chưa thử: với lag_max = 2, số tham số vượt số quan sát ngay cả khi skeleton đúng.
5. **Generator chỉ có một kiểu:** tuyến tính, dừng, nhiễu Gauss, lag_max = 2. Chưa có biến ẩn, chưa có nhiễu đo; plan mục 9 giao hai phần này cho Bài 4.
6. **Chưa có ô hỏng nào cho cạnh có lag ở kiểu đảo.** `reversed_any` có trong code nhưng chưa chạy với module.
7. **Các split đã dùng:** D-07H confirmatory (v2), D-07 confirmatory (v3), P4-H1 confirmatory (v3 và v4). P4-H1 development vẫn chưa dùng.
