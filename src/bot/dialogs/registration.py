from typing import Any

from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input.text import ManagedTextInput
from aiogram_dialog.widgets.text import Const
from sqlalchemy import func

from src.bot.dialogs import states
from src.bot.structures import UserRole
from src.bot.ui import strings
from src.config import conf
from src.db import Database
from src.db.models import Ticket


async def check_ticket(
    message: Message,
    widget: ManagedTextInput,
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
            await dialog_manager.start(
                state=states.MAIN.MAIN,
                mode=StartMode.RESET_STACK,
            )
        else:
            await message.reply(strings.errors.ticket_used)
    else:
        await message.reply(strings.errors.ticket_not_found)


async def check_admin(start_data: Any, manager: DialogManager):
    if manager.event.from_user.username.lower() in conf.bot.admin_list:
        await manager.event.answer("Администраторы проходят без очереди! 😎")
        db: Database = manager.middleware_data["db"]
        await db.user.new(
            id=manager.event.from_user.id,
            username=manager.event.from_user.username,
            role=UserRole.ORG,
        )
        await db.session.commit()
        await manager.start(
            state=states.MAIN.MAIN,
            mode=StartMode.RESET_STACK,
        )


registration = Window(
    Const(strings.errors.please_send_ticket),
    TextInput(id="ticket_id_input", type_factory=str, on_success=check_ticket),
    state=states.REGISTRATION.MAIN,
)

dialog = Dialog(registration, on_start=check_admin)
