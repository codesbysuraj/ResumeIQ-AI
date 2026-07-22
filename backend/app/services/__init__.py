"""
Services package initialization.

Exporting all core extraction, parsing, vector embedding, matching, and AI services.
"""
from app.services.resume.extractor import (
    extract_text_from_docx,
    extract_text_from_file,
    extract_text_from_pdf,
)
from app.services.nlp.parser import ResumeParser
from app.services.nlp.embeddings import EmbeddingService
from app.services.matching.matcher import ATSMatcher
from app.services.ai.gemini import GeminiAIService

__all__ = [
    "extract_text_from_pdf",
    "extract_text_from_docx",
    "extract_text_from_file",
    "ResumeParser",
    "EmbeddingService",
    "ATSMatcher",
    "GeminiAIService",
]
