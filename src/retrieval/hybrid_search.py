"""
Hybrid Search Module
Combines Dense Semantic Search (E5) and Sparse Keyword Search (BM25Okapi).
Follows w4 hybrid search architecture with Vietnamese stop words filtering.
"""

from typing import List, Dict, Any, Union, Optional
import re
import numpy as np
from rank_bm25 import BM25Okapi

from src.schemas import RetrievalResult, DocumentChunk

VIETNAMESE_STOPWORDS = {
    "là", "của", "và", "các", "có", "được", "cho", "trong", "để", "với", "những", 
    "khi", "thì", "này", "đã", "từ", "một", "về", "như", "ra", "ở", "hay", "lại",
    "bằng", "vào", "làm", "sao", "thế", "nào", "bao", "nhiêu", "hôm", "nay", "ngày",
    "mai", "gì", "ai", "đâu", "tại", "nào", "hướng", "dẫn", "cách", "đồng", "tiền",
    "phần", "trăm", "thay", "đổi", "trên", "dưới", "dữ", "liệu", "cơ", "sở"
}


def tokenize_vietnamese(text: str) -> List[str]:
    """Tokenize Vietnamese text and remove basic stopwords."""
    words = re.findall(r"\w+", text.lower())
    filtered = [w for w in words if w not in VIETNAMESE_STOPWORDS and len(w) > 1]
    return filtered if filtered else words


def min_max_normalize(scores: List[float]) -> List[float]:
    """Normalize score list into [0, 1] range."""
    if not scores:
        return []
    min_score = min(scores)
    max_score = max(scores)
    if max_score == min_score:
        return [0.0] * len(scores)
    return [(score - min_score) / (max_score - min_score) for score in scores]


class HybridSearch:
    def __init__(
        self,
        chunks: List[Union[Dict[str, Any], DocumentChunk]],
        embedder: Any,
        alpha: float = 0.5,
    ):
        """
        Initialize HybridSearch.
        alpha: weight for dense search (1 - alpha for sparse search).
        """
        if not chunks:
            raise ValueError("chunks cannot be empty.")

        self.chunks = chunks
        self.embedder = embedder
        self.alpha = float(alpha)

        # Extract contents and build BM25 index with tokenization
        self.contents = [
            chunk["content"] if isinstance(chunk, dict) else chunk.content
            for chunk in self.chunks
        ]
        tokenized_corpus = [tokenize_vietnamese(c) for c in self.contents]
        self.bm25 = BM25Okapi(tokenized_corpus)

        # Build or load precomputed document dense vectors
        from config import EMBEDDINGS_PATH
        loaded_vectors = None
        if EMBEDDINGS_PATH.exists():
            try:
                import json
                with EMBEDDINGS_PATH.open("r", encoding="utf-8") as f:
                    saved = json.load(f)
                if saved.get("embeddings") and len(saved["embeddings"]) == len(self.chunks):
                    loaded_vectors = np.asarray(saved["embeddings"], dtype=np.float32)
            except Exception:
                loaded_vectors = None

        if loaded_vectors is not None:
            self.doc_vectors = loaded_vectors
        else:
            vectors = self.embedder.embed_documents(self.contents)
            self.doc_vectors = np.asarray(vectors, dtype=np.float32)

        norms = np.linalg.norm(self.doc_vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.doc_vectors = self.doc_vectors / norms

    def search(self, query: str, top_k: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[RetrievalResult]:
        """Search query using fused Dense + Sparse scores with optional metadata filtering."""
        query = query.strip()
        if not query:
            raise ValueError("Query cannot be empty.")
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        # 1. Sparse BM25 Search
        query_tokens = tokenize_vietnamese(query)
        raw_bm25 = list(self.bm25.get_scores(query_tokens))
        max_bm25 = max(raw_bm25) if raw_bm25 else 0.0

        # Check if query touches any CTXH domain concept
        domain_terms = {
            "ctxh", "sinh", "viên", "điểm", "ngày", "tốt", "nghiệp", "quy", "đổi", 
            "khiếu", "nại", "mùa", "hè", "xanh", "tình", "nguyện", "hoạt", "động",
            "công", "tác", "xã", "hội", "học", "kỳ", "chiến", "dịch", "thực", "tập"
        }
        has_domain_term = any(t in domain_terms for t in query_tokens)

        norm_bm25 = min_max_normalize(raw_bm25)
        if not has_domain_term or max_bm25 < 4.0:
            confidence = 0.0 if not has_domain_term else max(0.0, (max_bm25 - 1.0) / 6.0)
            sparse_scores = [s * confidence for s in norm_bm25]
        else:
            sparse_scores = norm_bm25

        # 2. Dense Semantic Search
        q_vec = np.asarray(self.embedder.embed_query(query), dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm
        dense_scores = (self.doc_vectors @ q_vec).tolist()

        # 3. Score Fusion: alpha * dense + (1 - alpha) * sparse
        hybrid_scores = []
        for i, (d, s) in enumerate(zip(dense_scores, sparse_scores)):
            chunk = self.chunks[i]
            doc_id = chunk.get("doc_id", "") if isinstance(chunk, dict) else chunk.doc_id
            metadata = chunk.get("metadata", {}) if isinstance(chunk, dict) else chunk.metadata

            # Metadata Filter lọc theo doc hoặc metadata
            if filter_metadata:
                match = True
                for k, v in filter_metadata.items():
                    if k == "doc_id" and doc_id != v:
                        match = False
                        break
                    elif k in metadata and metadata[k] != v:
                        match = False
                        break
                if not match:
                    hybrid_scores.append(-1.0)
                    continue

            if not has_domain_term:
                # Completely out-of-domain query penalize dense score below threshold
                score = 0.4 * d
            elif max_bm25 < 4.0:
                score = (self.alpha * d * 0.7) + ((1.0 - self.alpha) * s)
            else:
                score = (self.alpha * d) + ((1.0 - self.alpha) * s)
            hybrid_scores.append(score)

        # Rank indices
        ranked_indices = np.argsort(hybrid_scores)[::-1][:top_k]

        results = []
        for idx in ranked_indices:
            idx = int(idx)
            if hybrid_scores[idx] < 0.0:
                continue
            chunk = self.chunks[idx]
            
            doc_id = chunk.get("doc_id", "") if isinstance(chunk, dict) else chunk.doc_id
            chunk_id = chunk.get("chunk_id", "") if isinstance(chunk, dict) else chunk.chunk_id
            content = chunk.get("content", "") if isinstance(chunk, dict) else chunk.content
            metadata = chunk.get("metadata", {}) if isinstance(chunk, dict) else chunk.metadata

            results.append(
                RetrievalResult(
                    doc_id=str(doc_id),
                    chunk_id=str(chunk_id),
                    content=content,
                    score=float(hybrid_scores[idx]),
                    metadata=metadata,
                    sparse_score=float(sparse_scores[idx]),
                    dense_score=float(dense_scores[idx]),
                )
            )

        return results