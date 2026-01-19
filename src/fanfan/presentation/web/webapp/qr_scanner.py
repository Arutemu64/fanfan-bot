from pathlib import Path

from aiogram import Bot
from aiogram_dialog import BgManagerFactory, ShowMode, StartMode
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Request
from starlette.responses import FileResponse, JSONResponse

from fanfan.application.common.id_provider import IdProvider
from fanfan.application.tickets.use_ticket import UseTicket
from fanfan.core.exceptions.base import AppException
from fanfan.core.exceptions.codes import CodeNotFound
from fanfan.core.vo.code import CodeId
from fanfan.core.vo.ticket import TicketId
from fanfan.presentation.tgbot import states
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
    code_processor: FromDishka[CodeProcessor],
    use_ticket: FromDishka[UseTicket],
    bg_factory: FromDishka[BgManagerFactory],
    bot: FromDishka[Bot],
    id_provider: FromDishka[IdProvider],
) -> JSONResponse:
    try:
        user = await id_provider.get_current_user()
        request_data = await request.json()
        qr_data = request_data.get("qr_data")

        # Assume user scanned CodeId
        try:
            result = await code_processor(CodeId(qr_data))
            return JSONResponse({"ok": True, "message": result.message})
        except CodeNotFound:
            pass

        # If CodeId not found, assume user scanned
        # TCloud QR code (numeric, 16 digits)
        if qr_data.isnumeric() and len(qr_data) == 16:
            await use_ticket(ticket_id=TicketId(qr_data))
            bg = bg_factory.bg(
                bot=bot,
                user_id=user.tg_id,
                chat_id=user.tg_id,
                load=True,
            )
            await bg.start(
                state=states.Main.HOME,
                mode=StartMode.RESET_STACK,
                show_mode=ShowMode.DELETE_AND_SEND,
            )
            return JSONResponse(
                {
                    "ok": True,
                    "message": "Билет успешно привязан! "
                    "Теперь тебе доступны все функции бота!",
                }
            )

    # Error handling
    except AppException as e:
        return JSONResponse({"ok": False, "message": e.message})
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"ok": False, "message": e.__class__.__name__})
    else:
        return JSONResponse({"ok": False, "message": None})
