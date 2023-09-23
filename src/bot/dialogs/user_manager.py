import operator
from typing import Any

from aiogram import Bot, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
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
from sqlalchemy.orm import undefer

from src.bot.dialogs import states
from src.bot.dialogs.common import DELETE_BUTTON
from src.bot.dialogs.widgets import Title
from src.bot.structures import UserRole
from src.bot.ui import strings
from src.db import Database
from src.db.models import User

ID_ACHIEVEMENTS_SCROLL = "achievements_scroll"

# fmt: off
AchievementsList = Jinja(  # noqa
    "{% for achievement in achievements %}"
        """<b>{{ achievement.id }}. {{ achievement.title }}</b> {{ "✅" if achievement.id in received_achievements else "" }}\n"""  # noqa
        "{% if achievement.description %}"
            "{{ achievement.description }}\n"
        "{% endif %}"
        "\n\n"
    "{% endfor %}"
)
# fmt: on


async def get_roles(**kwargs):
    return {"roles": list(map(lambda item: (item.value, item.label), UserRole))}


def points_pluralize(points: int) -> str:
    if (points % 10 == 1) and (points % 100 != 11):
        return "очков"
    elif (2 <= points % 10 <= 4) and (points % 100 < 10 or points % 100 >= 20):
        return "очка"
    else:
        return "очков"


async def user_info_getter(dialog_manager: DialogManager, db: Database, **kwargs):
    user = await db.user.get(
        dialog_manager.dialog_data["user_id"],
        options=[undefer(User.achievements_count)],
    )
    total_achievements_count = await db.achievement.get_count()
    return {
        "is_org": dialog_manager.dialog_data["role"] == UserRole.ORG,
        "user_info": [
            ("Никнейм:", user.username),
            ("ID:", user.id),
            ("Роль:", user.role.label),
            ("", ""),
            ("Очков:", user.points),
            (
                "Достижений получено:",
                f"{user.achievements_count} из {total_achievements_count}",
            ),
        ],
    }


async def achievements_getter(dialog_manager: DialogManager, db: Database, **kwargs):
    current_page = await dialog_manager.find(ID_ACHIEVEMENTS_SCROLL).get_page()
    pages = await db.achievement.get_number_of_pages(
        dialog_manager.dialog_data["achievements_per_page"]
    )
    if pages == 0:
        pages = 1
    results = await db.achievement.get_achievements_page(
        page=current_page,
        achievements_per_page=dialog_manager.dialog_data["achievements_per_page"],
        user_id=dialog_manager.dialog_data["user_id"],
    )
    if results:
        achievements, received_achievements = zip(*results)
    else:
        achievements, received_achievements = [], []
    return {
        "achievements": achievements,
        "received_achievements": received_achievements,
        "pages": pages,
    }


async def add_points(
    event: CallbackQuery,
    widget: ManagedCounter,
    dialog_manager: DialogManager,
):
    db: Database = dialog_manager.middleware_data["db"]
    bot: Bot = dialog_manager.middleware_data["bot"]

    points = int(widget.get_value())

    await db.user.add_points(
        user_id=dialog_manager.dialog_data["user_id"], points=points
    )
    await db.transaction.new(
        from_user_id=dialog_manager.event.from_user.id,
        to_user_id=dialog_manager.dialog_data["user_id"],
        points_added=points,
    )
    await db.session.commit()
    await bot.send_message(
        chat_id=dialog_manager.dialog_data["user_id"],
        text=f"💰 Вы получили {widget.get_value()} {points_pluralize(points)}!",
        reply_markup=DELETE_BUTTON.as_markup(),
    )
    await dialog_manager.switch_to(states.USER_MANAGER.MAIN)


async def add_achievement(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    db: Database = dialog_manager.middleware_data["db"]
    bot: Bot = dialog_manager.middleware_data["bot"]

    achievement = await db.achievement.get(data)
    if not achievement:
        await message.answer("⚠️ Такого достижения не существует!")
        return
    if await db.received_achievement.exists(
        user_id=dialog_manager.dialog_data["user_id"], achievement_id=data
    ):
        await message.answer("⚠️ У пользователя уже есть это достижение!")
        return

    await db.received_achievement.new(
        user_id=dialog_manager.dialog_data["user_id"], achievement_id=data
    )
    await db.transaction.new(
        from_user_id=dialog_manager.event.from_user.id,
        to_user_id=dialog_manager.dialog_data["user_id"],
        achievement_id_added=data,
    )
    await db.session.commit()
    await bot.send_message(
        chat_id=dialog_manager.dialog_data["user_id"],
        text=f"🏆 Вы получили достижение <b>{achievement.title}</b>!",
        reply_markup=DELETE_BUTTON.as_markup(),
    )
    await dialog_manager.switch_to(states.USER_MANAGER.MAIN)


async def change_user_role(
    callback: CallbackQuery, widget: Any, manager: DialogManager, item_id: str
):
    db: Database = manager.middleware_data["db"]
    user = await db.user.get(manager.dialog_data["user_id"])
    user.role = item_id
    await db.session.commit()
    try:
        await callback.bot.send_message(
            chat_id=user.id, text="🔄️ Ваша роль была изменена, перезапуск бота..."
        )
        await manager.bg(chat_id=user.id).start(
            state=states.MAIN.MAIN, mode=StartMode.RESET_STACK
        )
    except TelegramBadRequest:
        await callback.answer(
            "⚠️ Произошла ошибка при смене роли пользователю!", show_alert=True
        )
        return
    await callback.answer(f"✅ Роль пользователя @{user.username} была изменена!")
    await manager.switch_to(states.USER_MANAGER.MAIN)


async def show_user_editor(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    db: Database = dialog_manager.middleware_data["db"]
    if data.isnumeric():
        user_id = await db.user.exists(user_id=int(data))
    else:
        username = data.replace("@", "").lower()
        user_id = await db.user.exists(username=username)
    if user_id:
        dialog_manager.dialog_data["user_id"] = user_id
        await dialog_manager.switch_to(states.USER_MANAGER.MAIN)
    else:
        await message.answer(strings.errors.user_not_found)


add_points_window = Window(
    Const("<b>🔢 Укажите, сколько очков добавить пользователю</b>"),
    Const("<i>(от 5 до 50)</i>"),
    Counter(
        id="add_points_input",
        plus=Const("➕"),
        minus=Const("➖"),
        min_value=5,
        max_value=50,
        increment=5,
        default=5,
        text=Format("{value} | ✅"),
        on_text_click=add_points,
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
    AchievementsList,
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
    Title(strings.titles.user_manager),
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
    db: Database = manager.middleware_data["db"]
    manager.dialog_data["user_id"] = start_data

    user = await db.user.get(manager.event.from_user.id)
    manager.dialog_data["role"] = user.role
    manager.dialog_data["achievements_per_page"] = user.items_per_page


dialog = Dialog(
    user_manager_window,
    manual_user_search_window,
    add_points_window,
    add_achievement_window,
    role_change_window,
    on_start=on_user_manager_start,
)
