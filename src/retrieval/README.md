# Retrieval Module

## Overview

The `retrieval` package implements the Grounded Retrieval Layer of the Social Work RAG Agent. It combines Lexical BM25 search with Dense Semantic vector search (Hybrid Search), supports metadata filtering, and enforces confidence calibration to reject out-of-domain queries.

## Module Architecture

| Module | Technical Responsibility |
| :--- | :--- |
| **`embedder.py`** | Wraps `SentenceTransformer` using `intfloat/multilingual-e5-base` (768 dimensions). Applies the required `passage: ` prefix for indexing and `query: ` prefix for queries, outputting L2-normalized vectors. |
| **`bm25.py`** | Lexical keyword retrieval utilizing `BM25Okapi` with Vietnamese word segmentation and domain-tailored administrative stopword removal. |
| **`dense_search.py`** | Semantic vector search calculating cosine similarity via matrix dot products over precomputed L2-normalized embeddings. |
| **`hybrid_search.py`** | Core retrieval engine that fuses dense semantic scores and sparse lexical scores via Min-Max normalization, performs domain concept checks, and enforces metadata filtering. |
| **`calibration.py`** | Confidence calibration filter applying an absolute decision threshold (`threshold = 0.55`) to trigger safe refusal (`no_answer`) on unsupported or irrelevant questions. |
| **`vector_store.py`** | In-memory storage abstraction managing document chunks and their associated embedding vectors. |

## Hybrid Search Formulation

The hybrid retrieval score fuses normalized dense semantic similarity and sparse BM25 relevance using a configurable weighting factor $\alpha$ (default $\alpha = 0.5$):

$$\text{Score}_{\text{hybrid}} = \alpha \cdot \text{Score}_{\text{dense}} + (1 - \alpha) \cdot \text{Score}_{\text{sparse}}$$

- **Dense Semantic Score**: Dot product of normalized query and document embeddings.
- **Sparse BM25 Score**: Min-Max normalized BM25 score scaled by query domain relevance confidence.
- **Domain Verification**: Checks for regulatory CTXH terms; queries devoid of domain concepts have their dense scores penalized to prevent false-positive matches on general vocabulary.

## Metadata Filtering

The search engine supports pre-ranking metadata filtering through the `filter_metadata` parameter in `HybridSearch.search()`:

```python
# Filter retrieval candidates strictly to a specific document version or ID
results = retriever.search(
    query="điều kiện xét tốt nghiệp",
    top_k=3,
    filter_metadata={"doc_id": "CTXH_001"}
)
```

Chunks not matching the filter criteria are assigned a score of `-1.0` and excluded from the final ranked list.

## Confidence Calibration

To satisfy the refusal benchmark and eliminate hallucination:

- **Threshold**: Set to `0.55` based on empirical ablation experiments.
- **Decision Logic**: If the top-ranked candidate score satisfies $\text{Score}_{\text{top}} \ge 0.55$, the retrieval context is passed to the generation layer.
- **Rejection Behavior**: If $\text{Score}_{\text{top}} < 0.55$, `calibrator.should_answer()` returns `False`, causing the pipeline to emit the standard refusal response: *"Tôi chưa tìm thấy đủ căn cứ trong tài liệu hiện có để trả lời câu hỏi này (no_answer)."*

## Query Execution Workflow

```
User Query
   │
   ├──> Tokenize & Filter Stopwords ──> BM25 Scoring ──> Min-Max Normalize
   │
   ├──> Encode ("query: ...") ────────> Cosine Sim ───> Normalize
   │
   └──> Score Fusion & Metadata Filter
           │
           ▼
        Ranked Results (Top-K)
           │
           ▼
     Calibration Check (Score >= 0.55)
      ├── Yes ──> Emit Context with Citations [doc_id, chunk_id]
      └── No  ──> Trigger Safe Refusal (no_answer)
```

## Testing & Verification

Run unit tests for retrieval, calibration, normalization, and metadata filtering:

```bash
# Using pytest directly
pytest tests/test_retrieval.py -v

# Using uv
uv run pytest tests/test_retrieval.py -v
```


