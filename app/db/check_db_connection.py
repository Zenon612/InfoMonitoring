from __future__ import annotations

import asyncio

import asyncpg

from app.core.settings import settings


async def main() -> None:
    dsn = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)
    try:
        conn = await asyncpg.connect(dsn)
        await conn.close()
        print("DB connection OK")
    except Exception as e:  # noqa: BLE001
        print(f"DB connection FAILED: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

