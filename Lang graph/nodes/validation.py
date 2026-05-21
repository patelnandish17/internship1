import logging
from typing import Dict, Any, List, Tuple
from state import AgentState
from schema import PARAMETER_KEYS, VALIDATION_RULES

logger = logging.getLogger(__name__)

MAX_RETRIES = 3

def validate_data(data: Dict[str, Any]) -> Tuple[List[str], bool]:
    """Validates data against rules. Returns (failed_parameters, is_valid)"""
    failed_params = []
    
    for param in PARAMETER_KEYS:
        rules = VALIDATION_RULES.get(param, {})
        value = data.get(param)
        is_valid = True
        
        # Base logic
        if value is None or str(value).lower() in ["not found", "null", "none", "", "api error"]:
            is_valid = False
            
        # Composite validation
        if is_valid and rules.get("is_composite"):
            elements = str(value).split(";")
            elements = [e.strip() for e in elements if e.strip()]
            min_elems = rules.get("min_elements", 1)
            max_elems = rules.get("max_elements", 100)
            if len(elements) < min_elems or len(elements) > max_elems:
                is_valid = False
                
        if not is_valid:
            failed_params.append(param)
            
    return failed_params, len(failed_params) == 0

def groq_validate(state: AgentState) -> AgentState:
    logger.info("--- GROQ VALIDATE ---")
    data = state.get("groq_data", {})
    failed_params, is_valid = validate_data(data)
    
    retry_count = state.get("groq_retry_count", 0)
    if not is_valid and retry_count < MAX_RETRIES:
        return {"groq_failed_params": failed_params, "groq_retry_count": retry_count + 1, "groq_valid": False}
    else:
        return {"groq_failed_params": [], "groq_valid": True}

def github_validate(state: AgentState) -> AgentState:
    logger.info("--- GITHUB VALIDATE ---")
    data = state.get("github_data", {})
    failed_params, is_valid = validate_data(data)
    
    retry_count = state.get("github_retry_count", 0)
    if not is_valid and retry_count < MAX_RETRIES:
        return {"github_failed_params": failed_params, "github_retry_count": retry_count + 1, "github_valid": False}
    else:
        return {"github_failed_params": [], "github_valid": True}

def sambanova_validate(state: AgentState) -> AgentState:
    logger.info("--- SAMBANOVA VALIDATE ---")
    data = state.get("sambanova_data", {})
    failed_params, is_valid = validate_data(data)
    
    retry_count = state.get("sambanova_retry_count", 0)
    if not is_valid and retry_count < MAX_RETRIES:
        return {"sambanova_failed_params": failed_params, "sambanova_retry_count": retry_count + 1, "sambanova_valid": False}
    else:
        return {"sambanova_failed_params": [], "sambanova_valid": True}
