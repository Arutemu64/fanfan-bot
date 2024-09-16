import typing

from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.application.mailing.delete_mailing import DeleteMailing
from fanfan.core.utils.pluralize import NOTIFICATIONS_PLURALS, pluralize
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.ui import strings

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer

ID_MAILING_ID_INPUT = "mailing_id_input"


async def delete_mailing_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    delete_mailing: DeleteMailing = await container.get(DeleteMailing)

    mailing_info = await delete_mailing(data)
    await message.answer(
        f"✅ Будет удалено {mailing_info.count} "
        f"{pluralize(mailing_info.count, NOTIFICATIONS_PLURALS)}",
    )

    await dialog_manager.switch_to(states.Mailing.main)


delete_mailing_window = Window(
    Const("🗑️ Отправьте уникальный ID рассылки, которую нужно удалить"),
    TextInput(
        id=ID_MAILING_ID_INPUT,
        type_factory=str,
        on_success=delete_mailing_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back),
        id="back",
        state=states.Mailing.main,
    ),
    state=states.Mailing.delete_mailing,
)
