from fastapi import APIRouter

from app.api.v1.routes.monitor import router as monitor_router
from app.api.v1.routes.feedback import router as feedback_router

api_router = APIRouter()
api_router.include_router(monitor_router, prefix="/api/v1/monitor", tags=["monitor"])
api_router.include_router(feedback_router, prefix="/api/v1", tags=["feedback"])

