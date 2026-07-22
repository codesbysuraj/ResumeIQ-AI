"""
Unit tests for Milestone 3: Pydantic V2 Schemas & Data Validation.
"""
from datetime import datetime, timezone
import pytest
from app.schemas import (
    ContactInfo,
    JobDescriptionCreate,
    JobDescriptionResponse,
    MatchRequest,
    MatchResultResponse,
    MatchWeights,
    ParsedResumeData,
    ResumeCreate,
    ResumeResponse,
)


def test_resume_create_validation():
    """Verify ResumeCreate payload validation."""
    payload = ResumeCreate(filename="john_doe.pdf", file_type="application/pdf", file_size=2048)
    assert payload.filename == "john_doe.pdf"
    assert payload.file_size == 2048

    with pytest.raises(Exception):
        ResumeCreate(filename="", file_type="pdf", file_size=-10)


def test_job_description_create_validation():
    """Verify JobDescriptionCreate payload validation."""
    jd = JobDescriptionCreate(
        title="Backend Engineer",
        company="AI Inc",
        raw_text="We are looking for a Python and FastAPI developer with PostgreSQL experience.",
    )
    assert jd.title == "Backend Engineer"
    assert jd.company == "AI Inc"

    with pytest.raises(Exception):
        JobDescriptionCreate(title="Engineer", raw_text="Short")


def test_match_weights_validation():
    """Verify MatchWeights range validation."""
    weights = MatchWeights(skills_weight=0.6, experience_weight=0.2, education_weight=0.1, semantic_weight=0.1)
    assert weights.skills_weight == 0.6

    with pytest.raises(Exception):
        MatchWeights(skills_weight=1.5)


def test_dict_to_pydantic_conversion():
    """Verify converting raw database dict rows to Pydantic responses."""
    now = datetime.now(timezone.utc)
    resume_dict = {
        "id": "resume-uuid-123",
        "filename": "alice.pdf",
        "file_path": "/storage/uploads/alice.pdf",
        "file_type": "application/pdf",
        "file_size": 5000,
        "status": "parsed",
        "created_at": now,
        "updated_at": now,
    }
    resume_response = ResumeResponse.model_validate(resume_dict)
    assert resume_response.id == "resume-uuid-123"
    assert resume_response.filename == "alice.pdf"
    assert resume_response.status == "parsed"

    jd_dict = {
        "id": "jd-uuid-456",
        "title": "ML Engineer",
        "company": "DeepMind",
        "raw_text": "Machine Learning role with PyTorch and spaCy.",
        "created_at": now,
        "updated_at": now,
    }
    jd_response = JobDescriptionResponse.model_validate(jd_dict)
    assert jd_response.id == "jd-uuid-456"
    assert jd_response.company == "DeepMind"

    match_dict = {
        "id": "match-uuid-789",
        "resume_id": "resume-uuid-123",
        "job_description_id": "jd-uuid-456",
        "overall_score": 92.5,
        "created_at": now,
        "updated_at": now,
    }
    match_response = MatchResultResponse.model_validate(match_dict)
    assert match_response.id == "match-uuid-789"
    assert match_response.overall_score == 92.5
