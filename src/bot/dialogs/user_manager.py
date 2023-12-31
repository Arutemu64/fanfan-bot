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
from arq import ArqRedis

from src.bot.dialogs import states
from src.bot.dialogs.getters import get_roles
from src.bot.dialogs.templates import achievements_list
from src.bot.dialogs.widgets import Title
from src.bot.structures import Notification, UserRole
from src.bot.ui import strings
from src.db import Database
from src.db.models import DBUser

ID_ACHIEVEMENTS_SCROLL = "achievements_scroll"
ID_ADD_POINTS_COUNTER = "add_points_counter"


def points_pluralize(points: int) -> str:
    if (points % 10 == 1) and (points % 100 != 11):
        return "очков"
    elif (2 <= points % 10 <= 4) and (points % 100 < 10 or points % 100 >= 20):
        return "очка"
    else:
        return "очков"


async def user_info_getter(
    dialog_manager: DialogManager, db: Database, current_user: DBUser, **kwargs
):
    user = await db.user.get(dialog_manager.dialog_data["user_id"])
    total_achievements_count = await db.achievement.get_count()
    return {
        "is_org": current_user.role is UserRole.ORG,
        "user_info": [
            ("Никнейм:", user.username),
            ("ID:", user.id),
            (
                "Билет:",
                current_user.ticket.id if current_user.ticket else "не привязан",
            ),
            ("Роль:", user.role.label),
            ("", ""),
            ("Очков:", user.points),
            (
                "Достижений получено:",
                f"{await user.awaitable_attrs.achievements_count} "
                f"из {total_achievements_count}",
            ),
        ],
    }


async def achievements_getter(dialog_manager: DialogManager, db: Database, **kwargs):
    user = await db.user.get(dialog_manager.dialog_data["user_id"])
    page = await db.achievement.paginate(
        page=await dialog_manager.find(ID_ACHIEVEMENTS_SCROLL).get_page(),
        achievements_per_page=user.items_per_page,
    )
    received_achievements = await db.achievement.check_user_achievements(
        user, page.items
    )
    return {
        "achievements": page.items,
        "pages": page.total,
        "received_achievements": received_achievements,
        "show_ids": True,
    }


async def add_points(callback: CallbackQuery, button: Button, manager: DialogManager):
    db: Database = manager.middleware_data["db"]
    arq: ArqRedis = manager.middleware_data["arq"]
    counter: ManagedCounter = manager.find(ID_ADD_POINTS_COUNTER)
    user: DBUser = await db.user.get(manager.dialog_data["user_id"])

    points = int(counter.get_value())
    user.points += points
    await db.transaction.new(
        from_user=manager.middleware_data["current_user"],
        to_user=user,
        points_added=points,
    )
    await db.session.commit()

    await arq.enqueue_job(
        "send_notification",
        Notification(
            user_id=manager.dialog_data["user_id"],
            text=f"💰 Вы получили {points} {points_pluralize(points)}!",
        ),
    )
    await callback.answer(strings.common.success)
    await manager.switch_to(states.USER_MANAGER.MAIN)


async def add_achievement(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    db: Database = dialog_manager.middleware_data["db"]
    arq: ArqRedis = dialog_manager.middleware_data["arq"]
    user: DBUser = await db.user.get(dialog_manager.dialog_data["user_id"])

    achievement = await db.achievement.get(data)
    if not achievement:
        await message.reply("⚠️ Такого достижения не существует!")
        return
    await user.awaitable_attrs.received_achievements
    if achievement in user.received_achievements:
        await message.reply("⚠️ У пользователя уже есть это достижение!")
        return
    user.received_achievements.append(achievement)
    await db.transaction.new(
        from_user=dialog_manager.middleware_data["current_user"],
        to_user=user,
        achievement_added=achievement,
    )
    await db.session.commit()

    await arq.enqueue_job(
        "send_notification",
        Notification(
            user_id=dialog_manager.dialog_data["user_id"],
            text=f"🏆 Вы получили достижение <b>{achievement.title}</b>!",
        ),
    )
    await message.reply(strings.common.success)
    await dialog_manager.switch_to(states.USER_MANAGER.MAIN)


async def change_user_role(
    callback: CallbackQuery,
    widget: Any,
    manager: DialogManager,
    item_id: int,
):
    db: Database = manager.middleware_data["db"]
    arq: ArqRedis = manager.middleware_data["arq"]
    user: DBUser = await db.user.get(manager.dialog_data["user_id"])

    user.role = UserRole(item_id)
    await db.session.commit()

    await arq.enqueue_job(
        "send_notification",
        Notification(
            user_id=manager.dialog_data["user_id"],
            text=f"✏️ Ваша роль была изменена на <b>{user.role.label}</b>!",
        ),
    )
    await callback.answer(strings.common.success)
    await manager.switch_to(states.USER_MANAGER.MAIN)


async def show_user_editor(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    db: Database = dialog_manager.middleware_data["db"]
    if data.isnumeric():
        user = await db.user.get(int(data))
    else:
        user = await db.user.get_by_username(data)
    if user:
        dialog_manager.dialog_data["user_id"] = user.id
        await dialog_manager.switch_to(states.USER_MANAGER.MAIN)
    else:
        await message.answer(strings.errors.user_not_found)


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
        on_click=add_points,
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
        on_success=add_achievement,
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
            type_factory=int,
            on_click=change_user_role,
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
        on_success=show_user_editor,
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
    manager.dialog_data["user_id"] = start_data


dialog = Dialog(
    user_manager_window,
    manual_user_search_window,
    add_points_window,
    add_achievement_window,
    role_change_window,
    on_start=on_user_manager_start,
)
