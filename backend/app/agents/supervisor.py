from app.agents.state import ResumeGraphState

def should_process_nlp(state: ResumeGraphState) -> str:
    """Determine if we should proceed to NLP extraction or stop."""
    errors = state.get("errors", [])
    if errors and any("No readable text" in e for e in errors):
        return "end" # Skip to database agent to record failure
    return "nlp_extraction"

def should_evaluate_ats(state: ResumeGraphState) -> str:
    """Determine if we have a job description to evaluate ATS."""
    if state.get("job_description_id") and state.get("job_description_text"):
        return "ats_evaluation"
    return "database_agent"

def should_generate_ai_feedback(state: ResumeGraphState) -> str:
    """Determine if we should call Gemini based on evaluation success."""
    overall = state.get("overall_score")
    if overall is not None:
        return "ai_feedback"
    return "database_agent"
