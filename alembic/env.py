from __future__ import annotations

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context

from app.core.settings import settings
from app.db.base import Base

# Import models so Alembic can see them
from app.models.geo import Geo  # noqa: F401
from app.models.inforeason import Inforeason  # noqa: F401
from app.models.marketing_angle import MarketingAngle  # noqa: F401
from app.models.headline import Headline  # noqa: F401
from app.models.test_result import TestResult  # noqa: F401
from app.models.risk import Risk  # noqa: F401


config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_sync_url() -> str:
    """
    Трансформирует ссылку на асинхронный движок под alembic
    :return: url
    """
    url = settings.DATABASE_URL
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://")
    return url


def run_migrations_offline() -> None:
    """Генерация SQL-скриптов без подключения к БД."""
    url = get_sync_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,  # Важно: подставлять значения в SQL
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    # ❌ Без begin_transaction() в оффлайн-режиме!
    context.run_migrations()


def run_migrations_online() -> None:
    """Применение миграций к реальной БД."""
    # Создаём синхронный engine для Alembic
    connectable = create_engine(
        get_sync_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# 🎯 Для команды `alembic upgrade head` всегда используем онлайн-режим
# Оффлайн-режим оставьте только для `alembic upgrade head --sql` (генерация скрипта)
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()












