from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_result import TestResult


async def upsert_feedback(session: AsyncSession, payload) -> None:
    result = await session.execute(
        select(TestResult).where(TestResult.inforeason_id == payload.inforeason_id).order_by(TestResult.id.desc())
    )
    existing = result.scalars().first()

    if existing is None:
        session.add(
            TestResult(
                inforeason_id=payload.inforeason_id,
                status=payload.status,
                conversion_rate=payload.conversion_rate,
                comment=payload.comment,
            )
        )
    else:
        existing.status = payload.status
        existing.conversion_rate = payload.conversion_rate
        existing.comment = payload.comment

    await session.commit()

