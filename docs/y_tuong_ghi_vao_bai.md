# Ý tưởng cần ghi vào bài (chưa viết)

- B = 199: quy ước chọn B sao cho (B+1) chia hết cho 40, khi đó phân vị 2,5% và 97,5% rơi đúng vào hạng thứ 5 và 195 của 199 giá trị đã sắp xếp, không cần nội suy (Davison & Hinkley). Cần kiểm tra lại mã/spec xem nhóm có chủ đích này không trước khi viết thành câu khẳng định; nếu có thì thêm một câu ở mục thiết lập bootstrap.
- Cần thêm đoạn định nghĩa ngắn (cho người đọc không chuyên): bootstrap và khoảng bootstrap, hệ số c, điểm của một topology, bản biên và PAC, sàn lưới, cặp có hiệu ứng thật khác 0.

## Thiết kế bảng/hình đề xuất cho lần chỉnh sau (chưa làm, 2026-11-19)
Kết quả debate 3 vai (hình ảnh, phản biện thống kê, người đọc tối giản):
- A: ba bảng nhiệt theo lag, mỗi ô một số (tỉ lệ đạt ngưỡng bản biên), màu rời rạc quanh 0,90; ký hiệu ✓ (điểm ≥ 0,90), ≈ (điểm < 0,90 nhưng cận trên CI ≥ 0,90), ✗, "từ chối"; viền đậm ba ô lag 2 bị rút tuyên bố.
- B: biểu đồ chấm theo lag: AUROC tuyệt đối cờ mới/cũ/`-width` và chênh lệch kèm CI, đường +0,03. Lưu ý: AUROC `-width` chỉ có theo nhóm T trong kết quả, theo từng T phải tính lại từ dữ liệu đã lưu.
- C: bảng 8 hàng, interval score tuyệt đối, in đậm thấp nhất, † cho phương pháp không đạt mức đảm bảo, dòng "số ô thắng" (4/3/1); tỉ lệ đạt ngưỡng xuống phụ lục.
- D: một bảng 5 hàng (Gaussian, t4, Laplace, sai số đo 10%, 30%), hàng sai số đo tách theo T.
- E: bảng panel mô phỏng giữ cột "fit thành công". F: hệ số 0,5 chỉ ba câu trong thân bài, bảng ở phụ lục.
