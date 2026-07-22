from app.agents.state import ResumeGraphState
from app.services.matching.matcher import ATSMatcher

def ats_evaluation_node(state: ResumeGraphState) -> ResumeGraphState:
    resume_text = state.get("raw_text")
    jd_text = state.get("job_description_text")
    parsed_profile = state.get("parsed_profile")
    weights = state.get("weights")
    
    if not jd_text or not resume_text:
        return state
        
    if "errors" not in state:
        state["errors"] = []
        
    try:
        eval_result = ATSMatcher.evaluate_match(
            resume_text=resume_text,
            job_description_text=jd_text,
            resume_parsed=parsed_profile,
            weights=weights
        )
        state["overall_score"] = eval_result.get("overall_score")
        state["skills_score"] = eval_result.get("skills_score")
        state["semantic_score"] = eval_result.get("semantic_score")
        state["experience_score"] = eval_result.get("experience_score")
        state["matched_skills"] = eval_result.get("matched_skills", [])
        state["missing_skills"] = eval_result.get("missing_skills", [])
    except Exception as e:
        state["errors"].append(f"ATS Evaluation failed: {str(e)}")
        
    return state
