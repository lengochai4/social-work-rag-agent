
import json
from pathlib import Path

import pytest

from src.retrieval.hybrid_search import (
    HybridSearch,
    min_max_normalize,
)
from src.retrieval.calibration import RetrievalCalibration
from src.retrieval.hybrid_search import RetrievalResult


class FakeEmbedder:
    """A deterministic toy embedder for unit tests."""

    vocabulary = [
        "appeal",
        "score",
        "document",
        "deadline",
        "evaluation",
        "regulation",
        "bitcoin",
        "weather",
    ]

    def _encode(self, text: str) -> list[float]:
        text = text.lower()
        return [
            float(word in text)
            for word in self.vocabulary
        ]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._encode(text) for text in texts]

    def embed_query(self, query: str) -> list[float]:
        return self._encode(query)


@pytest.fixture
def chunks():
    return [
        {
            "doc_id": "D1",
            "chunk_id": "D1_001",
            "content": "Students can appeal their evaluation score.",
            "metadata": {"title": "Appeal Regulations"},
        },
        {
            "doc_id": "D2",
            "chunk_id": "D2_001",
            "content": "The evaluation regulations describe scoring criteria.",
            "metadata": {"title": "Evaluation"},
        },
        {
            "doc_id": "D3",
            "chunk_id": "D3_001",
            "content": "Bitcoin prices change in the financial market.",
            "metadata": {"title": "Finance"},
        },
    ]


def test_min_max_normalization():
    scores = min_max_normalize([2.0, 4.0, 6.0])

    assert scores == [0.0, 0.5, 1.0]


def test_min_max_normalization_constant_scores():
    scores = min_max_normalize([3.0, 3.0, 3.0])

    assert scores == [0.0, 0.0, 0.0]


def test_hybrid_search_returns_schema(chunks):
    retriever = HybridSearch(
        chunks=chunks,
        embedder=FakeEmbedder(),
        alpha=0.5,
    )

    results = retriever.search("appeal evaluation score", top_k=2)

    assert len(results) == 2
    assert all(isinstance(item, RetrievalResult) for item in results)
    assert results[0].chunk_id == "D1_001"
    assert results[0].score >= results[1].score


def test_hybrid_search_rejects_invalid_input(chunks):
    retriever = HybridSearch(chunks, FakeEmbedder())

    with pytest.raises(ValueError):
        retriever.search("", top_k=3)

    with pytest.raises(ValueError):
        retriever.search("appeal", top_k=0)


def test_calibration_accepts_high_score():
    results = [
        RetrievalResult(
            doc_id="D1",
            chunk_id="D1_001",
            content="Relevant content",
            score=0.8,
        )
    ]

    calibrator = RetrievalCalibration(threshold=0.55)

    assert calibrator.should_answer(results) is True
    assert len(calibrator.calibrate(results)) == 1


def test_calibration_rejects_low_score():
    results = [
        RetrievalResult(
            doc_id="D1",
            chunk_id="D1_001",
            content="Weakly related content",
            score=0.3,
        )
    ]

    calibrator = RetrievalCalibration(threshold=0.55)

    assert calibrator.should_answer(results) is False
    assert calibrator.calibrate(results) == []


def test_calibration_rejects_empty_results():
    calibrator = RetrievalCalibration(threshold=0.55)

    assert calibrator.should_answer([]) is False
    assert calibrator.calibrate([]) == []


def test_testset_has_twelve_questions():
    path = Path(__file__).parent / "testset.jsonl"

    with path.open("r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f if line.strip()]

    assert len(cases) == 12
    assert sum(not case["expected_answerable"] for case in cases) >= 4

#uv run python -m pytest tests/test_hybrid_search.py -v