from aiogram_dialog import Dialog, DialogManager

from fanfan.application import AppHolder
from fanfan.application.exceptions.event import NoCurrentEvent

from .common import show_event_page
from .main import schedule_main_window
from .tools import (
    set_manual_event_window,
    swap_events_window,
    toggle_event_skip_window,
)


async def on_start_schedule(start_data: dict, manager: DialogManager):
    app: AppHolder = manager.middleware_data["app"]
    try:
        current_event = await app.schedule.get_current_event()
        await show_event_page(manager, current_event.id)
    except NoCurrentEvent:
        pass


dialog = Dialog(
    schedule_main_window,
    set_manual_event_window,
    swap_events_window,
    toggle_event_skip_window,
    on_start=on_start_schedule,
)
