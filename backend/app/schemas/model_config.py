from pydantic import BaseModel, field_validator


class ModelConfigSchema(BaseModel):
    id: int
    model_name: str
    provider: str
    api_endpoint: str
    max_tokens: int
    temperature: float
    is_available: bool
    priority: int
    is_custom: bool = False


class ModelCreateRequest(BaseModel):
    model_name: str
    provider: str
    api_endpoint: str
    api_key: str
    max_tokens: int = 4096
    temperature: float = 0.7

    @field_validator("model_name")
    @classmethod
    def model_name_slug(cls, v: str) -> str:
        v = v.strip().lower().replace(" ", "-")
        if not v:
            raise ValueError("模型名称不能为空")
        return v

    @field_validator("api_endpoint")
    @classmethod
    def endpoint_valid(cls, v: str) -> str:
        if not v.startswith("http"):
            raise ValueError("API 端点必须以 http 开头")
        return v.rstrip("/")

    @field_validator("temperature")
    @classmethod
    def temp_range(cls, v: float) -> float:
        if v < 0 or v > 2:
            raise ValueError("temperature 必须在 0-2 之间")
        return v


class ModelTestRequest(BaseModel):
    model_name: str


class ModelTestResponse(BaseModel):
    code: int = 0
    data: dict
    message: str = "ok"
