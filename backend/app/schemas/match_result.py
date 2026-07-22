"""
Pydantic schemas for ATS matching requests, breakdown evaluation, and responses.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import Field

from app.schemas.base import BaseSchema


class MatchWeights(BaseSchema):
    """Custom weight configuration for matching algorithm components (sums to 1.0)."""
    skills_weight: float = Field(0.50, ge=0.0, le=1.0)
    experience_weight: float = Field(0.25, ge=0.0, le=1.0)
    education_weight: float = Field(0.10, ge=0.0, le=1.0)
    semantic_weight: float = Field(0.15, ge=0.0, le=1.0)


class MatchRequest(BaseSchema):
    """Payload for triggering a resume-to-job matching calculation."""
    resume_id: str = Field(..., min_length=1)
    job_description_id: str = Field(..., min_length=1)
    weights: Optional[MatchWeights] = Field(default_factory=MatchWeights)


class SkillMatchItem(BaseSchema):
    """Single skill evaluation item."""
    skill_name: str
    category: Optional[str] = "technical"
    matched: bool
    confidence: float = Field(1.0, ge=0.0, le=1.0)


class ScoreBreakdown(BaseSchema):
    """Detailed score breakdown per section."""
    skills_score: float = Field(..., ge=0.0, le=100.0)
    experience_score: float = Field(..., ge=0.0, le=100.0)
    education_score: float = Field(..., ge=0.0, le=100.0)
    semantic_similarity: float = Field(..., ge=0.0, le=100.0)
    penalty_reasons: List[str] = Field(default_factory=list)


class MatchResultResponse(BaseSchema):
    """Full serialized MatchResult response."""
    id: str
    resume_id: str
    job_description_id: str
    overall_score: float
    skills_score: Optional[float] = None
    experience_score: Optional[float] = None
    education_score: Optional[float] = None
    matched_skills: Optional[Dict[str, Any]] = None
    missing_skills: Optional[Dict[str, Any]] = None
    breakdown: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
