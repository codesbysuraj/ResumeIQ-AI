"""
Unit tests for Milestone 4: Core Services & NLP/AI Pipeline.
"""
import os
import tempfile
import pytest
from app.services import (
    ATSMatcher,
    EmbeddingService,
    ResumeParser,
    extract_text_from_file,
)


def test_document_extraction():
    """Test text extraction from TXT file."""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as tmp:
        tmp.write("John Doe\nPython Developer with FastAPI and PostgreSQL experience.")
        tmp_path = tmp.name

    try:
        extracted = extract_text_from_file(tmp_path)
        assert "John Doe" in extracted
        assert "FastAPI" in extracted
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_resume_parser():
    """Test NLP parser for contact info and skills."""
    sample_text = """
    John Smith
    Email: john.smith@example.com
    Phone: (555) 123-4567
    LinkedIn: https://linkedin.com/in/johnsmith

    Summary: Experienced Software Engineer specializing in Python, FastAPI, React, Docker, and PostgreSQL.
    """
    parsed = ResumeParser.parse_resume_text(sample_text)
    assert parsed["contact_info"]["email"] == "john.smith@example.com"
    assert parsed["contact_info"]["phone"] == "(555) 123-4567"
    assert "linkedin.com/in/johnsmith" in parsed["contact_info"]["linkedin"]

    skills = parsed["skills"]
    assert "Python" in skills
    assert "Fastapi" in skills or "FASTAPI" in skills or "FastAPI" in [s.upper() for s in skills]
    assert "Postgresql" in skills or "POSTGRESQL" in skills or "PostgreSQL" in [s.upper() for s in skills]


def test_embedding_service():
    """Test vector embedding generation and similarity scoring."""
    vec1 = EmbeddingService.generate_embedding("Senior Python Developer specializing in backend engineering.")
    vec2 = EmbeddingService.generate_embedding("Python Backend Engineer with API development experience.")
    vec3 = EmbeddingService.generate_embedding("Unrelated topic about baking bread and cakes.")

    assert len(vec1) == 384
    sim_related = EmbeddingService.calculate_cosine_similarity(vec1, vec2)
    sim_unrelated = EmbeddingService.calculate_cosine_similarity(vec1, vec3)

    assert sim_related > sim_unrelated
    assert sim_related > 50.0  # High similarity for related tech stack


def test_ats_matcher():
    """Test full ATS matching calculation between resume and job description."""
    resume_text = """
    Alice Johnson
    Experienced Full Stack Engineer skilled in Python, FastAPI, PostgreSQL, React, and Docker.
    5 years of experience building web applications and REST APIs.
    """

    jd_text = """
    We are looking for a Senior Python Developer with strong FastAPI, PostgreSQL, and Docker experience.
    Responsibilities include building RESTful services and collaborating with frontend teams using React.
    """

    result = ATSMatcher.evaluate_match(resume_text, jd_text)
    assert result["overall_score"] > 60.0
    assert result["skills_score"] > 70.0
    assert "Python" in result["matched_skills"] or "PYTHON" in [s.upper() for s in result["matched_skills"]]
