import operator
import typing

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Column, Select, SwitchTo
from aiogram_dialog.widgets.kbd.select import ManagedT
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from fanfan.application.tickets.generate_ticket import (
    GenerateTicket,
    GenerateTicketDTO,
)
from fanfan.core.models.user import UserData, UserRole
from fanfan.core.utils.code import get_qr_code_image
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.static import strings

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer

DATA_NEW_TICKET_ID = "new_ticket_id"
DATA_TICKET_CODE_ID = "ticket_code_id"


async def pick_role_getter(user: UserData, **kwargs) -> dict:
    roles = [UserRole.VISITOR, UserRole.PARTICIPANT]
    if user.role is UserRole.ORG:
        roles += [UserRole.HELPER, UserRole.ORG]
    return {
        "roles": [(item.value, item.label, item.label_plural) for item in roles],
    }


async def result_window_getter(
    dialog_manager: DialogManager,
    **kwargs,
) -> dict:
    return {
        "ticket_id": dialog_manager.middleware_data[DATA_NEW_TICKET_ID],
        "qr_file_path": get_qr_code_image(
            dialog_manager.middleware_data[DATA_TICKET_CODE_ID]
        ),
    }


async def pick_role_handler(
    callback: CallbackQuery, widget: ManagedT, manager: DialogManager, role: UserRole
):
    container: AsyncContainer = manager.middleware_data["container"]
    generate_ticket: GenerateTicket = await container.get(GenerateTicket)

    result = await generate_ticket(GenerateTicketDTO(role=role))

    manager.middleware_data[DATA_NEW_TICKET_ID] = result.ticket_id
    manager.middleware_data[DATA_TICKET_CODE_ID] = result.code_id

    await manager.switch_to(state=states.Staff.CREATE_TICKET_RESULT)


create_ticket_pick_role_window = Window(
    Const("✔️ Выберите роль для билета ниже"),
    Column(
        Select(
            Format("{item[1]}"),
            id="ticket_role_picker",
            item_id_getter=operator.itemgetter(0),
            items="roles",
            type_factory=UserRole,
            on_click=pick_role_handler,
        ),
    ),
    SwitchTo(Const(strings.buttons.back), id="back", state=states.Staff.MAIN),
    getter=pick_role_getter,
    state=states.Staff.CREATE_TICKET_PICK_ROLE,
)

create_ticket_result_window = Window(
    StaticMedia(path=Format("{qr_file_path}")),
    Format(
        "✅ Билет создан! Посетитель может отсканировать QR-код выше, "
        "используя раздел <b>📸 QR-код</b> в главном меню бота, "
        "либо сфотографировать это сообщение и ввести код вручную.\n"
        "Номер билета: <b>{ticket_id}</b>"
    ),
    Const(" "),
    Const(
        "⚠️ Номер билета чувствителен к регистру!"
        "Вводите номер точно, как он указан в этом сообщении!"
    ),
    SwitchTo(
        state=states.Staff.MAIN,
        id="org_main_window",
        text=Const(strings.buttons.back),
    ),
    state=states.Staff.CREATE_TICKET_RESULT,
    getter=[result_window_getter],
)
