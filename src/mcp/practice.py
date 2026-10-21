import json
from pathlib import Path
from typing import Optional
from src.schemas import ActivityRecord, StudentProfile

from config import DB_PATH

def load_db() ->dict:
    if not DB_PATH.exists():
        return {"students":{}}
    with open(DB_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return{"students":{}}

def load_student(student_id: str) -> Optional[StudentProfile]:
    db=load_db()

    students_map= db.get("student", db)
    student_data= students_map.get(student_id)
    