# Retrieval Module

## Tổng Quan (Overview)
Package `retrieval/` đóng vai trò là "Trái tim" của hệ thống RAG, chuyên xử lý kỹ thuật chuyển đổi chunk thành không gian vector đa chiều (Vector Space) và tìm kiếm ra các chunks phủ hợp nhất đối với câu hỏi của User.

## Trách Nhiệm Các Modules
- `embedder.py`: Nạp Mô hình Huggingface `SentenceTransformer` để sinh vector cho văn bản (chunk) và truy vấn (query).
- `hybrid_search.py`: **Engine Tìm kiếm trung tâm**, kế hợp thuật toán đánh dấu tự nhiên (BM25) và đo lường khoảng cách (Cosine Similarity). Các điểm số này được chuẩn hóa quy về thang `[0,1]` bằng thuật toán Min-Max Normalization.
- `calibration.py`: Một lớp Filter độc lập thực hiện so sánh điểm Hybrid với điểm kịch trần (Threshold) để vứt bỏ các câu hỏi quá xa vời nội dung tri thức.

## Quy Trình Xử Lý Truy Vấn (Hybrid Search Workflow)
1. Load nội dung text từ file dataset `data/ctxh_chunks.json`.
2. Tạo không gian Vector nhúng thông qua model `intfloat/multilingual-e5-base`.
3. Băm nhuyễn từ vựng bằng Tokenizer nội bộ, lọc bỏ Stop Words Tiếng Việt, sau đó tải vào không gian BM25.
4. Khi có câu hỏi User (Query), Hệ thống đối chiếu và lấy Vector chéo (Dot Product).
5. Trả về format List Dataset chuẩn hóa: `list[RetrievalResult]`.

Do đặc thù mô hình `e5-base`, embeddings text của tài liệu sẽ mang prefix `passage: `, còn câu hỏi user sẽ mang prefix `query: `.

## Thao Tác Chạy Thử Retrieval

Hãy sử dụng script mô phỏng có sẵn tại root dự án thay vì gọi các hàm đơn lẻ phức tạp:

```bash
uv run python -m tests.test_hybrid_search
```

Lệnh này sẽ vòng lặp tự động đọc `testset.jsonl` (Bộ 12 câu hỏi chiến lược kiểm thử khả năng tìm kiếm In-domain và đối nghịch Out-domain) rồi in ra toàn bộ điểm số cụ thể từng câu hỏi.

## Lưu ý (Limitations)
- `min_max_normalize` hiện tại là normalization động, sẽ ép mức điểm BM25 cao nhất của truy vấn có mặt về 1.0. Do đó để bộ lọc bám sát nhất nên đẩy hệ số calibration threshold lên cao.
- Có thể scale module này lên cao hơn trong tương lai thông qua CSDL Vector chuyên dụng như Milvus/Qdrant.
