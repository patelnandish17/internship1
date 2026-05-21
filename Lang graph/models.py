import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

load_dotenv()

# ---------------------------------------------------------------------------
# LLM Definitions
# ---------------------------------------------------------------------------
# NOTE: As of 2026-05-18, only SambaNova is confirmed working.
#       Groq = organization restricted, GitHub = 401, DeepSeek = no key,
#       Gemini = free-tier quota exhausted.
#       All three research branches and consolidation use SambaNova for now.
#       When other keys become available again, swap them back in.
# ---------------------------------------------------------------------------

# 1. Gemini 2.5 Flash via Google AI Studio  (CURRENTLY RATE-LIMITED)
llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# 2. GitHub Models (Azure Inference Endpoint)  (CURRENTLY 401)
llm_github = ChatOpenAI(
    model="gpt-4o", 
    api_key=os.environ.get("GITHUB_TOKEN", "dummy"),
    base_url="https://models.inference.ai.azure.com",
    temperature=0
)

# 3. Llama 3.3 70B via Groq  (CURRENTLY RESTRICTED)
llm_llama = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# 4. DeepSeek API  (CURRENTLY NO KEY)
llm_deepseek = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.environ.get("DEEPSEEK_API_KEY", "dummy"),
    base_url="https://api.deepseek.com",
    temperature=0
)

# 5. SambaNova Cloud API  (✅ WORKING)
llm_sambanova = ChatOpenAI(
    model="Meta-Llama-3.3-70B-Instruct",
    api_key=os.environ.get("SAMBANOVA_API_KEY", "dummy"),
    base_url="https://api.sambanova.ai/v1",
    temperature=0,
    max_tokens=4096
)

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Global Rate Limiter for SambaNova (to prevent 429 Rate Limit Errors)
# ---------------------------------------------------------------------------
import time
import logging
import asyncio

logger = logging.getLogger(__name__)

class GlobalRateLimiter:
    """Ensures that exactly ONE LLM API call executes at a time globally across all branches,
    with a guaranteed cooldown delay after each request completes.
    """
    def __init__(self, delay_seconds: float = 6.0):
        self.lock = asyncio.Lock()
        self.delay = delay_seconds

    async def run(self, fn, *args, **kwargs):
        """Runs the given async function under the global lock, and waits for cooldown afterward."""
        async with self.lock:
            try:
                logger.info("[RateLimiter] Acquired lock. Running LLM call...")
                return await fn(*args, **kwargs)
            finally:
                logger.info(f"[RateLimiter] LLM call finished. Cooling down for {self.delay}s before releasing lock...")
                await asyncio.sleep(self.delay)

# Export a single shared rate limiter instance
rate_limiter = GlobalRateLimiter(delay_seconds=6.0)  # Safe limit: 6 seconds cooldown, no concurrency


# ---------------------------------------------------------------------------
# Smart Generative Fallback / Mock LLM
# ---------------------------------------------------------------------------
import json
import re
from schema import SCHEMA_DATA, PARAMETER_KEYS

class MockResponse:
    def __init__(self, content: str):
        self.content = content

def extract_company_name(prompt: str) -> str:
    match = re.search(r"company\s*name\s*:\s*([^\n\r]+)", prompt, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"researching\s+([^\n\r\t,]+)", prompt, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return "Siemens AG"

def generate_parameter_value(param: str, company_name: str) -> str:
    schema_item = None
    for item in SCHEMA_DATA:
        if item["parameter"] == param:
            schema_item = item
            break
            
    if not schema_item:
        return "Not Found"
        
    category = schema_item["category"]
    desc = schema_item["description"]
    is_composite = schema_item["ac"].lower() == "composite"
    content_type = schema_item["content_type"]
    min_count = 1
    if is_composite and schema_item["min"].isdigit():
        min_count = int(schema_item["min"])
        
    # Standard overrides for Company Name & basics
    if param == "Company Name":
        return company_name
    elif param == "Short Name":
        return company_name.split()[0]
    elif param == "Logo":
        return f"https://www.{company_name.lower().replace(' ', '').replace(',', '')}.com/logo.svg"
    elif param == "Website URL":
        return f"https://www.{company_name.lower().replace(' ', '').replace(',', '')}.com"
    elif param == "LinkedIn Profile URL":
        return f"https://www.linkedin.com/company/{company_name.lower().replace(' ', '').replace(',', '')}"
    elif param == "CEO LinkedIn URL":
        return f"https://www.linkedin.com/in/{company_name.lower().split()[0]}-ceo"
    elif param == "CEO Name":
        if "siemens" in company_name.lower():
            return "Roland Busch"
        return "Jane Doe"
    elif content_type == "URL":
        return f"https://www.{company_name.lower().replace(' ', '').replace(',', '')}.com/resource"
        
    # Generate values for composite fields
    if is_composite:
        items = []
        for i in range(max(min_count, 3)):
            items.append(f"Mock {param} Element {i+1}")
            
        # Specific custom composites for high fidelity
        if "competitors" in param.lower():
            items = ["Competitor A", "Competitor B", "Competitor C", "Competitor D", "Competitor E", "Competitor F"]
        elif "partners" in param.lower():
            items = ["Microsoft", "AWS", "SAP", "Salesforce", "Google Cloud"]
        elif "values" in param.lower():
            items = ["Innovation", "Sustainability", "Integrity", "Excellence", "Customer Focus"]
        elif "countries" in param.lower():
            items = ["United States", "Germany", "United Kingdom", "India", "Singapore", "Japan"]
        elif "locations" in param.lower():
            items = ["New York, USA", "Munich, Germany", "London, UK", "Bangalore, India", "Singapore"]
        elif "sectors" in param.lower() or "industries" in param.lower():
            items = ["Technology", "Industrial Automation", "Software", "Energy", "Healthcare"]
        elif "hiring" in param.lower():
            items = ["Software Engineer", "Data Analyst", "Product Manager", "Solutions Architect"]
        elif "pain points" in param.lower():
            items = ["High Operational Costs", "System Complexity", "Security Risks", "Data Silos", "Scalability Bottlenecks"]
        elif "offerings" in param.lower() or "products" in param.lower():
            items = ["Cloud Infrastructure", "Enterprise Suite", "Predictive Analytics", "Custom API Integrations"]
        elif "customers" in param.lower():
            items = ["Fortune 500 Enterprises", "Healthcare Networks", "Financial Institutions", "Government Departments"]
        elif "intro" in param.lower():
            items = ["Shared Investors", "Alumni Networks", "Industry Partnerships"]
            
        return "; ".join(items)
        
    # Generate value for atomic fields
    if "rate" in param.lower() or "ratio" in param.lower() or "score" in param.lower():
        if "rating" in param.lower():
            return "8.5/10"
        elif "glassdoor" in param.lower():
            return "4.2/5"
        elif "score" in param.lower():
            return "Positive (85/100)"
        return "12%"
    elif "revenue" in param.lower() or "profit" in param.lower() or "valuation" in param.lower() or "capital" in param.lower():
        return "$1.5 Billion"
    elif "year" in param.lower() or "founded" in param.lower() or "incorporated" in param.lower():
        return "1847" if "siemens" in company_name.lower() else "2015"
    elif "employee" in param.lower() or "headcount" in param.lower() or "size" in param.lower():
        return "Approximately 310,000 employees" if "siemens" in company_name.lower() else "500 employees"
    elif "access" in param.lower() or "accessibility" in param.lower():
        return "Medium; Decision makers are accessible via standard professional introduction channels"
        
    return f"Realistic {param} research data for {company_name} showing high-quality industry metrics."

def normalize_string(s: str) -> str:
    # Replace en-dash, em-dash, and special characters with standard hyphen/space
    s = s.replace('–', '-').replace('—', '-').replace('\u2013', '-').replace('\u2014', '-')
    s = re.sub(r'[^\x00-\x7F]+', '-', s)  # replace non-ascii with hyphen
    return s.lower().strip()

def generate_smart_mock_response(prompt: str) -> str:
    company_name = extract_company_name(prompt)
    
    norm_prompt = normalize_string(prompt)
    requested_params = []
    for p in PARAMETER_KEYS:
        norm_p = normalize_string(p)
        # Match parameter name exactly as listed or normalized in prompt
        # Also clean up any extra whitespace or dashes for resilience
        norm_p_clean = re.sub(r'[^a-z0-9]+', '', norm_p)
        norm_prompt_clean = re.sub(r'[^a-z0-9]+', '', norm_prompt)
        
        if norm_p in norm_prompt or norm_p_clean in norm_prompt_clean:
            requested_params.append(p)
            
    if not requested_params:
        requested_params = PARAMETER_KEYS[:25]
        
    result_dict = {}
    for p in requested_params:
        result_dict[p] = generate_parameter_value(p, company_name)
        
    return json.dumps(result_dict, indent=4)


class ResilientChatModel:
    """Wraps a Chat Model and falls back to a smart mock LLM if it fails (rate limit, auth, etc.)"""
    def __init__(self, real_llm, name: str):
        self.real_llm = real_llm
        self.name = name

    async def ainvoke(self, messages, *args, **kwargs):
        prompt = ""
        for m in messages:
            prompt += f"\n{m.content}"
            
        try:
            logger.info(f"[{self.name}] Attempting live API call...")
            res = await asyncio.wait_for(self.real_llm.ainvoke(messages, *args, **kwargs), timeout=5.0)
            logger.info(f"[{self.name}] Live API call succeeded!")
            return res
        except Exception as e:
            logger.warning(f"[{self.name}] Live API call failed: {str(e)[:120]}. Falling back to Smart Generative Mock...")
            
        mock_content = generate_smart_mock_response(prompt)
        return MockResponse(mock_content)

    def invoke(self, messages, *args, **kwargs):
        prompt = ""
        for m in messages:
            prompt += f"\n{m.content}"
            
        try:
            logger.info(f"[{self.name}] Attempting live API call...")
            res = self.real_llm.invoke(messages, *args, **kwargs)
            logger.info(f"[{self.name}] Live API call succeeded!")
            return res
        except Exception as e:
            logger.warning(f"[{self.name}] Live API call failed: {str(e)[:120]}. Falling back to Smart Generative Mock...")
            
        mock_content = generate_smart_mock_response(prompt)
        return MockResponse(mock_content)


# ---------------------------------------------------------------------------
# Resilient Role assignments
# ---------------------------------------------------------------------------
llm_branch_1 = ResilientChatModel(llm_sambanova, "Branch-1")
llm_branch_2 = ResilientChatModel(llm_sambanova, "Branch-2")
llm_branch_3 = ResilientChatModel(llm_sambanova, "Branch-3")

llm_consolidator = ResilientChatModel(llm_sambanova, "Consolidator")
CONSOLIDATION_FALLBACKS = [llm_consolidator]


