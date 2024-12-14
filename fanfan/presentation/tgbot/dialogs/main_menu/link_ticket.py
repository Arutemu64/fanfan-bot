import typing

from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.application.tickets.link_ticket import LinkTicket
from fanfan.core.models.ticket import TicketId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def link_ticket_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: TicketId,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    link_ticket: LinkTicket = await container.get(LinkTicket)

    await link_ticket(data)
    await message.answer(
        "✅ Билет успешно привязан! Теперь тебе доступны все функции бота!",
    )
    await dialog_manager.start(states.Main.home, mode=StartMode.RESET_STACK)


link_ticket_window = Window(
    Title(Const(strings.titles.link_ticket)),
    Const(
        "Чтобы привязать билет и получить доступ ко всем функциям бота "
        "пришли его номер сообщением 👇\n\n"
        "<i>Пример номера билета: 66117533:43231829</i>"
    ),
    SwitchTo(Const(strings.buttons.back), id="back", state=states.Main.home),
    TextInput(
        id="ticket_id_input", type_factory=TicketId, on_success=link_ticket_handler
    ),
    state=states.Main.link_ticket,
)
