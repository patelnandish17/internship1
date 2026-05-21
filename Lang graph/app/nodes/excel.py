import json
import logging
import os
import re

from app.models.state import AgentState
from app.config.settings import settings
from schema import SCHEMA_DATA

logger = logging.getLogger(__name__)

_ILLEGAL_CHARS = re.compile(r'[\\/:*?"<>|]')


def sanitize_filename(name: str) -> str:
    """Strip Windows-illegal chars, replace spaces with underscores, collapse duplicates."""
    name = _ILLEGAL_CHARS.sub("_", name)
    name = name.replace(" ", "_")
    name = re.sub(r"_+", "_", name)
    return name.strip("_").lower()


def excel(state: AgentState) -> AgentState:
    """Excel/Save Node — persists golden_record as JSON + Markdown table."""
    if not state.get("golden_record"):
        return {}

    logger.info("--- EXCEL NODE ---")
    company_name = state["company_name"]
    golden_record = state["golden_record"]
    safe_name = sanitize_filename(company_name)

    output_dir = settings.output_dir
    os.makedirs(output_dir, exist_ok=True)

    # Save JSON
    json_path = os.path.join(output_dir, f"{safe_name}_golden_record.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(golden_record, f, indent=4)
    logger.info(f"JSON record saved to {json_path}")

    # Save Markdown table
    md_lines = [
        f"# Data Profile for {company_name}",
        "| ID | Category | A/C | Parameter | Research Output / Data |",
        "|---|---|---|---|---|",
    ]
    for item in SCHEMA_DATA:
        val = golden_record.get(item["parameter"], "Not Found")
        val = str(val).replace("\n", " ").replace("\r", " ")
        md_lines.append(
            f"| {item['id']} | {item['category']} | {item['ac']} | {item['parameter']} | {val} |"
        )

    md_path = os.path.join(output_dir, f"{safe_name}_golden_record.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    logger.info(f"Markdown table saved to {md_path}")

    return state
