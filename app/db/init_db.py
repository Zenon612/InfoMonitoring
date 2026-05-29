from __future__ import annotations

import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine

from app.db.session import engine
from app.db.base import Base


async def init_db(engine_to_use: AsyncEngine | None = None) -> None:
    eng = engine_to_use or engine
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def main() -> None:
    asyncio.run(init_db())


if __name__ == "__main__":
    main()

