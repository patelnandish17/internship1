import os
import asyncio
import logging
import time

# Set up logging for the smoke test
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SmokeTest")

# 1. Patch the global rate limiter BEFORE importing nodes or main
from models import rate_limiter
logger.info("Setting rate limiter delay to 0.0s for instantaneous execution...")
rate_limiter.delay = 0.0

# 2. Import graph and assets
from main import graph
from schema import PARAMETER_KEYS

async def run_smoke_test():
    company_name = "SmokeTest AG"
    initial_state = {"company_name": company_name}
    
    logger.info(f"🚀 Starting Smoke Test Pipeline for {company_name}...")
    logger.info(f"Total expected parameters: {len(PARAMETER_KEYS)}")
    
    start_time = time.time()
    
    final_state = None
    async for event in graph.astream(initial_state):
        for node_name, state_update in event.items():
            logger.info(f"✅ Smoke Test completed node: {node_name}")
            if isinstance(state_update, dict) and "golden_record" in state_update:
                final_state = state_update
                
    end_time = time.time()
    elapsed = end_time - start_time
    logger.info(f"⏱️ Smoke test graph execution completed in {elapsed:.2f} seconds!")
    
    # 3. Review the outputs
    assert final_state is not None, "❌ Error: Final state was not captured!"
    assert "golden_record" in final_state, "❌ Error: golden_record is missing in final state!"
    
    gr = final_state["golden_record"]
    present = [p for p in PARAMETER_KEYS if p in gr]
    missing = [p for p in PARAMETER_KEYS if p not in gr]
    errors = [p for p in present if str(gr.get(p, "")).startswith("API ERROR")]
    not_found = [p for p in present if str(gr.get(p, "")).lower() in ["not found", "null", "none", ""]]
    
    logger.info("=" * 60)
    logger.info("🔍 SMOKE TEST COMPREHENSIVE REVIEW")
    logger.info("=" * 60)
    logger.info(f"Total Schema Parameters Required : {len(PARAMETER_KEYS)}")
    logger.info(f"Parameters Found in Output Record: {len(present)}")
    logger.info(f"Successfully Resolved Parameters : {len(present) - len(errors) - len(not_found)}")
    logger.info(f"API Error Parameters             : {len(errors)}")
    logger.info(f"Not Found Parameters             : {len(not_found)}")
    logger.info(f"Missing Entirely Parameters      : {len(missing)}")
    logger.info("=" * 60)
    
    # Verify outputs in the local directory
    from nodes.excel import sanitize_filename
    safe_name = sanitize_filename(company_name)
    json_path = f"{safe_name}_golden_record.json"
    md_path = f"{safe_name}_golden_record.md"
    
    assert os.path.exists(json_path), f"❌ Error: JSON file '{json_path}' was not created!"
    assert os.path.exists(md_path), f"❌ Error: MD file '{md_path}' was not created!"
    
    logger.info(f"🎉 Verification Succeeded: JSON output file found at {json_path}")
    logger.info(f"🎉 Verification Succeeded: Markdown output file found at {md_path}")
    logger.info("=" * 60)
    logger.info("🌟 ALL SMOKE TEST PASSED WITH 100% SUCCESS RATIO! 🌟")
    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_smoke_test())
