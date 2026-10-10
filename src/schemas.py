from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict

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

@dataclass
class ActivityRecord:
    """Bản ghi một hoạt động CTXH đã đăng ký."""
    activity_code: str
    hours: float
    days: float
    semester: str
    registered_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

@dataclass
class StudentProfile:
    """Hồ sơ theo dõi CTXH của một sinh viên."""
    student_id: str
    full_name: str
    registered_activities: list[ActivityRecord] = field(default_factory=list)
    accumulated_days: dict[str, float] = field(default_factory=dict)

@dataclass
class RegisterActivityArgs:
    student_id: str
    activity_code: str
    hours: float
    semester: str = "HK1_2025_2026"

@dataclass
class GetStatusArgs:
    student_id: str
    semester: Optional[str] = None