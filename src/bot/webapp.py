from aiogram import Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiogram_dialog import BgManagerFactory
from fastapi import APIRouter, Request
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette.responses import FileResponse, HTMLResponse, JSONResponse

from src.bot import STATIC_DIR
from src.bot.services.qr import proceed_qr_code
from src.bot.structures import QR
from src.db import Database

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
    manager = dialog_bg_factory.bg(
        bot=bot,
        user_id=web_app_init_data.user.id,
        chat_id=web_app_init_data.user.id,
        load=True,
    )
    async with session_pool() as session:
        await proceed_qr_code(
            qr=QR.parse(data["qr_text"]),
            bot=bot,
            manager=manager,
            db=Database(session),
            user_id=web_app_init_data.user.id,
        )
