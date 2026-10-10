"""
Processing module and save chunks in JSON format.
"""

import json 
from dataclasses import asdict
from pathlib import Path

from config import CHUNK_SIZE, CHUNK_OVERLAP, OUTPUT_PATH
from src.data_preprocessing.document_loader import load_documents_from_directory
from src.data_preprocessing.chunker import Document, DocumentChunk, split_document, clean_text, chunk_documents

def main(): 
    if not OUTPUT_PATH.parent.exists():
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        
    documents = load_documents_from_directory()
    
    chunks = chunk_documents(documents, chunksize=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
    data = [asdict(chunk) for chunk in chunks]
    with OUTPUT_PATH.open("w", encoding="utf-8") as f: 
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Saved {len(documents)} documents to {OUTPUT_PATH}")    
    print(f"Saved {len(chunks)} chunks to {OUTPUT_PATH}")
    print(f"Chunks saved to {OUTPUT_PATH}")
    
if __name__ == "__main__":
    main()