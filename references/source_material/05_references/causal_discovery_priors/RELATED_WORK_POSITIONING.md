# Related work và định vị contribution (Issue #96, P0-4)

- **Phạm vi:** định vị C1 (Enhanced v2: kênh orientation có arbitration theo local-BIC margin và fallback theo conflict rate) và Standard v2 so với các nhóm công trình gần nhất.
- **Trích dẫn:** `references.bib` cùng thư mục. Mọi mục đã đối chiếu với arXiv / proceedings / trang nhà xuất bản ngày 2026-09-25. Mục nào chỉ có preprint thì ghi rõ là preprint.
- **Chưa xác minh:** các mục Andrews et al. (2020), Ng et al. (2022), De Campos et al. (2011), Scheines et al. (1998) trong `README.md` chưa được đối chiếu nguồn; không trích dẫn trong bản thảo cho tới khi kiểm tra.

## 1. Bảng định vị

Trục: nguồn prior · cách tích hợp · cách xử lý prior sai · chế độ mẫu nhỏ.

| Công trình | Nguồn prior | Cách tích hợp | Xử lý prior sai | Mẫu nhỏ |
|---|---|---|---|---|
| Meek 1995 | Background knowledge (hướng cạnh) | Ràng buộc cứng trên equivalence class, luật Meek R1–R4 | Không (giả định đúng); chỉ kiểm tra tính nhất quán | Không |
| Chickering 2002 (GES) | Không | Score-based greedy trên equivalence class | — | Không |
| Borboudakis & Tsamardinos 2012 | Tri thức về đường nhân quả (có/không) | Ràng buộc cứng dạng path, PC-PDAG / PC-PAG | Không | Không |
| Perković et al. 2017 | Background knowledge về hướng | Maximal PDAG, adjustment và IDA trên MPDAG | Không | Không |
| Constantinou et al. 2023 | Tri thức chuyên gia nhiều dạng | Nhiều cách tích hợp (cứng / mềm) trên nhiều thuật toán | Đo tác động của các cách tích hợp tri thức lên structure learning | Không nêu trong abstract |
| Kıcıman et al. 2023 | LLM | Suy luận nhân quả theo cặp | Không (benchmark năng lực LLM) | — |
| Long et al. 2023 | LLM như expert không hoàn hảo | Định hướng cạnh ngoài MEC | Sửa tri thức expert dựa trên tính nhất quán | Không phải trọng tâm |
| Ban et al. 2023a | LLM | Ràng buộc từ LLM + structure learning (MINOBS, CaMML) | Không nêu trong abstract | Không phải trọng tâm |
| Ban et al. 2023b (ILS-CSL) | LLM | LLM giám sát lặp trên graph đã học | Lặp để giảm ràng buộc sai | Không phải trọng tâm |
| Chen et al. 2025 (TPAMI) | Prior cạnh (hướng tới prior từ LLM) | Chiến lược chống chịu lỗi prior mức cạnh | Phân loại lỗi prior, phân tích tác động lên SHD | Không phải trọng tâm |
| Takayama et al. 2025 | LLM + kết quả SCD | Prior augmentation cho statistical causal discovery | Gián tiếp qua statistical causal prompting | Không phải trọng tâm |
| Vashishtha et al. 2025 | LLM / expert không hoàn hảo | Causal order thay cho graph | Order ổn định hơn graph khi prompt theo cặp | Không phải trọng tâm |
| Wu et al. 2025 | LLM (phê phán) | Đề xuất LLM chỉ hỗ trợ tìm kiếm, không quyết định cạnh/hướng | Lập luận LLM không đủ tin cậy làm prior quyết định | — |
| Hiremath et al. 2025 (Guess2Graph) | Expert không đáng tin (gồm LLM) | Expert chỉ dẫn thứ tự kiểm định trong PC | Giữ correctness bất kể lỗi expert (có bảo đảm lý thuyết) | **Có, mẫu hữu hạn là trọng tâm** |
| Wang et al. 2025 | Ràng buộc cấu trúc không hoàn hảo | Surrogate đánh giá độ tin cậy ràng buộc + penalty thưa, multi-task gradient | Hòa giải tri thức và dữ liệu | Không phải trọng tâm |
| Xu & Corter 2026 (KG-SoftMAP) | Knowledge graph | Prior cạnh dạng logit có trọng số confidence cộng vào score BDeu (MAP) | Stress test làm hỏng / xóa / làm mờ KG | **Có, dữ liệu thưa** |
| Schubert et al. 2026 | Background knowledge | Dùng tri thức trong lúc tìm kiếm để khôi phục một phần graph | Không nêu trong abstract | Không phải trọng tâm |

## 2. Điểm khác và điểm trùng của Paper 2

**[FACT từ source] Standard v2:** soft prior trên skeleton, log-odds theo tier confidence, cộng vào BIC.
- Cùng lớp với KG-SoftMAP (prior logit có trọng số confidence cộng vào score) và với nhóm soft constraint mà Chen et al. 2025 phân tích.
- **Không phải novelty.** Chỉ trình bày như baseline.

**[FACT từ source] Enhanced v2:** giữ skeleton của Standard v2. Định hướng thêm trên CPDAG bằng prior hướng, kèm ba thành phần:
- arbitration theo local-BIC margin khi prior ngược data arrow;
- cổng strong-conflict;
- fallback toàn cục về Standard v2 khi conflict rate cao.

**Công trình gần nhất theo từng thành phần** [INFERENCE: đánh giá từ abstract, chưa đọc toàn văn]:
- Định hướng ngoài MEC bằng expert không hoàn hảo: Long et al. 2023. Khác biệt: Paper 2 dùng score margin cục bộ thay cho tiêu chí nhất quán, và có fallback toàn cục.
- Chống chịu lỗi prior mức cạnh: Chen et al. 2025. Khác biệt: Paper 2 là score-based GES với fallback; Chen et al. có phân tích lý thuyết tác động lên SHD, Paper 2 không có.
- An toàn khi expert sai, mẫu hữu hạn: Hiremath et al. 2025. Đây là đối thủ gần nhất về framing. Bài này có bảo đảm correctness lý thuyết cho PC. Paper 2 chỉ có non-inferiority thực nghiệm, và ở tầng Severe non-inferiority chủ yếu đạt nhờ fallback (A-91: 74–94 %). **Paper 2 không được claim an toàn tương đương.**

**Điểm khác có thể bảo vệ, dựa trên bằng chứng hiện có:**
1. Prior trích từ văn bản tài chính tiếng Việt (PP422), với tier confidence từ pipeline extraction. Kèm kết quả null: confidence không có giá trị tăng thêm ở cả mức calibration (`calibration_audit.md`, p = 0.46) và mức cơ chế (lane confidence #93).
2. Định lượng cái giá của cơ chế an toàn. Enhanced v2 giữ 0.26–0.70 lần lợi ích ΔSHD của `prior_forced` ở tầng Benign (#93, #96 P0-2), đổi lại có non-inferiority ở tầng Severe.
3. Bản đồ lợi ích / rủi ro theo T ≤ 60 × chất lượng prior, tách kênh skeleton khỏi kênh orientation (#96 P0-3):
   - lợi ích chính so với plain GES ở mẫu nhỏ đến từ kênh skeleton;
   - khi skeleton prior hỏng thì kênh này gây hại, và cơ chế an toàn của Enhanced v2 không che được phần này.
4. Case study trên panel 14 × 19 thật (#94): mô tả mức xung đột giữa prior và data theo từng cạnh.

**Hệ quả cho bản thảo:**
- Phải trích dẫn và thảo luận Hiremath et al. 2025, Long et al. 2023, Chen et al. 2025 và Xu & Corter 2026 trong phần related work.
- Nên có ít nhất một baseline ngoài: Long et al. 2023 có code công khai ([repo](https://github.com/StephLong614/Causal-disco-LLM-imperfect-experts)). Việc đưa vào là quyết định của Human vì tăng scope.
- Vashishtha et al. 2025 ủng hộ lỗi kiểu "cạnh tắt bắc cầu" (prompt theo cặp không tách được hiệu ứng trực tiếp và gián tiếp). Có thể dùng làm căn cứ cho lane P2-1 nếu mở.
- Wu et al. 2025 ủng hộ thiết kế ưu tiên data và fallback. Đồng thời là lý do không gọi prior văn bản là tri thức nhân quả đúng.

## 3. Nguồn đã đối chiếu

- Meek 1995: [ML Anthology](https://mlanthology.org/uai/1995/meek1995uai-causal/), [arXiv 1302.4972](https://arxiv.org/abs/1302.4972)
- Chickering 2002: [JMLR](https://jmlr.org/papers/v3/chickering02b.html)
- Borboudakis & Tsamardinos 2012: [arXiv 1206.6390](https://arxiv.org/abs/1206.6390)
- Perković et al. 2017: [UAI 2017](https://www.auai.org/uai2017/proceedings/papers/120.pdf), [arXiv 1707.02171](https://arxiv.org/abs/1707.02171)
- Constantinou et al. 2023: [arXiv 2102.00473](https://arxiv.org/abs/2102.00473)
- Kıcıman et al. 2023: [arXiv 2305.00050](https://arxiv.org/abs/2305.00050)
- Long et al. 2023: [arXiv 2307.02390](https://arxiv.org/abs/2307.02390)
- Ban et al. 2023a: [arXiv 2306.16902](https://arxiv.org/abs/2306.16902)
- Ban et al. 2023b: [arXiv 2311.11689](https://arxiv.org/abs/2311.11689)
- Chen et al. 2025: [DOI 10.1109/TPAMI.2025.3594755](https://doi.org/10.1109/tpami.2025.3594755), preprint [arXiv 2306.07032](https://arxiv.org/abs/2306.07032)
- Takayama et al. 2025: [arXiv 2402.01454](https://arxiv.org/abs/2402.01454), [OpenReview](https://openreview.net/forum?id=Reh1S8rxfh)
- Vashishtha et al. 2025: [ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/edcbd38b2509b57954d38de6cd9c05b3-Abstract-Conference.html)
- Wu et al. 2025: [arXiv 2506.00844](https://arxiv.org/abs/2506.00844)
- Hiremath et al. 2025: [arXiv 2510.14488](https://arxiv.org/abs/2510.14488)
- Wang et al. 2025: [arXiv 2511.06790](https://arxiv.org/abs/2511.06790)
- Xu & Corter 2026: [arXiv 2606.10358](https://arxiv.org/abs/2606.10358)
- Schubert et al. 2026: [arXiv 2607.10456](https://arxiv.org/abs/2607.10456)
