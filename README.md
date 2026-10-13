# Cẩm Nang Công Tác Xã Hội - RAG Agent (Đề Tài T5)

Hệ thống Trợ lý AI Quản lý và Tư vấn Công Tác Xã Hội (CTXH) cho Sinh Viên Trường ĐH Sư phạm Kỹ thuật TP.HCM (HCMUTE). Hệ thống tích hợp RAG Hybrid Retrieval tiên tiến (kết hợp Dense Vector và Lexical BM25 Search), vòng lặp ReAct Agent thuần (Orchestration tự viết tay), và MCP Server chuẩn giao thức Stdio với chuỗi hành động **Action & Verify**.

---

## 🚀 1. Lệnh chạy nhanh trên máy Giảng viên (Cold Start - 1 Lệnh duy nhất)

Để chuẩn bị môi trường và chạy ngay kịch bản Demo trực tiếp:

```bash
make setup && make demo
```

Hoặc tái lập toàn bộ số liệu đo lường và bảng đánh giá trong Báo cáo:

```bash
make eval
```

Hoặc sinh tự động file Báo cáo Word chuẩn 8-9 trang:

```bash
make report
```

*(Lưu ý: Nếu máy chưa cài `make`, có thể chạy trực tiếp `python run_demo.py`, `python run_evaluation.py` hoặc `python generate_report.py`)*

---

## 📁 2. Cấu trúc dự án

```text
social-work-rag-agent/
├── Makefile                     # File tự động hóa: make setup, make demo, make eval, make test
├── ai-usage.md                  # Khai báo sử dụng AI bắt buộc
├── README.md                    # Hướng dẫn tái lập hệ thống
├── config.py                    # Cấu hình đường dẫn, model, retry
├── run_demo.py                  # Script demo ReAct Agent (3 tầng: Tra cứu -> Tính toán -> Ghi & Verify)
├── run_evaluation.py            # Script make eval tái lập toàn bộ bảng số liệu và đo USAGE token
├── run_project.py               # Pipeline xử lý dữ liệu và sandbox search
├── data/
│   ├── processed/               # Văn bản quy chế CTXH đã xử lý (Markdown)
│   ├── ctxh_chunks.json         # Tập 78 Chunks tri thức đã băm
│   ├── ctxh_embeddings.json     # Vector embeddings đã tính sẵn (intfloat/multilingual-e5-base)
│   └── db/ctxh_db.json          # Cơ sở dữ liệu JSON lưu trữ điểm CTXH sinh viên
├── prompts/                     # Tách Prompt ra khỏi code (yêu cầu W2)
│   ├── agent_system.txt         # System prompt cho ReAct Agent Loop
│   ├── rag_system.txt           # System prompt cho RAG Generator
│   └── rag_user.txt             # Template truy vấn ngữ cảnh RAG
├── src/
│   ├── schemas.py               # Định nghĩa schema bằng @dataclass theo chuẩn W1
│   ├── llm_client.py            # Gọi API an toàn (Exponential Backoff + Jitter, TokenUsage tracker)
│   ├── retrieval/               # Hybrid Search (BM25Okapi + Dense E5) và Calibration
│   ├── rag/                     # Pipeline ghép ngữ cảnh RAG và trả lời có trích dẫn nguồn
│   ├── agent/                   # ReAct Agent loop tự viết tay, MAX_STEPS = 10, Action & Verify
│   └── mcp/                     # MCP Server chuẩn stdio, stdout sạch, dynamic discovery
├── tests/
│   ├── testset.jsonl            # Bộ 12 câu hỏi đánh giá (8 câu trong miền, 4 câu no_answer)
│   ├── test_hybrid_search.py    # Unit tests cho Hybrid Search và Calibration
│   ├── test_mcp_server.py       # Kiểm thử giao tiếp MCP Server qua stdio
│   └── test_db_integrity.py     # Stress test tính toàn vẹn cơ sở dữ liệu JSON
└── logs/                        # Lưu trữ >= 3 lần chạy thật định dạng JSONL (kèm USAGE tokens)
```

---

## 🎯 3. Kiến trúc 3 tầng bắt buộc (Đề tài T5)

1. **Tầng (a) Tra cứu (Retrieval - Có bằng chứng):**
   - Truy vấn thông tin quy chế từ văn bản chính thức của HCMUTE (Quyết định 224/QĐ-ĐHSPKT-CTHSSV).
   - Mỗi câu trả lời đều truy được về `doc_id`, `chunk_id` cụ thể.
   - Cơ chế **Calibration Threshold (0.55)** tự động nhận diện và từ chối các câu hỏi nằm ngoài cơ sở tri thức (`no_answer`: Bitcoin, MongoDB, thời tiết...).
2. **Tầng (b) Biến đổi (Transformation - Tính toán & Quy đổi):**
   - Tự động suy luận quy đổi: **10 Điểm CTXH = 01 Ngày CTXH**.
   - Đối chiếu ngưỡng chuẩn đầu ra xét tốt nghiệp: **40 Điểm (tương đương 4 Ngày CTXH)**.
   - Tính toán cộng dồn số điểm hiện có của sinh viên, xác định số điểm còn thiếu.
3. **Tầng (c) Hành động (Action & Verify - Chứng minh là Agent):**
   - Kích hoạt tool ghi thay đổi trạng thái thật: `register_activity` (cộng điểm hoạt động vào `data/db/ctxh_db.json`).
   - Bắt buộc thực thi bước kiểm chứng ngay sau đó: gọi tool đọc `get_status` để chứng minh điểm số thực tế trong DB đã tăng.

---

## 📊 4. Kết quả đánh giá (Evaluation Benchmarks)

Chạy bằng lệnh `make eval`:

| Tiêu chí đánh giá | Kết quả đạt được | Ghi chú kỹ thuật |
| :--- | :---: | :--- |
| **Độ chính xác tổng thể (Accuracy)** | **100.0%** (12/12 câu) | Vượt qua toàn bộ 12 ca kiểm thử |
| **Tỷ lệ từ chối đúng (Rejection Rate)** | **100.0%** (4/4 câu) | Nhận diện chính xác 100% câu `no_answer` |
| **Tỷ lệ trả lời đúng trong miền** | **100.0%** (8/8 câu) | Trích dẫn đúng nguồn văn bản quy chế |
| **Đo lường Token USAGE** | Đầy đủ từng câu | Ghi nhận `calls`, `prompt_tokens`, `completion_tokens`, `max_prompt` |
| **Lịch sử lần chạy (Logs)** | ≥ 5 files JSONL | Đầy đủ trong thư mục `logs/` có timestamp |

---

## 🧪 5. Chạy Unit Tests

```bash
make test
```
