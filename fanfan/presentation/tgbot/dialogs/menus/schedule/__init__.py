from aiogram_dialog import Dialog, DialogManager

from fanfan.application.exceptions.event import NoCurrentEvent
from fanfan.application.services import ServicesHolder

from .common import show_event_page
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
    services: ServicesHolder = manager.middleware_data["services"]
    try:
        current_event = await services.events.get_current_event()
        await show_event_page(manager, current_event.id)
    except NoCurrentEvent:
        pass


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
