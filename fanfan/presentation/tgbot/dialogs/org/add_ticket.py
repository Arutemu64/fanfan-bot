import operator
import typing

from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Column, ManagedRadio, Radio, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from fanfan.application.tickets.create_ticket import CreateTicket, CreateTicketDTO
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.ticket import TicketId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.getters import roles_getter
from fanfan.presentation.tgbot.ui import strings

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer

ID_TICKET_ROLE_PICKER = "ticket_role_picker"


async def add_ticket_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: TicketId,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    create_ticket: CreateTicket = await container.get(CreateTicket)
    role_picker: ManagedRadio[UserRole] = dialog_manager.find(ID_TICKET_ROLE_PICKER)

    try:
        ticket = await create_ticket(
            CreateTicketDTO(
                id=data,
                role=role_picker.get_checked(),
            ),
        )
    except AppException as e:
        await message.answer(e.message)
        return

    await message.answer(
        f"""✅ Билет "{ticket.id}" с ролью {ticket.role} успешно добавлен!""",
    )
    await dialog_manager.switch_to(states.Org.main)


add_ticket_window = Window(
    Const("✔️ Отметьте роль для билета ниже и напишите его номер"),
    Column(
        Radio(
            Format("🔘 {item[1]}"),
            Format("⚪️ {item[1]}"),
            id=ID_TICKET_ROLE_PICKER,
            item_id_getter=operator.itemgetter(0),
            items="roles",
            type_factory=UserRole,
        ),
    ),
    TextInput(id="ticket_id", type_factory=TicketId, on_success=add_ticket_handler),
    SwitchTo(
        state=states.Org.main,
        id="org_main_window",
        text=Const(strings.buttons.back),
    ),
    getter=roles_getter,
    state=states.Org.add_ticket,
)
