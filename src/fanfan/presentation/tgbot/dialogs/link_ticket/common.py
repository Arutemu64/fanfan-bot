import typing

from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput

from fanfan.application.common.id_provider import IdProvider
from fanfan.application.tickets.link_ticket import LinkTicket
from fanfan.core.vo.ticket import TicketId
from fanfan.presentation.tgbot import states

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def manual_ticket_input_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: TicketId,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    link_ticket = await container.get(LinkTicket)
    id_provider = await container.get(IdProvider)

    await link_ticket(data)
    # Update user in context
    # TODO: Find a (maybe) nicer way to update user
    # Middleware won't run after linking ticket, bg update fails
    dialog_manager.middleware_data["user"] = await id_provider.get_user_data()
    await message.answer(
        "✅ Билет успешно привязан! Теперь тебе доступны все функции бота!",
    )
    await dialog_manager.start(
        states.Main.HOME, mode=StartMode.RESET_STACK, show_mode=ShowMode.DELETE_AND_SEND
    )
