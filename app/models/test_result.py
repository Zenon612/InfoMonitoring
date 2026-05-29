from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TestResult(Base):
    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inforeason_id: Mapped[int] = mapped_column(Integer, ForeignKey("inforeasons.id"), index=True)

    conversion_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(16))
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

