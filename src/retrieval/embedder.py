""" 
Download and embed documents using a specified embedding model.
Convert documents to embeddings and save them in a JSON file.
Convert the user's documents to embeddings and save them in a JSON file.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import os
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL_NAME

class Embedder: 
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        """Initialize the Embedder with a specified model."""
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        
    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Convert a list of documents to embeddings."""
        passages = [f"passage: {text}" for text in documents]
        
        embeddings = self.model.encode(
            passages, 
            normalize_embeddings= True, 
            convert_to_numpy= True,
            show_progress_bar= True
        )
        return embeddings.tolist()
    
    def embed_query(self, query: str) -> list[float]:
        """Convert a query string to an embedding."""
        query_text = f"query: {query}"
        embedding = self.model.encode(
            query_text, 
            normalize_embeddings= True, 
            convert_to_numpy= True
        )
        return embedding.tolist()


if __name__ == "__main__":
    embedder = Embedder()
    test_vec = embedder.embed_query("Quy định CTXH")
    print(f"Embedding model: {embedder.model_name}")
    print(f"Dimension: {len(test_vec)}")
    print(f"Sample vector (first 5 elements): {test_vec[:5]}")
