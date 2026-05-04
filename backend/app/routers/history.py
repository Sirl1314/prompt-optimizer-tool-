from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models.prompt import PromptRecord, OptimizationSession
from ..schemas.prompt import HistoryItem, HistoryDetail, VersionItem
from ..utils.exceptions import AppException

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history")
async def list_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    domain: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    # 查询优化会话，关联 prompt record
    stmt = (
        select(OptimizationSession)
        .join(PromptRecord, OptimizationSession.prompt_id == PromptRecord.id)
        .order_by(desc(OptimizationSession.created_at))
    )
    if domain:
        stmt = stmt.where(PromptRecord.domain == domain)
    if search:
        stmt = stmt.where(
            (PromptRecord.title.contains(search)) |
            (PromptRecord.raw_prompt.contains(search))
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    rows = (await db.execute(stmt)).scalars().all()

    # 构建 HistoryItem
    items = []
    for session in rows:
        record = await db.get(PromptRecord, session.prompt_id)
        if record:
            items.append(HistoryItem(
                id=session.id,
                record_id=record.id,
                title=record.title,
                domain=record.domain,
                model_used=session.model_used,
                version=session.version,
                token_count_raw=record.token_count_raw,
                token_count_optimized=record.token_count_optimized,
                status=record.status.value,
                created_at=session.created_at,
            ))
    
    return {"code": 0, "data": {"items": items, "total": total, "page": page, "page_size": page_size}, "message": "ok"}


@router.get("/history/{record_id}")
async def get_history_detail(record_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(PromptRecord).where(PromptRecord.id == record_id).options(
        selectinload(PromptRecord.sessions)
    )
    result = (await db.execute(stmt)).scalar_one_or_none()
    if not result:
        raise AppException(404, "记录未找到")

    versions = [
        VersionItem.model_validate(s) for s in sorted(result.sessions, key=lambda s: s.version)
    ]
    detail = HistoryDetail(
        id=result.id,
        title=result.title,
        raw_prompt=result.raw_prompt,
        optimized_prompt=result.optimized_prompt,
        domain=result.domain,
        source_model=result.source_model,
        token_count_raw=result.token_count_raw,
        token_count_optimized=result.token_count_optimized,
        status=result.status.value,
        created_at=result.created_at,
        updated_at=result.updated_at,
        versions=versions,
    )
    return {"code": 0, "data": detail, "message": "ok"}


@router.delete("/history/{record_id}")
async def delete_history(record_id: str, db: AsyncSession = Depends(get_db)):
    # 先查找是 session 还是 record
    session = await db.get(OptimizationSession, record_id)
    if session:
        # 如果是 session，删除该 session
        await db.delete(session)
        await db.commit()
        return {"code": 0, "data": None, "message": "已删除"}
    
    # 如果是 record，删除整个记录及其所有 session
    stmt = select(PromptRecord).where(PromptRecord.id == record_id)
    result = (await db.execute(stmt)).scalar_one_or_none()
    if not result:
        raise AppException(404, "记录未找到")
    await db.delete(result)
    await db.commit()
    return {"code": 0, "data": None, "message": "已删除"}


@router.get("/history/{record_id}/versions")
async def list_versions(record_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(OptimizationSession).where(
        OptimizationSession.prompt_id == record_id
    ).order_by(OptimizationSession.version)
    rows = (await db.execute(stmt)).scalars().all()
    return {
        "code": 0,
        "data": [VersionItem.model_validate(r) for r in rows],
        "message": "ok",
    }
