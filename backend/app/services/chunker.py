"""
Splits page-level text into overlapping chunks suitable for embedding.

Why chunking: embedding models and LLM context windows both have limits,
and retrieval precision degrades if a "unit" of retrieved text is too
large (it dilutes relevance) or too small (it loses context). Chunking
finds a middle ground sized for the embedding model.

Why overlap: without overlap, a sentence that spans a chunk boundary gets
split and neither half carries full meaning — the fact needed to answer
a question can straddle two chunks. A small overlap (150 of 1000 chars
here) means boundary content appears in both neighboring chunks, so
retrieval is far less likely to "lose" an answer that sits on a seam.
"""
import uuid
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import settings
from app.services.document_loader import PageDocument


def chunk_documents(pages: List[PageDocument]) -> List[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    for page_doc in pages:
        pieces = splitter.split_text(page_doc.text)
        for piece in pieces:
            chunks.append(
                {
                    "text": piece,
                    "source": page_doc.source,
                    "page": page_doc.page,
                    "chunk_id": uuid.uuid4().hex[:12],
                }
            )
    return chunks
