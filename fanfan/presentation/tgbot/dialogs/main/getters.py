import math

from aiogram_dialog import DialogManager

from fanfan.application.dto.user import FullUserDTO
from fanfan.application.holder import AppHolder
from fanfan.common.enums import BotMode
from fanfan.config import get_config


async def main_menu_getter(
    dialog_manager: DialogManager,
    app: AppHolder,
    user: FullUserDTO,
    **kwargs,
):
    config = get_config()
    settings = await app.settings.get_settings()
    user_stats = None
    achievements_progress = 0
    if user.ticket:
        user_stats = await app.quest.get_user_stats(user.id)
        if user_stats.total_achievements > 0:
            achievements_progress = math.floor(
                user_stats.achievements_count * 100 / user_stats.total_achievements,
            )
    return {
        # Stats
        "achievements_count": user_stats.achievements_count if user_stats else None,
        "achievements_progress": achievements_progress if user_stats else None,
        "total_achievements": user_stats.total_achievements if user_stats else None,
        # Settings
        "voting_enabled": settings.voting_enabled,
        "webapp_link": config.web.build_qr_scanner_url()
        if config.web.mode is BotMode.WEBHOOK
        else None,
        # Most important thing ever
        "random_quote": await app.common.get_random_quote(),
    }
