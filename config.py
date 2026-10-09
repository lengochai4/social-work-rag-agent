
"""Shared configuration for the Social Work RAG Agent."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent

load_dotenv(ROOT_DIR / ".env")

DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CHUNKS_FILE = DATA_DIR / "ctxh_chunks.json"
DATABASE_FILE = DATA_DIR / "db" / "ctxh_db.json"

LOG_DIR = ROOT_DIR / "logs"
PROMPT_FILE = ROOT_DIR / "prompts" / "agent_system.txt"
TESTSET_FILE = ROOT_DIR / "tests" / "testset.jsonl"

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
LLM_BASE_URL = os.getenv(
    "LLM_BASE_URL",
    "https://api.groq.com/openai/v1",
)
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "30"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "5"))

MAX_STEPS = int(os.getenv("MAX_STEPS", "6"))