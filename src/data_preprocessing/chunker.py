"""
Take input from Document 
Split the content into chunks of specified size with overlap
Return a list of DocumentChunk objects
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import re
from config import CHUNK_SIZE, CHUNK_OVERLAP
from src.data_preprocessing.document_loader import load_documents_from_directory
from src.schemas import Document, DocumentChunk


def clean_text(text: str) -> str:
    """Normalize whitespace without removing meaningful content."""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()    
    
def split_document(document: Document, chunksize=CHUNK_SIZE, overlap=CHUNK_OVERLAP) -> List[DocumentChunk]:
    """Split a document into chunks with specified size and overlap"""
    chunks = []
    text = document.content
    start = 0 
    chunk_index = 0
    step = chunksize - overlap
    
    while start < len(text): 
        end = start + chunksize
        chunk_content = text[start:end]
        
        chunk = DocumentChunk(
            doc_id=document.doc_id, 
            chunk_id=f"{document.doc_id}_{chunk_index}",
            content=chunk_content, 
            chunk_index=chunk_index,
            metadata=document.metadata.copy()
        )
        
        chunks.append(chunk)
        chunk_index += 1
        start += step
        
    return chunks
    
    
def chunk_documents(documents: List[Document], chunksize=CHUNK_SIZE, overlap=CHUNK_OVERLAP) -> List[DocumentChunk]:
    """Split a list of documents into chunks"""
    all_chunks = []
    for document in documents: 
        document_chunks = split_document(document, chunksize, overlap)
        all_chunks.extend(document_chunks)
    return all_chunks


# Hàm xử lí dạng nhận bảng để tránh mất ngữ nghĩa 

def split_long_text(
    text: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:
    """
    Split long text by character count.

    Prefer paragraph/sentence/word boundaries when possible.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be >= 0 and smaller than chunk_size"
        )

    text = text.strip()

    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)

        if end < text_length:
            # Prefer a paragraph boundary.
            cut = text.rfind("\n\n", start, end)

            # Otherwise prefer a sentence boundary.
            if cut < start + chunk_size // 2:
                cut = max(
                    text.rfind(". ", start, end),
                    text.rfind("? ", start, end),
                    text.rfind("! ", start, end),
                )

            # Otherwise prefer a word boundary.
            if cut < start + chunk_size // 2:
                cut = text.rfind(" ", start, end)

            if cut > start:
                end = cut

        piece = text[start:end].strip()

        if piece:
            chunks.append(piece)

        if end >= text_length:
            break

        # Start the next chunk with overlap.
        next_start = max(0, end - overlap)

        # Avoid an infinite loop if no progress is made.
        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


def is_markdown_table_row(line: str) -> bool:
    """Check whether a line looks like a Markdown table row."""
    line = line.strip()
    return line.startswith("|") and line.endswith("|")


def is_table_separator(line: str) -> bool:
    """Check whether a line is a Markdown table separator."""
    if not is_markdown_table_row(line):
        return False

    cells = [cell.strip() for cell in line.strip("|").split("|")]
    return bool(cells) and all(
        re.fullmatch(r":?-{3,}:?", cell) is not None
        for cell in cells
    )


def split_markdown_blocks(text: str) -> list[dict[str, str]]:
    """
    Split Markdown into paragraph and table blocks.
    Keep consecutive table rows together.
    """
    lines = text.splitlines()
    blocks = []
    paragraph_lines = []
    i = 0

    def flush_paragraph():
        nonlocal paragraph_lines
        content = "\n".join(paragraph_lines).strip()
        if content:
            blocks.append({
                "type": "text",
                "content": content,
            })
        paragraph_lines = []

    while i < len(lines):
        # A table should contain a header followed by a separator.
        if (
            i + 1 < len(lines)
            and is_markdown_table_row(lines[i])
            and is_table_separator(lines[i + 1])
        ):
            flush_paragraph()

            table_lines = [lines[i], lines[i + 1]]
            i += 2

            while i < len(lines) and is_markdown_table_row(lines[i]):
                table_lines.append(lines[i])
                i += 1

            blocks.append({
                "type": "table",
                "content": "\n".join(table_lines),
            })
        else:
            if not lines[i].strip():
                flush_paragraph()
            else:
                paragraph_lines.append(lines[i])
            i += 1

    flush_paragraph()
    return blocks

# Nếu bảng dài hơn, chia theo dòng
    
def split_markdown_table(
    table_text: str,
    chunk_size: int,
) -> list[str]:
    """Split a Markdown table by complete rows, repeating its header."""
    lines = table_text.splitlines()

    if len(lines) < 2 or not is_table_separator(lines[1]):
        return [table_text]

    header = lines[0]
    separator = lines[1]
    data_rows = lines[2:]

    parts = []
    current_rows = []

    for row in data_rows:
        candidate_rows = current_rows + [row]
        candidate = "\n".join(
            [header, separator, *candidate_rows]
        )

        if len(candidate) <= chunk_size:
            current_rows.append(row)
        else:
            if current_rows:
                parts.append(
                    "\n".join([header, separator, *current_rows])
                )
            else:
                # A single row is longer than the limit.
                # Keep the row intact rather than breaking its columns.
                parts.append(
                    "\n".join([header, separator, row])
                )
                continue

            current_rows = [row]

    if current_rows:
        parts.append(
            "\n".join([header, separator, *current_rows])
        )

    if not parts:
        return ["\n".join([header, separator])]

    return parts

    

def split_document(
    document: Document,
    chunk_size: int,
    overlap: int,
) -> list[DocumentChunk]:
    """Split one document into chunks while preserving Markdown tables."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    blocks = split_markdown_blocks(
        clean_text(document.content)
    )

    # Chuyển các khối thành units.
    # Bảng được chia theo dòng; văn bản được chia theo đoạn.
    units = []

    for block in blocks:
        if block["type"] == "table":
            units.extend(
                split_markdown_table(
                    block["content"],
                    chunk_size,
                )
            )
        else:
            units.extend(
                split_long_text(
                    block["content"],
                    chunk_size, overlap
                )
            )

    # Gom units thành chunks và giữ overlap.
    raw_chunks = []
    current = ""

    for unit in units:
        unit = unit.strip()
        if not unit:
            continue

        candidate = f"{current}\n\n{unit}" if current else unit

        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                raw_chunks.append(current)

            # Không ghép overlap vào bảng vì có thể làm hỏng cấu trúc.
            if unit.lstrip().startswith("|"):
                current = unit
            else:
                overlap_text = current[-overlap:] if overlap else ""
                candidate = f"{overlap_text}\n\n{unit}".strip()

                if len(candidate) <= chunk_size:
                    current = candidate
                else:
                    raw_chunks.extend(
                        split_long_text(candidate, chunk_size, overlap)
                    )
                    current = ""

    if current:
        raw_chunks.append(current)

    # Tạo DocumentChunk và giữ metadata nguồn.
    chunks = []

    for index, chunk_text in enumerate(raw_chunks):
        chunk_metadata = {
            "title": document.title,
            "version": document.version,
            "owner": document.owner,
            "source": document.source,
            **document.metadata,
        }

        # Ghi nhận loại nội dung để tiện kiểm tra.
        chunk_metadata["content_type"] = (
            "table"
            if any(
                is_markdown_table_row(line)
                for line in chunk_text.splitlines()
            )
            else "text"
        )

        chunks.append(
            DocumentChunk(
                doc_id=document.doc_id,
                chunk_id=f"{document.doc_id}_chunk_{index:03d}",
                chunk_index=index,
                content=chunk_text,
                metadata=chunk_metadata,
            )
        )

    return chunks
    
    
if __name__ == "__main__": 
    documents = load_documents_from_directory()
    document_chunks = chunk_documents(documents)
    print(f"Total chunks: {len(document_chunks)}")
    
    for chunk in document_chunks[:-2]: 
        print("=" * 40)
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Document ID: {chunk.doc_id}")
        print(f"Chunk Index: {chunk.chunk_index}")
        print(f"Content: {chunk.content}")
        print("****")
        print(f"Metadata: {chunk.metadata}")
        print(f"Length of content: {len(chunk.content)}")
        print(f"Embedding: {chunk.embedding}")
        
#uv run python -m src.data_preprocessing.chunker
   
    