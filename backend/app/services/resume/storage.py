"""Secure local storage for uploaded resume documents."""
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4
import zipfile

from fastapi import UploadFile

from app.core.config import settings
from app.core.constants import ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES
from app.core.exceptions import FileValidationError
from app.core.security import sanitize_filename


CHUNK_SIZE_BYTES = 1024 * 1024


@dataclass(frozen=True)
class StoredUpload:
    """Metadata for a validated document written to local storage."""

    original_filename: str
    path: Path
    content_type: str
    size: int


class ResumeStorageService:
    """Validate and persist resume files without trusting client file metadata."""

    @staticmethod
    def _validate_metadata(upload: UploadFile) -> tuple[str, str]:
        if not upload.filename:
            raise FileValidationError("A filename is required.")
        filename = sanitize_filename(upload.filename)
        extension = Path(filename).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise FileValidationError("Only PDF and DOCX resume files are supported.")
        content_type = (upload.content_type or "").lower()
        if content_type and content_type not in ALLOWED_MIME_TYPES:
            raise FileValidationError("The uploaded file has an unsupported content type.")
        return filename, extension

    @staticmethod
    def _validate_file_signature(path: Path, extension: str) -> None:
        """Verify basic file structure after writing; MIME headers can be spoofed."""
        try:
            with path.open("rb") as uploaded_file:
                header = uploaded_file.read(8)
            if extension == ".pdf":
                if not header.startswith(b"%PDF-"):
                    raise FileValidationError("The file content is not a valid PDF document.")
                return
            if not zipfile.is_zipfile(path):
                raise FileValidationError("The file content is not a valid DOCX document.")
            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                raise FileValidationError("The file content is not a valid DOCX document.")
        except FileValidationError:
            raise
        except (OSError, zipfile.BadZipFile) as exc:
            raise FileValidationError("The uploaded document could not be validated.") from exc

    async def save(self, upload: UploadFile) -> StoredUpload:
        """Stream an upload to a temporary file, validate it, then atomically publish it."""
        original_filename, extension = self._validate_metadata(upload)
        upload_directory = Path(settings.UPLOAD_DIR)
        upload_directory.mkdir(parents=True, exist_ok=True)
        stored_path = upload_directory / f"{uuid4()}{extension}"
        temporary_path = stored_path.with_suffix(f"{extension}.part")
        size = 0
        try:
            with temporary_path.open("xb") as destination:
                while chunk := await upload.read(CHUNK_SIZE_BYTES):
                    size += len(chunk)
                    if size > settings.max_upload_size_bytes:
                        raise FileValidationError(
                            f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB} MB upload limit."
                        )
                    destination.write(chunk)
            if size == 0:
                raise FileValidationError("The uploaded file is empty.")
            self._validate_file_signature(temporary_path, extension)
            temporary_path.replace(stored_path)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            stored_path.unlink(missing_ok=True)
            raise
        return StoredUpload(
            original_filename=original_filename,
            path=stored_path,
            content_type=upload.content_type or "application/octet-stream",
            size=size,
        )

    @staticmethod
    def delete(path: str | Path) -> None:
        """Remove a stored upload when its database transaction cannot be completed."""
        Path(path).unlink(missing_ok=True)
