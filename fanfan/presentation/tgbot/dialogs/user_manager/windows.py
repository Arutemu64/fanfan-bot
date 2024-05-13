import operator

from aiogram import F
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Column, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, Progress

from fanfan.common.enums import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.getters import (
    CURRENT_USER,
    current_user_getter,
    roles_getter,
)
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings

from .getters import user_info_getter
from .handlers import (
    change_user_role_handler,
    open_user_achievements_handler,
    show_user_editor_handler,
)

role_change_window = Window(
    Const("✔️ Выберите роль для пользователя:"),
    Column(
        Select(
            Format("{item[1]}"),
            id="user_role_picker",
            item_id_getter=operator.itemgetter(0),
            items="roles",
            type_factory=UserRole,
            on_click=change_user_role_handler,
        ),
    ),
    SwitchTo(
        id="back",
        text=Const(strings.buttons.back),
        state=states.USER_MANAGER.MAIN,
    ),
    getter=roles_getter,
    state=states.USER_MANAGER.CHANGE_ROLE,
)
manual_user_search_window = Window(
    Const("⌨️ Напишите @никнейм или ID пользователя"),
    TextInput(
        id="manual_user_search_input",
        type_factory=str,
        on_success=show_user_editor_handler,
    ),
    Cancel(id="back", text=Const(strings.buttons.back)),
    state=states.USER_MANAGER.MANUAL_USER_SEARCH,
)
user_manager_window = Window(
    Title(Const(strings.titles.user_manager)),
    Format("<b>Никнейм:</b> {managed_user_username}"),
    Format("<b>ID:</b> {managed_user_id}"),
    Format("<b>Билет:</b> {managed_user_ticket_id}"),
    Format("<b>Роль:</b> {managed_user_role}"),
    Const(" "),
    Format(
        "<b>🏆 Достижений</b>: {managed_user_achievements_count} "
        "из {total_achievements_count}"
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
        state=states.USER_MANAGER.CHANGE_ROLE,
        when=F[CURRENT_USER].role.is_(UserRole.ORG),
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.USER_MANAGER.MAIN,
    getter=[user_info_getter, current_user_getter],
)
