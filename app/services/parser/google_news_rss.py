from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

import feedparser
import httpx

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RawNewsItem:
    title: str
    link: str
    pubdate: datetime


def build_rss_url(*, keywords: str, lookback_days: int, hl: str, gl: str) -> str:
    """
    Строит URL для Google News RSS с обязательным параметром ceid.

    Args:
        keywords: Поисковые слова (уже URL-encoded или простые)
        lookback_days: Период поиска в днях
        hl: Язык интерфейса (например, 'en', 'pt-BR')
        gl: Страна (например, 'US', 'BR')

    Returns:
        Полный URL для запроса
    """
    lang_code = hl.split("-")[0].lower()
    ceid = f"{gl.upper()}:{lang_code}"

    # Кодируем keywords на всякий случай
    from urllib.parse import quote_plus
    safe_keywords = quote_plus(keywords.strip())

    return (
        "https://news.google.com/rss/search?"
        f"q={safe_keywords}+when:{lookback_days}d"
        f"&hl={hl.lower()}"
        f"&gl={gl.upper()}"
        f"&ceid={ceid}"
    )


async def fetch_google_news_rss(
        *,
        rss_url: str,
        timeout_s: float = 20.0,
        limit: int = 20,
) -> list[RawNewsItem]:
    """
    Скачивает и парсит новости из Google News RSS.

    Args:
        rss_url: URL RSS-ленты (с параметром ceid)
        timeout_s: Таймаут запроса в секундах
        limit: Максимальное количество новостей для возврата

    Returns:
        Список объектов RawNewsItem
    """
    logger.debug(f"📡 Запрос RSS: {rss_url}")


    async with httpx.AsyncClient(timeout=timeout_s, follow_redirects=True) as client:
        resp = await client.get(
            rss_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        resp.raise_for_status()
        html = resp.text

    feed = feedparser.parse(html)

    if feed.bozo:
        logger.warning(f"⚠️ Feedparser warning: {feed.bozo_exception}")

    logger.info(f"📰 Найдено записей в фиде: {len(feed.entries)}")

    out: list[RawNewsItem] = []
    for entry in feed.entries[:limit]:
        title = str(entry.get("title", "")).strip()
        link = str(entry.get("link", "")).strip()

        if not title or not link:
            logger.debug(f"⏭ Пропущена запись без title/link: {entry.get('title', 'N/A')}")
            continue

        pub_dt = datetime.now(timezone.utc)
        if entry.get("published_parsed"):
            try:
                tt = entry.published_parsed
                pub_dt = datetime(
                    year=tt.tm_year, month=tt.tm_mon, day=tt.tm_mday,
                    hour=tt.tm_hour, minute=tt.tm_min, second=tt.tm_sec,
                    tzinfo=timezone.utc
                )
            except (AttributeError, ValueError, IndexError) as e:
                logger.warning(f"⚠️ Не удалось распарсить дату: {e}, используем текущую")

        out.append(RawNewsItem(title=title, link=link, pubdate=pub_dt))

    logger.info(f"✅ Возвращено {len(out)} новостей (лимит: {limit})")
    return out

