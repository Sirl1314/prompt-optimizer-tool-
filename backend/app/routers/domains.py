from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.domain import DomainStrategy as DomainStrategyModel
from ..domains import registry
from ..domains.base import CustomDomainStrategy
from ..schemas.domain import DomainStrategySchema, DomainCreateRequest
from ..utils.exceptions import AppException

router = APIRouter(prefix="/api", tags=["domains"])

BUILTIN_DOMAINS = {
    "code_dev", "copywriting", "data_analysis", "marketing",
    "healthcare", "legal", "education", "ai_visual",
}


async def _load_custom_from_db(db: AsyncSession):
    """Load all custom domains from database and register them in the registry."""
    result = await db.execute(
        select(DomainStrategyModel).where(DomainStrategyModel.is_active == True)
    )
    for row in result.scalars().all():
        if row.domain_name in registry.get_domain_names():
            registry.unregister(row.domain_name)
        strategy = CustomDomainStrategy(
            domain_name=row.domain_name,
            display_name=row.display_name,
            template=row.template,
            role_instruction=row.role_instruction,
            rules=row.rules,
            scoring_weights=row.scoring_weights,
            db_id=row.id,
        )
        registry.register(strategy)


@router.get("/domains")
async def list_domains(db: AsyncSession = Depends(get_db)):
    await _load_custom_from_db(db)

    strategies = registry.list_all()
    data = []
    for i, s in enumerate(strategies):
        is_custom = isinstance(s, CustomDomainStrategy)
        data.append(DomainStrategySchema(
            id=s.db_id if is_custom and s.db_id else -(i + 1),
            domain_name=s.domain,
            display_name=s.display_name,
            template=s.template,
            role_instruction=s.role_instruction,
            rules=s.rules,
            scoring_weights=s.scoring_weights,
            is_active=True,
            version=1,
            is_custom=is_custom,
        ))
    return {"code": 0, "data": data, "message": "ok"}


@router.post("/domains")
async def create_domain(body: DomainCreateRequest, db: AsyncSession = Depends(get_db)):
    if body.domain_name in BUILTIN_DOMAINS:
        raise AppException(400, "不能使用内置领域名称，请换一个标识")
    existing = await db.execute(
        select(DomainStrategyModel).where(DomainStrategyModel.domain_name == body.domain_name)
    )
    if existing.scalar_one_or_none():
        raise AppException(400, f"领域 '{body.domain_name}' 已存在")

    model = DomainStrategyModel(
        domain_name=body.domain_name,
        display_name=body.display_name,
        template=body.template,
        role_instruction=body.role_instruction,
        rules=body.rules,
        scoring_weights=body.scoring_weights,
        is_active=True,
        version=1,
    )
    db.add(model)
    await db.commit()
    await db.refresh(model)

    strategy = CustomDomainStrategy(
        domain_name=model.domain_name,
        display_name=model.display_name,
        template=model.template,
        role_instruction=model.role_instruction,
        rules=model.rules,
        scoring_weights=model.scoring_weights,
        db_id=model.id,
    )
    registry.register(strategy)

    return {
        "code": 0,
        "data": DomainStrategySchema(
            id=model.id,
            domain_name=model.domain_name,
            display_name=model.display_name,
            template=model.template,
            role_instruction=model.role_instruction,
            rules=model.rules,
            scoring_weights=model.scoring_weights,
            is_active=model.is_active,
            version=model.version,
            is_custom=True,
        ),
        "message": "创建成功",
    }


@router.put("/domains/{domain_id}")
async def update_domain(domain_id: int, body: DomainCreateRequest, db: AsyncSession = Depends(get_db)):
    if domain_id < 0:
        raise AppException(400, "内置领域不可编辑")

    model = await db.get(DomainStrategyModel, domain_id)
    if not model:
        raise AppException(404, "领域未找到")

    model.display_name = body.display_name
    model.template = body.template
    model.role_instruction = body.role_instruction
    model.rules = body.rules
    model.scoring_weights = body.scoring_weights
    await db.commit()
    await db.refresh(model)

    registry.unregister(model.domain_name)
    strategy = CustomDomainStrategy(
        domain_name=model.domain_name,
        display_name=model.display_name,
        template=model.template,
        role_instruction=model.role_instruction,
        rules=model.rules,
        scoring_weights=model.scoring_weights,
        db_id=model.id,
    )
    registry.register(strategy)

    return {"code": 0, "data": None, "message": "更新成功"}


@router.delete("/domains/{domain_id}")
async def delete_domain(domain_id: int, db: AsyncSession = Depends(get_db)):
    if domain_id < 0:
        raise AppException(400, "内置领域不可删除")

    model = await db.get(DomainStrategyModel, domain_id)
    if not model:
        raise AppException(404, "领域未找到")

    registry.unregister(model.domain_name)
    await db.delete(model)
    await db.commit()

    return {"code": 0, "data": None, "message": "已删除"}
