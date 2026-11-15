---
title: "Danh sách phản hồi buổi họp 13/11/2026 và cách nhóm hiểu, đề nghị thầy xác nhận"
---

**Ghi nhận chung của thầy:** về mặt đóng góp, bài đã đủ; từ nay chỉ tập trung cải thiện các điểm dưới đây (hướng tạp chí Q2). Nhóm hiểu "mở rộng bối cảnh mô phỏng" là: tăng số lượng topology, tăng số lag, và cấu hình lại phân phối nhiễu.

| # | Phản hồi của thầy | Nhóm hiểu là | Hướng thực hiện | Thầy xác nhận |
|:-:|---|---|---|:-:|
| 1 | Áp dụng vào dữ liệu thực tế (thị trường Việt Nam), ra kết quả thực tế | Chạy phương pháp trên dữ liệu thật để thấy tính thực tiễn; là một section riêng (case study), tách khỏi phần mô phỏng | Chạy trên panel 14 biến, 19 quý; chỉ minh họa khoảng tin cậy, không báo coverage vì không có giá trị thật. Bảy biến ngân hàng của panel hiện là dữ liệu mô phỏng hiệu chỉnh, sẽ khai báo rõ trong bài | ☐ Đúng  ☐ Chỉnh |
| 2 | Chứng minh điều kiện đủ để coverage đúng | Có một phát biểu hữu hạn mẫu, nêu rõ điều kiện, bảo đảm khoảng tin cậy phủ đúng | Phát biểu theo hướng conformal ở mức topology (hệ số nới độ rộng là thống kê hạng trên các topology hiệu chỉnh), kèm kiểm chứng bằng mô phỏng độc lập | ☐ Đúng  ☐ Chỉnh |
| 3 | Chứng minh hệ số 0,5 | Giải thích vì sao có hằng số 0,5 và nó có ảnh hưởng không | Hằng số này không có cơ sở lý thuyết; kiểm độ nhạy và đề xuất bỏ nó, thay bằng hiệu chỉnh trực tiếp | ☐ Đúng  ☐ Chỉnh |
| 4 | Mở rộng bối cảnh mô phỏng (cấu hình phân phối Gaussian, tăng số lượng topology) | Nhiều topology hơn, nhiều lag hơn, nhiều kiểu nhiễu hơn | Tập 1.200 topology (trước đây 40), lag 1 đến 3, nhiễu đuôi dày (Student-t, Laplace) và sai số đo | ☐ Đúng  ☐ Chỉnh |
| 5 | Cải thiện các metric ở RQ4.4 (AUROC) | Cờ độ tin cậy cần phân biệt tốt hơn cặp nào sẽ bị trượt | Dùng thêm đặc trưng quan sát được (độ rộng theo hàng và cột, khai báo hỏng, cấu trúc skeleton khai báo); đánh giá trên tập chưa dùng | ☐ Đúng  ☐ Chỉnh |
| 6 | Xem kỹ phần so sánh trong kết quả chính | Phép so sánh với các phương pháp tham chiếu phải công bằng | Hiệu chỉnh mọi phương pháp bằng cùng một quy tắc để so ở cùng mức đảm bảo; nêu rõ ngân sách tính toán và thông tin mỗi phương pháp dùng | ☐ Đúng  ☐ Chỉnh |
| 7 | Vẽ architecture | Sơ đồ khối tổng thể của phương pháp | Sơ đồ từ đầu vào (dữ liệu, skeleton, mức hỏng khai báo) đến khoảng tin cậy, gồm 6 bước | ☐ Đúng  ☐ Chỉnh |
| 8 | Giải thích số liệu trong các bảng kết quả | Mỗi bảng cần có đoạn hướng dẫn đọc: cột nào, hàng nào, kết luận gì | Viết đoạn "cách đọc bảng" ngay sau từng bảng; bổ sung bảng cho các mục hiện chỉ có văn bản | ☐ Đúng  ☐ Chỉnh |
| 9 | Tìm tài liệu tham khảo từ 2021 trở về sau | Cập nhật danh mục tham khảo gần đây, nhất là về conformal và bootstrap cho SVAR | Bổ sung các tài liệu từ 2021 đã kiểm tra nguồn; thêm vào phần Công trình liên quan | ☐ Đúng  ☐ Chỉnh |
| 10 | Ablation: tìm T hoặc mức hỏng mà module chịu lỗi hiện tại chạy được | Xác định ngưỡng cỡ mẫu và mức hỏng tối đa để phương pháp còn dùng được | Quét T, số lag và mức hỏng từ 10% đến 80%; báo T tối thiểu theo từng số lag | ☐ Đúng  ☐ Chỉnh |

**Cấu trúc bài đề xuất:** Giới thiệu, Công trình liên quan, Bài toán, Phương pháp, Bảo đảm lý thuyết, Thiết lập mô phỏng, **Kết quả chính** (mô phỏng: so sánh, mức hỏng, ablation), **Case study** (dữ liệu thật, section riêng), Thảo luận, Kết luận.  ☐ Đúng  ☐ Chỉnh

**Ghi chú của thầy:** ____________________________________________________________________
