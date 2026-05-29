from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title="AI-мониторинг инфоповодов",
    description=(
        "Система для автоматизированного мониторинга новостей и "
        "генерации маркетинговых идей"
    ),
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # в проде ограничить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="")


