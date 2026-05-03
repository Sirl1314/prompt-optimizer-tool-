from pydantic import BaseModel, field_validator
from typing import Optional


class DomainStrategySchema(BaseModel):
    id: int
    domain_name: str
    display_name: str
    template: dict
    role_instruction: str
    rules: list
    scoring_weights: dict
    is_active: bool
    version: int
    is_custom: bool = False


class DomainCreateRequest(BaseModel):
    domain_name: str
    display_name: str
    template: dict[str, str]
    role_instruction: str
    rules: list[dict]
    scoring_weights: dict[str, float]

    @field_validator("domain_name")
    @classmethod
    def domain_name_slug(cls, v: str) -> str:
        import re
        v = v.strip().lower().replace(" ", "_")
        if not re.match(r"^[a-z0-9_]+$", v):
            raise ValueError("领域标识只能包含小写字母、数字和下划线")
        return v

    @field_validator("scoring_weights")
    @classmethod
    def weights_sum_to_one(cls, v: dict[str, float]) -> dict[str, float]:
        total = sum(v.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"评分权重之和必须为 1.0，当前为 {total:.2f}")
        return v

    @field_validator("template")
    @classmethod
    def template_not_empty(cls, v: dict[str, str]) -> dict[str, str]:
        if not v:
            raise ValueError("模板至少需要一个章节")
        return v

    @field_validator("rules")
    @classmethod
    def rules_not_empty(cls, v: list[dict]) -> list[dict]:
        if not v:
            raise ValueError("至少需要一条优化规则")
        for i, rule in enumerate(v):
            if "name" not in rule:
                raise ValueError(f"第 {i + 1} 条规则缺少 name 字段")
        return v


class DomainUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    template: Optional[dict] = None
    role_instruction: Optional[str] = None
    rules: Optional[list] = None
    scoring_weights: Optional[dict] = None
    is_active: Optional[bool] = None
