"""ATS evaluation and matching endpoints using raw SQL."""
import json
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
import psycopg2.extras

from app.core.database import get_db
from app.schemas.match_result import MatchRequest, MatchResultResponse
from app.services.matching.matcher import ATSMatcher
from app.services.ai.gemini import GeminiAIService

router = APIRouter()


@router.post(
    "/evaluate",
    response_model=MatchResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate a resume against a job description",
)
def evaluate_match(
    payload: MatchRequest,
    db = Depends(get_db),
) -> MatchResultResponse:
    """Compare a resume and job description, compute scores, and generate AI feedback."""
    # 1. Fetch resume and job description using raw SQL
    with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, file_path, file_type, raw_text, parsed_data FROM resumes WHERE id = %s",
            (payload.resume_id,)
        )
        resume = cur.fetchone()
        
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {payload.resume_id} not found."
        )

    with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, raw_text FROM job_descriptions WHERE id = %s",
            (payload.job_description_id,)
        )
        jd = cur.fetchone()
        
    if not jd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job Description with ID {payload.job_description_id} not found."
        )

    # 2. Extract weights
    weights = None
    if payload.weights:
        weights = {
            "skills": payload.weights.skills_weight,
            "semantic": payload.weights.semantic_weight,
            "experience": payload.weights.experience_weight,
        }

    # 3. Build initial LangGraph State
    from app.agents.graph import resume_graph
    
    initial_state = {
        "resume_id": payload.resume_id,
        "file_path": resume["file_path"],
        "file_type": resume["file_type"],
        "job_description_id": payload.job_description_id,
        "job_description_text": jd["raw_text"],
        "weights": weights,
        "raw_text": resume["raw_text"]
    }
    
    # 4. Invoke the LangGraph workflow
    final_state = resume_graph.invoke(initial_state)
    
    if final_state.get("errors"):
        # We check if there are fatal errors
        if any("No readable text" in e for e in final_state["errors"]):
            raise HTTPException(status_code=400, detail="Could not extract text from document.")
            
    # 5. Build response using the final state
    breakdown = {
        "ai_feedback": final_state.get("gemini_feedback", ""),
        "weights": weights
    }
    
    from datetime import datetime
    return MatchResultResponse(
        id=final_state.get("match_id", str(uuid4())),
        resume_id=payload.resume_id,
        job_description_id=payload.job_description_id,
        overall_score=final_state.get("overall_score") or 0.0,
        skills_score=final_state.get("skills_score"),
        experience_score=final_state.get("experience_score"),
        education_score=final_state.get("semantic_score"), # semantic score is mapped to education_score field
        matched_skills={"skills": final_state.get("matched_skills", [])},
        missing_skills={"skills": final_state.get("missing_skills", [])},
        breakdown=breakdown,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

