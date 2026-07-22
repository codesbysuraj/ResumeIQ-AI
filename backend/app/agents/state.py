from typing import TypedDict, Optional, List, Dict, Any

class ResumeGraphState(TypedDict):
    # Inputs
    resume_id: str
    file_path: str
    file_type: str
    job_description_id: Optional[str]
    job_description_text: Optional[str]
    weights: Optional[Dict[str, float]]
    
    # NLP Pipeline Data
    raw_text: Optional[str]
    parsed_profile: Optional[Dict[str, Any]]
    extracted_skills: Optional[List[str]]
    resume_embedding: Optional[List[float]]
    job_embedding: Optional[List[float]]
    
    # ATS Data
    overall_score: Optional[float]
    skills_score: Optional[float]
    semantic_score: Optional[float]
    experience_score: Optional[float]
    matched_skills: Optional[List[str]]
    missing_skills: Optional[List[str]]
    
    # AI Feedback
    gemini_feedback: Optional[str]
    
    # Infrastructure
    match_id: Optional[str]
    database_status: str # "pending", "success", "failed"
    errors: List[str]
