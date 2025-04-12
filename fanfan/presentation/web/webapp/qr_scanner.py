from pathlib import Path

from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import BgManagerFactory, ShowMode, StartMode
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Request
from starlette.responses import FileResponse, JSONResponse

from fanfan.adapters.db.repositories.achievements import AchievementsRepository
from fanfan.adapters.utils.notifier import BotNotifier
from fanfan.application.codes.proceed_code import ProceedCode
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.notification import UserNotification
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.code import CodeId
from fanfan.core.utils.notifications import (
    create_achievement_notification,
    create_app_exception_notification,
    create_exception_notification,
)
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.keyboards.buttons import DELETE_BUTTON
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
    proceed_code: FromDishka[ProceedCode],
    notifier: FromDishka[BotNotifier],
    id_provider: FromDishka[IdProvider],
    achievements_repo: FromDishka[AchievementsRepository],
    bot: FromDishka[Bot],
    bg_factory: FromDishka[BgManagerFactory],
) -> JSONResponse:
    user_id = id_provider.get_current_user_id()
    try:
        data = await request.json()
        code = await proceed_code(CodeId(data["qr_data"]))
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
        if code.achievement_id:
            achievement = await achievements_repo.get_achievement_by_id(
                code.achievement_id
            )
            await notifier.send_notification(
                user_id=user_id,
                notification=create_achievement_notification(achievement),
            )
        if code.ticket_id:
            await notifier.send_notification(
                user_id=user_id,
                notification=UserNotification(
                    title="✅ Билет привязан",
                    text="Билет успешно привязан к вашему аккаунту Telegram!",
                    reply_markup=InlineKeyboardBuilder([[DELETE_BUTTON]]).as_markup(),
                ),
            )
            bg = bg_factory.bg(
                bot=bot,
                user_id=user_id,
                chat_id=user_id,
                load=True,
            )
            await bg.start(
                state=states.Main.HOME,
                mode=StartMode.RESET_STACK,
                show_mode=ShowMode.DELETE_AND_SEND,
            )
        return JSONResponse({"ok": True})
