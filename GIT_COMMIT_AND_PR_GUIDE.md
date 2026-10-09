# 🚀 HƯỚNG DẪN LÀM VIỆC NHÓM & QUY TRÌNH TỰ ĐỘNG CẬP NHẬT GITHUB PROJECTS

Tài liệu này hướng dẫn chuẩn thao tác Git và cách liên kết công việc để bảng Kanban trên GitHub Projects **tự động nhảy cột 100%**, hạn chế xung đột code (conflict) và đáp ứng yêu cầu chấm điểm lịch sử Git của giảng viên.

---

## 1. CƠ CHẾ HOẠT ĐỘNG CỦA HỆ THỐNG TỰ ĐỘNG

Dự án đã được cấu hình 4 workflows tự động:
1. **Issue vừa được tạo:** Tự động nạp vào Board và nhận trạng thái `Todo`.
2. **Khi bắt đầu làm:** Thành viên gán tên mình vào Issue và kéo thẻ sang `In progress`.
3. **Khi mở Pull Request (PR):** Thẻ Issue liên kết tự động chuyển sang `In review`.
4. **Khi Merge PR vào nhánh main:** Thẻ Issue tự động đóng và chuyển sang `Done`.

---

## 2. QUY TRÌNH 5 BƯỚC CHO TỪNG THÀNH VIÊN

### 📌 Bước 1: Nhận việc trên GitHub
1. Vào tab **Issues** hoặc mở trực tiếp trên bảng **Projects**.
2. Chọn Issue mà bạn chuẩn bị thực hiện.
3. Ở cột bên phải:
   - Mục **Assignees**: Chọn tên GitHub của bạn.
   - Kéo thẻ từ `Todo` sang `In progress` trên Board.

---

### 📌 Bước 2: Tạo nhánh tính năng (Branch) ở máy cục bộ
Tuyệt đối **KHÔNG** commit hoặc đẩy code trực tiếp lên nhánh `main`. Luôn luôn tạo nhánh mới từ nhánh `main` mới nhất:

```bash
# 1. Chuyển về main và kéo code mới nhất về
git checkout main
git pull origin main

# 2. Tạo nhánh chức năng riêng của bạn (đặt tên theo mã Issue)
# Ví dụ: Thành viên A làm Issue #1
git checkout -b feat/a1-rag-chunking

# Ví dụ: Thành viên B làm Issue #4
git checkout -b feat/b1-mcp-server

# Ví dụ: Thành viên C làm Issue #7
git checkout -b feat/c1-agent-loop


### Hướng dẫn 
git checkout: Lệnh dùng để chuyển đổi qua lại giữa các nhánh (branches) trong kho mã nguồn Git.

-b (viết tắt của branch): Tham số chỉ thị cho Git: "Hãy tạo mới nhánh này trước rồi lập tức chuyển vùng làm việc sang nhánh đó". Nếu không có -b, Git sẽ hiểu là nhánh đã có sẵn; nếu nhánh chưa tồn tại, Git sẽ báo lỗi.

feat/a1-rag-chunking: Tên nhánh mới được đặt chuẩn theo quy ước:

feat/ (feature): Tiền tố tiêu chuẩn trong ngành phần mềm, thông báo đây là nhánh phát triển một chức năng/tính năng mới.

a1: Mã định danh liên kết trực tiếp với thẻ công việc (Issue A1) trên bảng phân công GitHub Projects.

rag-chunking: Tên mô tả ngắn gọn nội dung công việc (ở đây là phân đoạn tài liệu và xử lý chunking cho RAG).


***NGUYÊN TẮC***
- Mỗi chức năng của mỗi người thiết kế sẽ là 1 nhánh duy nhất

---

## 📌 Bước 3: Code và Commit rõ ràng

Trong quá trình thực hiện công việc trên nhánh tính năng cá nhân, thành viên cần commit thường xuyên với thông điệp rõ nghĩa, tuân thủ chuẩn **Conventional Commits** và **bắt buộc gắn mã số Issue (`#Issue_ID`)** để phục vụ việc đối chiếu lịch sử commit của từng người khi bảo vệ đồ án.

### 1. Luồng lệnh thực thi tại Terminal
```bash
# 1. Kiểm tra trạng thái và danh sách file đã thay đổi
git status

# 2. Đưa các file đã sửa đổi vào khu vực chờ commit (Staging Area)
git add .

# 3. Tạo commit với thông điệp chuẩn và gắn mã Issue tương ứng
# Cú pháp: git commit -m "<type>(<phạm vi>): <mô tả ngắn gọn> (#<Mã_Issue>)"
git commit -m "feat(rag): parse policy documents and generate chunk embeddings (#1)"

## 📌 Bước 4: Git push origin
Chỉ push code của issue mới làm xong lên chính nhánh của issue đó 
