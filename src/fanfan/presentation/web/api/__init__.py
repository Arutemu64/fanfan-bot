from fastapi import APIRouter

from fanfan.presentation.web.api.tcloud import tcloud_webhook_router


def setup_api_router() -> APIRouter:
    router = APIRouter(prefix="/api")

    router.include_router(tcloud_webhook_router)

    return router
