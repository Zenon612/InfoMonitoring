from typing import Literal

from pydantic import BaseModel, Field


class InforeasonSchema(BaseModel):
    title: str = Field(..., description="Заголовок инфоповода")
    category: str = Field(
        ...,
        description="экономика / политика / соцсети / селеба / скандал / банки-налоги / страхи",
    )
    description: str = Field(..., description="Краткое описание в 2-3 предложения")
    emotional_trigger: str = Field(..., description="деньги / кризис / возможность / страх / доверие")
    urgency: str = Field(..., description="срочно 24-48ч / неделя / более")


class AngleSchema(BaseModel):
    angle_text: str = Field(..., description="Формулировка угла захода")
    offer_connection: str = Field(..., description="Как связать с оффером")
    target_pain: str = Field(..., description="Целевая боль аудитории")
    creative_type: str = Field(..., description="новостной / эмоциональный / разоблачение / личная история")
    priority: Literal["A", "B", "C"]


class HeadlineSchema(BaseModel):
    text: str = Field(..., description="Продающий заголовок")
    format_type: Literal["вопрос", "шок", "цифра", "цитата", "интрига"]
    char_count: int




class RiskSchema(BaseModel):
    legal_risk: str
    ban_risk: str = Field(..., description="Риск бана платформой")
    audience_negative: str
    expiration_date: str

