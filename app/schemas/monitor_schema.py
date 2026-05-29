from __future__ import annotations

from pydantic import BaseModel, Field
import re


class MonitorRunRequestSchema(BaseModel):
    geo_code: str = Field(
        ...,
        description="Код страны (например: BR, NG, DE)",
        pattern="^[A-Z]{2}$",
        min_length=2,
        max_length=2
    )
    lookback_days: int = Field(
        default=7,
        ge=1,
        le=30,
        description="Количество дней для поиска новостей"
    )
    limit_raw: int = Field(
        default=20,
        ge=5,
        le=50,
        description="Максимальное количество raw новостей для обработки"
    )

    model_config = {"json_schema_extra": {
        "examples": [{
            "geo_code": "BR",
            "lookback_days": 7,
            "limit_raw": 20
        }]
    }}

