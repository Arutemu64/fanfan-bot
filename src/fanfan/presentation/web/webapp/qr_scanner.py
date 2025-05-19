from pathlib import Path

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Request
from starlette.responses import FileResponse, JSONResponse

from fanfan.adapters.utils.notifier import BotNotifier
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.base import AppException
from fanfan.core.utils.notifications import (
    create_app_exception_notification,
    create_exception_notification,
)
from fanfan.core.vo.code import CodeId
from fanfan.presentation.tgbot.utils.code_processor import CodeProcessor
from fanfan.presentation.web.webapp.auth import webapp_auth

QR_SCANNER_APP = Path(__file__).parent.joinpath("qr_scanner.html")

qr_scanner_router = APIRouter()


@qr_scanner_router.get("/qr_scanner")
async def open_qr_scanner() -> FileResponse:
    return FileResponse(QR_SCANNER_APP)


@qr_scanner_router.post(
    "/qr_scanner",
    dependencies=[Depends(webapp_auth)],
)
@inject
async def proceed_qr_post(
    request: Request,
    proceed_code: FromDishka[CodeProcessor],
    notifier: FromDishka[BotNotifier],
    id_provider: FromDishka[IdProvider],
) -> JSONResponse:
    user_id = id_provider.get_current_user_id()
    try:
        data = await request.json()
        await proceed_code(CodeId(data["qr_data"]))
    except AppException as e:
        await notifier.send_notification(
            user_id=user_id,
            notification=create_app_exception_notification(e),
        )
        return JSONResponse({"ok": False})
    except Exception as e:  # noqa: BLE001
        await notifier.send_notification(
            user_id=user_id,
            notification=create_exception_notification(e),
        )
        return JSONResponse({"ok": False})
    else:
        return JSONResponse({"ok": True})
