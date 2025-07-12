import typing

from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from fanfan.core.vo.code import CodeId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.qr import (
    get_qr_scanner_button,
    qr_scanner_url_getter,
    user_qr_path_getter,
)
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.tgbot.utils.code_processor import CodeProcessor

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def manual_code_input_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: CodeId,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    code_processor = await container.get(CodeProcessor)
    result = await code_processor(data)
    await message.reply(result.message)


main_qr_window = Window(
    StaticMedia(path=Format("{user_qr_path}")),
    Title(Const(strings.titles.qr)),
    Const(
        "🤳 Ищи и сканируй QR-коды на территории фестиваля, "
        "чтобы получать достижения в квесте.\n\n"
        "Если не получается отсканировать QR-код, ты можешь отправить код вручную."
    ),
    get_qr_scanner_button(),
    Cancel(Const(strings.buttons.back)),
    TextInput(
        id="ticket_id_input",
        type_factory=CodeId,
        on_success=manual_code_input_handler,
    ),
    getter=[qr_scanner_url_getter, user_qr_path_getter],
    state=states.QR.MAIN,
)
