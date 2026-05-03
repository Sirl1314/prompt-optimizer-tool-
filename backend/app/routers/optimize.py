from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..database import get_db
from ..schemas.prompt import (
    OptimizeRequest, OptimizeResponse,
    TokenEstimateRequest, TokenEstimateResponse,
)
from ..engine.pipeline import run_pipeline
from ..models.prompt import PromptRecord, OptimizationSession, PromptStatus
from ..models_adapter import load_custom_from_db
from ..utils.token_counter import estimate_tokens
from ..utils.exceptions import AppException

router = APIRouter(prefix="/api", tags=["optimize"])


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_prompt(req: OptimizeRequest, db: AsyncSession = Depends(get_db)):
    await load_custom_from_db(db)
    try:
        result = await run_pipeline(
            raw_prompt=req.prompt,
            force_domain=req.domain,
            model_name=req.model or "deepseek-chat",
            output_language=req.language or "auto",
        )
    except Exception as e:
        raise AppException(500, f"优化失败: {str(e)}")

    existing = await db.execute(
        select(PromptRecord).where(PromptRecord.raw_prompt == req.prompt)
    )
    record = existing.scalar_one_or_none()

    if record:
        record.optimized_prompt = result.optimized_text
        record.domain = result.domain
        record.source_model = result.model_used
        record.token_count_optimized = result.token_count_optimized
        record.status = PromptStatus.optimized

        max_ver = await db.execute(
            select(func.max(OptimizationSession.version)).where(
                OptimizationSession.prompt_id == record.id
            )
        )
        next_version = (max_ver.scalar() or 0) + 1
    else:
        record = PromptRecord(
            title=req.title or req.prompt[:50],
            raw_prompt=req.prompt,
            optimized_prompt=result.optimized_text,
            domain=result.domain,
            source_model=result.model_used,
            token_count_raw=result.token_count_raw,
            token_count_optimized=result.token_count_optimized,
            status=PromptStatus.optimized,
        )
        db.add(record)
        await db.flush()
        next_version = 1

    session = OptimizationSession(
        prompt_id=record.id,
        version=next_version,
        optimized_text=result.optimized_text,
        model_used=result.model_used,
        domain_strategy=result.domain,
        scores=result.scores.model_dump(),
        diff_html=result.diff_html,
        token_delta=result.token_saved,
    )
    db.add(session)
    await db.commit()

    return OptimizeResponse(data=result)


@router.post("/token-estimate", response_model=TokenEstimateResponse)
async def token_estimate(req: TokenEstimateRequest):
    result = estimate_tokens(req.prompt)
    return TokenEstimateResponse(data=result)
