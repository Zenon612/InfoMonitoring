from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_session
from app.schemas.monitor_response_schema import MonitorRunResponseSchema
from app.schemas.monitor_schema import MonitorRunRequestSchema
from app.workflows.monitor import run_monitor_for_geo
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/run",
    response_model=MonitorRunResponseSchema,
    summary="Запустить мониторинг для GEO",
    description="Запускает полный pipeline: парсинг новостей → LLM анализ → экспорт"
)
async def monitor_run(
    req: MonitorRunRequestSchema,
    session: AsyncSession = Depends(get_async_session)
):
    """Запускает мониторинг инфоповодов для указанного GEO."""
    try:
        result = await run_monitor_for_geo(
            session=session,
            geo_code=req.geo_code,
            lookback_days=req.lookback_days,
            limit_raw=req.limit_raw,
        )
        return result
    except ValueError as e:
        logger.warning(f"Validation error for geo_code={req.geo_code}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in monitor_run: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during monitoring"
        )


