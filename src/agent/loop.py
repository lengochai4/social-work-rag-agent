"""
The ReAct loop: Reason + Act, step by step for CTXH Social Work Agent.
Uses OpenAI/Groq Native Tool Calling to handle function execution safely.
Enforces MAX_STEPS = 10 and Action & Verify constraints (W6 requirement).
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Callable
from dotenv import load_dotenv
from rich import print

from src.llm_client import call_llm, TokenUsage
from src.schemas import RegisterActivityArgs, GetStatusArgs
from config import PROJECT_ROOT

MAX_STEPS = 10

PROMPT_FILE = PROJECT_ROOT / "prompts" / "agent_system.txt"
if PROMPT_FILE.exists():
    SYSTEM_PROMPT = PROMPT_FILE.read_text(encoding="utf-8").strip()
else:
    SYSTEM_PROMPT = """You are an AI assistant for CTXH (Social Work) management at HCMUTE.
Your job is to answer queries, search regulations, and register activities for students.

CRITICAL RULE (Action & Verify):
If you call 'register_activity', you MUST call 'get_status' in the next step to verify the registered data before giving the final answer to the user."""

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_policy",
            "description": "Look up CTXH regulations and guidelines from documents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The policy search query"},
                    "doc_id": {
                        "type": "string", 
                        "description": "Optional document filter ID (e.g., 'CTXH_001' for 2013 regulation, 'CTXH_002' for 2024 student handbook)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "register_activity",
            "description": "Register a CTXH activity for a student (mutates state / side effect).",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "Student ID"},
                    "activity_code": {"type": "string", "description": "Activity code"},
                    "points": {"type": "integer", "description": "Activity points to award"},
                    "semester": {"type": "string", "description": "Semester code (e.g., HK1_2025_2026)"}
                },
                "required": ["student_id", "activity_code", "points"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_status",
            "description": "Check registered activities and total accumulated points for a student (read/verify).",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "Student ID"},
                    "semester": {"type": "string", "description": "Semester code (optional)"}
                },
                "required": ["student_id"]
            }
        }
    }
]


@dataclass
class AgentResult:
    question: str
    final_answer: str
    steps: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    usage: Dict[str, Any]
    verified: bool = False


def react_agent(
    question: str, 
    tool_executor_map: Dict[str, Callable], 
    max_steps: int = MAX_STEPS,
    verbose: bool = True
) -> AgentResult:
    """Run ReAct loop: Thought / Native Tool Call / Observation."""
    usage_tracker = TokenUsage()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    has_registered = False
    has_verified = False
    trace_steps = []
    recorded_tool_calls = []

    for step in range(1, max_steps + 1):
        response = call_llm(
            messages=messages, 
            tools=TOOLS_SCHEMA, 
            tracker=usage_tracker
        )
        response_message = response.choices[0].message

        if verbose:
            print(f"\n[bold cyan]--- Bước {step} ---[/bold cyan]")

        # 1. Neu LLM goi tool
        if response_message.tool_calls:
            messages.append(response_message)

            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_call_id = getattr(tool_call, "id", f"call_{step}")
                raw_args = tool_call.function.arguments

                try:
                    kwargs = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except Exception as e:
                    observation = f"Error: Argument parse failed: {e}"
                    kwargs = {}
                else:
                    if tool_name in tool_executor_map:
                        try:
                            # Chạy tool và bắt ngoại lệ an toàn, trả chuỗi 'Error: ...'
                            observation = str(tool_executor_map[tool_name](**kwargs))
                        except Exception as e:
                            observation = f"Error: executing {tool_name}: {e}"
                    else:
                        observation = f"Error: unknown tool '{tool_name}'"

                # Ghi nhận trạng thái kiểm định Side-Effect
                if tool_name == "register_activity":
                    has_registered = True
                elif tool_name == "get_status" and has_registered:
                    has_verified = True

                tool_record = {
                    "step": step,
                    "name": tool_name,
                    "args": kwargs,
                    "observation": observation
                }
                recorded_tool_calls.append(tool_record)
                trace_steps.append(tool_record)

                if verbose:
                    print(f"[yellow]Gọi Tool:[/yellow] {tool_name}({kwargs})")
                    print(f"[green]Kết quả:[/green] {observation[:200]}...")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": tool_name,
                    "content": str(observation)
                })

        # 2. Neu LLM tra ve Final Answer
        else:
            content = response_message.content or ""
            if verbose:
                print(f"[bold green]Assistant:[/bold green] {content}")

            # Ràng buộc Action & Verify
            if has_registered and not has_verified:
                messages.append(response_message)
                messages.append({
                    "role": "user",
                    "content": "SYSTEM CONSTRAINT: You registered an activity but HAVE NOT verified status with 'get_status'. "
                               "You MUST call 'get_status' to verify before giving the final response."
                })
                continue

            return AgentResult(
                question=question,
                final_answer=content,
                steps=trace_steps,
                tool_calls=recorded_tool_calls,
                usage=usage_tracker.to_dict(),
                verified=has_verified if has_registered else True
            )

    return AgentResult(
        question=question,
        final_answer="(Dừng: Vượt quá số bước tối đa MAX_STEPS)",
        steps=trace_steps,
        tool_calls=recorded_tool_calls,
        usage=usage_tracker.to_dict(),
        verified=has_verified
    )