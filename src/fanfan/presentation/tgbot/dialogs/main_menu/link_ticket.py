import typing

from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.application.common.id_provider import IdProvider
from fanfan.application.tickets.link_ticket import LinkTicket
from fanfan.core.vo.ticket import TicketId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings

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
    id_provider: IdProvider = await container.get(IdProvider)

    await link_ticket(data)
    # Update user in context
    # TODO: Find a (maybe) nicer way to update user
    # Middleware won't run after linking ticket, bg update fails
    dialog_manager.middleware_data["user"] = await id_provider.get_user_data()
    await message.answer(
        "✅ Билет успешно привязан! Теперь тебе доступны все функции бота!",
    )
    await dialog_manager.start(states.Main.HOME, mode=StartMode.RESET_STACK)


link_ticket_window = Window(
    Title(Const(strings.titles.link_ticket)),
    Const(
        "Основные функции бота доступны сразу. "
        "Пришли номер своего билета и получи доступ к:\n"
        "⚔️ Участию в квесте\n"
        "📣 Голосованию во внесценических номинациях\n"
        "💌 Рассылкам (для участников)\n"
        "🎁 Возможно, к чему-то ещё?...\n\n"
        "ℹ️ Если ты покупал билет онлайн, ищи номер билета рядом со штрих-кодом.\n"
        "Он должен выглядеть так: <i>1114290477285406</i>\n"
        "А если на кассе - вот так: <i>GWBWGS1W</i>"
    ),
    SwitchTo(Const(strings.buttons.back), id="back", state=states.Main.HOME),
    TextInput(
        id="ticket_id_input", type_factory=TicketId, on_success=link_ticket_handler
    ),
    state=states.Main.LINK_TICKET,
)
