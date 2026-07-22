from app.agents.state import ResumeGraphState
from app.services.ai.gemini import GeminiAIService

def ai_feedback_node(state: ResumeGraphState) -> ResumeGraphState:
    resume_text = state.get("raw_text")
    jd_text = state.get("job_description_text")
    
    if not jd_text or not resume_text:
        return state
        
    if "errors" not in state:
        state["errors"] = []
        
    try:
        gemini_feedback = GeminiAIService.generate_structured_summary({
            "overall_score": state.get("overall_score"),
            "semantic_score": state.get("semantic_score"),
            "experience_score": state.get("experience_score"),
            "matched_skills": state.get("matched_skills"),
            "missing_skills": state.get("missing_skills"),
            "sections": state.get("parsed_profile", {}).get("sections", {})
        })
        
        if gemini_feedback:
            state["gemini_feedback"] = gemini_feedback
        else:
            _set_local_fallback(state)
            
    except Exception as e:
        state["errors"].append(f"AI Feedback failed: {str(e)}")
        _set_local_fallback(state)
        
    return state

def _set_local_fallback(state: ResumeGraphState):
    overall = state.get("overall_score", 0)
    matched = ", ".join(state.get("matched_skills", [])) if state.get("matched_skills") else "None"
    missing = ", ".join(state.get("missing_skills", [])) if state.get("missing_skills") else "None"
    semantic = state.get("semantic_score", 0)
    exp = state.get("experience_score", 0)
    
    state["gemini_feedback"] = (
        "⚠️ Local Fallback Assessment (Gemini Quota/Rate-Limited):\n\n"
        f"• **Score Overview**: Candidate evaluated with an overall ATS alignment score of {overall:.0f}%.\n"
        f"• **Skills Match Details**: Matched technical skills: {matched}. Missing required technical skills: {missing}.\n"
        f"• **Semantic & Experience Breakdown**: Calculated a semantic relevance similarity of {semantic:.1f}% and an experience match of {exp:.1f}%."
    )
