from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Const

from src.bot.dialogs import states
from src.bot.ui import strings
from src.db import Database
from src.db.models import User


async def check_ticket(
    message: Message, message_input: MessageInput, manager: DialogManager
):
    db: Database = manager.middleware_data.get("db")
    ticket = await db.user.get_by_where(User.ticket_id == message.text)
    if ticket:
        if ticket.tg_id is None:
            ticket.tg_id = message.from_user.id
            ticket.username = message.from_user.username.lower()
            await db.session.commit()
            await message.answer(strings.success.registration_successful)
            manager.middleware_data["user"] = ticket
            await manager.start(state=states.MAIN.MAIN, mode=StartMode.RESET_STACK)
        else:
            await message.reply(strings.errors.ticket_used)
    else:
        await message.reply(strings.errors.ticket_not_found)


registration = Window(
    Const(strings.errors.please_send_ticket),
    MessageInput(check_ticket, content_types=[ContentType.TEXT]),
    state=states.REGISTRATION.MAIN,
)

dialog = Dialog(registration)
