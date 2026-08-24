"""
Thin retrieval layer between the raw vector store and the RAG pipeline.
Kept separate so retrieval strategy (top-k, filtering, future reranking
or hybrid search) can evolve without touching vector_store.py or
rag_pipeline.py.
"""
import logging
from typing import List

from app.config import settings
from app.services import vector_store

logger = logging.getLogger("docuchat.retriever")


def retrieve(question: str, k: int = None) -> List[dict]:
    k = k or settings.TOP_K
    results = vector_store.similarity_search(question, k=k)

    retrieved = []
    for doc in results:
        retrieved.append(
            {
                "text": doc.page_content,
                "source": doc.metadata.get("source"),
                "page": doc.metadata.get("page"),
                "chunk_id": doc.metadata.get("chunk_id"),
            }
        )

    logger.info(f"Retrieved {len(retrieved)} chunks for question: {question[:60]!r}")
    return retrieved
