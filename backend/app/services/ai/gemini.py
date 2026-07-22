"""
Google Gemini AI Integration Service.
"""
from typing import Any, Dict, Optional
import google.generativeai as genai

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class GeminiAIService:
    """Service wrapper for Google Gemini AI model interactions."""

    _configured: bool = False

    @classmethod
    def configure(cls) -> bool:
        """Configure Gemini API key if present."""
        if not cls._configured:
            api_key = settings.GEMINI_API_KEY
            if api_key:
                genai.configure(api_key=api_key)
                cls._configured = True
            else:
                logger.warning("GEMINI_API_KEY not configured. AI fallback services will be disabled.")
        return cls._configured

    @classmethod
    def generate_structured_summary(cls, payload: Dict[str, Any]) -> Optional[str]:
        """
        Generates a summary heavily grounded in the structured ATS engine outputs.
        """
        if not cls.configure():
            return None

        try:
            model = genai.GenerativeModel(settings.GEMINI_MODEL)
            prompt = (
                "You are an expert HR recruitment specialist. Analyze the following candidate data "
                "which has been evaluated by an ATS system, and write a concise 4-bullet point executive summary:\n"
                "1. Executive Summary\n"
                "2. Strengths\n"
                "3. Weaknesses\n"
                "4. Recommendation\n\n"
                "STRICT RULES:\n"
                "- DO NOT hallucinate missing skills. If a skill appears in the 'Matched Skills' list, it is present. DO NOT say it is missing.\n"
                "- Only comment on the skills explicitly listed in the Matched or Missing skills.\n"
                "- Reference the ATS Scores in your evaluation.\n\n"
                f"Candidate Data:\n"
                f"Overall ATS Score: {payload.get('overall_score')}%\n"
                f"Semantic Score: {payload.get('semantic_score')}%\n"
                f"Experience Score: {payload.get('experience_score')}%\n"
                f"Matched Skills: {', '.join(payload.get('matched_skills', []))}\n"
                f"Missing Skills: {', '.join(payload.get('missing_skills', []))}\n\n"
                "Extracted Resume Sections:\n"
            )
            
            sections = payload.get("sections", {})
            for sec, content in sections.items():
                if content:
                    prompt += f"\n--- {sec.upper()} ---\n{content[:1000]}\n"
                    
            response = model.generate_content(prompt)
            return response.text.strip() if response and response.text else None
        except Exception as e:
            logger.error("Failed to generate structured candidate summary via Gemini AI: %s", str(e))
            return None
