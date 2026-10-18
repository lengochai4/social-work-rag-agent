# BÁO CÁO THỬ NGHIỆM ĐÁNH GIÁ CƠ CHẾ METADATA FILTERING

## 1. Giới thiệu thử nghiệm
- **Tài liệu gốc**: `QUY_DINH_DIEM_CTXH-SOTAYSINHVIEN-2024.md` (doc_id: `CTXH_002`, publication_year: `2024`)
- **Tài liệu giả lập (Fake Data)**: `QUY_DINH_DIEM_CTXH-SOTAYSINHVIEN-2025.md` (doc_id: `CTXH_003`, publication_year: `2025`)
- **Mục đích**: Kiểm tra năng lực phân tách văn bản quy chế cũ và mới thông qua siêu dữ liệu `publication_year`, tránh hiện tượng mô hình trả về điểm số bị nhiễu do xung đột thời gian (Temporal Conflict).

## 2. Bảng so sánh kết quả truy vấn (With Filter vs Without Filter)

| Case ID | Câu hỏi truy vấn | Năm mục tiêu | Kỳ vọng quy định | Without Filter (Doc / Năm) | With Filter (Doc / Năm) | Độ chính xác phiên bản |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: |
| **TC01** | Theo quy định năm 2024, sinh viên trực tiếp tham gia hiến máu tình nguyện được cộng bao nhiêu điểm CTXH? | 2024 | 5 điểm (0,5 ngày CTXH) | CTXH_002 (2024) | CTXH_002 (2024) | 100% Chính xác |
| **TC02** | Theo quy định mới năm 2025, trực tiếp hiến máu tình nguyện được cộng bao nhiêu điểm và quy đổi bao nhiêu ngày CTXH? | 2025 | 10 điểm (1 ngày CTXH) | CTXH_002 (2024) | CTXH_003 (2025) | 100% Chính xác |
| **TC03** | Sinh viên cần tích lũy tối thiểu bao nhiêu điểm CTXH để đủ điều kiện xét tốt nghiệp theo quy định năm 2024? | 2024 | 40 điểm CTXH (tương đương 04 Ngày CTXH) | CTXH_001 (2013) | CTXH_002 (2024) | 100% Chính xác |
| **TC04** | Theo quy định năm 2025, tham gia chiến dịch Mùa hè xanh suốt 01 tháng tại các tỉnh được cộng thang điểm bao nhiêu? | 2025 | Thang điểm 30→50 (quy đổi 3→5 ngày CTXH) | CTXH_002 (2024) | CTXH_003 (2025) | 100% Chính xác |

## 3. Chi tiết từng ca kiểm thử

### TC01: Theo quy định năm 2024, sinh viên trực tiếp tham gia hiến máu tình nguyện được cộng bao nhiêu điểm CTXH?
- **Tài liệu mục tiêu**: `CTXH_002` (Năm `2024`)
- **Quy định chuẩn**: 5 điểm (0,5 ngày CTXH)
- **Kết quả Without Filter**: Tài liệu `CTXH_002` (Năm `2024`), Score: `0.9657`
- **Kết quả With Filter**: Tài liệu `CTXH_002` (Năm `2024`), Score: `0.9657`
- **Trích dẫn nội dung**: *"| Lĩnh vực CTXH | Mã | Nội dung & định lượng | Thang điểm | Quy đổi sang ngày CTXH | | ------------------------------ | ------ | -----------..."*

### TC02: Theo quy định mới năm 2025, trực tiếp hiến máu tình nguyện được cộng bao nhiêu điểm và quy đổi bao nhiêu ngày CTXH?
- **Tài liệu mục tiêu**: `CTXH_003` (Năm `2025`)
- **Quy định chuẩn**: 10 điểm (1 ngày CTXH)
- **Kết quả Without Filter**: Tài liệu `CTXH_002` (Năm `2024`), Score: `0.9669`
- **Kết quả With Filter**: Tài liệu `CTXH_003` (Năm `2025`), Score: `0.9645`
- **Trích dẫn nội dung**: *"| Lĩnh vực CTXH | Mã | Nội dung & định lượng | Thang điểm | Quy đổi sang ngày CTXH | | ------------------------------ | ------ | -----------..."*

### TC03: Sinh viên cần tích lũy tối thiểu bao nhiêu điểm CTXH để đủ điều kiện xét tốt nghiệp theo quy định năm 2024?
- **Tài liệu mục tiêu**: `CTXH_002` (Năm `2024`)
- **Quy định chuẩn**: 40 điểm CTXH (tương đương 04 Ngày CTXH)
- **Kết quả Without Filter**: Tài liệu `CTXH_001` (Năm `2013`), Score: `0.9612`
- **Kết quả With Filter**: Tài liệu `CTXH_002` (Năm `2024`), Score: `0.7553`
- **Trích dẫn nội dung**: *"## 3. Yêu cầu đối với sinh viên về hoạt động CTXH  - Sinh viên phải tích lũy 04 Ngày CTXH (tương đương 40 điểm CTXH) để được xét tốt nghiệp..."*

### TC04: Theo quy định năm 2025, tham gia chiến dịch Mùa hè xanh suốt 01 tháng tại các tỉnh được cộng thang điểm bao nhiêu?
- **Tài liệu mục tiêu**: `CTXH_003` (Năm `2025`)
- **Quy định chuẩn**: Thang điểm 30→50 (quy đổi 3→5 ngày CTXH)
- **Kết quả Without Filter**: Tài liệu `CTXH_002` (Năm `2024`), Score: `0.9577`
- **Kết quả With Filter**: Tài liệu `CTXH_003` (Năm `2025`), Score: `0.9555`
- **Trích dẫn nội dung**: *"| Lĩnh vực CTXH | Mã | Nội dung & định lượng | Thang điểm | Quy đổi sang ngày CTXH | | ------------------------------ | ------ | -----------..."*

## 4. Kết luận cho Báo cáo (Dành cho Hải)
1. **Hiệu quả của Metadata Filtering**: Khi bổ sung ràng buộc siêu dữ liệu `publication_year`, hệ thống đạt độ chính xác **100% (4/4 cases)** trong việc truy xuất đúng văn bản quy định của năm được hỏi.
2. **Xử lý xung đột thời gian (Temporal Conflict)**: Đối với các quy định có cùng từ khóa (như *hiến máu tình nguyện*, *mùa hè xanh*, *xét tốt nghiệp*) nhưng thay đổi điểm qua các năm, Metadata Filter giúp loại bỏ hoàn toàn các chunk nhiễu từ các năm không mong muốn, bảo đảm tính toàn vẹn và độ tin cậy của câu trả lời từ Agent.
