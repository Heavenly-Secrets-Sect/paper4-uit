# Bản nháp: giải thích số liệu trong các bảng kết quả (phản hồi điểm 8)

Mỗi mục dưới đây là đoạn "cách đọc bảng" đề xuất đặt ngay sau bảng tương ứng trong `sections/05_ket_qua.tex`. Mọi con số lấy nguyên từ bản `.tex` hiện tại; chưa thêm số nào. Chưa chèn vào bài (chờ các thầy xem). Đoạn cuối mỗi mục nêu điều bảng **không** chứng minh.

## Bảng `tab:full`: RB và SRCI theo loại lỗi và cỡ mẫu

**Cách đọc.** Mỗi ô có dạng *coverage / interval score* (IS), tính trên 60 bộ dữ liệu. Coverage là tỉ lệ khoảng tin cậy chứa giá trị thật; mức danh nghĩa là 0,95. IS gộp độ rộng và mức trượt giá trị thật vào một thước đo, càng thấp càng tốt. Cột RB là residual bootstrap cắm skeleton như đúng; cột SRCI là phương pháp đề xuất. Mỗi hàng là một loại và mức lỗi của skeleton, mỗi cặp cột là một cỡ mẫu T.

**Điều bảng cho thấy.** Đọc theo hàng "Thiếu 50%": RB phủ khoảng 0,33 ở cả ba T với IS gần 29, tức khoảng của RB hẹp mà sai; SRCI phủ 0,95 đến 0,97 với IS từ 4,99 (T = 40) xuống 1,99 (T = 150). Đọc theo hàng "Không hỏng": RB chỉ phủ 0,86, 0,88, 0,91 ở T = 40, 80, 150, nghĩa là một phần cải thiện của SRCI đến từ hiệu chỉnh độ rộng, không riêng do xử lý cấu trúc.

**Điều bảng không chứng minh.** Hàng "Skeleton do GES" dùng cột SRCI là bản chưa chọn lọc lag (đã ghi trong chú thích); coverage của SRCI chưa đạt đúng 0,95 ở mọi ô (ví dụ 0,92 ở T = 40).

## Bảng `tab:main` và `tab:diff`: so sánh với các phương pháp tham chiếu

**Cách đọc.** `tab:main` có dạng *IS (coverage)*; mỗi cột là một ô: T ∈ {80, 150} và tỉ lệ cạnh thiếu 20% hoặc 50%. `tab:diff` là hiệu IS giữa SRCI và từng phương pháp tham chiếu trên cùng bộ dữ liệu; số âm nghĩa là SRCI tốt hơn. Chữ "(cal)" chỉ bản đã hiệu chỉnh độ rộng cho công bằng với SRCI.

**Điều bảng cho thấy.** SRCI có IS thấp nhất ở cả bốn ô và coverage 0,96 đến 0,97. Chênh lệch với phương pháp tham chiếu gần nhất là 0,05 đến 0,8 trên mức IS 2 đến 4, tức khoảng 2 đến 25%, nhỏ hơn nhiều so với khoảng cách với RB (IS 10 đến 29). Có 27 trên 28 so sánh có khoảng tin cậy 95% của hiệu không chứa 0 (hiệu chỉnh Holm trên 56 so sánh); trường hợp hòa là PSel-Union (cal) ở T = 150, thiếu 50% (hiệu −0,05).

**Điều bảng không chứng minh.** (i) Chỉ có bốn ô thiếu cạnh với T = 80 và 150; chưa có ô thừa hay đảo cạnh. (ii) SRCI nhận số cạnh thiếu khai báo để quyết định mở bao nhiêu lag, còn PSel-Union, BVAR-Minnesota và TLP không dùng thông tin này khi chọn cấu trúc, nên lợi thế gộp cả phương pháp và thông tin khai báo. (iii) PSel-Union (cal) dùng số lần bootstrap gấp 32 lần. (iv) Một số phương pháp tham chiếu là bản do nhóm chuyển thể, không phải bản công bố gốc.

## Bảng đóng góp từng thành phần (thăm dò)

**Cách đọc.** Mỗi hàng là một thành phần của phương pháp; cột bên phải là tác dụng đo được khi thêm thành phần đó, trên tập phát triển, so với bản không có thành phần. IS giảm nghĩa là thành phần có ích.

**Điều bảng cho thấy.** Bổ sung cạnh cùng kỳ và rút chiều ngẫu nhiên là nguồn lợi thế chính so với chỉ mở mọi lag (Full VAR (cal) tệ hơn ở 19 trên 21 ô sau Holm). Mở lag có chọn lọc giảm IS ở cả 6 ô thiếu cạnh (từ −0,23 đến −2,93) và không làm tệ ô nào. Hiệu chỉnh độ rộng hai phía giảm IS 0,71 đến 0,79 ở T = 40 khi thiếu cạnh, ở ô khác gần như không đổi.

**Điều bảng không chứng minh.** Đây là kết quả thăm dò trên tập phát triển, không phải kiểm chứng.

## Bảng ba lần kiểm chứng RQ4.1

**Cách đọc.** Hàng là lần kiểm chứng (mỗi lần 20 topology mới), cột (a) đến (d) là bốn tiêu chí đã ghi trước; "Đạt" hoặc "Trượt" kèm số ô đạt. Cột "Quy tắc" cho biết tiêu chí gốc hay bản đã sửa.

**Điều bảng cho thấy.** Theo quy tắc gốc, RQ4.1 không đạt ở lần 1. Kết luận định tính vững là: thiếu cạnh nặng nhất, thừa cạnh gần như vô hại, cạnh đảo làm sai cả lag.

**Điều bảng không chứng minh.** Các tiêu chí (a′) và (c2) được sửa sau khi đã thấy kết quả lần 1 và lần 2; chỉ ngưỡng 0,85 và cách gộp theo T được khóa trước lần 3. Thứ tự đầy đủ thiếu > đảo > thừa chỉ đạt 4/6.

## Bản đồ chi phí theo cạnh (RQ4.3) và cờ độ tin cậy (RQ4.4): đề xuất thêm hai bảng nhỏ

Hiện hai mục này chỉ có đoạn văn. Đề xuất:

| Loại cạnh hỏng | Độ lệch trung vị trên đường truyền dẫn | Khoảng tin cậy 95% |
|---|---|---|
| Thiếu cạnh cùng kỳ | 0,952 | [0,929; 0,965] |
| Thiếu cạnh có lag | 0,844 | [0,749; 0,895] |
| Đảo cạnh cùng kỳ | 0,541 | [0,510; 0,574] |

| Cỡ mẫu | AUROC của cờ | Khoảng tin cậy 95% | Hơn comparator độ rộng tương đối | Cặp gắn cờ trượt nhiều gấp |
|---|---|---|---|---|
| T = 80 và 150 | 0,720 | [0,698; 0,744] | +0,089 | 3,98 |
| T = 40 | 0,812 | [0,791; 0,832] | +0,220 | 6,77 |

**Cách đọc cờ:** AUROC bằng 0,5 là đoán ngẫu nhiên, 1,0 là phân loại hoàn hảo; cờ ở mức 0,72 khá khiêm tốn. Điều này cũng là lý do điểm 5 (cải thiện AUROC) còn mở.

## Bảng `tab:vung`: T tối thiểu theo số lag

**Cách đọc.** Hàng là số lag p; hai cột là T tối thiểu từ đó trở lên phương pháp dùng được (đủ ba điều kiện: ít nhất 57/60 lượt chạy có kết quả, coverage gộp ≥ 0,90, IS trung bình không quá 3 lần Oracle) ở cả hai mức hỏng.

**Điều bảng cho thấy.** SRCI dùng được từ T = 19 khi p = 1, từ 40 khi p = 2, từ 80 khi p = 4; phiên bản không chọn lọc lag đòi T lớn hơn ở p = 1 (25) và p = 4 (150).

**Điều bảng không chứng minh.** Đây là kết quả thăm dò trên tập phát triển với điều kiện gộp ba điểm; kết quả mới trên tập 1.200 topology (lag 1 đến 3) cho ngưỡng tương tự nhưng theo tiêu chí khác (có hệ số đảm bảo hữu hạn); cần quyết định dùng tiêu chí nào khi viết bài.
