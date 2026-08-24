from pydantic import BaseModel
from typing import List


class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks: int


class DocumentInfo(BaseModel):
    filename: str
    chunks: int
    pages: int | None = None


class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]


class DeleteResponse(BaseModel):
    message: str
    filename: str
