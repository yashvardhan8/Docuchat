import logging
import os
import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import settings
from app.schemas.documents import UploadResponse, DocumentListResponse, DocumentInfo, DeleteResponse
from app.services import rag_pipeline, vector_store, document_loader
from app.utils.file_utils import (
    validate_extension,
    validate_size,
    safe_filename,
    UnsupportedFileTypeError,
    FileTooLargeError,
)

logger = logging.getLogger("docuchat.api.upload")
router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        validate_extension(file.filename)
    except UnsupportedFileTypeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    contents = await file.read()
    try:
        validate_size(len(contents))
    except FileTooLargeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    stored_name = safe_filename(file.filename)
    dest_path = os.path.join(settings.UPLOAD_DIR, stored_name)

    with open(dest_path, "wb") as f:
        f.write(contents)

    # We display the ORIGINAL filename in citations (more useful to the
    # user) while storing under a collision-safe name on disk.
    display_name = file.filename

    try:
        chunk_count = rag_pipeline.ingest_document(dest_path, display_name)
    except document_loader.EmptyDocumentError as e:
        os.remove(dest_path)
        raise HTTPException(status_code=422, detail=str(e))
    except document_loader.CorruptedFileError as e:
        os.remove(dest_path)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected ingestion failure")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        raise HTTPException(status_code=500, detail="Failed to process document.")

    return UploadResponse(
        message="Document processed successfully",
        filename=display_name,
        chunks=chunk_count,
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents():
    counts = vector_store.list_indexed_documents()
    docs = [DocumentInfo(filename=name, chunks=count) for name, count in counts.items()]
    return DocumentListResponse(documents=docs)


@router.delete("/{filename}", response_model=DeleteResponse)
async def delete_document(filename: str):
    deleted = vector_store.delete_document(filename)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"'{filename}' not found in the index.")
    return DeleteResponse(message="Document removed", filename=filename)
