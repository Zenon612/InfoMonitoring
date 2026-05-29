from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class FeedbackRequestSchema(BaseModel):
    inforeason_id: int
    status: Literal["success", "fail"]
    conversion_rate: float | None = Field(None, ge=0.0)
    comment: str | None = None

