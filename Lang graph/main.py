import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END

from state import AgentState
from nodes.entry import entry_node
from nodes.research import groq_generate, github_generate, sambanova_generate
from nodes.validation import groq_validate, github_validate, sambanova_validate
from nodes.consolidation import consolidation_node
from nodes.routing import route_groq, route_github, route_sambanova, route_consolidate
from nodes.excel import excel
from schema import PARAMETER_KEYS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def build_graph():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("entry", entry_node)
    
    workflow.add_node("groq_generate", groq_generate)
    workflow.add_node("github_generate", github_generate)
    workflow.add_node("sambanova_generate", sambanova_generate)
    
    workflow.add_node("groq_validate", groq_validate)
    workflow.add_node("github_validate", github_validate)
    workflow.add_node("sambanova_validate", sambanova_validate)
    
    workflow.add_node("consolidate", consolidation_node)
    workflow.add_node("excel", excel)

    # Add edges
    workflow.add_edge(START, "entry")
    
    # Fan out from entry to parallel generators
    workflow.add_edge("entry", "groq_generate")
    workflow.add_edge("entry", "github_generate")
    workflow.add_edge("entry", "sambanova_generate")
    
    # Generator to Validator edges
    workflow.add_edge("groq_generate", "groq_validate")
    workflow.add_edge("github_generate", "github_validate")
    workflow.add_edge("sambanova_generate", "sambanova_validate")
    
    # Validator conditional edges (cycle back or to consolidate)
    workflow.add_conditional_edges(
        "groq_validate",
        route_groq,
        {
            "groq_generate": "groq_generate",
            "consolidate": "consolidate"
        }
    )
    
    workflow.add_conditional_edges(
        "github_validate",
        route_github,
        {
            "github_generate": "github_generate",
            "consolidate": "consolidate"
        }
    )
    
    workflow.add_conditional_edges(
        "sambanova_validate",
        route_sambanova,
        {
            "sambanova_generate": "sambanova_generate",
            "consolidate": "consolidate"
        }
    )
    
    # Consolidate conditional edge
    workflow.add_conditional_edges(
        "consolidate",
        route_consolidate,
        {
            "excel": "excel",
            "__end__": END
        }
    )
    workflow.add_edge("excel", END)

    return workflow.compile()

# Create the global graph instance required for LangGraph Studio
graph = build_graph()

if __name__ == "__main__":
    async def run_pipeline():
        company_name = "Siemens"
        initial_state = {"company_name": company_name}
        
        logger.info(f"Starting Multi-Agent Pipeline for {company_name}...")
        logger.info(f"Total parameters to generate: {len(PARAMETER_KEYS)}")
        
        final_state = None
        try:
            async for event in graph.astream(initial_state):
                for node_name, state_update in event.items():
                    logger.info(f"Completed node: {node_name}")
                    # Keep track of golden_record if present
                    if isinstance(state_update, dict) and "golden_record" in state_update:
                        final_state = state_update
                    
            logger.info("=" * 60)
            logger.info("PIPELINE EXECUTION COMPLETE")
            logger.info("=" * 60)
            
            if final_state and final_state.get("golden_record"):
                gr = final_state["golden_record"]
                from schema import PARAMETER_KEYS as ALL_PARAMS
                present = [p for p in ALL_PARAMS if p in gr]
                missing = [p for p in ALL_PARAMS if p not in gr]
                errors = [p for p in present if str(gr.get(p, "")).startswith("API ERROR")]
                not_found = [p for p in present if str(gr.get(p, "")).lower() in ["not found", "null", "none", ""]]
                
                logger.info(f"Parameters in golden_record: {len(present)}/{len(ALL_PARAMS)}")
                logger.info(f"Successfully researched: {len(present) - len(errors) - len(not_found)}")
                logger.info(f"Not Found: {len(not_found)}")
                logger.info(f"API Errors: {len(errors)}")
                logger.info(f"Missing entirely: {len(missing)}")
                if missing:
                    logger.warning(f"Missing parameters: {missing[:10]}{'...' if len(missing) > 10 else ''}")
            else:
                logger.warning("No golden_record found in final state!")
                
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
        
    asyncio.run(run_pipeline())
