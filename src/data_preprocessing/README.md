# Data Preprocessing

## Overview

The `data_preprocessing/` package prepares source documents for the Social Work RAG Agent. It loads processed documents, splits their content into manageable chunks, preserves relevant metadata, and exports the resulting dataset as JSON.

## Module Responsibilities

- `document_loader.py`: Loads processed documents and converts them into structured document objects.
- `chunker.py`: Splits document content into chunks while preserving Markdown tables and relevant metadata.
- `build_dataset.py`: Coordinates document loading and chunking, then saves the generated dataset to `data/ctxh_chunks.json`.
- `__init__.py`: Marks the directory as a Python package.

## Workflow

1. Load documents from `data/processed/`.
2. Normalize document text and identify Markdown tables.
3. Split text into chunks according to the configured chunk size and overlap.
4. Preserve document identifiers, chunk indices, metadata, and content types.
5. Export the chunks to `data/ctxh_chunks.json`.

Text chunks use overlap to preserve context between consecutive chunks. Markdown tables are split by rows, with table headers repeated when a table spans multiple chunks.

## Configuration

Chunking parameters are defined in the root `config.py` file.

- `CHUNK_SIZE`: Target maximum size of a text chunk.
- `CHUNK_OVERLAP`: Number of overlapping characters between consecutive text chunks.

Adjust these values based on document structure and retrieval requirements.

## Run the Pipeline

From the project root:

```bash
uv run python -m src.data_preprocessing.build_dataset
```

The command generates or overwrites `data/ctxh_chunks.json`.

## Output

Each chunk contains:

- `doc_id`: Identifier of the source document.
- `chunk_id`: Unique identifier of the chunk.
- `chunk_index`: Position of the chunk within its document.
- `content`: Text content of the chunk.
- `metadata`: Document metadata and content type.
- `embedding`: Optional embedding vector, initially set to `null`.

The generated dataset is consumed by the retrieval component.
