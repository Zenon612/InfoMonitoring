from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from app.schemas.llm import AngleSchema, HeadlineSchema, InforeasonSchema, RiskSchema

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GeneratedRelease:
    """Результат работы LLM pipeline со всеми этапами обработки."""
    inforeasons: list[InforeasonSchema]
    angles: list[AngleSchema]
    headlines: list[HeadlineSchema]
    risks: list[RiskSchema]
    top5: list[dict[str, Any]]
    urgent_titles: list[str]
    later_titles: list[str]


class LLMReleasePipeline:
    """
    Полный 5-этапный pipeline обработки новостей через LLM.
    
    Этапы:
    1. Фильтрация & классификация инфоповодов
    2. Генерация маркетинговых углов захода
    3. Генерация рекламных заголовков
    4. Оценка рисков для Top-5
    5. Формирование Top-5 рекомендаций
    
    Использует OpenAI Structured Outputs (JSON Schema) для типобезопасной генерации.
    """

    async def run(
        self,
        *,
        llm_client: Any,
        model: str,
        raw_items: list[dict[str, Any]],
        feedback_context: str | None = None,
    ) -> GeneratedRelease:
        """Запускает 5-этапный LLM pipeline."""
        logger.info(f"Starting LLM pipeline with {len(raw_items)} raw items")
        
        raw_for_prompt = [
            {
                "title": it.get("title"),
                "link": it.get("link"),
                "pubdate": it.get("pubdate"),
            }
            for it in raw_items
        ]

        # Stage 1: Inforeasons filtering & classification
        try:
            logger.debug("Stage 1: Filtering and classifying inforeasons")
            
            class InforeasonsOut(BaseModel):
                items: list[InforeasonSchema]

            prompt_1 = (
                "Ты — ассистент маркетинговой контент-команды. "
                "Выбери наиболее перспективные инфоповоды из списка и классифицируй их. "
                "Верни только JSON по схеме. "
                "Правила: "
                "- category строго из: экономика / политика / соцсети / селеба / скандал / банки-налоги / страхи\n"
                "- emotional_trigger строго из: деньги / кризис / возможность / страх / доверие\n"
                "- urgency строго из: срочно 24-48ч / неделя / более\n"
                "- описание 2-3 предложения на русском\n"
                "- title должен оставаться осмысленным и читабельным, можно переформулировать\n"
                "- верни 5-10 лучших инфоповодов\n\n"
                f"RAW_NEWS (json): {raw_for_prompt}\n\n"
                f"FEEDBACK_CONTEXT (может быть пустым): {feedback_context or ''}\n"
            )

            out_1 = await llm_client.generate_structured(
                model=model,
                schema=InforeasonsOut,
                prompt=prompt_1,
            )
            inforeasons = out_1.items
            logger.info(f"Stage 1 complete: {len(inforeasons)} inforeasons generated")
        except Exception as e:
            logger.error(f"Stage 1 failed: {e}", exc_info=True)
            raise RuntimeError(f"Failed to generate inforeasons: {e}") from e

        # Stage 2: Marketing angles generation
        try:
            logger.debug("Stage 2: Generating marketing angles")
            
            class AnglesOut(BaseModel):
                items: list[AngleSchema]

            inforeasons_for_prompt = [i.model_dump() for i in inforeasons]
            prompt_2 = (
                "Сгенерируй маркетинговые углы (angle -> offer) под выбранные инфоповоды. "
                "Верни только JSON по схеме. "
                "Учитывай: angle_text — формулировка угла захода, offer_connection — как логически связать с оффером, "
                "target_pain — конкретная боль аудитории.\n"
                "creative_type: новостной / эмоциональный / разоблачение / личная история\n"
                "priority: A/B/C\n"
                "Сделай 5-10 углов. "
                "priority: 1-2 самых сильных для теста пометь как A, дальше как B, остальные C.\n\n"
                f"INFO_REASONS (json): {inforeasons_for_prompt}\n"
                f"FEEDBACK_CONTEXT (может быть пустым): {feedback_context or ''}\n"
            )

            out_2 = await llm_client.generate_structured(
                model=model,
                schema=AnglesOut,
                prompt=prompt_2,
            )
            angles = out_2.items
            logger.info(f"Stage 2 complete: {len(angles)} angles generated")
        except Exception as e:
            logger.error(f"Stage 2 failed: {e}", exc_info=True)
            raise RuntimeError(f"Failed to generate angles: {e}") from e
        class HeadlinesOut(BaseModel):
            items: list[HeadlineSchema]

        # Чтобы связать заголовки с углами, включаем в промпт угол text.
        angles_for_prompt = [a.model_dump() for a in angles]
        prompt_3 = (
            "Сгенерируй рекламные заголовки под каждый угол. "
            "Верни только JSON по схеме.\n"
            "Требования: текст заголовка с FOMO/интригой, без запрещённых обещаний. "
            "format_type: вопрос / шок / цифра / цитата / интрига\n"
            "В output укажи char_count = длина текста в символах.\n"
            "Сгенерируй 10-20 заголовков (можно распределить равномерно между углами).\n\n"
            f"ANGLES (json): {angles_for_prompt}\n"
        )

        out_3 = await llm_client.generate_structured(
            model=model,
            schema=HeadlinesOut,
            prompt=prompt_3,
        )
        headlines = out_3.items

        # 4) Risks
        class RisksOut(BaseModel):
            items: list[RiskSchema]

        prompt_4 = (
            "Оцени риски для топ-инфоповодов и углов. "
            "Верни 3-5 объектов RiskSchema.\n"
            "legal_risk: юридические риски (цитирование/клэйм/обобщения)\n"
            "ban_risk: риск бана рекламной платформой (избегай персональных наездов, обещаний и т.п.)\n"
            "audience_negative: риск негатива аудитории\n"
            "expiration_date: срок протухания (например 1-3 недели)\n\n"
            f"INFO_REASONS (json): {[i.model_dump() for i in inforeasons]}\n"
            f"ANGLES (json): {[a.model_dump() for a in angles]}\n"
        )

        out_4 = await llm_client.generate_structured(
            model=model,
            schema=RisksOut,
            prompt=prompt_4,
        )
        risks = out_4.items

        # 5) Recommendations (top-5 + по 3 headline на идею)
        class RecommendationsOut(BaseModel):
            top5: list[dict[str, Any]]

        # Используем простую схему словаря (чтобы не зависеть от модели/валидации при первом шаге),
        # но сама генерация structured по json_schema.
        class RecommendationsOutStrict(BaseModel):
            top5: list[dict[str, Any]]

        prompt_5 = (
            "Сформируй top-5 рекомендаций к тесту по ТЗ. "
            "Каждая рекомендация должна содержать: "
            "- inforeason_title: title выбранного инфоповода\n"
            "- angle_text: текст угла\n"
            "- offer_connection: связь с оффером\n"
            "- why_top: почему это в топ-5 (свежесть/триггер/соответствие офферу)\n"
            "- headlines: ровно 3 заголовка под эту идею\n"
            "Верни только JSON.\n\n"
            f"INFO_REASONS (json): {[i.model_dump() for i in inforeasons]}\n"
            f"ANGLES (json): {[a.model_dump() for a in angles]}\n"
            f"HEADLINES (json): {[h.model_dump() for h in headlines]}\n"
        )

        out_5 = await llm_client.generate_structured(
            model=model,
            schema=RecommendationsOutStrict,
            prompt=prompt_5,
        )

        # Urgency summary (🔥/⏳) — детерминированно из urgency поля.
        # "срочно 24-48ч" => 🔥, "неделя/более" => ⏳.
        urgent_bag: list[InforeasonSchema] = [
            i for i in inforeasons if "24-48" in i.urgency or "срочно" in i.urgency
        ]
        later_bag: list[InforeasonSchema] = [
            i for i in inforeasons if i not in urgent_bag
        ]

        urgent_titles: list[str] = [i.title for i in urgent_bag]
        later_titles: list[str] = [i.title for i in later_bag]

        return GeneratedRelease(
            inforeasons=inforeasons,
            angles=angles,
            headlines=headlines,
            risks=risks,
            top5=out_5.top5,
            urgent_titles=urgent_titles,
            later_titles=later_titles,
        )



