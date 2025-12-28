from aiogram import Router
from aiogram_dialog import Dialog, DialogManager

from fanfan.core.vo.user import UserId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.achievements.list_achievements import (
    list_achievements_window,
)
from fanfan.presentation.tgbot.dialogs.common.utils import (
    get_current_user,
    merge_start_data,
)

achievements_router = Router(name="achievements_router")


async def start_achievements(manager: DialogManager, user_id: UserId | None = None):
    current_user = get_current_user(manager)
    await manager.start(
        state=states.Achievements.LIST_ACHIEVEMENTS,
        data={
            "user_id": user_id or current_user.id,
        },
    )


achievements_dialog = Dialog(list_achievements_window, on_start=merge_start_data)
achievements_router.include_routers(achievements_dialog)
