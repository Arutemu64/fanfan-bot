from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Counter, ManagedCounter, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, List

from src.bot.dialogs import states
from src.bot.dialogs.widgets import Title
from src.bot.ui import strings
from src.db import Database
from src.db.models import ReceivedAchievement

ID_ITEMS_PER_PAGE_INPUT = "items_per_page_input"


async def user_info_getter(dialog_manager: DialogManager, db: Database, **kwargs):
    user = await db.user.get(dialog_manager.event.from_user.id)
    return {
        "user": user,
        "user_info_list": [
            ("Никнейм:", user.username),
            ("ID:", user.id),
            ("Роль:", user.role.label),
        ],
    }


async def update_counter_value(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    db: Database = manager.middleware_data["db"]
    await manager.find(ID_ITEMS_PER_PAGE_INPUT).set_value(
        await db.user.get_items_per_page(manager.event.from_user.id)
    )


async def update_items_per_page(
    event: CallbackQuery,
    widget: ManagedCounter,
    dialog_manager: DialogManager,
):
    db: Database = dialog_manager.middleware_data["db"]
    await db.user.set_items_per_page(
        dialog_manager.event.from_user.id, int(widget.get_value())
    )
    await db.session.commit()
    await event.answer("✅ Успешно!")
    await dialog_manager.switch_to(state=states.SETTINGS.MAIN)


async def reset_achievements_and_points(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    db: Database = manager.middleware_data["db"]
    await db.user.set_points(user_id=manager.event.from_user.id, points=0)
    achievements = await db.received_achievement._get_many(
        ReceivedAchievement.user_id == manager.event.from_user.id
    )
    for achievement in achievements:
        await db.session.delete(achievement)
    await db.session.commit()
    await callback.answer("✅ Успешно!")


set_items_per_page_window = Window(
    Const(
        "🔢 <b>Укажите, сколько выступлений/участников выводить "
        "на одной странице</b> <i>(от 3 до 10)</i>"
    ),
    Counter(
        id=ID_ITEMS_PER_PAGE_INPUT,
        plus=Const("➕"),
        minus=Const("➖"),
        min_value=3,
        max_value=10,
        text=Format("{value} · 💾"),
        on_text_click=update_items_per_page,
    ),
    state=states.SETTINGS.SET_ITEMS_PER_PAGE,
)

settings_window = Window(
    Title(strings.titles.settings),
    List(Format("<b>{item[0]}</b> {item[1]}"), items="user_info_list"),
    SwitchTo(
        text=Format("🔢 Элементов на страницу: {user.items_per_page}"),
        id="set_items_per_page_button",
        on_click=update_counter_value,
        state=states.SETTINGS.SET_ITEMS_PER_PAGE,
    ),
    Button(
        text=Const("[ТЕСТ] ♻️ Сбросить достижения и очки"),
        id="reset_achievements_and_points",
        on_click=reset_achievements_and_points,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.SETTINGS.MAIN,
    getter=user_info_getter,
)

dialog = Dialog(settings_window, set_items_per_page_window)
