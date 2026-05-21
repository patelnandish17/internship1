import os
import json
import asyncio
import logging
from typing import TypedDict, List, Dict, Any

from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

# Load env variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
MAX_RETRIES = 3
TOTAL_PARAMETERS = 163
BATCH_SIZE = 20 # Number of parameters to ask per prompt to avoid API rate limits and context truncation
CONCURRENCY_LIMIT = 3 # Number of concurrent batches per LLM

# Mock 163 parameters (e.g., param_1, param_2, ..., param_163)
PARAMETER_KEYS = [f"param_{i}" for i in range(1, TOTAL_PARAMETERS + 1)]

# Mock dynamic validation ruleset (to be replaced with actual rules)
VALIDATION_RULES = {
    f"param_{i}": {"type": "string", "required": True} for i in range(1, TOTAL_PARAMETERS + 1)
}

# --- STATE DEFINITION ---
class AgentState(TypedDict):
    company_name: str
    research_data: List[Dict[str, Any]]           # List of 3 dicts (one per LLM), each with parameter keys
    validation_results: Dict[str, List[Dict[str, Any]]] # Keyed by param, holds list of candidate validation statuses
    golden_record: Dict[str, Any]                 # Final consolidated exactly 163 parameters
    failed_parameters: List[str]                  # Parameters needing regeneration
    retry_count: int                              # Tracks regeneration loops

# --- MODELS INITIALIZATION ---
# 1. Gemini 2.5 Flash via Google AI Studio
llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# 2. Grok 3 via GitHub Models (Azure Inference Endpoint)
llm_grok = ChatOpenAI(
    model="grok-3", # Ensure this model name matches the exact deployment name on GitHub Models
    api_key=os.environ.get("GITHUB_TOKEN"),
    base_url="https://models.inference.ai.azure.com",
    temperature=0
)

# 3. Llama 3.3 70B via Groq
llm_llama = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# Consolidation Agent (using Gemini for fast JSON consolidation)
llm_consolidator = llm_gemini

# --- PROMPTS ---
RESEARCH_PROMPT = """You are a highly capable OSINT research agent. 
Target Company: {company_name}

Your task is to find the values for the following parameters:
{parameters_list}

CRUCIAL CONSTRAINTS:
1. ONLY return data if you are absolutely certain.
2. If the data is unavailable or you cannot find it, you MUST return `null` or "Not Found".
3. DO NOT hallucinate, guess, or invent fake data under any circumstances.

Output your response as a valid JSON object mapping the parameter names to their extracted values. Do not output anything else.
"""

CONSOLIDATION_PROMPT = """You are a master data consolidator.
Target Company: {company_name}

You have received 3 candidate values for several parameters from 3 different independent researchers.
You also have the validation status for each candidate.

Here is the data:
{validation_results}

Your task:
For each parameter, select a single unified "Golden" value based on:
1. Rule Compliance (only pick PASSed candidates if available)
2. Accuracy and Data Freshness
3. If all candidates are "Not Found" or fail validation, return `null`.

Output a single valid JSON object mapping each parameter to its Golden Record value. Do not output anything else.
"""

# --- HELPER FUNCTIONS ---
async def fetch_parameters_batch(llm, company_name: str, parameters: List[str], semaphore: asyncio.Semaphore) -> Dict[str, Any]:
    """Fetch a specific batch of parameters using the provided LLM."""
    async with semaphore:
        prompt = RESEARCH_PROMPT.format(
            company_name=company_name,
            parameters_list=", ".join(parameters)
        )
        
        try:
            response = await llm.ainvoke([
                SystemMessage(content="You always respond in valid JSON format only."), 
                HumanMessage(content=prompt)
            ])
            
            content = response.content
            # Cleanup potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content.strip())
        except Exception as e:
            logger.error(f"Error fetching batch with LLM: {e}")
            # Fallback to 'Not Found' to prevent pipeline crash
            return {p: "Not Found" for p in parameters}

async def research_with_llm(llm, company_name: str, parameters_to_fetch: List[str]) -> Dict[str, Any]:
    """Chunks parameters and fetches them concurrently for a single LLM to prevent rate limits."""
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    tasks = []
    
    # Split parameters into batches
    for i in range(0, len(parameters_to_fetch), BATCH_SIZE):
        batch = parameters_to_fetch[i:i+BATCH_SIZE]
        tasks.append(fetch_parameters_batch(llm, company_name, batch, semaphore))
    
    # Gather all batches concurrently for this LLM
    results = await asyncio.gather(*tasks)
    
    # Merge dictionary batches
    merged_result = {}
    for res in results:
        merged_result.update(res)
        
    return merged_result

# --- PHASE FUNCTIONS (NODES) ---

async def entry_node(state: AgentState) -> AgentState:
    """Phase 1: User Input (Entry Node)"""
    logger.info("--- PHASE 1: ENTRY NODE ---")
    return {
        "company_name": state["company_name"],
        "research_data": [],
        "validation_results": {},
        "golden_record": {},
        "failed_parameters": state.get("failed_parameters", []),
        "retry_count": state.get("retry_count", 0)
    }

async def research_node(state: AgentState) -> AgentState:
    """Phase 2: Research Agent (Generation Node)"""
    logger.info("--- PHASE 2: RESEARCH AGENT ---")
    company_name = state["company_name"]
    failed_params = state.get("failed_parameters", [])
    
    # If no specific failures exist, fetch all 163 parameters
    params_to_fetch = failed_params if failed_params else PARAMETER_KEYS
    logger.info(f"Fetching {len(params_to_fetch)} parameters. Current Retry Count: {state.get('retry_count', 0)}")
    
    # Execute the 3 LLMs in parallel
    tasks = [
        research_with_llm(llm_gemini, company_name, params_to_fetch),
        research_with_llm(llm_grok, company_name, params_to_fetch),
        research_with_llm(llm_llama, company_name, params_to_fetch)
    ]
    
    llm_results = await asyncio.gather(*tasks)
    
    # Merge new results with existing research_data (important for retries)
    current_data = state.get("research_data", [])
    if not current_data or len(current_data) != 3:
        current_data = [{}, {}, {}]
        
    for i in range(3):
        current_data[i].update(llm_results[i])
        
    return {"research_data": current_data}

def validation_node(state: AgentState) -> AgentState:
    """Phase 3: Validation Suite (Tool Layer Node)"""
    logger.info("--- PHASE 3: VALIDATION SUITE ---")
    research_data = state["research_data"]
    validation_results = {}
    
    # Evaluate the 3 candidate values for each parameter across the 163 fields
    for param in PARAMETER_KEYS:
        candidates = []
        for i, data in enumerate(research_data):
            value = data.get(param)
            
            # Programmatic Rule Validation (Mock)
            # In production, VALIDATION_RULES dictionary logic applies here
            is_valid = True
            if value is None or str(value).lower() in ["not found", "null", "none", ""]:
                is_valid = False
            
            candidates.append({
                "llm_id": i + 1,
                "value": value,
                "status": "PASS" if is_valid else "FAIL"
            })
            
        validation_results[param] = candidates

    return {"validation_results": validation_results}

async def consolidation_node(state: AgentState) -> AgentState:
    """Phase 4: Consolidation Agent (LLM Node)"""
    logger.info("--- PHASE 4: CONSOLIDATION AGENT ---")
    company_name = state["company_name"]
    validation_results = state["validation_results"]
    failed_parameters = state.get("failed_parameters", [])
    
    # Consolidate parameters that were just fetched/retried, or all if it's the first run
    params_to_consolidate = failed_parameters if failed_parameters else PARAMETER_KEYS
    
    consolidated_data = state.get("golden_record", {})
    new_failures = []
    
    # Consolidating in batches to avoid massive prompts for the consolidation LLM
    consolidation_batch_size = 50
    for i in range(0, len(params_to_consolidate), consolidation_batch_size):
        batch_params = params_to_consolidate[i:i+consolidation_batch_size]
        batch_validation = {p: validation_results[p] for p in batch_params}
        
        prompt = CONSOLIDATION_PROMPT.format(
            company_name=company_name,
            validation_results=json.dumps(batch_validation, indent=2)
        )
        
        try:
            response = await llm_consolidator.ainvoke([
                SystemMessage(content="You always respond in valid JSON format only."), 
                HumanMessage(content=prompt)
            ])
            
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            golden_batch = json.loads(content.strip())
            
            # Check completeness to determine if regeneration is needed
            for p in batch_params:
                val = golden_batch.get(p)
                if val is None or str(val).lower() in ["not found", "null"]:
                    new_failures.append(p)
                else:
                    consolidated_data[p] = val
                    
        except Exception as e:
            logger.error(f"Consolidation error: {e}")
            new_failures.extend(batch_params)
            
    return {
        "golden_record": consolidated_data,
        "failed_parameters": new_failures
    }

def route_after_consolidation(state: AgentState) -> str:
    """Phase 5: Routing Logic"""
    logger.info("--- PHASE 5: CONDITIONAL ROUTING ---")
    failed_parameters = state.get("failed_parameters", [])
    retry_count = state.get("retry_count", 0)
    
    logger.info(f"Failed parameters needing regeneration: {len(failed_parameters)} / {TOTAL_PARAMETERS}")
    
    if len(failed_parameters) > 0 and retry_count < MAX_RETRIES:
        logger.info(f"Initiating regeneration loop. Retry Count will be incremented to {retry_count + 1}.")
        return "increment_retry"
    
    if len(failed_parameters) > 0:
        logger.warning("Max retries reached. Some parameters could not be found.")
    
    logger.info("Routing to SAVE_NODE...")
    return "save_node"

def increment_retry(state: AgentState) -> AgentState:
    """Helper node to increment retry count before routing back to research."""
    return {"retry_count": state.get("retry_count", 0) + 1}

def save_node(state: AgentState) -> AgentState:
    """Phase 6: JSON Save Node"""
    logger.info("--- PHASE 6: JSON SAVE NODE ---")
    company_name = state["company_name"]
    golden_record = state["golden_record"]
    
    filename = f"{company_name.replace(' ', '_').lower()}_golden_record.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(golden_record, f, indent=4)
        
    logger.info(f"Successfully saved {len(golden_record)} parameters to {filename}")
    return state

# --- GRAPH COMPILATION ---
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("entry_node", entry_node)
workflow.add_node("research_agent", research_node)
workflow.add_node("validation_suite", validation_node)
workflow.add_node("consolidation_agent", consolidation_node)
workflow.add_node("increment_retry", increment_retry)
workflow.add_node("save_node", save_node)

# Add Edges (Sequential Flow)
workflow.add_edge(START, "entry_node")
workflow.add_edge("entry_node", "research_agent")
workflow.add_edge("research_agent", "validation_suite")
workflow.add_edge("validation_suite", "consolidation_agent")

# Add Conditional Edges (Regeneration Loop)
workflow.add_conditional_edges(
    "consolidation_agent",
    route_after_consolidation,
    {
        "increment_retry": "increment_retry",
        "save_node": "save_node"
    }
)

# Complete the loop
workflow.add_edge("increment_retry", "research_agent")
workflow.add_edge("save_node", END)

# Compile Graph
app = workflow.compile()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    async def run_pipeline():
        company_name = input("Enter the target company name: ")
        initial_state = {"company_name": company_name}
        
        logger.info(f"Starting Multi-Agent Pipeline for {company_name}...")
        
        try:
            # Stream events to see progression
            async for event in app.astream(initial_state):
                for node_name, state_update in event.items():
                    logger.info(f"Completed execution of node: {node_name}")
                    
            logger.info("Pipeline Execution Complete.")
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
        
    # Execute the event loop
    asyncio.run(run_pipeline())
