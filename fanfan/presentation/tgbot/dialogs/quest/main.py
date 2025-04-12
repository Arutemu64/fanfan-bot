import math

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, WebApp
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format, Multi, Progress
from dishka import AsyncContainer

from fanfan.adapters.config.models import Configuration
from fanfan.application.codes.get_user_code import GetUserCode
from fanfan.application.quest.get_user_quest_details import GetUserQuestStats
from fanfan.core.models.user import UserFull
from fanfan.core.utils.code import get_qr_code_image
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.achievements import start_achievements
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings


async def quest_main_getter(
    dialog_manager: DialogManager,
    user: UserFull,
    container: AsyncContainer,
    **kwargs,
) -> dict:
    get_user_stats: GetUserQuestStats = await container.get(GetUserQuestStats)
    get_user_code: GetUserCode = await container.get(GetUserCode)
    config: Configuration = await container.get(Configuration)

    achievements_progress = 0
    user_stats = await get_user_stats(user.id)
    if user_stats.total_achievements > 0:
        achievements_progress = math.floor(
            user_stats.achievements_count * 100 / user_stats.total_achievements,
        )

    return {
        # User stats
        "points": user_stats.points,
        "achievements_count": user_stats.achievements_count,
        "achievements_progress": achievements_progress,
        "total_achievements": user_stats.total_achievements,
        # QR
        "qr_file_path": get_qr_code_image(await get_user_code()),
        "qr_scanner_url": config.web.build_qr_scanner_url() if config.web else None,
    }


async def open_achievements_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    await start_achievements(manager, manager.event.from_user.id)
    return


main_quest_window = Window(
    StaticMedia(path=Format("{qr_file_path}")),
    Title(Const(strings.titles.quest)),
    Const(
        "Во время фестиваля можно поучаствовать в разнообразных активностях "
        "и проверить глубину своего познания мира фантастики и анимации! "
    ),
    Const(" "),
    Multi(
        Format("<b>💰 Очков:</b> {points}"),
        Format("<b>🏆 Достижений:</b> {achievements_count} из {total_achievements}"),
        Progress(field="achievements_progress", filled="🟩", empty="⬜"),
    ),
    Group(
        WebApp(
            Const(strings.titles.qr_scanner),
            url=Format("{qr_scanner_url}"),
            when="qr_scanner_url",
        ),
        Button(
            text=Const("🏆 Мои достижения"),
            id="open_achievements",
            on_click=open_achievements_handler,
        ),
    ),
    Cancel(Const(strings.buttons.back)),
    getter=quest_main_getter,
    state=states.Quest.MAIN,
)
