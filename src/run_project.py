import json
from pathlib import Path

from src.data_preprocessing.build_dataset import main as build_dataset_main
from src.retrieval.embedder import Embedder
from src.retrieval.hybrid_search import HybridSearch
from src.retrieval.calibration import RetrievalCalibration
from config import OUTPUT_PATH

def run_project():
    print("=" * 80)
    print(" BƯỚC 1: DATA PREPROCESSING (XỬ LÝ DỮ LIỆU & BĂM CHUNKS)")
    print("=" * 80)
    # Lấy tài liệu từ 'document_guide', băm ra lưu vào 'data/ctxh_chunks.json'
    build_dataset_main()
    
    print("\n" + "=" * 80)
    print(" BƯỚC 2: KHỞI TẠO TÌM KIẾM (HYBRID RETRIEVAL)")
    print("=" * 80)
    
    if not OUTPUT_PATH.exists():
        print(f"Lỗi: Không tìm thấy {OUTPUT_PATH}. Pipeline thất bại.")
        return
        
    with OUTPUT_PATH.open("r", encoding="utf-8") as f:
        real_chunks = json.load(f)
        
    print(f"-> Đã nạp thành công {len(real_chunks)} chunks vào bộ nhớ.")
    print("-> Đang khởi tạo Embedder (SentenceTransformer) và BM25 Index...")
    print("   (Quá trình này cần load model E5 và Index Vector nên sẽ mất vài chục giây)\n")
    
    embedder = Embedder()
    retriever = HybridSearch(chunks=real_chunks, embedder=embedder, alpha=0.5)
    calibrator = RetrievalCalibration(threshold=0.55)
    
    print("\n" + "=" * 80)
    print(" BƯỚC 3: MÔ PHỎNG HỎI ĐÁP (SANDBOX TESTING)")
    print("=" * 80)
    
    test_queries = [
        "Sinh viên khiếu nại kết quả đánh giá CTXH như thế nào?",
        "Danh sách những lỗi vi phạm khiến sinh viên bị hủy tư cách đội viên cờ đỏ?",
        "Vì sao iPhone 16 Pro Max lại được người dùng ưa chuộng?" 
    ]
    
    for idx, q in enumerate(test_queries, start=1):
        print(f"\n[Câu hỏi {idx}]: {q}")
        print("-" * 60)
        
        results = retriever.search(q, top_k=1)
        
        if results:
            top_res = results[0]
            will_answer = calibrator.should_answer(results)
            
            clean_content = top_res.content.replace('\n', ' ')
            print(f"   Kết quả tìm được (ID: {top_res.chunk_id}):")
            print(f"   - Score Tổng (Hybrid): {top_res.score:.5f}")
            print(f"   - Score BM25 (Sparse) : {top_res.sparse_score:.4f}")
            print(f"   - Score E5 (Dense)    : {top_res.dense_score:.4f}")
            print(f"   - Nguồn văn bản       : {top_res.metadata.get('title', 'Unknown')}")
            print(f"   - Trích đoạn          : {clean_content[:150]}...")
            print("")
            
            if will_answer:
                print(f"   => KẾT LUẬN: ĐỦ TIN CẬY TRẢ LỜI (Accept | Score >= {calibrator.threshold}) ")
            else:
                print(f"   => KẾT LUẬN: TỪ CHỐI TRẢ LỜI (no_answer | Score < {calibrator.threshold}) ")
        else:
            print("   => Không tìm thấy bất kỳ chunks nào phù hợp.")

if __name__ == "__main__":
    run_project()
