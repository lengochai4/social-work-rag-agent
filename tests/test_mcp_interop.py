"""Unit test for MCP Server Interoperability via second independent client (+1 bonus point)."""

import asyncio
from src.mcp.second_client import run_second_client


def test_second_client_interop():
    result = asyncio.run(run_second_client("24110089"))
    assert result is not None
    assert "student_id" in result
    assert result["student_id"] == "24110089"
    assert "total_accumulated_points" in result
