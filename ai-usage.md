# 🤖 KHAI BÁO SỬ DỤNG AI (AI-USAGE DECLARATION)
**Môn học:** Các phương pháp Trí tuệ Nhân tạo Tiên tiến (AIPR)  
**Đề tài:** T5 — Trợ lý CTXH: Quy đổi & Đăng ký (Social Work RAG Agent)  
**Nhóm sinh viên:** 3 thành viên  

---

## 1. Danh sách các công cụ AI đã sử dụng
1. **Google Antigravity IDE / Gemini 2.5 & Claude 3.5 Sonnet:** Trợ lý lập trình pair-programming, hỗ trợ gợi ý cấu trúc mã nguồn, debug lỗi môi trường Windows và định dạng chuẩn JSON-RPC.
2. **Groq LLM API (`llama-3.1-8b-instant` / `llama-3.3-70b-versatile`):** Mô hình sinh ngôn ngữ tự nhiên phục vụ Agent ReAct Loop và RAG Answer Generation.

---

## 2. Mục đích và phạm vi sử dụng AI trong từng phần của dự án

| STT | Thành phần dự án | Công cụ AI | Mục đích sử dụng | Mức độ can thiệp của sinh viên |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **RAG & Hybrid Search** | Gemini / Claude | Gợi ý khung thuật toán kết hợp BM25Okapi và Dense E5, công thức chuẩn hóa Min-Max | Sinh viên tự viết bộ lọc Stopwords tiếng Việt, thiết lập ngưỡng Calibration Score và tiền xử lý văn bản quy chế HCMUTE. |
| **2** | **MCP Server & Client** | Gemini / Claude | Hướng dẫn định dạng giao thức Stdio MCP và cơ chế bóc tách schema từ Dataclass | Sinh viên tự triển khai 2 tools (`register_activity`, `get_status`), xử lý luồng `sys.stderr` sạch và kiểm thử tính toàn vẹn DB. |
| **3** | **Agent ReAct Loop** | Claude 3.5 Sonnet | Gợi ý mẫu vòng lặp Native Tool Calling và ràng buộc Action & Verify | Sinh viên tự lập trình vòng lặp thuần (không dùng LangChain), bóc tách tham số JSON an toàn và xử lý cờ kiểm chứng. |
| **4** | **Benchmark & Đo lường** | Gemini / Claude | Gợi ý cấu trúc logging JSONL và đo lường USAGE token từng câu | Sinh viên xây dựng bộ testset 12 câu, thiết lập ma trận kiểm định và script tái lập `make eval`. |

---

## 3. Các Prompt chính đã sử dụng

### Prompt 1: Thiết kế module Hybrid Search có Calibration từ chối
```text
Hãy giúp tôi viết một class HybridSearch bằng Python kết hợp giữa BM25Okapi (rank_bm25) 
và Dense Cosine Similarity (E5 vector). Yêu cầu:
- Chuẩn hóa điểm số Min-Max về khoảng [0, 1].
- Tích hợp bộ lọc từ khóa/stop words tiếng Việt để tránh việc câu hỏi ngoài lề (out-of-domain) 
  vẫn nhận điểm số cao.
- Trả về danh sách đối tượng RetrievalResult theo cấu trúc @dataclass.
```

### Prompt 2: Xây dựng vòng lặp ReAct Agent thuần và Action & Verify
```text
Viết một hàm react_agent tự viết tay (không dùng LangChain/CrewAI) bằng Python với:
- Giới hạn MAX_STEPS = 10.
- Parse JSON arguments an toàn từ tool_calls của LLM.
- Thực thi ràng buộc an toàn (Action & Verify): nếu agent gọi tool ghi 'register_activity', 
  bắt buộc bước tiếp theo phải gọi tool đọc 'get_status' để kiểm chứng sự thay đổi của DB 
  trước khi trả lời người dùng.
```

### Prompt 3: Hệ thống Benchmark và Logging USAGE Token
```text
Viết một script run_evaluation.py bằng Python để chạy bộ 12 câu hỏi testset (gồm cả câu no_answer).
Yêu cầu:
- Đo lường độ chính xác Calibration (tỷ lệ từ chối đúng).
- Ghi log định dạng JSONL vào thư mục logs/ với các trường: timestamp, question, actual_answerable, 
  top_score, latency, và USAGE chi tiết (calls, prompt_tokens, completion_tokens, max_prompt).
```

---

## 4. Các đoạn mã nguồn có sự hỗ trợ của AI
1. **[src/retrieval/hybrid_search.py](file:///c:/Users/Admin/AIPR/social-work-rag-agent/src/retrieval/hybrid_search.py):** Hàm `min_max_normalize` và hàm phân tích `tokenize_vietnamese`.
2. **[src/agent/loop.py](file:///c:/Users/Admin/AIPR/social-work-rag-agent/src/agent/loop.py):** Khung bắt lỗi parse tool arguments và logic chuyển trạng thái `has_registered -> has_verified`.
3. **[src/llm_client.py](file:///c:/Users/Admin/AIPR/social-work-rag-agent/src/llm_client.py):** Cơ chế Exponential Backoff kèm Jitter và lớp `TokenUsage`.
4. **[run_evaluation.py](file:///c:/Users/Admin/AIPR/social-work-rag-agent/run_evaluation.py):** Bộ bảng hiển thị kết quả bằng thư viện `rich`.

---

## 5. Cam kết liêm chính học thuật
- Nhóm sinh viên cam kết đã **hiểu rõ 100% từng dòng mã nguồn** trong dự án.
- Tất cả logic nghiệp vụ (quy đổi 10 điểm = 1 ngày CTXH, hạn mức 40 điểm tốt nghiệp, mã hoạt động) đều do sinh viên nghiên cứu và thiết lập dựa trên tài liệu quy chế thực tế của trường HCMUTE.
- Toàn bộ thành viên sẵn sàng giải thích và sửa đổi mã nguồn trực tiếp tại buổi bảo vệ theo yêu cầu của Giảng viên.
