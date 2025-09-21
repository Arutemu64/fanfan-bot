import operator

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Column, Select, SwitchTo
from aiogram_dialog.widgets.kbd.select import ManagedT
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.tickets.generate_ticket import (
    GenerateTicket,
    GenerateTicketDTO,
)
from fanfan.core.dto.user import FullUserDTO
from fanfan.core.utils.code import get_qr_code_image
from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.staff.data import StaffDialogData
from fanfan.presentation.tgbot.static import strings


async def pick_role_getter(current_user: FullUserDTO, **kwargs) -> dict:
    roles = [UserRole.VISITOR, UserRole.PARTICIPANT]
    if current_user.role is UserRole.ORG:
        roles += [UserRole.HELPER, UserRole.ORG]
    return {
        "roles": [(item.value, item.label, item.label_plural) for item in roles],
    }


async def result_window_getter(
    dialog_manager: DialogManager,
    **kwargs,
) -> dict:
    dialog_data_adapter = get_dialog_data_adapter(dialog_manager)
    dialog_data = dialog_data_adapter.load(StaffDialogData)
    return {
        "ticket_id": dialog_data.new_ticket_id,
        "qr_file_path": get_qr_code_image(dialog_data.new_ticket_code_id),
    }


@inject
async def pick_role_handler(
    callback: CallbackQuery,
    widget: ManagedT,
    manager: DialogManager,
    data: UserRole,
    generate_ticket: FromDishka[GenerateTicket],
):
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(StaffDialogData)

    result = await generate_ticket(GenerateTicketDTO(role=data))
    dialog_data.new_ticket_id = result.ticket_id
    dialog_data.new_ticket_code_id = result.code_id
    dialog_data_adapter.flush(dialog_data)

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
        "✅ Уникальный код создан! Посетитель может отсканировать QR-код выше, "
        "либо ввести код вручную.\n"
        "Уникальный код: <b>{ticket_id}</b>"
    ),
    Const(" "),
    Const(
        "⚠️ Код чувствителен к регистру! "
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
