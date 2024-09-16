import typing

from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.application.tickets.link_ticket import LinkTicket
from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.application.users.update_user_commands import UpdateUserCommands
from fanfan.core.exceptions.base import AppException
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def link_ticket_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    link_ticket = await container.get(LinkTicket)
    get_user_by_id = await container.get(GetUserById)
    update_user_commands = await container.get(UpdateUserCommands)

    user_id = dialog_manager.event.from_user.id

    try:
        await link_ticket(ticket_id=data, user_id=user_id)
        await update_user_commands(user_id=user_id)
    except AppException as e:
        await message.reply(e.message)
        return

    dialog_manager.middleware_data["user"] = await get_user_by_id(user_id)
    await message.answer(
        "✅ Билет успешно привязан! Теперь тебе доступны все функции бота!",
    )
    await dialog_manager.start(states.Main.home, mode=StartMode.RESET_STACK)


link_ticket_window = Window(
    Title(Const(strings.titles.link_ticket)),
    Const(
        "🎫 Чтобы привязать билет и получить доступ ко всем функциям бота "
        "пришли его номер сообщением 👇\n\n"
        "Пример номера билета: 66117533:43231829\n\n"
        "🕒 Билет становится доступным для привязки "
        "в течение часа с момента оплаты",
    ),
    SwitchTo(Const(strings.buttons.back), id="back", state=states.Main.home),
    TextInput(id="ticket_id_input", type_factory=str, on_success=link_ticket_handler),
    state=states.Main.link_ticket,
)
