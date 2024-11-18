from fastapi import APIRouter

from fanfan.adapters.config.models import Configuration


def setup_api_router(config: Configuration) -> APIRouter:
    from .timepad import setup_timepad_router

    router = APIRouter(prefix="/api")

    if config.timepad:
        router.include_router(setup_timepad_router())

    return router
