import operator
import typing
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Column, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from fanfan.application.users.update_user import UpdateUser, UpdateUserDTO
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.base import AppException
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.getters import roles_getter
from fanfan.presentation.tgbot.ui import strings

from .common import DATA_USER_ID

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def change_role_handler(
    callback: CallbackQuery,
    widget: Any,
    manager: DialogManager,
    data: UserRole,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    update_user: UpdateUser = await container.get(UpdateUser)

    try:
        await update_user(
            UpdateUserDTO(
                id=manager.start_data[DATA_USER_ID],
                role=data,
            ),
        )
    except AppException as e:
        await callback.answer(e.message, show_alert=True)
        return

    await callback.answer(strings.common.success)
    await manager.switch_to(states.UserManager.user_info)


change_role_window = Window(
    Const("✔️ Выберите роль для пользователя:"),
    Column(
        Select(
            Format("{item[1]}"),
            id="user_role_picker",
            item_id_getter=operator.itemgetter(0),
            items="roles",
            type_factory=UserRole,
            on_click=change_role_handler,
        ),
    ),
    SwitchTo(
        id="back",
        text=Const(strings.buttons.back),
        state=states.UserManager.user_info,
    ),
    getter=roles_getter,
    state=states.UserManager.change_role,
)