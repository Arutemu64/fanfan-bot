import math

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja, Progress
from dishka import AsyncContainer

from fanfan.application.quest.get_user_quest_details import GetUserQuestStats
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.achievements import start_achievements
from fanfan.presentation.tgbot.dialogs.common.predicates import is_org
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings

from .common import DATA_USER_ID, managed_user_getter


async def user_info_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    managed_user_id = dialog_manager.start_data[DATA_USER_ID]
    get_user_quest_details: GetUserQuestStats = await container.get(GetUserQuestStats)

    user_stats = await get_user_quest_details(managed_user_id)
    achievements_progress = 0
    if user_stats.total_achievements > 0:
        achievements_progress = math.floor(
            user_stats.achievements_count * 100 / user_stats.total_achievements,
        )
    return {
        "points": user_stats.points,
        "achievements_count": user_stats.achievements_count,
        "achievements_progress": achievements_progress,
        "total_achievements_count": user_stats.total_achievements,
        "quest_registration": user_stats.quest_registration,
    }


async def open_user_achievements_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    await start_achievements(manager, manager.start_data[DATA_USER_ID], add_mode=True)


user_info_window = Window(
    Title(Const(strings.titles.user_manager)),
    Jinja("<b>Никнейм:</b> {{ managed_user.username|e }}"),
    Jinja("<b>ID:</b> {{ managed_user.id }}"),
    Jinja(
        "<b>Билет:</b> {{ managed_user.ticket.id "
        "if managed_user.ticket else 'не привязан' }}"
    ),
    Jinja("<b>Роль:</b> {{ managed_user.role }}"),
    Jinja("<b>Регистрация на квест:</b> {{ '✅' if quest_registration else '❌' }}"),
    Const(" "),
    Jinja("<b>💰 Очков</b>: {{ points }} "),
    Jinja(
        "<b>🏆 Достижений</b>: {{ achievements_count }} "
        "из {{ total_achievements_count }}",
    ),
    Progress("achievements_progress", filled="🟩", empty="⬜"),
    Button(
        text=Const("🏆 Достижения"),
        id="show_achievements",
        on_click=open_user_achievements_handler,
    ),
    SwitchTo(
        Const("💰 Добавить очков"),
        id="open_add_points",
        state=states.UserManager.set_points,
    ),
    SwitchTo(
        text=Const("✏️ Изменить роль"),
        id="change_user_role",
        state=states.UserManager.change_role,
        when=is_org,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.UserManager.user_info,
    getter=[user_info_getter, managed_user_getter],
)
