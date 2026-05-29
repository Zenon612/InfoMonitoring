from __future__ import annotations


from pydantic import BaseModel, Field


class RecommendationIdeaOut(BaseModel):
    # Идея в ТЗ = связка «инфоповод → угол → оффер»,
    # но в текущей архитектуре у нас есть только inforeason/angle/headline.
    # Поэтому храним ссылки/тексты и обоснование.
    inforeason_title: str = Field(..., description="Название инфоповода")
    angle_text: str = Field(..., description="Текст угла")
    offer_connection: str = Field(..., description="Как связывается с оффером")

    # Обоснование топ-выбора
    why_top: str = Field(..., description="Почему это в топ-5 (свежесть/триггер/соответствие офферу)")

    # 3 лучших заголовка под эту идею
    headlines: list[str] = Field(..., description="Ровно 3 заголовка")


class RecommendationsOut(BaseModel):
    # Рекомендации к тесту по ТЗ: топ-5 идей
    top5: list[RecommendationIdeaOut]

