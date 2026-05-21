from fastapi import APIRouter, HTTPException
from typing import List

from app.models.api import GenerateRequest, RunResponse
from app.service import workflow_service
from app.exceptions import RunNotFoundError

router = APIRouter(prefix="/v1/agent", tags=["agent"])


@router.post("/generate", response_model=RunResponse, status_code=202)
async def generate(request: GenerateRequest) -> RunResponse:
    """
    Start a new research pipeline run for the given company.

    Returns immediately with `status=queued` and a `run_id` you can use
    to poll `/v1/agent/status/{run_id}`.
    """
    run = await workflow_service.start_run(request.company_name)
    return run


@router.get("/status", response_model=List[RunResponse])
async def list_runs() -> List[RunResponse]:
    """Return the status of all runs (most recent first, max 100)."""
    runs = await workflow_service.get_all_runs()
    return list(reversed(runs))


@router.get("/status/{run_id}", response_model=RunResponse)
async def get_run_status(run_id: str) -> RunResponse:
    """Return the current status of a specific run."""
    run = await workflow_service.get_run(run_id)
    if run is None:
        raise RunNotFoundError(run_id)
    return run
