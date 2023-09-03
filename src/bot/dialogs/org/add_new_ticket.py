import operator

from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input.text import ManagedTextInput
from aiogram_dialog.widgets.kbd import Radio, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.bot.dialogs import states
from src.bot.structures import UserRole
from src.bot.ui import strings
from src.db import Database

TICKET_ROLE_PICKER_ID = "ticket_role_picker"


async def get_roles(**kwargs):
    roles = [
        ("Зритель", UserRole.VISITOR),
        ("Волонтёр", UserRole.HELPER),
        ("Организатор", UserRole.ORG),
    ]
    return {"roles": roles}


async def add_new_ticket(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    db: Database = dialog_manager.middleware_data["db"]
    role = dialog_manager.find(TICKET_ROLE_PICKER_ID).get_checked()

    check_ticket = await db.ticket.get(data)
    if check_ticket:
        await message.reply("Билет с таким номером уже существует!")
        return

    new_ticket = await db.ticket.new(id=data, role=role, issued_by=message.from_user.id)
    db.session.add(new_ticket)
    await db.session.commit()

    await message.answer(
        f"""Билет "{new_ticket.id}" с ролью {new_ticket.role} успешно добавлен!"""
    )
    await dialog_manager.switch_to(states.ORG.MAIN)


new_ticket_window = Window(
    Const("Выберите роль для билета и введите его номер:"),
    Radio(
        Format("🔘 {item[0]}"),
        Format("⚪️ {item[0]}"),
        id=TICKET_ROLE_PICKER_ID,
        item_id_getter=operator.itemgetter(1),
        items="roles",
    ),
    TextInput(id="ticket_id", type_factory=str, on_success=add_new_ticket),
    SwitchTo(state=states.ORG.MAIN, id="org_menu", text=Const(strings.buttons.back)),
    getter=get_roles,
    state=states.ORG.NEW_TICKET,
)
