from datetime import datetime
import json
import logging
import sys

from mcp.server import MCPServer
from src.mcp.db import load_student, save_student
from src.schemas import ActivityRecord

mcp = MCPServer("ctxh-mcp-server")
# 1. LOGGING CONFIGURATION: Route all logs to sys.stderr to keep stdout clean
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    stream=sys.stderr,  # Strictly avoid stdout
)
logger = logging.getLogger("mcp-ctxh-server")

# --- TOOL 1: READ / VERIFICATION TOOL ---
@mcp.tool()
def get_status(student_id: str, semester: str = "") -> str:
    """Retrieve social work records of a student for verification.

    Args:
        student_id: Unique student ID (e.g., '24110089').
        semester: Academic semester (e.g., 'HK1_2025_2026'). Leave empty to
          retrieve all records.
    """
    logger.info(
        f"Calling get_status: student_id='{student_id}', semester='{semester}'"
    )

    profile = load_student(student_id)
    if not profile:
        logger.warning(f"Student not found: student_id='{student_id}'")
        return f"Error: Student with ID '{student_id}' not found."

    accumulated = (
        profile.accumulated_days.get(semester, 0.0)
        if semester
        else profile.accumulated_days
    )

    result_data = {
        "student_id": profile.student_id,
        "full_name": profile.full_name,
        "accumulated_days": accumulated,
        "total_registered_activities": len(profile.registered_activities),
    }
    return json.dumps(result_data, ensure_ascii=False)


# --- TOOL 2: WRITE / SIDE-EFFECT TOOL ---
@mcp.tool()
def register_activity(
    student_id: str,
    activity_code: str,
    hours: float,
    semester: str = "HK1_2025_2026",
) -> str:
    """Register a new social work activity for a student (produces side-effects).

    Args:
        student_id: Unique student ID.
        activity_code: Activity identifier.
        hours: Number of participation hours.
        semester: Academic semester (defaults to 'HK1_2025_2026').
    """
    logger.info(
        f"Calling register_activity: student_id='{student_id}', activity='{activity_code}', hours={hours}"
    )

    profile = load_student(student_id)
    if not profile:
        logger.warning(
            f"Registration failed - student not found: student_id='{student_id}'"
        )
        return f"Error: Student with ID '{student_id}' not found."

    # Standard conversion: 8 hours = 1 social work day
    added_days = round(hours / 8.0, 2)
    current_days = profile.accumulated_days.get(semester, 0.0)

    # Append new record and update state
    new_record = ActivityRecord(
        activity_code=activity_code,
        hours=hours,
        days=added_days,
        semester=semester,
        registered_at=datetime.now().isoformat(),
    )
    profile.registered_activities.append(new_record)
    profile.accumulated_days[semester] = round(current_days + added_days, 2)

    # Persist updated profile to storage
    save_student(profile)
    logger.info(
        f"Successfully registered activity: student_id='{student_id}', activity='{activity_code}', added_days={added_days}"
    )

    result = {
        "status": "success",
        "message": f"Successfully registered activity '{activity_code}'.",
        "student_id": student_id,
        "added_days": added_days,
        "total_days_in_semester": profile.accumulated_days[semester],
    }
    return json.dumps(result, ensure_ascii=False)

if __name__ == "__main__":
    logger.info("Starting CTXH MCP Server via stdio transport...")
    mcp.run()