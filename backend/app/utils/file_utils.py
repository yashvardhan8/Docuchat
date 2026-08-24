"""
Small, focused helpers for safe file handling.
Kept separate from the API layer so upload.py stays thin.
"""
import re
import uuid
from pathlib import Path

from app.config import settings


class UnsupportedFileTypeError(Exception):
    pass


class FileTooLargeError(Exception):
    pass


def validate_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"'{ext}' is not supported. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    return ext


def validate_size(size_bytes: int):
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        raise FileTooLargeError(
            f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB upload limit."
        )


def safe_filename(original_filename: str) -> str:
    """
    Strip path components and unsafe characters, but keep the original
    name recognizable (unlike a pure UUID rename) since it's shown in
    citations to the end user.
    """
    name = Path(original_filename).name  # strip any path traversal
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    stem, ext = Path(name).stem, Path(name).suffix
    unique_suffix = uuid.uuid4().hex[:8]
    return f"{stem}_{unique_suffix}{ext}"
