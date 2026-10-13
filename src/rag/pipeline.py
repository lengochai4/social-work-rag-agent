from dataclasses import dataclass, field


@dataclass
class RAGResponse:
    question: str
    answer: str
    status: str
    sources: list[dict] = field(default_factory=list)


class RAGPipeline:
    def __init__(
        self,
        retriever,
        calibrator,
        generator,
        top_k: int = 5,
    ):
        self.retriever = retriever
        self.calibrator = calibrator
        self.generator = generator
        self.top_k = top_k

    def ask(self, question: str) -> RAGResponse:
        question = question.strip()

        if not question:
            return RAGResponse(
                question=question,
                answer="Vui lòng nhập câu hỏi.",
                status="no_answer",
            )

        #Retrieval
        results = self.retriever.search(
            question,
            top_k=self.top_k,
        )

        if not results:
            return self._no_answer(question, results)

        #Calibration
        if not self.calibrator.should_answer(results):
            return self._no_answer(question, results)

        #Ghép nội dung
        context = self._build_context(results)

        if not context.strip():
            return self._no_answer(question, results)

        #generation
        answer = self.generator.generate(
            question=question,
            context=context,
        )

        if not answer:
            return self._no_answer(question, results)

        #Trả lời kèm nguồn
        return RAGResponse(
            question=question,
            answer=answer,
            status="success",
            sources=self._extract_sources(results),
        )

    def _build_context(self, results) -> str:
        sections = []

        for index, result in enumerate(results, start=1):
            content = self._get(result, "content", "")
            metadata = self._get(result, "metadata", {}) or {}

            doc_id = self._get(result, "doc_id", "unknown")
            chunk_id = self._get(result, "chunk_id", "unknown")
            title = metadata.get("title", "")

            if not content:
                continue

            sections.append(
                f"[Nguồn {index}: {title}; "
                f"doc_id={doc_id}; chunk_id={chunk_id}]\n"
                f"{content}"
            )

        return "\n\n".join(sections)

    def _extract_sources(self, results) -> list[dict]:
        sources = []

        for result in results:
            metadata = self._get(result, "metadata", {}) or {}

            sources.append({
                "doc_id": self._get(result, "doc_id"),
                "chunk_id": self._get(result, "chunk_id"),
                "title": metadata.get("title"),
                "score": self._get(result, "score"),
            })

        return sources

    def _no_answer(self, question, results):
        return RAGResponse(
            question=question,
            answer=(
                "Tôi chưa tìm thấy đủ căn cứ trong "
                "tài liệu hiện có để trả lời câu hỏi này."
            ),
            status="no_answer",
            sources=self._extract_sources(results or []),
        )

    @staticmethod
    def _get(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)

        return getattr(obj, key, default)