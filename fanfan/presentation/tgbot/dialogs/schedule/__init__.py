from aiogram_dialog import Dialog, DialogManager

from fanfan.application.exceptions.event import NoCurrentEvent
from fanfan.application.holder import AppHolder

from .common import show_event_page
from .windows import (
    schedule_main_window,
    subscriptions_main_window,
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
    subscriptions_main_window,
    on_start=on_start_schedule,
)
