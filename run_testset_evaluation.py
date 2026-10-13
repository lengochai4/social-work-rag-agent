import json
from pathlib import Path
from dataclasses import asdict

from src.schemas import RetrievalResult
from src.retrieval.hybrid_search import HybridSearch
from src.retrieval.embedder import Embedder
from src.retrieval.dense_search import DenseSearch
from config import TESTSET_PATH, OUTPUT_TEST_RAG_PATH

RETRIEVAL_MODE = "dense" #dense hoặc hybrid

TOP_K = 5


def load_testset(path: Path) -> list[dict]:
    """Đọc bộ câu hỏi JSONL."""
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy testset: {path}")

    with path.open("r", encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]



def build_retriever():
    with open("data/ctxh_chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)

    embedder = Embedder()

    if RETRIEVAL_MODE == "dense":
        return DenseSearch(chunks, embedder)

    if RETRIEVAL_MODE == "hybrid":
        return HybridSearch(
            chunks=chunks,
            embedder=embedder,
            alpha=0.5,
        )

    raise ValueError(f"Unknown retrieval mode: {RETRIEVAL_MODE}")



def main():
    testset = load_testset(TESTSET_PATH)
    retriever = build_retriever()

    output = []

    for index, item in enumerate(testset, start=1):
        question = item.get("question") or item.get("query")

        if not question:
            raise ValueError(f"Câu hỏi thứ {index} bị thiếu nội dung.")

        results = retriever.search(question.strip(), top_k=TOP_K)

        output.append({
            "question_id": item.get("id", index),
            "question": question.strip(),
            "expected": item.get(
                "expected",
                item.get("answerable")
            ),
            "retrieval_results": [
                asdict(result)
                if isinstance(result, RetrievalResult)
                else result
                for result in results
            ],
        })

        print(f"[{index}/{len(testset)}] "
              f"Tìm được {len(results)} chunks")

    OUTPUT_TEST_RAG_PATH.parent.mkdir(
        parents=True, exist_ok=True
    )

    with OUTPUT_TEST_RAG_PATH.open("w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)

    print(f"\nĐã lưu kết quả: {OUTPUT_TEST_RAG_PATH}")
    print(f"Tổng số câu hỏi: {len(output)}")


if __name__ == "__main__":
    main()
