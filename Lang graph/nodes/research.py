import json
import asyncio
import logging
from typing import List, Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage

from state import AgentState
from schema import PARAMETER_KEYS
from models import llm_branch_1, llm_branch_2, llm_branch_3, rate_limiter
from prompts import RESEARCH_PROMPT, get_schema_table_md

logger = logging.getLogger(__name__)

BATCH_SIZE = 25
LLM_TIMEOUT_SECONDS = 120
MAX_RETRIES_PER_BATCH = 3


async def fetch_parameters_batch(llm, company_name: str, parameters: List[str], retry: int = 0) -> Dict[str, Any]:
    """Fetch one batch of parameters from a single LLM, with timeout and retry."""
    schema_table = get_schema_table_md(parameters)
    prompt = RESEARCH_PROMPT.format(
        company_name=company_name,
        schema_table=schema_table,
        parameters_list="\n".join([f"- {p}" for p in parameters])
    )
    
    for attempt in range(MAX_RETRIES_PER_BATCH):
        try:
            if attempt > 0:
                wait = 4.0 * (2 ** attempt)  # exponential backoff
                logger.info(f"    Retry {attempt}/{MAX_RETRIES_PER_BATCH} after {wait}s backoff...")
                await asyncio.sleep(wait)
            
            # Respect global rate limit pacing across all concurrent nodes (strictly sequential, 1 request at a time)
            response = await rate_limiter.run(
                asyncio.wait_for,
                llm.ainvoke([
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
                
            result = json.loads(content.strip())
            return result
            
        except asyncio.TimeoutError:
            logger.warning(f"    Timeout ({LLM_TIMEOUT_SECONDS}s) on attempt {attempt+1}")
        except json.JSONDecodeError as e:
            logger.warning(f"    JSON parse error on attempt {attempt+1}: {e}")
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate_limit" in error_str.lower():
                logger.warning(f"    Rate limited on attempt {attempt+1}, will backoff...")
                continue
            logger.error(f"    LLM error on attempt {attempt+1}: {error_str[:120]}")
            # Non-retryable error
            break
    
    logger.error(f"    All {MAX_RETRIES_PER_BATCH} attempts failed for batch of {len(parameters)} params")
    return {p: "API ERROR: Max retries exceeded" for p in parameters}


async def research_with_llm(llm, company_name: str, parameters_to_fetch: List[str]) -> Dict[str, Any]:
    """Run batched research SEQUENTIALLY, paced by the rate limiter."""
    if not parameters_to_fetch:
        return {}
    
    merged_result = {}
    batches = [parameters_to_fetch[i:i+BATCH_SIZE] for i in range(0, len(parameters_to_fetch), BATCH_SIZE)]
    total = len(batches)
    
    for idx, batch in enumerate(batches):
        logger.info(f"  Processing batch {idx+1}/{total} ({len(batch)} params)...")
        result = await fetch_parameters_batch(llm, company_name, batch)
        merged_result.update(result)
    
    return merged_result


async def groq_generate(state: AgentState) -> AgentState:
    logger.info("--- BRANCH 1 GENERATE (groq) ---")
    company_name = state["company_name"]
    failed_params = state.get("groq_failed_params", [])
    params_to_fetch = failed_params if failed_params else PARAMETER_KEYS
    logger.info(f"  Fetching {len(params_to_fetch)} parameters...")
    
    result = await research_with_llm(llm_branch_1, company_name, params_to_fetch)
    
    current_data = state.get("groq_data", {})
    current_data.update(result)
    return {"groq_data": current_data}


async def github_generate(state: AgentState) -> AgentState:
    logger.info("--- BRANCH 2 GENERATE (github) ---")
    company_name = state["company_name"]
    failed_params = state.get("github_failed_params", [])
    params_to_fetch = failed_params if failed_params else PARAMETER_KEYS
    logger.info(f"  Fetching {len(params_to_fetch)} parameters...")
    
    # Stagger: wait for branch 1 to get a head start and clear rate limits
    await asyncio.sleep(15)
    
    result = await research_with_llm(llm_branch_2, company_name, params_to_fetch)
    
    current_data = state.get("github_data", {})
    current_data.update(result)
    return {"github_data": current_data}


async def sambanova_generate(state: AgentState) -> AgentState:
    logger.info("--- BRANCH 3 GENERATE (sambanova) ---")
    company_name = state["company_name"]
    failed_params = state.get("sambanova_failed_params", [])
    params_to_fetch = failed_params if failed_params else PARAMETER_KEYS
    logger.info(f"  Fetching {len(params_to_fetch)} parameters...")
    
    # Stagger: wait for branches 1&2 to finish/reduce pressure
    await asyncio.sleep(30)
    
    result = await research_with_llm(llm_branch_3, company_name, params_to_fetch)
    
    current_data = state.get("sambanova_data", {})
    current_data.update(result)
    return {"sambanova_data": current_data}
