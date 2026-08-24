from pydantic import BaseModel, Field
from typing import List, Optional


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User's question")
    history: Optional[List[ChatMessage]] = Field(
        default=None, description="Prior turns for conversational context"
    )


class SourceChunk(BaseModel):
    filename: str
    page: Optional[int] = None
    chunk_id: str
    snippet: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk] = []
