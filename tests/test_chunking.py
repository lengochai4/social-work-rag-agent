"""Unit test for DocumentChunk dataclass and structure."""

from src.schemas import DocumentChunk


def test_chunk_dataclass():
    chunk = DocumentChunk(
        chunk_id="CTXH_001_chunk_001",
        doc_id="CTXH_001",
        chunk_index=0,
        content="Sinh viên tích lũy tối thiểu 40 điểm CTXH để tốt nghiệp.",
        metadata={"title": "Quy định 2013"}
    )
    assert chunk.chunk_id == "CTXH_001_chunk_001"
    assert chunk.doc_id == "CTXH_001"
    assert "40 điểm" in chunk.content
    assert chunk.metadata["title"] == "Quy định 2013"
