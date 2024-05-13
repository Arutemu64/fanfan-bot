from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

from fanfan.application.dto.user import UpdateUserDTO
from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.common.enums import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.ui import strings

from .constants import DATA_MANAGED_USER_ID


async def change_user_role_handler(
    callback: CallbackQuery,
    widget: Any,
    manager: DialogManager,
    data: UserRole,
):
    app: AppHolder = manager.middleware_data["app"]

    try:
        await app.users.update_user(
            UpdateUserDTO(
                id=manager.dialog_data[DATA_MANAGED_USER_ID],
                role=data,
            ),
        )
    except ServiceError as e:
        await callback.answer(e.message, show_alert=True)
        return

    await callback.answer(strings.common.success)
    await manager.switch_to(states.USER_MANAGER.MAIN)


async def show_user_editor_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    app: AppHolder = dialog_manager.middleware_data["app"]

    if data.isnumeric():
        try:
            user = await app.users.get_user_by_id(int(data))
        except ServiceError as e:
            await message.answer(e.message)
            return
    else:
        try:
            user = await app.users.get_user_by_username(data)
        except ServiceError as e:
            await message.answer(e.message)
            return
    await dialog_manager.start(states.USER_MANAGER.MAIN, data=user.id)


async def open_user_achievements_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    await manager.start(
        state=states.ACHIEVEMENTS.MAIN,
        data=manager.dialog_data[DATA_MANAGED_USER_ID],
    )
