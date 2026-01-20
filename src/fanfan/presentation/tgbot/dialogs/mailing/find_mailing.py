from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.notifications.get_mailing_info import (
    GetMailingInfo,
    GetMailingInfoDTO,
)
from fanfan.core.vo.mailing import MailingId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.mailing.api import show_mailing_info
from fanfan.presentation.tgbot.static import strings


@inject
async def find_mailing_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: MailingId,
    get_mailing_info: FromDishka[GetMailingInfo],
) -> None:
    await get_mailing_info(GetMailingInfoDTO(mailing_id=data))
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
