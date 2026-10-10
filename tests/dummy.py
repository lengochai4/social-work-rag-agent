
if __name__ == "__main__":
    from src.retrieval.embedder import Embedder
    from config import OUTPUT_PATH
    
    print("*" * 50)
    print("RUNNING HYBRID SEARCH SIMULATION")
    print("*" * 50)
    
    if not OUTPUT_PATH.exists():
        print(f"Error: {OUTPUT_PATH} not found. Please run chunker / build_dataset first.")
    else:
        with OUTPUT_PATH.open("r", encoding="utf-8") as f:
            real_chunks = json.load(f)
            
        print(f"Loaded {len(real_chunks)} chunks for Hybrid Search.")
        print("Initializing Embedder and BM25 Index (This might take a few seconds)...")
        # Initialize with real data
        embedder = Embedder()
        retriever = HybridSearch(chunks=real_chunks, embedder=embedder, alpha=0.5)
        
        query = "Sinh viên khiếu nại kết quả điểm rèn luyện như thế nào?"
        print(f"\nQuery: {query}")
        print("=" * 80)
        
        results = retriever.search(query, top_k=3)
        
        for rank, result in enumerate(results, start=1):
            print(f"\nRank: {rank}")
            print(f"Chunk ID: {result.chunk_id}")
            print(f"Combined Score: {result.score:.5f}")
            print(f"BM25 (Sparse) Score: {result.sparse_score:.5f}")
            print(f"Vector (Dense) Score: {result.dense_score:.5f}")
            print(f"Title: {result.metadata.get('title', 'Unknown')}")
            print(f"Content:\n{result.content[:300]}...")
            print("-" * 80)
        
        # Test calibration
        calibrator = RetrievalCalibration(threshold=0.55)
        will_answer = calibrator.should_answer(results)
        print(f"\n[Calibration] Threshold: 0.55")
        if will_answer:
            print("[Calibration] Result: Có thể trả lời (Đủ độ tin cậy) - Accept")
        else:
            print("[Calibration] Result: Từ chối chuẩn (no_answer) - Reject")
