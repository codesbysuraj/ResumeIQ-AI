"""Tests for secure resume-upload storage."""
import asyncio
from io import BytesIO

import pytest
from starlette.datastructures import Headers, UploadFile

from app.core.config import settings
from app.core.exceptions import FileValidationError
from app.services.resume.storage import ResumeStorageService


def _upload(filename: str, content: bytes, content_type: str) -> UploadFile:
    return UploadFile(
        file=BytesIO(content),
        filename=filename,
        headers=Headers({"content-type": content_type}),
    )


def test_storage_saves_valid_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    payload = b"%PDF-1.7\nresume text"
    stored = asyncio.run(
        ResumeStorageService().save(_upload("candidate resume.pdf", payload, "application/pdf"))
    )
    assert stored.original_filename == "candidate_resume.pdf"
    assert stored.path.exists()
    assert stored.size == len(payload)


def test_storage_rejects_invalid_pdf_content(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    with pytest.raises(FileValidationError, match="valid PDF"):
        asyncio.run(
            ResumeStorageService().save(_upload("candidate.pdf", b"not a pdf", "application/pdf"))
        )
    assert list(tmp_path.iterdir()) == []


def test_storage_rejects_unsupported_extension(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    with pytest.raises(FileValidationError, match="PDF and DOCX"):
        asyncio.run(
            ResumeStorageService().save(_upload("candidate.txt", b"resume", "text/plain"))
        )
