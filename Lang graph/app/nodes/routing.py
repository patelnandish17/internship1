import logging
from app.models.state import AgentState

logger = logging.getLogger(__name__)


def route_groq(state: AgentState) -> str:
    return "consolidate" if state.get("groq_valid") else "groq_generate"


def route_github(state: AgentState) -> str:
    return "consolidate" if state.get("github_valid") else "github_generate"


def route_sambanova(state: AgentState) -> str:
    return "consolidate" if state.get("sambanova_valid") else "sambanova_generate"
