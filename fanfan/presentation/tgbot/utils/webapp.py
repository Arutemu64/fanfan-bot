from aiogram import Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiogram_dialog import BgManagerFactory
from fastapi import APIRouter, Request
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette.responses import FileResponse, HTMLResponse, JSONResponse

from fanfan.application.dto.common import QR
from fanfan.application.exceptions import ServiceError
from fanfan.application.services import UserService
from fanfan.application.services.qr import QRService
from fanfan.infrastructure.db import UnitOfWork
from fanfan.presentation.tgbot import STATIC_DIR
from fanfan.presentation.tgbot.dialogs.widgets import DELETE_BUTTON

webapp_router = APIRouter()


@webapp_router.get("/qr_scanner", response_class=HTMLResponse)
async def open_qr_scanner():
    return FileResponse(STATIC_DIR.joinpath("qr_scanner.html"))


@webapp_router.post("/qr_scanner")
async def proceed_qr_post(request: Request):
    bot: Bot = request.app.state.bot
    dialog_bg_factory: BgManagerFactory = request.app.state.dialog_bg_factory
    session_pool: async_sessionmaker = request.app.state.session_pool

    data = await request.form()
    try:
        web_app_init_data = safe_parse_webapp_init_data(
            token=bot.token, init_data=data["_auth"]
        )
    except ValueError:
        return JSONResponse({"ok": False, "err": "Unauthorized"}, status_code=401)
    async with session_pool() as session:
        uow = UnitOfWork(session)
        async with uow:
            user = await UserService(uow).get_user_by_id(web_app_init_data.user.id)
            manager = dialog_bg_factory.bg(
                bot=bot,
                user_id=web_app_init_data.user.id,
                chat_id=web_app_init_data.user.id,
                load=True,
            )
            try:
                await QRService(uow, user, manager).proceed_qr_code(
                    QR.parse(data["qr_text"])
                )
            except ServiceError as e:
                await bot.send_message(
                    chat_id=web_app_init_data.user.id,
                    text=e.message,
                    reply_markup=DELETE_BUTTON.as_markup(),
                )
                return
