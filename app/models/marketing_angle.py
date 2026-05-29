from sqlalchemy import ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.headline import Headline

class MarketingAngle(Base):
    __tablename__ = "marketing_angles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inforeason_id: Mapped[int] = mapped_column(Integer, ForeignKey("inforeasons.id"), index=True)

    angle_text: Mapped[str] = mapped_column(Text)
    offer_connection: Mapped[str] = mapped_column(Text)
    target_pain: Mapped[str] = mapped_column(Text)
    creative_type: Mapped[str] = mapped_column(String(64))
    priority: Mapped[str] = mapped_column(String(8))

    created_at: Mapped[str] = mapped_column(String, server_default=func.now())

    headlines: Mapped[list["Headline"]] = relationship(back_populates="angle", lazy="selectin")

