from aiogram_dialog import DialogManager
from dishka import AsyncContainer
from dishka.integrations.aiogram import CONTAINER_NAME

from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.core.dto.user import FullUserDTO
from fanfan.presentation.tgbot.middlewares.dialog_data_adapter import (
    DIALOG_DATA_ADAPTER_KEY,
    DialogDataAdapter,
)
from fanfan.presentation.tgbot.middlewares.load_current_user import (
    CURRENT_USER_KEY,
    inject_current_user,
)


async def merge_start_data(start_data: dict | None, manager: DialogManager) -> None:
    if isinstance(start_data, dict):
        manager.dialog_data.update(start_data)


def get_container(dialog_manager: DialogManager) -> AsyncContainer:
    return dialog_manager.middleware_data[CONTAINER_NAME]


def get_dialog_data_adapter(dialog_manager: DialogManager) -> DialogDataAdapter:
    return dialog_manager.middleware_data[DIALOG_DATA_ADAPTER_KEY]


def get_current_user(dialog_manager: DialogManager) -> FullUserDTO:
    return dialog_manager.middleware_data[CURRENT_USER_KEY]


async def refresh_current_user(dialog_manager: DialogManager) -> None:
    container = get_container(dialog_manager)
    current_user = get_current_user(dialog_manager)
    get_user_by_id = await container.get(GetUserById)
    current_user = await get_user_by_id(current_user.id)
    inject_current_user(dialog_manager.middleware_data, current_user)
