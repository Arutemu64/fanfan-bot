import typing

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Counter, SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.application.users.update_user_settings import (
    UpdateUserSettings,
    UpdateUserSettingsDTO,
)
from fanfan.core.models.user import FullUser
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.settings.common import ID_ITEMS_PER_PAGE_INPUT
from fanfan.presentation.tgbot.ui import strings

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def items_per_page_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    update_user_settings: UpdateUserSettings = await container.get(UpdateUserSettings)
    get_user_by_id: GetUserById = await container.get(GetUserById)
    user: FullUser = manager.middleware_data["user"]

    await update_user_settings(
        UpdateUserSettingsDTO(
            user_id=user.id,
            items_per_page=manager.find(ID_ITEMS_PER_PAGE_INPUT).get_value(),
        )
    )
    manager.middleware_data["user"] = await get_user_by_id(user.id)
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
    SwitchTo(
        text=Const(strings.buttons.back),
        id="back",
        state=states.Settings.main,
    ),
    state=states.Settings.set_items_per_page,
)
