# Data Preprocessing

## Overview

The `data_preprocessing` package handles the extraction, normalization, chunking, and metadata preservation of HCMUTE Social Work (CTXH) regulatory documents. It produces the standardized corpus `data/ctxh_chunks.json`, which serves as the knowledge base for Grounded Retrieval and Hybrid Search (BM25 + Dense E5).

## Module Architecture

- **`document_loader.py`**: Reads processed Markdown (`.md`) files from `data/processed/` using `utf-8-sig` encoding and maps each document to standardized metadata (document ID, official title, decision number `224/QĐ-ĐHSPKT-CTHSSV`, version, and source URL).
- **`chunker.py`**: Normalizes whitespace and applies a sliding-window chunking strategy (`CHUNK_SIZE`, `CHUNK_OVERLAP`) to retain contextual continuity and table structures across split boundaries.
- **`build_dataset.py`**: Entrypoint script that executes the complete preprocessing pipeline and serializes the generated chunks into JSON.
- **`document_store.py`**: In-memory repository providing querying, retrieval, and CRUD interfaces for documents and chunk objects.

## Pipeline Workflow

1. **Document Ingestion**: Loads verified source regulations (`CTXH_001` - 2013 Decision 224; `CTXH_002` - 2024 Student Handbook).
2. **Text Normalization**: Cleans excessive whitespace and standardizes line breaks while preserving document hierarchies.
3. **Sliding-Window Chunking**: Splits text into chunks of target size with character overlap to ensure cross-boundary facts are not fragmented.
4. **Metadata Propagation**: Attaches document-level provenance attributes (`doc_id`, `title`, `document_number`) to every individual chunk for citation tracking.
5. **Serialization**: Exports the structured chunk collection to `data/ctxh_chunks.json`.

## Configuration Parameters

Parameters are defined centrally in `config.py`:

| Parameter | Default Value | Description |
| :--- | :--- | :--- |
| `CHUNK_SIZE` | `1000` | Target character count per text chunk. |
| `CHUNK_OVERLAP` | `200` | Overlapping character count between consecutive chunks. |
| `PROCESSED_DATA_PATH` | `data/processed` | Directory containing cleaned Markdown documents. |
| `OUTPUT_PATH` | `data/ctxh_chunks.json` | Target destination for serialized chunk dataset. |

## Execution

Run the preprocessing pipeline from the repository root:

```bash
# Using uv
uv run python -m src.data_preprocessing.build_dataset

# Using standard Python
python -m src.data_preprocessing.build_dataset
```

## Output Schema

Each item in `data/ctxh_chunks.json` conforms to the `DocumentChunk` dataclass defined in `src/schemas.py`:

```json
{
  "doc_id": "CTXH_001",
  "chunk_id": "CTXH_001_0",
  "chunk_index": 0,
  "content": "QUY ĐỊNH\nTổ chức thực hiện chương trình Công tác xã hội...",
  "metadata": {
    "document_type": "regulation",
    "document_number": "224/QĐ-ĐHSPKT-CTHSSV",
    "publication_year": 2013,
    "language": "Vietnamese"
  },
  "embedding": null
}
```

- **`doc_id`**: Source document identifier, utilized for metadata-filtered retrieval.
- **`chunk_id`**: Globally unique chunk identifier, cited in verified RAG responses.
- **`content`**: Text payload indexed by BM25 and vectorized by the Dense Embedder.
- **`embedding`**: Placeholder initialized to `null`, computed downstream by `src/retrieval/embedder.py`.

