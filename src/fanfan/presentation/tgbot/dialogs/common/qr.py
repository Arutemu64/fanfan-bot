from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import WebApp
from aiogram_dialog.widgets.text import Const, Format
from dishka import AsyncContainer

from fanfan.application.codes.get_user_code_id import GetUserCodeId
from fanfan.core.utils.code import get_qr_code_image
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.web.config import WebConfig

QR_SCANNER_URL = "qr_scanner_url"
USER_QR_PATH = "user_qr_path"


def get_qr_scanner_button() -> WebApp:
    return WebApp(
        Const(strings.buttons.open_qr_scanner),
        url=Format("{qr_scanner_url}"),
    )


async def qr_scanner_url_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
) -> dict:
    config = await container.get(WebConfig)
    return {
        QR_SCANNER_URL: config.build_qr_scanner_url(),
    }


async def user_qr_path_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
) -> dict:
    get_user_code = await container.get(GetUserCodeId)

    return {
        USER_QR_PATH: get_qr_code_image(await get_user_code()),
    }
