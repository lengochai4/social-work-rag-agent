"""
Demo Entrypoint for Social Work (CTXH) RAG Agent (make demo target).
Demonstrates all 3 required layers:
1. Retrieval (Tra cứu có bằng chứng doc_id/chunk_id).
2. Transformation (Biến đổi: tính toán quy đổi điểm -> ngày, đối chiếu hạn mức 40 điểm).
3. Action & Verify (Gọi tool ghi register_activity -> Gọi tool đọc get_status để kiểm chứng).
"""

import sys
import json
from pathlib import Path

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich import print
from rich.panel import Panel
from rich.console import Console

from src.agent.agent import SocialWorkAgent
from src.mcp.server import load_student

console = Console()


def run_demo():
    print(Panel.fit(
        "[bold cyan]AIPR FINAL PROJECT - KỊCH BẢN DEMO HỆ THỐNG TRỢ LÝ CTXH[/bold cyan]\n"
        "[yellow]Đề tài T5: Trợ lý CTXH: Quy đổi & Đăng ký[/yellow]\n"
        "[green]Luồng chuẩn: Tra cứu RAG -> Tính toán quy đổi -> Ghi nhận (Side effect) -> Kiểm chứng (Verify)[/green]",
        title="LIVE DEMO"
    ))

    agent = SocialWorkAgent()
    # Tự động reset DB về trạng thái gốc để kịch bản demo luôn tái hiện được chuẩn xác
    seed_path = Path("data/db/ctxh_db.seed.json")
    if seed_path.exists():
        import shutil
        shutil.copy(seed_path, Path("data/db/ctxh_db.json"))

    student_id = "24110089"
    initial_profile = load_student(student_id)
    initial_pts = sum(initial_profile.accumulated_points.values()) if initial_profile else 0

    print(f"\n[bold white]1. Thông tin sinh viên thử nghiệm:[/bold white]")
    print(f"   - MSSV: [bold yellow]{student_id}[/bold yellow]")
    print(f"   - Họ và tên: [bold yellow]{initial_profile.full_name if initial_profile else 'Nguyễn Văn An'}[/bold yellow]")
    print(f"   - Điểm CTXH hiện tại trong DB: [bold yellow]{initial_pts}/40 điểm[/bold yellow] (Chưa đủ điều kiện)")

    question = (
        f"Tôi là sinh viên MSSV {student_id}. "
        "Tôi vừa tham gia hoạt động 'Tiếp sức mùa thi 2026' được 15 điểm. "
        "Hãy tra cứu quy định xem hoạt động này quy đổi được mấy ngày CTXH, "
        "đăng ký cộng 15 điểm mã CTXH_TIEP_SUC_MUA_THI_2026 cho tôi vào học kỳ HK1_2025_2026, "
        "và kiểm tra lại xem tổng điểm mới của tôi đã đủ điều kiện xét tốt nghiệp chưa?"
    )

    print(f"\n[bold white]2. Câu hỏi của Sinh Viên gửi đến Agent:[/bold white]")
    print(Panel(f"[italic]{question}[/italic]", style="cyan"))

    print("\n[bold white]3. Quá trình Agent suy luận và tương tác Tools (ReAct Loop):[/bold white]")
    result = agent.ask(question=question, verbose=True)

    print("\n[bold white]4. Câu trả lời cuối cùng từ Trợ lý CTXH:[/bold white]")
    print(Panel(result.final_answer, title="TRẢ LỜI CỦA AGENT", style="bold green"))

    # Kiểm tra trực tiếp DB sau khi chạy
    updated_profile = load_student(student_id)
    updated_pts = sum(updated_profile.accumulated_points.values()) if updated_profile else initial_pts

    print("\n[bold white]5. Bằng chứng kiểm chứng dữ liệu thực tế (Database Verification):[/bold white]")
    print(f"   - Điểm ban đầu trong DB: [yellow]{initial_pts} điểm[/yellow]")
    print(f"   - Điểm sau khi Agent chạy: [bold green]{updated_pts} điểm[/bold green]")
    print(f"   - Trạng thái tốt nghiệp: [bold green]{'ĐẠT CHUẨN TỐT NGHIỆP (>= 40 điểm)' if updated_pts >= 40 else 'Chưa đạt'}[/bold green]")
    print(f"   - Chuỗi Action & Verify: [bold green]{'ĐÃ THỰC THI THÀNH CÔNG' if result.verified else 'CHƯA VERIFY'}[/bold green]")
    print(f"   - Chi phí Tokens: [cyan]{result.usage.get('total_tokens', 0)} tokens[/cyan] ({result.usage.get('calls', 0)} LLM calls)")


if __name__ == "__main__":
    run_demo()
