"""Unit test for Retrieval calibration."""

from src.retrieval.calibration import RetrievalCalibration
from src.schemas import RetrievalResult


def test_retrieval_calibration_edge_cases():
    calibrator = RetrievalCalibration(threshold=0.55)
    
    # Empty
    assert calibrator.should_answer([]) is False
    
    # Low score
    low_res = [RetrievalResult(chunk_id="c1", doc_id="d1", content="t", score=0.40)]
    assert calibrator.should_answer(low_res) is False
    
    # High score
    high_res = [RetrievalResult(chunk_id="c1", doc_id="d1", content="t", score=0.85)]
    assert calibrator.should_answer(high_res) is True
