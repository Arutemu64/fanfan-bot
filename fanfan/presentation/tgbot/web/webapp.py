from pathlib import Path

from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiogram_dialog import BgManagerFactory
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Request
from pydantic import ValidationError
from starlette.responses import FileResponse, JSONResponse

from fanfan.application.dto.qr import QR
from fanfan.application.exceptions import ServiceError
from fanfan.application.exceptions.quest import UserAlreadyHasThisAchievement
from fanfan.application.holder import AppHolder
from fanfan.application.services import UserService
from fanfan.common.enums import QRType
from fanfan.infrastructure.db import UnitOfWork
from fanfan.presentation.tgbot.buttons import DELETE_BUTTON

QR_SCANNER_APP = Path(__file__).parent.joinpath("qr_scanner.html")

webapp_router = APIRouter()


@webapp_router.get("/qr_scanner")
async def open_qr_scanner():
    return FileResponse(QR_SCANNER_APP)


@webapp_router.post("/qr_scanner")
@inject
async def proceed_qr_post(
    request: Request,
    bot: FromDishka[Bot],
    dialog_bg_factory: FromDishka[BgManagerFactory],
    uow: FromDishka[UnitOfWork],
):
    data = await request.form()
    try:
        web_app_init_data = safe_parse_webapp_init_data(
            token=bot.token,
            init_data=data["_auth"],
        )
    except ValueError:
        return JSONResponse({"ok": False, "err": "Unauthorized"}, status_code=401)

    user = await UserService(uow).get_user_by_id(web_app_init_data.user.id)
    app = AppHolder(uow=uow, identity=user)

    try:
        qr = QR.model_validate_json(data["qr_text"])
        match qr.type:
            case QRType.USER:
                manager = dialog_bg_factory.bg(
                    bot=bot,
                    user_id=web_app_init_data.user.id,
                    chat_id=web_app_init_data.user.id,
                    load=True,
                )
                await app.qr.open_user_manager(
                    user_id=int(qr.data),
                    manager=manager,
                )
            case QRType.ACHIEVEMENT:
                try:
                    await app.qr.receive_achievement(
                        secret_id=qr.data,
                        user_id=web_app_init_data.user.id,
                    )
                except UserAlreadyHasThisAchievement:
                    await bot.send_message(
                        chat_id=web_app_init_data.user.id,
                        text="⚠️ У тебя уже есть это достижение",
                        reply_markup=InlineKeyboardBuilder()
                        .add(DELETE_BUTTON)
                        .as_markup(),
                    )
    except ValidationError:
        await bot.send_message(
            chat_id=web_app_init_data.user.id,
            text="⚠️ Ошибка при валидации QR-кода, попробуйте ещё раз",
            reply_markup=InlineKeyboardBuilder().add(DELETE_BUTTON).as_markup(),
        )
    except ServiceError as e:
        await bot.send_message(
            chat_id=web_app_init_data.user.id,
            text=e.message,
            reply_markup=InlineKeyboardBuilder().add(DELETE_BUTTON).as_markup(),
        )
