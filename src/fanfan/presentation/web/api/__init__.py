from fastapi import APIRouter


def setup_api_router() -> APIRouter:
    from .timepad import setup_timepad_router

    router = APIRouter(prefix="/api")
    setup_timepad_router()

    return router
