from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_session
from app.schemas.feedback_schema import FeedbackRequestSchema
from app.services.feedback.service import upsert_feedback
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/feedback",
    summary="Фиксация результатов теста",
    description="Сохраняет результаты A/B теста для обучения модели"
)
async def feedback(
    req: FeedbackRequestSchema,
    session: AsyncSession = Depends(get_async_session)
):
    """Фиксирует результаты теста инфоповода для обучения алгоритма."""
    try:
        if req.conversion_rate is not None and not (0.0 <= req.conversion_rate <= 1.0):
            raise ValueError("conversion_rate должен быть между 0 и 1")
        
        await upsert_feedback(session=session, payload=req)
        logger.info(f"Feedback recorded: inforeason_id={req.inforeason_id}, status={req.status}")
        return {"ok": True}
    except ValueError as e:
        logger.warning(f"Validation error in feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in feedback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while recording feedback"
        )


