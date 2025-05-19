from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import SwitchTo, WebApp
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
from dishka import AsyncContainer

from fanfan.adapters.config.models import Configuration
from fanfan.application.codes.get_user_code_id import GetUserCodeId
from fanfan.core.utils.code import get_qr_code_image
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.static import strings


async def qr_window_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
) -> dict:
    config: Configuration = await container.get(Configuration)
    get_user_code: GetUserCodeId = await container.get(GetUserCodeId)

    return {
        "qr_file_path": get_qr_code_image(await get_user_code()),
        "qr_scanner_url": config.web.build_qr_scanner_url() if config.web else None,
    }


qr_window = Window(
    StaticMedia(path=Format("{qr_file_path}")),
    Const(
        "🎫 Это твой уникальный QR-код. Покажи его волонтёру, "
        "чтобы получить очки за участие в квесте.\n\n"
        "📸 Ищи и сканируй QR-коды на территории фестиваля, чтобы получать достижения."
    ),
    WebApp(
        Const("📸 Открыть сканер"),
        url=Format("{qr_scanner_url}"),
        when="qr_scanner_url",
    ),
    SwitchTo(Const(strings.buttons.back), id="back", state=states.Main.HOME),
    getter=qr_window_getter,
    state=states.Main.QR_CODE,
)
