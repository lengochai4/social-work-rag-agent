
from retrieval.vector_store import VectorStore
from config import EMBEDDINGS_PATH, OUTPUT_PATH


def main():
    store = VectorStore()

    # Load chunks and build/load embeddings.
    store.build()

    query = "Sinh viên khiếu nại kết quả điểm rèn luyện như thế nào?"
    results = store.search(query, top_k=5)

    print(f"\nQuery: {query}")
    print("=" * 80)

    for rank, result in enumerate(results, start=1):
        print(f"\nRank: {rank}")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Score: {result['score']:.4f}")
        print(f"Title: {result.get('metadata', {}).get('title')}")
        print(f"Content:\n{result['content'][:500]}")
        print("-" * 80)


if __name__ == "__main__":
    main()
    
#uv run python -m tests.test_vector_store