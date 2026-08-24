"""
Reusable embedding service, backed by sentence-transformers so the
project works fully offline/free without any embedding API cost.

Loaded once as a module-level singleton — the model is a few hundred MB
and expensive to reload, so we pay that cost once per process, not once
per request.
"""
import logging
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import settings

logger = logging.getLogger("docuchat.embeddings")

_embedding_model = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        _embedding_model = HuggingFaceEmbeddings(
            model_name=f"sentence-transformers/{settings.EMBEDDING_MODEL}"
            if "/" not in settings.EMBEDDING_MODEL
            else settings.EMBEDDING_MODEL
        )
    return _embedding_model
