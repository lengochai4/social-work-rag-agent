""" 
Download and embed documents using a specified embedding model.
Convert documents to embeddings and save them in a JSON file.
Convert the user's documents to embeddings and save them in a JSON file.
"""

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
    
    