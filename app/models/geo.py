from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Geo(Base):
    __tablename__ = "geos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(16))
    keywords: Mapped[str] = mapped_column(Text)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

