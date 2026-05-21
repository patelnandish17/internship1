import json
import logging
import re
from state import AgentState
from schema import SCHEMA_DATA

logger = logging.getLogger(__name__)

# Windows-illegal filename characters: \ / : * ? " < > |
_ILLEGAL_CHARS = re.compile(r'[\\/:*?"<>|]')

def sanitize_filename(name: str) -> str:
    """Strip Windows-illegal chars, replace spaces with underscores, collapse duplicates."""
    name = _ILLEGAL_CHARS.sub("_", name)   # replace illegal chars
    name = name.replace(" ", "_")           # spaces → underscores
    name = re.sub(r"_+", "_", name)         # collapse repeated underscores
    name = name.strip("_").lower()          # trim edges, lowercase
    return name

def excel(state: AgentState) -> AgentState:
    """Excel Node (Save Node)"""
    if not state.get("golden_record"):
        return {}
        
    logger.info("--- EXCEL NODE ---")
    company_name = state["company_name"]
    golden_record = state["golden_record"]
    
    safe_name = sanitize_filename(company_name)

    # Save as JSON
    json_filename = f"{safe_name}_golden_record.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(golden_record, f, indent=4)
        
    logger.info(f"JSON record saved to {json_filename}")
    
    # Generate Output Format: Markdown Table per user requirements
    md_lines = []
    md_lines.append(f"# Data Profile for {company_name}")
    md_lines.append("| ID | Category | A/C | Parameter | Research Output / Data |")
    md_lines.append("|---|---|---|---|---|")
    
    for item in SCHEMA_DATA:
        val = golden_record.get(item["parameter"], "Not Found")
        val = str(val).replace("\n", " ").replace("\r", " ")
        md_lines.append(f"| {item['id']} | {item['category']} | {item['ac']} | {item['parameter']} | {val} |")
        
    md_filename = f"{safe_name}_golden_record.md"
    with open(md_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
        
    logger.info(f"Markdown table successfully saved to {md_filename}")
    
    # Verification: count parameters
    from schema import PARAMETER_KEYS
    total = len(PARAMETER_KEYS)
    present = sum(1 for k in PARAMETER_KEYS if k in golden_record)
    not_found = sum(1 for k in PARAMETER_KEYS if str(golden_record.get(k, "")).lower() in ["not found", "null", "none", ""])
    api_errors = sum(1 for k in PARAMETER_KEYS if str(golden_record.get(k, "")).startswith("API ERROR"))
    good = present - not_found - api_errors
    
    logger.info(f"=== OUTPUT VERIFICATION ===")
    logger.info(f"  Total expected parameters: {total}")
    logger.info(f"  Parameters in golden_record: {present}")
    logger.info(f"  Successfully researched: {good}")
    logger.info(f"  'Not Found' values: {not_found}")
    logger.info(f"  'API ERROR' values: {api_errors}")
    logger.info(f"  Missing from record: {total - present}")
    
    return {"golden_record": golden_record}
