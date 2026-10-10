"""
Project Configuration

Defines the project root, data paths, supported file types,
embedding model, and document chunking parameters.
"""

from pathlib import Path

#PROJECT ROOT 
PROJECT_ROOT = Path(__file__).resolve().parent

#DATA PATHS
DATA_PATH = PROJECT_ROOT / "data"
DB_PATH = DB_PATH = PROJECT_ROOT / "data" / "db" / "ctxh_db.json"


# Directory containing cleaned and preprocessed documents.
PROCESSED_DATA_PATH = DATA_PATH / "processed"
# Directory containing raw, unprocessed documents.
RAW_DATA_PATH = DATA_PATH / "raw"
# Path to the JSON file containing generated document chunks.
OUTPUT_PATH = DATA_PATH / "ctxh_chunks.json"
# Path to the JSON file containing document embedding vectors.
EMBEDDINGS_PATH = DATA_PATH / "ctxh_embeddings.json"


#SOURCES FILE SETTINGS 
SUPPORTED_FILE_TYPES = [".md", ".txt"]

#EMBEDING SETTINGS
EMBEDDING_MODEL_NAME = str("intfloat/multilingual-e5-base")
#EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200