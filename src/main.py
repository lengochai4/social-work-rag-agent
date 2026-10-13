"""
Main CLI Entrypoint for Social Work (CTXH) RAG Agent.
Allows querying the CTXH agent interactively or running a quick check.
"""

import sys
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
from rich.prompt import Prompt

from src.agent.agent import SocialWorkAgent


def main():
    print(Panel.fit(
        "[bold cyan]TRỢ LÝ AI CÔNG TÁC XÃ HỘI (CTXH) - ĐH SƯ PHẠM KỸ THUẬT TP.HCM (HCMUTE)[/bold cyan]\n"
        "[yellow]Hỗ trợ tra cứu quy chế, quy đổi điểm/ngày CTXH và đăng ký hoạt động.[/yellow]",
        title="HCMUTE CTXH AGENT"
    ))

    agent = SocialWorkAgent()

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\n[cyan]Câu hỏi:[/cyan] {query}")
        result = agent.ask(query, verbose=True)
        print("\n[bold green]Kết quả:[/bold green]")
        print(result.final_answer)
        return

    print("\n[dim]Gợi ý: Nhập câu hỏi về CTXH, hoặc 'exit'/'quit' để thoát. Nhập 'demo' để chạy kịch bản mẫu.[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold green]Sinh viên hỏi[/bold green]")
            if not user_input or user_input.strip() == "":
                continue
            if user_input.strip().lower() in ["exit", "quit", "q"]:
                print("[cyan]Tạm biệt![/cyan]")
                break
            if user_input.strip().lower() == "demo":
                from run_demo import run_demo
                run_demo()
                continue

            result = agent.ask(user_input.strip(), verbose=True)
            print("\n" + "=" * 50)
            print(f"[bold green]Trợ lý CTXH trả lời:[/bold green]\n{result.final_answer}")
            print(f"[dim]Tokens sử dụng: {result.usage.get('total_tokens', 0)} ({result.usage.get('calls', 0)} calls)[/dim]")
            print("=" * 50 + "\n")
        except (KeyboardInterrupt, EOFError):
            print("\n[cyan]Đã dừng chương trình.[/cyan]")
            break


if __name__ == "__main__":
    main()
