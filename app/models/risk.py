from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Risk(Base):
    __tablename__ = "risks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Риски считаются по топ-инфоповодам.
    inforeason_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inforeasons.id"), index=True
    )

    # Текстовые поля для 4 типов риска из ТЗ
    legal_risk: Mapped[str] = mapped_column(Text)
    ban_risk: Mapped[str] = mapped_column(Text)
    audience_negative: Mapped[str] = mapped_column(Text)
    expiration_date: Mapped[str] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


