from app.agents.state import ResumeGraphState
from app.services.nlp.parser import ResumeParser

def nlp_extraction_node(state: ResumeGraphState) -> ResumeGraphState:
    # Skip parsing if we already have it
    if state.get("parsed_profile"):
        return state

    raw_text = state.get("raw_text")
    if not raw_text:
        return state
        
    if "errors" not in state:
        state["errors"] = []
        
    try:
        parsed_data = ResumeParser.parse_resume_text(raw_text)
        state["parsed_profile"] = parsed_data
        state["extracted_skills"] = parsed_data.get("skills", [])
    except Exception as e:
        state["errors"].append(f"NLP parsing failed: {str(e)}")
        
    return state
