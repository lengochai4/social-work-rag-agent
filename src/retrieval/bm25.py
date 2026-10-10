from rich import print 
from rank_bm25 import BM25Okapi
import sys 
from pathlib import Path 
from sentence_transformers import CrossEncoder
import numpy as np

sys.path.append(str(Path(__file__).resolve().parent.parent / "24110103"))
print(sys.path)
from vector_store import VectorStore
# pyrefly: ignore [missing-import]
from src.schemas import DocumentChunk


documents = [
    "The cat sat on the mat.",
    "The dog sat on the log.",
    "The cat and the dog are friends.",
    "The quick brown fox jumps over the lazy dog."
]

tokenized = [doc.lower().split() for doc in documents]
print(tokenized)
bm25 = BM25Okapi(tokenized)
querry = "on the mat".lower().split()
doc_scores = bm25.get_scores(querry)
print(doc_scores)

for doc, score in zip(documents, doc_scores):
    print(f"Document: {doc} | Score: {score:.3f}")


def normalize_scores (scores: list[float]) -> list[float]:
    if not scores: 
        return []
    
    min_score = min(scores)
    max_score = max(scores)
    if max_score == min_score: 
        return [1.0] * len(scores)
    return [(score - min_score) / (max_score - min_score) for score in scores]

def build_bm25_index(chunks: list) -> BM25Okapi:
    tokenized_chunks = [chunk.content.lower().split() for chunk in chunks]
    return BM25Okapi(tokenized_chunks)

def hybrid_search(
    query: str,
    chunks: list,
    bm25_index: BM25Okapi,
    embedding: list[list[float]], 
    top_k: int = 3,
    w_bm25: float = 0.3,
    w_vector: float = 0.7
) -> list[tuple]: 
    """
    Hybrid search: combines BM25 and vector search results based on a weighted score.
    returns a list (chunk_index, hybrid_score) sorted by hybrid_score in descending order.
    """

    def cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        a_arr = np.array(a)
        b_arr = np.array(b)
        if np.linalg.norm(a_arr) == 0 or np.linalg.norm(b_arr) == 0:
            return 0.0
        return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr)))
    
    query_tokens = query.lower().split()
    bm25_scores = list(bm25_index.get_scores(query_tokens))
    query_embedding = VectorStore()._embed_query(query)
    vector_scores = [
        cosine_similarity(query_embedding, chunk_embedding)
        for chunk_embedding in embedding
    ]
    
    normalized_bm25 = normalize_scores(bm25_scores)
    normalized_vector = normalize_scores(vector_scores)
    
    results = [
        (index, (w_bm25 * normalized_bm25[index] + w_vector * normalized_vector[index]))
        for index in range(len(chunks))
    ]
    
    results.sort(key=lambda result: result[1], reverse=True)
    return results[:top_k]


hybrid_results = hybrid_search(
    query="on the mat",
    chunks=[DocumentChunk(content=doc) for doc in documents],
    bm25_index=bm25,
    embedding=[VectorStore()._embed_query(doc) for doc in documents],
    top_k=3,
    w_bm25=0.3,
    w_vector=0.7
)

print("\nHybrid search results:")
for index, score in hybrid_results:
    print(f"Score: {score:.3f} | Document: {documents[index]}")
    
corpus = [
    "The Eiffel Tower is located in Paris, France.",
    "Python is a popular programming language for data science.",
    "BM25 is a ranking function used in information retrieval.",
    "RAG combines retrieval with language model generation.",
    "The Great Wall of China is a historic fortification.",
    "Vector databases store embeddings for similarity search.",
    "Cross-encoders rerank documents by scoring query-doc pairs jointly.",
    "Paris is the capital of France and a major European city.",
]
query ="famous rag-relevant algorithms"

tokenized_corpus = [doc.lower().split() for doc in corpus]
bm25 = BM25Okapi(tokenized_corpus)
scores = bm25.get_scores(query.lower().split())
top_k_idx = sorted(range(len(scores)),key=lambda i: -scores[i])[:5]

print("==BM25 only - no ranking ==")
for i in top_k_idx:
    print(f"{scores[i]:.3f} | {corpus[i]}")

#with ranking
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
K=6
top_k_idx = sorted(range(len(scores)),key=lambda i: -scores[i])[:K]
candidates =[corpus[i] for i in top_k_idx]

pairs = [(query,doc) for doc in candidates]
rerank_scores = reranker.predict(pairs)

reranker = sorted(
    zip(candidates, rerank_scores),
    key=lambda pair: pair[1],
    reverse=True
)
print("\n===BM25 + Cross Encoder Rerank ===")
for doc, s in reranker:
    print(f"{s:.3f}|{doc}")
    
    
    
    
if __name__ == "__main__":
    # Example usage
    hybrid_results = hybrid_search(
        query="on the mat",
        chunks=[DocumentChunk(content=doc) for doc in documents],
        bm25_index=bm25,
        embedding=[VectorStore()._embed_query(doc) for doc in documents],
        top_k=3,
        w_bm25=0.3,
        w_vector=0.7
    )

    print("\nHybrid search results:")
    for index, score in hybrid_results:
        print(f"Score: {score:.3f} | Document: {documents[index]}")
