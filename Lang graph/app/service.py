"""
app/service.py — WorkflowService: manages in-memory run state and drives the graph.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from collections import OrderedDict
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.models.api import RunResponse, RunStatus

logger = logging.getLogger(__name__)

# Maps node name → (progress %, human-readable message)
NODE_PROGRESS: Dict[str, tuple[int, str]] = {
    "entry":               (5,  "Initializing pipeline"),
    "groq_generate":       (20, "Groq / Llama researching"),
    "github_generate":     (20, "GitHub / GPT-4o researching"),
    "sambanova_generate":  (20, "SambaNova researching"),
    "groq_validate":       (40, "Validating Groq output"),
    "github_validate":     (40, "Validating GitHub output"),
    "sambanova_validate":  (40, "Validating SambaNova output"),
    "consolidate":         (80, "Consolidating golden record"),
    "excel":               (95, "Saving output files"),
}

MAX_RUNS_IN_MEMORY = 100


class WorkflowService:
    def __init__(self) -> None:
        # OrderedDict so we can evict oldest entry when over capacity
        self._runs: OrderedDict[str, RunResponse] = OrderedDict()
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def start_run(self, company_name: str) -> RunResponse:
        """Create a new run, fire-and-forget the execution, return RunResponse(queued)."""
        run_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        run = RunResponse(
            run_id=run_id,
            company_name=company_name,
            status=RunStatus.QUEUED,
            progress=0,
            message="Queued — waiting for pipeline slot",
            created_at=now,
            updated_at=now,
        )
        await self._store(run)

        initial_state = {"company_name": company_name}
        asyncio.create_task(self._execute_run(run_id, initial_state))
        return run

    async def get_run(self, run_id: str) -> Optional[RunResponse]:
        async with self._lock:
            return self._runs.get(run_id)

    async def get_all_runs(self) -> List[RunResponse]:
        async with self._lock:
            return list(self._runs.values())

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _store(self, run: RunResponse) -> None:
        async with self._lock:
            if run.run_id in self._runs:
                self._runs.move_to_end(run.run_id)
            self._runs[run.run_id] = run
            # Evict oldest if over capacity
            while len(self._runs) > MAX_RUNS_IN_MEMORY:
                self._runs.popitem(last=False)

    async def _update(self, run_id: str, **kwargs) -> None:
        async with self._lock:
            run = self._runs.get(run_id)
            if run is None:
                return
            updated = run.model_copy(update={"updated_at": datetime.now(timezone.utc), **kwargs})
            self._runs[run_id] = updated

    async def _execute_run(self, run_id: str, initial_state: dict) -> None:
        # Lazy import to avoid circular imports at module load time
        from app.graph import compiled_graph

        await self._update(run_id, status=RunStatus.RUNNING, progress=1, message="Starting pipeline")

        try:
            golden_record = None
            failed_params = None

            async for event in compiled_graph.astream(initial_state, stream_mode="updates"):
                for node_name, state_update in event.items():
                    progress, message = NODE_PROGRESS.get(node_name, (50, f"Executing {node_name}"))
                    logger.info(f"[run={run_id}] node={node_name} progress={progress}%")
                    
                    if isinstance(state_update, dict):
                        if "golden_record" in state_update and state_update["golden_record"]:
                            golden_record = state_update["golden_record"]
                        if "failed_parameters" in state_update and state_update["failed_parameters"]:
                            failed_params = state_update["failed_parameters"]
                            
                    await self._update(run_id, progress=progress, message=message)

            await self._update(
                run_id,
                status=RunStatus.COMPLETED,
                progress=100,
                message="Pipeline completed successfully",
                output=golden_record,
                failed_parameters=failed_params,
            )

        except Exception as exc:
            logger.exception(f"[run={run_id}] Pipeline failed: {exc}")
            await self._update(
                run_id,
                status=RunStatus.FAILED,
                message="Pipeline encountered an error",
                error=str(exc),
            )


# Singleton instance used by the FastAPI router
workflow_service = WorkflowService()
