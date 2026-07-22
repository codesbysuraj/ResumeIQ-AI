import json
from uuid import uuid4
import psycopg2.extras
from app.agents.state import ResumeGraphState
from app.core.database import get_db_conn
from app.core.logging import get_logger

logger = get_logger(__name__)

def database_agent_node(state: ResumeGraphState) -> ResumeGraphState:
    resume_id = state.get("resume_id")
    jd_id = state.get("job_description_id")
    overall = state.get("overall_score")
    
    if "errors" not in state:
        state["errors"] = []

    try:
        with get_db_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                
                # If we have ATS matching data, we insert into match_results
                if jd_id and overall is not None:
                    match_id = str(uuid4())
                    
                    # Construct breakdown
                    breakdown = {
                        "ai_feedback": state.get("gemini_feedback", ""),
                        "weights": state.get("weights", {})
                    }
                    
                    cur.execute(
                        """
                        INSERT INTO match_results (
                            id, resume_id, job_description_id, overall_score, skills_score,
                            experience_score, education_score, matched_skills, missing_skills, breakdown
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            match_id,
                            resume_id,
                            jd_id,
                            overall,
                            state.get("skills_score"),
                            state.get("experience_score"),
                            state.get("semantic_score"), # stored in education_score schema field
                            json.dumps({"skills": state.get("matched_skills", [])}),
                            json.dumps({"skills": state.get("missing_skills", [])}),
                            json.dumps(breakdown)
                        )
                    )
                    logger.info("Database Agent: Saved match_results for %s", resume_id)
                    state["match_id"] = match_id
                
                # Update resume status if we extracted text successfully
                raw_text = state.get("raw_text")
                parsed = state.get("parsed_profile")
                if raw_text:
                    cur.execute(
                        """
                        UPDATE resumes
                        SET raw_text = %s, parsed_data = %s, status = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        """,
                        (raw_text, json.dumps(parsed) if parsed else None, "parsed", resume_id)
                    )
                    logger.info("Database Agent: Updated resume %s to parsed status", resume_id)

        state["database_status"] = "success"
    except Exception as e:
        logger.error("Database Agent Error: %s", str(e))
        state["errors"].append(f"Database persistence failed: {str(e)}")
        state["database_status"] = "failed"
        
    return state
