import operator
from typing import Any

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Column,
    Counter,
    CurrentPage,
    FirstPage,
    LastPage,
    ManagedCounter,
    NextPage,
    PrevPage,
    Row,
    Select,
    StubScroll,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja, List

from fanfan.application.dto.user import FullUserDTO, UpdateUserDTO
from fanfan.application.exceptions import ServiceError
from fanfan.application.services import ServicesHolder
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
    dialog_manager: DialogManager, user: FullUserDTO, services: ServicesHolder, **kwargs
):
    managed_user = await services.users.get_user_by_id(
        dialog_manager.dialog_data[DATA_MANAGED_USER_ID]
    )
    user_stats = await services.quest.get_user_stats(managed_user.id)
    return {
        "is_org": user.role is UserRole.ORG,
        "user_info": [
            ("Никнейм:", managed_user.username),
            ("ID:", managed_user.id),
            (
                "Билет:",
                managed_user.ticket.id if managed_user.ticket else "не привязан",
            ),
            ("Роль:", managed_user.role.label),
            ("", ""),
            ("Очков:", user_stats.points),
            (
                "Достижений получено:",
                f"{user_stats.achievements_count} "
                f"из {user_stats.total_achievements}",
            ),
        ],
    }


async def achievements_getter(
    dialog_manager: DialogManager, user: FullUserDTO, services: ServicesHolder, **kwargs
):
    page = await services.quest.get_achievements_page(
        page=await dialog_manager.find(ID_ACHIEVEMENTS_SCROLL).get_page(),
        achievements_per_page=user.items_per_page,
        user_id=dialog_manager.dialog_data[DATA_MANAGED_USER_ID],
    )
    return {
        "achievements": page.items,
        "pages": page.total,
        "show_ids": True,
    }


async def add_points_handler(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    services: ServicesHolder = manager.middleware_data["services"]
    counter: ManagedCounter = manager.find(ID_ADD_POINTS_COUNTER)

    try:
        await services.quest.add_points(
            user_id=manager.dialog_data[DATA_MANAGED_USER_ID],
            amount=int(counter.get_value()),
        )
    except ServiceError as e:
        await callback.answer(e.message, show_alert=True)
        return

    await callback.answer(strings.common.success)
    await manager.switch_to(states.USER_MANAGER.MAIN)


async def add_achievement_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    services: ServicesHolder = dialog_manager.middleware_data["services"]
    try:
        await services.quest.add_achievement(
            user_id=dialog_manager.dialog_data[DATA_MANAGED_USER_ID],
            achievement_id=data,
        )
    except ServiceError as e:
        await message.reply(e.message)
        return

    await message.reply(strings.common.success)
    await dialog_manager.switch_to(states.USER_MANAGER.MAIN)


async def change_user_role_handler(
    callback: CallbackQuery,
    widget: Any,
    manager: DialogManager,
    data: UserRole,
):
    services: ServicesHolder = manager.middleware_data["services"]

    try:
        await services.users.update_user(
            UpdateUserDTO(
                id=manager.dialog_data[DATA_MANAGED_USER_ID],
                role=data,
            )
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
    services: ServicesHolder = dialog_manager.middleware_data["services"]

    if data.isnumeric():
        try:
            user = await services.users.get_user_by_id(int(data))
        except ServiceError as e:
            await message.answer(e.message)
            return
    else:
        try:
            user = await services.users.get_user_by_username(data)
        except ServiceError as e:
            await message.answer(e.message)
            return
    await dialog_manager.start(states.USER_MANAGER.MAIN, data=user.id)


add_points_window = Window(
    Const("<b>🔢 Укажите, сколько очков добавить пользователю</b>"),
    Const("<i>(от 5 до 50)</i>"),
    Counter(
        id=ID_ADD_POINTS_COUNTER,
        plus=Const("➕"),
        minus=Const("➖"),
        min_value=5,
        max_value=50,
        increment=5,
        default=5,
    ),
    Button(
        text=Const("✅ Добавить"),
        id="add_points",
        on_click=add_points_handler,
    ),
    SwitchTo(
        text=Const(strings.buttons.back),
        id="back",
        state=states.USER_MANAGER.MAIN,
    ),
    state=states.USER_MANAGER.ADD_POINTS,
)

add_achievement_window = Window(
    Const("⌨️ Укажите достижение, которое получит пользователь:\n"),
    Jinja(achievements_list),
    TextInput(
        id="achievement_id_input",
        type_factory=int,
        on_success=add_achievement_handler,
    ),
    StubScroll(id=ID_ACHIEVEMENTS_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_ACHIEVEMENTS_SCROLL, text=Format(text="{current_page1}/{pages}")
        ),
        NextPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("⏭️")),
        when=F["pages"] != 1,
    ),
    SwitchTo(
        id="back", text=Const(strings.buttons.back), state=states.USER_MANAGER.MAIN
    ),
    state=states.USER_MANAGER.ADD_ACHIEVEMENT,
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
        id="back", text=Const(strings.buttons.back), state=states.USER_MANAGER.MAIN
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
    List(Format("<b>{item[0]}</b> {item[1]}"), items="user_info"),
    SwitchTo(
        text=Const("🪙 Добавить очков"),
        id="add_points",
        state=states.USER_MANAGER.ADD_POINTS,
    ),
    SwitchTo(
        text=Const("🏆 Засчитать достижение"),
        id="add_achievement",
        state=states.USER_MANAGER.ADD_ACHIEVEMENT,
    ),
    SwitchTo(
        text=Const("✏️ Изменить роль пользователя"),
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
    add_points_window,
    add_achievement_window,
    role_change_window,
    on_start=on_user_manager_start,
)
