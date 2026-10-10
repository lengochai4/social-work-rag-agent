from datetime import datetime
from src.mcp.db import load_student, save_student
from src.schemas import ActivityRecord, StudentProfile


def test_db_operations():
    print("=" * 60)
    print("🚀 STARTING MOCK CTXH DATABASE TEST")
    print("=" * 60)

    # 1. Select student profile for testing (Hai - 24110089)
    student_id = "24110089"
    semester = "HK1_2025_2026"

    # Load initial state
    profile = load_student(student_id)
    initial_days = profile.accumulated_days.get(semester, 0.0)
    initial_act_count = len(profile.registered_activities)

    print(f"\n[1] INITIAL STATE:")
    print(f" - Student: {profile.full_name} ({profile.student_id})")
    print(f" - Accumulated days ({semester}): {initial_days} day(s)")
    print(f" - Registered activities count: {initial_act_count}")

    # 2. Create a new activity record to append (Side-effect)
    new_activity_code = "CTXH_TIEP_SUC_MUA_THI_2026"
    hours = 16.0
    added_days = round(hours / 8.0, 2)  

    new_record = ActivityRecord(
        activity_code=new_activity_code,
        hours=hours,
        days=added_days,
        semester=semester,
        registered_at=datetime.now().isoformat(),
    )

    # Update StudentProfile dataclass
    profile.registered_activities.append(new_record)
    profile.accumulated_days[semester] = round(initial_days + added_days, 2)

    # 3. Persist to Mock DB via Atomic Write
    print(
        f"\n[2] PERFORMING WRITE (SIDE-EFFECT): Registering {new_activity_code} (+{added_days} days)..."
    )
    save_student(profile)
    print(" -> Successfully saved via Atomic Write.")

    # 4. Reload from disk to verify state change (Verify step)
    reloaded_profile = load_student(student_id)
    reloaded_days = reloaded_profile.accumulated_days.get(semester, 0.0)
    reloaded_act_count = len(reloaded_profile.registered_activities)

    print(f"\n[3] VERIFY STATE FROM DISK:")
    print(f" - Updated days in DB: {reloaded_days} day(s)")
    print(f" - Updated activities count in DB: {reloaded_act_count}")

    # 5. Assertions for automated validation
    assert reloaded_days == round(
        initial_days + added_days, 2
    ), f"Accumulated days mismatch: expected {initial_days + added_days}, got {reloaded_days}"
    assert (
        reloaded_act_count == initial_act_count + 1
    ), "Activity count did not increment!"

    print("\n" + "=" * 60)
    print("✅ TEST PASSED: Read, Write (side-effect), and Verification succeeded!")
    print("=" * 60)


if __name__ == "__main__":
    test_db_operations()