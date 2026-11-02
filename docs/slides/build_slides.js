const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.title = "Paper 4: Dynamic SEM chịu lỗi skeleton";

const F = "Arial", MONO = "Courier New";
const INK = "111111", PAPER = "F4F4F2", GRAY = "555555", LGRAY = "BBBBBB", WHITE = "FFFFFF";
const TOTAL = 18;
let n = 0;

function base(section, dark) {
  const s = pres.addSlide();
  n += 1;
  s.background = { color: PAPER };
  s.addText(section, { x: 0.6, y: 7.0, w: 10.6, h: 0.3, fontFace: MONO, fontSize: 11, color: GRAY, margin: 0 });
  s.addText(`${n} / ${TOTAL}`, { x: 11.7, y: 7.0, w: 1.03, h: 0.3, fontFace: MONO, fontSize: 11, color: GRAY, align: "right", margin: 0 });
  return s;
}
function title(s, text, dark) {
  s.addText(text, { x: 0.6, y: 0.4, w: 12.1, h: 0.8, fontFace: F, fontSize: 30, bold: true, color: INK, margin: 0, valign: "middle" });
}
function card(s, x, y, w, h, head, body, o = {}) {
  const dark = false;
  s.addShape(pres.ShapeType.rect, { x, y, w, h, fill: { color: dark ? "1C1C1C" : WHITE }, line: { color: dark ? PAPER : INK, width: 1.5 } });
  s.addText(head, { x: x + 0.2, y: y + 0.12, w: w - 0.4, h: 0.45, fontFace: F, fontSize: o.hs || 16, bold: true, color: dark ? PAPER : INK, margin: 0, valign: "top" });
  s.addText(body, { x: x + 0.2, y: y + 0.6, w: w - 0.4, h: h - 0.72, fontFace: F, fontSize: o.bs || 14, color: dark ? INK : INK, margin: 0, valign: "top", paraSpaceAfter: 4 });
}
function bullets(items, size, color) {
  return items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1, fontSize: size, color: color || INK } }));
}
function table(s, rows, colW, x, y, o = {}) {
  const fs = o.fs || 14;
  const data = rows.map((r, i) => r.map((c, j) => ({
    text: String(c),
    options: i === 0
      ? { bold: true, color: PAPER, fill: { color: INK }, fontFace: F, fontSize: fs, valign: "middle" }
      : { color: INK, fill: { color: WHITE }, fontFace: (o.monoCol === j ? MONO : F), fontSize: fs, bold: o.boldCol === j, valign: "middle" },
  })));
  s.addTable(data, { x, y, w: colW.reduce((a, b) => a + b, 0), colW, rowH: o.rowH || 0.5, border: { type: "solid", pt: 0.75, color: "888888" }, margin: [0.04, 0.1, 0.04, 0.1] });
}

// 1 cover
{
  const s = base("", true);
  s.addText("UIT NCKH · PAPER 4", { x: 0.9, y: 0.9, w: 8, h: 0.4, fontFace: MONO, fontSize: 14, color: GRAY, charSpacing: 2, margin: 0 });
  s.addText("Ước lượng hiệu ứng động khi skeleton nhân quả có thể sai", { x: 0.9, y: 2.2, w: 11.3, h: 2.2, fontFace: F, fontSize: 44, bold: true, color: INK, margin: 0, valign: "top" });
  s.addText("Dynamic SEM chịu lỗi skeleton: phương pháp, baseline và kết quả", { x: 0.9, y: 4.5, w: 11, h: 0.7, fontFace: F, fontSize: 22, color: "333333", margin: 0 });
  s.addText("Trình bày để thảo luận nhóm", { x: 0.9, y: 6.3, w: 8, h: 0.4, fontFace: MONO, fontSize: 14, color: GRAY, margin: 0 });
  s.addNotes("Paper 4 hỏi một câu hẹp nhưng thực tế: skeleton đưa vào luôn có lỗi. Nếu vẫn dùng nó để ước lượng hiệu ứng động, interval có còn đúng không, và làm sao để nó vẫn trung thực. Thứ tự: cách dựng dữ liệu, interval và coverage, baseline, phương pháp chính, kết quả, hướng mở rộng.");
}

// 2 problem
{
  const s = base("Bài toán");
  title(s, "Skeleton đầu vào luôn có lỗi");
  card(s, 0.6, 1.5, 5.9, 2.6, "Skeleton đến từ đâu", bullets([
    "Paper 1: trích từ văn bản (LLM + chunk tin tức)",
    "Paper 2/3: học từ dữ liệu bằng GES",
    "Cả hai sai một phần: thiếu cạnh, thừa cạnh, đảo chiều",
  ], 20), { hs: 22 });
  card(s, 6.83, 1.5, 5.9, 2.6, "Paper 4 hỏi", bullets([
    "Dùng skeleton sai để ước lượng hiệu ứng động C(H): interval còn đúng 95% không?",
    "Làm sao ước lượng để interval vẫn trung thực?",
  ], 20), { hs: 22 });
  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 4.5, w: 12.13, h: 2.0, fill: { color: INK }, line: { color: INK } });
  s.addText([
    { text: "INPUT  ", options: { bold: true, fontFace: MONO } },
    { text: "dữ liệu T × 14 + skeleton (có thể sai) + số cạnh thiếu / thừa / đảo do người dùng khai báo (chỉ số lượng, không biết cạnh nào)", options: { breakLine: true } },
    { text: " ", options: { breakLine: true, fontSize: 8 } },
    { text: "OUTPUT ", options: { bold: true, fontFace: MONO } },
    { text: "hiệu ứng tích lũy C(H) cho mọi cặp biến, kèm interval 95%" },
  ], { x: 0.9, y: 4.65, w: 11.5, h: 1.7, fontFace: F, fontSize: 20, color: PAPER, margin: 0, valign: "middle" });
  s.addNotes("Skeleton ở đây là đồ thị: cặp nào nối nhau, chiều của cạnh cùng kỳ. Module nhận thêm một khai báo về mức hỏng: bao nhiêu cạnh thiếu, thừa, đảo, nhưng không cho biết cạnh nào.");
}

// 3 RQs
{
  const s = base("Bài toán");
  title(s, "Bốn câu hỏi nghiên cứu (plan mục 5.1)");
  const q = [
    ["RQ4.1", "Sai số cường độ và độ trễ thay đổi thế nào theo loại và mức hỏng của skeleton?"],
    ["RQ4.2", "Interval gộp bất định cấu trúc có coverage đúng danh nghĩa và hẹp hơn các cách báo một điểm không?"],
    ["RQ4.3", "Cạnh nào của skeleton, khi sai, làm hiệu ứng lệch nhiều nhất? Bản đồ này có ổn định qua các topology không?"],
    ["RQ4.4", "Có đại lượng quan sát được, không cần truth, dự báo được độ tin cậy của hiệu ứng không?"],
  ];
  q.forEach((r, i) => card(s, 0.6 + (i % 2) * 6.23, 1.5 + Math.floor(i / 2) * 2.65, 5.9, 2.4, r[0], r[1], { hs: 26, bs: 22 }));
  s.addNotes("Bốn câu hỏi nguyên văn từ plan của thầy. Đáp án ở slide 15.");
}

// 4 pipeline
{
  const s = base("Thiết lập thực nghiệm");
  title(s, "Quy trình một lượt thực nghiệm");
  const row = (y, label, texts) => {
    s.addText(label, { x: 0.6, y, w: 12, h: 0.3, fontFace: MONO, fontSize: 12, color: GRAY, margin: 0 });
    texts.forEach((t, i) => {
      const x = 0.6 + i * 4.3;
      s.addShape(pres.ShapeType.rect, { x, y: y + 0.38, w: 3.5, h: 0.95, fill: { color: WHITE }, line: { color: INK, width: 1.5 } });
      s.addText(t, { x: x + 0.1, y: y + 0.4, w: 3.3, h: 0.9, fontFace: F, fontSize: 17, color: INK, align: "center", valign: "middle", margin: 0 });
      if (i < texts.length - 1) s.addText("→", { x: x + 3.5, y: y + 0.38, w: 0.8, h: 0.95, fontFace: F, fontSize: 28, bold: true, color: INK, align: "center", valign: "middle", margin: 0 });
    });
  };
  row(1.45, "THẾ GIỚI THẬT (chỉ bước chấm điểm được thấy)", ["Topology 14 nút từ bank", "Gán lag + hệ số = true SVAR", "Dữ liệu T × 14 và C_true"]);
  row(3.1, "THỨ METHOD ĐƯỢC THẤY", ["True skeleton (bỏ lag, bỏ hệ số)", "Làm hỏng có kiểm soát: xóa / thêm / đảo", "Skeleton hỏng + số cạnh khai báo"]);
  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 4.95, w: 12.13, h: 1.6, fill: { color: INK }, line: { color: INK } });
  s.addText([
    { text: "Method: ", options: { bold: true } },
    { text: "dữ liệu + skeleton hỏng + khai báo  →  Ĉ(H) + interval 95%", options: { breakLine: true } },
    { text: "Chấm điểm: ", options: { bold: true } },
    { text: "so Ĉ và interval với C_true  →  coverage, interval score, sai số" },
  ], { x: 0.9, y: 5.0, w: 11.5, h: 1.5, fontFace: F, fontSize: 20, color: PAPER, margin: 0, valign: "middle", paraSpaceAfter: 8 });
  s.addNotes("Điểm mấu chốt: dữ liệu được sinh từ thế giới thật, còn method chỉ thấy skeleton đã bị làm hỏng. Nếu sinh dữ liệu từ chính skeleton đưa vào thì không còn lỗi nào để nghiên cứu.");
}

// 5 banks
{
  const s = base("Thiết lập thực nghiệm");
  title(s, "Build bộ data: topology bank");
  table(s, [
    ["Bank", "Nguồn", "Vai trò"],
    ["D-07", "Paper 2", "Development: phát triển và thử mọi method"],
    ["D-07H", "Paper 2 (held-out)", "Development: hiệu chỉnh width, không chấm điểm"],
    ["P4-H1", "Sinh cho Paper 4 (seed 20261102)", "Kiểm tra held-out vòng đầu"],
    ["P4-H2", "Sinh sau vòng 1 (seed 20261103), niêm phong", "Chạy xác nhận đúng một lần"],
  ], [1.5, 4.4, 6.2], 0.6, 1.5, { fs: 17, rowH: 0.66, monoCol: 0 });
  s.addText(bullets([
    "Mỗi bank: 40 đồ thị · 14 nút · 21 cạnh · 20 development + 20 confirmatory",
    "Hai họ đồ thị: Erdős–Rényi và hub (scale-free)",
    "Tên 14 nút là biến panel thật (7 ngân hàng, 3 vĩ mô, 4 chứng khoán); cấu trúc cạnh là ngẫu nhiên",
    "Niêm phong: P4-H2 chưa ai nhìn trước lượt chạy xác nhận, nên kết quả trên đó là bằng chứng độc lập",
  ], 17), { x: 0.6, y: 5.0, w: 12.1, h: 1.9, fontFace: F, color: INK, margin: 0, valign: "top", paraSpaceAfter: 6 });
  s.addNotes("D-07 đã dùng hàng chục lần để chỉnh method, nên kết quả trên đó gọi là exploratory. P4-H2 là bank niêm phong: kết quả trên đó gọi là xác nhận.");
}

// 5b status and data
{
  const s = base("Thiết lập thực nghiệm");
  title(s, "Exploratory và Confirmed: ý nghĩa và bộ dữ liệu");
  card(s, 0.6, 1.3, 5.9, 1.7, "Exploratory (thăm dò)", "Đo trên bank đã dùng để thiết kế và chỉnh method (D-07 development). Method có thể bị chỉnh theo chính bank đó, nên số có thể lạc quan. Dùng để tìm hướng, chưa để khẳng định.", { hs: 17, bs: 14 });
  card(s, 6.83, 1.3, 5.9, 1.7, "Confirmed (xác nhận)", "Đo trên bank chưa ai nhìn (P4-H2), quy tắc ghi trước khi chạy, chạy đúng một lần, báo cả kết quả không đạt. Bằng chứng độc lập.", { hs: 17, bs: 14 });
  table(s, [
    ["Kết quả", "Trạng thái", "Bộ dữ liệu (số bộ mô phỏng)"],
    ["Ours so với 7 baseline; biến thể không khai báo mức hỏng", "Confirmed", "P4-H2 confirmatory: 20 topology × 3 lần = 60 bộ mỗi cell"],
    ["Các vòng trước: so với baseline; biến ẩn; skeleton do GES", "Held-out", "P4-H1, D-07 confirmatory: 20 topology × 3 mỗi bank"],
    ["Vùng dùng được; nhiễu non-Gaussian; nhiễu đo; lag", "Exploratory", "D-07 development: 20 topology × 3 = 60 bộ mỗi cell"],
    ["RQ4.3 bản đồ chi phí theo cạnh", "Confirmed", "P4-H3 niêm phong: 40 topology (cả hai split), T = 2000"],
    ["RQ4.4 cờ tin cậy", "Confirmed", "P4-H3 niêm phong: 40 topology × 3, cờ đóng băng"],
    ["RQ4.1 đặc trưng sai số", "Not confirmed (3/4)", "P4-H3 niêm phong: 40 topology × 3"],
    ["Hiệu chỉnh width (calibration)", "Không chấm điểm", "D-07H development: 20 topology × 1"],
  ], [4.9, 1.9, 5.3], 0.6, 3.15, { fs: 12, rowH: 0.42, boldCol: 1 });
  s.addNotes("Held-out nghĩa là đã tái lập trên bank khác với bank phát triển, nhưng chưa theo quy trình niêm phong cuối cùng của P4-H2. Mọi bank hiện đã dùng hết; muốn xác nhận thêm cần bank niêm phong mới.");
}

// 6 data generation
{
  const s = base("Thiết lập thực nghiệm");
  title(s, "Giả lập dữ liệu: SVAR có ground truth");
  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 1.45, w: 12.13, h: 0.9, fill: { color: INK }, line: { color: INK } });
  s.addText("x_t = B0·x_t + B1·x_(t-1) + B2·x_(t-2) + e_t,   e_t ~ N(0, diag(σ²))", { x: 0.8, y: 1.45, w: 11.7, h: 0.9, fontFace: MONO, fontSize: 18, color: PAPER, valign: "middle", margin: 0 });
  const items = [
    ["Lag của mỗi cạnh", "Cùng kỳ (lag 0) với xác suất 0.3, còn lại ngẫu nhiên 1 hoặc 2 quý"],
    ["Hệ số cạnh", "|b| ~ U(0.3, 0.8), dấu ngẫu nhiên"],
    ["Tự hồi quy", "Hệ số lag 1 của mỗi nút ~ U(0.2, 0.6)"],
    ["Phương sai nhiễu", "σ² ~ U(0.5, 1.5) cho mỗi nút"],
    ["Ổn định", "Co phần lag đến khi bán kính companion < 0.9; burn-in 200"],
    ["Ground truth", "C_true = tổng IRF từ h = 0 đến 4, tính bằng công thức từ hệ số thật"],
  ];
  items.forEach((it, i) => card(s, 0.6 + (i % 2) * 6.23, 2.6 + Math.floor(i / 2) * 1.35, 5.9, 1.2, it[0], it[1], { hs: 17, bs: 15 }));
  s.addText("Cỡ mẫu T ∈ {40, 80, 150} (vùng dùng được: T từ 19). Một bộ dữ liệu = một true model + T × 14 quan sát.", { x: 0.6, y: 6.62, w: 12.1, h: 0.35, fontFace: F, fontSize: 14, color: GRAY, margin: 0 });
  s.addNotes("Các tham số này do nhóm đề xuất vì plan chưa quy định cách rút lag và hệ số. Chúng được ghi trong open_questions.md và chờ thầy quyết.");
}

// 7 damage
{
  const s = base("Thiết lập thực nghiệm");
  title(s, "Giả lập skeleton hỏng");
  table(s, [
    ["Loại hỏng", "Cách làm trên true skeleton", "Ảnh hưởng chính"],
    ["Thiếu cạnh", "Xóa k cạnh thật", "Nặng nhất: đường truyền dẫn bị cắt"],
    ["Thừa cạnh", "Thêm k cặp không có cạnh", "Gần như vô hại"],
    ["Đảo chiều", "Lật chiều k cạnh cùng kỳ", "Sai B0, sai cả lag"],
  ], [2.2, 5.0, 4.9], 0.6, 1.5, { fs: 18, rowH: 0.65, boldCol: 0 });
  card(s, 0.6, 4.35, 5.9, 2.3, "Mức hỏng", bullets([
    "Tỷ lệ 20% hoặc 50%",
    "k = floor(tỷ lệ × số cạnh + 0.5): 21 cạnh → k = 4 hoặc 11",
    "Đảo: k tính trên số cạnh cùng kỳ",
  ], 17), { hs: 20 });
  card(s, 6.83, 4.35, 5.9, 2.3, "Method được thấy gì", bullets([
    "Skeleton hỏng (cặp nối, chiều cạnh cùng kỳ)",
    "Số cạnh thiếu / thừa / đảo khai báo",
    "Không thấy: cạnh nào hỏng, lag, hệ số, C_true",
  ], 17), { hs: 20 });
  s.addNotes("Danh sách cạnh hỏng thật được ghi vào một log riêng chỉ bước chấm điểm đọc. Mỗi method nhận một bản skeleton đã xóa log và lag.");
}

// 8 interval and coverage
{
  const s = base("Thiết lập thực nghiệm");
  title(s, "Interval và coverage: bao nhiêu lần chạy?");
  card(s, 0.6, 1.45, 5.9, 3.2, "Trong MỘT bộ dữ liệu: interval", [
    { text: "1. Fit mô hình → B̂ và phần dư", options: { breakLine: true } },
    { text: "2. Sinh dữ liệu giả từ phần dư (bootstrap)", options: { breakLine: true } },
    { text: "3. Fit lại trên từng bộ giả (Ours: chọn lại cấu trúc ở mỗi lần)", options: { breakLine: true } },
    { text: "4. Lấy phân vị 2.5% và 97.5% của 199 giá trị Ĉ(H)" },
  ], { hs: 19, bs: 17 });
  card(s, 6.83, 1.45, 5.9, 3.2, "Trên NHIỀU bộ dữ liệu: coverage", [
    { text: "20 topology × 3 lần lặp = 60 bộ dữ liệu mỗi cell", options: { breakLine: true } },
    { text: "Mỗi bộ có khoảng 30–40 cặp có hiệu ứng thật (|C_true| > 0.1)", options: { breakLine: true } },
    { text: "Coverage = tỷ lệ interval chứa C_true trên khoảng 2000 phép kiểm", options: { breakLine: true } },
    { text: "Cặp mất đường truyền (Ĉ = 0) tính là trượt" },
  ], { hs: 19, bs: 17 });
  const big = [["199", "lần bootstrap\nmỗi bộ dữ liệu"], ["60", "bộ dữ liệu\nmỗi cell"], ["1260", "bộ dữ liệu mỗi method\n(3 cỡ T × 7 mức hỏng × 60)"]];
  big.forEach((b, i) => {
    const x = 0.6 + i * 4.1;
    s.addShape(pres.ShapeType.rect, { x, y: 4.95, w: 3.95, h: 1.75, fill: { color: INK }, line: { color: INK } });
    s.addText(b[0], { x, y: 5.0, w: 3.95, h: 0.9, fontFace: F, fontSize: 44, bold: true, color: PAPER, align: "center", valign: "middle", margin: 0 });
    s.addText(b[1], { x, y: 5.85, w: 3.95, h: 0.8, fontFace: F, fontSize: 15, color: "D0D0D0", align: "center", valign: "top", margin: 0 });
  });
  s.addNotes("Hai tầng lặp khác nhau. Tầng trong (bootstrap 199 lần) là một phần của method và ngoài đời cũng chạy được trên một bộ dữ liệu duy nhất. Tầng ngoài (60 bộ giả lập mỗi cell) chỉ có trong thực nghiệm, vì cần C_true. Mỗi method trong lượt chạy xác nhận được fit khoảng 1260 × 199 ≈ 250 nghìn lần.");
}

// 9 metrics
{
  const s = base("Thiết lập thực nghiệm");
  title(s, "Các metric chính");
  table(s, [
    ["Metric", "Định nghĩa", "Đọc thế nào"],
    ["Coverage", "Tỷ lệ interval chứa C_true", "Mục tiêu khoảng 0.95; thấp = tự tin quá mức"],
    ["Width", "hi − lo", "Hẹp tốt, nhưng chỉ khi coverage đạt"],
    ["Interval score (IS)", "width + 40 × khoảng cách trượt (α = 0.05)", "Thấp tốt; gộp độ rộng và việc trượt"],
    ["Sai số cường độ", "|Ĉ − C|, tuyệt đối và tương đối", "Mô tả (RQ4.1)"],
    ["Sai số lag", "Lệch mean lag; peak lag đúng", "Mô tả (RQ4.1)"],
  ], [2.6, 4.9, 4.6], 0.6, 1.5, { fs: 16, rowH: 0.62, boldCol: 0 });
  s.addText(bullets([
    "Vì sao cần IS: một interval cực rộng đạt coverage 100% nhưng vô dụng; interval cực hẹp thì trượt. IS phạt cả hai",
    "C(H) = tổng IRF từ h = 0 đến H, với H = 4 quý",
    "Không dùng F1 và SHD (theo plan)",
  ], 16), { x: 0.6, y: 5.45, w: 12.1, h: 1.4, fontFace: F, color: INK, margin: 0, valign: "top", paraSpaceAfter: 5 });
  s.addNotes("Interval score của Gneiting và Raftery. Hệ số 40 = 2/α với α = 0.05. Báo cáo kèm so sánh ghép cặp và CI bootstrap theo topology, hiệu chỉnh Holm khi so nhiều cell.");
}

// 10 baselines
{
  const s = base("Baseline và phương pháp");
  title(s, "Các baseline");
  table(s, [
    ["Baseline", "Cách làm", "Vai trò"],
    ["plugin", "Tin skeleton tuyệt đối, bootstrap phần dư", "Cách làm thông thường"],
    ["inflate", "Interval của plugin nhân hằng số c", "Cách chữa rẻ nhất"],
    ["lp_allpast", "Local projection trên mọi lag (2021)", "Không tin skeleton"],
    ["IDA-union", "Union qua lớp tương đương (2009)", "Bất định về chiều cạnh"],
    ["BVAR Minnesota", "Mọi lag, prior siết ngoài skeleton", "Co hệ số về 0"],
    ["pselect_union", "Chọn lại cạnh từ dữ liệu, union (2026)", "Baseline mạnh nhất"],
    ["Targeted LP", "Co LP về SVAR, double bootstrap (2026)", "Baseline mới nhất"],
  ], [2.4, 6.0, 3.7], 0.6, 1.4, { fs: 15, rowH: 0.55, monoCol: 0 });
  s.addText("Oracle (fit trên đồ thị thật) là mốc tham chiếu. Nguồn: Montiel Olea & Plagborg-Møller 2021 · Maathuis et al. 2009 · Chang, Guo & Malinsky 2026 · Nemtyrev & Boldea 2026.", { x: 0.6, y: 5.95, w: 12.1, h: 0.5, fontFace: F, fontSize: 12, color: GRAY, margin: 0 });
  s.addText("Lưu ý: plan chỉ nói \"baseline báo một điểm\". Cách làm cụ thể và danh sách này do nhóm đề xuất, chưa được thầy duyệt. plugin không phải method của Paper 2.", { x: 0.6, y: 6.45, w: 12.1, h: 0.5, fontFace: F, fontSize: 13, bold: true, color: INK, margin: 0 });
  s.addNotes("plugin nghĩa là cắm skeleton thẳng vào mô hình như thể nó đúng. Bootstrap của plugin giữ nguyên skeleton ở mọi lần lặp nên chỉ đo nhiễu dữ liệu, không đo bất định cấu trúc.");
}

// 11 method
{
  const s = base("Baseline và phương pháp", true);
  title(s, "Phương pháp đề xuất: Ours", true);
  const st = [
    ["1  Bằng chứng", "F-test lag + tương quan phần dư của từng cặp ngoài skeleton, trong phương trình cấu trúc"],
    ["2  Mở lag có chọn lọc", "Chỉ K cặp có bằng chứng mạnh nhất, không mở lag của cả 14 biến"],
    ["3  Sửa cạnh cùng kỳ", "Thêm lại cạnh nghi thiếu (Benjamini–Hochberg); chiều rút ngẫu nhiên"],
    ["4  Lật chiều", "Mỗi draw lật r cạnh cùng kỳ có hệ số đáng kể (|t| > 1.645)"],
    ["5  Bootstrap", "Mỗi draw chạy lại bước 1–4 trên dữ liệu giả; 199 draw; phân vị 2.5–97.5%"],
    ["6  Hiệu chỉnh width", "Hệ số theo (T, loại hỏng) tune ở bank riêng; có thể nhỏ hơn 1"],
  ];
  st.forEach((r, i) => card(s, 0.6 + (i % 3) * 4.1, 1.5 + Math.floor(i / 3) * 2.3, 3.95, 2.1, r[0], r[1], { dark: true, hs: 19, bs: 16 }));
  s.addText("Bootstrap có chọn lại cấu trúc ở mỗi draw chính là \"gộp bất định cấu trúc\" của RQ4.2. Hiệu chỉnh width ở bước 6 cho phép thu hẹp lẫn nới rộng interval. (Mã: tolerant_v5_1)", { x: 0.6, y: 6.2, w: 12.1, h: 0.7, fontFace: F, fontSize: 15, color: INK, margin: 0, valign: "top" });
  s.addNotes("Khai báo mức hỏng quyết định có mở lag hay không: K = max(3 × số cạnh thiếu khai báo, số cặp có p < 0.10). Khi khai báo không có cạnh thiếu, method không mở thêm lag và chỉ dùng skeleton như được cho.");
}

// 12 results
{
  const s = base("Kết quả · Confirmed · P4-H2 confirmatory, 60 bộ mỗi cell");
  title(s, "Kết quả chính: Ours so với 7 baseline (P4-H2)");
  s.addText("Interval score (coverage), thiếu cạnh; IS thấp hơn = tốt hơn", { x: 0.6, y: 1.3, w: 12, h: 0.35, fontFace: F, fontSize: 14, color: GRAY, margin: 0 });
  table(s, [
    ["Method", "T80 · 20%", "T80 · 50%", "T150 · 20%", "T150 · 50%"],
    ["Ours", "2.68 (0.963)", "2.89 (0.969)", "1.75 (0.964)", "1.99 (0.960)"],
    ["pselect_union_v3", "3.46 (0.968)", "3.41 (0.978)", "2.15 (0.983)", "2.30 (0.988)"],
    ["pselect_union_v3_cal", "3.30 (0.943)", "3.20 (0.952)", "1.95 (0.950)", "2.04 (0.959)"],
    ["pselect_cal", "3.91 (0.962)", "4.12 (0.943)", "2.62 (0.972)", "3.06 (0.937)"],
    ["fullvar_cal", "3.41 (0.973)", "3.74 (0.953)", "2.62 (0.976)", "3.01 (0.953)"],
    ["targeted_lp_cal", "3.50 (0.955)", "3.75 (0.940)", "2.22 (0.979)", "2.43 (0.962)"],
    ["tlp2_db_p3", "3.71 (0.872)", "4.83 (0.804)", "2.21 (0.905)", "2.88 (0.857)"],
    ["bvar_minnesota_v2_cal", "4.64 (0.969)", "4.44 (0.969)", "3.72 (0.953)", "3.79 (0.957)"],
  ], [3.7, 2.1, 2.1, 2.1, 2.1], 0.6, 1.75, { fs: 15, rowH: 0.5, boldCol: 0 });
  s.addText(bullets([
    "Ours có IS thấp nhất ở cả 4 cell và coverage 0.96–0.97",
    "Baseline được hiệu chỉnh width bằng cùng quy trình; mọi so sánh ghép cặp trên cùng dữ liệu",
  ], 15), { x: 0.6, y: 6.35, w: 12.1, h: 0.6, fontFace: F, color: INK, margin: 0, valign: "top", paraSpaceAfter: 3 });
  s.addNotes("Nguồn: results/ext_baselines3_p4h2/ruling.md. Bảy baseline: pselect_union_v3 và bản hiệu chỉnh, pselect_cal, fullvar_cal (mở mọi lag), targeted_lp_cal, tlp2_db_p3 (double bootstrap), bvar_minnesota_v2_cal.");
}

// 13 differences
{
  const s = base("Kết quả · Confirmed · P4-H2 confirmatory, 60 bộ mỗi cell");
  title(s, "Ours − baseline: hiệu interval score (âm = Ours tốt hơn)");
  table(s, [
    ["Baseline", "T80 · 20%", "T80 · 50%", "T150 · 20%", "T150 · 50%"],
    ["pselect_union_v3", "−0.78", "−0.51", "−0.41", "−0.30"],
    ["pselect_union_v3_cal", "−0.61", "−0.30", "−0.20", "−0.05  hòa"],
    ["pselect_cal", "−1.22", "−1.22", "−0.87", "−1.07"],
    ["fullvar_cal", "−0.72", "−0.85", "−0.87", "−1.02"],
    ["targeted_lp_cal", "−0.82", "−0.85", "−0.47", "−0.44"],
    ["tlp2_db_p3", "−1.02", "−1.93", "−0.46", "−0.89"],
    ["bvar_minnesota_v2_cal", "−1.96", "−1.54", "−1.97", "−1.80"],
  ], [3.7, 2.1, 2.1, 2.1, 2.1], 0.6, 1.4, { fs: 16, rowH: 0.52, boldCol: 0 });
  s.addText(bullets([
    "27/28 so sánh Ours thắng có ý nghĩa (CI 95% không chứa 0, Holm trên 56 so sánh); không so sánh nào thua",
    "Hòa duy nhất: pselect_union_v3_cal ở T150 · 50% (−0.05, CI [−0.17, +0.04]); baseline này dùng gấp 32 lần số bootstrap draw",
  ], 16), { x: 0.6, y: 5.75, w: 12.1, h: 1.1, fontFace: F, color: INK, margin: 0, valign: "top", paraSpaceAfter: 5 });
  s.addNotes("pselect_union là bản chuyển thể của nhóm từ Chang, Guo và Malinsky; baseline mạnh nhất phụ thuộc ngân sách tính toán nên bảng chính cần cột budget.");
}

// 14 analysis
{
  const s = base("Kết quả · Confirmed (P4-H2) và exploratory (plugin trên D-07)");
  title(s, "Phân tích kết quả");
  const big = [["0.96–0.97", "Coverage của Ours ở 4 cell thiếu cạnh\n(P4-H2)"], ["27 / 27", "so sánh thắng baseline\nđược tái lập trên P4-H2"], ["0.33", "Coverage của plugin khi thiếu 50% cạnh\n(exploratory, D-07)"]];
  big.forEach((b, i) => {
    const x = 0.6 + i * 4.1;
    s.addShape(pres.ShapeType.rect, { x, y: 1.45, w: 3.95, h: 1.8, fill: { color: INK }, line: { color: INK } });
    s.addText(b[0], { x, y: 1.5, w: 3.95, h: 0.9, fontFace: F, fontSize: 34, bold: true, color: PAPER, align: "center", valign: "middle", margin: 0 });
    s.addText(b[1], { x, y: 2.4, w: 3.95, h: 0.8, fontFace: F, fontSize: 15, color: "D0D0D0", align: "center", valign: "top", margin: 0 });
  });
  s.addText(bullets([
    "Thiếu cạnh là lỗi nặng nhất: plugin hẹp nhưng sai nên coverage chỉ 0.33–0.66; cạnh thừa gần như vô hại",
    "Mở lag của mọi biến ở T = 40 cần 28 biến hồi quy trên 38 dòng nên interval phình rộng; Ours chỉ mở lag cho cặp có bằng chứng",
    "Từ T150 lợi thế thu hẹp: baseline mạnh nhất hòa với Ours",
    "Ours rộng hơn plugin, vì plugin hẹp mà sai. RQ4.2 nên phát biểu lại theo interval score thay vì độ rộng",
    "Biên thắng phụ thuộc ngân sách bootstrap của baseline: bản pselect đủ ngân sách mạnh hơn nhiều bản rút gọn",
  ], 20), { x: 0.6, y: 3.55, w: 12.1, h: 3.4, fontFace: F, color: INK, margin: 0, valign: "top", paraSpaceAfter: 7 });
  s.addNotes("Con số plugin 0.33 lấy từ lượt chạy exploratory trên D-07; Ours 0.96–0.97 lấy từ P4-H2. Hai con số khác bank nên chỉ để thấy cỡ độ lớn.");
}

// 15 RQ results
{
  const s = base("Kết quả · nguồn dữ liệu ghi trong từng ô bên phải");
  title(s, "Trả lời các câu hỏi nghiên cứu");
  const rq = [
    ["RQ4.1", "Thiếu cạnh nặng nhất (plugin: sai số tương đối khoảng 1.0, coverage 0.32–0.35 khi thiếu 50%); đạt 3/4 tiêu chí; trượt ở T40, nơi dữ liệu không tách được cạnh đảo khỏi cạnh thừa.", "Not confirmed", "P4-H3: đạt 3/4 tiêu chí"],
    ["RQ4.2", "Coverage đạt danh nghĩa. Interval rộng hơn plugin nhưng IS thấp hơn mọi baseline đã thử ở T ≥ 80 (hòa ở một cell T150). Nên phát biểu lại theo IS.", "Xác nhận", "P4-H2 confirmatory"],
    ["RQ4.3", "Chi phí dồn vào cạnh nằm trên đường truyền dẫn (lệch 81–93%). Bản đồ ổn định giữa các topology (Spearman 0.97–0.99; P4-H3: 0.99 và 0.97).", "Xác nhận", "P4-H3 niêm phong, T = 2000"],
    ["RQ4.4", "Cờ logistic (width, relative width, mức hỏng) AUROC 0.73 ở T ≥ 80 và 0.82 ở T40 (P4-H3: 0.72 và 0.81); cặp bị gắn cờ trượt nhiều gấp 4–7 lần.", "Xác nhận", "P4-H3 niêm phong, cờ đóng băng"],
  ];
  rq.forEach((r, i) => {
    const y = 1.4 + i * 1.3;
    s.addShape(pres.ShapeType.rect, { x: 0.6, y, w: 1.5, h: 1.2, fill: { color: INK }, line: { color: INK } });
    s.addText(r[0], { x: 0.6, y, w: 1.5, h: 1.2, fontFace: MONO, fontSize: 18, bold: true, color: PAPER, align: "center", valign: "middle", margin: 0 });
    s.addShape(pres.ShapeType.rect, { x: 2.1, y, w: 8.5, h: 1.2, fill: { color: WHITE }, line: { color: INK, width: 1.5 } });
    s.addText(r[1], { x: 2.25, y, w: 8.2, h: 1.2, fontFace: F, fontSize: 16, color: INK, valign: "middle", margin: 0 });
    s.addShape(pres.ShapeType.rect, { x: 10.6, y, w: 2.13, h: 1.2, fill: { color: r[2] === "Xác nhận" ? INK : WHITE }, line: { color: INK, width: 1.5 } });
    s.addText([{ text: r[2], options: { bold: true, fontSize: 15, breakLine: true } }, { text: r[3], options: { bold: false, fontSize: 11 } }], { x: 10.6, y, w: 2.13, h: 1.2, fontFace: F, color: r[2] === "Xác nhận" ? PAPER : INK, align: "center", valign: "middle", margin: 0 });
  });
  s.addText("Xác nhận = bank niêm phong (P4-H2, P4-H3), chạy một lần. Not confirmed = đã chạy, không đạt quy tắc ghi trước.", { x: 0.6, y: 6.62, w: 12.1, h: 0.3, fontFace: F, fontSize: 11, color: GRAY, margin: 0 });
  s.addNotes("RQ4.2: plan hỏi interval có hẹp hơn không. Thực tế module rộng hơn plugin vì plugin hẹp mà sai; thước đo hợp lý là interval score.");
}

// 16 region and limits
{
  const s = base("Giới hạn và hướng mở rộng");
  title(s, "Vùng dùng được và giới hạn");
  s.addText("T tối thiểu khi thiếu cạnh (exploratory, D-07 development)", { x: 0.6, y: 1.4, w: 6.2, h: 0.4, fontFace: F, fontSize: 15, bold: true, color: INK, margin: 0 });
  table(s, [["lag_max", "T tối thiểu (Ours)"], ["1", "19"], ["2", "40"], ["4", "80"]], [2.3, 3.9], 0.6, 1.9, { fs: 20, rowH: 0.62, boldCol: 0 });
  s.addText(bullets([
    "Với lag_max = 1, panel thật 14 × 19 nằm trong vùng dùng được của Ours",
    "Ở lag_max = 2, T < 40: nhiều phương trình không ước lượng được kể cả plugin",
  ], 17), { x: 0.6, y: 4.6, w: 6.2, h: 1.6, fontFace: F, color: INK, margin: 0, valign: "top", paraSpaceAfter: 5 });
  card(s, 7.2, 1.4, 5.53, 5.1, "Giới hạn đã đo", bullets([
    "Nhiễu đo 30%: coverage chỉ 0.77–0.89",
    "Cạnh đảo: coverage trên cặp bị ảnh hưởng thấp hơn oracle 0.06–0.08",
    "Chỉ SVAR tuyến tính, 14 nút, một generator",
    "Baseline mạnh nhất do nhóm chuyển thể",
    "Mọi bank đã dùng; claim xác nhận thêm cần bank mới",
    "Hệ số width tune trên bank riêng (reviewer có thể chất vấn)",
  ], 18), { hs: 22 });
  s.addNotes("Vùng dùng được: một ô dùng được nếu có ít nhất 57/60 run chạy được, coverage ≥ 0.90 và IS không quá 3 lần oracle.");
}

// 17 discuss
{
  const s = base("Giới hạn và hướng mở rộng", true);
  title(s, "Hướng mở rộng và câu hỏi thảo luận", true);
  card(s, 0.6, 1.45, 5.9, 5.2, "Hướng mở rộng", bullets([
    "Case study dữ liệu thật 14 × 19 (lag_max = 1); cần kiểm tra cột lãi suất",
    "Nhiễu đo: hiệu chỉnh errors-in-variables",
    "Chiều cạnh cùng kỳ: non-Gaussian, proxy từ văn bản / LLM",
    "Hàm lạm phát để mở rộng T (plan chưa định nghĩa)",
    "Generator khác: phi tuyến, nhiễu đuôi dày, nhiều nút",
  ], 20, INK), { dark: true, hs: 24 });
  card(s, 6.83, 1.45, 5.9, 5.2, "Để thảo luận", bullets([
    "RQ4.2 phát biểu lại theo interval score có hợp lý không?",
    "Danh sách baseline đã đủ chưa, còn thiếu gì?",
    "Giữ biến thể không cần khai báo mức hỏng (auto3) trong paper?",
    "Text / LLM thuộc Bài 4 hay Bài 5?",
  ], 20, INK), { dark: true, hs: 24 });
  s.addNotes("Bốn câu hỏi thảo luận trùng với bốn việc cần thầy quyết.");
}

pres.writeFile({ fileName: "paper4_presentation.pptx" }).then(f => console.log("wrote", f));
