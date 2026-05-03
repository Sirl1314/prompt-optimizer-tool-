from pydantic import BaseModel, Field
from typing import Optional


class ParsedInput(BaseModel):
    raw_text: str
    char_count: int
    word_count: int
    language: str = "zh"
    token_count: int = 0
    has_code_blocks: bool = False
    has_markdown: bool = False


class RedundancyMarker(BaseModel):
    text_segment: str
    reason: str
    suggestion: str


class AnalysisReport(BaseModel):
    has_role_definition: bool = False
    has_output_spec: bool = False
    has_context: bool = False
    has_constraints: bool = False
    structure_score: float = 0.0
    redundancy_markers: list[RedundancyMarker] = []
    missing_sections: list[str] = []


class DomainResult(BaseModel):
    domain: str
    confidence: float
    sub_domain: str = ""
    alternative_domains: list[str] = []


class ScoreDetail(BaseModel):
    score: float
    weight: float
    notes: str = ""


class ScoreReport(BaseModel):
    clarity: ScoreDetail
    structure: ScoreDetail
    redundancy: ScoreDetail
    role_setting: ScoreDetail
    output_spec: ScoreDetail
    total: float


class PipelineResult(BaseModel):
    original_text: str
    optimized_text: str
    domain: str
    domain_confidence: float
    scores: ScoreReport
    token_count_raw: int
    token_count_optimized: int
    token_saved: int
    diff_html: str
    model_used: str
    analysis_report: AnalysisReport
