import math

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, Jinja, Progress
from dishka import AsyncContainer

from fanfan.application.quest.get_user_stats import GetUserStats
from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.achievements import start_achievements
from fanfan.presentation.tgbot.dialogs.common.predicates import is_org
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings

from .common import DATA_USER_ID


async def user_info_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    get_user_by_id = await container.get(GetUserById)
    get_user_stats = await container.get(GetUserStats)

    managed_user = await get_user_by_id(
        dialog_manager.start_data[DATA_USER_ID],
    )
    user_stats = await get_user_stats(managed_user.id)
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


async def open_user_achievements_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    await start_achievements(manager, manager.start_data[DATA_USER_ID])


user_info_window = Window(
    Title(Const(strings.titles.user_manager)),
    Jinja("<b>Никнейм:</b> {{ managed_user_username|e }}"),
    Format("<b>ID:</b> {managed_user_id}"),
    Format("<b>Билет:</b> {managed_user_ticket_id}"),
    Format("<b>Роль:</b> {managed_user_role}"),
    Const(" "),
    Format(
        "<b>🏆 Достижений</b>: {managed_user_achievements_count} "
        "из {total_achievements_count}",
    ),
    Progress("managed_user_achievements_progress", filled="🟩", empty="⬜"),
    Button(
        text=Const("🏆 Достижения"),
        id="show_achievements",
        on_click=open_user_achievements_handler,
    ),
    SwitchTo(
        text=Const("✏️ Изменить роль"),
        id="change_user_role",
        state=states.UserManager.change_role,
        when=is_org,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.UserManager.main,
    getter=user_info_getter,
)
