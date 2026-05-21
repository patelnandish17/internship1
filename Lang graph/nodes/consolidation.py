import json
import asyncio
import logging
from langchain_core.messages import HumanMessage, SystemMessage

from state import AgentState
from schema import PARAMETER_KEYS
from models import CONSOLIDATION_FALLBACKS, rate_limiter
from prompts import CONSOLIDATION_PROMPT

logger = logging.getLogger(__name__)

LLM_TIMEOUT_SECONDS = 90
MAX_RETRIES_PER_BATCH = 3
BATCH_DELAY = 4  # seconds between consolidation batches


async def consolidation_node(state: AgentState) -> AgentState:
    """Phase 4: Consolidation Agent (LLM Node)
    
    Waits until all 3 parallel branches are validated before doing real work.
    Early invocations (before all branches complete) return {} safely.
    """
    # Check if all branches are done
    if not (state.get("groq_valid") and state.get("github_valid") and state.get("sambanova_valid")):
        logger.info("Consolidate triggered but waiting for all parallel branches to complete...")
        return {}

    # If already consolidated in a previous trigger, skip
    if state.get("golden_record"):
        logger.info("Golden record already exists. Skipping re-consolidation.")
        return {}

    logger.info("--- PHASE 4: CONSOLIDATION AGENT ---")
    logger.info("All 3 branches validated. Starting consolidation...")
    company_name = state["company_name"]
    
    # Construct validation_results from parallel data
    groq_data = state.get("groq_data", {})
    github_data = state.get("github_data", {})
    sambanova_data = state.get("sambanova_data", {})
    
    validation_results = {}
    for param in PARAMETER_KEYS:
        validation_results[param] = [
            {"llm_name": "branch_1", "value": groq_data.get(param)},
            {"llm_name": "branch_2", "value": github_data.get(param)},
            {"llm_name": "branch_3", "value": sambanova_data.get(param)}
        ]

    params_to_consolidate = PARAMETER_KEYS
    consolidated_data = {}
    new_failures = []
    last_error = "Unknown error"
    
    consolidation_batch_size = 25
    total_batches = (len(params_to_consolidate) + consolidation_batch_size - 1) // consolidation_batch_size
    
    for batch_idx, i in enumerate(range(0, len(params_to_consolidate), consolidation_batch_size)):
        batch_params = params_to_consolidate[i:i+consolidation_batch_size]
        batch_validation = {p: validation_results[p] for p in batch_params}
        
        prompt = CONSOLIDATION_PROMPT.format(
            company_name=company_name,
            validation_results=json.dumps(batch_validation, indent=2)
        )
        
        golden_batch = {}
        batch_success = False
        
        # Retry loop with exponential backoff
        for attempt in range(MAX_RETRIES_PER_BATCH):
            if attempt > 0:
                wait = 4.0 * (2 ** attempt)
                logger.info(f"  Retry {attempt}/{MAX_RETRIES_PER_BATCH} for batch {batch_idx+1} after {wait}s backoff...")
                await asyncio.sleep(wait)
            
            for llm_idx, current_llm in enumerate(CONSOLIDATION_FALLBACKS):
                try:
                    logger.info(f"  Consolidation batch {batch_idx+1}/{total_batches} ({len(batch_params)} params) - LLM #{llm_idx+1}, attempt {attempt+1}")
                    
                    # Respect global rate limit pacing
                    response = await rate_limiter.run(
                        asyncio.wait_for,
                        current_llm.ainvoke([
                            SystemMessage(content="You always respond in valid JSON format only. Do not wrap in markdown tags like ```json."), 
                            HumanMessage(content=prompt)
                        ]),
                        timeout=LLM_TIMEOUT_SECONDS
                    )
                    content = response.content
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0]
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0]
                        
                    golden_batch = json.loads(content.strip())
                    batch_success = True
                    break
                except asyncio.TimeoutError:
                    last_error = f"Timeout ({LLM_TIMEOUT_SECONDS}s)"
                    logger.warning(f"  Consolidation timeout with LLM #{llm_idx+1}")
                except json.JSONDecodeError as e:
                    last_error = f"Invalid JSON: {str(e)[:80]}"
                    logger.warning(f"  JSON error with LLM #{llm_idx+1}: {e}")
                except Exception as e:
                    last_error = str(e)[:100]
                    if "429" in last_error or "rate_limit" in last_error.lower():
                        logger.warning(f"  Rate limited on LLM #{llm_idx+1}, will backoff...")
                    else:
                        logger.warning(f"  Consolidation error: {last_error}")
            
            if batch_success:
                break
                
        if not batch_success:
            logger.error(f"  All attempts failed for batch {batch_idx+1}. Error: {last_error}")
            new_failures.extend(batch_params)
            for p in batch_params:
                consolidated_data[p] = f"API ERROR: {last_error}"
            continue
            
        for p in batch_params:
            val = golden_batch.get(p)
            if val is None or str(val).strip().lower() in ["not found", "null", "none", ""]:
                new_failures.append(p)
                consolidated_data[p] = "Not Found"
            else:
                consolidated_data[p] = val
    
    success_count = len(PARAMETER_KEYS) - len(new_failures)
    logger.info(f"Consolidation complete: {success_count}/{len(PARAMETER_KEYS)} parameters resolved. {len(new_failures)} failed.")
    if new_failures:
        logger.info(f"Failed parameters: {new_failures[:20]}{'...' if len(new_failures) > 20 else ''}")
            
    return {
        "golden_record": consolidated_data,
        "failed_parameters": new_failures
    }
