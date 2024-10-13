import json
from pathlib import Path

from adaptix import Retort
from adaptix.load_error import LoadError
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiogram_dialog import BgManagerFactory
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Request
from starlette.responses import FileResponse, JSONResponse

from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.notifier import Notifier
from fanfan.application.quest.receive_achievement_by_secret_id import (
    ReceiveAchievementBySecretId,
)
from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.achievement import SecretId
from fanfan.core.models.notification import UserNotification
from fanfan.core.models.qr import QR, QRType
from fanfan.core.utils.notifications import create_achievement_notification
from fanfan.infrastructure.auth.utils.token import JwtTokenProcessor
from fanfan.infrastructure.config_reader import BotConfig
from fanfan.infrastructure.stream.routes.send_notification import (
    SendNotificationDTO,
)
from fanfan.presentation.tgbot.dialogs.user_manager import start_user_manager
from fanfan.presentation.tgbot.keyboards.buttons import DELETE_BUTTON

QR_SCANNER_APP = Path(__file__).parent.joinpath("qr_scanner.html")

qr_scanner_router = APIRouter()


@qr_scanner_router.get("/qr_scanner")
async def open_qr_scanner() -> FileResponse:
    return FileResponse(QR_SCANNER_APP)


@qr_scanner_router.post("/qr_scanner")
@inject
async def proceed_qr_post(
    request: Request,
    bot: FromDishka[Bot],
    config: FromDishka[BotConfig],
    notifier: FromDishka[Notifier],
    token_processor: FromDishka[JwtTokenProcessor],
    id_provider: FromDishka[IdProvider],
    receive_achievement_by_secret_id: FromDishka[ReceiveAchievementBySecretId],
    get_user_id_by: FromDishka[GetUserById],
    bg_factory: FromDishka[BgManagerFactory],
) -> JSONResponse:
    data = await request.form()

    # Auth
    try:
        web_app_init_data = safe_parse_webapp_init_data(
            token=config.token.get_secret_value(),
            init_data=data["_auth"],
        )
        token = token_processor.create_access_token(web_app_init_data.user.id)
        request.session["token"] = token
    except ValueError:
        return JSONResponse({"ok": False, "err": "Unauthorized"}, status_code=401)

    # Parsing QR code
    try:
        qr = Retort(strict_coercion=False).load(json.loads(data["qr_text"]), QR)
    except LoadError:
        await notifier.send_notification(
            SendNotificationDTO(
                user_id=id_provider.get_current_user_id(),
                notification=UserNotification(
                    title="⚠️ Ошибка",
                    text="⚠️ Ошибка при валидации QR-кода, попробуйте ещё раз",
                    reply_markup=InlineKeyboardBuilder().add(DELETE_BUTTON).as_markup(),
                ),
            )
        )
        return JSONResponse({"ok": False})

    try:
        match qr.type:
            case QRType.ACHIEVEMENT:
                achievement = await receive_achievement_by_secret_id(SecretId(qr.data))
                await notifier.show_notification(
                    create_achievement_notification(achievement)
                )
                return JSONResponse({"ok": True})
            case QRType.USER:
                user = await get_user_id_by(id_provider.get_current_user_id())
                if user.role in [UserRole.HELPER, UserRole.ORG]:
                    bg = bg_factory.bg(
                        bot=bot,
                        user_id=id_provider.get_current_user_id(),
                        chat_id=id_provider.get_current_user_id(),
                        load=True,
                    )
                    await start_user_manager(bg, int(qr.data))
                    return JSONResponse({"ok": True})
                raise AccessDenied
    except AppException as e:
        await notifier.send_notification(
            SendNotificationDTO(
                user_id=id_provider.get_current_user_id(),
                notification=UserNotification(
                    title="⚠️ Ошибка",
                    text=e.message,
                    reply_markup=InlineKeyboardBuilder().add(DELETE_BUTTON).as_markup(),
                ),
            )
        )
        return JSONResponse({"ok": False})
    return JSONResponse({"ok": True})
