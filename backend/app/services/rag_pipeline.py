"""
Orchestrates the two halves of RAG:

  ingest_document(): Loader -> Chunker -> Embeddings -> Vector store
  answer_question(): Retriever -> LLM -> (answer, sources)

Kept deliberately thin — all real logic lives in the individual services
so each part is independently testable and swappable.
"""
import logging
import os

from app.config import settings
from app.services import document_loader, chunker, vector_store, retriever, llm

logger = logging.getLogger("docuchat.pipeline")


def ingest_document(file_path: str, display_name: str) -> int:
    logger.info(f"Ingesting document: {display_name}")

    pages = document_loader.load_document(file_path, display_name)
    logger.info(f"Extracted {len(pages)} page-unit(s) from {display_name}")

    chunks = chunker.chunk_documents(pages)
    logger.info(f"Split into {len(chunks)} chunk(s)")

    vector_store.add_documents(chunks)
    logger.info(f"Indexed {len(chunks)} chunk(s) into the vector store")

    return len(chunks)


def answer_question(question: str) -> dict:
    retrieved = retriever.retrieve(question)

    if not retrieved:
        return {
            "answer": "I couldn't find this information in the uploaded documents.",
            "sources": [],
        }

    answer_text = llm.generate_answer(question, retrieved)

    sources = [
        {
            "filename": r["source"],
            "page": r["page"],
            "chunk_id": r["chunk_id"],
            "snippet": r["text"][:180].strip() + ("..." if len(r["text"]) > 180 else ""),
        }
        for r in retrieved
    ]

    return {"answer": answer_text, "sources": sources}
