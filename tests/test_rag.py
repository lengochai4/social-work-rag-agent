"""Unit test for RAG prompt template loading."""

from config import PROJECT_ROOT


def test_prompts_exist():
    prompt_dir = PROJECT_ROOT / "prompts"
    assert prompt_dir.exists()
    agent_sys = prompt_dir / "agent_system.txt"
    assert agent_sys.exists()
    content = agent_sys.read_text(encoding="utf-8")
    assert "CTXH" in content
    assert "register_activity" in content
    assert "get_status" in content
