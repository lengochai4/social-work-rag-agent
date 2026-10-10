from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from src.data_preprocessing.chunker import DocumentChunk 
from src.data_preprocessing.document_loader import Document
from src.data_preprocessing.document_store import DocumentStore
from src.retrieval.embedder import Embedder
from src.retrieval.hybrid_search import HybridSearch, RetrievalResult
from src.retrieval.calibration import RetrievalCalibration

@dataclass
class DocumentChunk: 
    """A chunk extracted from a document."""
    
    doc_id: str
    chunk_id: str
    chunk_index: int 
    content: str
    metadata: dict = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    
@dataclass
class Document: 
    """Raw document """
    
    title: str 
    doc_id: str 
    content: str 
    version: Optional[str] = None 
    owner: Optional[str] = None
    source: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    created_at: Optional[datetime] = field(default_factory=datetime.now)

@dataclass
class DocumentStore: 
    """An in memory store for documents and their chunks"""
    
    documents: dict[str, Document] = field(default_factory=dict)
    chunks: dict[str, DocumentChunk] = field(default_factory=dict)
    
@dataclass
class RetrievalResult:
    doc_id: str
    chunk_id: str
    content: str
    score: float
    metadata: dict = field(default_factory=dict)
    spare_core: float = 0.0 
    dense_score: float = 0.0

@dataclass
class RetrievalCalibration:
    threshold: float = 0.55