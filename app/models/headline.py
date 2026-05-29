from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.marketing_angle import MarketingAngle

class Headline(Base):
    __tablename__ = "headlines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    angle_id: Mapped[int] = mapped_column(Integer, ForeignKey("marketing_angles.id"), index=True)

    text: Mapped[str] = mapped_column(Text)
    format_type: Mapped[str] = mapped_column(String(64))
    char_count: Mapped[int] = mapped_column(Integer)

    angle: Mapped["MarketingAngle"] = relationship(back_populates="headlines", lazy="selectin")

