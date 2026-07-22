from langgraph.graph import StateGraph, END
from app.agents.state import ResumeGraphState
from app.agents.document_agent import document_processing_node
from app.agents.nlp_agent import nlp_extraction_node
from app.agents.ats_agent import ats_evaluation_node
from app.agents.ai_agent import ai_feedback_node
from app.agents.database_agent import database_agent_node
from app.agents.supervisor import should_process_nlp, should_evaluate_ats, should_generate_ai_feedback

def compile_resume_graph():
    builder = StateGraph(ResumeGraphState)
    
    # Add Nodes
    builder.add_node("document_processing", document_processing_node)
    builder.add_node("nlp_extraction", nlp_extraction_node)
    builder.add_node("ats_evaluation", ats_evaluation_node)
    builder.add_node("ai_feedback", ai_feedback_node)
    builder.add_node("database_agent", database_agent_node)
    
    # Define execution flow (Edges)
    builder.set_entry_point("document_processing")
    
    # Document -> NLP (Conditional)
    builder.add_conditional_edges(
        "document_processing",
        should_process_nlp,
        {
            "nlp_extraction": "nlp_extraction",
            "end": "database_agent"
        }
    )
    
    # NLP -> ATS (Conditional)
    builder.add_conditional_edges(
        "nlp_extraction",
        should_evaluate_ats,
        {
            "ats_evaluation": "ats_evaluation",
            "database_agent": "database_agent"
        }
    )
    
    # ATS -> AI Feedback (Conditional)
    builder.add_conditional_edges(
        "ats_evaluation",
        should_generate_ai_feedback,
        {
            "ai_feedback": "ai_feedback",
            "database_agent": "database_agent"
        }
    )
    
    # AI Feedback -> Database
    builder.add_edge("ai_feedback", "database_agent")
    
    # Database -> End
    builder.add_edge("database_agent", END)
    
    return builder.compile()

# Global Compiled Graph
resume_graph = compile_resume_graph()
