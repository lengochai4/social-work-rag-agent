"""
Social Work Agent Core
Orchestrates RAG Retrieval + MCP Tool Execution in a ReAct loop.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from src.retrieval.embedder import Embedder
from src.retrieval.hybrid_search import HybridSearch
from src.retrieval.calibration import RetrievalCalibration
from src.agent.loop import react_agent, AgentResult
from src.mcp.server import get_status as mcp_get_status, register_activity as mcp_register_activity
from config import OUTPUT_PATH, DB_PATH


class SocialWorkAgent:
    def __init__(self, chunks_path: Path = OUTPUT_PATH, threshold: float = 0.55):
        self.threshold = threshold
        self.calibrator = RetrievalCalibration(threshold=threshold)
        
        # Load precomputed chunks
        if chunks_path.exists():
            with chunks_path.open("r", encoding="utf-8") as f:
                self.chunks = json.load(f)
        else:
            self.chunks = []

        if self.chunks:
            self.embedder = Embedder()
            self.retriever = HybridSearch(chunks=self.chunks, embedder=self.embedder, alpha=0.5)
        else:
            self.retriever = None

    def search_policy(self, query: str, doc_id: Optional[str] = None) -> str:
        """RAG Tool: Look up CTXH regulations and guidelines with calibration filter and optional metadata filter."""
        if not self.retriever:
            return "Error: Cơ sở tri thức chưa được nạp (thiếu data/ctxh_chunks.json)."

        clean_doc_id = str(doc_id).strip() if doc_id and str(doc_id).lower() != "null" else ""
        results = []
        
        if clean_doc_id:
            # Nếu người dùng truyền doc_id cụ thể -> Lọc chính xác theo doc_id đó
            filter_meta = {"doc_id": clean_doc_id}
            results = self.retriever.search(query, top_k=3, filter_metadata=filter_meta)
        else:
            # GIẢI PHÁP ĐỘNG: Tìm kiếm diện rộng top 5-6 kết quả liên quan nhất
            raw_results = self.retriever.search(query, top_k=6, filter_metadata=None)
            
            if raw_results:
                # Tự động sắp xếp (Sort) theo NĂM BAN HÀNH (publication_year) giảm dần để ưu tiên tài liệu MỚI NHẤT
                def _extract_year(r) -> int:
                    y = r.metadata.get("publication_year") or r.metadata.get("year", 0)
                    return int(y) if str(y).isdigit() else 0

                sorted_results = sorted(
                    raw_results, 
                    key=_extract_year, 
                    reverse=True
                )
                # Lấy top 3 kết quả mới nhất & phù hợp nhất
                results = sorted_results[:3]

        if not results:
            return "Không tìm thấy tài liệu phù hợp trong quy chế."

        if not self.calibrator.should_answer(results):
            return f"Cảnh báo: Điểm phù hợp ({results[0].score:.3f}) dưới ngưỡng tin cậy ({self.threshold}). Không có cơ sở quy định trong tài liệu."

        context_parts = []
        for r in results:
            # Lấy thông tin động từ Metadata của Chunk
            title = r.metadata.get("title", r.metadata.get("source_file", "Quy định CTXH"))
            doc_code = r.doc_id or r.metadata.get("doc_id", r.chunk_id.split("_chunk")[0] if "_chunk" in r.chunk_id else "N/A")
            year_tag = r.metadata.get("publication_year") or r.metadata.get("year", "")
            
            # Đảm bảo hiển thị rõ RAG context để LLM đọc đúng năm/văn bản
            header_str = f"[{title} | Mã văn bản: {doc_code} | Năm: {year_tag} | chunk_id={r.chunk_id} | score={r.score:.3f}]"
            context_parts.append(f"{header_str}:\n{r.content}")

        return "\n\n".join(context_parts)

    def register_activity(self, student_id: str, activity_code: str, points: int, semester: str = "HK1_2025_2026") -> str:
        """MCP Tool (Write): Register activity points."""
        return mcp_register_activity(student_id=student_id, activity_code=activity_code, points=points, semester=semester)

    def get_status(self, student_id: str, semester: str = "") -> str:
        """MCP Tool (Read / Verify): Check status and total points."""
        return mcp_get_status(student_id=student_id, semester=semester)

    def ask(self, question: str, verbose: bool = True) -> AgentResult:
        """Execute agent on user query."""
        tools = {
            "search_policy": self.search_policy,
            "register_activity": self.register_activity,
            "get_status": self.get_status,
        }
        return react_agent(question=question, tool_executor_map=tools, verbose=verbose)