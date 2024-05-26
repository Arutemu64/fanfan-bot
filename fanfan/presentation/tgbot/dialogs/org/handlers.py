from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, ManagedRadio

from fanfan.application.dto.settings import UpdateSettingsDTO
from fanfan.application.dto.ticket import CreateTicketDTO
from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.common.enums import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.org.constants import (
    ID_TICKET_ROLE_PICKER,
)


async def toggle_voting_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    app: AppHolder = manager.middleware_data["app"]
    try:
        settings = await app.settings.get_settings()
        await app.settings.update_settings(
            UpdateSettingsDTO(voting_enabled=not settings.voting_enabled)
        )
    except ServiceError as e:
        await callback.answer(e.message)
        return


async def add_new_ticket_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    app: AppHolder = dialog_manager.middleware_data["app"]
    role_picker: ManagedRadio[UserRole] = dialog_manager.find(ID_TICKET_ROLE_PICKER)

    try:
        ticket = await app.tickets.create_ticket(
            CreateTicketDTO(
                id=data,
                role=role_picker.get_checked(),
            ),
        )
    except ServiceError as e:
        await message.answer(e.message)
        return

    await message.answer(
        f"""✅ Билет "{ticket.id}" с ролью {ticket.role} успешно добавлен!""",
    )
    await dialog_manager.switch_to(states.ORG.MAIN)
