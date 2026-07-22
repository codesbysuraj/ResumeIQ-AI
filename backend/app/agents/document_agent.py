from app.agents.state import ResumeGraphState
from app.services.resume.extractor import extract_text_from_file

def document_processing_node(state: ResumeGraphState) -> ResumeGraphState:
    # Skip extraction if we already have text
    if state.get("raw_text"):
        return state

    file_path = state.get("file_path")
    file_type = state.get("file_type")
    
    # Initialize errors list if missing
    if "errors" not in state:
        state["errors"] = []
        
    try:
        raw_text = extract_text_from_file(file_path, file_type)
        if not raw_text:
            state["errors"].append("No readable text found in document.")
        else:
            state["raw_text"] = raw_text
    except Exception as e:
        state["errors"].append(f"Document extraction failed: {str(e)}")
        
    return state
