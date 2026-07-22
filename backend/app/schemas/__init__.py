"""
Pydantic schemas package initialization.

Exporting all request, payload, and response schemas for clean imports across controllers/services.
"""
from app.schemas.base import APIResponse, BaseSchema, PaginatedResponse
from app.schemas.resume import (
    ContactInfo,
    EducationItem,
    ParsedResumeData,
    ResumeCreate,
    ResumeResponse,
    ResumeUpdate,
    WorkExperienceItem,
)
from app.schemas.job_description import (
    JobDescriptionCreate,
    JobDescriptionResponse,
    JobDescriptionUpdate,
    ParsedRequirements,
)
from app.schemas.match_result import (
    MatchRequest,
    MatchResultResponse,
    MatchWeights,
    ScoreBreakdown,
    SkillMatchItem,
)

__all__ = [
    "BaseSchema",
    "APIResponse",
    "PaginatedResponse",
    "ContactInfo",
    "WorkExperienceItem",
    "EducationItem",
    "ParsedResumeData",
    "ResumeCreate",
    "ResumeUpdate",
    "ResumeResponse",
    "ParsedRequirements",
    "JobDescriptionCreate",
    "JobDescriptionUpdate",
    "JobDescriptionResponse",
    "MatchWeights",
    "MatchRequest",
    "SkillMatchItem",
    "ScoreBreakdown",
    "MatchResultResponse",
]
