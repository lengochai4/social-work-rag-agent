"""tests/test_mcp.py: Consolidated test suite for CTXH MCP Server.
Covers:
1. Dynamic Tool Discovery (get_status, register_activity)
2. State Mutation & Verification loop (Side-effect -> Read/Verify)
3. Clean stdout stream purity check (Strictly JSON-RPC on stdout, logs on stderr)
4. Independent Second Client Interoperability
"""

import sys
import json
import asyncio
import subprocess
from pathlib import Path
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from src.mcp.second_client import run_second_client


async def _run_mcp_full_workflow():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.mcp.server"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # 1. Dynamic Discovery
            tools_resp = await session.list_tools()
            tool_names = [t.name for t in tools_resp.tools]
            assert "get_status" in tool_names, "Missing 'get_status' tool"
            assert "register_activity" in tool_names, "Missing 'register_activity' tool"

            # 2. Read initial profile
            test_id = "24110089"
            read_res = await session.call_tool(
                "get_status",
                {"student_id": test_id, "semester": "HK1_2025_2026"}
            )
            data_init = json.loads(read_res.content[0].text)
            init_pts = data_init.get("semester_points", 0)

            # 3. Action (Mutation)
            reg_res = await session.call_tool(
                "register_activity",
                {
                    "student_id": test_id,
                    "activity_code": "CTXH_HIEN_MAU_TEST",
                    "points": 5,
                    "semester": "HK1_2025_2026"
                }
            )
            assert "success" in reg_res.content[0].text.lower()

            # 4. Verify step
            verify_res = await session.call_tool(
                "get_status",
                {"student_id": test_id, "semester": "HK1_2025_2026"}
            )
            data_verified = json.loads(verify_res.content[0].text)
            assert data_verified["semester_points"] == init_pts + 5


def test_mcp_server_workflow():
    """Test full MCP handshake, tool discovery, mutation, and verification."""
    asyncio.run(_run_mcp_full_workflow())


def test_mcp_stdout_purity():
    """Ensure stdout contains pure JSON-RPC without contaminated log strings."""
    server_cmd = [sys.executable, "-m", "src.mcp.server"]

    process = subprocess.Popen(
        server_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "purity-checker", "version": "1.0"}
        }
    }

    try:
        stdout_data, stderr_data = process.communicate(
            input=json.dumps(init_payload) + "\n",
            timeout=5
        )
    except subprocess.TimeoutExpired:
        process.kill()
        stdout_data, stderr_data = process.communicate()

    # Every line in stdout must be valid JSON
    for line in stdout_data.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError:
            pytest.fail(f"Stdout contaminated with non-JSON text: {line}")


def test_second_client_interoperability():
    """Verify independent second client can connect and discover tools."""
    result = asyncio.run(run_second_client("24110089"))
    assert result is not None
    assert result.get("student_id") == "24110089"
