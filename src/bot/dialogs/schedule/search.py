from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input.text import ManagedTextInputAdapter
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from src.bot.dialogs import states
from src.bot.dialogs.schedule.common import (
    ID_SCHEDULE_SCROLL,
    set_current_schedule_page,
)


async def set_search_query(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    data: str,
):
    dialog_manager.dialog_data["search_query"] = data
    await dialog_manager.find(ID_SCHEDULE_SCROLL).set_page(0)
    await dialog_manager.switch_to(states.SCHEDULE.MAIN)


async def reset_search(callback: CallbackQuery, button: Button, manager: DialogManager):
    manager.dialog_data.pop("search_query")
    await set_current_schedule_page(manager)


search_window = Window(
    Const("🔍 Введите поисковый запрос:"),
    TextInput(
        id="search_input",
        type_factory=str,
        on_success=set_search_query,
    ),
    state=states.SCHEDULE.SEARCH,
)
