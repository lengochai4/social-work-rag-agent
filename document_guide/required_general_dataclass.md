```python
"""
src/schemas.py: Hợp đồng dữ liệu kỹ thuật dùng chung cho toàn bộ dự án.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any

# ==========================================
# 1. TẦNG TRA CỨU (RETRIEVAL - Thành viên A & C)
# ==========================================
@dataclass
class DocumentChunk:
    """Đơn vị ngữ cảnh văn bản quy chế CTXH."""
    chunk_id: str                      # Mã chunk (ví dụ: "DOC0001_chunk_01")
    doc_id: str                        # Mã văn bản (ví dụ: "DOC0001")
    content: str                       # Nội dung trích đoạn quy chế
    chunk_index: int                   # Vị trí chunk trong văn bản
    metadata: dict[str, Any] = field(default_factory=dict) # doc_id, title, version, owner
    embedding: Optional[list[float]] = None                # Tọa độ vector biểu diễn
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class RetrievalResult:
    """Kết quả tra cứu sau khi xếp hạng Hybrid Search."""
    chunk: DocumentChunk
    score: float                       # Điểm số kết hợp (Hybrid Score)
    bm25_score: float = 0.0            # Điểm chuẩn hóa BM25
    dense_score: float = 0.0           # Điểm cosine similarity


# ==========================================
# 2. TẦNG MCP TOOLS (ACTION & VERIFY - Thành viên B & C)
# ==========================================
@dataclass
class RegisterActivityArgs:
    """Schema tham số đầu vào cho tool ghi (Side effect)."""
    student_id: str                    # Mã số sinh viên (ví dụ: "SV202401")
    activity_code: str                 # Mã hoạt động CTXH (ví dụ: "CTXH_MHX_2026")
    hours: float                       # Số giờ tham gia thực tế (ví dụ: 16.0)
    semester: str                      # Học kỳ áp dụng (ví dụ: "HK1_2025_2026")

@dataclass
class GetStatusArgs:
    """Schema tham số đầu vào cho tool đọc kiểm chứng (Verify tool)."""
    student_id: str                    # Mã số sinh viên cần tra cứu
    semester: Optional[str] = None     # Học kỳ cần lọc trạng thái

@dataclass
class ToolExecutionResult:
    """Kết quả thực thi chuẩn trả về từ MCP Server."""
    success: bool                      # Trạng thái thực thi thành công hay thất bại
    data: dict[str, Any] = field(default_factory=dict) # Dữ liệu chi tiết trả về
    message: str = ""                  # Thông báo phản hồi cho Agent LLM


# ==========================================
# 3. TẦNG AGENT LOOP & LOGGING (Thành viên C)
# ==========================================
@dataclass
class UsageStats:
    """Thống kê chi phí token theo chuẩn barem."""
    calls: int = 0                     # Số lượt gọi LLM
    prompt_tokens: int = 0             # Số prompt tokens tích lũy
    completion_tokens: int = 0         # Số completion tokens tích lũy
    total_tokens: int = 0              # Tổng lượng tokens tiêu thụ

@dataclass
class StepTrace:
    """Ghi vết từng bước thực thi trong vòng lặp Agent."""
    step: int
    thought: Optional[str] = None
    tool_name: Optional[str] = None
    tool_args: Optional[dict[str, Any]] = None
    observation: Optional[str] = None  # Kết quả trả về từ tool

@dataclass
class QueryLogRecord:
    """Bản ghi log cho từng câu test theo định dạng jsonl."""
    timestamp: str
    question: str
    final_answer: str
    is_verified: bool                  # Cờ kiểm tra bước verify đã thực hiện hay chưa
    usage: UsageStats
    traces: list[StepTrace] = field(default_factory=list)