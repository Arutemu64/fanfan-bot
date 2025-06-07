from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import AsyncContainer

from fanfan.application.quest.read_user_quest_details import GetUserQuestStatus
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.achievements import start_achievements
from fanfan.presentation.tgbot.dialogs.common.predicates import is_org
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings

from .common import DATA_USER_ID, managed_user_getter


async def view_user_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    managed_user_id = dialog_manager.start_data[DATA_USER_ID]
    get_user_quest_details: GetUserQuestStatus = await container.get(GetUserQuestStatus)
    user_stats = await get_user_quest_details(managed_user_id)
    return {
        "points": user_stats.points,
        "achievements_count": user_stats.achievements_count,
        "total_achievements_count": user_stats.total_achievements,
        "rank": user_stats.rank,
        "can_participate_in_quest": user_stats.can_participate_in_quest,
    }


async def open_user_achievements_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    await start_achievements(manager, manager.start_data[DATA_USER_ID])


view_user_window = Window(
    Title(Const(strings.titles.user_manager)),
    Jinja(
        "<b>👤 Никнейм:</b> {% if managed_user.username %}"
        "@{{ managed_user.username|e }}"
        "{% else %}"
        "не задан"
        "{% endif %}"
    ),
    Jinja("<b>🆔 ID:</b> <code>{{ managed_user.id }}</code>"),
    Jinja(
        "<b>🎫 Билет:</b> {% if managed_user.ticket %}"
        "<code>{{ managed_user.ticket.id }}</code>"
        "{% else %}"
        "не привязан"
        "{% endif %}"
    ),
    Jinja("<b>🧩 Роль:</b> {{ managed_user.role }}"),
    Const(" "),
    Jinja(
        "<b>⚔️ Может участвовать в квесте:</b> "
        "{{ '✅' if can_participate_in_quest else '❌' }}"
    ),
    Jinja("<b>💰 Очков</b>: {{ points }} "),
    Jinja(
        "<b>🎯 Достижений</b>: {{ achievements_count }} "
        "из {{ total_achievements_count }}",
    ),
    Jinja("🏆 На <b>№{{rank}}</b> месте в рейтинге", when="rank"),
    Button(
        text=Const("🎯 Достижения"),
        id="show_achievements",
        on_click=open_user_achievements_handler,
    ),
    SwitchTo(
        Const("💰 Добавить очков"),
        id="open_add_points",
        state=states.UserManager.SET_POINTS,
    ),
    SwitchTo(
        text=Const(strings.titles.send_message),
        id="send_message",
        state=states.UserManager.SEND_MESSAGE,
        when=is_org,
    ),
    SwitchTo(
        text=Const("🧩 Изменить роль"),
        id="change_user_role",
        state=states.UserManager.CHANGE_ROLE,
        when=is_org,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.UserManager.USER_INFO,
    getter=[view_user_getter, managed_user_getter],
)
