from src.retrieval.embedder import Embedder


def test_embedder():
    embedder = Embedder()

    documents = [
        "Sinh viên có quyền khiếu nại kết quả điểm rèn luyện.",
        "Thư viện trường mở cửa từ 7 giờ sáng.",
    ]

    document_vectors = embedder.embed_documents(documents)
    query = "Sinh viên khiếu nại điểm rèn luyện như thế nào?"
    query_vector = embedder.embed_query(query)

    assert len(document_vectors) == 2
    assert len(document_vectors[0]) > 0
    assert len(query_vector) == len(document_vectors[0])


if __name__ == "__main__":
    test_embedder()
    print("test_embedder passed!")