
from dataclasses import dataclass

from src.schemas import RetrievalResult


@dataclass
class RetrievalCalibration:
    threshold: float = 0.55

    def __post_init__(self):
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1.")

    def should_answer(
        self,
        results: list[RetrievalResult],
    ) -> bool:
        """Return True when the best retrieval score meets the threshold."""
        if not results:
            return False

        return results[0].score >= self.threshold

    def calibrate(
        self,
        results: list[RetrievalResult],
    ) -> list[RetrievalResult]:
        """Return retrieved results, or an empty list for no_answer."""
        if not self.should_answer(results):
            return []

        return results
