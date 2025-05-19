from fastapi import APIRouter

from fanfan.presentation.web.api.timepad.webhook import timepad_webhook_router


def setup_timepad_router() -> APIRouter:
    router = APIRouter(prefix="/timepad")

    router.include_router(timepad_webhook_router)

    return router
