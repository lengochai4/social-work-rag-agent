# Retrieval Module

## Overview
The `retrieval/` package serves as the core search engine for the Social Work RAG Agent. It handles indexing chunks into dense and sparse vector spaces and retrieving the most relevant contexts for a given user query.

## Modules & Responsibilities
- `embedder.py`: Wraps HuggingFace's `SentenceTransformer` to produce embedding vectors for document chunks and user queries (`intfloat/multilingual-e5-base`).
- `bm25.py`: Lexical BM25 search over tokenized and stopword-filtered Vietnamese documents.
- `dense_search.py`: Cosine similarity search over precomputed dense vectors.
- `vector_store.py`: In-memory storage for chunks and dense embeddings.
- `hybrid_search.py`: **Central Search Engine** combining BM25 and Dense search using Min-Max score normalization and tunable weights ($\alpha \cdot \text{Dense} + (1-\alpha) \cdot \text{BM25}$). Supports metadata filtering (`doc_id`).
- `calibration.py`: Independent confidence filter applying an absolute score threshold to reject out-of-domain or irrelevant queries.

## Query Processing Workflow
1. Load chunks from `data/ctxh_chunks.json` and embeddings from `data/ctxh_embeddings.json`.
2. Format queries with `query: ` prefix (matching E5 passage prefix `passage: `).
3. Compute dense cosine similarities and sparse BM25 scores across all chunks.
4. Apply metadata filter (e.g., `doc_id="D2"`) if specified.
5. Min-max normalize both score distributions to $[0, 1]$ and compute weighted hybrid scores.
6. Return calibrated `List[RetrievalResult]` chunks ranked by score.

## Testing
Run the retrieval test suite:
```bash
pytest tests/test_retrieval.py -v
```

