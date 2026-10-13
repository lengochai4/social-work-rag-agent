import os
from dotenv import load_dotenv
from groq import Groq

from src.rag.prompt import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class LLMGenerator:
    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("LLM_MODEL")

        if not self.model:
            raise ValueError("Chưa cấu hình LLM_MODEL trong .env")

    def generate(self, question: str, context: str) -> str:
        prompt = USER_PROMPT_TEMPLATE.format(
            question=question,
            context=context,
        )

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        return response.choices[0].message.content or ""
