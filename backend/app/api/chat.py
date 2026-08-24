import logging

from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse, SourceChunk
from app.services import rag_pipeline, vector_store
from app.services.llm import LLMConfigError

logger = logging.getLogger("docuchat.api.chat")
router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if not vector_store.list_indexed_documents():
        raise HTTPException(
            status_code=400,
            detail="No documents have been uploaded yet. Upload a document first.",
        )

    try:
        result = rag_pipeline.answer_question(question)
    except LLMConfigError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error answering question")
        raise HTTPException(status_code=500, detail="Failed to generate an answer.")

    sources = [SourceChunk(**s) for s in result["sources"]]
    return ChatResponse(answer=result["answer"], sources=sources)
