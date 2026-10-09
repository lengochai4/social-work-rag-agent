# 📋 PHÂN CÔNG CÔNG VIỆC CHI TIẾT THEO NGÀY (THÀNH VIÊN A - B - C)
**Đề tài T5: Trợ lý CTXH: Quy đổi & Đăng ký**

---

## 🟢 NGÀY 1: KHỞI TẠO NỀN TẢNG, DATASET & CORE SERVICES

### 👤 Thành viên A (RAG Core & Dataset)
- Tạo nhánh làm việc: `feat/rag-retrieval`.
- Soạn 3–5 tài liệu văn bản quy chế CTXH (hệ số quy đổi 8 giờ = 1 ngày, trần ngày tối đa theo học kỳ, danh mục mã hoạt động, phiên bản quy định cũ/mới).
- Gán siêu dữ liệu đầy đủ cho từng văn bản: `doc_id`, `title`, `version`, `owner`.
- Viết module đọc văn bản và cắt nhỏ thành các thực thể `DocumentChunk`.
- Soạn sẵn 3–5 dòng giải thích lý do lựa chọn `chunk_size` và `overlap` phục vụ báo cáo.
- Viết script tính vector embedding và lưu trữ kết quả ra file `data/ctxh_chunks.json`.

### 👤 Thành viên B (Mock Database & MCP Server Cơ bản)
- Tạo nhánh làm việc: `feat/mcp-server`.
- Thiết kế và khởi tạo cơ sở dữ liệu JSON giả lập cho sinh viên (`data/db/ctxh_db.json`) gồm: mã sinh viên, danh sách hoạt động đã đăng ký, tổng số ngày CTXH đã tích lũy theo từng học kỳ.
- Viết các hàm nghiệp vụ đọc/ghi file an toàn (sử dụng atomic write để chống hỏng file JSON khi chạy đồng thời).
- Khai báo Schema cho các tool bằng `@dataclass` (`RegisterActivityArgs`, `GetStatusArgs`) lấy từ `src/schemas.py`, viết hàm chuyển đổi sang JSON Schema cho MCP.
- Xây dựng khung MCP Server chạy qua luồng `stdio` (`src/mcp/server.py`).
- Cấu hình chuyển toàn bộ debug/print sang `sys.stderr`, đảm bảo luồng `stdout` sạch 100% chỉ phục vụ gói tin JSON-RPC.

### 👤 Thành viên C (Khung Agent, API Client & Quản lý Repo)
- Tạo repository, cấu trúc thư mục dự án và khởi tạo GitHub Projects (cột: Todo, In Progress, Done).
- Đẩy file hợp đồng kỹ thuật chung `src/schemas.py` lên nhánh `main`.
- Tạo nhánh làm việc: `feat/agent-loop`.
- Tạo file mẫu môi trường `.env.example` và thiết lập `Makefile` cơ bản.
- Tách nội dung system prompt ra file riêng biệt `prompts/agent_system.txt`.
- Xây dựng hàm `call_llm` tích hợp cơ chế retry (Exponential Backoff + Jitter), thời gian chờ timeout và bắt ngoại lệ `RateLimitError`, `APIConnectionError`.

> **Nghiệm thu Ngày 1:**
> - [ ] Repo có đầy đủ `src/schemas.py`, `.env.example`, `Makefile`.
> - [ ] File `data/ctxh_chunks.json` đã được tạo và chứa đầy đủ nội dung kèm vector embedding.
> - [ ] DB JSON đọc/ghi an toàn; MCP Server khởi chạy qua `stdio` không bị crash và không gây bẩn `stdout`.
> - [ ] Hàm `call_llm` thực thi được và xử lý được lỗi mạng.

---

## 🟡 NGÀY 2: TÍCH HỢP HYBRID SEARCH, AGENT LOOP & TESTSET

### 👤 Thành viên A (Hybrid Search, Calibration & Testset)
- Viết module Hybrid Search kết hợp Sparse BM25 (`rank_bm25`) và Dense Cosine Similarity (tích vô hướng NumPy với vector chuẩn hóa).
- Cài đặt hàm chuẩn hóa điểm số Min-Max Normalization: `(s - min) / (max - min)` trước khi nhân trọng số `w_bm25` và `w_vec`.
- Trả về kết quả tìm kiếm dưới dạng danh sách `list[RetrievalResult]` theo chuẩn `src/schemas.py`.
- Thiết lập ngưỡng Calibration Score: nếu điểm cao nhất thấp hơn ngưỡng tin cậy, trả về cờ không tìm thấy tài liệu để Agent từ chối trả lời (`no_answer`).
- Xây dựng tập kiểm thử `tests/testset.jsonl` đủ tối thiểu 12 câu, trong đó có tối thiểu 4 câu thuộc nhóm `no_answer` (các câu còn lại kiểm tra việc tính toán quy đổi giờ → ngày, vượt hạn mức, đăng ký sai mã).

### 👤 Thành viên B (Hoàn thiện MCP Server & Dynamic Client)
- Hoàn thiện đầy đủ mã nguồn cho 2 tools trong `src/mcp/server.py`:
  - `register_activity` (Tool ghi / Side effect): Cập nhật thông tin đăng ký vào database.
  - `get_status` (Tool đọc): Truy vấn số ngày CTXH đã tích lũy của sinh viên theo kỳ.
- Bao bọc toàn bộ thân hàm tool bằng khối `try...except`: khi gặp lỗi nghiệp vụ hoặc ngoại lệ, trả về chuỗi `"Error: <lý do>"` thay vì raise làm dừng tiến trình server.
- Viết module MCP Client (`src/mcp/client.py`) kết nối subprocess đến Server qua `stdio`.
- Hiện thực hóa cơ chế Dynamic Tool Discovery: lấy danh sách tool động từ server, tuyệt đối không hardcode danh sách tên công cụ ở client.

### 👤 Thành viên C (Agent Loop & Chuỗi Action-Verify)
- Tự viết tay vòng lặp Agent Loop (`src/agent/loop.py`) với vòng lặp `for step in range(MAX_STEPS)` (không sử dụng framework ngoài như LangChain, CrewAI).
- Xử lý bóc tách tham số `tool_calls` an toàn (bắt lỗi phân tích cú pháp JSON arguments, không làm chết run).
- Tích hợp module tìm kiếm quy chế từ Thành viên A thành một công cụ gọi trong agent.
- Thiết lập ràng buộc chuỗi **Side effect & Verify**: nếu Agent kích hoạt tool ghi (`register_activity`), bắt buộc phải gọi tiếp tool đọc (`get_status`) để xác minh dữ liệu thực tế đã đổi trước khi đưa ra câu trả lời cuối cùng.

> **Nghiệm thu Ngày 2:**
> - [ ] Module Hybrid Search lọc đúng tài liệu và nhận diện chuẩn các trường hợp từ chối.
> - [ ] MCP Client kết nối thành công với MCP Server và tự động discovery được 2 tools.
> - [ ] Agent Loop chạy trọn vẹn chu trình ReAct thuần: Tra cứu quy chế → Tính toán suy luận → Gọi tool ghi → Tự động gọi tool đọc để verify.
> - [ ] File `tests/testset.jsonl` có đủ 12 câu theo đúng cấu trúc yêu cầu.

---

## 🔴 NGÀY 3: ĐO LƯỜNG, LOGS, ĐÓNG GÓI BÁO CÁO & DEMO

### 👤 Thành viên A (Kiểm thử RAG & Viết Báo cáo phần RAG)
- Chạy kiểm thử độc lập module RAG trên tập dữ liệu kiểm thử, thống kê độ chính xác và tỷ lệ từ chối đúng các câu `no_answer`.
- Chọn ra ít nhất 1 ca kiểm thử thất bại (failure case) và phân tích nguyên nhân kỹ thuật.
- Soạn thảo nội dung Báo cáo Word:
  - **Mục 3:** Thiết kế RAG (1.5 trang: Chunking + lý do, Embedding, Hybrid BM25, truy vấn).
  - **Mục 6:** Đánh giá & Testset (1.5 trang: cấu trúc bộ test, kết quả đo lường, phân tích ca thất bại).
- Review Pull Request của các thành viên khác trước khi hợp nhất mã nguồn vào nhánh `main`.

### 👤 Thành viên B (Kiểm thử MCP & Viết Báo cáo phần MCP)
- Kiểm thử độ bền của Mock Database và MCP Server khi xử lý tuần tự toàn bộ các câu trong bộ testset, bảo đảm không bị race condition hay hỏng file JSON.
- Soạn thảo nội dung Báo cáo Word:
  - **Mục 5:** Thiết kế MCP Server (1 trang: danh sách tool + contract `@dataclass`, transport `stdio`, xử lý `stdout`, cơ chế discovery động của client).
  - **Mục 8:** Bảng phân công nhiệm vụ và liệt kê commit hash tương ứng với phần việc của mình.
- Review Pull Request và cùng Thành viên A, C hợp nhất mã nguồn vào nhánh `main`.

### 👤 Thành viên C (Đo lường USAGE, Đóng gói Hệ thống & Hoàn thiện Báo cáo)
- Viết module ghi log thực thi lưu ra thư mục `logs/` dưới định dạng JSONL.
- Đo lường và trích xuất chi tiết trường `USAGE` cho từng câu hỏi kiểm thử: số lượt gọi LLM (`calls`), số lượng `prompt_tokens`, `completion_tokens`, tổng số `total_tokens`.
- Chạy kiểm thử tự động toàn bộ 12 câu trong `testset.jsonl` tối thiểu 3 lần để sinh đủ ≥3 file log thực tế trong thư mục `logs/`.
- Hoàn thiện cấu hình `Makefile` với 3 lệnh chuẩn hóa: `make setup`, `make demo`, `make eval`.
- Viết file `ai-usage.md` (khai báo công cụ AI, nội dung sử dụng, đoạn code được AI sinh).
- Viết file `README.md` chỉ dẫn lệnh chạy duy nhất để phục vụ chấm điểm và chạy demo.
- Soạn thảo các phần còn lại của Báo cáo Word (`report.docx`):
  - **Mục 1:** Vấn đề, phạm vi, giả định (0.5–1 trang).
  - **Mục 2:** Kiến trúc tổng thể hệ thống (1 trang).
  - **Mục 4:** Thiết kế Agent Loop & Tool (2 trang: cơ chế ReAct, xử lý lỗi, Action & Verify, trace thực tế).
  - **Mục 7:** Hạn chế & Hướng phát triển (0.5 trang: nêu ≥2 hạn chế kỹ thuật trung thực).
  - **Mục 9:** Phụ lục (prompt gốc, trace mẫu, liên kết `ai-usage.md`).
- Tổng hợp file `report.docx` đảm bảo độ dài đúng 8–9 trang.
- Kiểm thử Cold Start trên môi trường sạch: Chạy thử thành công bằng lệnh duy nhất `make setup && make demo`.

> **Nghiệm thu Ngày 3:**
> - [ ] Thư mục `logs/` có đủ ≥3 file log `.jsonl` chạy thật chứa thông số `USAGE` và trace chi tiết.
> - [ ] Hệ thống chạy mượt mà từ đầu chỉ bằng 1 lệnh: `make setup && make demo` và kiểm thử tự động bằng `make eval`.
> - [ ] Toàn bộ code đã merge vào `main` với lịch sử Git thể hiện rõ commit của cả 3 thành viên.
> - [ ] File báo cáo `report.docx` hoàn thiện đúng 8–9 trang kèm đầy đủ các file phụ trợ (`README.md`, `ai-usage.md`, `tests/testset.jsonl`).
