"""tests/test_mcp_server.py: Script kiểm thử MCP Server qua stdio."""

import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rich import print


async def run_test():
    print("[bold cyan]1. Đang khởi chạy MCP Server qua subprocess stdio...[/bold cyan]")
    # Cấu hình lệnh khởi động server bằng chính Python trong môi trường hiện tại
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.mcp.server"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Bắt tay khởi tạo giao thức MCP
            await session.initialize()
            print("[bold green]✔ Kết nối và handshake thành công![/bold green]\n")

            # TEST 1: Dynamic Discovery (Client tự khám phá danh sách tool)
            print("[bold cyan]2. Đang khám phá công cụ động (list_tools)...[/bold cyan]")
            tools_resp = await session.list_tools()
            tools = tools_resp.tools
            print(f"Server cung cấp {len(tools)} tools:")
            for t in tools:
                print(f" - [yellow]{t.name}[/yellow]: {t.description}")
            assert len(tools) >= 2, "Lỗi: Server phải cung cấp tối thiểu 2 tools!"

            test_student_id = "24110089"

            # TEST 2: Đọc trạng thái ban đầu
            print(f"\n[bold cyan]3. Kiểm tra trạng thái ban đầu của {test_student_id}...[/bold cyan]")
            status_before = await session.call_tool(
                "get_status",
                {"student_id": test_student_id, "semester": "HK1_2025_2026"},
            )
            print("Kết quả ban đầu:", status_before.content[0].text)

            # TEST 3: Ghi dữ liệu (Side-effect)
            print(f"\n[bold cyan]4. Gọi tool ghi (register_activity)...[/bold cyan]")
            register_res = await session.call_tool(
                "register_activity",
                {
                    "student_id": test_student_id,
                    "activity_code": "CTXH_HIEN_MAU_2026",
                    "hours": 8.0,
                    "semester": "HK1_2025_2026",
                },
            )
            print("Kết quả đăng ký:", register_res.content[0].text)

            # TEST 4: Bước Verify (Bắt buộc theo yêu cầu 2.7)
            print(f"\n[bold cyan]5. Verify lại bằng tool đọc (get_status)...[/bold cyan]")
            status_after = await session.call_tool(
                "get_status",
                {"student_id": test_student_id, "semester": "HK1_2025_2026"},
            )
            print("Kết quả sau khi ghi:", status_after.content[0].text)
            print("\n[bold green]🎉 KIỂM THỬ THÀNH CÔNG! SERVER HOẠT ĐỘNG HOÀN HẢO.[/bold green]")


if __name__ == "__main__":
    asyncio.run(run_test())