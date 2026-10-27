# Khung 1 Provenance & Source Manifest

> **CHỈ THỊ ĐÓNG BĂNG (FROZEN / READ-ONLY POLICY):**
> Toàn bộ thư mục `01_paper1_foundation` là snapshot bất biến đại diện cho **Khung 1 (PP422 / ISBM 2026)**.
> Các tệp tại đây chỉ đóng vai trò đầu vào tri thức tiên nghiệm (prior knowledge input) cho Paper 2 (ACIIDS 2027).
> Mọi code nghiên cứu, thuật toán cải tiến, thực nghiệm CD mới phải được phát triển trong `03_causal_discovery`.
> Tuyệt đối KHÔNG sửa đổi, tái tính toán làm sai lệch các artifact gốc trong thư mục này.

- **Thời điểm thiết lập snapshot:** 2026-09-05 11:33:43
- **Nguồn cung cấp:** Dự án NCKH PP1 (external source project; machine-specific checkout path omitted from this portable snapshot).

## Bảng danh mục Artifacts và Mã băm kiểm định SHA256

| Tệp (Đích) | Dung lượng (bytes) | SHA256 | Vai trò kỹ thuật trong Paper 2 | Nguồn gốc |
|---|---|---|---|---|
| `canonical_nodes/canonical_node_set.csv` | 3,316 | `c0f2f7625b6e4897...` | Tap hop 26 bien canonical chuan hoa 4 linh vuc tai chinh | `canonical_node_set.csv` |
| `prior_graph/prior_graph_final_278.json` | 7,405 | `61ba4bbf60d9ed5e...` | Prior DAG 42 canh hoan chinh gom confidence, sign, n_instances, cờ conflicted | `prior_graph_final_278.json` |
| `prior_graph/pipeline_output_raw_278chunk.jsonl` | 112,522 | `dc12ea512f573bb8...` | 124 quan he trich xuat tho tu 278 chunks kem ly do accept/reject cua verifier | `pipeline_output_raw_278chunk.jsonl` |
| `prior_graph/dag_validation.json` | 5,505 | `17717904815118b4...` | Kiem dinh acyclicity cua Prior DAG qua DFS va Kahn topological sort | `dag_validation.json` |
| `rag_kb/rag_kb_full_content.jsonl` | 248,665 | `74b4f8255cb3d7cc...` | 278 chunks ngu lieu tai chinh tieng Viet hoan chinh | `rag_kb_full_content.jsonl` |
| `rag_kb/rag_pilot_manifest.csv` | 98,626 | `6a9734973d110fef...` | Metadata 152 nguon tai lieu (domain, URL, tier, validation flags) | `rag_pilot_manifest.csv` |
| `evaluation_benchmark/ground_truth_v1.2_draft.jsonl` | 20,764 | `0387a5cbe1722f2f...` | Ground truth tap hop cac quan he nhan qua text-level cua PP1 | `ground_truth_v1.2_draft.jsonl` |
| `evaluation_benchmark/eval_set_v1.2_draft.jsonl` | 39,708 | `082ebbb2f625cda3...` | Eval set gom cac instance de benchmark do tin cay trich xuat | `eval_set_v1.2_draft.jsonl` |
| `evaluation_benchmark/annotation_guideline.md` | 10,519 | `f9499325e24f7b8e...` | Huong dan va tieu chuan gan nhan quan he nhan qua | `annotation_guideline.md` |
| `quality_and_validation/formula_derivation.md` | 6,275 | `aac93240f341730d...` | Dien giai toan hoc cong thuc prior-weighting va sua loi nghich dao 1-c thanh c | `formula_derivation.md` |
| `quality_and_validation/paper_metrics_manifest.json` | 9,975 | `c309f89c70b5e3fc...` | Manifest kiem tra cheo toan bo so lieu va chi so cua PP1 | `paper_metrics_manifest.json` |
| `quality_and_validation/confidence_recompute.json` | 19,983 | `c8f887e0c275d7ca...` | Du lieu tinh toan lai trong so confidence cua 42 canh | `confidence_recompute.json` |
| `quality_and_validation/formula_weight_tests.json` | 4,417 | `9b54f4b8946d8e1a...` | Ket qua test cac ham trong so confidence | `formula_weight_tests.json` |
| `quality_and_validation/scripts/gen_metrics.py` | 28,025 | `01c2178a9caca508...` | Script sinh va doi chieu metric cho PP1 | `gen_metrics.py` |
| `quality_and_validation/scripts/gen_figures.py` | 7,148 | `1b2dd17cc351276f...` | Script ve bieu do phan bo va cau truc do thi PP1 | `gen_figures.py` |
| `quality_and_validation/scripts/formula_tests.py` | 6,672 | `15d8cbde0faf408a...` | Script kiem thu cong thuc toan | `formula_tests.py` |
| `quality_and_validation/scripts/run_validation.py` | 4,835 | `18c267f8f82ec99f...` | Script tong chay kiem dinh tinh hop le cua PP1 | `run_validation.py` || paper_accepted/422-ISBM 2026.docm | 309,181 | 65146c9e280e2352... | Ban thao Paper 1 accepted tai ISBM 2026 lam can cu goc | 422-ISBM 2026.docm |
