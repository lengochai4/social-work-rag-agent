import time
import random
import os
from typing import List, Dict, Any, Optional
from openai import OpenAI, RateLimitError, APIConnectionError, APIError
from config import LLM_PROVIDER, LLM_BASE_URL, LLM_MODEL, GROQ_API_KEY, LLM_TIMEOUT, LLM_MAX_RETRIES, LLM_BASE_DELAY, LLM_MAX_DELAY

client = OpenAI(
    api_key=GROQ_API_KEY or os.getenv("GROQ_API_KEY", "mock_key"),
    base_url=LLM_BASE_URL if LLM_BASE_URL else None,
    timeout=float(LLM_TIMEOUT)
)

def call_llm(
    messages: List[Dict[str, str]], 
    tools: Optional[List[Dict[str, Any]]] = None,
    temperature: float = 0.0
) -> Any:
    """
    A safe LLM API call function with integrated Exponential Backoff + Jitter and network error handling.
    """
    retries = 0
    while retries <= LLM_MAX_RETRIES:
        try:
            kwargs = {
                "model": LLM_MODEL,
                "messages": messages,
                "temperature": temperature,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = client.chat.completions.create(**kwargs)
            return response

        except (RateLimitError, APIConnectionError, APIError) as e:
            retries += 1
            if retries > LLM_MAX_RETRIES:
                print(f"[LLM ERROR] Exceeded the number of retry attempts ({LLM_MAX_RETRIES}). Error: {e}")
                raise e

            # Công thức Exponential Backoff với Jitter
            delay = min(LLM_MAX_DELAY, LLM_BASE_DELAY * (2 ** (retries - 1)))
            jitter = random.uniform(0, 0.1 * delay) # Add random delay to avoid bottleneck
            total_delay = delay + jitter

            print(f"[LLM RETRY] Caught a connection/RateLimit error ({e.__class__.__name__}). Trying again {retries}/{LLM_MAX_RETRIES} after {total_delay:.2f}s...")
            time.sleep(total_delay)

        except Exception as e:
            print(f"[LLM UNEXPECTED ERROR] Unknown error: {e}")
            raise e