import logging
from app.models.state import AgentState

logger = logging.getLogger(__name__)


async def entry_node(state: AgentState) -> AgentState:
    """Phase 1: Initialise all state fields to zero values."""
    logger.info("--- PHASE 1: ENTRY NODE ---")
    return {
        "company_name": state["company_name"],
        "groq_data": {},
        "github_data": {},
        "sambanova_data": {},
        "groq_failed_params": [],
        "github_failed_params": [],
        "sambanova_failed_params": [],
        "groq_retry_count": 0,
        "github_retry_count": 0,
        "sambanova_retry_count": 0,
        "groq_valid": False,
        "github_valid": False,
        "sambanova_valid": False,
        "golden_record": {},
        "failed_parameters": [],
    }
