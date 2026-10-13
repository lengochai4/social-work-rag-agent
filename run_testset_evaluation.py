"""
Testset Evaluation Script
=========================
Reads testset.jsonl, runs hybrid_search + calibration on each query,
and outputs whether each query is "phù hợp" (answerable) or "no_answer".

Usage:
    python run_testset_evaluation.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

from config import OUTPUT_PATH
from src.data_preprocessing.build_dataset import main as build_dataset_main
from src.retrieval.embedder import Embedder
from src.retrieval.hybrid_search import HybridSearch
from src.retrieval.calibration import RetrievalCalibration


# ── Configuration ──────────────────────────────────────────────────
TESTSET_PATH = Path(__file__).resolve().parent / "tests" / "testset.jsonl"
RESULTS_OUTPUT_PATH = Path(__file__).resolve().parent / "tests" / "evaluation_results.json"
CALIBRATION_THRESHOLD = 0.55
HYBRID_ALPHA = 0.5
TOP_K = 3  # retrieve top-3 to give calibration more context


def load_testset(path: Path) -> list[dict]:
    """Load test cases from a JSONL file."""
    if not path.exists():
        print(f"Testset not found: {path}")
        sys.exit(1)

    cases = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))

    print(f"Đã nạp {len(cases)} câu hỏi từ {path.name}")
    return cases


def build_chunks_if_needed() -> list[dict]:
    """Build or load document chunks."""
    if not OUTPUT_PATH.exists():
        print("ctxh_chunks.json chưa tồn tại. Đang chạy build_dataset...")
        build_dataset_main()

    if not OUTPUT_PATH.exists():
        print(f"Vẫn không tìm thấy {OUTPUT_PATH} sau khi build. Kiểm tra dữ liệu.")
        sys.exit(1)

    with OUTPUT_PATH.open("r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Đã nạp {len(chunks)} chunks từ {OUTPUT_PATH.name}")
    return chunks


def evaluate_testset():
    """Main evaluation: hybrid_search + calibration on testset.jsonl."""
    print("=" * 70)
    print("  TESTSET EVALUATION: Hybrid Search + Calibration")
    print("=" * 70)
    print(f"  Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Threshold: {CALIBRATION_THRESHOLD}")
    print(f"  Alpha (Sparse/Dense): {HYBRID_ALPHA}")
    print(f"  Top-K: {TOP_K}")
    print("=" * 70 + "\n")

    # ── Step 1: Load chunks ────────────────────────────────────────
    chunks = build_chunks_if_needed()

    # ── Step 2: Initialize Embedder, HybridSearch, Calibration ─────
    print("\nĐang khởi tạo Embedder (SentenceTransformer)...")
    embedder = Embedder()

    print("Đang khởi tạo HybridSearch (BM25 + Dense)...")
    retriever = HybridSearch(chunks=chunks, embedder=embedder, alpha=HYBRID_ALPHA)

    calibrator = RetrievalCalibration(threshold=CALIBRATION_THRESHOLD)
    print("Khởi tạo thành công!\n")

    # ── Step 3: Load testset ───────────────────────────────────────
    test_cases = load_testset(TESTSET_PATH)

    # ── Step 4: Run evaluation ─────────────────────────────────────
    print("\n" + "=" * 70)
    print("  KẾT QUẢ ĐÁNH GIÁ")
    print("=" * 70 + "\n")

    results_log = []
    passed = 0
    failed = 0

    for idx, case in enumerate(test_cases, start=1):
        query = case["query"]
        expected = case["expected_answerable"]

        # Hybrid search
        search_results = retriever.search(query, top_k=TOP_K)

        # Calibration decision
        will_answer = calibrator.should_answer(search_results)
        calibrated = calibrator.calibrate(search_results)

        # Compare with expected
        is_correct = will_answer == expected
        status = "PASS" if is_correct else "FAIL"

        if is_correct:
            passed += 1
        else:
            failed += 1

        # Decision label
        if will_answer:
            decision = "PHÙ HỢP (answerable)"
        else:
            decision = "NO_ANSWER (từ chối)"

        expected_label = "PHÙ HỢP" if expected else "NO_ANSWER"

        # Print result
        print(f"─── Câu {idx:02d} ───────────────────────────────────────")
        print(f"  Query   : {query}")
        print(f"  Kỳ vọng : {expected_label}")
        print(f"  Thực tế : {decision}")
        print(f"  Kết quả : {status}")

        if search_results:
            top = search_results[0]
            print(f"  Top-1 Score: {top.score:.4f} "
                  f"[BM25: {top.sparse_score:.4f} | E5: {top.dense_score:.4f}]")
            content_preview = top.content.replace("\n", " ")[:120]
            print(f"  Trích đoạn : {content_preview}...")
            print(f"  Nguồn     : {top.metadata.get('title', 'N/A')}")
        else:
            print("  Không tìm thấy kết quả nào.")

        print()

        # Log for export
        result_entry = {
            "index": idx,
            "query": query,
            "expected_answerable": expected,
            "actual_answerable": will_answer,
            "is_correct": is_correct,
            "decision": decision,
            "top_results": [
                {
                    "chunk_id": r.chunk_id,
                    "score": round(r.score, 5),
                    "sparse_score": round(r.sparse_score, 5),
                    "dense_score": round(r.dense_score, 5),
                    "content_preview": r.content[:200],
                    "source": r.metadata.get("title", "N/A"),
                }
                for r in search_results[:3]
            ],
        }
        results_log.append(result_entry)

    # ── Step 5: Summary ────────────────────────────────────────────
    total = len(test_cases)
    accuracy = (passed / total * 100) if total > 0 else 0

    print("=" * 70)
    print("  TỔNG KẾT")
    print("=" * 70)
    print(f"  Tổng số câu hỏi   : {total}")
    print(f"  Đúng (PASS)        : {passed}")
    print(f"  Sai (FAIL)         : {failed}")
    print(f"  Accuracy           : {accuracy:.1f}%")
    print(f"  Threshold          : {CALIBRATION_THRESHOLD}")
    print(f"  Alpha              : {HYBRID_ALPHA}")
    print("=" * 70)

    # ── Step 6: Save results to JSON ───────────────────────────────
    output_data = {
        "evaluation_time": datetime.now().isoformat(),
        "config": {
            "threshold": CALIBRATION_THRESHOLD,
            "alpha": HYBRID_ALPHA,
            "top_k": TOP_K,
            "embedding_model": "intfloat/multilingual-e5-base",
        },
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "accuracy_percent": round(accuracy, 2),
        },
        "results": results_log,
    }

    with RESULTS_OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\nKết quả đã được lưu vào: {RESULTS_OUTPUT_PATH}")


if __name__ == "__main__":
    evaluate_testset()
