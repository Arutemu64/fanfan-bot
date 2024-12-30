from pathlib import Path

from aiogram import Bot
from aiogram_dialog import BgManagerFactory
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Request
from starlette.responses import FileResponse, JSONResponse

from fanfan.adapters.utils.notifier import BotNotifier
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.quest.receive_achievement_by_secret_id import (
    ReceiveAchievementBySecretId,
)
from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.core.dto.qr import QRType
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.achievement import SecretId
from fanfan.core.models.user import UserRole
from fanfan.core.utils.notifications import (
    create_achievement_notification,
    create_app_exception_notification,
    create_exception_notification,
)
from fanfan.core.utils.qr import parse_qr_data
from fanfan.presentation.tgbot.dialogs.user_manager import start_user_manager
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
    bot: FromDishka[Bot],
    notifier: FromDishka[BotNotifier],
    id_provider: FromDishka[IdProvider],
    receive_achievement_by_secret_id: FromDishka[ReceiveAchievementBySecretId],
    get_user_id_by: FromDishka[GetUserById],
    bg_factory: FromDishka[BgManagerFactory],
) -> JSONResponse:
    data = await request.json()
    # Parsing QR code
    try:
        qr = parse_qr_data(data["qr_data"])
        match qr.type:
            case QRType.ACHIEVEMENT:
                achievement = await receive_achievement_by_secret_id(SecretId(qr.data))
                await notifier.send_notification(
                    user_id=id_provider.get_current_user_id(),
                    notification=create_achievement_notification(achievement),
                )
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
                else:
                    raise AccessDenied  # noqa: TRY301
    except AppException as e:
        await notifier.send_notification(
            user_id=id_provider.get_current_user_id(),
            notification=create_app_exception_notification(e),
        )
        return JSONResponse({"ok": False})
    except Exception as e:  # noqa: BLE001
        await notifier.send_notification(
            user_id=id_provider.get_current_user_id(),
            notification=create_exception_notification(e),
        )
        return JSONResponse({"ok": False})
    else:
        return JSONResponse({"ok": True})
