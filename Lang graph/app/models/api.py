from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from app.models.golden_record import GoldenRecord

from pydantic import BaseModel, Field, field_validator


class GenerateRequest(BaseModel):
    company_name: str = Field(..., min_length=1, description="Name of the company to research")

    @field_validator("company_name")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class RunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RunResponse(BaseModel):
    run_id: str
    company_name: str
    status: RunStatus
    progress: int = Field(0, ge=0, le=100, description="Completion percentage 0–100")
    message: str = Field("", description="Human-readable stage description")
    created_at: datetime
    updated_at: datetime
    output: Optional[GoldenRecord] = Field(None, description="golden_record on completion")
    failed_parameters: Optional[List[str]] = Field(None, description="Parameters that failed even after consolidation")
    error: Optional[str] = Field(None, description="Error details when status=failed")
