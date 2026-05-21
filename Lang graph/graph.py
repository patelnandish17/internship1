import os
import json
import asyncio
import logging
import re
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langgraph.graph import StateGraph, START, END
from state import AgentState
from schema import PARAMETER_KEYS, SCHEMA_DATA
from models import llm_branch_1, llm_branch_2, llm_branch_3, rate_limiter, CONSOLIDATION_FALLBACKS
from prompts import RESEARCH_PROMPT, CONSOLIDATION_PROMPT, get_schema_table_md
from langchain_core.messages import HumanMessage, SystemMessage

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("graph_workflow")

# Constants
BATCH_SIZE = 25
LLM_TIMEOUT_SECONDS = 120
MAX_RETRIES_PER_BATCH = 3

# ---------------------------------------------------------------------------
# Helper Research Functions
# ---------------------------------------------------------------------------
async def fetch_parameters_batch(llm, company_name: str, parameters: List[str]) -> Dict[str, Any]:
    """Fetch one batch of parameters from a single LLM, with timeout and rate-limit pacing."""
    schema_table = get_schema_table_md(parameters)
    prompt = RESEARCH_PROMPT.format(
        company_name=company_name,
        schema_table=schema_table,
        parameters_list="\n".join([f"- {p}" for p in parameters])
    )
    
    for attempt in range(MAX_RETRIES_PER_BATCH):
        try:
            if attempt > 0:
                wait = 4.0 * (2 ** attempt)
                logger.info(f"    Retry {attempt}/{MAX_RETRIES_PER_BATCH} after {wait}s...")
                await asyncio.sleep(wait)
            
            # Request LLM within global rate-limiter lock
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
                
            return json.loads(content.strip())
            
        except asyncio.TimeoutError:
            logger.warning(f"    Timeout on attempt {attempt+1}")
        except json.JSONDecodeError as e:
            logger.warning(f"    JSON parse error: {e}")
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate_limit" in error_str.lower():
                logger.warning(f"    Rate limited, backing off...")
                continue
            logger.error(f"    LLM call error: {error_str[:120]}")
            break
            
    return {p: "API ERROR: Max retries exceeded" for p in parameters}

async def research_with_llm(llm, company_name: str, parameters_to_fetch: List[str]) -> Dict[str, Any]:
    """Run sequential batched parameter querying across parameters."""
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

# ---------------------------------------------------------------------------
# Node Implementations
# ---------------------------------------------------------------------------

async def start_node(state: AgentState) -> AgentState:
    """1. Start Node: Entrypoint for the workflow execution."""
    logger.info("🎬 --- START NODE ---")
    return state

async def entry_node(state: AgentState) -> AgentState:
    """2. Entry/Input Node: Accepts user input and initializes data profile states."""
    logger.info("📥 --- ENTRY NODE ---")
    company_name = state.get("company_name", "Siemens AG")
    return {
        "company_name": company_name,
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
        "failed_parameters": []
    }

async def groq_generate(state: AgentState) -> AgentState:
    """3a. Parallel Branch 1: Groq LLM Execution"""
    logger.info("🧠 --- PARALLEL LLM BRANCH 1: GROQ ---")
    company_name = state["company_name"]
    result = await research_with_llm(llm_branch_1, company_name, PARAMETER_KEYS)
    return {"groq_data": result}

async def github_generate(state: AgentState) -> AgentState:
    """3b. Parallel Branch 2: GitHub LLM Execution"""
    logger.info("🧠 --- PARALLEL LLM BRANCH 2: GITHUB ---")
    company_name = state["company_name"]
    # Brief stagger to spread API limit window
    await asyncio.sleep(2)
    result = await research_with_llm(llm_branch_2, company_name, PARAMETER_KEYS)
    return {"github_data": result}

async def sambanova_generate(state: AgentState) -> AgentState:
    """3c. Parallel Branch 3: SambaNova LLM Execution"""
    logger.info("🧠 --- PARALLEL LLM BRANCH 3: SAMBANOVA ---")
    company_name = state["company_name"]
    # Brief stagger to spread API limit window
    await asyncio.sleep(4)
    result = await research_with_llm(llm_branch_3, company_name, PARAMETER_KEYS)
    return {"sambanova_data": result}

async def consolidation_node(state: AgentState) -> AgentState:
    """4. Parameter Consolidation: Merge 489 parameter outputs into 163 golden values."""
    logger.info("🤝 --- PARAMETER CONSOLIDATION NODE ---")
    company_name = state["company_name"]
    
    groq_data = state.get("groq_data", {})
    github_data = state.get("github_data", {})
    sambanova_data = state.get("sambanova_data", {})
    
    # 489 parameters input structure
    validation_results = {}
    for param in PARAMETER_KEYS:
        validation_results[param] = [
            {"llm_name": "branch_1", "value": groq_data.get(param)},
            {"llm_name": "branch_2", "value": github_data.get(param)},
            {"llm_name": "branch_3", "value": sambanova_data.get(param)}
        ]
        
    consolidated_data = {}
    new_failures = []
    
    consolidation_batch_size = 25
    total_batches = (len(PARAMETER_KEYS) + consolidation_batch_size - 1) // consolidation_batch_size
    
    for batch_idx, i in enumerate(range(0, len(PARAMETER_KEYS), consolidation_batch_size)):
        batch_params = PARAMETER_KEYS[i:i+consolidation_batch_size]
        batch_validation = {p: validation_results[p] for p in batch_params}
        
        prompt = CONSOLIDATION_PROMPT.format(
            company_name=company_name,
            validation_results=json.dumps(batch_validation, indent=2)
        )
        
        golden_batch = {}
        batch_success = False
        
        # Consolidation fallback model execution
        for attempt in range(MAX_RETRIES_PER_BATCH):
            if attempt > 0:
                await asyncio.sleep(2.0 * attempt)
            
            for llm_idx, current_llm in enumerate(CONSOLIDATION_FALLBACKS):
                try:
                    logger.info(f"  Consolidation batch {batch_idx+1}/{total_batches} - LLM #{llm_idx+1}")
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
                except Exception as e:
                    logger.warning(f"  Consolidation attempt error: {str(e)[:120]}")
            
            if batch_success:
                break
                
        if not batch_success:
            logger.error(f"  All consolidation attempts failed for batch {batch_idx+1}")
            for p in batch_params:
                consolidated_data[p] = "Not Found"
                new_failures.append(p)
            continue
            
        for p in batch_params:
            val = golden_batch.get(p)
            if val is None or str(val).strip().lower() in ["not found", "null", "none", ""]:
                consolidated_data[p] = "Not Found"
                new_failures.append(p)
            else:
                consolidated_data[p] = val
                
    logger.info(f"Consolidation completed successfully! {len(PARAMETER_KEYS) - len(new_failures)}/163 parameters matched.")
    return {
        "golden_record": consolidated_data,
        "failed_parameters": new_failures
    }

async def final_output_node(state: AgentState) -> AgentState:
    """5. Final Output Node: display and save verified profile logs."""
    logger.info("🏁 --- FINAL OUTPUT NODE ---")
    company_name = state["company_name"]
    golden_record = state.get("golden_record", {})
    
    # Sanitize Windows illegal file characters
    safe_name = re.sub(r'[\\/:*?"<>|]', '_', company_name)
    safe_name = safe_name.replace(" ", "_")
    safe_name = re.sub(r'_+', '_', safe_name).strip("_").lower()
    
    # Save as JSON output
    json_filename = f"{safe_name}_golden_record.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(golden_record, f, indent=4)
        
    logger.info(f"JSON record saved to {json_filename}")
    
    # Verification Profile Log
    good_params = sum(1 for k in PARAMETER_KEYS if k in golden_record and str(golden_record[k]).lower() not in ["not found", "null", "none", ""])
    logger.info("=" * 60)
    logger.info("🛡️ LANGSMITH STUDIO FINAL METRICS CHECK")
    logger.info("=" * 60)
    logger.info(f"  Company Name              : {company_name}")
    logger.info(f"  Total Schema Parameters   : {len(PARAMETER_KEYS)}")
    logger.info(f"  Successfully Populated    : {good_params}")
    logger.info(f"  Unresolved / Not Found    : {len(PARAMETER_KEYS) - good_params}")
    logger.info("=" * 60)
    
    return state

# ---------------------------------------------------------------------------
# LangGraph Workflow Architecture Definition
# ---------------------------------------------------------------------------
workflow = StateGraph(AgentState)

# Register nodes
workflow.add_node("start_node", start_node)
workflow.add_node("entry_node", entry_node)
workflow.add_node("groq_generate", groq_generate)
workflow.add_node("github_generate", github_generate)
workflow.add_node("sambanova_generate", sambanova_generate)
workflow.add_node("consolidation_node", consolidation_node)
workflow.add_node("final_output_node", final_output_node)

# Construct strictly parallel connections
workflow.add_edge(START, "start_node")
workflow.add_edge("start_node", "entry_node")

# Parallel Execution split
workflow.add_edge("entry_node", "groq_generate")
workflow.add_edge("entry_node", "github_generate")
workflow.add_edge("entry_node", "sambanova_generate")

# Joining parallel nodes back into parameter consolidation
workflow.add_edge("groq_generate", "consolidation_node")
workflow.add_edge("github_generate", "consolidation_node")
workflow.add_edge("sambanova_generate", "consolidation_node")

# Routing to final output
workflow.add_edge("consolidation_node", "final_output_node")
workflow.add_edge("final_output_node", END)

# Compile the graph
graph = workflow.compile()
