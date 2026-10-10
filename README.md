# Cẩm Nang Công Tác Xã Hội - RAG Agent

Hệ thống RAG thu thập các quy định về Công Tác Xã Hội và giải đáp thắc mắc cho Sinh Viên thông qua cơ chế RAG Hybrid Retrieval tiên tiến (kết hợp Dense Vector và Lexical BM25 Search).

## 1. Cấu trúc thư mục định danh

```text
social-work-rag-agent/
├── config.py
├── requirements.txt
├── README.md
├── run_project.py               # Script tổng chạy từ A-Z Pipeline
├── data/
│   ├── processed/               # Markdown đã chuyển đổi
│   └── ctxh_chunks.json         # Cơ sở dữ liệu Chunks (JSON)
├── src/
│   ├── schemas.py               # Cấu trúc chung (DocumentChunk, RetrievalResult)
│   ├── data_preprocessing/
│   │   ├── document_loader.py   # Load Markdown & Metadata
│   │   ├── chunker.py           # Chia đoạn (Chunking) & Clean Text
│   │   └── build_dataset.py     # Module xuất dataset
│   └── retrieval/
│       ├── embedder.py          # SentenceTransformer Embedder (E5)
│       ├── hybrid_search.py     # Engine thuật toán lai BM25 + Cosine
│       ├── calibration.py       # Bộ lọc ngưỡng từ chối trả lời (no_answer)
│       └── vector_store.py      # Lưu trữ và tìm kiếm Vector tĩnh
├── tests/
│   ├── testset.jsonl            # Bộ 12 câu hỏi đánh giá
│   ├── test_hybrid_search.py    # Batch Test Hybrid Search
│   ├── test_embedder.py
│   └── test_vector_store.py
└── document_guide/              # Thư mục chứa báo cáo kỹ thuật thuật toán
```

## 2. Hướng dẫn chạy nhanh (Quick Start)

Cách dễ nhất để kiểm thử luồng RAG từ khâu xử lý tài liệu cho đến truy vấn Hybrid Search mà không cần setup phức tạp là cấu trúc script tổng:

```bash
uv run python run_project.py
```

Lệnh này sẽ tự động:
1. Đọc file Markdown -> Cắt Chunks.
2. Nạp E5 Embedding Model & Tính toán BM25 Inverted Index.
3. Chạy qua 3 câu hỏi giả lập để test điểm Dense / Sparse và màng lọc Threshold độc lập.

## 3. Hệ thống Hybrid Retrieval System

Quá trình truy vấn không sử dụng cơ sở dữ liệu cồng kềnh mà hoạt động in-memory qua sự dung hợp (Fusion):
- **Dense Search (Ngữ nghĩa):** Sử dụng LLM Embedder `intfloat/multilingual-e5-base` tối ưu tiếng Việt. Trọng số 0.5.
- **Sparse Search (Từ khóa):** Dùng `BM25 Okapi` qua bộ lọc lột bỏ 41 Stop words Tiếng Việt để tránh nhiễu hệ số. Trọng số 0.5.
- **Min-Max Score Normalization:** Chuẩn hoá 2 thang biểu diễn điểm số về khoảng `[0..1]`.
- **Calibration (Màng lọc Ảo giác)**: Hệ số an toàn Threshold cài đặt sẵn (`0.55`) giúp luồng dữ liệu mạnh dạn **từ chối (no_answer)** thao tác với các câu hỏi nằm ngoài vùng tri thức (VD: Hỏi Bitcoin, Cài phần mềm).

## 4. Chạy Unit Test Dự Án

```bash
uv run pytest tests/ -v
```
Quá trình này đảm nhiệm kiểm thử module `Hybrid Search` và độ dài của câu hỏi trong `testset.jsonl`.
