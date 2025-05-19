from fastapi import APIRouter

from fanfan.presentation.web.webapp.qr_scanner import qr_scanner_router


def setup_webapp_router() -> APIRouter:
    router = APIRouter()

    router.include_router(qr_scanner_router)

    return router
