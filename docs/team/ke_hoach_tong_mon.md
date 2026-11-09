# Kế hoạch dựng "tông môn" học tập: Discord + GitHub + Obsidian + LaTeX

Mục tiêu: một nhóm học tập (môn cao học và nghiên cứu khoa học) có chỗ trao đổi, kho tri thức chung, quản lý code và bài viết, mà không bị ngập thông báo.

Nguyên tắc xuyên suốt (nếu chỉ nhớ năm dòng):
1. **Mỗi thứ có đúng một nơi là nguồn sự thật.** Code và LaTeX ở Git. Ghi chú và tri thức ở Obsidian vault (cũng là Git). Deadline và lịch họp ở một lịch duy nhất. Discord chỉ là nơi *trao đổi và nhận thông báo*, không lưu tài liệu.
2. **Kênh chia theo chức năng, thread/forum chia theo chủ đề.** Không tạo một kênh mới cho mỗi bài tập hay mỗi lần họp.
3. **Kênh bot (GitHub, bản tin) tách khỏi kênh người nói chuyện**, và mặc định tắt thông báo.
4. **Thông báo có chọn lọc:** chỉ những sự kiện cần hành động mới được ping.
5. **Bí mật không đi qua Discord:** API key, `.env`, URL webhook, dữ liệu chưa công bố.

---

## Trạng thái thực tế (cập nhật 2026-11-09)

Các mục bên dưới là kế hoạch ban đầu. Khi khác với bảng này thì bảng này đúng.

| Hạng mục | Thực tế |
|---|---|
| GitHub Organization | `Heavenly-Secrets-Sect` (Thiên Cơ Môn, tiếng Anh: Heavenly Secrets Sect) |
| Repo nghiên cứu | `paper4-uit` (Paper 4) |
| Repo vault Obsidian | `knowledge-base`, một vault chung cho mọi dự án và môn học |
| Server Discord | Thiên Cơ Môn, bản rút gọn. Tên kênh viết theo kiểu tiên hiệp có dấu, phần mô tả (topic) ghi nghĩa hiện đại. Tên kênh trong Discord là chuẩn, tên kênh trong các mục dưới chỉ là tên thiết kế |
| Webhook GitHub → Discord | Đặt ở cấp organization, gửi vào `thiên-cơ-báo`, URL thêm `/github`. Sự kiện: Pull requests, Issues, Releases. Không bật Pushes (xem mục 4) |
| Jira | `thiencomon.atlassian.net`, một project `KAN` (Kanban), tách việc bằng Epic. Không dùng Confluence |

Secret của GitHub Actions và kênh Discord tương ứng:

| Secret | Kênh | Workflow |
|---|---|---|
| `DISCORD_WEBHOOK_DIGEST` | `thiên-cơ-báo` | `daily-digest` (có ở `paper4-uit` và `knowledge-base`) |
| `DISCORD_WEBHOOK_REMINDER` | `thiên-kiếp-bảng` | `deadline-reminder` |
| `DISCORD_WEBHOOK_LOG` | `hộ-sơn-đại-trận` | `notify-failure` |

Secret có thể đặt ở cấp organization nếu phạm vi repo của secret gồm repo cần dùng. Quy trình đưa nội dung đã chốt lên Confluence (chưa dựng) ở [quy_trinh_phat_hanh_tri_thuc.md](quy_trinh_phat_hanh_tri_thuc.md).

---

## 1. Quyết định cần chốt trước (Phase 0)

| # | Câu hỏi | Gợi ý mặc định |
|---|---|---|
| 1 | Server riêng tư hay công khai? | Riêng tư, vào bằng link mời có hạn |
| 2 | Có thầy/anh hướng dẫn trong server không? | Có, vai trò `Trưởng Lão`, chỉ thấy kênh dành cho họ |
| 3 | Ngôn ngữ chính | Tiếng Việt, giữ thuật ngữ tiếng Anh |
| 4 | Bao nhiêu người? | Dưới 10 người thì giữ ít kênh; trên 10 mới chia nhiều |
| 5 | LaTeX: Git hay Overleaf? | Git là nguồn chính (xem mục 5) |
| 6 | Ai là admin dự phòng? | Ít nhất 2 người có quyền Admin (tránh một người rời đi là mất server) |
| 7 | GitHub: tài khoản cá nhân hay Organization? | Tạo một Organization miễn phí cho nhóm |

---

## 2. Cách đặt tên "tu tiên"

Quy ước: **tên tiên hiệp + nghĩa thường** để người mới không phải đoán. Ví dụ `tang-kinh-cac` kèm mô tả kênh "kho tài liệu". Tên kênh Discord cho phép dấu tiếng Việt, nhóm dùng tên tiên hiệp có dấu và ghi nghĩa hiện đại trong mô tả kênh. Tên file và thư mục trong vault vẫn viết không dấu (xem mục 6.1).

| Tên tiên hiệp | Nghĩa thường | Dùng cho |
|---|---|---|
| Tông môn | Server | Toàn bộ nhóm |
| Tông Chủ | Owner | Chủ server |
| Trưởng Lão | Mentor / supervisor | Thầy, anh hướng dẫn |
| Chấp Sự | Admin, moderator | Người quản lý kỹ thuật và quy tắc |
| Đệ Tử | Thành viên | Mọi người trong nhóm |
| Ký Danh | Khách, người mới | Người chưa đủ quyền, chỉ xem |
| Tàng Kinh Các | Thư viện, knowledge base | Obsidian vault, tài liệu, paper đã đọc |
| Truyền Công Đường | Thông báo, quy tắc, onboarding | Kênh chung |
| Thiên Cơ Các | Lịch, deadline, nhắc việc | Một kênh duy nhất cho nhắc nhở |
| Nghị Sự Điện | Họp | Ghi chú và biên bản họp |
| Luyện Đan Phòng | Chạy thực nghiệm, tính toán | Kết quả chạy, log, benchmark |
| Chấp Pháp Đường | Review code, review bài | Pull request, góp ý bản thảo |
| Đì Bấc Lâu | Debug | Hỏi và xử lý lỗi (tên do bạn đề xuất) |
| Bí Cảnh | Một dự án/paper | Một nhóm kênh cho mỗi paper |
| Tạp Dịch Viện | Việc vặt, trò chuyện | Off-topic |
| Vạn Bảo Các | Tool, công cụ, mẹo | Chia sẻ phần mềm, extension, thủ thuật |

Gợi ý nhỏ: tên role và category dùng tiên hiệp, còn **tên repo và file giữ tiếng Anh/Việt thường** (ví dụ `paper4-uit`), để công cụ và người ngoài nhóm không bị rối.

---

## 3. Cấu trúc Discord

### 3.1 Bật Community
Discord cần bật chế độ **Community** (Server Settings, Enable Community) mới có **Forum channel** và **Announcement channel**. Việc bật yêu cầu chọn một kênh quy tắc và một kênh cập nhật. Cả hai sẽ dùng `truyen-cong-duong`.

### 3.2 Sơ đồ kênh (bản đề xuất, khoảng 20 kênh)

```
TÔNG MÔN (category: chung)
  #truyen-cong-duong      Announcement: quy tắc, thông báo quan trọng, onboarding
  #thien-co-cac           CHỈ bot và Chấp Sự: deadline, lịch họp, nhắc việc
  #ban-tin-hang-ngay      CHỈ bot: bản tin tổng hợp mỗi ngày (xem mục 6)
  #nghi-su-dien           Chat họp; biên bản đưa lên Obsidian rồi link vào đây
  #tap-dich-vien          Off-topic
  #van-bao-cac            Tool, thủ thuật

TÀNG KINH CÁC (category: tri thức)
  #tang-kinh-cac          Forum: thảo luận paper/tài liệu, mỗi bài một post, gắn tag
  #cap-nhat-vault         CHỈ bot: thông báo vault (đã lọc, xem mục 6)

MÔN HỌC (category: học kỳ hiện tại)
  #mh-<ten-mon>           Forum cho mỗi môn: mỗi bài tập/chủ đề một post
                          Tag: bai-tap, de-thi, ghi-chu, huong-dan, deadline

BÍ CẢNH: PAPER 4 (category cho mỗi dự án nghiên cứu đang hoạt động)
  #p4-tro-chuyen          Trao đổi hằng ngày
  #p4-luyen-dan-phong     Kết quả chạy, log, số liệu (người đăng)
  #p4-chap-phap           Review PR, góp ý bản thảo (có thể dùng forum)
  #p4-github              CHỈ bot: thông báo repo (xem mục 4)

ĐÌ BẤC LÂU
  #di-bac-lau             Forum: mỗi lỗi một post, tag: da-xu-ly, dang-xu-ly, can-giup

QUẢN TRỊ (ẩn với Đệ Tử)
  #chap-su                Chấp Sự trao đổi nội bộ
  #bot-log                Lỗi của webhook, bot, Actions
```

**Giới hạn chống phình to:**
- Mỗi Bí Cảnh có **tối đa 4 kênh**. Cần thêm thì dùng thread hoặc forum post.
- Môn học dùng **một forum mỗi môn**, không phải một kênh mỗi bài tập.
- Khi hết học kỳ: chuyển category môn học vào `Archive` (khóa quyền gửi, giữ lại đọc). Đừng xóa.
- Khi paper nộp xong: đổi tên category thành `[Xong] Paper 4`, chuyển xuống cuối, chỉ giữ `#p4-github` nếu repo còn cập nhật.

### 3.3 Roles và quyền

| Role | Quyền chính |
|---|---|
| Tông Chủ | Owner (không dùng hằng ngày) |
| Chấp Sự | Manage Channels, Manage Webhooks, Manage Threads, Manage Events |
| Trưởng Lão | Xem mọi kênh, gửi tin ở kênh trao đổi; không cần quyền quản trị |
| Đệ Tử | Xem và gửi tin, tạo thread; không quản lý webhook |
| Ký Danh | Chỉ xem `#truyen-cong-duong` |
| `@p4`, `@mh-xxx` | Role theo dự án/môn, dùng để mention và mở quyền xem category |

Quyền chi tiết:
- Kênh bot (`#p4-github`, `#cap-nhat-vault`, `#ban-tin-hang-ngay`, `#thien-co-cac`): tắt "Send Messages" với Đệ Tử; webhook vẫn gửi được. Mọi người vẫn trả lời được bằng thread nếu bật "Create Public Threads".
- Chỉ **Chấp Sự** được quản lý webhook, vì URL webhook là bí mật (ai có URL là gửi được tin giả).

### 3.4 Cài đặt thông báo mặc định (rất quan trọng)
- Server Settings, Notification Settings, mặc định **Only @mentions**.
- Mỗi người **mute** các kênh bot, trừ `#thien-co-cac`.
- `#thien-co-cac` dùng `@everyone` **rất hạn chế** (một lần khi có deadline hoặc họp). Nhắc thường ngày dùng role (`@p4`, `@mh-xxx`).
- Gợi ý với người hay quên: bật thông báo cho Scheduled Event (mục 6.3).

---

## 4. Webhook GitHub: quy tắc lọc

### 4.1 Cách kết nối
Discord có endpoint tương thích GitHub: tạo webhook cho kênh bot (Channel Settings, Integrations, Webhooks), copy URL, thêm đuôi `/github`. Nhóm đặt webhook ở **cấp organization** (Organization Settings, Webhooks) để mọi repo hiện tại và repo mới đều gửi về cùng một kênh. Webhook organization không lọc được theo repo, chỉ lọc theo loại sự kiện. Cách đặt ở cấp repo giống nhau, tại repo Settings, Webhooks, Add webhook:
- Payload URL: URL Discord + `/github`
- Content type: `application/json`
- Chọn **"Let me select individual events"** (không chọn "Send me everything").

URL webhook là bí mật: không dán vào chat, không commit vào repo, lưu trong password manager. Nếu lộ thì xóa và tạo lại.

### 4.2 Sự kiện nên bật và nên tắt

| Sự kiện | Bật? | Lý do |
|---|---|---|
| Pushes | Tắt ở webhook organization | Repo vault tự commit mỗi vài phút nên sẽ ngập kênh. Tin commit lấy từ bản tin hằng ngày. Nếu một repo code cần tin push thì thêm webhook riêng cho repo đó (xem 4.3 để giảm nhiễu) |
| Pull requests | Bật | Cần review |
| Issues | Bật | Việc cần làm |
| Releases | Bật | Mốc quan trọng |
| Workflow runs | Chỉ khi cần | Nhiều nhiễu; xem 4.4 để chỉ báo khi fail |
| Issue comments, PR review comments | Tắt | Quá nhiều; bình luận xem trên GitHub |
| Stars, Watches, Forks | Tắt | Không cần hành động |
| Check runs, Check suites | Tắt | Trùng với workflow runs |
| Branch/tag creation | Tắt | Ít giá trị |

### 4.3 Giảm nhiễu từ push
- **Bảo vệ nhánh `main`:** chỉ cho merge qua Pull Request. Khi đó thông báo chủ yếu là PR, không phải từng commit lẻ.
- Quy ước nhánh: `feat/...`, `fix/...`, `docs/...`, `exp/...`.
- Commit message dạng ngắn rõ ràng (`feat: ...`, `fix: ...`, `docs: ...`, `exp: ...`). Điều này cũng giúp bản tin hằng ngày dễ đọc.
- GitHub webhook **không** có bộ lọc theo nhánh. Nếu muốn chỉ báo push vào `main`, dùng GitHub Actions gửi tin (mục 4.4) thay vì webhook trực tiếp.

### 4.4 Cách linh hoạt hơn: GitHub Actions gửi tin
Dùng khi muốn kiểm soát nội dung và điều kiện. Lưu URL vào **repository secret** `DISCORD_WEBHOOK`, không ghi vào file.

```yaml
# .github/workflows/notify-main.yml
name: notify-main
on:
  push:
    branches: [main]
jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Post to Discord
        env:
          WEBHOOK: ${{ secrets.DISCORD_WEBHOOK }}
          MSG: ${{ github.event.head_commit.message }}
          AUTHOR: ${{ github.event.head_commit.author.name }}
          URL: ${{ github.event.head_commit.url }}
        run: |
          jq -n --arg c "**$AUTHOR** vừa cập nhật main: $MSG $URL" '{content:$c, allowed_mentions:{parse:[]}}' \
            | curl -sS -H "Content-Type: application/json" -d @- "$WEBHOOK"
```

Tương tự có thể làm workflow báo khi build LaTeX hoặc test **thất bại** (điều kiện `if: failure()`), thay vì báo mọi lần chạy. Cần kiểm tra lại nội dung tin (dài, ký tự đặc biệt) sau khi thử.

### 4.5 Bố trí theo repo
- Thực tế: một webhook organization gửi sự kiện của mọi repo vào `thiên-cơ-báo`. Bản tin hằng ngày của từng repo cũng vào kênh này.
- Repo vault Obsidian **không** có tin push (xem 6.2), vì auto-commit sinh rất nhiều tin. Bản tin hằng ngày của vault liệt kê ghi chú mới hoặc đổi.

---

## 5. Git, LaTeX và Overleaf

### 5.1 Tổ chức repo
- **Một repo cho mỗi paper** (ví dụ `paper4-uit`): code, dữ liệu nhỏ, LaTeX trong `docs/latex/`.
- **Một repo cho vault** (`knowledge-base`): ghi chú Obsidian, dùng chung cho mọi dự án và môn học.
- **Repo mẫu/chung** (tùy chọn): template LaTeX, template ghi chú, script.
- GitHub **Organization** `Heavenly-Secrets-Sect` đã tạo; quản lý quyền theo Team (`research`, `courses`) khi nhóm lớn hơn.
- Repo mặc định **private**. Chuyển public chỉ khi đã đồng ý công bố.

### 5.2 Quy trình làm việc
1. Tạo nhánh từ `main`: `exp/<ten>` hoặc `feat/<ten>`.
2. Commit nhỏ, có message rõ.
3. Mở Pull Request, gắn người review; mô tả: làm gì, vì sao, kết quả (số) nếu có.
4. Merge sau khi có ít nhất một người đồng ý (chỉ cần một trong nhóm nhỏ).
5. Xóa nhánh sau khi merge.

Tệp nên có trong mỗi repo: `README.md`, `.gitignore`, `PULL_REQUEST_TEMPLATE.md`, `CONTRIBUTING.md` (ngắn), và `CODEOWNERS` nếu cần.

**Không đưa vào Git:** `.env`, khóa API, file dữ liệu lớn, PDF nặng, kết quả trung gian lớn. Dùng `.gitignore`, và Git LFS hoặc ổ lưu trữ chung cho file lớn.

### 5.3 LaTeX: Git hay Overleaf?

| | Git (repo) | Overleaf |
|---|---|---|
| Đồng bộ với code | Tốt, cùng repo | Cần tích hợp GitHub (thường là tính năng trả phí) |
| Cộng tác thời gian thực | Không | Có |
| Lịch sử thay đổi | Đầy đủ | Có, nhưng khó review từng chỗ |
| Chi phí | Miễn phí | Gói miễn phí giới hạn số cộng tác viên; kiểm tra điều kiện hiện tại và xem trường có gói riêng không |
| Font/package | Tùy máy | Hạn chế (xem lưu ý dưới) |

**Khuyến nghị:** dùng **Git làm nguồn chính** cho LaTeX, biên dịch bằng `latexmk` hoặc script `build.sh` (đã có trong `docs/latex/`). Dùng Overleaf chỉ khi mọi người cùng viết một đoạn trong thời gian ngắn, rồi kéo kết quả về Git.

Lưu ý riêng cho tài liệu hiện tại: `main.tex` dùng font **Times New Roman và Courier New** qua `fontspec`. Overleaf thường không có các font này, nên nếu đưa lên Overleaf cần đổi sang font tương đương (ví dụ TeX Gyre Termes) hoặc chọn compiler XeLaTeX và font có sẵn. Khi nộp journal sẽ phải chuyển sang template của họ bằng tiếng Anh, nên hãy giữ nội dung trong `sections/` tách khỏi phần định dạng để dễ chuyển.

### 5.4 Build tự động (tùy chọn)
Một workflow GitHub Actions biên dịch LaTeX mỗi khi có PR và đính kèm PDF vào artifact. Khi build lỗi thì báo vào `#bot-log` hoặc `#p4-github` (mục 4.4). Giúp mọi người thấy ngay bản thảo có biên dịch được không.

---

## 6. Obsidian: knowledge base chung

### 6.1 Cấu trúc vault

```
knowledge-base/
  00_Inbox/            Ghi nhanh, chưa phân loại (dọn mỗi tuần)
  10_Mon-hoc/
    <ma-mon>/          Bài giảng, bài tập, ôn thi
  20_Nghien-cuu/
    <ten-du-an>/       Mỗi dự án một thư mục, có trang <ten-du-an>-index.md (ví dụ paper4/paper4-index.md)
  30_Tai-lieu/         Ghi chú đọc paper (literature notes), mỗi paper một file
  40_Hop/              Biên bản họp theo ngày
  50_Template/         Mẫu ghi chú
  60_Khai-niem/        Khái niệm, phương pháp dùng lại cho nhiều dự án
  90_Archive/          Đã xong
  publish/             Chỉ những gì sẵn sàng công bố
```

Quy ước ghi chú:
- Tên file và thư mục không dấu, không dấu cách, dùng gạch ngang; tiêu đề có dấu viết trong nội dung. Lý do: tên có dấu lưu khác nhau giữa macOS, Windows và Linux nên Git có thể coi là hai file.
- Tên file phải duy nhất trong toàn vault để wikilink gọn: `YYYY-MM-DD-chu-de` cho họp; `tac-gia-nam-tu-khoa` cho paper (ví dụ `chang-2026-post-selection`); `<ten-du-an>-index` cho trang dự án.
- Frontmatter YAML thống nhất: `title`, `type`, `status`, `owner`, `date`, `project`, `tags` (dạng danh sách); thêm `repo`, `jira` khi có.
- Link trong vault dạng `[[wikilink]]`, dùng alias khi cần hiển thị có dấu (`[[ten-file|Tên hiển thị]]`); link ra ngoài ghi đầy đủ nguồn.
- Mỗi ghi chú paper có đủ: trích dẫn, ý chính, phương pháp, kết quả, liên quan đến project nào, và độ tin cậy (đã đọc toàn văn hay chỉ abstract).

### 6.2 Đồng bộ bằng Git
- Dùng plugin **Obsidian Git**.
- Thiết lập: tự **pull khi mở**, tự commit và push mỗi 10 đến 15 phút (hoặc thủ công nếu muốn ít commit).
- `.gitignore` cho vault: `.obsidian/workspace*.json`, `.obsidian/cache`, `.trash/`, file tạm.
- **Mỗi ghi chú có một chủ sở hữu** (`owner` trong frontmatter): sửa ghi chú của người khác thì bình luận hoặc nhắn trước. Điều này giảm xung đột merge ở file Markdown.
- Core plugin **Templates** (thư mục `50_Template`). Plugin nên cân nhắc thêm khi vault lớn: Bases hoặc Dataview (danh sách tự động theo frontmatter), tùy chọn Zotero Integration.
- Thư mục `.obsidian/` được commit để cả nhóm dùng chung cài đặt; `workspace.json` bị bỏ qua vì là trạng thái riêng của từng máy. Plugin cộng đồng mỗi người tự cài trên máy mình.
- File PDF/ảnh lớn **không** đẩy vào vault; dùng Zotero group library hoặc ổ chung, rồi link trong ghi chú.

**Về thông báo:** vì auto-commit sinh rất nhiều push, **không** gắn webhook push cho repo vault. Thay vào đó dùng **bản tin hằng ngày** (mục 6.4) để báo ghi chú nào mới hoặc đổi.

### 6.3 Nhắc việc và lịch họp
- **Nguồn lịch duy nhất:** chọn một lịch (Google Calendar chung hoặc một ghi chú `Lịch.md` trong vault). Đừng nhập deadline ở nhiều nơi.
- **Scheduled Events của Discord** cho từng buổi họp: có người bấm "Interested" và Discord nhắc trước giờ bắt đầu. Quản lý bởi Chấp Sự.
- **Deadline:** đăng một tin trong `#thien-co-cac` khi đặt, rồi nhắc lại trước 3 ngày và 1 ngày. Có thể làm bằng workflow Actions chạy theo lịch đọc file `deadlines.yml` trong repo, hoặc dùng bot nhắc nhở sẵn có.
- Tin nhắc nên có: tên việc, hạn, người chịu trách nhiệm (mention), link.

### 6.4 Bản tin hằng ngày
Một workflow Actions chạy theo cron (một lần mỗi ngày), lấy `git log` trong 24 giờ của repo vault và repo paper, tóm tắt thành một tin gửi vào `#ban-tin-hang-ngay`. Nội dung gợi ý:
- Số commit và người đóng góp.
- Ghi chú vault mới hoặc đổi nhiều.
- PR đang mở chờ review.
- Việc đến hạn trong 3 ngày tới.
Nếu ngày đó không có gì thì không gửi, để kênh không bị rác.

---

## 7. Phân bổ thông báo: bảng tổng hợp

| Nguồn | Kênh nhận | Ping ai | Tần suất |
|---|---|---|---|
| Push/PR/Issue/Release repo paper | `#p4-github` | Không | Theo sự kiện, đã lọc |
| Build LaTeX/test lỗi | `#p4-github` hoặc `#bot-log` | `@Chấp Sự` khi fail | Chỉ khi lỗi |
| Vault Obsidian | `#cap-nhat-vault` | Không | Qua bản tin, không per-commit |
| Deadline | `#thien-co-cac` | Role dự án/môn | 3 ngày và 1 ngày trước |
| Lịch họp | Scheduled Event + `#thien-co-cac` | Người tham dự | Trước giờ họp |
| Bản tin tổng hợp | `#ban-tin-hang-ngay` | Không | Mỗi ngày nếu có thay đổi |
| Lỗi webhook/bot | `#bot-log` | `@Chấp Sự` | Khi có lỗi |

Trả lời câu hỏi của bạn: **không gom mọi thứ vào một kênh.** Tách ra ba lớp: (1) kênh người nói chuyện, (2) kênh bot theo dự án (muted), (3) một kênh nhắc việc duy nhất (`#thien-co-cac`) có chủ ý không ồn. Reminder deadline và họp gom chung vào kênh (3), còn thông báo GitHub và vault thì không.

---

## 8. Quy tắc nhóm (đưa vào `#truyen-cong-duong`)

1. Trao đổi trong thread hoặc forum post, không trả lời rải rác trong kênh chính.
2. Mỗi quyết định quan trọng ghi lại trong Obsidian (ghi chú họp hoặc ADR ngắn), kèm link Discord.
3. Không dán khóa API, `.env`, URL webhook, hay dữ liệu chưa công bố lên Discord.
4. Không commit trực tiếp lên `main`; dùng Pull Request.
5. Ping có mục đích: ping role, không ping `@everyone` trừ khi khẩn.
6. Giờ yên tĩnh (ví dụ 23h đến 7h): không ping, trừ việc khẩn.
7. Hết học kỳ hoặc hết dự án thì archive, không xóa.
8. Tài liệu thuộc về vault; Discord chỉ chứa thảo luận và thông báo.

---

## 9. Lộ trình triển khai

| Phase | Việc | Xong khi |
|---|---|---|
| 0 | Chốt các quyết định ở mục 1; tạo GitHub Organization | Có danh sách quyết định |
| 1 | Tạo server, bật Community, dựng category/kênh/role theo mục 3, đặt quyền, viết `#truyen-cong-duong` | Mọi người vào được và đúng kênh |
| 2 | Tạo webhook cho `#p4-github`, bật các sự kiện mục 4.2, bảo vệ nhánh `main`, thử bằng một PR giả | Một PR giả hiện đúng ở kênh |
| 3 | Dựng repo vault, cấu trúc thư mục, template, cài Obsidian Git cho từng người | Hai người sửa cùng vault không xung đột |
| 4 | Workflow bản tin hằng ngày, nhắc deadline, Scheduled Event cho họp | Một tuần chạy ổn, không ồn |
| 5 | Onboarding thành viên, tổng kết sau 4 tuần: kênh nào ít dùng thì gộp, kênh nào ồn thì tăng lọc | Nhóm thấy không bị ngập thông báo |

Mỗi phase nên kiểm thử với 1 đến 2 người trước, rồi mới mời cả nhóm.

---

## 10. Rủi ro và cách giảm

| Rủi ro | Cách giảm |
|---|---|
| Ngập thông báo | Kênh bot muted, lọc sự kiện, bản tin gộp, không webhook cho vault |
| Lộ URL webhook hoặc khóa | Lưu trong secret và password manager; xoay vòng khi nghi ngờ |
| Một người giữ hết quyền | Ít nhất 2 Admin; ghi lại cách cấu hình trong repo |
| Xung đột khi nhiều người sửa vault | Chủ sở hữu từng ghi chú, pull trước khi sửa, commit nhỏ |
| Phình kênh | Giới hạn 4 kênh mỗi Bí Cảnh, dùng forum/thread |
| Tri thức nằm lẫn trong chat | Quy tắc 2 và 8: quyết định và tài liệu ghi vào vault |
| Dữ liệu chưa công bố bị lộ | Server private, Trưởng Lão kiểm soát, kênh nhạy cảm tách role |
| Công cụ thay đổi (giá, giới hạn) | Kiểm tra lại các giới hạn Overleaf, Discord, GitHub trước khi cam kết |

---

## 11. Checklist nhanh trước khi mời cả nhóm

- [ ] Có ít nhất 2 Admin; quy ước và cấu hình ghi trong repo.
- [ ] Kênh bot không cho Đệ Tử gửi tin; webhook chỉ Chấp Sự thấy.
- [ ] Mỗi webhook lưu an toàn; không có URL nào trong repo.
- [ ] `main` được bảo vệ; có PR template.
- [ ] Vault có `.gitignore`, template, và hướng dẫn cài Obsidian Git.
- [ ] Một nguồn lịch duy nhất đã chọn.
- [ ] `#truyen-cong-duong` có quy tắc và bảng nghĩa tên tiên hiệp.
- [ ] Đã thử toàn bộ luồng với 1 đến 2 người.

---

## 12. Quản lý task: Jira dạng Kanban (không sprint), kết hợp Obsidian

### 12.1 Vì sao Kanban hợp với nhóm học tập
Sprint hợp với đội làm sản phẩm có tốc độ ổn định. Nhóm học tập và nghiên cứu có việc đến không đều (deadline môn học, kết quả thí nghiệm bất ngờ, bị chặn chờ thầy duyệt). Kanban là luồng liên tục: task được đẩy vào bất cứ lúc nào, mỗi người kéo việc theo năng lực, không có "kế hoạch cứng" cho hai tuần để phá vỡ.

### 12.2 Cấu hình Jira
- Tạo project kiểu **Kanban** (Company-managed hoặc Team-managed đều được; team-managed đơn giản hơn).
- **Cột (workflow):** `Backlog` → `Ready` → `In Progress` → `In Review` → `Done`. Thêm cột hoặc trạng thái `Blocked` khi cần, thay vì để task nằm im không rõ lý do.
- **Giới hạn WIP:** `In Progress` tối đa 2 việc mỗi người; `In Review` tối đa 3 việc toàn nhóm. Việc quá giới hạn thì phải xong bớt rồi mới kéo thêm. Đây là cơ chế thay cho "cam kết sprint".
- **Issue types:** `Epic` (một paper hoặc một môn), `Task`, `Experiment` (thí nghiệm, có link quy tắc ghi trước), `Bug`, `Study` (đọc tài liệu, ôn thi).
- **Epic = một Bí Cảnh hoặc một môn:** "Paper 4", "Môn X". Task con thuộc Epic để lọc theo dự án.
- **Trường bắt buộc nên có:** Assignee, Due date (nếu có hạn thật), Labels (`paper4`, `mh-xxx`), và mô tả "xong khi nào" (definition of done, 1 đến 3 dòng).
- **Backlog:** ai cũng được thêm. Mỗi tuần một người rà lại, bỏ việc cũ không còn ý nghĩa.

### 12.2b Thay sprint bằng nhịp đều, nhẹ
| Nhịp | Việc | Thời lượng |
|---|---|---|
| Hằng ngày | Mỗi người cập nhật trạng thái task mình đang làm (kéo cột, một dòng comment) | 2 phút |
| Hằng tuần | Họp ngắn: nhìn board, ai bị chặn, kéo việc từ Ready | 20 phút |
| Theo mốc | Đặt **Fix version / mốc** cho cột mốc thật (nộp bản thảo, hạn môn học); xem ở view Timeline | khi có mốc |
| Hàng tháng | Rà backlog, tổng kết, đổi quy tắc nếu board bị ngập | 30 phút |

Chỉ số nên xem thay vì velocity: **cycle time** (từ In Progress đến Done) và số việc đang Blocked. Jira có sẵn Control Chart cho Kanban.

### 12.3 Cập nhật tiến độ mà không cần sprint
- Kéo task qua các cột là cập nhật chính. Việc dài (một thí nghiệm nhiều bước) chia thành **sub-task** hoặc checklist, để tiến độ nhìn thấy được.
- Khi có số liệu hoặc quyết định: comment ngắn trong task, kèm link PR hoặc ghi chú Obsidian.
- Task bị chặn: chuyển `Blocked`, ghi lý do và người cần hỗ trợ.

### 12.4 Nối với GitHub và Discord
- **Quy ước tên nhánh và commit chứa mã task** (ví dụ `exp/P4-12-baseline-cost`, commit `P4-12: ...`). Jira có tích hợp GitHub (Jira Cloud hỗ trợ) để hiện nhánh và PR ngay trong task. Chi tiết cài đặt và giới hạn bản miễn phí cần kiểm tra lại.
- **Thông báo sang Discord:** dùng Jira Automation, rule "khi task đến hạn trong 3 ngày" hoặc "khi chuyển sang Blocked" gửi webhook đến `#thien-co-cac` hoặc kênh dự án. Không báo mọi thay đổi (sẽ giống vấn đề push ở mục 4).

### 12.5 Quyết định: Jira + Obsidian, không dùng Confluence
Nhóm chọn Jira cho task và Obsidian cho tri thức, **bỏ Confluence** để chỉ có một nơi lưu tri thức. Phân vai:

| Cần ghi | Nơi ghi | Ghi chú |
|---|---|---|
| Việc cần làm, trạng thái, người phụ trách, hạn | Jira | Nguồn sự thật duy nhất cho tiến độ |
| Ghi chú đọc paper, nhật ký thí nghiệm, ôn thi, biên bản họp | Obsidian vault | Nằm trong Git cùng code |
| Code, LaTeX, kết quả | Git | |
| Báo cáo tiến độ gửi thầy | Một ghi chú Obsidian theo mẫu (`40_Hop/`) hoặc xuất PDF | Không cần công cụ riêng |

Quy tắc nối hai bên:
- Mỗi task Jira có trường mô tả chứa **link tới ghi chú Obsidian** liên quan (đường dẫn trong repo vault trên GitHub).
- Mỗi ghi chú họp hoặc thí nghiệm trong Obsidian ghi **mã task Jira** ở frontmatter (`jira: P4-12`).
- Không sao chép nội dung giữa hai nơi, chỉ link.
- Biên bản họp viết trong Obsidian, việc phát sinh từ buổi họp được tạo thành task Jira ngay trong hoặc sau buổi họp.

### 12.6 Phương án thay thế, nên cân nhắc
- **GitHub Projects** (board Kanban, miễn phí, ngay trong GitHub): gắn trực tiếp vào issue và PR, không cần tích hợp, phù hợp nếu nhóm nhỏ và mọi việc đều xoay quanh repo.
- Jira đáng dùng nếu bạn đã quen Atlassian, cần Timeline và báo cáo, hoặc muốn rèn quy trình làm việc giống công ty. Gói miễn phí giới hạn số người; cần kiểm tra giới hạn hiện tại trước khi dựng.

### 12.7 Lộ trình bổ sung (sau Phase 3)
- **Phase 3b:** tạo project Kanban, cột, WIP, Epic cho Paper 4 và môn đang học; nhập backlog ban đầu.
- **Phase 4b:** tích hợp GitHub, rule Automation gửi nhắc deadline vào Discord.
- Sau 4 tuần: xem cycle time và số việc Blocked, điều chỉnh WIP hoặc cột.
