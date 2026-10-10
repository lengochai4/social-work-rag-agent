import json
from pathlib import Path
from typing import Optional
from src.schemas import ActivityRecord, StudentProfile

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT_DIR / "data" / "db" / "ctxh_db.json"


def load_db() -> dict:
  if not DB_PATH.exists():
    return {"students": {}}
  with open(DB_PATH, "r", encoding="utf-8") as f:
    try:
      return json.load(f)
    except json.JSONDecodeError:
      return {"students": {}}


def load_student(student_id: str) -> Optional[StudentProfile]:
  db = load_db()

  # Bóc tách qua tầng "students" nếu có
  students_map = db.get("students", db)
  student_data = students_map.get(student_id)

  if not student_data:
    return None

  # Chuyển đổi activities (tự fallback nếu còn trường cũ 'days')
  activities = []
  for act in student_data.get("registered_activities", []):
    points = act.get("points")
    if points is None:
      # Quy đổi dự phòng từ ngày cũ: 1 ngày = 5 điểm
      points = int(act.get("days", 1.0) * 5)

    activities.append(
        ActivityRecord(
            activity_code=act.get("activity_code", ""),
            points=points,
            semester=act.get("semester", "HK1_2025_2026"),
            registered_at=act.get("registered_at", ""),
        )
    )

  accumulated_points = student_data.get("accumulated_points")
  if accumulated_points is None:
    # Nếu DB cũ đang dùng 'accumulated_days'
    old_days = student_data.get("accumulated_days", {})
    accumulated_points = {sem: int(days * 5) for sem, days in old_days.items()}

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

  DB_PATH.parent.mkdir(parents=True, exist_ok=True)
  with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False) 