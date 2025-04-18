import operator
import typing
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Column, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from fanfan.application.users.update_user import UpdateUser
from fanfan.core.models.user import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.getters import roles_getter
from fanfan.presentation.tgbot.static import strings

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

    await update_user.change_role(user_id=manager.start_data[DATA_USER_ID], role=data)
    await callback.answer(strings.common.success)
    await manager.switch_to(states.UserManager.USER_INFO)


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
        state=states.UserManager.USER_INFO,
    ),
    getter=roles_getter,
    state=states.UserManager.CHANGE_ROLE,
)
