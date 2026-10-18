# Data Directory

## Overview

The `data/` directory stores the source documents and generated datasets used by the Social Work RAG Agent. It separates original documents from processed documents and generated chunk data.

## Directory Structure

```text
data/
├── raw/
├── processed/
├── ctxh_chunks.json
└── ctxh_embeddings.json
```

- `raw/`: Stores original source documents before preprocessing.
- `processed/`: Stores cleaned and normalized documents ready for chunking.
- `ctxh_chunks.json`: Generated dataset containing document chunks and their metadata.
- `ctxh_embeddings.json`: Generated embedding vectors associated with the document chunks.

The JSON files are generated artifacts and do not need to be committed to Git if they can be recreated from the source documents.

## Workflow

1. Place source documents in `raw/`.
2. Preprocess the documents and save the results in `processed/`.
3. Run the dataset-building pipeline to split the processed documents into chunks.
4. Save the generated chunks to `ctxh_chunks.json`.
5. Run the retrieval pipeline to generate and store embeddings in `ctxh_embeddings.json`.

## Generate the Chunk Dataset

Run the following command from the project root:

```bash
uv run python -m src.data_preprocessing.build_dataset
```

The command reads the processed documents, generates chunks, and saves the resulting dataset.

## Notes

- Keep original documents separate from processed documents.
- Do not manually edit generated JSON files unless necessary for debugging.
- Ensure that source documents can legally be shared before committing them to version control.
- Generated datasets can be recreated by running the corresponding pipeline.
