import asyncio
import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.models.state import AgentState
from schema import PARAMETER_KEYS
from models import llm_consolidator, llm_llama, llm_gemini
from prompts import CONSOLIDATION_PROMPT

logger = logging.getLogger(__name__)

CONSOLIDATION_BATCH_SIZE = 20


async def consolidation_node(state: AgentState) -> AgentState:
    """Phase 4: Consolidation Agent — merges 3 parallel branches into a golden record."""

    # Guard: wait until all branches are validated
    if not (state.get("groq_valid") and state.get("github_valid") and state.get("sambanova_valid")):
        logger.info("Consolidate triggered but waiting for all parallel branches to complete…")
        return {}

    # Idempotency guard
    if state.get("golden_record"):
        return {}

    logger.info("--- PHASE 4: CONSOLIDATION AGENT ---")
    company_name = state["company_name"]

    groq_data = state.get("groq_data", {})
    github_data = state.get("github_data", {})
    sambanova_data = state.get("sambanova_data", {})

    validation_results = {
        param: [
            {"llm_name": "groq", "value": groq_data.get(param)},
            {"llm_name": "github", "value": github_data.get(param)},
            {"llm_name": "sambanova", "value": sambanova_data.get(param)},
        ]
        for param in PARAMETER_KEYS
    }

    consolidated_data: dict = {}
    new_failures: list[str] = []
    last_error = ""

    for i in range(0, len(PARAMETER_KEYS), CONSOLIDATION_BATCH_SIZE):
        batch_params = PARAMETER_KEYS[i : i + CONSOLIDATION_BATCH_SIZE]
        batch_validation = {p: validation_results[p] for p in batch_params}

        prompt = CONSOLIDATION_PROMPT.format(
            company_name=company_name,
            validation_results=json.dumps(batch_validation, indent=2),
        )

        llms_to_try = [llm_consolidator, llm_llama, llm_gemini]
        golden_batch: dict = {}
        batch_success = False

        for current_llm in llms_to_try:
            try:
                response = await current_llm.ainvoke(
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
                golden_batch = json.loads(content.strip())
                batch_success = True
                break
            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"Consolidation error with {type(current_llm).__name__}: {e}. Trying fallback…"
                )
                await asyncio.sleep(2)

        if not batch_success:
            logger.error("All LLMs failed for consolidation batch.")
            new_failures.extend(batch_params)
            for p in batch_params:
                consolidated_data[p] = f"API ERROR: {last_error[:100]}"
            continue

        for p in batch_params:
            val = golden_batch.get(p)
            if val is None or str(val).lower() in ["not found", "null"]:
                new_failures.append(p)
                consolidated_data[p] = "Not Found"
            else:
                consolidated_data[p] = val

    return {"golden_record": consolidated_data, "failed_parameters": new_failures}
