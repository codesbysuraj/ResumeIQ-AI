"""Application service coordinating resume ingestion using raw SQL."""
import json
from uuid import uuid4
from fastapi import UploadFile
import psycopg2.extras

from app.core.exceptions import DatabaseError, FileProcessingError
from app.core.logging import get_logger
from app.services.nlp.parser import ResumeParser
from app.services.resume.extractor import extract_text_from_file
from app.services.resume.storage import ResumeStorageService, StoredUpload

logger = get_logger(__name__)


class ResumeService:
    """Create resume records and run the synchronous extraction pipeline using raw SQL."""

    def __init__(self, storage: ResumeStorageService | None = None) -> None:
        self._storage = storage or ResumeStorageService()

    async def create_from_upload(self, upload: UploadFile, db) -> dict:
        """Persist an upload, extract its contents, and return its completed record as a dict."""
        stored_upload: StoredUpload | None = None
        resume_id = str(uuid4())
        try:
            stored_upload = await self._storage.save(upload)
            with db.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO resumes (id, filename, file_path, file_type, file_size, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        resume_id,
                        stored_upload.original_filename,
                        str(stored_upload.path),
                        stored_upload.content_type,
                        stored_upload.size,
                        "processing",
                    ),
                )
        except Exception as exc:
            if stored_upload:
                self._storage.delete(stored_upload.path)
            logger.exception("Unable to create resume record.")
            raise DatabaseError("Unable to save the resume record.") from exc

        try:
            raw_text = extract_text_from_file(str(stored_upload.path), stored_upload.content_type)
            if not raw_text:
                raise FileProcessingError("No readable text was found in the uploaded document.")
            parsed_data = ResumeParser.parse_resume_text(raw_text)
            
            with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    UPDATE resumes
                    SET raw_text = %s, parsed_data = %s, status = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id, filename, file_path, file_type, file_size, raw_text, parsed_data, status, created_at, updated_at
                    """,
                    (raw_text, json.dumps(parsed_data), "parsed", resume_id)
                )
                row = cur.fetchone()
                
            logger.info("Resume %s processed successfully.", resume_id)
            return dict(row)
        except Exception as exc:
            try:
                with db.cursor() as cur:
                    cur.execute(
                        "UPDATE resumes SET status = 'error', updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                        (resume_id,)
                    )
            except Exception:
                logger.exception("Unable to record processing failure for resume %s.", resume_id)
            if isinstance(exc, FileProcessingError):
                raise
            logger.exception("Resume %s processing failed.", resume_id)
            raise FileProcessingError("Unable to extract text from the uploaded resume.") from exc
