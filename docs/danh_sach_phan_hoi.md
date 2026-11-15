Phản hồi của các thầy (buổi họp 13/11/2026) và cách nhóm hiểu

Chung: về mặt đóng góp bài đã đủ, từ nay chỉ cải thiện các điểm dưới đây, hướng tạp chí Q2. "Mở rộng bối cảnh mô phỏng" nhóm hiểu là tăng số topology, tăng số lag, cấu hình lại phân phối nhiễu.

1. Áp dụng vào dữ liệu thực tế (thị trường Việt Nam), ra kết quả thực tế.
   Hiểu là: chạy phương pháp trên dữ liệu thật để thấy tính thực tiễn, làm thành một section riêng (case study), tách khỏi phần mô phỏng.

2. Chứng minh điều kiện đủ để coverage đúng.
   Hiểu là: có một phát biểu hữu hạn mẫu, nêu rõ điều kiện, bảo đảm khoảng tin cậy phủ đúng.

3. Chứng minh hệ số 0,5.
   Hiểu là: giải thích vì sao có hằng số 0,5 và nó ảnh hưởng thế nào đến kết quả.

4. Mở rộng bối cảnh mô phỏng (cấu hình phân phối Gaussian, tăng số lượng topology).
   Hiểu là: nhiều topology hơn, nhiều lag hơn, nhiều kiểu nhiễu hơn.

5. Cải thiện các metric ở RQ4.4 (AUROC).
   Hiểu là: cờ độ tin cậy phải phân biệt tốt hơn cặp biến nào sẽ bị khoảng tin cậy trượt.

6. Xem kỹ phần so sánh trong kết quả chính.
   Hiểu là: phép so sánh với các phương pháp tham chiếu phải công bằng.

7. Vẽ architecture.
   Hiểu là: sơ đồ khối tổng thể của phương pháp, từ đầu vào đến khoảng tin cậy.

8. Giải thích số liệu trong các bảng kết quả.
   Hiểu là: mỗi bảng cần có đoạn hướng dẫn đọc (cột nào, hàng nào, kết luận gì).

9. Tìm tài liệu tham khảo từ 2021 trở về sau.
   Hiểu là: cập nhật danh mục tham khảo gần đây, nhất là conformal và bootstrap cho SVAR.

10. Ablation: tìm T hoặc mức hỏng mà module chịu lỗi hiện tại có thể chạy được.
    Hiểu là: xác định ngưỡng cỡ mẫu và mức hỏng tối đa để phương pháp còn dùng được.

Cấu trúc bài nhóm đề xuất: mô phỏng là phần chính (Kết quả chính), ứng dụng dữ liệu thật là một section riêng (Case study) đứng sau.
