"""
Project Configuration

Defines the project root, data paths, supported file types,
embedding model, and document chunking parameters.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

#PROJECT ROOT 
PROJECT_ROOT = Path(__file__).resolve().parent

#DATA PATHS
DATA_PATH = PROJECT_ROOT / "data"
DB_PATH = PROJECT_ROOT / "data" / "db" / "ctxh_db.json"
RESULTS_PATH = PROJECT_ROOT / "results"


# Directory containing cleaned and preprocessed documents.
PROCESSED_DATA_PATH = DATA_PATH / "processed"
# Directory containing raw, unprocessed documents.
RAW_DATA_PATH = DATA_PATH / "raw"
# Path to the JSON file containing generated document chunks.
OUTPUT_PATH = DATA_PATH / "ctxh_chunks.json"
# Path to the JSON file containing document embedding vectors.
EMBEDDINGS_PATH = DATA_PATH / "ctxh_embeddings.json"
# Test set 
TESTSET_PATH = PROJECT_ROOT / "tests" / "testset.jsonl"

OUTPUT_TEST_RAG_PATH = RESULTS_PATH / "retrieval_results.json" 
#SOURCES FILE SETTINGS 
SUPPORTED_FILE_TYPES = [".md", ".txt"]

#EMBEDING SETTINGS
EMBEDDING_MODEL_NAME = str("intfloat/multilingual-e5-base")
#EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


# LLM & API CLIENT SETTINGS 
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", None)
# LLM_MODEL = os.getenv("LLM_MODEL", "qwen/qwen3.8-27b")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")
# LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Retry & Timeout Settings
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "30.0"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "5"))
LLM_BASE_DELAY = float(os.getenv("LLM_BASE_DELAY", "1.0"))
LLM_MAX_DELAY = float(os.getenv("LLM_MAX_DELAY", "30.0"))