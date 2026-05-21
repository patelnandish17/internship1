"""
app/main.py — FastAPI application entry point.

Start with:
    uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations

import logging
import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.exceptions import (
    RunNotFoundError,
    GraphExecutionError,
    ProviderError,
    PipelineTimeoutError,
    run_not_found_handler,
    graph_execution_handler,
    provider_error_handler,
    timeout_handler,
    generic_exception_handler,
)
from app.middleware.logging import TimingMiddleware
from app.routes.agent import router as agent_router

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("app")


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀  FastAPI server starting up (version %s)", settings.api_version)
    yield
    logger.info("🛑  FastAPI server shutting down")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


app = FastAPI(
    title="LangGraph Company Research API",
    description=(
        "Multi-agent pipeline that researches companies across 163 parameters "
        "using Groq, GitHub/GPT-4o, and SambaNova in parallel."
    ),
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing
app.add_middleware(TimingMiddleware)

# Exception handlers
app.add_exception_handler(RunNotFoundError, run_not_found_handler)
app.add_exception_handler(GraphExecutionError, graph_execution_handler)
app.add_exception_handler(ProviderError, provider_error_handler)
app.add_exception_handler(PipelineTimeoutError, timeout_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Routers
app.include_router(agent_router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "version": settings.api_version}
