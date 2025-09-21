from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import WebApp
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.codes.get_user_code_id import GetUserCodeId
from fanfan.core.dto.user import FullUserDTO
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


@inject
async def qr_scanner_url_getter(
    dialog_manager: DialogManager,
    config: FromDishka[WebConfig],
    **kwargs,
) -> dict:
    return {
        QR_SCANNER_URL: config.build_qr_scanner_url(),
    }


@inject
async def user_qr_path_getter(
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
    get_user_code: FromDishka[GetUserCodeId],
    **kwargs,
) -> dict:
    return {
        USER_QR_PATH: get_qr_code_image(await get_user_code(current_user.id)),
    }
