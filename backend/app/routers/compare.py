from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models.prompt import OptimizationSession
from ..schemas.prompt import CompareRequest
from ..utils.diff import generate_diff_html
from ..utils.exceptions import AppException

router = APIRouter(prefix="/api", tags=["compare"])


@router.post("/compare")
async def compare_versions(req: CompareRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(OptimizationSession).where(OptimizationSession.id.in_(req.version_ids))
    rows = (await db.execute(stmt)).scalars().all()

    if len(rows) < 2:
        raise AppException(400, "至少需要 2 个版本才能进行对比")

    rows = sorted(rows, key=lambda r: r.version)

    comparisons = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            diff_html = generate_diff_html(rows[i].optimized_text, rows[j].optimized_text)
            comparisons.append({
                "version_a": rows[i].version,
                "version_b": rows[j].version,
                "text_a_preview": rows[i].optimized_text[:500],
                "text_b_preview": rows[j].optimized_text[:500],
                "diff_html": diff_html,
            })

    return {
        "code": 0,
        "data": {
            "versions": [
                {"id": r.id, "version": r.version, "model_used": r.model_used}
                for r in rows
            ],
            "comparisons": comparisons,
        },
        "message": "ok",
    }
