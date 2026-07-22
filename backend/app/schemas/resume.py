"""
Pydantic schemas for Resume payloads, parsed structured data, and API responses.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema


class ContactInfo(BaseSchema):
    """Extracted contact information from a resume."""
    name: Optional[str] = Field(None, description="Full name of the candidate")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="City, State / Country")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    website: Optional[str] = Field(None, description="Personal portfolio URL")


class WorkExperienceItem(BaseSchema):
    """Single work experience entry."""
    job_title: str
    company: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    skills_used: List[str] = Field(default_factory=list)


class EducationItem(BaseSchema):
    """Single education entry."""
    degree: str
    institution: str
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None


class ParsedResumeData(BaseSchema):
    """Complete structured NLP extraction payload from a resume."""
    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    summary: Optional[str] = Field(None, description="Professional summary / objective")
    skills: List[str] = Field(default_factory=list, description="Extracted technical and soft skills")
    experience: List[WorkExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)


class ResumeCreate(BaseSchema):
    """Payload metadata for creating/uploading a resume."""
    filename: str = Field(..., min_length=1, max_length=255)
    file_type: str = Field(..., max_length=50)
    file_size: int = Field(..., ge=0)


class ResumeUpdate(BaseSchema):
    """Payload for updating resume processing status or data."""
    status: Optional[str] = Field(None, max_length=50)
    raw_text: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None


class ResumeResponse(BaseSchema):
    """Full serialized Resume response."""
    id: str
    filename: str
    file_path: str
    file_type: str
    file_size: int
    raw_text: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    updated_at: datetime
