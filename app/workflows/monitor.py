from __future__ import annotations

import logging
import os
from datetime import date
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.models.geo import Geo
from app.models.headline import Headline
from app.models.inforeason import Inforeason
from app.models.marketing_angle import MarketingAngle
from app.models.test_result import TestResult

from app.services.llm.client import LLMClient
from app.services.llm.pipeline import LLMReleasePipeline
from app.services.parser.google_news_rss import build_rss_url, fetch_google_news_rss

logger = logging.getLogger(__name__)


async def run_monitor_for_geo(
    *,
    session: AsyncSession,
    geo_code: str,
    lookback_days: int,
    limit_raw: int,
) -> dict[str, Any]:
    """
    Запускает полный pipeline мониторинга для указанного GEO.
    
    Pipeline:
    1. Парсит свежие новости из Google News RSS
    2. Фильтрует и классифицирует инфоповоды через LLM
    3. Генерирует маркетинговые углы захода
    4. Генерирует рекламные заголовки
    5. Оценивает риски
    6. Формирует Top-5 рекомендаций
    7. Сохраняет результаты в БД и генерирует Markdown отчёт
    
    Args:
        session: AsyncSession для БД операций
        geo_code: Код страны (например 'BR', 'NG')
        lookback_days: Количество дней для поиска новостей (1-30)
        limit_raw: Максимум raw новостей для обработки (5-50)
    
    Returns:
        dict с ключами: release_id, markdown_path, geo_code, raw_inforeasons_saved
    
    Raises:
        ValueError: Если GEO не найден в БД
        Exception: Если ошибка при парсинге или LLM запросе
    """
    logger.info(f"Starting monitor for geo_code={geo_code}, lookback_days={lookback_days}")
    
    geo_res = await session.execute(select(Geo).where(Geo.code == geo_code))
    geo = geo_res.scalars().first()
    if geo is None:
        logger.error(f"Geo not found for code={geo_code}")
        raise ValueError(
            f"Geo not found for code={geo_code}. "
            "Please add GEO to geos table first (or run init_db)."
        )
    
    logger.debug(f"Found geo: {geo.name} ({geo.code})")

    rss_url = build_rss_url(
        keywords=geo.keywords or "technology", # костыли
        lookback_days=lookback_days,
        hl=geo.language or "en",
        gl=geo.code,
    )
    logger.debug(f"Built RSS URL for {geo.code}")

    try:
        raw_items = await fetch_google_news_rss(rss_url=rss_url, limit=limit_raw)
        logger.info(f"Fetched {len(raw_items)} raw news items for {geo.code}")
    except Exception as e:
        logger.error(f"Failed to fetch news from RSS: {e}", exc_info=True)
        raise

    llm_client = LLMClient()
    pipeline = LLMReleasePipeline()

    raw_for_llm = [
        {"title": it.title, "link": it.link, "pubdate": it.pubdate.isoformat()}
        for it in raw_items
    ]

    recent_test_rows = await session.execute(
        select(
            TestResult.inforeason_id,
            TestResult.status,
            TestResult.conversion_rate,
            TestResult.comment,
        )
        .join(Inforeason, TestResult.inforeason_id == Inforeason.id)
        .where(Inforeason.geo_id == geo.id)
        .order_by(TestResult.updated_at.desc())
        .limit(30)
    )
    recent_tests = recent_test_rows.all()

    feedback_context_lines: list[str] = []
    for row in recent_tests:
        m = getattr(row, "_mapping", None) or {}
        inforeason_id = m.get("inforeason_id") or row[0]
        status = m.get("status") or row[1]
        conversion_rate = m.get("conversion_rate") or row[2]
        comment = m.get("comment") or row[3]
        feedback_context_lines.append(
            f"inforeason_id={inforeason_id}; status={status}; conversion_rate={conversion_rate}; comment={comment}"
        )

    feedback_context = "\n".join(feedback_context_lines) if feedback_context_lines else None

    generated = await pipeline.run(
        llm_client=llm_client,
        model=settings.OPENAI_MODEL,
        raw_items=raw_for_llm,
        feedback_context=feedback_context,
    )


    # Persist: inforeasons + angles + headlines + risks.

    saved_inforeasons = 0
    inforeason_models: list[Inforeason] = []

    for idx, info in enumerate(generated.inforeasons):
        src = (
            raw_items[idx]
            if idx < len(raw_items)
            else (raw_items[0] if raw_items else None)
        )
        if src is None:
            break

        inforeason = Inforeason(
            geo_id=geo.id,
            title=info.title,
            source_url=src.link,
            source_type="google_news_rss",
            date=src.pubdate.date(),
            category=info.category,
            description=info.description,
            emotional_trigger=info.emotional_trigger,
            urgency=info.urgency,
        )
        session.add(inforeason)
        await session.flush()

        inforeason_models.append(inforeason)
        saved_inforeasons += 1

    angle_models: list[MarketingAngle] = []
    for idx, angle in enumerate(generated.angles):
        parent = (
            inforeason_models[idx % len(inforeason_models)]
            if inforeason_models
            else None
        )
        if parent is None:
            continue

        mangle = MarketingAngle(
            inforeason_id=parent.id,
            angle_text=angle.angle_text,
            offer_connection=angle.offer_connection,
            target_pain=angle.target_pain,
            creative_type=angle.creative_type,
            priority=angle.priority,
        )
        session.add(mangle)
        await session.flush()
        angle_models.append(mangle)

    for idx, h in enumerate(generated.headlines):
        parent_angle = (
            angle_models[idx % len(angle_models)] if angle_models else None
        )
        if parent_angle is None:
            continue

        headline = Headline(
            angle_id=parent_angle.id,
            text=h.text,
            format_type=h.format_type,
            char_count=h.char_count,
        )
        session.add(headline)
        await session.flush()

    await session.commit()

    # Markdown release
    release_id = str(uuid4())
    out_dir = os.path.join(os.getcwd(), os.getenv("OUTPUT_DIR", "outputs"))
    os.makedirs(out_dir, exist_ok=True)
    markdown_path = os.path.join(out_dir, f"release_{geo_code}_{release_id}.md")

    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write("# AI-мониторинг инфоповодов и генерация маркетинговых связок\n\n")
        f.write(f"- GEO: {geo.name} ({geo.code})\n")
        f.write(f"- Дата генерации: {date.today().isoformat()}\n")
        f.write(f"- Период покрытия: последние {lookback_days} дней\n\n")

        # Block 1: Таблица сырых инфоповодов
        f.write("## 1) Блок 1. Сырые инфоповоды (Inforeasons)\n\n")
        f.write("| # | Заголовок | Источник | Дата | Категория | Триггер | Срочность | Описание |\n")
        f.write("|---|-----------|----------|------|-----------|---------|-----------|----------|\n")
        for idx, info in enumerate(generated.inforeasons, start=1):
            src = (
                raw_items[idx - 1]
                if idx - 1 < len(raw_items)
                else (raw_items[0] if raw_items else None)
            )
            source_link = f"[Ссылка]({src.link})" if src else "N/A"
            pub_date = src.pubdate.date().isoformat() if src else "N/A"
            # Escaping pipe characters in description
            desc_escaped = info.description.replace("|", "\\|")[:100]
            f.write(
                f"| {idx} | {info.title} | {source_link} | {pub_date} | {info.category} | "
                f"{info.emotional_trigger} | {info.urgency} | {desc_escaped}... |\n"
            )
        f.write("\n")

        # Block 2
        f.write("## 2) Блок 2. Углы и идеи\n\n")
        for idx, a in enumerate(generated.angles, start=1):
            f.write(
                f"### Идея #{idx}\n"
                f"- Угол: {a.angle_text}\n"
                f"- Связь с оффером: {a.offer_connection}\n"
                f"- Боль аудитории: {a.target_pain}\n"
                f"- Тип креатива: {a.creative_type}\n"
                f"- Приоритет: {a.priority}\n\n"
            )

        # Block 3
        f.write("## 3) Блок 3. Заголовки\n\n")
        for idx, h in enumerate(generated.headlines, start=1):
            f.write(
                f"- {idx}. **[{h.format_type}]** {h.text} (≈{h.char_count} знаков)\n"
            )
        f.write("\n")

        # Block 4
        f.write("## 4) Блок 4. Рекомендации к тесту (top-5)\n\n")
        for idx, rec in enumerate(generated.top5, start=1):
            f.write(f"### Рекомендация #{idx}\n")
            f.write(f"- Инфоповод: {rec.get('inforeason_title')}\n")
            f.write(f"- Угол: {rec.get('angle_text')}\n")
            f.write(f"- Связь с оффером: {rec.get('offer_connection')}\n")
            f.write(f"- Почему топ: {rec.get('why_top')}\n")
            f.write("- 3 заголовка:\n")
            headlines_list = rec.get("headlines") or []
            for h_idx, h_text in enumerate(headlines_list, start=1):
                f.write(f"  {h_idx}) {h_text}\n")
            f.write("\n")

        # Block 5
        f.write("## 5) Блок 5. Риски\n\n")
        for idx, r in enumerate(generated.risks, start=1):
            f.write(f"### Риск #{idx}\n")
            f.write(f"- Юридические риски: {r.legal_risk}\n")
            f.write(f"- Риск бана: {r.ban_risk}\n")
            f.write(f"- Риск негатива аудитории: {r.audience_negative}\n")
            f.write(f"- Срок протухания: {r.expiration_date}\n\n")

        # Block 6
        f.write("## 6) Блок 6. Срочность\n\n")
        f.write("🔥 Срочно (в течение 48 часов):\n")
        for t in generated.urgent_titles:
            f.write(f"- {t}\n")
        f.write("\n⏳ Можно позже (вечная/не срочная тема):\n")
        for t in generated.later_titles:
            f.write(f"- {t}\n")

    return {
        "release_id": release_id,
        "markdown_path": markdown_path,
        "geo_code": geo_code,
        "raw_inforeasons_saved": saved_inforeasons,
    }

