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

        filter_meta = {"doc_id": doc_id} if doc_id else None
        results = self.retriever.search(query, top_k=3, filter_metadata=filter_meta)
        if not results:
            return "Không tìm thấy tài liệu phù hợp trong quy chế."

        if not self.calibrator.should_answer(results):
            return f"Cảnh báo: Điểm phù hợp ({results[0].score:.3f}) dưới ngưỡng tin cậy ({self.threshold}). Không có cơ sở quy định trong tài liệu."

        # Format context with citations
        context_parts = []
        for r in results:
            title = r.metadata.get("title", "Quy định CTXH")
            context_parts.append(f"[{title} | chunk_id={r.chunk_id} | score={r.score:.3f}]:\n{r.content}")

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
