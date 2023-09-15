from pathlib import Path

from aiogram import Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiogram_dialog import BgManagerFactory
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from sqlalchemy.orm import sessionmaker

from src.bot.utils.qr import proceed_qr_code
from src.db import Database


async def open_qr_scanner(request: Request):
    return FileResponse(Path(__file__).parent.resolve() / "qr_scanner.html")


async def proceed_qr_post(request: Request):
    bot: Bot = request.app["bot"]
    session_pool: sessionmaker = request.app["session_pool"]
    bgm_factory: BgManagerFactory = request.app["bgm_factory"]

    data = await request.post()
    try:
        web_app_init_data = safe_parse_webapp_init_data(
            token=bot.token, init_data=data["_auth"]
        )
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    bg = bgm_factory.bg(
        bot=bot, user_id=web_app_init_data.user.id, chat_id=web_app_init_data.user.id
    )

    async with session_pool() as session:
        await proceed_qr_code(
            manager=bg,
            db=Database(session),
            qr_text=data["qr_text"],
            bot=bot,
            user_id=web_app_init_data.user.id,
        )
