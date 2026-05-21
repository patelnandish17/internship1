import json
import logging
import pandas as pd
from state import AgentState
from schema import SCHEMA_DATA

logger = logging.getLogger(__name__)

def save_node(state: AgentState) -> AgentState:
    """Phase 6: Save Node (Markdown Table / JSON)"""
    logger.info("--- PHASE 6: SAVE NODE ---")
    company_name = state["company_name"]
    golden_record = state["golden_record"]
    
    # Save as JSON
    json_filename = f"{company_name.replace(' ', '_').lower()}_golden_record.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(golden_record, f, indent=4)
        
    logger.info(f"JSON record saved to {json_filename}")
    
    # Generate Output Format: Markdown Table per user requirements
    # Columns required: ID, Category, A/C, Parameter, Research Output / Data
    md_lines = []
    md_lines.append(f"# Data Profile for {company_name}")
    md_lines.append("| ID | Category | A/C | Parameter | Research Output / Data |")
    md_lines.append("|---|---|---|---|---|")
    
    for item in SCHEMA_DATA:
        val = golden_record.get(item["parameter"], "Not Found")
        # Ensure single line for table compatibility
        val = str(val).replace("\n", " ").replace("\r", " ")
        md_lines.append(f"| {item['id']} | {item['category']} | {item['ac']} | {item['parameter']} | {val} |")
        
    md_filename = f"{company_name.replace(' ', '_').lower()}_golden_record.md"
    with open(md_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
        
    logger.info(f"Markdown table successfully saved to {md_filename}")
    return state
