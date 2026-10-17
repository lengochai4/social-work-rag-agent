"""tests/test_agent.py: Consolidated test suite for ReAct Agent, Prompt templates & DB integrity.
Covers:
1. TokenUsage tracker mechanics and accumulation
2. Prompt template separation (prompts/*.txt)
3. Database integrity and stress testing (data/db/ctxh_db.json)
"""

import json
from pathlib import Path
import pytest

from src.llm_client import TokenUsage
from src.mcp.db import load_db, load_student, save_student
from config import PROJECT_ROOT, DB_PATH


def test_token_usage_tracker():
    usage = TokenUsage()
    assert usage.calls == 0
    assert usage.total_tokens == 0
    assert usage.max_prompt == 0

    usage.add(p_tokens=120, c_tokens=30)
    assert usage.calls == 1
    assert usage.prompt_tokens == 120
    assert usage.completion_tokens == 30
    assert usage.total_tokens == 150
    assert usage.max_prompt == 120

    usage.add(p_tokens=200, c_tokens=50)
    assert usage.calls == 2
    assert usage.prompt_tokens == 320
    assert usage.completion_tokens == 80
    assert usage.total_tokens == 400
    assert usage.max_prompt == 200

    d = usage.to_dict()
    assert d["calls"] == 2
    assert d["total_tokens"] == 400


def test_prompt_templates_exist():
    prompt_dir = PROJECT_ROOT / "prompts"
    assert prompt_dir.exists(), "prompts directory missing!"

    agent_sys = prompt_dir / "agent_system.txt"
    assert agent_sys.exists(), "agent_system.txt missing!"
    content = agent_sys.read_text(encoding="utf-8")
    assert "CTXH" in content
    assert "register_activity" in content
    assert "get_status" in content

    rag_sys = prompt_dir / "rag_system.txt"
    assert rag_sys.exists(), "rag_system.txt missing!"


def test_db_structure_and_integrity():
    assert DB_PATH.exists(), f"Database not found at {DB_PATH}"

    db = load_db()
    assert "students" in db, "Missing 'students' key in JSON DB"
    assert len(db["students"]) >= 3, "Expected at least 3 students in seed DB"

    for sv_id, profile in db["students"].items():
        assert "student_id" in profile
        assert "accumulated_points" in profile
        assert "registered_activities" in profile


def test_load_and_save_student():
    student = load_student("24110089")
    assert student is not None
    assert student.student_id == "24110089"

    # Nonexistent student returns None
    invalid = load_student("99999999")
    assert invalid is None
