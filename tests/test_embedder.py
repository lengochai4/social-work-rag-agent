
from src.retrieval.embedder import Embedder


def main():
    embedder = Embedder()

    documents = [
        "Sinh viên có quyền khiếu nại kết quả điểm rèn luyện.",
        "Điểm rèn luyện được đánh giá theo các tiêu chí quy định.",
        "Thư viện trường mở cửa từ 7 giờ sáng.",
    ]

    # Embed document chunks
    document_vectors = embedder.embed_documents(documents)

    # Embed user query
    query = "Sinh viên khiếu nại điểm rèn luyện như thế nào?"
    query_vector = embedder.embed_query(query)

    print("Number of document vectors:", len(document_vectors))
    print("Document vector dimension:", len(document_vectors[0]))
    print("Query vector dimension:", len(query_vector))
    print("First 5 values:", query_vector[:5])


if __name__ == "__main__":
    main()
    
    
# uv run python -m tests.test_embedder