from schema import SCHEMA_DATA

def get_schema_table_md(parameters: list) -> str:
    """Build a compact markdown table containing only the schema definitions for the requested parameters."""
    md = "ID | Category | Description | Parameter | Content Type to Generate | Min | Max | A/C\n"
    md += "--- | --- | --- | --- | --- | --- | --- | ---\n"
    # Create lookup for fast lookup
    param_set = set(parameters)
    for item in SCHEMA_DATA:
        if item["parameter"] in param_set:
            md += f"{item['id']} | {item['category']} | {item['description']} | {item['parameter']} | {item['content_type']} | {item['min']} | {item['max']} | {item['ac']}\n"
    return md

RESEARCH_PROMPT = """# ROLE ASSIGNMENT 
You are an expert Corporate Intelligence Analyst and Data Researcher. Your task is to conduct comprehensive web research to generate a detailed data profile for a specific target company. 

# INPUT DATA 
**Target Company:** {company_name}

**Data Schema:**
{schema_table}

# LOGIC & FORMATTING RULES (CRITICAL) 
You must adhere to the following logic strictly for every row in the Data Schema requested in this batch:

1. **Research & Accuracy:** 
  - Search the web for current, accurate information. 
  - If exact data is unavailable, provide a professional **estimate** based on industry benchmarks or similar companies.  
  - Never leave a field blank. If absolutely no data or estimate is possible, write "Not Found". 

2. **Atomic vs. Composite Fields (Column "A/C"):** 
  - Check the "A/C" column in the schema for each ID. 
  - **IF ATOMIC:** The response must be a **single value**. Do not list multiple items. 
  - **IF COMPOSITE:** You must generate multiple values. 
    - Respect the "Min" and "Max" columns for quantity. 
    - **Format:** All values must be separated ONLY by a semicolon (e.g., `Value 1; Value 2; Value 3`).  
    - Do not use bullet points, numbering, or new lines within a cell. 

# TARGET PARAMETERS FOR THIS BATCH
You only need to research the following parameters for this prompt:
{parameters_list}

# OUTPUT FORMAT
Return the result as a valid JSON object mapping the exact parameter names requested to their researched values (following the Atomic/Composite formatting rules). Do not output a markdown table here; output pure JSON.
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
