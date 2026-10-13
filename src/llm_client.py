"""
Safe LLM API Client with Exponential Backoff + Jitter and Token Usage tracking.
Complies with W2 requirements (retry/timeout, error logging).
"""

from dataclasses import dataclass, field
import time
import random
import os
import sys
import logging
from typing import List, Dict, Any, Optional
from groq import Groq
from config import LLM_BASE_URL, LLM_MODEL, GROQ_API_KEY, LLM_TIMEOUT, LLM_MAX_RETRIES, LLM_BASE_DELAY, LLM_MAX_DELAY

logger = logging.getLogger("llm_client")


@dataclass
class TokenUsage:
    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    max_prompt: int = 0

    def add(self, p_tokens: int, c_tokens: int):
        self.calls += 1
        self.prompt_tokens += p_tokens
        self.completion_tokens += c_tokens
        self.total_tokens += (p_tokens + c_tokens)
        self.max_prompt = max(self.max_prompt, p_tokens)

    def to_dict(self) -> dict:
        return {
            "calls": self.calls,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "max_prompt": self.max_prompt,
        }


# Global usage tracking for current execution
current_session_usage = TokenUsage()


class MockMessage:
    def __init__(self, content: str, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []


class MockChoice:
    def __init__(self, message):
        self.message = message


class MockUsage:
    def __init__(self, prompt_tokens: int, completion_tokens: int):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = prompt_tokens + completion_tokens


class MockResponse:
    def __init__(self, content: str, prompt_tokens: int = 150, completion_tokens: int = 50, tool_calls=None):
        self.choices = [MockChoice(MockMessage(content, tool_calls))]
        self.usage = MockUsage(prompt_tokens, completion_tokens)


def get_groq_client() -> Optional[Groq]:
    api_key = os.getenv("GROQ_API_KEY") or GROQ_API_KEY
    if not api_key:
        return None
    try:
        return Groq(
            api_key=api_key,
            base_url=LLM_BASE_URL if LLM_BASE_URL else None,
            timeout=float(LLM_TIMEOUT),
        )
    except Exception as exc:
        logger.warning(f"Failed to initialize Groq client: {exc}")
        return None


def call_llm(
    messages: List[Dict[str, str]], 
    tools: Optional[List[Dict[str, Any]]] = None,
    temperature: float = 0.0,
    model: str = LLM_MODEL,
    tracker: Optional[TokenUsage] = None
) -> Any:
    """
    Safe LLM API call with Exponential Backoff + Jitter and Usage tracking.
    Falls back gracefully if API key is not configured.
    """
    client = get_groq_client()

    # If no valid API key, return deterministic mock response for cold-start demo/eval
    if not client:
        user_content = next((m.get("content", "") for m in reversed(messages) if m.get("role") == "user"), "")
        est_prompt_tokens = max(10, len(str(messages)) // 4)
        est_completion_tokens = 45
        
        # Check if caller requested tools and question mentions registration
        mock_tool_calls = []
        mock_text = f"Theo quy định về Công tác xã hội (CTXH): {user_content}"
        
        resp = MockResponse(
            content=mock_text,
            prompt_tokens=est_prompt_tokens,
            completion_tokens=est_completion_tokens,
            tool_calls=mock_tool_calls
        )
        if tracker:
            tracker.add(est_prompt_tokens, est_completion_tokens)
        current_session_usage.add(est_prompt_tokens, est_completion_tokens)
        return resp

    retries = 0
    while retries <= LLM_MAX_RETRIES:
        try:
            kwargs: Dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = client.chat.completions.create(**kwargs)

            # Record token usage
            if hasattr(response, "usage") and response.usage:
                p_tok = getattr(response.usage, "prompt_tokens", 0)
                c_tok = getattr(response.usage, "completion_tokens", 0)
                if tracker:
                    tracker.add(p_tok, c_tok)
                current_session_usage.add(p_tok, c_tok)

            return response

        except Exception as e:
            err_name = e.__class__.__name__
            is_transient = "RateLimit" in err_name or "Connection" in err_name or "Timeout" in err_name
            retries += 1
            if retries > LLM_MAX_RETRIES or not is_transient:
                logger.error(f"[LLM ERROR] Exception after {retries-1} retries: {e}")
                # Fallback to safe response rather than crashing execution
                est_p = max(10, len(str(messages)) // 4)
                est_c = 30
                if tracker:
                    tracker.add(est_p, est_c)
                return MockResponse(
                    content="Tôi chưa tìm thấy đủ căn cứ trong tài liệu hiện có để trả lời câu hỏi này.",
                    prompt_tokens=est_p,
                    completion_tokens=est_c
                )

            delay = min(LLM_MAX_DELAY, LLM_BASE_DELAY * (2 ** (retries - 1)))
            jitter = random.uniform(0, 0.1 * delay)
            total_delay = delay + jitter
            logger.warning(f"[LLM RETRY] {err_name}. Retrying {retries}/{LLM_MAX_RETRIES} after {total_delay:.2f}s...")
            time.sleep(total_delay)