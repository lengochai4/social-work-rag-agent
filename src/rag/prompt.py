"""
RAG Prompt Templates loader.
Loads prompts from external text templates in prompts/ directory (W2 requirement).
"""

from pathlib import Path
from config import PROJECT_ROOT

PROMPTS_DIR = PROJECT_ROOT / "prompts"

def load_prompt_file(filename: str, default_text: str) -> str:
    path = PROMPTS_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return default_text.strip()

DEFAULT_SYSTEM_PROMPT = """You are an AI assistant that helps university students retrieve
and understand Social Work (CTXH) regulations and related documents at HCMUTE.

Follow these rules:
1. Answer only using the information provided in the CONTEXT.
2. Do not fabricate regulations, deadlines, scores, eligibility requirements, or citations.
3. If the CONTEXT does not contain sufficient information to answer the question, clearly state that there is insufficient evidence in the available documents.
4. Respond in Vietnamese using clear, direct, and easy-to-understand language.
5. Whenever possible, identify the source document by its title or document ID.
6. Distinguish explicitly stated facts from any interpretation.
7. Do not claim that a policy or requirement exists unless it is supported by the provided CONTEXT."""

DEFAULT_USER_PROMPT_TEMPLATE = """QUESTION:
{question}

RETRIEVED CONTEXT:
{context}

Answer the question using only the information provided in the CONTEXT.
If the CONTEXT does not contain sufficient evidence to answer the question, explicitly state that the available documents do not provide enough information.
Do not invent facts or rely on unsupported assumptions.
Whenever possible, identify the relevant source document."""

SYSTEM_PROMPT = load_prompt_file("rag_system.txt", DEFAULT_SYSTEM_PROMPT)
USER_PROMPT_TEMPLATE = load_prompt_file("rag_user.txt", DEFAULT_USER_PROMPT_TEMPLATE)
