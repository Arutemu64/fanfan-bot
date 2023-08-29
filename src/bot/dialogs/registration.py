from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input.text import ManagedTextInputAdapter
from aiogram_dialog.widgets.text import Const
from sqlalchemy import func

from src.bot.dialogs import states
from src.bot.ui import strings
from src.db import Database
from src.db.models import Ticket


async def check_ticket(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    data: str,
):
    db: Database = dialog_manager.middleware_data["db"]
    ticket = await db.ticket.get_by_where(func.lower(Ticket.id) == data.lower())
    if ticket:
        if ticket.used_by is None:
            user = await db.user.new(
                id=message.from_user.id,
                username=message.from_user.username,
                role=ticket.role,
            )
            await db.session.flush([user])
            ticket.used_by = user.id
            await db.session.commit()
            await message.answer(strings.success.registration_successful)
            dialog_manager.middleware_data["user"] = user
            await dialog_manager.start(
                state=states.MAIN.MAIN, mode=StartMode.RESET_STACK
            )
        else:
            await message.reply(strings.errors.ticket_used)
    else:
        await message.reply(strings.errors.ticket_not_found)


registration = Window(
    Const(strings.errors.please_send_ticket),
    TextInput(id="enter_ticket", type_factory=str, on_success=check_ticket),
    state=states.REGISTRATION.MAIN,
)

dialog = Dialog(registration)
