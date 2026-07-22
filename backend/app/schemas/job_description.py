"""
Pydantic schemas for Job Description payloads, extracted criteria, and API responses.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import Field

from app.schemas.base import BaseSchema


class ParsedRequirements(BaseSchema):
    """Structured requirements extracted from job description text."""
    must_have_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    minimum_experience_years: Optional[float] = None
    required_education: Optional[str] = None
    role_responsibilities: List[str] = Field(default_factory=list)


class JobDescriptionCreate(BaseSchema):
    """Payload for creating a new Job Description."""
    title: str = Field(..., min_length=1, max_length=255, description="Job Title")
    company: Optional[str] = Field(None, max_length=255, description="Company Name")
    raw_text: str = Field(..., min_length=10, description="Full job description text")


class JobDescriptionUpdate(BaseSchema):
    """Payload for updating an existing Job Description."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    raw_text: Optional[str] = Field(None, min_length=10)
    required_skills: Optional[Dict[str, Any]] = None
    preferred_skills: Optional[Dict[str, Any]] = None


class JobDescriptionResponse(BaseSchema):
    """Full serialized JobDescription response."""
    id: str
    title: str
    company: Optional[str] = None
    raw_text: str
    required_skills: Optional[Dict[str, Any]] = None
    preferred_skills: Optional[Dict[str, Any]] = None
    parsed_requirements: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
