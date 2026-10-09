## 1. Cấu trúc thư mục tổng thể

```text
social-work-rag-agent/
├── config.py
├── requirements.txt
├── README.md
├── data/
│   ├── raw/                         # File DOCX/PDF gốc
│   ├── processed/                   # Markdown đã chuyển đổi và kiểm tra
│   └── ctxh_chunks.json             # Chunk + metadata + embedding
├── src/
│   ├── data_processing/
│   │   ├── __init__.py
│   │   ├── document_loader.py       # Đọc Markdown và metadata
│   │   ├── chunker.py               # Làm sạch/chia chunk
│   │   └── build_dataset.py         # Điều phối tạo dataset và embedding
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── embedder.py              # Tạo embedding cho truy vấn/tài liệu
│   │   ├── vector_store.py          # Lưu và tìm kiếm vector
│   │   ├── bm25_retriever.py        # Tìm kiếm theo từ khóa
│   │   └── retriever.py             # Kết hợp/xếp hạng kết quả
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── rag_pipeline.py          # Retrieval + context + LLM
│   │   └── prompt_templates.py      # Prompt cho trợ lý quy chế CTXH
│   └── agent/
│       ├── __init__.py
│       ├── agent.py                 # Điều phối và gọi tools
│       └── tools.py                 # Tra cứu, lọc phiên bản, tính toán
├── tests/
│   ├── test_document_loader.py
│   ├── test_chunking.py
│   ├── test_retrieval.py
│   └── test_rag.py
└── docs/
    ├── architecture.md
    └── team_tasks.md
```

### Vai trò các phần chính

- `config.py`: cấu hình đường dẫn, chunk size, overlap và embedding
  model.
- `data/`: dữ liệu đầu vào và dữ liệu đã xử lý.
- `src/data_processing/`: chuyển Markdown thành chunk có metadata và
  embedding.
- `src/retrieval/`: tìm các chunk liên quan đến câu hỏi.
- `src/rag/`: đưa các chunk vào prompt để LLM trả lời dựa trên tài
  liệu.
- `src/agent/`: điều phối pipeline và gọi công cụ khi cần.
- `tests/`: kiểm tra từng thành phần độc lập.
- `docs/`: tài liệu kiến trúc và kế hoạch thực hiện.
