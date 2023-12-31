from aiogram_dialog import Dialog, DialogManager

from src.db import Database

from .common import set_schedule_page
from .main import schedule_main_window
from .subscriptions import (
    select_event_window,
    set_counter_window,
    subscriptions_main_window,
)
from .tools import (
    set_manual_event_window,
    swap_events_window,
    toggle_event_skip_window,
)


async def on_start_schedule(start_data: dict, manager: DialogManager):
    db: Database = manager.middleware_data["db"]
    current_event = await db.event.get_current()
    await set_schedule_page(manager, current_event)


dialog = Dialog(
    schedule_main_window,
    set_manual_event_window,
    swap_events_window,
    toggle_event_skip_window,
    subscriptions_main_window,
    select_event_window,
    set_counter_window,
    on_start=on_start_schedule,
)
