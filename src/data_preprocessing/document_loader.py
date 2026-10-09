"""
4 main duties:
- Load file .md in data/processed 
- Read Vietnamese text from the file
- Extract metadata from the file
- Return list of Document for file chunker.py to process
"""

from datetime import datetime
from pathlib import Path 
from dataclasses import dataclass, field
from typing import Optional
from config import PROJECT_ROOT, PROCESSED_DATA_PATH, SUPPORTED_FILE_TYPES, RAW_DATA_PATH

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
    
# @dataclass
# class DocumentChunk: 
#     """Chunk of a document"""
    
#     doc_id: str = ""
#     chunk_id: str = ""
#     chunk_index: int = 0
#     content: str
#     metadata: dict = field(default_factory=dict)
#     created_at: Optional[datetime] = field(default_factory=datetime.now)
    
DOCUMENT_METADATA = {
    "QUYDINH-HDCDONG-2013.md": {
            "doc_id":  "CTXH_001",
            "title": "Quy định tổ chức thực hiện chương trình Công tác xã hội cho sinh viên hệ chính quy HCMUTE 2013",
            "document_type": "regulation",
            "document_number": "224/QĐ-ĐHSPKT-CTHSSV",
            "version": "v1.0",
            "owner": "Trường Đại học Công nghệ Kỹ thuật TPHCM",
            "publication_year": 2013,
            "language": "Vietnamese",
            "source": "https://sao.hcmute.edu.vn/Resources/Docs/SubDomain/sao/Quy%20%C4%91%E1%BB%8Bnh%20hi%E1%BB%87n%20h%C3%A0nh/QUYDINH-HDCDONG-2013%20(1).pdf"
        },
    
    "QUY_DINH_DIEM_CTXH-SOTAYSINHVIEN-2024.md": {
        "doc_id": "CTXH_002",
        "title": "Quy định về đánh giá kết quả điểm công tác xã hội sinh viên HCMUTE",
        "document_type": "regulation",
        "document_number": "224/QĐ-ĐHSPKT-CTHSSV",
        "version": "v2.0",
        "owner": "Trường Đại học Công nghệ Kỹ thuật TPHCM",
        "publication_year": 2024,
        "language": "Vietnamese",
        "source": "https://sao.hcmute.edu.vn/Resources/Docs/SubDomain/sao/Quy%20%C4%91%E1%BB%8Bnh%20hi%E1%BB%87n%20h%C3%A0nh/_SO%20TAY%20SV%202024%20-%2006-11%20-%20final.pdf"
    }
}

def read_markdown(file_path: Path) -> str:
    """Read Vietnamese text from a markdown file."""
    try: 
        content= file_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc: 
        raise ValueError(f"Cannot read file {file_path} due to encoding error: {exc}") from exc
    
    content = content.strip()
    
    if not content: 
        raise ValueError(f"File {file_path} is empty.")
    
    return content

def load_document_with_metadata(file_path: Path) -> Document: 
    """Load a markdown file and return a Document object with metadata."""
    if not file_path.exists() or not file_path.is_file(): 
        raise FileNotFoundError(f"File {file_path} does not exist or is not a file.")
    
    content = read_markdown(file_path)
    metadata = DOCUMENT_METADATA.get(file_path.name, {})
    
    # Dùng tên file làm doc_id nếu không có trong metadata
    doc_id = metadata.get("doc_id", file_path.stem)

    return Document(
        doc_id = doc_id, 
        title = metadata.get("title"),
        content = content,
        version = metadata.get("version"),
        owner = metadata.get("owner"),
        source = metadata.get("source"),
        metadata={
            "document_type": metadata.get("document_type"),
            "document_number": metadata.get("document_number"),
            "publication_year": metadata.get("publication_year"),
            "language": metadata.get("language"),
        }
    )

def load_documents_from_directory(data_dir: Path = PROCESSED_DATA_PATH) -> list[Document]: 
    """Load all markdown files from a directory and return a list of Document objects."""
    
    file_paths = sorted(data_dir.glob("*.md"))
    documents = [load_document_with_metadata(file_path) for file_path in file_paths]
    
    documents.sort(key=lambda doc: doc.doc_id)
    
    doc_ids = [doc.doc_id for doc in documents]
    if len(doc_ids) != len(set(doc_ids)):
        raise ValueError("Duplicate doc_id found in loaded documents.")

    return documents 

if __name__ == "__main__":
    documents = load_documents_from_directory()
    
    print(f"Loaded {len(documents)} documents:")
    for doc in documents: 
        print("=" * 40)
        print(f"doc_id: {doc.doc_id}")
        print(f"title: {doc.title}")
        print(f"version: {doc.version}")
        print(f"owner: {doc.owner}")
        print(f"source: {doc.source}")
        print(f"length: {len(doc.content)} characters")
        print(f"metadata: {doc.metadata}")
        print(f"created_at: {doc.created_at:%Y-%m-%d %H:%M:%S}")
        
        
#uv run python -m src.data_preprocessing.document_loader