""" 
Document store for managing and retrieving documents.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from src.schemas import Document, DocumentChunk
from src.data_preprocessing.chunker import chunk_documents

@dataclass
class DocumentStore: 
    """An in memory store for documents and their chunks"""
    
    documents: dict[str, Document] = field(default_factory=dict)
    chunks: dict[str, DocumentChunk] = field(default_factory=dict)
    
    """ 
    CTXH001 -> 1
    CTXH001 -> 2
    CTXH002 -> 2
    """
    
    def add(self, document: Document) -> str: 
        """ Add a document to the store and return its ID"""
        
        if not document.doc_id: 
            document.doc_id = f"CTXH{len(self.documents)+1:03d}"
            self.documents[document.doc_id] = document
            chunks = chunk_documents(document)
            for chunk in chunks:
                self.add_chunk(chunk)
            return document.doc_id
        
    def get(self, doc_id: str) -> Optional[Document]: 
        return self.documents.get(doc_id)
    
    def delete(self, doc_id: str) -> bool:
        if doc_id in self.documents: 
            del self.documents[doc_id]
            chunk_ids = [cid for cid, c in self.chunks.items() if c.doc_id == doc_id]
            for cid in chunk_ids: 
                del self.chunks[cid]
            return True
        return False
    
    def list_all(self) -> List[Document]:
        return list(self.documents.values())
    
    def add_chunk(self, chunk: DocumentChunk) -> str:
        if not chunk.chunk_id: 
            chunk.chunk_id = f"chunk_{len(self.chunks)+1:04d}"
        self.chunks[chunk.chunk_id] = chunk 
        return chunk.chunk_id
    
    def get_chunks_by_doc(self, doc_id: str) -> list[DocumentChunk]:
        return [c for c in self.chunks.values() if c.doc_id == doc_id]
    
    def count(self) -> dict: 
        return {"documents": len(self.documents), "chunks": len(self.chunks)}
            

