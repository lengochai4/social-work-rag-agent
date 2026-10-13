"""Unit test for Document loader and metadata lookup."""

from src.schemas import Document
from src.data_preprocessing.document_loader import DOCUMENT_METADATA


def test_document_metadata_schema():
    assert "QUYDINH-HDCDONG-2013.md" in DOCUMENT_METADATA
    meta = DOCUMENT_METADATA["QUYDINH-HDCDONG-2013.md"]
    assert meta["doc_id"] == "CTXH_001"
    assert "HCMUTE" in meta["title"]


def test_document_dataclass():
    doc = Document(
        doc_id="TEST_001",
        title="Tài liệu kiểm thử",
        content="Nội dung kiểm thử",
        source="test.md",
        version="v1.0",
        metadata={"document_type": "regulation"}
    )
    assert doc.doc_id == "TEST_001"
    assert doc.content == "Nội dung kiểm thử"
    assert doc.metadata["document_type"] == "regulation"
