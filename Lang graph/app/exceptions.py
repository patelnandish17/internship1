from fastapi import Request
from fastapi.responses import JSONResponse


# ---------------------------------------------------------------------------
# Custom exception classes
# ---------------------------------------------------------------------------


class RunNotFoundError(Exception):
    """Raised when a run_id does not exist in the in-memory store."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        super().__init__(f"Run '{run_id}' not found")


class GraphExecutionError(Exception):
    """Raised when the LangGraph pipeline raises an unhandled exception."""

    def __init__(self, run_id: str, detail: str):
        self.run_id = run_id
        self.detail = detail
        super().__init__(f"Graph execution error for run '{run_id}': {detail}")


class ProviderError(Exception):
    """Raised when an LLM provider is unreachable or rate-limited."""

    def __init__(self, provider: str, detail: str):
        self.provider = provider
        self.detail = detail
        super().__init__(f"Provider '{provider}' error: {detail}")


class PipelineTimeoutError(Exception):
    """Raised when a run exceeds the configured maximum duration."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        super().__init__(f"Run '{run_id}' timed out")


# ---------------------------------------------------------------------------
# FastAPI exception handlers — registered in app/main.py
# ---------------------------------------------------------------------------


async def run_not_found_handler(request: Request, exc: RunNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc), "run_id": exc.run_id},
    )


async def graph_execution_handler(request: Request, exc: GraphExecutionError) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": exc.detail, "run_id": exc.run_id},
    )


async def provider_error_handler(request: Request, exc: ProviderError) -> JSONResponse:
    return JSONResponse(
        status_code=502,
        content={"detail": exc.detail, "provider": exc.provider},
    )


async def timeout_handler(request: Request, exc: PipelineTimeoutError) -> JSONResponse:
    return JSONResponse(
        status_code=504,
        content={"detail": "Pipeline timed out", "run_id": exc.run_id},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal error occurred. Check server logs."},
    )
