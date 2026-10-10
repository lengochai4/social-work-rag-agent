from datetime import datetime
from mcp.server.mcpserver import MCPServer
from src.mcp.db import load_student, save_student
from src.schemas import ActivityRecord
import json
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    stream=sys.stderr
)

logger= logging.getLogger("ctxh-mcp-server")

mcp=MCPServer("ctxh-mcp-server")

PASSING_POINTS_THRESHOLD = 40

@mcp.tool()
def get_status(student_id: str, semester: str="") -> str:
    """Retrieve social work records of a student for verfication.
    
    Args:
    student_id: Unique student ID.
        semester: Academic semester. If empty, returns
          all semesters.
    """

    logger.info(f"Calling get_status: student_id='{student_id}', semester: '{semester}'")

    profile= load_student(student_id)
    if not profile:
        logger.warning(f"Student not found: student_id='{student_id}'")
        return f"Error: student with ID '{student_id}' not found"

    total_all_semesters= sum(profile.accumulated_points.values())
    semester_points= (
        profile.accumulated_points.get(semester,0)
        if semester
        else total_all_semesters
    )
    is_qualified= total_all_semesters >= PASSING_POINTS_THRESHOLD

    result_data= {
        "student_id":profile.student_id,
        "full_name": profile.full_name,
        "semester_points": semester_points,
        "total_accumulated_points": total_all_semesters,
        "required_threshold": PASSING_POINTS_THRESHOLD,
        "is_qualified": is_qualified,
        "total_registered_activities": len(profile.registered_activities),
    }
    return json.dumps(result_data, ensure_ascii=False)  


@mcp.tool()
def register_activity(student_id: str, activity_code: str, points: int, semester: str="HK1_2025_2026") -> str:
    """Register social work points for a completed activity (produces side-effects).

    Args:
        student_id: Unique student ID.
        activity_code: Activity code (e.g., 'HIEN_MAU_2026',
          'XUAN_TINH_NGUYEN_2026').
        points: Social work points to award (e.g., 5, 10, 15).
        semester: Academic semester (defaults to 'HK1_2025_2026').
    """

    profile = load_student(student_id)
    if not profile:
        logger.warning(
            f"Registration failed - student not found: student_id='{student_id}'"
        )
        return f"Error: Student with ID '{student_id}' not found."

    current_semester_points = profile.accumulated_points.get(semester, 0)

    # Thêm bản ghi hoạt động mới
    new_record = ActivityRecord(
        activity_code=activity_code,
        points=points,
        semester=semester,
        registered_at=datetime.now().isoformat(),
    )
    profile.registered_activities.append(new_record)
    profile.accumulated_points[semester] = current_semester_points + points

    total_points = sum(profile.accumulated_points.values())
    is_qualified = total_points >= PASSING_POINTS_THRESHOLD

    # Ghi đè cập nhật vào cơ sở dữ liệu
    save_student(profile)
    logger.info(
        f"Successfully awarded {points} points to {student_id}. Total: {total_points}/{PASSING_POINTS_THRESHOLD}"
    )

    result = {
        "status": "success",
        "message": f"Successfully registered activity '{activity_code}'.",
        "student_id": student_id,
        "awarded_points": points,
        "semester_points": profile.accumulated_points[semester],
        "total_accumulated_points": total_points,
        "is_qualified": is_qualified,
    }
    return json.dumps(result, ensure_ascii=False)


# --- ENTRYPOINT ---
if __name__ == "__main__":
    logger.info("Starting CTXH MCP Server via stdio transport...")
    mcp.run()

   
