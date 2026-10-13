"""Unit tests for LLM client and TokenUsage tracking."""

import pytest
from src.llm_client import TokenUsage


def test_token_usage_accumulation():
    usage = TokenUsage()
    assert usage.calls == 0
    assert usage.total_tokens == 0
    assert usage.max_prompt == 0

    usage.add(p_tokens=100, c_tokens=25)
    assert usage.calls == 1
    assert usage.prompt_tokens == 100
    assert usage.completion_tokens == 25
    assert usage.total_tokens == 125
    assert usage.max_prompt == 100

    usage.add(p_tokens=150, c_tokens=50)
    assert usage.calls == 2
    assert usage.prompt_tokens == 250
    assert usage.completion_tokens == 75
    assert usage.total_tokens == 325
    assert usage.max_prompt == 150

    d = usage.to_dict()
    assert d["calls"] == 2
    assert d["total_tokens"] == 325
    assert d["max_prompt"] == 150
