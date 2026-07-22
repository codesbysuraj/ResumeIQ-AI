"""
Application constants, enums, and configuration values.
Centralizes all magic numbers and string literals used across the codebase.
"""
from enum import Enum


# ---------------------------------------------------------------------------
# File Upload Constants
# ---------------------------------------------------------------------------

class AllowedFileType(str, Enum):
    """MIME types accepted for resume uploads."""
    PDF = "application/pdf"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class FileExtension(str, Enum):
    """File extensions accepted for resume uploads."""
    PDF = ".pdf"
    DOCX = ".docx"


ALLOWED_EXTENSIONS: set[str] = {FileExtension.PDF.value, FileExtension.DOCX.value}
ALLOWED_MIME_TYPES: set[str] = {AllowedFileType.PDF.value, AllowedFileType.DOCX.value}

MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
MAX_FILENAME_LENGTH: int = 255


# ---------------------------------------------------------------------------
# Resume Section Constants
# ---------------------------------------------------------------------------

class ResumeSection(str, Enum):
    """Standard resume sections used during parsing."""
    SUMMARY = "summary"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    SKILLS = "skills"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    ACHIEVEMENTS = "achievements"
    LANGUAGES = "languages"
    CONTACT = "contact"


# Headers that commonly appear in resumes for each section.
# Used by the section detector to classify text blocks.
SECTION_HEADERS: dict[ResumeSection, list[str]] = {
    ResumeSection.SUMMARY: [
        "summary", "objective", "profile", "about me", "professional summary",
        "career objective", "career summary",
    ],
    ResumeSection.EDUCATION: [
        "education", "academic", "qualifications", "academic background",
        "educational qualifications", "academic qualifications",
    ],
    ResumeSection.EXPERIENCE: [
        "experience", "work experience", "employment", "professional experience",
        "work history", "employment history", "career history",
    ],
    ResumeSection.SKILLS: [
        "skills", "technical skills", "core competencies", "competencies",
        "tools", "technologies", "tech stack", "proficiencies",
    ],
    ResumeSection.PROJECTS: [
        "projects", "personal projects", "academic projects", "key projects",
        "notable projects", "side projects",
    ],
    ResumeSection.CERTIFICATIONS: [
        "certifications", "certificates", "licenses", "professional certifications",
        "courses", "training",
    ],
    ResumeSection.ACHIEVEMENTS: [
        "achievements", "awards", "honors", "accomplishments",
        "recognition", "extracurricular",
    ],
    ResumeSection.LANGUAGES: [
        "languages", "language proficiency", "linguistic skills",
    ],
}


# ---------------------------------------------------------------------------
# ATS Scoring Constants
# ---------------------------------------------------------------------------

class ScoreCategory(str, Enum):
    """ATS scoring categories."""
    TECHNICAL_SKILLS = "technical_skills"
    EXPERIENCE = "experience"
    PROJECTS = "projects"
    EDUCATION = "education"
    CERTIFICATIONS = "certifications"
    RESUME_QUALITY = "resume_quality"


# Weights must sum to 1.0 — each category's contribution to the final score.
SCORE_WEIGHTS: dict[str, float] = {
    ScoreCategory.TECHNICAL_SKILLS.value: 0.35,
    ScoreCategory.EXPERIENCE.value: 0.25,
    ScoreCategory.PROJECTS.value: 0.15,
    ScoreCategory.EDUCATION.value: 0.10,
    ScoreCategory.CERTIFICATIONS.value: 0.10,
    ScoreCategory.RESUME_QUALITY.value: 0.05,
}


# ---------------------------------------------------------------------------
# Analysis & Interview Constants
# ---------------------------------------------------------------------------

class AnalysisStatus(str, Enum):
    """Processing status for a resume analysis."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class QuestionDifficulty(str, Enum):
    """Interview question difficulty tiers."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SkillType(str, Enum):
    """Classification of a skill within a job description."""
    REQUIRED = "required"
    PREFERRED = "preferred"


# ---------------------------------------------------------------------------
# NLP Constants
# ---------------------------------------------------------------------------

MIN_SKILL_LENGTH: int = 2
MAX_SKILLS_EXTRACTED: int = 50
MIN_SECTION_TEXT_LENGTH: int = 10


# ---------------------------------------------------------------------------
# API Pagination
# ---------------------------------------------------------------------------

DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 100
