from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Counter, ManagedCounter, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.bot.dialogs import states
from src.bot.structures import UserRole
from src.bot.ui import strings
from src.db import Database

ID_ITEMS_PER_PAGE_INPUT = "items_per_page_input"


async def user_info_getter(dialog_manager: DialogManager, db: Database, **kwargs):
    user = await db.user.get(dialog_manager.event.from_user.id)
    return {
        "username": user.username,
        "user_id": user.id,
        "user_role": UserRole.get_role_name(user.role),
        "items_per_page": user.items_per_page,
    }


async def update_counter_value(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    db: Database = manager.middleware_data["db"]
    await manager.find(ID_ITEMS_PER_PAGE_INPUT).set_value(
        await db.user.get_items_per_page_setting(manager.event.from_user.id)
    )


async def update_items_per_page(
    event: CallbackQuery,
    widget: ManagedCounter,
    dialog_manager: DialogManager,
):
    db: Database = dialog_manager.middleware_data["db"]
    await db.user.set_items_per_page_setting(
        dialog_manager.event.from_user.id, int(widget.get_value())
    )
    await event.answer("✅ Успешно!")
    await dialog_manager.switch_to(state=states.SETTINGS.MAIN)


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
    Const("<b>⚙️ Настройки</b>\n"),
    Format("Никнейм: @{username}"),
    Format("ID: {user_id}"),
    Format("Роль: {user_role}\n"),
    Format("Выступлений на страницу: {items_per_page}"),
    SwitchTo(
        text=Const("🔢 Задать количество элементов на страницу"),
        id="set_items_per_page_button",
        on_click=update_counter_value,
        state=states.SETTINGS.SET_ITEMS_PER_PAGE,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.SETTINGS.MAIN,
    getter=user_info_getter,
)

dialog = Dialog(settings_window, set_items_per_page_window)
