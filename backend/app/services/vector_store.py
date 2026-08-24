"""
FAISS-backed vector store with local persistence.

Kept behind a small functional interface (create/add/save/load/search)
so swapping FAISS for Chroma later only means rewriting this one file —
nothing in rag_pipeline.py or the API layer needs to change.
"""
import logging
import os
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

from app.config import settings
from app.services.embeddings import get_embedding_model

logger = logging.getLogger("docuchat.vectorstore")

_INDEX_NAME = "docuchat_index"
_store: Optional[FAISS] = None


def _index_files_exist() -> bool:
    faiss_file = os.path.join(settings.VECTOR_STORE_PATH, f"{_INDEX_NAME}.faiss")
    return os.path.exists(faiss_file)


def load_vector_store() -> Optional[FAISS]:
    global _store
    if _store is not None:
        return _store
    if not _index_files_exist():
        logger.info("No existing vector store found on disk.")
        return None
    logger.info("Loading vector store from disk.")
    _store = FAISS.load_local(
        settings.VECTOR_STORE_PATH,
        get_embedding_model(),
        index_name=_INDEX_NAME,
        allow_dangerous_deserialization=True,  # safe: it's our own local index
    )
    return _store


def save_vector_store():
    if _store is not None:
        _store.save_local(settings.VECTOR_STORE_PATH, index_name=_INDEX_NAME)
        logger.info("Vector store persisted to disk.")


def add_documents(chunks: List[dict]):
    """chunks: list of {text, source, page, chunk_id}"""
    global _store
    docs = [
        Document(
            page_content=c["text"],
            metadata={
                "source": c["source"],
                "page": c["page"],
                "chunk_id": c["chunk_id"],
            },
        )
        for c in chunks
    ]

    embeddings = get_embedding_model()
    existing = load_vector_store()

    if existing is None:
        _store = FAISS.from_documents(docs, embeddings)
    else:
        existing.add_documents(docs)
        _store = existing

    save_vector_store()


def similarity_search(query: str, k: Optional[int] = None) -> List[Document]:
    store = load_vector_store()
    if store is None:
        return []
    k = k or settings.TOP_K
    return store.similarity_search(query, k=k)


def list_indexed_documents() -> dict:
    """Returns {filename: chunk_count} by scanning the in-memory docstore."""
    store = load_vector_store()
    if store is None:
        return {}
    counts: dict = {}
    for doc in store.docstore._dict.values():
        src = doc.metadata.get("source", "unknown")
        counts[src] = counts.get(src, 0) + 1
    return counts


def delete_document(filename: str) -> bool:
    """
    Rebuilds the index excluding the given filename. FAISS doesn't support
    efficient row deletion, so for a portfolio-scale project we rebuild —
    documented as a known limitation / future improvement (see README).
    """
    global _store
    store = load_vector_store()
    if store is None:
        return False

    remaining = [
        doc for doc in store.docstore._dict.values()
        if doc.metadata.get("source") != filename
    ]
    if len(remaining) == len(store.docstore._dict):
        return False  # nothing matched

    embeddings = get_embedding_model()
    if remaining:
        _store = FAISS.from_documents(remaining, embeddings)
    else:
        _store = None
        # remove persisted files so a restart doesn't reload stale data
        for ext in (".faiss", ".pkl"):
            f = os.path.join(settings.VECTOR_STORE_PATH, f"{_INDEX_NAME}{ext}")
            if os.path.exists(f):
                os.remove(f)
        return True

    save_vector_store()
    return True
