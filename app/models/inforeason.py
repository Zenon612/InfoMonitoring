from sqlalchemy import Date, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Inforeason(Base):
    __tablename__ = "inforeasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    geo_id: Mapped[int] = mapped_column(Integer, index=True)

    title: Mapped[str] = mapped_column(String(500))
    source_url: Mapped[str] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(64), default="google_news_rss")

    date: Mapped[Date] = mapped_column(Date)
    category: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text)

    emotional_trigger: Mapped[str] = mapped_column(String(64))
    urgency: Mapped[str] = mapped_column(String(64))

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

