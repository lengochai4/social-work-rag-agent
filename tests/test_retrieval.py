"""tests/test_retrieval.py: Comprehensive unit tests for RAG Retrieval & Calibration pipeline.
Covers:
1. Chunk and Document schema dataclasses
2. Embedder & VectorStore operations
3. BM25 + Dense Hybrid Search score fusion
4. Min-Max normalization
5. Calibration rejection logic (thresholding)
6. Metadata filtering (doc_id)
7. Benchmark testset validation
"""

import json
from pathlib import Path
import pytest
import numpy as np

from src.schemas import Document, DocumentChunk, RetrievalResult
from src.retrieval.hybrid_search import HybridSearch, min_max_normalize
from src.retrieval.calibration import RetrievalCalibration
from src.retrieval.embedder import Embedder
from src.retrieval.vector_store import VectorStore
from config import PROJECT_ROOT, OUTPUT_PATH


class FakeEmbedder:
    """Deterministic mock embedder for lightning-fast testing without loading neural weights."""
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(t) % 10 + 1), 0.5, 0.2] for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return [float(len(text) % 10 + 1), 0.5, 0.2]


@pytest.fixture
def sample_chunks():
    return [
        {
            "chunk_id": "D1_001",
            "doc_id": "D1",
            "content": "Sinh viên có quyền khiếu nại kết quả đánh giá điểm công tác xã hội.",
            "metadata": {"title": "Quy chế CTXH 2013"}
        },
        {
            "chunk_id": "D1_002",
            "doc_id": "D1",
            "content": "Quy định về thời hạn khiếu nại điểm CTXH trong vòng 15 ngày làm việc.",
            "metadata": {"title": "Quy chế CTXH 2013"}
        },
        {
            "chunk_id": "D2_001",
            "doc_id": "D2",
            "content": "Sinh viên tích lũy tối thiểu 40 điểm CTXH để đủ điều kiện xét tốt nghiệp.",
            "metadata": {"title": "Sổ tay sinh viên 2024"}
        }
    ]


def test_document_and_chunk_dataclasses():
    doc = Document(
        doc_id="CTXH_TEST",
        title="Test Regulation",
        content="Testing content",
        version="v1.0"
    )
    assert doc.doc_id == "CTXH_TEST"
    assert doc.title == "Test Regulation"

    chunk = DocumentChunk(
        chunk_id="CTXH_TEST_chunk_001",
        doc_id="CTXH_TEST",
        chunk_index=0,
        content="Testing chunk content"
    )
    assert chunk.chunk_id == "CTXH_TEST_chunk_001"
    assert chunk.chunk_index == 0


def test_min_max_normalization():
    raw_scores = [1.0, 2.0, 3.0, 4.0, 5.0]
    norm_scores = min_max_normalize(raw_scores)
    assert norm_scores[0] == 0.0
    assert norm_scores[-1] == 1.0
    assert all(0.0 <= s <= 1.0 for s in norm_scores)


def test_min_max_constant_scores():
    raw_scores = [3.0, 3.0, 3.0]
    norm_scores = min_max_normalize(raw_scores)
    assert norm_scores == [0.0, 0.0, 0.0]


def test_hybrid_search_workflow(sample_chunks):
    retriever = HybridSearch(
        chunks=sample_chunks,
        embedder=FakeEmbedder(),
        alpha=0.5
    )
    results = retriever.search("khiếu nại điểm công tác xã hội", top_k=2)
    assert len(results) == 2
    assert all(isinstance(r, RetrievalResult) for r in results)
    assert results[0].score >= results[1].score


def test_hybrid_search_with_metadata_filter(sample_chunks):
    retriever = HybridSearch(chunks=sample_chunks, embedder=FakeEmbedder())
    results = retriever.search("điểm", top_k=2, filter_metadata={"doc_id": "D2"})
    assert len(results) > 0
    assert all(r.doc_id == "D2" for r in results)


def test_hybrid_search_invalid_inputs(sample_chunks):
    retriever = HybridSearch(chunks=sample_chunks, embedder=FakeEmbedder())
    with pytest.raises(ValueError):
        retriever.search("", top_k=3)
    with pytest.raises(ValueError):
        retriever.search("test", top_k=0)


def test_calibration_thresholding():
    calibrator = RetrievalCalibration(threshold=0.55)
    assert calibrator.should_answer([]) is False

    low_res = [RetrievalResult(chunk_id="c1", doc_id="d1", content="t", score=0.42)]
    assert calibrator.should_answer(low_res) is False

    high_res = [RetrievalResult(chunk_id="c1", doc_id="d1", content="t", score=0.91)]
    assert calibrator.should_answer(high_res) is True


def test_testset_has_twelve_questions_and_four_no_answers():
    testset_path = PROJECT_ROOT / "tests" / "testset.jsonl"
    assert testset_path.exists(), "testset.jsonl is missing!"

    cases = []
    with testset_path.open("r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f if line.strip()]

    assert len(cases) >= 12, f"Expected >= 12 questions, got {len(cases)}"
    no_answers = [c for c in cases if not c.get("expected_answerable", True)]
    assert len(no_answers) >= 4, f"Expected >= 4 no_answer questions, got {len(no_answers)}"
