import math
import operator
from typing import Any

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Cancel,
    Column,
    CurrentPage,
    FirstPage,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    Select,
    StubScroll,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja, Progress

from fanfan.application.dto.user import FullUserDTO, UpdateUserDTO
from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.common.enums import UserRole
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.getters import get_roles
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.static.templates import achievements_list
from fanfan.presentation.tgbot.ui import strings

ID_ACHIEVEMENTS_SCROLL = "achievements_scroll"
ID_ADD_POINTS_COUNTER = "add_points_counter"

DATA_MANAGED_USER_ID = "managed_user_id"


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
        "is_org": user.role is UserRole.ORG,
        # Managed user info
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
        achievements_per_page=user.items_per_page,
        user_id=dialog_manager.dialog_data[DATA_MANAGED_USER_ID],
    )
    return {
        "achievements": page.items,
        "pages": page.total_pages,
    }


async def change_user_role_handler(
    callback: CallbackQuery,
    widget: Any,
    manager: DialogManager,
    data: UserRole,
):
    app: AppHolder = manager.middleware_data["app"]

    try:
        await app.users.update_user(
            UpdateUserDTO(
                id=manager.dialog_data[DATA_MANAGED_USER_ID],
                role=data,
            ),
        )
    except ServiceError as e:
        await callback.answer(e.message, show_alert=True)
        return

    await callback.answer(strings.common.success)
    await manager.switch_to(states.USER_MANAGER.MAIN)


async def show_user_editor_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    app: AppHolder = dialog_manager.middleware_data["app"]

    if data.isnumeric():
        try:
            user = await app.users.get_user_by_id(int(data))
        except ServiceError as e:
            await message.answer(e.message)
            return
    else:
        try:
            user = await app.users.get_user_by_username(data)
        except ServiceError as e:
            await message.answer(e.message)
            return
    await dialog_manager.start(states.USER_MANAGER.MAIN, data=user.id)


achievements_list_window = Window(
    Title(Const("🏆 Достижения участника")),
    Jinja(achievements_list),
    StubScroll(id=ID_ACHIEVEMENTS_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_ACHIEVEMENTS_SCROLL,
            text=Format(text="{current_page1}/{pages}"),
        ),
        NextPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("⏭️")),
        when=F["pages"] != 1,
    ),
    SwitchTo(
        id="back",
        text=Const(strings.buttons.back),
        state=states.USER_MANAGER.MAIN,
    ),
    state=states.USER_MANAGER.ACHIEVEMENTS_LIST,
    getter=achievements_getter,
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
    getter=get_roles,
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
    SwitchTo(
        text=Const("🏆 Достижения"),
        id="add_achievement",
        state=states.USER_MANAGER.ACHIEVEMENTS_LIST,
    ),
    SwitchTo(
        text=Const("✏️ Изменить роль"),
        id="change_user_role",
        state=states.USER_MANAGER.CHANGE_ROLE,
        when="is_org",
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.USER_MANAGER.MAIN,
    getter=user_info_getter,
)


async def on_user_manager_start(start_data: int, manager: DialogManager):
    manager.dialog_data[DATA_MANAGED_USER_ID] = start_data


dialog = Dialog(
    user_manager_window,
    manual_user_search_window,
    achievements_list_window,
    role_change_window,
    on_start=on_user_manager_start,
)
