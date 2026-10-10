# Tests

## Overview

The `tests/` directory contains scripts for verifying the embedding and retrieval components of the Social Work RAG Agent.

These tests help identify problems before the components are integrated into the complete RAG pipeline.

## Test Modules

- `test_embedder.py`: Verifies that the embedding model can encode document text and user queries into vectors.
- `test_vector_store.py`: Verifies that the vector store can load the chunk dataset, generate or reuse embeddings, and retrieve relevant chunks.

## Run the Embedding Test

From the project root:

```bash
uv run python -m tests.test_embedder
```

This test checks that:

- The embedding model loads successfully.
- Document embeddings are generated.
- Query embeddings are generated.
- Document and query vectors have compatible dimensions.

## Run the Vector Store Test

```bash
uv run python -m tests.test_vector_store
```

This test checks that:

- The chunk dataset can be loaded.
- Embeddings can be generated or reused.
- A query returns the top-k ranked chunks.
- Each result includes its chunk identifier, similarity score, metadata, and content.

## Testing Guidelines

- Run tests from the project root to ensure imports and relative paths work correctly.
- Ensure that `data/ctxh_chunks.json` exists before running the vector store test.
- The first run may take longer because the embedding model must be downloaded and document embeddings generated.
- Review the retrieved content manually to evaluate whether the results are relevant to the query.
- Do not treat a successful execution as proof of retrieval quality; inspect the returned chunks and scores.

## Current Scope

These scripts are component-level tests. They do not yet evaluate the complete RAG pipeline or measure retrieval quality against a labeled benchmark.
