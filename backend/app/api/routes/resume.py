"""Resume ingestion endpoints."""
from fastapi import APIRouter, Depends, File, UploadFile, status

from app.core.database import get_db
from app.schemas.resume import ResumeResponse
from app.services.resume.service import ResumeService

router = APIRouter()


@router.post(
    "/upload",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and process a resume",
)
async def upload_resume(
    file: UploadFile = File(..., description="Resume document in PDF or DOCX format."),
    db = Depends(get_db),
) -> ResumeResponse:
    """Store a resume, extract its text, and return the parsed record."""
    resume_dict = await ResumeService().create_from_upload(file, db)
    return ResumeResponse.model_validate(resume_dict)
