
import numpy as np

from src.retrieval.embedder import Embedder
from src.schemas import RetrievalResult


class DenseSearch:
    def __init__(self, chunks: list[dict], embedder: Embedder):
        if not chunks:
            raise ValueError("chunks cannot be empty.")

        self.chunks = chunks
        self.embedder = embedder

        vectors = self.embedder.embed_documents(
            [chunk["content"] for chunk in chunks]
        )

        self.document_vectors = np.asarray(
            vectors, dtype=np.float32
        )

        # Chuẩn hóa vector để tính cosine similarity bằng dot product.
        norms = np.linalg.norm(self.document_vectors, axis=1)
        if np.any(norms == 0):
            raise ValueError("Document embeddings contain zero vectors.")

        self.document_vectors /= norms[:, None]

    def search(
        self, query: str, top_k: int = 5
    ) -> list[RetrievalResult]:
        if not query.strip():
            raise ValueError("query cannot be empty.")
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        query_vector = np.asarray(
            self.embedder.embed_query(query), dtype=np.float32
        )

        query_norm = np.linalg.norm(query_vector)
        if query_norm == 0:
            raise ValueError("Query embedding is a zero vector.")

        query_vector /= query_norm

        scores = self.document_vectors @ query_vector
        indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for i in indices:
            chunk = self.chunks[int(i)]
            score = float(scores[i])

            results.append(
                RetrievalResult(
                    doc_id=str(chunk.get("doc_id", "")),
                    chunk_id=str(chunk.get("chunk_id", "")),
                    content=chunk["content"],
                    score=score,
                    metadata=chunk.get("metadata", {}),
                    sparse_score=0.0,
                    dense_score=score,
                )
            )

        return results
