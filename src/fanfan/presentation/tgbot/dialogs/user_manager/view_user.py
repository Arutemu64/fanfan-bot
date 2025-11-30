from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.quest.get_user_quest_status import GetUserQuestStatus
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.achievements import start_achievements
from fanfan.presentation.tgbot.dialogs.common.predicates import is_org
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.middlewares.dialog_data_adapter import DialogDataAdapter
from fanfan.presentation.tgbot.static import strings

from .common import selected_user_getter
from .data import UserManagerDialogData


@inject
async def view_user_getter(
    dialog_manager: DialogManager,
    dialog_data_adapter: DialogDataAdapter,
    get_user_quest_details: FromDishka[GetUserQuestStatus],
    **kwargs,
):
    dialog_data = dialog_data_adapter.load(UserManagerDialogData)
    user_stats = await get_user_quest_details(dialog_data.selected_user_id)
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
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(UserManagerDialogData)
    await start_achievements(manager, dialog_data.selected_user_id)


view_user_window = Window(
    Title(Const(strings.titles.user_manager)),
    Jinja(
        "<b>👤 Никнейм:</b> {% if selected_user_username %}"
        "@{{ selected_user_username|e }}"
        "{% else %}"
        "не задан"
        "{% endif %}"
    ),
    Jinja("<b>🆔 ID:</b> <code>{{ selected_user_id }}</code>"),
    Jinja("<b>🎫 Билет:</b> {{ selected_user_ticket_id or 'не привязан' }}"),
    Jinja("<b>🧩 Роль:</b> {{ selected_user_role }}"),
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
    getter=[view_user_getter, selected_user_getter],
)
