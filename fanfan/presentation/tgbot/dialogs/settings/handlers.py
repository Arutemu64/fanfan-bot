from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from fanfan.application.dto.user import FullUserDTO, UpdateUserSettingsDTO
from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.presentation.tgbot import states

from .constants import ID_ITEMS_PER_PAGE_INPUT


async def update_counter_value_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    user: FullUserDTO = manager.middleware_data["user"]
    await manager.find(ID_ITEMS_PER_PAGE_INPUT).set_value(user.settings.items_per_page)


async def items_per_page_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    app: AppHolder = manager.middleware_data["app"]
    user: FullUserDTO = manager.middleware_data["user"]
    try:
        await app.users.update_user_settings(
            UpdateUserSettingsDTO(
                user_id=manager.event.from_user.id,
                items_per_page=manager.find(ID_ITEMS_PER_PAGE_INPUT).get_value(),
            ),
        )
        manager.middleware_data["user"] = await app.users.get_user_by_id(user.id)
    except ServiceError as e:
        await callback.answer(e.message)
        return
    await callback.answer("✅ Успешно!")
    await manager.switch_to(state=states.SETTINGS.MAIN)
