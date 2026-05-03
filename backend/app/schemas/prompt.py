from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from .pipeline import PipelineResult


class OptimizeRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=20000)
    domain: Optional[str] = Field(default=None, description="auto-detect if empty")
    model: Optional[str] = Field(default=None, description="use default if empty")
    title: Optional[str] = None
    language: Optional[str] = Field(default=None, description="output language: zh/en/auto, auto-detect if empty")


class OptimizeResponse(BaseModel):
    code: int = 0
    data: Optional[PipelineResult] = None
    message: str = "ok"


class TokenEstimateRequest(BaseModel):
    prompt: str


class TokenEstimateResponse(BaseModel):
    code: int = 0
    data: dict
    message: str = "ok"


class HistoryItem(BaseModel):
    id: str
    title: str
    domain: str
    token_count_raw: int
    token_count_optimized: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VersionItem(BaseModel):
    id: str
    version: int
    optimized_text: str
    model_used: str
    domain_strategy: str
    scores: Optional[dict]
    diff_html: Optional[str]
    token_delta: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HistoryDetail(BaseModel):
    id: str
    title: str
    raw_prompt: str
    optimized_prompt: Optional[str]
    domain: str
    source_model: Optional[str]
    token_count_raw: int
    token_count_optimized: int
    status: str
    created_at: datetime
    updated_at: datetime
    versions: list[VersionItem] = []

    model_config = ConfigDict(from_attributes=True)


class CompareRequest(BaseModel):
    version_ids: list[str] = Field(..., min_length=2, max_length=5)
