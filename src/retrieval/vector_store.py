
import json
from pathlib import Path

import numpy as np

from config import DATA_PATH, OUTPUT_PATH, EMBEDDINGS_PATH
from src.schemas import Document, DocumentChunk
from src.retrieval.embedder import Embedder



class VectorStore:
    def __init__(self, embedder: Embedder | None = None):
        self.embedder = embedder or Embedder()
        self.chunks: list[dict] = []
        self.embeddings: np.ndarray | None = None

    def build(self, force_rebuild: bool = False):
        """Load chunks and build or reuse their embeddings."""

        if not OUTPUT_PATH.exists():
            raise FileNotFoundError(
                f"Chunk dataset not found: {OUTPUT_PATH}. "
                "Run build_dataset.py first."
            )

        with OUTPUT_PATH.open("r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        if not self.chunks:
            raise ValueError("The chunk dataset is empty.")

        if EMBEDDINGS_PATH.exists() and not force_rebuild:
            with EMBEDDINGS_PATH.open("r", encoding="utf-8") as f:
                saved = json.load(f)

            # Reuse saved embeddings only if they match the current chunks.
            if (
                saved.get("chunk_ids")
                == [chunk["chunk_id"] for chunk in self.chunks]
                and saved.get("model_name")
                == self.embedder.model_name
            ):
                self.embeddings = np.asarray(
                    saved["embeddings"], dtype=np.float32
                )
                if (
                    self.embeddings.ndim == 2
                    and len(self.embeddings) == len(self.chunks)
                ):
                    print("Loaded saved embeddings.")
                    return
                self.embeddings = None

        # Create embeddings from chunk contents.
        texts = [chunk["content"] for chunk in self.chunks]
        vectors = self.embedder.embed_documents(texts)
        self.embeddings = np.asarray(vectors, dtype=np.float32)

        EMBEDDINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

        saved = {
            "model_name": self.embedder.model_name,
            "chunk_ids": [chunk["chunk_id"] for chunk in self.chunks],
            "embeddings": self.embeddings.tolist(),
        }

        with EMBEDDINGS_PATH.open("w", encoding="utf-8") as f:
            json.dump(saved, f, ensure_ascii=False)

        print(f"Built embeddings for {len(self.chunks)} chunks.")
        print(f"Saved embeddings to: {EMBEDDINGS_PATH}")

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Return the top-k most relevant chunks for a query."""

        if self.embeddings is None:
            raise RuntimeError("Call build() before search().")

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        query_vector = np.asarray(
            self.embedder.embed_query(query), dtype=np.float32
        )

        if query_vector.shape[0] != self.embeddings.shape[1]:
            raise ValueError("Query and document embedding dimensions differ.")

        # Embeddings are normalized, so dot product equals cosine similarity.
        scores = self.embeddings @ query_vector

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for index in top_indices:
            chunk = self.chunks[int(index)]

            results.append({
                **chunk,
                "score": float(scores[index]),
            })

        return results
    
