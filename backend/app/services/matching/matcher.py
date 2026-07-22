"""
ATS Resume-to-Job Matching Engine.
"""
from typing import Any, Dict, List, Optional
from app.services.nlp.embeddings import EmbeddingService
from app.services.nlp.parser import ResumeParser, SKILL_ALIASES


class ATSMatcher:
    """
    Weighted ATS Resume Matcher.

    Evaluates:
      1. Skill Match Score (Direct & Fuzzy taxonomy comparison)
      2. Semantic Vector Similarity Score (SentenceTransformers embeddings)
      3. Experience & Education alignment
      4. Missing & Matched Skill Gap breakdown
    """

    @staticmethod
    def calculate_skills_score(resume_skills: List[str], jd_text: str) -> Dict[str, Any]:
        """
        Compare normalized resume skills against normalized job description skills.
        Returns score (0-100), matched skills list, and missing skills list.
        """
        from app.services.nlp.parser import SKILL_ALIASES
        jd_skills = ResumeParser.extract_skills(jd_text, custom_taxonomy=SKILL_ALIASES)
        if not jd_skills:
            return {
                "skills_score": 75.0,
                "matched_skills": resume_skills,
                "missing_skills": [],
            }

        resume_set = set(resume_skills)
        jd_set = set(jd_skills)

        matched_skills = sorted(list(resume_set.intersection(jd_set)))
        missing_skills = sorted(list(jd_set - resume_set))

        score = (len(matched_skills) / len(jd_set)) * 100.0 if jd_set else 100.0
        return {
            "skills_score": round(score, 2),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
        }

    @classmethod
    def evaluate_match(
        cls,
        resume_text: str,
        job_description_text: str,
        resume_parsed: Optional[Dict[str, Any]] = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Calculate full ATS match evaluation between resume and job description.
        """
        w = weights or {
            "skills": 0.50,
            "semantic": 0.30,
            "experience": 0.20,
        }

        # 1. Parse resume if not provided
        parsed_res = resume_parsed or ResumeParser.parse_resume_text(resume_text)
        resume_skills = parsed_res.get("skills", [])

        # 2. Skills Match
        skill_res = cls.calculate_skills_score(resume_skills, job_description_text)
        skills_score = skill_res["skills_score"]

        # 3. Vector Embeddings Semantic Similarity
        resume_emb = EmbeddingService.generate_embedding(resume_text)
        jd_emb = EmbeddingService.generate_embedding(job_description_text)
        semantic_score = EmbeddingService.calculate_cosine_similarity(resume_emb, jd_emb)

        # 4. Length/Experience Heuristic Score
        experience_score = min(100.0, max(50.0, (len(resume_text) / 1500.0) * 100.0))

        # 5. Weighted Overall Score
        overall_score = (
            (skills_score * w.get("skills", 0.50))
            + (semantic_score * w.get("semantic", 0.30))
            + (experience_score * w.get("experience", 0.20))
        )
        overall_score = round(min(100.0, max(0.0, overall_score)), 2)

        return {
            "overall_score": overall_score,
            "skills_score": skills_score,
            "experience_score": round(experience_score, 2),
            "semantic_score": semantic_score,
            "matched_skills": skill_res["matched_skills"],
            "missing_skills": skill_res["missing_skills"],
            "breakdown": {
                "skills_match_weight": w.get("skills", 0.50),
                "semantic_weight": w.get("semantic", 0.30),
                "experience_weight": w.get("experience", 0.20),
            },
        }
