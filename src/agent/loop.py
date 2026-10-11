"""
The ReAct loop: Reason + Act, step by step for CTXH Social Work Agent.
Uses OpenAI/Groq Native Tool Calling to handle function execution safely.

Enforces MAX_STEPS = 10 and Action & Verify constraints.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from rich import print
from typing import Dict, Any, List
from src.llm_client import call_llm

MAX_STEPS = 10

# ---------------------------------------------------------------------------
# Step 1: System Prompt & Tools Schema
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an AI assistant for CTXH (Social Work) management.
Your job is to answer queries, search regulations, and register activities for students.

CRITICAL RULE (Action & Verify):
If you call 'register_activity', you MUST call 'get_status' in the next step to verify the registered data before giving the final answer to the user.
"""

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_policy",
            "description": "Look up CTXH regulations and guidelines from documents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The policy search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "register_activity",
            "description": "Register a CTXH activity for a student.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "Student ID"},
                    "activity_code": {"type": "string", "description": "Activity code"},
                    "points": {"type": "integer", "description": "Activity points"},
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
            "description": "Check registered activities and total accumulated points for a student.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "Student ID"},
                    "semester": {"type": "string", "description": "Semester code"}
                },
                "required": ["student_id"]
            }
        }
    }
]

# ---------------------------------------------------------------------------
# Step 2: ReAct Agent Loop
# ---------------------------------------------------------------------------


def react_agent(question: str, tool_executor_map: dict, max_steps=MAX_STEPS) -> str:
    """Run Thought / Native Tool Call / Observation cycle."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    has_registered = False
    has_verified = False

    for step in range(1, max_steps + 1):
        # Pass tools schema so Groq API knows tools are supported
        response = call_llm(messages=messages, tools=TOOLS_SCHEMA)
        response_message = response.choices[0].message

        print(f"\n--- step {step} ---")

        # 1. If LLM wants to call a tool
        if response_message.tool_calls:
            messages.append(response_message)  # Save assistant tool call turn

            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_call_id = tool_call.id
                raw_args = tool_call.function.arguments

                try:
                    kwargs = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except Exception as e:
                    observation = f"Error parsing arguments: {e}"
                else:
                    if tool_name in tool_executor_map:
                        try:
                            observation = str(tool_executor_map[tool_name](**kwargs))
                        except Exception as e:
                            observation = f"Error executing {tool_name}: {e}"
                    else:
                        observation = f"Error: unknown tool '{tool_name}'"

                # Update verification flags
                if tool_name == "register_activity":
                    has_registered = True
                elif tool_name == "get_status" and has_registered:
                    has_verified = True

                print(f"Tool Call: {tool_name}({kwargs})")
                print(f"Observation: {observation}")

                # Send observation back to LLM
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": tool_name,
                    "content": str(observation)
                })

        # 2. If LLM outputs text (Final Answer)
        else:
            content = response_message.content or ""
            print(f"Assistant: {content}")

            # Enforce Action & Verify constraint
            if has_registered and not has_verified:
                messages.append(response_message)
                messages.append({
                    "role": "user",
                    "content": "SYSTEM ERROR: You registered an activity but HAVE NOT checked status with 'get_status'. "
                               "You MUST call 'get_status' to verify before giving the final answer."
                })
                continue

            return content

    return "(stopped: too many steps)"

def save_trace_log(
        question: str,
        final_answer: str,
        usage_stats: Dict[str, Any],
        traces: List[Dict[str, Any]],
        is_verified: bool,
        log_filename: str = None
) -> str:
    """ Export trace and detailed USAGE stats to the logs/*.jsonl"""
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)

    if not log_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"agent_eval_{timestamp}.jsonl"

    filepath = os.path.join(logs_dir, log_filename)

    usage_payload = {
        "calls": usage_stats.get("calls", 0),
        "prompt_tokens": usage_stats.get("prompt_tokens", 0),
        "completion_tokens": usage_stats.get("completion_tokens", 0),
        "total_tokens": usage_stats.get("total_tokens", 0),
    }

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "final_answer": final_answer,
        "is_verified": is_verified,
        "usage": usage_payload,
        "traces": traces
    }

    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    return filepath

def main():
    load_dotenv()

    dummy_executors = {
        "search_policy": lambda query: f"Policy lookup result for '{query}': Registration guidelines found.",
        "register_activity": lambda student_id, activity_code, points, semester="HK1_2025_2026": f"Successfully registered {activity_code} ({points} pts) for student {student_id} in {semester}.",
        "get_status": lambda student_id, semester=None: f"Status for {student_id}: Total accumulated CTXH points = 5 in {semester or 'all semesters'}."
    }

    question = "Please register activity ACT01 with 5 points for student SV01 in HK1_2025_2026 and verify the updated status."

    print(f"Question: {question}")
    final_answer = react_agent(question, dummy_executors)
    print(f"\nFinal Answer: {final_answer}")


if __name__ == "__main__":
    main()