from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):
    company_name: str

    # Model-specific data
    groq_data: Dict[str, Any]
    github_data: Dict[str, Any]
    sambanova_data: Dict[str, Any]

    # Model-specific failed parameters for retries
    groq_failed_params: List[str]
    github_failed_params: List[str]
    sambanova_failed_params: List[str]

    # Model-specific retry counts
    groq_retry_count: int
    github_retry_count: int
    sambanova_retry_count: int

    # Validation flags indicating readiness for consolidation
    groq_valid: bool
    github_valid: bool
    sambanova_valid: bool

    # Final data
    golden_record: Dict[str, Any]
    failed_parameters: List[str]
