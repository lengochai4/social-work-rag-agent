"""tests/test_mcp_server.py: Test suite for CTXH MCP Server.

Validates:
1. Dynamic Tool Discovery (at least 2 tools: get_status, register_activity).
2. Clean stdout stream: stdout is strictly JSON-RPC; all logs route to stderr.
3. State Mutation & Verification loop: get_status -> register_activity (points) -> get_status.
"""

import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rich import print


async def test_mcp_server_workflow():
  print("[bold cyan]=== BẮT ĐẦU KIỂM THỬ MCP SERVER QUA STDIO ===[/bold cyan]\n")

  # 1. Cấu hình subprocess khởi chạy server bằng chính Python của .venv hiện tại
  server_params = StdioServerParameters(
      command=sys.executable,
      args=["-m", "src.mcp.server"],
  )

  # 2. Mở kênh kết nối stdio và khởi tạo session
  async with stdio_client(server_params) as (read_stream, write_stream):
    async with ClientSession(read_stream, write_stream) as session:
      # Bước bắt tay giao thức (Handshake)
      await session.initialize()
      print("[bold green]✔ Kết nối handshake qua stdio thành công![/bold green]")

      # TEST 1: Dynamic Discovery (Khám phá công cụ động)
      print(
          "\n[bold cyan]1. Kiểm tra Dynamic Discovery (list_tools)...[/bold cyan]"
      )
      tools_resp = await session.list_tools()
      tools = tools_resp.tools
      tool_names = [t.name for t in tools]
      print(f"Server công bố {len(tools)} tools: [yellow]{tool_names}[/yellow]")

      assert (
          "get_status" in tool_names
      ), "Lỗi: Thiếu read/verify tool 'get_status'!"
      assert (
          "register_activity" in tool_names
      ), "Lỗi: Thiếu write tool 'register_activity'!"
      print("[bold green]✔ Dynamic Discovery hợp lệ![/bold green]")

      test_student_id = "24110089"

      # TEST 2: Đọc trạng thái ban đầu (READ / VERIFY trước khi ghi)
      print(
          f"\n[bold cyan]2. Đọc hồ sơ ban đầu của sinh viên {test_student_id}...[/bold cyan]"
      )
      read_before = await session.call_tool(
          "get_status",
          {"student_id": test_student_id, "semester": "HK1_2025_2026"},
      )
      data_before = json.loads(read_before.content[0].text)
      initial_points = data_before.get("total_accumulated_points", 0)
      print(f" - Họ tên: {data_before.get('full_name')}")
      print(
          f" - Điểm tích lũy hiện tại: {initial_points} /"
          f" {data_before.get('required_threshold')} điểm"
      )
      print(f" - Đạt điều kiện: {data_before.get('is_qualified')}")

      # TEST 3: Ghi dữ liệu tạo Side-Effect bằng tham số points (WRITE)
      award_points = 5  # Ví dụ: Hoạt động hiến máu +5 điểm
      print(
          f"\n[bold cyan]3. Ghi nhận hoạt động (+{award_points} điểm CTXH)...[/bold cyan]"
      )
      register_resp = await session.call_tool(
          "register_activity",
          {
              "student_id": test_student_id,
              "activity_code": "CTXH_HIEN_MAU_2026",
              "points": award_points,
              "semester": "HK1_2025_2026",
          },
      )
      reg_result = json.loads(register_resp.content[0].text)
      print(f" - Phản hồi đăng ký: {reg_result.get('message')}")
      print(
          f" - Điểm mới trong học kỳ: {reg_result.get('semester_points')} điểm"
      )

      # TEST 4: Bước Verify (Bắt buộc: Đọc lại để quan sát sự thay đổi dữ liệu)
      print(
          "\n[bold cyan]4. Gọi lại 'get_status' để verify thay đổi"
          " (Verification Step)...[/bold cyan]"
      )
      read_after = await session.call_tool(
          "get_status",
          {"student_id": test_student_id, "semester": "HK1_2025_2026"},
      )
      data_after = json.loads(read_after.content[0].text)
      updated_points = data_after.get("total_accumulated_points", 0)
      print(f" - Điểm tích lũy sau cập nhật: {updated_points} điểm")

      # Khẳng định dữ liệu đã thực sự biến đổi đúng với số điểm vừa cộng
      assert (
          updated_points == initial_points + award_points
      ), f"Lỗi: Điểm tích lũy không khớp! Mong muốn {initial_points + award_points}, thực tế {updated_points}"
      print(
          "[bold green]✔ Xác nhận Side-Effect thành công: Điểm đã tăng chính"
          " xác![/bold green]"
      )


def test_stdout_purity():
  """Kiểm tra trực tiếp độ sạch của stdout:

  Mọi byte gửi qua stdout phải phân tích cú pháp được thành JSON-RPC hợp lệ,
  tuyệt đối không bị lẫn tạp âm debug log hay chuỗi in tự do.
  """
  import subprocess

  print(
      "\n[bold cyan]5. Kiểm tra độ sạch của luồng stdout (Clean stdout check)...[/bold cyan]"
  )

  # Chạy server với timeout ngắn và đóng stdin ngay lập tức
  proc = subprocess.Popen(
      [sys.executable, "-m", "src.mcp.server"],
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      text=True,
  )

  try:
    stdout_data, stderr_data = proc.communicate(input="", timeout=3)
  except subprocess.TimeoutExpired:
    proc.kill()
    stdout_data, stderr_data = proc.communicate()

  # stdout khi chưa nhận JSON-RPC request hợp lệ phải trống rỗng hoặc chỉ chứa JSON hợp lệ
  clean_stdout = True
  for line in stdout_data.splitlines():
    line = line.strip()
    if not line:
      continue
    try:
      json.loads(line)  # Phải là gói tin JSON
    except json.JSONDecodeError:
      clean_stdout = False
      print(f"[bold red]❌ Phát hiện tạp âm rò rỉ ra stdout:[/bold red] {line}")

  assert (
      clean_stdout
  ), "Lỗi: stdout bị nhiễm văn bản thường/log! Hãy kiểm tra lại sys.stderr."
  print(
      "[bold green]✔ stdout hoàn toàn sạch, không có tạp âm log lọt qua![/bold"
      " green]"
  )

  if stderr_data:
    print(
        "[bold cyan]Log thu được từ sys.stderr (Đúng chuẩn):[/bold cyan]\n"
        + stderr_data.strip()[:300]
        + "..."
    )


async def main():
  await test_mcp_server_workflow()
  test_stdout_purity()
  print(
      "\n[bold green]🎉 TẤT CẢ CÁC BƯỚC KIỂM THỬ ĐÃ VƯỢT QUA XUẤT SẮC![/bold"
      " green]"
  )


if __name__ == "__main__":
  asyncio.run(main())