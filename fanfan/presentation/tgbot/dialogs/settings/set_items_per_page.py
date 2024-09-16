import typing

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Counter
from aiogram_dialog.widgets.text import Const

from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.application.users.update_user import (
    UpdateUser,
    UpdateUserDTO,
    UpdateUserSettingsDTO,
)
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.user import FullUserDTO
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.settings.common import ID_ITEMS_PER_PAGE_INPUT

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def items_per_page_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    update_user = await container.get(UpdateUser)
    get_user_by_id = await container.get(GetUserById)
    user: FullUserDTO = manager.middleware_data["user"]

    try:
        await update_user(
            UpdateUserDTO(
                id=user.id,
                settings=UpdateUserSettingsDTO(
                    items_per_page=manager.find(ID_ITEMS_PER_PAGE_INPUT).get_value(),
                ),
            ),
        )
        manager.middleware_data["user"] = await get_user_by_id(user.id)
    except AppException as e:
        await callback.answer(e.message)
        return
    await callback.answer("✅ Успешно!")
    await manager.switch_to(state=states.Settings.main)


items_per_page_window = Window(
    Const(
        "🔢 <b>Укажите, сколько выступлений/участников выводить "
        "на одной странице</b> <i>(от 3 до 10)</i>",
    ),
    Counter(
        id=ID_ITEMS_PER_PAGE_INPUT,
        plus=Const("➕"),
        minus=Const("➖"),
        min_value=3,
        max_value=10,
    ),
    Button(
        text=Const("💾 Сохранить"),
        id="save_items_per_page",
        on_click=items_per_page_handler,
    ),
    state=states.Settings.set_items_per_page,
)
