from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.tickets.use_ticket import UseTicket
from fanfan.application.users.get_current_user import GetCurrentUser
from fanfan.core.vo.ticket import TicketId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.middlewares.load_current_user import CURRENT_USER_KEY


@inject
async def manual_ticket_input_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: TicketId,
    get_current_user: FromDishka[GetCurrentUser],
    use_ticket: FromDishka[UseTicket],
) -> None:
    await use_ticket(data)
    # Update user in context
    # TODO: Find a (maybe) nicer way to update user
    # Middleware won't run after linking ticket, bg update fails
    dialog_manager.middleware_data[CURRENT_USER_KEY] = await get_current_user()
    await message.answer(
        "✅ Билет успешно привязан! Теперь тебе доступны все функции бота!",
    )
    await dialog_manager.start(
        states.Main.HOME, mode=StartMode.RESET_STACK, show_mode=ShowMode.DELETE_AND_SEND
    )
