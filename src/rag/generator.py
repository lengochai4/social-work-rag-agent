"""
RAG Generator Module.
Generates grounded answers based on retrieved context using call_llm.
"""

from src.rag.prompt import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.llm_client import call_llm


class LLMGenerator:
    def __init__(self, model: str | None = None):
        self.model = model

    def generate(self, question: str, context: str) -> str:
        prompt = USER_PROMPT_TEMPLATE.format(
            question=question,
            context=context,
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        try:
            response = call_llm(messages=messages, temperature=0.1)
            if response and response.choices:
                return response.choices[0].message.content or ""
        except Exception as e:
            print(f"[Generator Warning] Fallback generation due to: {e}")

        # Grounded fallback summary directly from context if LLM unavailable
        if context.strip():
            lines = [l.strip() for l in context.splitlines() if l.strip() and not l.startswith("[Nguồn")]
            preview = " ".join(lines[:3]) if lines else "Đã tìm thấy tài liệu phù hợp."
            return f"Căn cứ theo quy định của nhà trường: {preview}"
        return "Tôi chưa tìm thấy đủ căn cứ trong tài liệu hiện có để trả lời câu hỏi này."
