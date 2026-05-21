import logging
from state import AgentState

logger = logging.getLogger(__name__)

def route_groq(state: AgentState) -> str:
    if state.get("groq_valid"):
        return "consolidate"
    return "groq_generate"

def route_github(state: AgentState) -> str:
    if state.get("github_valid"):
        return "consolidate"
    return "github_generate"

def route_sambanova(state: AgentState) -> str:
    if state.get("sambanova_valid"):
        return "consolidate"
    return "sambanova_generate"

def route_consolidate(state: AgentState) -> str:
    if state.get("golden_record"):
        logger.info("Consolidation successful. Routing to EXCEL node.")
        return "excel"
    logger.info("Consolidation not complete yet. Ending thread execution safely.")
    return "__end__"

