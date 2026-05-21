import httpx
import asyncio
import time
import sys

API_BASE = "http://127.0.0.1:8000"

async def test_api():
    print(f"Testing Health Check at {API_BASE}/health...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        health_resp = await client.get(f"{API_BASE}/health")
        if health_resp.status_code != 200:
            print(f"Failed health check: {health_resp.text}")
            sys.exit(1)
        print("Health Check Passed:", health_resp.json())

        print("\nStarting pipeline for company: 'Smoketest API AG'...")
        gen_resp = await client.post(f"{API_BASE}/v1/agent/generate", json={"company_name": "Smoketest API AG"})
        if gen_resp.status_code != 202:
            print(f"Failed to start pipeline: {gen_resp.text}")
            sys.exit(1)
            
        data = gen_resp.json()
        run_id = data["run_id"]
        print(f"Pipeline started successfully! Run ID: {run_id}")

        print("\nPolling status...")
        while True:
            status_resp = await client.get(f"{API_BASE}/v1/agent/status/{run_id}")
            if status_resp.status_code != 200:
                print(f"Failed to get status: {status_resp.text}")
                sys.exit(1)
                
            status_data = status_resp.json()
            status = status_data["status"]
            progress = status_data["progress"]
            msg = status_data["message"]
            
            print(f"[{status.upper()}] Progress: {progress}% - {msg}")
            
            if status in ["completed", "failed"]:
                if status == "completed":
                    print("\n🎉 Smoke test completed successfully!")
                    # Check outputs
                    if status_data.get("output"):
                        print(f"Output has {len(status_data['output'])} keys.")
                    if status_data.get("failed_parameters"):
                        print(f"Failed parameters: {len(status_data['failed_parameters'])}")
                else:
                    print(f"\n❌ Pipeline failed: {status_data.get('error')}")
                break
                
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(test_api())
