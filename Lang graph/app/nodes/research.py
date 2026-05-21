import json
import asyncio
import logging
from typing import List, Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.models.state import AgentState
from schema import PARAMETER_KEYS
from models import llm_llama, llm_github, llm_sambanova
from prompts import RESEARCH_PROMPT, get_schema_table_md

logger = logging.getLogger(__name__)

BATCH_SIZE = 20
CONCURRENCY_LIMIT = 3


async def fetch_parameters_batch(
    llm, company_name: str, parameters: List[str], semaphore: asyncio.Semaphore
) -> Dict[str, Any]:
    async with semaphore:
        schema_table = get_schema_table_md(parameters)
        prompt = RESEARCH_PROMPT.format(
            company_name=company_name,
            schema_table=schema_table,
            parameters_list="\n".join([f"- {p}" for p in parameters]),
        )
        try:
            response = await llm.ainvoke(
                [
                    SystemMessage(
                        content="You always respond in valid JSON format only. Do not wrap in markdown tags like ```json."
                    ),
                    HumanMessage(content=prompt),
                ]
            )
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.loads(content.strip())
        except Exception as e:
            logger.error(f"Error with LLM {type(llm).__name__}: {e}")
            return {p: f"API ERROR: {str(e)[:100]}" for p in parameters}


async def research_with_llm(
    llm, company_name: str, parameters_to_fetch: List[str]
) -> Dict[str, Any]:
    if not parameters_to_fetch:
        return {}
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    tasks = [
        fetch_parameters_batch(llm, company_name, parameters_to_fetch[i : i + BATCH_SIZE], semaphore)
        for i in range(0, len(parameters_to_fetch), BATCH_SIZE)
    ]
    results = await asyncio.gather(*tasks)
    merged: Dict[str, Any] = {}
    for res in results:
        merged.update(res)
    return merged


async def groq_generate(state: AgentState) -> AgentState:
    logger.info("--- GROQ GENERATE ---")
    company_name = state["company_name"]
    failed_params = state.get("groq_failed_params", [])
    params_to_fetch = failed_params if failed_params else PARAMETER_KEYS
    result = await research_with_llm(llm_llama, company_name, params_to_fetch)
    current_data = state.get("groq_data", {})
    current_data.update(result)
    return {"groq_data": current_data}


async def github_generate(state: AgentState) -> AgentState:
    logger.info("--- GITHUB GENERATE ---")
    company_name = state["company_name"]
    failed_params = state.get("github_failed_params", [])
    params_to_fetch = failed_params if failed_params else PARAMETER_KEYS
    result = await research_with_llm(llm_github, company_name, params_to_fetch)
    current_data = state.get("github_data", {})
    current_data.update(result)
    return {"github_data": current_data}


async def sambanova_generate(state: AgentState) -> AgentState:
    logger.info("--- SAMBANOVA GENERATE ---")
    company_name = state["company_name"]
    failed_params = state.get("sambanova_failed_params", [])
    params_to_fetch = failed_params if failed_params else PARAMETER_KEYS
    result = await research_with_llm(llm_sambanova, company_name, params_to_fetch)
    current_data = state.get("sambanova_data", {})
    current_data.update(result)
    return {"sambanova_data": current_data}
