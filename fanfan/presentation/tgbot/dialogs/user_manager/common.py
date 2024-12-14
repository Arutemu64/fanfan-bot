from aiogram_dialog import DialogManager
from dishka import AsyncContainer

from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.core.models.user import FullUser

DATA_USER_ID = "user_id"
MANAGED_USER = "managed_user"


async def managed_user_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
) -> dict[str, FullUser]:
    get_user_by_id: GetUserById = await container.get(GetUserById)
    managed_user = await get_user_by_id(
        dialog_manager.start_data[DATA_USER_ID],
    )
    return {MANAGED_USER: managed_user}
