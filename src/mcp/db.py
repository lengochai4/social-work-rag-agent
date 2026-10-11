import json
from pathlib import Path
from typing import Optional
from src.schemas import ActivityRecord, StudentProfile

from config import DBA_PATH


def load_db() -> dict:
  if not DBA_PATH.exists():
    return {"students": {}}
  with open(DBA_PATH, "r", encoding="utf-8") as f:
    try:
      return json.load(f)
    except json.JSONDecodeError:
      return {"students": {}}


def load_student(student_id: str) -> Optional[StudentProfile]:
  db = load_db()

  students_map = db.get("students", db)
  student_data = students_map.get(student_id)

  if not student_data:
    return None

  # Chuyển đổi activities 
  activities = []
  for act in student_data.get("registered_activities", []):
    points = act.get("points")

    activities.append(
        ActivityRecord(
            activity_code=act.get("activity_code", ""),
            points=points,
            semester=act.get("semester", "HK1_2025_2026"),
            registered_at=act.get("registered_at", ""),
        )
    )

  accumulated_points = student_data.get("accumulated_points")

  return StudentProfile(
      student_id=student_data.get("student_id", student_id),
      full_name=student_data.get("full_name", ""),
      accumulated_points=accumulated_points,
      registered_activities=activities,
  )


def save_student(profile: StudentProfile) -> None:
  db = load_db()
  if "students" not in db:
    db = {"students": db}

  db["students"][profile.student_id] = {
    "student_id": profile.student_id,
    "full_name": profile.full_name,
    "accumulated_points": profile.accumulated_points,
    "registered_activities": [
      {
        "activity_code": act.activity_code,
        "points": act.points,
        "semester": act.semester,
        "registered_at": act.registered_at,
      }
      for act in profile.registered_activities
    ],
  }

  DBA_PATH.parent.mkdir(parents=True, exist_ok=True)
  with open(DBA_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False) 