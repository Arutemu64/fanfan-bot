import math

from aiogram_dialog import DialogManager

from fanfan.application.dto.user import FullUserDTO
from fanfan.application.holder import AppHolder

from .constants import (
    DATA_MANAGED_USER_ID,
    ID_ACHIEVEMENTS_SCROLL,
)


async def user_info_getter(
    dialog_manager: DialogManager,
    user: FullUserDTO,
    app: AppHolder,
    **kwargs,
):
    managed_user = await app.users.get_user_by_id(
        dialog_manager.dialog_data[DATA_MANAGED_USER_ID],
    )
    user_stats = await app.quest.get_user_stats(managed_user.id)
    achievements_progress = 0
    if user_stats.total_achievements > 0:
        achievements_progress = math.floor(
            user_stats.achievements_count * 100 / user_stats.total_achievements,
        )
    return {
        "managed_user_username": managed_user.username,
        "managed_user_id": managed_user.id,
        "managed_user_ticket_id": managed_user.ticket.id
        if managed_user.ticket
        else "билет не привязан",
        "managed_user_role": managed_user.role.label,
        "managed_user_achievements_count": user_stats.achievements_count,
        "managed_user_achievements_progress": achievements_progress,
        "total_achievements_count": user_stats.total_achievements,
    }


async def achievements_getter(
    dialog_manager: DialogManager,
    user: FullUserDTO,
    app: AppHolder,
    **kwargs,
):
    page = await app.quest.get_achievements_page(
        page_number=await dialog_manager.find(ID_ACHIEVEMENTS_SCROLL).get_page(),
        achievements_per_page=user.settings.items_per_page,
        user_id=dialog_manager.dialog_data[DATA_MANAGED_USER_ID],
    )
    return {
        "achievements": page.items,
        "pages": page.total_pages,
    }
