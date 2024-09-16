from pathlib import Path

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.web_app import safe_parse_webapp_init_data
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Request
from pydantic import ValidationError
from starlette.responses import FileResponse, JSONResponse

from fanfan.application.achievements.add_achievement_to_user import AddAchievementToUser
from fanfan.application.achievements.get_achievement_by_secret_id import (
    GetAchievementBySecretId,
)
from fanfan.application.common.id_provider import IdProvider
from fanfan.common.config import BotConfig
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.notification import UserNotification
from fanfan.core.models.qr import QR, QRType
from fanfan.infrastructure.auth.utils.token import JwtTokenProcessor
from fanfan.infrastructure.scheduler.notifications.bot_notifier import Notifier
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
    config: FromDishka[BotConfig],
    notifier: FromDishka[Notifier],
    token_processor: FromDishka[JwtTokenProcessor],
    id_provider: FromDishka[IdProvider],
    get_achievement_by_secret_id: FromDishka[GetAchievementBySecretId],
    receive_achievement: FromDishka[AddAchievementToUser],
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
        qr = QR.model_validate_json(data["qr_text"])
    except ValidationError:
        await notifier.send_notification(
            UserNotification(
                user_id=id_provider.get_current_user_id(),
                title="⚠️ Ошибка",
                text="⚠️ Ошибка при валидации QR-кода, попробуйте ещё раз",
                reply_markup=InlineKeyboardBuilder().add(DELETE_BUTTON).as_markup(),
            )
        )
        return JSONResponse({"ok": False})

    match qr.type:
        case QRType.ACHIEVEMENT:
            try:
                achievement = await get_achievement_by_secret_id(qr.data)
                await receive_achievement(
                    user_id=id_provider.get_current_user_id(),
                    achievement_id=achievement.id,
                )
            except AppException as e:
                await notifier.send_notification(
                    UserNotification(
                        user_id=id_provider.get_current_user_id(),
                        title="⚠️ Ошибка",
                        text=e.message,
                        reply_markup=InlineKeyboardBuilder()
                        .add(DELETE_BUTTON)
                        .as_markup(),
                    )
                )
            return JSONResponse({"ok": False})
    return JSONResponse({"ok": True})
