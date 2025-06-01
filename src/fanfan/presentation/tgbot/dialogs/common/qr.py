from aiogram_dialog import DialogManager
from dishka import AsyncContainer

from fanfan.application.codes.get_user_code_id import GetUserCodeId
from fanfan.core.utils.code import get_qr_code_image
from fanfan.presentation.web.config import WebConfig

QR_SCANNER_URL = "qr_scanner_url"
USER_QR_PATH = "user_qr_path"


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
