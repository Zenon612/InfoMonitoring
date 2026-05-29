from __future__ import annotations

from pydantic import BaseModel


class RiskSchemaOut(BaseModel):
    legal_risk: str
    ban_risk: str
    audience_negative: str
    expiration_date: str

