# Retrieval

## Overview

The `retrieval/` package converts document chunks into vector representations and retrieves the most relevant chunks for a user query. These results can later be provided to the language model as context for generating grounded answers.

## Module Responsibilities

- `embedder.py`: Uses a Sentence Transformers model to generate embeddings for document chunks and user queries.
- `vector_store.py`: Loads the chunk dataset, creates or reuses stored embeddings, calculates cosine similarity, and returns the top-k most relevant chunks.
- `__init__.py`: Marks the directory as a Python package.

## Retrieval Workflow

1. Load the chunk dataset from `data/ctxh_chunks.json`.
2. Generate embeddings for each chunk using `intfloat/multilingual-e5-base`.
3. Save the embeddings to `data/ctxh_embeddings.json` for reuse.
4. Convert a user query into an embedding.
5. Calculate cosine similarity between the query vector and document vectors.
6. Rank the chunks by similarity score and return the top-k results.

The embedding model uses the `passage:` prefix for document content and the `query:` prefix for user queries. Embeddings are normalized before similarity calculations.

## Build the Vector Store

Run the following command from the project root:

```bash
uv run python -m tests.test_vector_store
```

The first run generates embeddings if no valid saved embeddings are available. Subsequent runs can reuse the saved vectors when the chunk identifiers and model name match.

To force embedding regeneration, call:

```python
store.build(force_rebuild=True)
```

## Search for Relevant Chunks

```python
from src.retrieval.vector_store import VectorStore

store = VectorStore()
store.build()

results = store.search(
    query="How can a student appeal a training score?",
    top_k=5,
)

for result in results:
    print(result["chunk_id"])
    print(result["score"])
    print(result["content"])
```

Each search result includes the original chunk fields and a similarity score.

## Limitations

- The current implementation performs dense vector retrieval using cosine similarity.
- Retrieval quality depends on document quality, chunking, and the embedding model.
- The current saved-embedding validation checks chunk identifiers and model name. Changes to chunk content with unchanged identifiers may require forced regeneration.

Hybrid retrieval, reranking, and more scalable vector databases can be considered in future development.
