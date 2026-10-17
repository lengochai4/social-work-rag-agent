# KHAI BÁO SỬ DỤNG AI (AI-USAGE DECLARATION)
**Môn học:** AI Programming with Python (AIPR)  
**Đề tài:** T5 — Trợ lý CTXH: Quy đổi & Đăng ký (Social Work RAG Agent)  
**Nhóm sinh viên:** 3 thành viên  

---

## 1. Danh sách các công cụ AI đã sử dụng
1. **Google Antigravity IDE / Gemini 2.5 & Claude 3.5 Sonnet:** Trợ lý lập trình pair-programming, hỗ trợ gợi ý cấu trúc mã nguồn, debug lỗi môi trường Windows và định dạng chuẩn JSON-RPC.
2. **Groq LLM API (`llama-3.1-8b-instant` / `llama-3.3-70b-versatile`):** Mô hình sinh ngôn ngữ tự nhiên phục vụ Agent ReAct Loop và RAG Answer Generation.

---

## 2. Mục đích và phạm vi sử dụng AI trong từng phần của dự án

| STT | Thành phần dự án | Công cụ AI | Mục đích sử dụng | 
| :---: | :--- | :--- | :--- | 
| **1** | **RAG & Hybrid Search** | Gemini / Claude | Gợi ý khung thuật toán kết hợp BM25Okapi và Dense E5, công thức chuẩn hóa Min-Max |
| **2** | **MCP Server & Client** | Gemini / Claude | Hướng dẫn định dạng giao thức Stdio MCP và cơ chế bóc tách schema từ Dataclass 
| **3** | **Agent ReAct Loop** | Claude 3.5 Sonnet | Gợi ý mẫu vòng lặp Native Tool Calling và ràng buộc Action & Verify 
| **4** | **Benchmark & Đo lường** | Gemini / Claude | Gợi ý cấu trúc logging JSONL và đo lường USAGE token từng câu | 

---

## 3. Các thành phần sử dụng 

## Lê Ngọc Hải:

### Trong server.py
- AI hỗ trợ phân tích và gợi ý cú pháp khởi tạo giá trị mặc định cho các @dataclass trên dữ liệu quản lý CTXH.
- AI hỗ trợ viết docstring chuẩn google style để mcp tự đọc thành json schema.

### Trong db.py
- AI gợi ý lệnh kiểm tra và tự động tạo thư mục mkdir(parents=True) trước khi ghi file JSON.
- Hỗ trợ viết vòng lặp chuyển đổi qua lại giữa dict và @dataclass cho từng trường hợp sử dụng tool.

### Trong client.py
- Sinh template cho 2 phương thức `__aenter__` và `__aexit__`
- Gợi ý cách kiểm tra thuộc tính động khi đọc danh sách tools từ server để tránh lỗi.

### Trong quá trình test:
- Hỗ trợ sinh code để kiểm tra luồng stdout, sinh 12 trường hợp giả định, trong đó có 8 trường hợp hợp lệ và 4 trường hợp là không hợp lệ để kiểm tra cơ sở dữ liệu đồng thời quan sát được cách lỗi trả về khi gặp phải các trường hợp không hợp lệ.

---

## Trần Gia Kiệt

### Đề xuất thiết kế module Hybrid Search có Calibration từ chối
- AI giúp lên kế hoạch cấu trúc sườn bài cách trình bày
- Chuẩn hóa điểm số Min-Max về khoảng [0, 1].
- Tích hợp bộ lọc từ khóa/stop words tiếng Việt để tránh việc câu hỏi ngoài lề (out-of-domain) vẫn nhận điểm số cao.
- Testcase và logs
- Hỗ trợ tạo Make file
- Chuẩn hóa bảng chunk dữ liệu bảng để hạn chế mất ngữ nghĩa của chunk

---

## Trần Thiên Ân:

### Trong quá trình cài đặt:
- AI hướng dẫn sử dụng lệnh freeze > requirements.txt giúp thống nhất môi trường và thư viện.
- AI gợi ý cấu trúc cây thư mục chuẩn để thống nhất chung cho cả nhóm.
- AI hướng dẫn và hỗ trợ sinh file .env.example mẫu để quản lý an toàn các biến môi trường và API Key để không push làm lộ thông tin bảo mật lên git.

### src/llm_client:
- AI hỗ trợ bắt các ngoại lệ kết nối API như RateLimitError và APIConnectionError.
- AI gợi ý giải thuật Exponential Backoff kết hợp Jitter ngẫu nhiên để xử lý lỗi nghẽn mạng và tự động thử lại (Retry).

### src/agent/loop.py:
- AI gợi ý và đề xuất thiết kế lớp bảo vệ thứ 2 bằng cách chặn mã nguồn thông qua việc quản lý trạng thái 2 cờ là has_registered và has_verified.
- AI giúp chỉnh sửa lỗi gặp phải khi viết hàm save_trace_log

