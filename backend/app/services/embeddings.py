import logging

from langchain_community.embeddings import FastEmbedEmbeddings

logger = logging.getLogger("docuchat.embeddings")

_embedding_model = None


def get_embedding_model() -> FastEmbedEmbeddings:
    global _embedding_model

    if _embedding_model is None:
        logger.info("Loading lightweight FastEmbed model...")

        _embedding_model = FastEmbedEmbeddings(
            model_name="BAAI/bge-small-en-v1.5"
        )

    return _embedding_model