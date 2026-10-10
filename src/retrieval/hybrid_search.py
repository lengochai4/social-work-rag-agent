""" 
Hybrid Search Implementation

This module implements a hybrid search approach that combines multiple search techniques to improve the accuracy and relevance of search results.

"""

import re 
import tokenize
from typing import List, Optional, Any, Protocol
from dataclasses import dataclass, field
from src.retrieval.embedder import Embedder

import numpy as np
from rank_bm25 import BM25Okapi


""" 
score: điểm kết hợp cuối cùng để xếp hang các kết quả tìm kiếm
dense_score: điểm vector embedding (cosine similarity) giữa truy vấn và chunk
spare_core: điểm BM25 giữa truy vấn và chunk
metadata: thông tin bổ sung về chunk, ví dụ như tên tài liệu, ngày tạo, v.v.
"""
@dataclass
class RetrievalResult:
    doc_id: str
    chunk_id: str
    content: str
    score: float
    metadata: dict = field(default_factory=dict)
    spare_core: float = 0.0 
    dense_score: float = 0.0

class EmbeddingModel(Protocol):
    def embed_query(self, query: str) -> List[float]:
        ...

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        ...    
        
    def tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+', text.lower(), flags=re.UNICODE)
    
    def min_max_normalize(self, scores: List[float]) -> List[float]:
        """Normalize a list of scores to the range [0, 1] using min-max normalization."""
        if not scores:
            return []
        min_score = min(scores)
        max_score = max(scores)
        if max_score == min_score:
            return [1.0] * len(scores)
        return [(score - min_score) / (max_score - min_score) for score in scores]
    
    def build_bm25_index(self, chunks: List[dict[str, Any]]) -> BM25Okapi:
        tokenized_chunks = [self.tokenize(chunk["content"]) for chunk in chunks]
        return BM25Okapi(tokenized_chunks)

class HybridSearch:
    def __init__(
        self,
        chunks: list[dict[str, Any]],
        embedder: Embedder,
        alpha: float = 0.5,
        ):
        if not 0.0 <= alpha <= 1.0:
            raise ValueError("alpha must be between 0 and 1.")

        if not chunks:
            raise ValueError("chunks cannot be empty.")

        self.chunks = chunks
        self.embedder = embedder
        self.alpha = alpha

        self.tokenized_corpus = [
            tokenize(chunk["content"]) for chunk in chunks
        ]

        self.bm25 = BM25Okapi(self.tokenized_corpus)

        document_vectors = self.embedder.embed_documents(
            [chunk["content"] for chunk in chunks]
        )

        self.document_vectors = np.asarray(
            document_vectors, dtype=np.float32
        )

        if self.document_vectors.ndim != 2:
            raise ValueError("Document embeddings must be a 2D array.")

        if len(self.document_vectors) != len(self.chunks):
            raise ValueError(
                "Number of embeddings must match number of chunks."
            )

        norms = np.linalg.norm(self.document_vectors, axis=1)
        if np.any(norms == 0):
            raise ValueError("Document embeddings must not contain zero vectors.")

        self.document_vectors = (
            self.document_vectors / norms[:, None]
        )


def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievalResult]:
        if not query.strip():
            raise ValueError("query cannot be empty.")

        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        # Sparse retrieval: BM25 followed by Min-Max normalization.
        sparse_raw = self.bm25.get_scores(tokenize(query)).tolist()
        sparse_scores = min_max_normalize(sparse_raw)

        # Dense retrieval: cosine similarity.
        query_vector = np.asarray(
            self.embedder.embed_query(query), dtype=np.float32
        ).reshape(-1)

        if query_vector.shape[0] != self.document_vectors.shape[1]:
            raise ValueError(
                "Query and document embedding dimensions differ."
            )

        query_norm = np.linalg.norm(query_vector)
        if query_norm == 0:
            raise ValueError("Query embedding must not be a zero vector.")

        query_vector = query_vector / query_norm
        dense_raw = self.document_vectors @ query_vector

        # Map cosine similarity from [-1, 1] to [0, 1].
        dense_scores = np.clip((dense_raw + 1.0) / 2.0, 0.0, 1.0)

        # Weighted fusion.
        combined_scores = (
            self.alpha * np.asarray(sparse_scores)
            + (1.0 - self.alpha) * dense_scores
        )

        ranked_indices = np.argsort(combined_scores)[::-1][:top_k]

        results = []
        for index in ranked_indices:
            chunk = self.chunks[int(index)]

            results.append(
                RetrievalResult(
                    doc_id=str(chunk.get("doc_id", "")),
                    chunk_id=str(chunk.get("chunk_id", "")),
                    content=chunk["content"],
                    score=float(combined_scores[index]),
                    metadata=chunk.get("metadata", {}),
                    sparse_score=float(sparse_scores[index]),
                    dense_score=float(dense_scores[index]),
                )
            )

        return results
