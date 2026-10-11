"""
tests/test_db_integrity.py: Kiểm thử tính toàn vẹn của Mock DB JSON 
khi chạy liên tiếp các tình huống mô phỏng 12 câu testset.
"""
import json
import asyncio
from pathlib import Path
from src.mcp.client import CTXHMCPClient
from src.mcp.db import load_db
from config import DB_PATH

async def run_stress_test():
    print("=== BẮT ĐẦU KIỂM THỬ TÍNH TOÀN VẸN CỦA DB JSON ===")
    
    # 1. Đọc trạng thái ban đầu
    initial_db = load_db()
    print(f"-> Số lượng sinh viên ban đầu: {len(initial_db.get('students', {}))}")

    # Mô phỏng 12 tác vụ liên tiếp (bao gồm cả câu bình thường, câu lỗi, câu vượt ngưỡng)
    simulated_queries = [
        ("get_status", {"student_id": "24110089"}),
        ("register_activity", {"student_id": "24110089", "activity_code": "CTXH_DON_DEP_2026", "points": 5}),
        ("get_status", {"student_id": "24110103"}),
        ("register_activity", {"student_id": "24110103", "activity_code": "CTXH_HIEN_MAU_2026", "points": 10}),
        ("get_status", {"student_id": "INVALID_ID"}),  # Test lỗi
        ("register_activity", {"student_id": "24110089", "activity_code": "CTXH_XUAN_TN_2026", "points": 10}),
        ("register_activity", {"student_id": "INVALID_ID", "activity_code": "TEST", "points": 5}),  # Test lỗi
        ("get_status", {"student_id": "24110077"}),
        ("register_activity", {"student_id": "24110089", "activity_code": "TEST_INVALID", "points": -5}),  # Test lỗi
        ("get_status", {"student_id": "24110089"}),
        ("register_activity", {"student_id": "24110077", "activity_code": "CTXH_HOI_THAO_2026", "points": 5}),
        ("get_status", {"student_id": "24110077"}),
    ]

    async with CTXHMCPClient() as client:
        for idx, (tool_name, args) in enumerate(simulated_queries, start=1):
            res = await client.call_tool(tool_name, args)
            print(f"[{idx}/12] Gọi {tool_name}({args.get('student_id')}) -> Phản hồi an toàn: {res[:45]}...")

    # 2. Kiểm tra tính toàn vẹn của file JSON
    print("\n=== ĐỐI CHIẾU KIỂM TRA FILE data/db/ctxh_db.json ===")
    assert DB_PATH.exists(), "LỖI: File DB không tồn tại!"
    
    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f) 
        
    assert "students" in data, "LỖI: Cấu trúc JSON bị mất key 'students'!"
    for sv_id, sv in data["students"].items():
        assert "student_id" in sv and "accumulated_points" in sv and "registered_activities" in sv, f"Lỗi cấu trúc tại sinh viên {sv_id}"
        
    print("-> ĐÃ KIỂM TRA: File JSON hợp lệ 100%, không bị hỏng cấu trúc sau 12 lượt chạy liên tục!")

if __name__ == "__main__":
    asyncio.run(run_stress_test())