from src.retrieval.vector_store import VectorStore
from config import OUTPUT_PATH


def test_vector_store():
    store = VectorStore()
    if OUTPUT_PATH.exists():
        store.build()
        query = "Sinh viên quy đổi điểm CTXH như thế nào?"
        results = store.search(query, top_k=2)
        assert len(results) > 0
        assert "chunk_id" in results[0]
        assert "score" in results[0]


if __name__ == "__main__":
    test_vector_store()
    print("test_vector_store passed!")