from rich import print
from groq import Groq
from mcp import Client, StdioServerParameters

import os
import sys
import asyncio

class CTXHMCPClient:
    def __init__(self, server_module: str= "src.mcp.server"):
        #1. Khởi tạo cấu hình chạy server qua tiến trình con subprocess
        self.server_params= StdioServerParameters(
            command= sys.executable,
            args= ["-m", server_module],
            raw= True
        )
        self.client_cm= None
        self.client = None
        self.available_tools= []

    async def __aenter__(self):
        self.client_cm = Client(self.server_params)
        self.client= await self.client_cm.__aenter__()

        await self.discover_tools()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client_cm:
            await self.client_cm.__aexit__(exc_type, exc_val, exc_tb)

    async def discover_tools(self):
        """Khám phá danh sách tools động từ Server, tuyệt đối không hardcode."""
        response = await self.client.list_tools()
        self.available_tools = []
        for t in response.tools:
            schema = getattr(t, "input_schema", getattr(t, "inputSchema", {}))
            self.available_tools.append({
                "name": t.name,
                "description": t.description,
                "input_schema": schema
            })
        return self.available_tools

    async def call_tool(self, name: str, arguments: dict) -> str:
        """Gọi tool an toàn, bắt lỗi trả về chuỗi text."""
        try:
            res = await self.client.call_tool(name, arguments)
            
            # Kiểm tra cờ lỗi từ MCP Server
            is_err = getattr(res, "isError", getattr(res, "is_error", False))
            if is_err:
                err_msg = res.content[0].text if res.content else "Unknown error"
                return f"Error: {err_msg}"

            if res.content and len(res.content) > 0:
                return res.content[0].text
            return "Error: Tool không trả về nội dung."
        except Exception as exc:
            return f"Error: {str(exc)}"


# --- LUỒNG CHẠY KIỂM THỬ ĐỘC LẬP TẠI CLIENT ---
async def main():
    print("[bold green]=== 1. KHỞI TẠO TIẾN TRÌNH CON & KẾT NỐI MCP SERVER ===[/bold green]")
    async with CTXHMCPClient() as client:
        print("\n[bold cyan]=== 2. DYNAMIC TOOL DISCOVERY (KHÁM PHÁ ĐỘNG TỪ SERVER) ===[/bold cyan]")
        print(f"Server công bố {len(client.available_tools)} tools:")
        for tool in client.available_tools:
            print(f" -> Tên tool: [yellow]{tool['name']}[/yellow]")
            desc_first_line = tool['description'].splitlines()[0] if tool['description'] else ""
            print(f"    Mô tả   : {desc_first_line}")
            print(f"    Schema  : {tool['input_schema']}\n")

        test_student_id = "24110089"

        # TEST TOOL ĐỌC: get_status
        print(f"[bold cyan]=== 3. GỌI TOOL ĐỌC (get_status) CHO MSSV {test_student_id} ===[/bold cyan]")
        status_res = await client.call_tool("get_status", {"student_id": test_student_id})
        print(f"Kết quả:\n{status_res}\n")

        # TEST TOOL GHI: register_activity (Side-effect cộng điểm)
        print(f"[bold cyan]=== 4. GỌI TOOL GHI (register_activity) CỘNG 10 ĐIỂM ===[/bold cyan]")
        reg_res = await client.call_tool(
            "register_activity",
            {
                "student_id": test_student_id,
                "activity_code": "CTXH_HIEN_MAU_2026",
                "points": 10,
                "semester": "HK1_2025_2026"
            }
        )
        print(f"Kết quả:\n{reg_res}\n")

        # TEST VERIFY LẠI
        print(f"[bold cyan]=== 5. XÁC MINH LẠI (VERIFY) XEM ĐIỂM ĐÃ TĂNG TRONG DB CHƯA ===[/bold cyan]")
        verify_res = await client.call_tool("get_status", {"student_id": test_student_id})
        print(f"Kết quả sau khi cập nhật:\n{verify_res}\n")

        # TEST BẮT LỖI AN TOÀN
        print(f"[bold cyan]=== 6. THỬ NGHIỆM TRUY VẤN LỖI (MÃ SINH VIÊN KHÔNG TỒN TẠI) ===[/bold cyan]")
        err_res = await client.call_tool("get_status", {"student_id": "24110089"})
        print(f"Kết quả bắt lỗi an toàn: {err_res}\n")


if __name__ == "__main__":
    asyncio.run(main())
    