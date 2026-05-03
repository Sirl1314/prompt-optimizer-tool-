from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.model_config import ModelConfig
from ..models_adapter import (
    list_adapters, get_adapter, register_custom, unregister_custom,
    load_custom_from_db, CustomAdapter, BUILTIN_MODELS,
)
from ..schemas.model_config import ModelConfigSchema, ModelCreateRequest, ModelTestRequest, ModelTestResponse
from ..utils.exceptions import AppException

router = APIRouter(prefix="/api", tags=["models"])


@router.get("/models")
async def list_models(db: AsyncSession = Depends(get_db)):
    await load_custom_from_db(db)
    adapters = list_adapters()
    data = []
    builtin_idx = 0
    for a in adapters:
        is_custom = a.get("is_custom", False)
        if is_custom:
            data.append(ModelConfigSchema(
                id=a["db_id"],
                model_name=a["model_name"],
                provider=a["provider"],
                api_endpoint="",
                max_tokens=4096,
                temperature=0.7,
                is_available=True,
                priority=0,
                is_custom=True,
            ))
        else:
            builtin_idx += 1
            data.append(ModelConfigSchema(
                id=-builtin_idx,
                model_name=a["model_name"],
                provider=a["provider"],
                api_endpoint="",
                max_tokens=4096,
                temperature=0.7,
                is_available=True,
                priority=0,
                is_custom=False,
            ))
    return {"code": 0, "data": data, "message": "ok"}


@router.post("/models")
async def create_model(body: ModelCreateRequest, db: AsyncSession = Depends(get_db)):
    if body.model_name in BUILTIN_MODELS:
        raise AppException(400, "不能使用内置模型名称，请换一个标识")

    existing = await db.execute(
        select(ModelConfig).where(ModelConfig.model_name == body.model_name)
    )
    if existing.scalar_one_or_none():
        raise AppException(400, f"模型 '{body.model_name}' 已存在")

    model = ModelConfig(
        model_name=body.model_name,
        provider=body.provider,
        api_endpoint=body.api_endpoint,
        api_key_ref=body.api_key,
        max_tokens=body.max_tokens,
        temperature=body.temperature,
        is_available=True,
        priority=0,
    )
    db.add(model)
    await db.commit()
    await db.refresh(model)

    adapter = CustomAdapter(
        model_name=model.model_name,
        provider=model.provider,
        api_endpoint=model.api_endpoint,
        api_key=model.api_key_ref,
        max_tokens=model.max_tokens,
        temperature=model.temperature,
        db_id=model.id,
    )
    register_custom(adapter)

    return {
        "code": 0,
        "data": ModelConfigSchema(
            id=model.id,
            model_name=model.model_name,
            provider=model.provider,
            api_endpoint=model.api_endpoint,
            max_tokens=model.max_tokens,
            temperature=model.temperature,
            is_available=model.is_available,
            priority=model.priority,
            is_custom=True,
        ),
        "message": "创建成功",
    }


@router.put("/models/{model_id}")
async def update_model(model_id: int, body: ModelCreateRequest, db: AsyncSession = Depends(get_db)):
    if model_id < 0:
        raise AppException(400, "内置模型不可编辑")

    model = await db.get(ModelConfig, model_id)
    if not model:
        raise AppException(404, "模型未找到")

    unregister_custom(model.model_name)

    model.provider = body.provider
    model.api_endpoint = body.api_endpoint
    if body.api_key:
        model.api_key_ref = body.api_key
    model.max_tokens = body.max_tokens
    model.temperature = body.temperature
    await db.commit()
    await db.refresh(model)

    adapter = CustomAdapter(
        model_name=model.model_name,
        provider=model.provider,
        api_endpoint=model.api_endpoint,
        api_key=model.api_key_ref,
        max_tokens=model.max_tokens,
        temperature=model.temperature,
        db_id=model.id,
    )
    register_custom(adapter)

    return {"code": 0, "data": None, "message": "更新成功"}


@router.delete("/models/{model_id}")
async def delete_model(model_id: int, db: AsyncSession = Depends(get_db)):
    if model_id < 0:
        raise AppException(400, "内置模型不可删除")

    model = await db.get(ModelConfig, model_id)
    if not model:
        raise AppException(404, "模型未找到")

    unregister_custom(model.model_name)
    await db.delete(model)
    await db.commit()

    return {"code": 0, "data": None, "message": "已删除"}


@router.post("/models/test", response_model=ModelTestResponse)
async def test_model(req: ModelTestRequest, db: AsyncSession = Depends(get_db)):
    await load_custom_from_db(db)
    try:
        adapter = get_adapter(req.model_name)
        ok = await adapter.test_connection()
        return ModelTestResponse(data={"available": ok, "model": req.model_name})
    except Exception as e:
        return ModelTestResponse(code=503, data={"available": False}, message=str(e))
