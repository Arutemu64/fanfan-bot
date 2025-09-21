import operator
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Column, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.users.update_user import UpdateUser
from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.getters import roles_getter
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.static import strings

from .data import UserManagerDialogData


@inject
async def change_role_handler(
    callback: CallbackQuery,
    widget: Any,
    manager: DialogManager,
    data: UserRole,
    update_user: FromDishka[UpdateUser],
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(UserManagerDialogData)
    await update_user.set_role(user_id=dialog_data.selected_user_id, role=data)
    await callback.answer(strings.common.success)
    await manager.switch_to(states.UserManager.USER_INFO)


change_role_window = Window(
    Const("✔️ Выберите роль для пользователя:"),
    Column(
        Select(
            Jinja("{{ item[1] }}"),
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
