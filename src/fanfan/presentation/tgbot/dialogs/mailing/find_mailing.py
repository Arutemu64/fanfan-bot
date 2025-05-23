from typing import TYPE_CHECKING

from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.application.mailing.read_mailing_info import ReadMailingInfo
from fanfan.core.dto.mailing import MailingId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.mailing.view_mailing import show_mailing_info
from fanfan.presentation.tgbot.static import strings

if TYPE_CHECKING:
    from dishka import AsyncContainer


async def find_mailing_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: MailingId,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    get_mailing_info: ReadMailingInfo = await container.get(ReadMailingInfo)
    await get_mailing_info(data)
    await show_mailing_info(dialog_manager, data)


find_mailing_window = Window(
    Const("⌨️ Введите уникальный ID рассылки"),
    TextInput(
        id="find_mailing_id_input",
        type_factory=MailingId,
        on_success=find_mailing_handler,
    ),
    SwitchTo(Const(strings.buttons.back), id="back", state=states.Mailing.MAIN),
    state=states.Mailing.FIND_MAILING,
)
