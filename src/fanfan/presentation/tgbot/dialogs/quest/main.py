import math

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, SwitchTo, WebApp
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format, Jinja, Progress
from dishka import AsyncContainer

from fanfan.application.quest.read_user_quest_details import GetUserQuestStats
from fanfan.core.models.user import UserData
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.achievements import start_achievements
from fanfan.presentation.tgbot.dialogs.common.qr import (
    qr_scanner_url_getter,
    user_qr_path_getter,
)
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings


async def quest_main_getter(
    dialog_manager: DialogManager,
    user: UserData,
    container: AsyncContainer,
    **kwargs,
) -> dict:
    get_user_stats: GetUserQuestStats = await container.get(GetUserQuestStats)

    achievements_progress = 0
    user_stats = await get_user_stats(user.id)
    if user_stats.total_achievements > 0:
        achievements_progress = math.floor(
            user_stats.achievements_count * 100 / user_stats.total_achievements,
        )

    return {
        "points": user_stats.points,
        "achievements_count": user_stats.achievements_count,
        "rank": user_stats.rank,
        "achievements_progress": achievements_progress,
        "total_achievements": user_stats.total_achievements,
    }


async def open_achievements_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    await start_achievements(manager, manager.event.from_user.id)
    return


main_quest_window = Window(
    StaticMedia(path=Format("{user_qr_path}")),
    Title(Const(strings.titles.quest)),
    Const(
        "⚔️ Во время фестиваля можно поучаствовать в разнообразных активностях "
        "и проверить глубину своего познания мира фантастики и анимации!\n\n"
        "📸 Ищи и сканируй QR-коды на территории фестиваля, чтобы получать достижения."
    ),
    Const(" "),
    Jinja("🏆 Ты на <b>№{{rank}}</b> месте в рейтинге", when="rank"),
    Jinja("<b>💰 Очков:</b> {{ points }}"),
    Jinja("<b>🎯 Достижений:</b> {{ achievements_count }} из {{ total_achievements }}"),
    Progress(field="achievements_progress", filled="🟩", empty="⬜"),
    WebApp(
        Const(strings.buttons.open_qr_scanner),
        url=Format("{qr_scanner_url}"),
        when="qr_scanner_url",
    ),
    Group(
        Button(
            text=Const("🏆 Мои достижения"),
            id="open_achievements",
            on_click=open_achievements_handler,
        ),
        SwitchTo(Const(strings.titles.rating), state=states.Quest.RATING, id="rating"),
        width=2,
    ),
    Cancel(Const(strings.buttons.back)),
    getter=[quest_main_getter, qr_scanner_url_getter, user_qr_path_getter],
    state=states.Quest.MAIN,
)
