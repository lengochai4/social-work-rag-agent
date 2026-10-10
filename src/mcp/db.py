from dataclasses import asdict
import json
import os
from pathlib import Path
import tempfile
from src.schemas import ActivityRecord, StudentProfile
from config import DB_PATH


def load_student(student_id: str) -> StudentProfile:
    """Đọc dữ liệu sinh viên và trả về StudentProfile."""
    if not DB_PATH.exists():
        return StudentProfile(
            student_id=student_id, full_name=f"Sinh viên {student_id}"
        )

    with open(DB_PATH, "r", encoding="utf-8") as f:
        raw_db = json.load(f).get("students", {})

    if student_id not in raw_db:
        return StudentProfile(
            student_id=student_id, full_name=f"Sinh viên {student_id}"
        )

    data = raw_db[student_id]
    activities = [
        ActivityRecord(
            activity_code=act["activity_code"],
            hours=act["hours"],
            days=act["days"],
            semester=act["semester"],
            registered_at=act.get("registered_at", ""),
        )
        for act in data.get("registered_activities", [])
    ]

    return StudentProfile(
        student_id=data["student_id"],
        full_name=data["full_name"],
        registered_activities=activities,
        accumulated_days=data.get("accumulated_days", {}),
    )


def save_student(profile: StudentProfile) -> None:
    """Ghi dữ liệu StudentProfile an toàn bằng Atomic Write."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    raw_db = {"students": {}}
    if DB_PATH.exists():
        with open(DB_PATH, "r", encoding="utf-8") as f:
            raw_db = json.load(f)

    raw_db.setdefault("students", {})[profile.student_id] = asdict(profile)

    with tempfile.NamedTemporaryFile(
        "w", dir=DB_PATH.parent, delete=False, encoding="utf-8"
    ) as tf:
        json.dump(raw_db, tf, indent=2, ensure_ascii=False)
        temp_name = tf.name

    os.replace(temp_name, DB_PATH)